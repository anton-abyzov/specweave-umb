#!/usr/bin/env python3
"""Validate private operational receipts without loading environment secrets."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

PROJECTS = ("sw-easychamp", "jobweave", "specweave")
PENDING = {"idle", "pending", "queued", "preparing", "starting", "running", "waiting"}


def read(root, name):
    return json.loads((root / name).read_text())


def quoted(path):
    return "'" + str(path).replace("'", "'\"'\"'") + "'"


def require_quiescent(projection):
    """Recheck native state; summary arrays cannot hide an unresolved approval."""
    assert not any(r["status"] in PENDING for r in projection["runs"])
    assert not any(t["status"] in PENDING for t in projection.get("providerTurns", []))
    assert not any(r["status"] == "pending" for r in projection.get("runtimeRequests", []))
    assert not any(i.get("status") in PENDING for i in projection["turnItems"]
                   if i["type"] in ("command_execution", "dynamic_tool", "subagent"))
    assert not any(t["status"] in PENDING for t in projection.get("subagents", []))
    assert not any(t.get("completionDelivery", {}).get("state") not in ("acknowledged", "delivered", "disposed")
                   for t in projection.get("subagents", []) if t.get("origin") == "app_owned")


def retained_output(root, name, projection, native_item):
    """Bind a full public-API item read to the original native command projection."""
    outputs = read(root, name + ".outputs.json")
    assert outputs["version"] == 1 and outputs["threadId"] == projection["thread"]["id"]
    matches = [item for item in outputs["items"] if item["itemId"] == native_item["id"]]
    assert len(matches) == 1
    retained = matches[0]
    data = (root / Path(retained["response"]["path"]).name).read_bytes()
    assert hashlib.sha256(data).hexdigest() == retained["response"]["sha256"]
    actual = json.loads(data)["item"]
    assert actual["type"] == "command_execution" and actual["threadId"] == outputs["threadId"]
    assert actual["id"] == retained["itemId"] == native_item["id"]
    assert actual["runId"] == retained["runId"] == native_item["runId"]
    assert actual["input"] == retained["input"] == native_item["input"]
    assert actual["status"] == native_item["status"] == "completed"
    assert actual["exitCode"] == native_item["exitCode"] == 0
    output = actual["output"]
    assert isinstance(output, str) and output and output == retained["output"]
    assert not actual.get("outputOmitted") and "output truncated for transport" not in output
    return output


def package_fields(prefix):
    """Read complete top-level fields from the first 100 lines of package.json."""
    decoder = json.JSONDecoder()
    text = prefix.lstrip()
    assert text.startswith("{")
    pos, fields = 1, {}
    while pos < len(text):
        pos += len(text[pos:]) - len(text[pos:].lstrip())
        if pos == len(text) or text[pos] == "}":
            break
        try:
            key, pos = decoder.raw_decode(text, pos)
            assert isinstance(key, str)
            pos += len(text[pos:]) - len(text[pos:].lstrip())
            assert text[pos] == ":"
            pos += 1
            pos += len(text[pos:]) - len(text[pos:].lstrip())
            value, pos = decoder.raw_decode(text, pos)
        except (json.JSONDecodeError, IndexError):
            break
        fields[key] = value
        pos += len(text[pos:]) - len(text[pos:].lstrip())
        if pos == len(text) or text[pos] == "}":
            break
        assert text[pos] == ","
        pos += 1
    assert isinstance(fields.get("name"), str) and isinstance(fields.get("scripts"), dict)
    return fields


def audit(root):
    source = read(root, "m4-current-work-audit.json")
    assert source["readOnly"] is True
    assert source["cliVersion"] == source["npmStableVersion"]
    for host in ("m1", "m3"):
        repos = read(root, f"{host}-clone-type-audit.json")["repositories"]
        assert len(repos) == 46
        for repo in repos:
            assert repo["clean"] and repo["isShallow"] == "false"
            assert repo["independentDotGitDirectory"] and not repo["objectAlternatesExists"]
    reuse = read(root, "m1-original-easychamp-reuse-audit.json")
    assert reuse["readOnly"] is True


def checkout_commands(baseline):
    """Require source inspection independently of a receipt's command summary."""
    assert len(baseline) == 2 and baseline[0]["path"] != baseline[1]["path"]
    commands = []
    for state in baseline:
        path = state["path"]
        assert Path(path).is_absolute()
        readme = quoted(Path(path) / "README.md")
        git = "/Library/Developer/CommandLineTools/usr/bin/git --no-optional-locks -C " + quoted(path)
        commands.extend((git + " rev-parse --show-toplevel HEAD", git + " branch --show-current",
                         git + " remote get-url origin", "/usr/bin/sed -n '1,45p' " + readme))
    return commands


def cycle(root, name, source_context=None, transport=None):
    receipt = read(root, name)
    assert receipt["status"] == "passed", name
    assert receipt["temporarySessionRevoked"] is True
    assert len(receipt["observedRuns"]) == 3
    assert all(r["status"] == "completed" for r in receipt["observedRuns"])
    assert receipt["finalSourceState"] == receipt["baseline"]
    assert all(r["status"] == "" for r in receipt["baseline"])
    for state in receipt["quiescence"]:
        assert all(not value for key, value in state.items() if key != "threadId")
    outcome = receipt["outcome"]
    assert outcome["automaticWakeRunId"]
    assert outcome["completionState"] in ("acknowledged", "delivered")
    parent = read(root, name + ".parent.json")
    worker = read(root, name + ".worker.json")
    require_quiescent(parent)
    require_quiescent(worker)
    assert parent["thread"]["id"] == receipt["coordinatorId"]
    assert worker["thread"]["id"] == outcome["workerThreadId"]
    assert parent["thread"]["projectId"] == worker["thread"]["projectId"] == receipt["projectId"]
    observed_ids = {run["id"] for run in receipt["observedRuns"]}
    assert len(observed_ids) == 3
    runs = [r for p in (parent, worker) for r in p["runs"] if r["id"] in observed_ids]
    assert len(runs) == 3 and all(r["status"] == "completed" for r in runs)
    worker_runs = [r for r in worker["runs"] if r["id"] in observed_ids]
    assert len(worker_runs) == 1
    worker_run_id = worker_runs[0]["id"]
    task = next(s for s in parent["subagents"] if s.get("childThreadId") == worker["thread"]["id"])
    wake = next(r for r in parent["runs"] if r["id"] == outcome["automaticWakeRunId"])
    assert wake["id"] in observed_ids
    message = next(m for m in parent["messages"] if m["id"] == wake["userMessageId"])
    assert message["createdBy"] == "agent" and message["creationSource"] == "server"
    assert message["delegatedCompletion"]["parentRunId"] == task["runId"]
    assert message["delegatedCompletion"]["taskIds"] == [task["id"]]
    assert task["completionDelivery"]["observedByRunId"] == wake["id"]
    assert task["completionDelivery"]["state"] in ("acknowledged", "delivered")
    if source_context is not None:
        assert source_context and source_context in receipt["prompt"]
        initial = next(r for r in parent["runs"] if r["id"] == task["runId"])
        assert initial["id"] in observed_ids and initial["id"] != wake["id"]
        assignment = next(m for m in parent["messages"] if m["id"] == initial["userMessageId"])
        assert assignment["role"] == "user" and assignment["runId"] == initial["id"]
        assert assignment["text"] == receipt["prompt"] and source_context in assignment["text"]
        assert source_context in task["prompt"]
        assignments = [i for i in worker["turnItems"]
                       if i["type"] == "user_message" and i.get("runId") == worker_run_id]
        assert assignments and any(source_context in i["text"] for i in assignments)
    required_commands = checkout_commands(receipt["baseline"])
    destination_reads = []
    if source_context is not None:
        checkpoint = Path(transport["checkpointPath"])
        assert checkpoint.is_absolute() and ".." not in checkpoint.parts
        assert checkpoint.is_relative_to(receipt["baseline"][0]["path"])
        cat_variants = [f"{binary} {quoted(checkpoint)}" for binary in ("/bin/cat", "/usr/bin/cat")]
        cat_commands = [command for command in receipt["commands"] if command in cat_variants]
        assert len(cat_commands) == 1
        destination_reads = [cat_commands[0], "/usr/bin/sed -n '1,100p' " +
                             quoted(Path(receipt["baseline"][1]["path"]) / "package.json")]
        required_commands.extend(destination_reads)
    assert set(required_commands).issubset(receipt["commands"])
    commands = [i for i in worker["turnItems"]
                if i["type"] == "command_execution" and i.get("runId") == worker_run_id]
    for expected in set(required_commands + receipt["commands"]):
        matches = [c for c in commands if c["input"] in (expected, "/bin/zsh -lc " + json.dumps(expected))]
        assert matches and all(c["status"] == "completed" and c.get("exitCode") == 0 and not c.get("outputIndicatesFailure") for c in matches)
    if destination_reads:
        read_items = [next(c for c in commands if c["input"] in
                          (command, "/bin/zsh -lc " + json.dumps(command))) for command in destination_reads]
        checkpoint = json.loads(retained_output(root, name, worker, read_items[0]))
        assert checkpoint["sourceRelayText"] == source_context
        assert checkpoint["marker"] == receipt["marker"] and checkpoint["decision"] == receipt["decision"]
        assert checkpoint["nestedPin"]["sha"] == receipt["baseline"][1]["sha"]
        package = receipt["outcome"]["packageInspection"]
        fields = package_fields(retained_output(root, name, worker, read_items[1]))
        assert package["name"] == fields["name"]
        for label in ("workerScripts", "relayScripts"):
            assert isinstance(package[label], list) and package[label]
            assert all(isinstance(pair, list) and len(pair) == 2 and
                       all(isinstance(value, str) and value for value in pair) for pair in package[label])
            assert all(fields["scripts"].get(key) == command for key, command in package[label])
        common = [pair for pair in package["workerScripts"] if pair in package["relayScripts"]]
        assert any(all(package["name"] in outcome[field] and key in outcome[field] and command in outcome[field]
                       for field in ("workerText", "relayText")) for key, command in common)
    for field in ("workerText", "relayText"):
        text = outcome[field]
        assert receipt["marker"] in text and receipt["decision"] in text
        assert all(source["sha"] in text for source in receipt["baseline"])
    for projection, field, run_id in ((worker, "workerText", worker_run_id), (parent, "relayText", wake["id"])):
        actual = "\n".join(i["text"] for i in projection["turnItems"] if i["type"] == "assistant_message" and i.get("runId") == run_id)
        assert actual == outcome[field], "Receipt must match actual native output"
    return receipt


def handoff(root):
    for project in PROJECTS:
        source = cycle(root, f"m4-{project}-source.json")
        assert source["mode"] == "source" and source["host"] == "m4"
        expected_context = hashlib.sha256(source["outcome"]["relayText"].encode()).hexdigest()
        children = {source["outcome"]["workerThreadId"]}
        for host in ("m1", "m3"):
            transport = read(root, f"{host}-transport-{project}.json")
            target = cycle(root, f"{host}-{project}-destination.json", source["outcome"]["relayText"], transport)
            assert transport["status"] == "passed" and transport["clean"] and transport["nestedClean"]
            assert transport["head"] == transport["transportSha"] == target["baseline"][0]["sha"]
            assert transport["branch"] == target["baseline"][0]["branch"]
            assert transport["path"] == target["baseline"][0]["path"]
            assert transport["nestedPin"] == target["baseline"][1]["sha"]
            assert transport["nestedPath"] == target["baseline"][1]["path"]
            assert transport["projectId"] == target["projectId"]
            assert transport["pickup"]["exitCode"] == 0 and transport["aheadBehind"].split() == ["0", "0"]
            assert target["host"] == host and target["mode"] == "destination"
            assert target["sourceCheckpointSha256"] == expected_context
            assert target["marker"] == source["marker"]
            assert target["baseline"][1]["sha"] == source["baseline"][1]["sha"]
            assert target["outcome"]["workerThreadId"] not in children
            children.add(target["outcome"]["workerThreadId"])
            package = target["outcome"]["packageInspection"]
            assert package["name"] and len(package["packageSha256"]) == 64
            assert package["workerScripts"] and package["relayScripts"]
            assert any(script in package["workerScripts"] for script in package["relayScripts"])


def environment(root):
    # The private aggregate is authored only from per-host copy/start/readback receipts.
    report = read(root, "local-development-verification.json")
    assert report["status"] == "passed"
    assert set(report["hosts"]) == {"m1", "m3"}
    def reference(ref):
        path = root / Path(ref["path"]).name
        data = path.read_bytes()
        assert hashlib.sha256(data).hexdigest() == ref["sha256"], path.name
        return json.loads(data) if path.suffix == ".json" else data

    for host_name, host in report["hosts"].items():
        assert host["sourceUnchanged"] is True
        assert host["configurationVerified"] is True
        assert set(host["projects"]) == set(PROJECTS)
        assert all(p["status"] == "passed" for p in host["projects"].values())
        final = reference(host["readback"])
        config = reference(host["configurationReceipt"])
        runtime = reference(host["runtimeReceipt"])
        schema = reference(host["configurationLocalDatabaseUpdates"])
        for item in (final, config, runtime, schema):
            assert item["host"] == host_name
        assert final["configurationVerified"] and final["sourceUnchanged"] and final["testServicesStopped"]
        assert len(final["files"]) == host["configFiles"] == 7
        for item in final["files"]:
            assert item["sha256"] == item["expectedSha256"] and item["matches"]
            assert item["mode"] == "0o600" and item["gitIgnored"] and not item["isSymlink"]
        assert config["status"] == "passed" and config["sourceStatePreserved"]
        assert runtime["status"] == "passed-with-limitations" and runtime["sourcePreserved"] and runtime["ownedProcessesStopped"]
        assert all(command["exit"] == 0 for command in runtime["commands"])
        assert {"specweave-typescript-build", "specweave-cli-version"}.issubset(
            command["label"] for command in runtime["commands"])
        for key, label in (("sw-easychamp", "easychamp"), ("jobweave", "jobweave")):
            response = next(item for item in runtime["http"] if item["project"] == label)
            assert response == host["projects"][key]["http"]
            assert response["status"] == 200 and response["markerPresent"] and response["bytes"] > 0
        assert schema["status"] == "passed" and schema["sourcePreserved"] and schema["ownedServerStopped"]
        assert all(command["exit"] == 0 for command in schema["commands"])
        database = host["projects"]["jobweave"]
        assert reference(database["schema"]) == schema
        observed = reference(database["databaseReadback"])
        assert observed["status"] == "passed" and observed["ownedServerStopped"]
        assert observed["result"] == database["schemaReadback"]
        assert observed["result"]["appliedMigrations"] == 53 and observed["result"]["publicTableCount"] == 51
        assert observed["result"]["vectorVersion"] == "0.8.2" and observed["result"]["vectorDistance"] == 1
        uikit = reference(host["projects"]["sw-easychamp"]["uikitBuild"])
        assert uikit["host"] == host_name and uikit["status"] == "passed"
        assert uikit["sourcePreserved"] and uikit["localesEntryExists"]
        assert any(command["label"] == "build" for command in uikit["commands"])
        assert all(command["exit"] == 0 for command in uikit["commands"])
        reference(host["launchHelper"])
        launcher = reference(host["launchHelper"]["verification"])
        assert launcher["status"] == "passed" and launcher["ownedDbStopped"]
    reference(report["runbook"])


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", choices=("audit", "handoff", "environment", "all", "product-code",
                        "product-review", "product-release", "product-handoff", "product-all"), required=True)
    parser.add_argument("--evidence", type=Path, default=Path.home() / ".local/share/specweave/fleet/handoff-proof-20261013")
    args = parser.parse_args()
    phases = {"audit": audit, "handoff": handoff, "environment": environment}
    if args.phase.startswith("product-"):
        spec = importlib.util.spec_from_file_location("product_handoff_evidence",
                                                     Path(__file__).with_name("product_handoff_evidence.py"))
        product = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(product)
        phases = product.PHASES
    for name, check in phases.items():
        if args.phase in (name, "all", "product-all"):
            check(args.evidence)
            print(f"{name}: passed")
