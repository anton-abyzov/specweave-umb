"""Invented offline evidence only; never a real handoff or release receipt."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
import uuid

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/fleet/product_handoff_evidence.py"
SPEC = importlib.util.spec_from_file_location("product_evidence", SCRIPT)
V = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(V)
FIXTURES = Path(__file__).parent / "fixtures"
BODY = b"frozen fixture body\n"
PNG = b"\x89PNG\r\n\x1a\nexplicit invented unit-test image bytes"
CANDIDATE = {"sourceCommit": "d" * 40, "version": "1.2.3-test",
             "repository": "https://example.invalid/synthetic-studio.git"}


def encode(value):
    return json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode()


def ref(root, name, value):
    data = value if isinstance(value, bytes) else encode(value)
    path = root / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return {"path": name, "sha256": V.digest(data)}


def rehash_native(native):
    for record in native["approvals"]:
        record["payloadSha256"] = V.digest(encode(record["payload"]))
    for output in native["outputs"]:
        output["sha256"] = V.digest(encode(output["response"]))


def invented_native(mode, key, host):
    fixture = json.loads((FIXTURES / f"product_native_{mode}.json").read_text())
    assert fixture["synthetic"] is True
    old = fixture["plan"]
    operation = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"synthetic-{key}-{host}"))
    project = f"source-{key}" if mode == "source" else "machine-handoff:" + operation
    workspace = f"/synthetic/{host}/{key}/product-workspace"
    worker = f"synthetic-{mode}-{host}-{key}-worker"
    replacements = {
        old["coordinatorId"]: "project-coordinator:" + project,
        old["projectId"]: project,
        old["workspaceRoot"]: workspace,
        old["operationId"]: operation,
        old["branch"]: f"codex/0907-product-{key}-{host}",
        old["commitMessage"]: f"0907: Complete {key} handoff diagnostic",
        "studio://thread/worker": "studio://thread/" + worker,
    }
    if mode == "destination":
        replacements["2026-10-13T12:00"] = "2026-10-13T12:06"

    def replace(value, field=None):
        if isinstance(value, dict):
            return {k: replace(v, k) for k, v in value.items()}
        if isinstance(value, list):
            return [replace(v) for v in value]
        if isinstance(value, str):
            if value == "worker" and field in ("id", "threadId", "workerThreadId", "childThreadId"):
                return worker
            if value == "environment":
                return "synthetic-env-" + host
            for before, after in sorted(replacements.items(), key=lambda pair: -len(pair[0])):
                value = value.replace(before, after)
        return value

    plan, native = replace(fixture["plan"]), replace(fixture["receipt"])
    plan["host"], native["host"] = host, host
    if mode == "source":
        del plan["operationId"]
        native["operationId"] = None
    native["temporarySessionRevoked"] = True
    for projection in (native["parent"], native["rawParent"], native["worker"]):
        for run in projection["runs"]:
            run.update(startedAt="2026-10-13T12:00:00Z" if mode == "source" else "2026-10-13T12:06:00Z",
                       completedAt="2026-10-13T12:01:00Z" if mode == "source" else "2026-10-13T12:07:00Z")
    rehash_native(native)
    return plan, native


def set_context(plan, native, content):
    h = V.digest(content)
    plan["frozen"]["context"] = h
    for state in (native["baseline"], native["after"]):
        state["files"]["context"]["sha256"] = h
    for output in native["outputs"]:
        if output["kind"] == "read-context":
            output["response"]["output"] = content.decode()
    initial = next(run for run in native["parent"]["runs"]
                   if run["id"] != native["outcome"]["automaticWakeRunId"])
    prompt = V.product_prompt(plan["operationId"], plan["paths"]["context"], plan["workspaceRoot"])
    for projection in (native["parent"], native["rawParent"]):
        for message in projection["messages"]:
            if message["id"] == initial["userMessageId"]:
                message["text"] = prompt
        for item in projection["turnItems"]:
            if item["type"] == "user_message" and item.get("runId") == initial["id"]:
                item["text"] = prompt
    rehash_native(native)


def invented_evidence(root):
    index = {"version": 1, "candidate": CANDIDATE, "handoff": {"sources": [], "routes": [], "preservation": []}}
    runtimes = {}
    for host in ("m4", "m1", "m3"):
        app = ref(root, f"{host}-wrapper.json", {"version": "1.0.9",
                  "executableSha256": "e" * 64, "runningExecutableSha256": "e" * 64})
        server = ref(root, f"{host}-server.json", {"sourceCommit": CANDIDATE["sourceCommit"], "version": CANDIDATE["version"],
                     "environmentId": "synthetic-env-" + host})
        asset = ref(root, f"{host}-candidate-client.js", b"// explicit synthetic client asset\n")
        served = ref(root, f"{host}-served-client.js", b"// explicit synthetic client asset\n")
        client = ref(root, f"{host}-client.json", {"sourceCommit": CANDIDATE["sourceCommit"],
            "version": CANDIDATE["version"], "assets": [{"url": f"http://localhost/{host}/synthetic-client.js",
                "sha256": asset["sha256"], "builtAsset": asset, "servedAsset": served}]})
        runtimes[host] = ref(root, f"{host}-runtime.json", {"candidateCommit": CANDIDATE["sourceCommit"],
            "host": host, "version": CANDIDATE["version"], "environmentId": "synthetic-env-" + host,
            "kind": "transfer-service", "wrapperReadback": app, "clientReadback": client, "serverReadback": server})
        before = [{"projectKey": key, "kind": kind, "path": f"/synthetic/{host}/original/{key}/{kind}",
                   "head": "f" * 40, "branch": "main", "statusSha256": V.digest(b""),
                   "gitConfigSha256": V.digest(b"original config"), "indexSha256": V.digest(b"original index")}
                  for key in V.PROJECTS for kind in ("root", "nested")]
        private = [] if host == "m4" else [{"path": f"/synthetic/{host}/original/sw-easychamp/root/repositories/owner/app-{n}/.env.local",
            "exists": True, "size": 31, "sha256": V.digest(b"explicit synthetic placeholder"), "mode": "0600"} for n in range(7)]
        index["handoff"]["preservation"].append(ref(root, f"{host}-preservation.json", {"host": host,
            "before": before, "after": copy.deepcopy(before),
            "privateFilesBefore": private, "privateFilesAfter": copy.deepcopy(private),
            "configFilesBefore": [{"path": r["path"] + "/.specweave/config.json", "exists": False} for r in before],
            "configFilesAfter": [{"path": r["path"] + "/.specweave/config.json", "exists": False} for r in before],
            "configBeforeAt": "2026-01-01T00:00:00Z", "configAfterAt": "2027-01-01T00:00:00Z",
            "beforeAt": "2026-01-01T00:00:00Z", "afterAt": "2027-01-01T00:00:00Z"}))
    for key in V.PROJECTS:
        source, source_native = invented_native("source", key, "m4")
        preservation_ref = index["handoff"]["preservation"][0]
        preservation = json.loads((root / preservation_ref["path"]).read_bytes())
        for side in ("before", "after"):
            for row in preservation[side]:
                if row["projectKey"] == key:
                    row["path"] = source["workspaceRoot" if row["kind"] == "root" else "nestedRoot"]
                    row["head"] = source["originalShas"][row["kind"]]
        for side in ("Before", "After"):
            preservation["configFiles" + side] = [{"path": r["path"] + "/.specweave/config.json", "exists": False}
                                                    for r in preservation[side.lower()]]
        preservation_ref.update(ref(root, preservation_ref["path"], preservation))
        relative = "repositories/owner/code"
        identities = {".": "github.com/anton-abyzov/" + V.REPOSITORIES[key][0],
                      relative: "github.com/anton-abyzov/" + V.REPOSITORIES[key][1]}
        source_record = {"key": key, "plan": ref(root, f"{key}-source-plan.json", source),
            "native": ref(root, f"{key}-source-native.json", source_native),
            "start": ref(root, f"{key}-source-start.json", {"status": "started", "key": key,
                "temporarySessionRevoked": True,
                "projectId": source["projectId"], "coordinatorId": source["coordinatorId"],
                "environmentId": source["environmentId"], "messageId": source["startMessageId"],
                "originalShas": source["originalShas"], "runtime": {"environmentId": source["environmentId"],
                    "serverVersion": "1.0.9", "observedAt": "2026-10-13T11:59:00Z"}}),
            "repositoryIdentities": identities,
            "project": ref(root, f"{key}-source-project.json", {"id": source["projectId"], "workspaceRoot": source["workspaceRoot"]}),
            "files": {name: ref(root, f"{key}-frozen-{name}.txt", BODY)
                      for name in ("implementation", "test", "readme", "continuation")}}
        index["handoff"]["sources"].append(source_record)
        for host in V.HOSTS:
            plan, native = invented_native("destination", key, host)
            operation = plan["operationId"]
            bundle = {"manifest": {"version": 1, "operationId": operation, "repositories": [
                {"relativePath": path, "identity": identities[path], "head": sha,
                 "ref": f"refs/heads/codex/handoff/{operation}/{sha}"}
                for path, sha in ((".", source["originalShas"]["root"]), (relative, source["originalShas"]["nested"]))]},
                "sourceEnvironmentId": source["environmentId"], "sourceProjectId": source["projectId"],
                "sourceThreadId": source["coordinatorId"], "createdAt": "2026-10-13T12:02:00Z",
                "context": {"goal": "Invented fixture only", "instructions": "No operational evidence.", "notes": [],
                    "threads": [{"threadId": thread, "title": "Synthetic", "kind": kind,
                        "branch": None, "worktreePath": source["workspaceRoot"], "messages": [
                            {"id": "invented-message", "role": "assistant", "text": output, "createdAt": "2026-01-01T00:00:00Z"}]}
                        for thread, kind, output in ((source["coordinatorId"], "coordinator", source_native["outcome"]["relayText"]),
                            (source_native["outcome"]["workerThreadId"], "worker", source_native["outcome"]["workerText"]))]}}
            bundle["digest"] = V.digest(V.canonical(bundle))
            context = encode(bundle)
            set_context(plan, native, context)
            prefix = f"{key}-{host}"
            existing_id = f"original-{key}-{host}"
            receive = {"operationId": operation, "phase": "started", "projectId": plan["projectId"],
                       "coordinatorThreadId": plan["coordinatorId"], "workspacePath": plan["workspaceRoot"],
                       "contextPath": plan["paths"]["context"], "replayed": False}
            actions = []
            for number, action in enumerate(("open-handoff", "select-destination", "confirm-transfer")):
                observation = f"Synthetic visible {action} for {key} {host}"
                actions.append({"action": action, "observedAt": f"2026-10-13T12:0{number+3}:00Z",
                    "startedAt": f"2026-10-13T12:0{number+3}:00Z",
                    "observation": observation, "snapshot": ref(root, f"{prefix}-ui-{number}.txt", observation.encode()),
                    "screenshot": ref(root, f"{prefix}-ui-{number}.png", PNG)})
            actions[1].update(environmentId=plan["environmentId"], projectId=existing_id)
            ui = {"candidateCommit": CANDIDATE["sourceCommit"], "operationId": operation, "bundleDigest": bundle["digest"],
                "source": {"environmentId": source["environmentId"], "projectId": source["projectId"], "threadId": source["coordinatorId"]},
                "destination": {"environmentId": plan["environmentId"], "projectId": existing_id},
                "entryPoint": "ordinary-coordinator", "usageLimitRequired": False, "actions": actions, "reviewer": "synthetic-reviewer",
                "visualReview": ref(root, f"{prefix}-visual-review.txt",
                    f"synthetic-reviewer observed {operation}: {actions[1]['observation']}".encode())}
            index["handoff"]["routes"].append({"key": key, "host": host,
                "plan": ref(root, f"{prefix}-plan.json", plan), "native": ref(root, f"{prefix}-native.json", native),
                "runtime": runtimes[host], "sourceRuntime": runtimes["m4"], "sourceRecord": ref(root, f"{prefix}-source-record.json",
                    {"bundle": bundle, "publication": "published", "contextBytes": len(context), "messageCount": 2}),
                "destinationRecord": ref(root, f"{prefix}-destination-record.json",
                    {"digest": bundle["digest"], "destinationProjectId": existing_id, "configured": True, "receipt": receive}),
                "context": ref(root, f"{prefix}-context.json", context),
                "gitOperation": ref(root, f"{prefix}-git-operation.json", {"version": 1,
                    "manifestSha256": V.digest(encode(bundle["manifest"])), "manifest": bundle["manifest"],
                    "registeredRoot": f"/synthetic/{host}/original/{key}/root"}),
                "destinationProject": ref(root, f"{prefix}-existing-project.json",
                    {"id": existing_id, "workspaceRoot": f"/synthetic/{host}/original/{key}/root"}),
                "operationProject": ref(root, f"{prefix}-operation-project.json",
                    {"id": plan["projectId"], "workspaceRoot": plan["workspaceRoot"]}),
                "ui": ref(root, f"{prefix}-ui.json", ui)})
    (root / "product-evidence-index.json").write_bytes(encode(index))
    return index


def invented_release_evidence(root, index):
    """Additional invented command/report bytes for the three release gates."""
    cwd = "/synthetic/candidate-studio"
    names = ["wrong-repository", "dirty-destination", "diverged-destination", "missing-source-object",
             "nested-pin-mismatch", "active-owner", "denied-transfer"]
    report = ref(root, "synthetic-vitest-report.json", {"success": True, "numTotalTests": len(names),
        "numPassedTests": len(names), "numFailedTests": 0, "numPendingTests": 0,
        "testResults": [{"assertionResults": [{"fullName": name, "status": "passed"} for name in names]}]})

    def command(name, argv, stdout, test=False):
        item = {"candidateCommit": CANDIDATE["sourceCommit"], "argv": argv, "cwd": cwd, "exitCode": 0,
                "startedAt": "2026-10-13T00:00:00Z", "finishedAt": "2026-10-13T00:00:01Z",
                "stdout": ref(root, f"{name}.stdout", stdout.encode()), "stderr": ref(root, f"{name}.stderr", b"")}
        if test:
            item["testReport"] = report
        return ref(root, f"{name}.command.json", item)

    git = ["git", "--no-optional-locks", "-C", cwd]
    head = command("head", git + ["rev-parse", "HEAD"], CANDIDATE["sourceCommit"] + "\n")
    status = command("status", git + ["status", "--porcelain=v1", "--untracked-files=all"], "")
    origin = command("origin", git + ["remote", "get-url", "origin"], CANDIDATE["repository"] + "\n")
    unit = command("unit", ["npm", "run", "test:unit"], "7 tests passed\n", True)
    component = command("component", ["npm", "run", "test:component"], "7 tests passed\n", True)
    build = command("build", ["npm", "run", "build"], "Synthetic build completed\n")
    index["code"] = ref(root, "code.json", {"candidateCommit": CANDIDATE["sourceCommit"],
        "source": {"head": CANDIDATE["sourceCommit"], "origin": CANDIDATE["repository"], "status": "", "path": cwd,
                   "headCommand": head, "statusCommand": status, "originCommand": origin},
        "checks": [{"kind": kind, "command": cmd, **({"testReport": report} if kind != "build" else {})}
                   for kind, cmd in (("unit", unit), ("component", component), ("build", build))]})
    index["review"] = ref(root, "review.json", {"candidateCommit": CANDIDATE["sourceCommit"],
        "reviewer": "synthetic-independent-reviewer", "implementationOwner": "synthetic-author", "unresolvedFindings": [],
        "report": ref(root, "review.md", f"synthetic-independent-reviewer reviewed {CANDIDATE['sourceCommit']}\n".encode()),
        "cases": {name: {"command": unit, "testReport": report, "assertion": name} for name in names}})
    artifact = ref(root, "synthetic-release.bin", b"Explicit invented artifact, never a real application.")
    build_record = json.loads((root / build["path"]).read_text())
    build_record["producedArtifacts"] = [artifact]
    build.update(ref(root, build["path"], build_record))
    code_record = json.loads((root / index["code"]["path"]).read_text())
    code_record["checks"][2]["command"] = build
    index["code"] = ref(root, index["code"]["path"], code_record)
    publication = ref(root, "publication.json", {"sourceCommit": CANDIDATE["sourceCommit"],
        "version": CANDIDATE["version"], "artifactSha256": artifact["sha256"], "downloadedArtifact": artifact,
        "url": "https://example.invalid/synthetic-release"})
    hosts = []
    for host in ("m4", "m1", "m3"):
        runtime = json.loads((root / f"{host}-runtime.json").read_text())
        runtime["kind"] = "released-native-app"
        runtime["appReadback"] = ref(root, f"{host}-released-app.json", {
            "sourceCommit": CANDIDATE["sourceCommit"], "version": CANDIDATE["version"],
            "executableSha256": "e" * 64, "runningExecutableSha256": "e" * 64})
        runtime["installedFromArtifactSha256"] = artifact["sha256"]
        # Separate release readbacks preserve handoff index references.
        hosts.append({"host": host, "readback": ref(root, f"{host}-release-runtime.json", runtime)})
    index["release"] = ref(root, "release.json", {"candidateCommit": CANDIDATE["sourceCommit"],
        "version": CANDIDATE["version"], "build": build, "artifact": artifact, "publication": publication, "hosts": hosts})
    (root / "product-evidence-index.json").write_bytes(encode(index))


class ProductHandoffEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="synthetic-product-evidence-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.index = invented_evidence(self.root)

    def save(self):
        (self.root / "product-evidence-index.json").write_bytes(encode(self.index))

    def change(self, reference, callback):
        item = json.loads((self.root / reference["path"]).read_text())
        callback(item)
        reference.update(ref(self.root, reference["path"], item))
        self.save()

    def rejected(self):
        with self.assertRaises((ValueError, KeyError, StopIteration, FileNotFoundError)):
            V.product_handoff(self.root)

    def test_complete_explicitly_invented_envelope_and_native_replay_pass(self):
        V.product_handoff(self.root)

    def test_all_product_phases_fail_when_real_evidence_is_absent(self):
        (self.root / "product-evidence-index.json").unlink()
        for check in V.PHASES.values():
            with self.subTest(check=check.__name__), self.assertRaises(ValueError):
                check(self.root)

    def test_status_only_claim_is_rejected(self):
        self.index["handoff"] = {"status": "passed"}
        self.save()
        self.rejected()

    def test_hash_changed_without_index_change_is_rejected(self):
        reference = self.index["handoff"]["routes"][0]["native"]
        (self.root / reference["path"]).write_text('{"status":"passed"}')
        self.rejected()

    def test_parent_traversal_reference_is_rejected(self):
        self.index["handoff"]["sources"][0]["plan"]["path"] = "../outside.json"
        self.save()
        self.rejected()

    def test_symlink_reference_is_rejected(self):
        target = self.root / self.index["handoff"]["sources"][0]["plan"]["path"]
        original = target.with_suffix('.original')
        target.rename(original)
        target.symlink_to(original)
        self.rejected()

    def test_duplicate_json_keys_are_rejected(self):
        reference = self.index["handoff"]["sources"][0]["plan"]
        reference.update(ref(self.root, reference["path"], b'{"version":1,"version":2}'))
        self.save()
        self.rejected()

    def test_missing_route_is_rejected(self):
        self.index["handoff"]["routes"].pop()
        self.save()
        self.rejected()

    def test_duplicate_route_is_rejected(self):
        self.index["handoff"]["routes"][-1] = self.index["handoff"]["routes"][0]
        self.save()
        self.rejected()

    def test_mutated_original_checkout_is_rejected(self):
        self.change(self.index["handoff"]["preservation"][1],
                    lambda d: d["after"][0].update(head="1" * 40))
        self.rejected()

    def add_extra_checkout(self):
        reference = self.index["handoff"]["preservation"][1]
        def add_extra(d):
            row = copy.deepcopy(next(row for row in d["before"] if row["kind"] == "root"))
            row.update(kind="additional", path=row["path"] + "/repositories/owner/extra",
                       statusSha256=V.digest(b" M existing-user-work\n"))
            d["before"].append(row)
            d["after"].append(copy.deepcopy(row))
            for side in ("Before", "After"):
                d["configFiles" + side].append({"path": row["path"] + "/.specweave/config.json", "exists": False})
        self.change(reference, add_extra)
        return reference

    def test_additional_dirty_target_repository_can_remain_preserved(self):
        self.add_extra_checkout()
        V.product_handoff(self.root)

    def test_changed_additional_target_repository_is_rejected(self):
        reference = self.add_extra_checkout()
        self.change(reference, lambda d: d["after"][-1].update(statusSha256=V.digest(b"")))
        self.rejected()

    def test_omitted_additional_repository_after_transfer_is_rejected(self):
        reference = self.add_extra_checkout()
        self.change(reference, lambda d: d["after"].pop())
        self.rejected()

    def test_private_configuration_change_is_rejected(self):
        self.change(self.index["handoff"]["preservation"][1],
                    lambda d: d["privateFilesAfter"][0].update(sha256="0" * 64))
        self.rejected()

    def test_private_configuration_omission_is_rejected(self):
        def remove(d):
            d["privateFilesBefore"].pop()
            d["privateFilesAfter"].pop()
        self.change(self.index["handoff"]["preservation"][1], remove)
        self.rejected()

    def test_project_configuration_change_is_rejected(self):
        self.change(self.index["handoff"]["preservation"][1], lambda d: d["configFilesAfter"][0].update(
            exists=True, size=2, sha256=V.digest(b"{}"), mode="0644"))
        self.rejected()

    def test_config_baseline_after_readonly_source_but_before_transfer_is_valid(self):
        self.change(self.index["handoff"]["preservation"][0],
                    lambda d: d.update(configBeforeAt="2026-10-13T12:01:30Z"))
        V.product_handoff(self.root)

    def test_config_baseline_after_transfer_is_rejected(self):
        self.change(self.index["handoff"]["preservation"][0],
                    lambda d: d.update(configBeforeAt="2026-10-13T12:02:30Z"))
        self.rejected()

    def test_transfer_service_can_use_actual_older_native_wrapper(self):
        evidence = V.Evidence(self.root)
        route = self.index["handoff"]["routes"][0]
        observed = V.runtime(evidence, route["runtime"], route["host"])
        wrapper = evidence.json(observed["wrapperReadback"])
        self.assertEqual(wrapper["version"], "1.0.9")
        self.assertNotEqual(wrapper["version"], CANDIDATE["version"])

    def test_wrong_served_client_bytes_are_rejected(self):
        reference = self.index["handoff"]["routes"][0]["runtime"]
        runtime = json.loads((self.root / reference["path"]).read_bytes())
        self.change(runtime["clientReadback"], lambda d: d["assets"][0].update(
            servedAsset=ref(self.root, "wrong-served.js", b"other client")))
        reference.update(ref(self.root, reference["path"], runtime))
        self.save()
        with self.assertRaisesRegex(ValueError, "served client asset"):
            V.product_handoff(self.root)

    def test_stale_preservation_interval_is_rejected(self):
        self.change(self.index["handoff"]["preservation"][0],
                    lambda d: d.update(beforeAt="2025-01-01T00:00:00Z", afterAt="2025-01-02T00:00:00Z"))
        self.rejected()

    def test_unrelated_m4_checkout_cannot_claim_source_preservation(self):
        def corrupt(d):
            for side in ("before", "after"):
                d[side][0]["path"] = "/synthetic/m4/unrelated-tree"
            for side in ("Before", "After"):
                d["configFiles" + side][0]["path"] = "/synthetic/m4/unrelated-tree/.specweave/config.json"
        self.change(self.index["handoff"]["preservation"][0], corrupt)
        with self.assertRaisesRegex(ValueError, "actual owned source"):
            V.product_handoff(self.root)

    def test_source_version_is_actual_not_relabelled_as_candidate(self):
        source = self.index["handoff"]["sources"][0]
        observed = json.loads((self.root / source["start"]["path"]).read_text())
        self.assertEqual(observed["runtime"]["serverVersion"], "1.0.9")
        self.assertNotEqual(observed["runtime"]["serverVersion"], CANDIDATE["version"])
        V.product_handoff(self.root)

    def test_unrevoked_source_dispatch_session_is_rejected(self):
        self.change(self.index["handoff"]["sources"][0]["start"],
                    lambda d: d.update(temporarySessionRevoked=False))
        with self.assertRaisesRegex(ValueError, "source start/native plan"):
            V.product_handoff(self.root)

    def test_multiple_source_environments_cannot_claim_one_m4(self):
        source = self.index["handoff"]["sources"][1]
        self.change(source["plan"], lambda d: d.update(environmentId="other-m4"))
        def change_start(d):
            d["environmentId"] = d["runtime"]["environmentId"] = "other-m4"
        self.change(source["start"], change_start)
        with self.assertRaisesRegex(ValueError, "multiple M4"):
            V.product_handoff(self.root)

    def test_m1_and_m3_cannot_share_one_runtime_environment(self):
        route = self.index["handoff"]["routes"][1]
        self.change(route["plan"], lambda d: d.update(environmentId="synthetic-env-m1"))
        runtime = json.loads((self.root / route["runtime"]["path"]).read_text())
        server = json.loads((self.root / runtime["serverReadback"]["path"]).read_text())
        server["environmentId"] = runtime["environmentId"] = "synthetic-env-m1"
        runtime["serverReadback"].update(ref(self.root, runtime["serverReadback"]["path"], server))
        route["runtime"].update(ref(self.root, route["runtime"]["path"], runtime))
        self.save()
        with self.assertRaisesRegex(ValueError, "share an environment"):
            V.product_handoff(self.root)

    def test_answer_reseeded_destination_prompt_is_rejected(self):
        def reseed(d):
            initial_id = next(r["userMessageId"] for r in d["parent"]["runs"] if r["id"] != d["outcome"]["automaticWakeRunId"])
            for projection in (d["parent"], d["rawParent"]):
                next(m for m in projection["messages"] if m["id"] == initial_id)["text"] += " Here is the completed answer."
        self.change(self.index["handoff"]["routes"][0]["native"], reseed)
        with self.assertRaisesRegex(ValueError, "product continuation prompt"):
            V.product_handoff(self.root)

    def test_ui_confirmation_after_native_start_is_rejected(self):
        def late(d):
            d["actions"][-1].update(startedAt="2026-10-13T12:08:00Z", observedAt="2026-10-13T12:08:01Z")
        self.change(self.index["handoff"]["routes"][0]["ui"], late)
        with self.assertRaisesRegex(ValueError, "already running"):
            V.product_handoff(self.root)

    def test_wrong_runtime_candidate_is_rejected(self):
        self.change(self.index["handoff"]["routes"][0]["runtime"],
                    lambda d: d.update(candidateCommit="1" * 40))
        self.rejected()

    def test_forged_native_test_count_with_rehashed_receipt_is_rejected(self):
        self.change(self.index["handoff"]["routes"][0]["native"],
                    lambda d: d["testRecords"][0].update({"pass": 99}))
        self.rejected()

    def test_missing_automatic_wake_with_rehashed_receipt_is_rejected(self):
        def corrupt(d):
            for p in (d["parent"], d["rawParent"]):
                p["messages"][-1]["creationSource"] = "web"
        self.change(self.index["handoff"]["routes"][0]["native"], corrupt)
        self.rejected()

    def test_unrevoked_temporary_session_is_rejected(self):
        self.change(self.index["handoff"]["sources"][0]["native"],
                    lambda d: d.update(temporarySessionRevoked=False))
        self.rejected()

    def test_wrong_bundle_digest_is_rejected(self):
        self.change(self.index["handoff"]["routes"][0]["sourceRecord"],
                    lambda d: d["bundle"].update(digest="0" * 64))
        self.rejected()

    def test_recomputed_digest_cannot_hide_wrong_nested_pin(self):
        def corrupt(d):
            d["bundle"]["manifest"]["repositories"][1]["head"] = "1" * 40
            d["bundle"]["digest"] = V.digest(V.canonical({k: v for k, v in d["bundle"].items() if k != "digest"}))
        self.change(self.index["handoff"]["routes"][0]["sourceRecord"], corrupt)
        self.rejected()

    def test_unpublished_bundle_is_rejected(self):
        self.change(self.index["handoff"]["routes"][0]["sourceRecord"],
                    lambda d: d.update(publication="unpublished"))
        self.rejected()

    def test_removed_source_context_with_recomputed_digest_is_rejected(self):
        def corrupt(d):
            d["bundle"]["context"]["threads"] = []
            d["bundle"]["digest"] = V.digest(V.canonical({k: v for k, v in d["bundle"].items() if k != "digest"}))
        self.change(self.index["handoff"]["routes"][0]["sourceRecord"], corrupt)
        self.rejected()

    def test_receive_workspace_mismatch_is_rejected(self):
        self.change(self.index["handoff"]["routes"][0]["destinationRecord"],
                    lambda d: d["receipt"].update(workspacePath="/synthetic/wrong"))
        self.rejected()

    def test_selected_existing_project_mismatch_is_rejected(self):
        self.change(self.index["handoff"]["routes"][0]["destinationRecord"],
                    lambda d: d.update(destinationProjectId="other-project"))
        self.rejected()

    def test_missing_persisted_git_operation_is_rejected(self):
        del self.index["handoff"]["routes"][0]["gitOperation"]
        self.save()
        self.rejected()

    def test_persisted_git_operation_wrong_registered_checkout_is_rejected(self):
        self.change(self.index["handoff"]["routes"][0]["gitOperation"],
                    lambda d: d.update(registeredRoot="/synthetic/other-root"))
        self.rejected()

    def test_persisted_git_operation_wrong_manifest_is_rejected(self):
        self.change(self.index["handoff"]["routes"][0]["gitOperation"],
                    lambda d: d["manifest"]["repositories"][1].update(head="9" * 40))
        self.rejected()

    def test_canonical_bundle_hash_is_not_git_operation_hash(self):
        self.change(self.index["handoff"]["routes"][0]["gitOperation"],
                    lambda d: d.update(manifestSha256=V.digest(V.canonical(d["manifest"]))))
        self.rejected()

    def test_ui_screenshot_alone_is_not_selection_proof(self):
        self.change(self.index["handoff"]["routes"][0]["ui"],
                    lambda d: d.update(actions=[]))
        self.rejected()

    def test_wrong_ui_destination_is_rejected(self):
        self.change(self.index["handoff"]["routes"][0]["ui"],
                    lambda d: d["destination"].update(environmentId="wrong-machine"))
        self.rejected()

    def test_no_visual_review_is_rejected(self):
        self.change(self.index["handoff"]["routes"][0]["ui"],
                    lambda d: d.pop("visualReview"))
        self.rejected()

    def test_unobserved_ui_action_is_rejected(self):
        self.change(self.index["handoff"]["routes"][0]["ui"],
                    lambda d: d["actions"][1].update(observation="Invented extra assertion absent from snapshot"))
        self.rejected()

    def test_changed_frozen_test_bytes_are_rejected(self):
        self.index["handoff"]["sources"][0]["files"]["test"] = ref(self.root, "wrong-test.txt", b"weakened tests")
        self.save()
        self.rejected()

    def test_index_cannot_select_executable_validator(self):
        stub = self.root / "forged-verifier.mjs"
        stub.write_text("throw new Error('must never execute indexed code');")
        self.index["handoff"]["supervisor"] = ref(self.root, stub.name, stub.read_bytes())
        self.save()
        V.product_handoff(self.root)

    def test_product_cli_missing_evidence_exits_nonzero(self):
        (self.root / "product-evidence-index.json").unlink()
        cli = SCRIPT.with_name("verify-handoff-evidence.py")
        result = subprocess.run([shutil.which("python3"), str(cli), "--phase", "product-all", "--evidence", str(self.root)],
                                capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn("passed", result.stdout)


class ProductReleaseEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="synthetic-product-release-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.index = invented_evidence(self.root)
        invented_release_evidence(self.root, self.index)

    def read(self, reference):
        return json.loads((self.root / reference["path"]).read_text())

    def replace(self, reference, value):
        reference.update(ref(self.root, reference["path"], value))
        (self.root / "product-evidence-index.json").write_bytes(encode(self.index))

    def test_invented_code_review_release_fixtures_pass(self):
        for check in (V.product_code, V.product_review, V.product_release):
            check(self.root)

    def test_echo_cannot_claim_candidate_head(self):
        code = self.read(self.index["code"])
        check = self.read(code["source"]["headCommand"])
        check["argv"] = ["echo", CANDIDATE["sourceCommit"]]
        self.replace(code["source"]["headCommand"], check)
        self.replace(self.index["code"], code)
        with self.assertRaisesRegex(ValueError, "Git command"):
            V.product_code(self.root)

    def test_unrelated_checkout_cannot_supply_unit_or_build_results(self):
        original = self.read(self.index["code"])
        for number in (0, 2):
            code = copy.deepcopy(original)
            check = self.read(code["checks"][number]["command"])
            check["cwd"] = "/synthetic/other-candidate"
            self.replace(code["checks"][number]["command"], check)
            self.replace(self.index["code"], code)
            with self.assertRaises(ValueError):
                V.product_code(self.root)

    def test_missing_raw_origin_readback_is_rejected(self):
        code = self.read(self.index["code"])
        del code["source"]["originCommand"]
        self.replace(self.index["code"], code)
        with self.assertRaises(KeyError):
            V.product_code(self.root)

    def test_echo_cannot_claim_a_build(self):
        code = self.read(self.index["code"])
        check = self.read(code["checks"][2]["command"])
        check["argv"] = ["echo", "build"]
        self.replace(code["checks"][2]["command"], check)
        self.replace(self.index["code"], code)
        with self.assertRaisesRegex(ValueError, "unrecognized"):
            V.product_code(self.root)

    def test_version_output_cannot_claim_unit_component_or_build_execution(self):
        for kind in ("unit", "component", "build"):
            with self.subTest(kind=kind), self.assertRaisesRegex(ValueError, "version/help"):
                V.check_invocation(["node", "--version", "test" if kind != "build" else "build"], kind)

    def test_known_test_and_typecheck_runner_forms_are_recognized(self):
        for argv, kind in ((["pnpm", "exec", "vitest", "run", "test.ts"], "unit"),
                           (["bunx", "vitest", "run", "component.test.tsx"], "component"),
                           (["npx", "--no-install", "vitest", "run"], "unit"),
                           (["node", "node_modules/vitest/vitest.mjs", "run"], "unit"),
                           (["node", "node_modules/vite-plus/bin/vp", "test", "run", "component.test.tsx"], "component"),
                           (["node", "node_modules/typescript/bin/tsc", "--noEmit"], "typecheck"),
                           (["node", "node_modules/typescript/bin/tsc", "--noEmit", "-p", "apps/server/tsconfig.json"], "typecheck"),
                           (["tsc", "--build"], "build")):
            V.check_invocation(argv, kind)

    def test_dry_run_and_other_noop_flags_cannot_claim_execution(self):
        for argv, kind in ((["tsc", "--build", "--dry"], "build"),
                           (["tsc", "--noEmit", "--showConfig"], "typecheck"),
                           (["npm", "test", "--ignore-scripts"], "unit"),
                           (["vitest", "run", "--help=true"], "component")):
            with self.subTest(argv=argv), self.assertRaisesRegex(ValueError, "no-op"):
                V.check_invocation(argv, kind)

    def adapt_combined_command(self):
        code = self.read(self.index["code"])
        reference = code["checks"][0]["command"]
        observed = self.read(reference)
        stdout = observed.pop("stdout")
        del observed["stderr"]
        owner = {"source": observed["candidateCommit"], "command": observed["argv"], "cwd": observed["cwd"],
            "startedAt": observed["startedAt"], "completedAt": observed["finishedAt"], "exitCode": observed["exitCode"],
            "sourceUnchanged": True, "log": "/synthetic/owner-original/combined.log"}
        observed["combinedOutput"] = {**stdout, "originPath": owner["log"]}
        observed["ownerReceipt"] = ref(self.root, "synthetic-owner-command.json", owner)
        self.replace(reference, observed)
        self.replace(self.index["code"], code)
        return reference, observed

    def test_actual_combined_owner_output_can_be_retained_without_invented_stderr(self):
        self.adapt_combined_command()
        V.product_code(self.root)

    def test_adapter_cannot_change_observed_owner_command(self):
        reference, observed = self.adapt_combined_command()
        observed["argv"] = ["npm", "run", "test:another"]
        self.replace(reference, observed)
        code = self.read(self.index["code"])
        code["checks"][0]["command"] = reference
        self.replace(self.index["code"], code)
        with self.assertRaisesRegex(ValueError, "retained owner receipt"):
            V.product_code(self.root)

    def test_combined_owner_output_cannot_claim_separate_empty_stderr(self):
        reference, observed = self.adapt_combined_command()
        observed["stderr"] = ref(self.root, "invented-empty-stderr.txt", b"")
        self.replace(reference, observed)
        code = self.read(self.index["code"])
        code["checks"][0]["command"] = reference
        self.replace(self.index["code"], code)
        with self.assertRaisesRegex(ValueError, "separated streams"):
            V.product_code(self.root)

    def test_typecheck_preserves_successful_empty_output(self):
        code = self.read(self.index["code"])
        check = self.read(code["checks"][0]["command"])
        check["argv"] = ["node", "node_modules/typescript/bin/tsc", "--noEmit", "-p", "apps/server/tsconfig.json"]
        check["stdout"] = ref(self.root, "empty-typecheck.txt", b"")
        reference = ref(self.root, "typecheck-empty.json", check)
        V.candidate_command(V.Evidence(self.root), reference, "typecheck", code["source"]["path"])

    def retained_desktop_builder(self):
        code = self.read(self.index["code"])
        observed = self.read(code["checks"][2]["command"])
        root, stage, node = code["source"]["path"], "/synthetic/output-stage", "/synthetic/node22/node"
        # Explicit invented data uses a stable release version accepted by the
        # real artifact CLI; this helper validates only command provenance.
        candidate = dict(CANDIDATE, version="1.0.10")
        builder = (f"const root = '{root}';\nconst stage = '{stage}';\nconst node = '{node}';\n"
            "const result = spawnSync(node, ['scripts/build-desktop-artifact.ts','--platform','mac','--target','dmg','--arch','arm64','--build-version','1.0.10','--output-dir',stage], { cwd:root, env, stdio:['ignore',fd,fd] });\n")
        builder_ref = ref(self.root, "invented-build-final.mjs", builder.encode())
        prepared = ref(self.root, "invented-preparation.json", {"preparedAt": "2026-10-12T00:00:00Z",
            "repoRoot": root, "version": "1.0.10", "files": [{"file": "build-final.mjs", "preparedSha256": builder_ref["sha256"]}]})
        owner = {"source": CANDIDATE["sourceCommit"], "stage": stage, "startedAt": observed["startedAt"],
            "completedAt": observed["finishedAt"], "exitCode": 0, "sourceUnchanged": True, "log": "/synthetic/build.log"}
        observed.update(argv=[node,"scripts/build-desktop-artifact.ts","--platform","mac","--target","dmg","--arch","arm64",
            "--build-version","1.0.10","--output-dir",stage], ownerReceipt=ref(self.root,"invented-build-receipt.json",owner),
            builderSource=builder_ref,builderPreparation=prepared,invocationProvenance="derived-from-retained-builder",
            combinedOutput={**observed.pop("stdout"),"originPath":owner["log"]})
        del observed["stderr"]
        reference = ref(self.root,"invented-build-command.json",observed)
        evidence=V.Evidence(self.root);evidence.candidate=candidate
        return evidence,reference,observed,root

    def test_build_invocation_can_be_explicitly_derived_from_frozen_creator(self):
        evidence,reference,_,root=self.retained_desktop_builder()
        V.candidate_command(evidence,reference,"build",root)

    def test_derived_build_cannot_invent_different_argv(self):
        evidence,reference,observed,root=self.retained_desktop_builder()
        observed["argv"][-1]="/synthetic/different-output"
        self.replace(reference,observed)
        with self.assertRaisesRegex(ValueError,"differs from frozen creator"):
            V.candidate_command(evidence,reference,"build",root)

    def test_modified_builder_does_not_match_pre_run_frozen_hash(self):
        evidence,reference,observed,root=self.retained_desktop_builder()
        observed["builderSource"]=ref(self.root,"changed-builder.mjs",b"// changed creator\n")
        self.replace(reference,observed)
        with self.assertRaisesRegex(ValueError,"pre-build preparation"):
            V.candidate_command(evidence,reference,"build",root)

    def external_case(self):
        code, review = self.read(self.index["code"]), self.read(self.index["review"])
        original = self.read(code["checks"][0]["command"])
        root, path = code["source"]["path"], "/synthetic/independent-review/permissions.test.ts"
        imported = root + "/apps/server/authorization.ts"
        body = ref(self.root, "external-test.ts", f'import * as Auth from "{imported}";\n'.encode())
        production = ref(self.root, "candidate-import.ts", b"export const requiredScopes = ['handoff'];\n")
        execution = {**original, "cwd": "/synthetic/independent-review",
                     "argv": ["node", root + "/node_modules/vite-plus/bin/vp", "test", "run", path]}
        report = self.read(original["testReport"])
        for suite in report["testResults"]:
            suite["name"] = path
        execution["testReport"] = ref(self.root, "external-named-report.json", report)
        command = ref(self.root, "external-execution.json", execution)
        git = {**original, "cwd": root, "argv": ["git", "--no-optional-locks", "-C", root, "show",
            CANDIDATE["sourceCommit"] + ":apps/server/authorization.ts"], "stdout": production}
        external = {"candidateCommit": CANDIDATE["sourceCommit"], "command": command,
            "testReport": execution["testReport"], "reviewer": review["reviewer"],
            "review": ref(self.root, "external-review.txt", (review["reviewer"] + " " + CANDIDATE["sourceCommit"]
                + " " + path + " " + body["sha256"] + " " + production["sha256"]).encode()),
            "testFiles": [{"path": path, "bytes": body, "candidateImports": [{"path": imported,
                "relativePath": "apps/server/authorization.ts", "bytes": production,
                "gitShowCommand": ref(self.root, "external-candidate-git-show.json", git)}]}]}
        reference = ref(self.root, "external-case.json", external)
        review["cases"]["denied-transfer"] = {"command": command, "testReport": execution["testReport"],
            "assertion": "denied-transfer", "externalTest": reference, "testPath": path}
        self.replace(self.index["review"], review)
        return reference, external, review

    def update_external(self, reference, external, review):
        self.replace(reference, external)
        review["cases"]["denied-transfer"]["externalTest"] = reference
        self.replace(self.index["review"], review)

    def test_external_reviewer_test_binds_frozen_candidate_imports(self):
        self.external_case()
        V.product_review(self.root)

    def test_external_test_without_candidate_import_is_rejected(self):
        reference, external, review = self.external_case()
        external["testFiles"][0]["candidateImports"] = []
        self.update_external(reference, external, review)
        with self.assertRaisesRegex(ValueError, "no explicit candidate import"):
            V.product_review(self.root)

    def test_external_test_source_hash_must_be_independently_reviewed(self):
        reference, external, review = self.external_case()
        external["testFiles"][0]["bytes"] = ref(self.root, "changed-external.ts", b"// changed after review\n")
        self.update_external(reference, external, review)
        with self.assertRaisesRegex(ValueError, "bytes not independently reviewed"):
            V.product_review(self.root)

    def test_external_import_cannot_use_another_commit(self):
        reference, external, review = self.external_case()
        imported = external["testFiles"][0]["candidateImports"][0]
        git = self.read(imported["gitShowCommand"])
        git["argv"][-1] = "0" * 40 + ":apps/server/authorization.ts"
        self.replace(imported["gitShowCommand"], git)
        self.update_external(reference, external, review)
        with self.assertRaisesRegex(ValueError, "actual frozen Git blob"):
            V.product_review(self.root)

    def test_external_import_retained_bytes_must_equal_git_blob(self):
        reference, external, review = self.external_case()
        imported = external["testFiles"][0]["candidateImports"][0]
        git = self.read(imported["gitShowCommand"])
        git["stdout"] = ref(self.root, "wrong-actual-import.ts", b"unrelated source bytes")
        self.replace(imported["gitShowCommand"], git)
        self.update_external(reference, external, review)
        with self.assertRaisesRegex(ValueError, "differ from reviewed frozen source"):
            V.product_review(self.root)

    def test_external_command_must_name_retained_test_file(self):
        reference, external, review = self.external_case()
        execution = self.read(external["command"])
        execution["argv"][-1] = "/synthetic/independent-review/other.test.ts"
        self.replace(external["command"], execution)
        review["cases"]["denied-transfer"]["command"] = external["command"]
        self.update_external(reference, external, review)
        with self.assertRaisesRegex(ValueError, "not named by actual test command"):
            V.product_review(self.root)

    def test_excluded_external_file_cannot_use_another_suites_passing_assertions(self):
        reference, external, review = self.external_case()
        execution = self.read(external["command"])
        execution["argv"].insert(-1, "--exclude")
        report = self.read(external["testReport"])
        report["testResults"][0]["name"] = "/synthetic/independent-review/actually-ran.test.ts"
        self.replace(external["testReport"], report)
        execution["testReport"] = external["testReport"]
        self.replace(external["command"], execution)
        review["cases"]["denied-transfer"].update(command=external["command"], testReport=external["testReport"])
        self.update_external(reference, external, review)
        with self.assertRaisesRegex(ValueError, "JSON reporter suite paths"):
            V.product_review(self.root)

    def test_external_case_must_name_its_actual_frozen_suite(self):
        _, _, review = self.external_case()
        review["cases"]["denied-transfer"]["testPath"] = "/synthetic/other-suite.test.ts"
        self.replace(self.index["review"], review)
        with self.assertRaisesRegex(ValueError, "executed frozen suite"):
            V.product_review(self.root)

    def configured_external_case(self):
        reference, external, review = self.external_case()
        path = "/synthetic/independent-review/named.config.mjs"
        config = {"test": {"root": "/synthetic/independent-review", "include": ["permissions.test.ts"],
            "environment": "node", "testTimeout": 60000, "hookTimeout": 60000}}
        config_ref = ref(self.root, "external-config.mjs", b"export default " + encode(config) + b";\n")
        source = external["testFiles"][0]
        bindings = {"candidateCommit": CANDIDATE["sourceCommit"], "candidatePath": "/synthetic/candidate-studio",
            "harnessFiles": [{"path": "independent-review/permissions.test.ts", "sha256": source["bytes"]["sha256"]},
                             {"path": "independent-review/named.config.mjs", "sha256": config_ref["sha256"]}],
            "directImportsAndWorkspaceEntry": [{"sha256": source["candidateImports"][0]["bytes"]["sha256"]}]}
        bindings_ref = ref(self.root, "external-harness-bindings.json", bindings)
        execution = self.read(external["command"])
        execution["argv"][-1] = "--config=" + path
        execution.update(externalHarnessBindings=bindings_ref, harnessUnchanged=True)
        self.replace(external["command"], execution)
        external.update(config={"path": path, "bytes": config_ref}, harnessBindings=bindings_ref, harnessRoot="/synthetic",
            review=ref(self.root, "external-config-review.txt", (review["reviewer"] + " " + CANDIDATE["sourceCommit"]
                + " " + bindings_ref["sha256"]).encode()))
        review["cases"]["denied-transfer"]["command"] = external["command"]
        self.update_external(reference, external, review)
        return reference, external, review

    def test_external_config_binds_exact_executed_files_and_import_bytes(self):
        self.configured_external_case()
        V.product_review(self.root)

    def test_external_config_alias_overrides_are_rejected(self):
        reference, external, review = self.configured_external_case()
        external["config"]["bytes"] = ref(self.root, "external-overridden.mjs",
            b'export default {"test":{},"resolve":{"alias":{"production":"fake"}}};\n')
        self.update_external(reference, external, review)
        with self.assertRaisesRegex(ValueError, "unreviewed runner overrides"):
            V.product_review(self.root)

    def test_failed_named_assertion_overrides_success_flag(self):
        code = self.read(self.index["code"])
        check = self.read(code["checks"][0]["command"])
        report = self.read(check["testReport"])
        report["testResults"][0]["assertionResults"][0]["status"] = "failed"
        self.replace(check["testReport"], report)
        code["checks"][0]["testReport"] = check["testReport"]
        self.replace(code["checks"][0]["command"], check)
        self.replace(self.index["code"], code)
        with self.assertRaisesRegex(ValueError, "assertions"):
            V.product_code(self.root)

    def test_self_review_is_rejected(self):
        review = self.read(self.index["review"])
        review["reviewer"] = review["implementationOwner"]
        self.replace(self.index["review"], review)
        with self.assertRaisesRegex(ValueError, "independent"):
            V.product_review(self.root)

    def test_missing_failure_case_is_rejected(self):
        review = self.read(self.index["review"])
        del review["cases"]["denied-transfer"]
        self.replace(self.index["review"], review)
        with self.assertRaisesRegex(ValueError, "adversarial"):
            V.product_review(self.root)

    def test_unresolved_finding_is_rejected(self):
        review = self.read(self.index["review"])
        review["unresolvedFindings"] = ["Synthetic unfixed defect"]
        self.replace(self.index["review"], review)
        with self.assertRaisesRegex(ValueError, "unresolved"):
            V.product_review(self.root)

    def test_corrupted_release_artifact_is_rejected(self):
        release = self.read(self.index["release"])
        (self.root / release["artifact"]["path"]).write_bytes(b"wrong artifact")
        with self.assertRaisesRegex(ValueError, "hash mismatch"):
            V.product_release(self.root)

    def test_separate_noop_cannot_claim_packaging(self):
        release = self.read(self.index["release"])
        built = self.read(release["build"])
        for argv in (["echo", "build"], ["node", "--version", "build"]):
            with self.subTest(argv=argv):
                built["argv"] = argv
                release["build"] = ref(self.root, "separate-noop-package.json", built)
                self.replace(self.index["release"], release)
                with self.assertRaises(ValueError):
                    V.product_release(self.root)

    def test_separate_packaging_from_another_checkout_is_rejected(self):
        release = self.read(self.index["release"])
        built = self.read(release["build"])
        built["cwd"] = "/synthetic/unreviewed-candidate"
        release["build"] = ref(self.root, "separate-wrong-package.json", built)
        self.replace(self.index["release"], release)
        with self.assertRaisesRegex(ValueError, "another checkout"):
            V.product_release(self.root)

    def test_wrong_published_source_is_rejected(self):
        release = self.read(self.index["release"])
        publication = self.read(release["publication"])
        publication["sourceCommit"] = "1" * 40
        self.replace(release["publication"], publication)
        self.replace(self.index["release"], release)
        with self.assertRaisesRegex(ValueError, "published artifact mismatch"):
            V.product_release(self.root)

    def test_missing_host_install_is_rejected(self):
        release = self.read(self.index["release"])
        release["hosts"].pop()
        self.replace(self.index["release"], release)
        with self.assertRaisesRegex(ValueError, "three release host"):
            V.product_release(self.root)

    def test_transfer_runtime_cannot_claim_final_native_release(self):
        release = self.read(self.index["release"])
        runtime = self.read(release["hosts"][0]["readback"])
        runtime["kind"] = "transfer-service"
        self.replace(release["hosts"][0]["readback"], runtime)
        self.replace(self.index["release"], release)
        with self.assertRaisesRegex(ValueError, "runtime evidence kind"):
            V.product_release(self.root)

    def test_older_native_wrapper_cannot_claim_final_release(self):
        release = self.read(self.index["release"])
        runtime = self.read(release["hosts"][0]["readback"])
        app = self.read(runtime["appReadback"])
        app["version"] = "1.0.9"
        self.replace(runtime["appReadback"], app)
        self.replace(release["hosts"][0]["readback"], runtime)
        self.replace(self.index["release"], release)
        with self.assertRaisesRegex(ValueError, "released native app"):
            V.product_release(self.root)

    def test_running_wrong_binary_is_rejected(self):
        release = self.read(self.index["release"])
        host = self.read(release["hosts"][0]["readback"])
        app = self.read(host["appReadback"])
        app["runningExecutableSha256"] = "0" * 64
        self.replace(host["appReadback"], app)
        self.replace(release["hosts"][0]["readback"], host)
        self.replace(self.index["release"], release)
        with self.assertRaisesRegex(ValueError, "running executable"):
            V.product_release(self.root)

    def test_product_all_dispatches_only_product_phases(self):
        cli = SCRIPT.with_name("verify-handoff-evidence.py")
        result = subprocess.run([shutil.which("python3"), str(cli), "--phase", "product-all", "--evidence", str(self.root)],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.splitlines(), [name + ": passed" for name in V.PHASES])


if __name__ == "__main__":
    unittest.main()
