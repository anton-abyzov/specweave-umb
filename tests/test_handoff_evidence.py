"""Negative tests using invented data, never private operational receipts.

All fixture paths, IDs, source text and hashes are synthetic. These tests exercise
the evidence validator; they do not constitute evidence of a machine handoff.
"""

import copy
from contextlib import redirect_stdout
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import runpy
import sys
import tempfile
import unittest
from unittest.mock import patch


SCRIPT = Path(__file__).resolve().parents[1] / "scripts/fleet/verify-handoff-evidence.py"
SPEC = importlib.util.spec_from_file_location("handoff_evidence", SCRIPT)
VERIFIER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VERIFIER)
REJECTED = (AssertionError, KeyError, StopIteration, ValueError, FileNotFoundError)


def digest(text):
    return hashlib.sha256(text.encode()).hexdigest()


def invented_cycle(host, project, source=None):
    """A minimal invented native coordinator/worker/completion projection."""
    label = f"synthetic-{host}-{project}"
    root_path = f"/synthetic/{host}/{project}"
    nested_path = f"{root_path}/repositories/example/product"
    root_sha = digest(label)[:40]
    nested_sha = digest(f"synthetic-code-{project}")[:40]
    marker = f"SYNTHETIC-CONTINUATION-{project}"
    decision = "Keep the synthetic fixture read-only."
    next_step = "Inspect the package scripts without executing them."
    baseline = [
        {"path": path, "sha": sha, "branch": "codex/synthetic-handoff", "status": "",
         "origin": f"https://example.invalid/{project}/{kind}.git"}
        for kind, path, sha in (("root", root_path, root_sha), ("nested", nested_path, nested_sha))
    ]
    commands = []
    command_outputs = []
    for state in baseline:
        git = "/Library/Developer/CommandLineTools/usr/bin/git --no-optional-locks -C " + f"'{state['path']}'"
        commands.extend((git + " rev-parse --show-toplevel HEAD", git + " branch --show-current",
                         git + " remote get-url origin", f"/usr/bin/sed -n '1,45p' '{state['path']}/README.md'"))
        command_outputs.extend((f"{state['path']}\n{state['sha']}\n", state["branch"] + "\n",
                                state["origin"] + "\n", "# Synthetic product README\n"))
    prompt = f"{marker}\n{decision}\n{next_step}"
    if source:
        prompt += "\nSource checkpoint:\n" + source["outcome"]["relayText"]
        checkpoint = {"sourceRelayText": source["outcome"]["relayText"], "marker": marker,
                      "decision": decision, "nestedPin": {"sha": nested_sha}}
        commands.extend((f"/bin/cat '{root_path}/.specweave/increments/0001-synthetic/checkpoint.json'",
                         f"/usr/bin/sed -n '1,100p' '{nested_path}/package.json'"))
        command_outputs.extend((json.dumps(checkpoint), json.dumps({
            "name": "synthetic-package", "scripts": {"test": "node --test synthetic.test.js"}})))
    worker_text = f"{marker}\n{decision}\n{root_sha}\n{nested_sha}\n{next_step}"
    if source:
        worker_text += "\nPackage synthetic-package: test = node --test synthetic.test.js"
    relay_text = worker_text + "\nCoordinator observed the synthetic worker completion."
    initial_id, worker_id, wake_id = (f"{label}-{part}" for part in ("initial-run", "worker-run", "wake-run"))
    parent_id, child_id, task_id = (f"{label}-{part}" for part in ("parent", "child", "task"))
    project_id = f"{label}-project"
    initial_message, wake_message = f"{label}-assignment", f"{label}-completion"
    receipt = {
        "fixture": "invented-unit-test-data", "status": "passed", "host": host,
        "mode": "destination" if source else "source", "key": project,
        "projectId": project_id, "coordinatorId": parent_id, "baseline": baseline,
        "finalSourceState": copy.deepcopy(baseline), "temporarySessionRevoked": True,
        "observedRuns": [{"id": run_id, "status": "completed"} for run_id in (initial_id, worker_id, wake_id)],
        "quiescence": [{"threadId": parent_id, "activeRuns": [], "activeWorkers": []}],
        "marker": marker, "decision": decision, "prompt": prompt, "commands": commands,
        "sourceCheckpointSha256": digest(source["outcome"]["relayText"]) if source else None,
        "outcome": {"workerText": worker_text, "relayText": relay_text,
                    "workerThreadId": child_id, "automaticWakeRunId": wake_id,
                    "completionState": "acknowledged"},
    }
    parent = {
        "thread": {"id": parent_id, "projectId": project_id},
        "runs": [{"id": initial_id, "status": "completed", "userMessageId": initial_message},
                 {"id": wake_id, "status": "completed", "userMessageId": wake_message}],
        "messages": [
            {"id": initial_message, "runId": initial_id, "role": "user", "createdBy": "user",
             "creationSource": "web", "text": prompt},
            {"id": wake_message, "runId": wake_id, "role": "user", "createdBy": "agent",
             "creationSource": "server", "delegatedCompletion": {"parentRunId": initial_id, "taskIds": [task_id]}},
        ],
        "subagents": [{"id": task_id, "childThreadId": child_id, "runId": initial_id,
                       "prompt": prompt, "status": "completed", "origin": "app_owned",
                       "completionDelivery": {"observedByRunId": wake_id, "state": "acknowledged"}}],
        "turnItems": [{"type": "user_message", "runId": initial_id, "text": prompt},
                      {"type": "assistant_message", "runId": wake_id, "text": relay_text}],
    }
    worker = {
        "thread": {"id": child_id, "projectId": project_id},
        "runs": [{"id": worker_id, "status": "completed"}],
        "messages": [{"id": f"{label}-worker-assignment", "role": "user", "text": prompt}],
        "turnItems": [{"type": "user_message", "runId": worker_id, "text": prompt}] + [
            {"type": "command_execution", "id": f"{label}-command-{i}", "threadId": child_id,
             "runId": worker_id, "input": command, "status": "completed",
             "exitCode": 0, "output": output}
            for i, (command, output) in enumerate(zip(commands, command_outputs))
        ] + [{"type": "assistant_message", "runId": worker_id, "text": worker_text}],
    }
    if source:
        receipt["outcome"]["packageInspection"] = {
            "name": "synthetic-package", "packageSha256": digest("synthetic-package"),
            "workerScripts": [["test", "node --test synthetic.test.js"]],
            "relayScripts": [["test", "node --test synthetic.test.js"]],
        }
    return receipt, parent, worker


class HandoffEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="synthetic-handoff-test-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for project in VERIFIER.PROJECTS:
            source, parent, worker = invented_cycle("m4", project)
            self.save_cycle(f"m4-{project}-source.json", source, parent, worker)
            for host in ("m1", "m3"):
                target, parent, worker = invented_cycle(host, project, source)
                self.save_cycle(f"{host}-{project}-destination.json", target, parent, worker)
                root, nested = target["baseline"]
                self.write(f"{host}-transport-{project}.json", {
                    "fixture": "invented-unit-test-data", "status": "passed", "host": host,
                    "clean": True, "nestedClean": True, "head": root["sha"], "transportSha": root["sha"],
                    "branch": root["branch"], "path": root["path"], "nestedPin": nested["sha"],
                    "nestedPath": nested["path"], "projectId": target["projectId"],
                    "pickup": {"exitCode": 0}, "aheadBehind": "0\t0",
                    "checkpointPath": root["path"] + "/.specweave/increments/0001-synthetic/checkpoint.json",
                })

    def read(self, name):
        return json.loads((self.root / name).read_text())

    def write(self, name, value):
        (self.root / name).write_text(json.dumps(value))

    def save_cycle(self, name, receipt, parent, worker):
        self.write(name, receipt)
        self.write(name + ".parent.json", parent)
        self.write(name + ".worker.json", worker)
        if receipt["mode"] == "destination":
            outputs = {"version": 1, "threadId": worker["thread"]["id"], "items": []}
            for i, item in enumerate([i for i in worker["turnItems"] if i["type"] == "command_execution"][-2:]):
                response_name = name + f".item-{i}.json"
                self.write(response_name, {"item": item})
                response_hash = hashlib.sha256((self.root / response_name).read_bytes()).hexdigest()
                outputs["items"].append({"itemId": item["id"], "runId": item["runId"],
                                         "input": item["input"], "output": item["output"],
                                         "response": {"path": response_name, "sha256": response_hash}})
            self.write(name + ".outputs.json", outputs)

    def assert_rejected(self):
        with self.assertRaises(REJECTED):
            VERIFIER.handoff(self.root)

    def change_output(self, name, index, edit):
        outputs = self.read(name + ".outputs.json")
        retained = outputs["items"][index]
        response_name = retained["response"]["path"]
        response = self.read(response_name)
        edit(response["item"])
        self.write(response_name, response)
        retained["output"] = response["item"]["output"]
        retained["response"]["sha256"] = hashlib.sha256((self.root / response_name).read_bytes()).hexdigest()
        self.write(name + ".outputs.json", outputs)

    def test_complete_synthetic_fixture_is_accepted(self):
        VERIFIER.handoff(self.root)

    def test_corrupted_native_assistant_output_is_rejected(self):
        name = "m1-jobweave-destination.json.worker.json"
        worker = self.read(name)
        worker["turnItems"][-1]["text"] += "\nThis differs from the receipt."
        self.write(name, worker)
        self.assert_rejected()

    def test_missing_server_automatic_wake_is_rejected(self):
        name = "m3-specweave-destination.json.parent.json"
        parent = self.read(name)
        parent["messages"][-1]["creationSource"] = "web"
        parent["messages"][-1]["createdBy"] = "user"
        self.write(name, parent)
        self.assert_rejected()

    def test_unobserved_completion_delivery_is_rejected(self):
        name = "m1-sw-easychamp-destination.json.parent.json"
        parent = self.read(name)
        parent["subagents"][0]["completionDelivery"]["observedByRunId"] = "different-run"
        self.write(name, parent)
        self.assert_rejected()

    def test_wrong_transport_sha_is_rejected(self):
        name = "m3-transport-jobweave.json"
        transport = self.read(name)
        transport["head"] = "f" * 40
        self.write(name, transport)
        self.assert_rejected()

    def test_missing_context_hash_is_rejected(self):
        name = "m1-specweave-destination.json"
        target = self.read(name)
        del target["sourceCheckpointSha256"]
        self.write(name, target)
        self.assert_rejected()

    def test_wrong_context_hash_is_rejected(self):
        name = "m3-sw-easychamp-destination.json"
        target = self.read(name)
        target["sourceCheckpointSha256"] = digest("unrelated synthetic checkpoint")
        self.write(name, target)
        self.assert_rejected()

    def test_wrong_native_worker_sha_is_rejected(self):
        name = "m1-specweave-destination.json"
        target = self.read(name)
        old_sha = target["baseline"][1]["sha"]
        target["outcome"]["workerText"] = target["outcome"]["workerText"].replace(old_sha, "f" * 40)
        self.write(name, target)
        worker = self.read(name + ".worker.json")
        worker["turnItems"][-1]["text"] = target["outcome"]["workerText"]
        self.write(name + ".worker.json", worker)
        self.assert_rejected()

    def test_failed_native_command_is_rejected(self):
        name = "m3-specweave-destination.json.worker.json"
        worker = self.read(name)
        worker["turnItems"][1]["exitCode"] = 1
        self.write(name, worker)
        self.assert_rejected()

    def test_missing_destination_receipt_is_rejected(self):
        (self.root / "m3-jobweave-destination.json").unlink()
        self.assert_rejected()

    def test_no_checkout_commands_is_rejected(self):
        """A copied status flag and generated prose cannot prove a source read."""
        name = "m1-jobweave-destination.json"
        target = self.read(name)
        target["commands"] = []
        self.write(name, target)
        worker = self.read(name + ".worker.json")
        worker["turnItems"] = [i for i in worker["turnItems"] if i["type"] != "command_execution"]
        self.write(name + ".worker.json", worker)
        self.assert_rejected()

    def test_arbitrary_eight_commands_cannot_replace_checkout_reads(self):
        name = "m1-jobweave-destination.json"
        target = self.read(name)
        target["commands"] = [f"echo synthetic-{i}" for i in range(8)]
        self.write(name, target)
        worker = self.read(name + ".worker.json")
        for item, command in zip((i for i in worker["turnItems"] if i["type"] == "command_execution"),
                                 target["commands"]):
            item["input"] = command
        self.write(name + ".worker.json", worker)
        self.assert_rejected()

    def test_checkout_read_from_another_run_is_rejected(self):
        name = "m3-specweave-destination.json.worker.json"
        worker = self.read(name)
        worker["turnItems"][1]["runId"] = "synthetic-prior-run"
        self.write(name, worker)
        self.assert_rejected()

    def test_checkout_read_without_exit_code_is_rejected(self):
        name = "m1-sw-easychamp-destination.json.worker.json"
        worker = self.read(name)
        del worker["turnItems"][1]["exitCode"]
        self.write(name, worker)
        self.assert_rejected()

    def test_shell_wrapped_native_checkout_commands_are_accepted(self):
        name = "m4-jobweave-source.json.worker.json"
        worker = self.read(name)
        for item in worker["turnItems"]:
            if item["type"] == "command_execution":
                item["input"] = "/bin/zsh -lc " + json.dumps(item["input"])
        self.write(name, worker)
        VERIFIER.handoff(self.root)

    def test_each_native_assignment_requires_source_checkpoint(self):
        name = "m1-jobweave-destination.json"
        for boundary in ("parent", "task", "worker"):
            with self.subTest(boundary=boundary):
                parent = self.read(name + ".parent.json")
                worker = self.read(name + ".worker.json")
                original_parent, original_worker = copy.deepcopy(parent), copy.deepcopy(worker)
                if boundary == "parent":
                    parent["messages"][0]["text"] = "Unrelated synthetic parent assignment."
                elif boundary == "task":
                    parent["subagents"][0]["prompt"] = "Unrelated synthetic delegated task."
                else:
                    worker["turnItems"][0]["text"] = "Unrelated synthetic worker assignment."
                self.write(name + ".parent.json", parent)
                self.write(name + ".worker.json", worker)
                self.assert_rejected()
                self.write(name + ".parent.json", original_parent)
                self.write(name + ".worker.json", original_worker)

    def test_parent_checkpoint_from_another_run_is_rejected(self):
        name = "m1-specweave-destination.json.parent.json"
        parent = self.read(name)
        parent["messages"][0]["runId"] = "synthetic-prior-run"
        self.write(name, parent)
        self.assert_rejected()

    def test_context_hash_without_delivered_checkpoint_is_rejected(self):
        """The right summary hash must not substitute for actual source context."""
        name = "m3-jobweave-destination.json"
        target = self.read(name)
        replacement = "An unrelated synthetic assignment without the M4 checkpoint."
        target["prompt"] = replacement
        self.write(name, target)
        parent = self.read(name + ".parent.json")
        parent["messages"][0]["text"] = replacement
        parent["turnItems"][0]["text"] = replacement
        parent["subagents"][0]["prompt"] = replacement
        self.write(name + ".parent.json", parent)
        worker = self.read(name + ".worker.json")
        worker["messages"][0]["text"] = replacement
        worker["turnItems"][0]["text"] = replacement
        self.write(name + ".worker.json", worker)
        self.assert_rejected()

    def test_each_destination_file_read_is_required(self):
        name = "m3-jobweave-destination.json"
        for index in (-2, -1):
            with self.subTest(index=index):
                target, worker = self.read(name), self.read(name + ".worker.json")
                original_target, original_worker = copy.deepcopy(target), copy.deepcopy(worker)
                command = target["commands"].pop(index)
                worker["turnItems"] = [i for i in worker["turnItems"] if i.get("input") != command]
                self.write(name, target)
                self.write(name + ".worker.json", worker)
                self.assert_rejected()
                self.write(name, original_target)
                self.write(name + ".worker.json", original_worker)

    def test_missing_full_output_receipt_is_rejected(self):
        (self.root / "m1-specweave-destination.json.outputs.json").unlink()
        self.assert_rejected()

    def test_corrupted_raw_api_response_is_rejected(self):
        (self.root / "m3-sw-easychamp-destination.json.item-1.json").write_text("{}")
        self.assert_rejected()

    def test_raw_api_item_from_another_run_is_rejected(self):
        self.change_output("m1-jobweave-destination.json", 1,
                           lambda item: item.update(runId="synthetic-unrelated-run"))
        self.assert_rejected()

    def test_truncated_native_output_is_rejected(self):
        self.change_output("m1-jobweave-destination.json", 1,
                           lambda item: item.update(output=item["output"] + "\n… output truncated for transport"))
        self.assert_rejected()

    def test_checkpoint_content_must_match_actual_source_relay(self):
        def corrupt(item):
            checkpoint = json.loads(item["output"])
            checkpoint["sourceRelayText"] = "Unrelated synthetic source discovery."
            item["output"] = json.dumps(checkpoint)
        self.change_output("m1-specweave-destination.json", 0, corrupt)
        self.assert_rejected()

    def test_invented_package_command_is_rejected(self):
        def corrupt(item):
            package = json.loads(item["output"])
            package["scripts"]["test"] = "node different-test.js"
            item["output"] = json.dumps(package)
        self.change_output("m3-specweave-destination.json", 1, corrupt)
        self.assert_rejected()

    def test_bare_script_names_are_not_script_pairs(self):
        name = "m1-jobweave-destination.json"
        target = self.read(name)
        target["outcome"]["packageInspection"]["workerScripts"] = ["test"]
        self.write(name, target)
        self.assert_rejected()

    def test_both_native_texts_must_include_package_and_complete_command(self):
        name = "m3-sw-easychamp-destination.json"
        for role, field in (("worker", "workerText"), ("parent", "relayText")):
            with self.subTest(role=role):
                target, projection = self.read(name), self.read(name + f".{role}.json")
                original_target, original_projection = copy.deepcopy(target), copy.deepcopy(projection)
                replacement = target["outcome"][field].replace("node --test synthetic.test.js", "incomplete")
                target["outcome"][field] = replacement
                projection["turnItems"][-1]["text"] = replacement
                self.write(name, target)
                self.write(name + f".{role}.json", projection)
                self.assert_rejected()
                self.write(name, original_target)
                self.write(name + f".{role}.json", original_projection)

    def test_valid_package_fields_in_a_partial_json_prefix_are_accepted(self):
        self.change_output("m3-jobweave-destination.json", 1,
                           lambda item: item.update(output=item["output"][:-1] + ', "dependencies": {'))
        VERIFIER.handoff(self.root)

    def test_empty_package_prefix_has_no_usable_evidence(self):
        for prefix in ("{", "{}"):
            with self.subTest(prefix=prefix), self.assertRaises(AssertionError):
                VERIFIER.package_fields(prefix)

    def test_pending_native_state_cannot_hide_behind_quiescence_summary(self):
        name = "m1-jobweave-destination.json.parent.json"
        original = self.read(name)
        for field, record in (
            ("runtimeRequests", {"id": "synthetic-unresolved-approval", "status": "pending"}),
            ("providerTurns", {"id": "synthetic-active-provider-turn", "status": "waiting"}),
            ("runs", {"id": "synthetic-unfinished-old-run", "status": "running"}),
            ("turnItems", {"id": "synthetic-unfinished-tool", "type": "dynamic_tool", "status": "queued"}),
            ("subagents", {"id": "synthetic-active-task", "status": "starting"}),
            ("subagents", {"id": "synthetic-undelivered-task", "status": "completed", "origin": "app_owned",
                           "completionDelivery": {"state": "pending"}}),
        ):
            with self.subTest(field=field, record=record["id"]):
                parent = copy.deepcopy(original)
                parent.setdefault(field, []).append(record)
                self.write(name, parent)
                self.assert_rejected()
        self.write(name, original)

    def test_pending_worker_approval_is_rejected(self):
        name = "m3-specweave-destination.json.worker.json"
        worker = self.read(name)
        worker["runtimeRequests"] = [{"id": "synthetic-worker-approval", "status": "pending"}]
        self.write(name, worker)
        self.assert_rejected()

    def test_settled_old_history_is_preserved_and_accepted(self):
        name = "m1-jobweave-destination.json.parent.json"
        parent = self.read(name)
        parent["runs"].append({"id": "synthetic-interrupted-old-run", "status": "interrupted"})
        parent["subagents"].append({"id": "synthetic-disposed-old-task", "status": "cancelled", "origin": "app_owned",
                                    "completionDelivery": {"state": "disposed"}})
        self.write(name, parent)
        VERIFIER.handoff(self.root)


class EnvironmentEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="synthetic-environment-test-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.report = {"status": "passed", "hosts": {}}
        for host in ("m1", "m3"):
            final = {
                "host": host, "configurationVerified": True, "sourceUnchanged": True,
                "testServicesStopped": True,
                "files": [{"path": f"/synthetic/{host}/config-{i}", "sha256": digest(str(i)),
                           "expectedSha256": digest(str(i)), "matches": True, "mode": "0o600",
                           "gitIgnored": True, "isSymlink": False} for i in range(7)],
            }
            runtime = {
                "host": host, "status": "passed-with-limitations", "sourcePreserved": True,
                "ownedProcessesStopped": True,
                "commands": [{"label": label, "exit": 0} for label in
                             ("specweave-typescript-build", "specweave-cli-version")],
                "http": [{"project": project, "status": 200, "markerPresent": True, "bytes": 100}
                         for project in ("easychamp", "jobweave")],
            }
            schema = {"host": host, "status": "passed", "sourcePreserved": True,
                      "ownedServerStopped": True, "commands": [{"label": "migrate", "exit": 0}]}
            observed = {"host": host, "status": "passed", "ownedServerStopped": True,
                        "result": {"appliedMigrations": 53, "publicTableCount": 51,
                                   "vectorVersion": "0.8.2", "vectorDistance": 1}}
            schema_ref = self.ref(f"{host}-schema.json", schema)
            host_report = {
                "sourceUnchanged": True, "configurationVerified": True, "configFiles": 7,
                "readback": self.ref(f"{host}-readback.json", final),
                "configurationReceipt": self.ref(f"{host}-config.json", {
                    "host": host, "status": "passed", "sourceStatePreserved": True}),
                "runtimeReceipt": self.ref(f"{host}-runtime.json", runtime),
                "configurationLocalDatabaseUpdates": schema_ref,
                "projects": {
                    "sw-easychamp": {
                        "status": "passed", "http": runtime["http"][0],
                        "uikitBuild": self.ref(f"{host}-uikit.json", {
                            "host": host, "status": "passed", "sourcePreserved": True,
                            "localesEntryExists": True, "commands": [{"label": "build", "exit": 0}]}),
                    },
                    "jobweave": {"status": "passed", "http": runtime["http"][1],
                                 "schema": schema_ref, "schemaReadback": observed["result"],
                                 "databaseReadback": self.ref(f"{host}-database.json", observed)},
                    "specweave": {"status": "passed"},
                },
                "launchHelper": self.ref(f"{host}-launcher.py", "# synthetic helper; never execute\n"),
            }
            host_report["launchHelper"]["verification"] = self.ref(f"{host}-launcher-check.json", {
                "host": host, "status": "passed", "ownedDbStopped": True})
            self.report["hosts"][host] = host_report
        self.report["runbook"] = self.ref("synthetic-runbook.md", "Invented test runbook.\n")
        self.save_report()

    def ref(self, name, value):
        data = json.dumps(value).encode() if isinstance(value, dict) else value.encode()
        (self.root / name).write_bytes(data)
        return {"path": f"/synthetic/evidence/{name}", "sha256": hashlib.sha256(data).hexdigest()}

    def save_report(self):
        (self.root / "local-development-verification.json").write_text(json.dumps(self.report))

    def change_ref(self, reference, edit):
        name = Path(reference["path"]).name
        document = json.loads((self.root / name).read_text())
        edit(document)
        reference.update(self.ref(name, document))
        self.save_report()

    def assert_rejected(self):
        with self.assertRaises(REJECTED):
            VERIFIER.environment(self.root)

    def test_complete_synthetic_environment_is_accepted(self):
        VERIFIER.environment(self.root)

    def test_modified_receipt_hash_is_rejected(self):
        (self.root / "m1-runtime.json").write_text("{}")
        self.assert_rejected()

    def test_world_readable_config_is_rejected(self):
        self.change_ref(self.report["hosts"]["m1"]["readback"],
                        lambda d: d["files"][0].update(mode="0o644"))
        self.assert_rejected()

    def test_missing_runtime_project_is_rejected(self):
        del self.report["hosts"]["m3"]["projects"]["jobweave"]
        self.save_report()
        self.assert_rejected()

    def test_failed_specweave_command_is_rejected(self):
        self.change_ref(self.report["hosts"]["m1"]["runtimeReceipt"],
                        lambda d: d["commands"][0].update(exit=1))
        self.assert_rejected()

    def test_missing_specweave_commands_is_rejected(self):
        self.change_ref(self.report["hosts"]["m1"]["runtimeReceipt"],
                        lambda d: d.update(commands=[]))
        self.assert_rejected()

    def test_either_missing_specweave_check_is_rejected(self):
        reference = self.report["hosts"]["m1"]["runtimeReceipt"]
        original = json.loads((self.root / Path(reference["path"]).name).read_text())
        for missing in ("specweave-typescript-build", "specweave-cli-version"):
            with self.subTest(missing=missing):
                changed = copy.deepcopy(original)
                changed["commands"] = [c for c in changed["commands"] if c["label"] != missing]
                reference.update(self.ref("m1-runtime.json", changed))
                self.save_report()
                self.assert_rejected()

    def test_failed_uikit_build_is_rejected(self):
        self.change_ref(self.report["hosts"]["m3"]["projects"]["sw-easychamp"]["uikitBuild"],
                        lambda d: d.update(status="failed", commands=[{"label": "build", "exit": 1}]))
        self.assert_rejected()

    def test_uikit_pass_flag_cannot_override_failed_build(self):
        self.change_ref(self.report["hosts"]["m3"]["projects"]["sw-easychamp"]["uikitBuild"],
                        lambda d: d["commands"][0].update(exit=1))
        self.assert_rejected()

    def test_missing_uikit_build_is_rejected(self):
        self.change_ref(self.report["hosts"]["m1"]["projects"]["sw-easychamp"]["uikitBuild"],
                        lambda d: d.update(commands=[]))
        self.assert_rejected()


class AuditEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="synthetic-audit-test-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.write("m4-current-work-audit.json", {
            "readOnly": True, "cliVersion": "0.0.0-test", "npmStableVersion": "0.0.0-test"})
        for host in ("m1", "m3"):
            self.write(f"{host}-clone-type-audit.json", {"repositories": [
                {"path": f"/synthetic/{host}/repo-{i}", "clean": True, "isShallow": "false",
                 "independentDotGitDirectory": True, "objectAlternatesExists": False} for i in range(46)]})
        self.write("m1-original-easychamp-reuse-audit.json", {"readOnly": True})

    def write(self, name, value):
        (self.root / name).write_text(json.dumps(value))

    def test_complete_synthetic_audit_is_accepted(self):
        VERIFIER.audit(self.root)

    def test_stale_cli_version_is_rejected(self):
        self.write("m4-current-work-audit.json", {
            "readOnly": True, "cliVersion": "0.0.0-test", "npmStableVersion": "0.0.1-test"})
        with self.assertRaises(REJECTED):
            VERIFIER.audit(self.root)

    def test_cli_audit_reads_the_explicit_synthetic_directory(self):
        output = io.StringIO()
        argv = [str(SCRIPT), "--phase", "audit", "--evidence", str(self.root)]
        with patch.object(sys, "argv", argv), redirect_stdout(output):
            runpy.run_path(str(SCRIPT), run_name="__main__")
        self.assertEqual(output.getvalue(), "audit: passed\n")

    def test_cli_does_not_fall_back_to_real_evidence(self):
        (self.root / "m4-current-work-audit.json").unlink()
        argv = [str(SCRIPT), "--phase", "audit", "--evidence", str(self.root)]
        with patch.object(sys, "argv", argv), self.assertRaises(FileNotFoundError):
            runpy.run_path(str(SCRIPT), run_name="__main__")


if __name__ == "__main__":
    unittest.main()
