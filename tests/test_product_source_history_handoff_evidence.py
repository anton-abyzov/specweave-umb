"""Invented terminal history; no captured user conversation or operational proof."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from urllib.parse import quote

import test_product_handoff_evidence as fixtures


def invented_history(plan, native):
    """Extend an invented successful cycle with one later failed worker."""
    parent_id = plan["coordinatorId"]
    native["startedAt"] = "2026-10-13T12:00:00.000Z"
    fields = ("runs", "providerTurns", "attempts", "turnItems", "nodes", "subagents",
              "runtimeRequests", "messages", "plans", "checkpointScopes", "checkpoints",
              "contextHandoffs", "contextTransfers")
    for projection in (native["rawParent"], native["worker"], native["prior"]):
        parent = projection["thread"]["id"] == parent_id
        projection["thread"].update(title="Invented coordinator" if parent else "Invented worker",
            branch=None, worktreePath=None, deletedAt=None, createdAt="2026-10-13T11:00:00.000Z",
            createdBy="user", creationSource="web", forkedFrom=None if parent else {"type": "node", "nodeId": "task"},
            lineage={"parentThreadId": None if parent else parent_id,
                     "relationshipToParent": None if parent else "subagent", "rootThreadId": parent_id})
        for field in fields:
            projection.setdefault(field, [])
        for run in projection["runs"]:
            run["threadId"] = projection["thread"]["id"]
        for message in projection["messages"]:
            message.update(threadId=projection["thread"]["id"], role="user", streaming=False)
            message["createdAt"] = "2026-10-13T12:00:00.000Z"
        for task in projection["subagents"]:
            task["threadId"] = parent_id
    for projection, output in ((native["rawParent"], "relayText"), (native["worker"], "workerText")):
        projection["messages"].append({"id": "invented-" + output, "threadId": projection["thread"]["id"],
            "role": "assistant", "text": native["outcome"][output], "streaming": False,
            "createdAt": "2026-10-13T12:01:00.000Z"})
    native["parent"] = copy.deepcopy(native["rawParent"])
    parent, worker = copy.deepcopy(native["rawParent"]), copy.deepcopy(native["worker"])
    extra = copy.deepcopy(worker)
    extra["thread"].update(id="invented-later-failed-worker", title="Invented failure",
                             forkedFrom={"type": "node", "nodeId": "later-task"})
    for field in fields:
        extra[field] = []
    extra["runs"] = [{"id": "later-child-run", "threadId": extra["thread"]["id"], "status": "failed",
                       "completedAt": "2026-10-13T12:01:20.000Z"}]
    extra["messages"] = [{"id": "later-failed-message", "threadId": extra["thread"]["id"],
        "role": "assistant", "text": "Invented historical failure; no implementation change.",
        "streaming": False, "createdAt": "2026-10-13T12:01:20.000Z"}]
    parent["subagents"].append({"id": "later-task", "threadId": parent_id, "runId": "later-parent-run",
        "origin": "app_owned", "childThreadId": extra["thread"]["id"], "status": "failed",
        "completionDelivery": {"state": "acknowledged"}})
    parent["runs"].append({"id": "later-parent-run", "threadId": parent_id, "status": "completed",
                          "completedAt": "2026-10-13T12:01:21.000Z"})
    parent["messages"].append({"id": "later-user-message", "threadId": parent_id, "role": "user",
        "text": "Invented later task.", "streaming": False, "createdAt": "2026-10-13T12:01:10.000Z"})
    projections = [parent, worker, extra]

    def reads(at):
        return [{"method": "GET", "path": "/api/orchestration/threads/" + quote(p["thread"]["id"], safe=""),
                 "requestedAt": at, "receivedAt": at, "response": {"projection": copy.deepcopy(p)}}
                for p in projections]

    history = {"version": 1, "kind": "source-terminal-history-supplement", "host": "m4",
        "source": {}, "startedAt": "2026-10-13T12:01:30.000Z", "finishedAt": "2026-10-13T12:01:34.000Z",
        "configRead": {"method": "RPC", "path": "server.getConfig", "requestedAt": "2026-10-13T12:01:30.000Z",
            "receivedAt": "2026-10-13T12:01:30.000Z", "response": {"environment": {"environmentId": plan["environmentId"]}}},
        "reads": {"before": reads("2026-10-13T12:01:31.000Z"), "after": reads("2026-10-13T12:01:32.000Z")},
        "files": {"before": copy.deepcopy(native["baseline"]), "after": copy.deepcopy(native["baseline"])},
        "historicalOnlyThreadIds": [extra["thread"]["id"]], "temporarySessionRevoked": True}
    threads = [{"threadId": p["thread"]["id"], "title": p["thread"]["title"], "branch": None,
        "worktreePath": None, "kind": "coordinator" if p["thread"]["id"] == parent_id else "worker",
        "messages": [{k: m[k] for k in ("id", "role", "text", "createdAt")} for m in p["messages"]]}
        for p in projections]
    # JS serializes each timestamp to millisecond ISO form.
    for thread in threads:
        for message in thread["messages"]:
            message["createdAt"] = fixtures.V.time_value(message["createdAt"]).isoformat(
                timespec="milliseconds").replace("+00:00", "Z")
    return history, threads


class SourceHistoryTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix="invented-history-")
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name).resolve()
        self.index = fixtures.invented_evidence(self.root)
        self.entry = self.index["handoff"]["sources"][0]
        self.route = self.index["handoff"]["routes"][0]
        self.plan, self.native = self.read(self.entry["plan"]), self.read(self.entry["native"])
        self.saved = self.read(self.route["sourceRecord"])
        self.history, self.threads = invented_history(self.plan, self.native)
        self.entry["native"] = fixtures.ref(self.root, self.entry["native"]["path"], self.native)
        self.history["source"] = {"planSha256": self.entry["plan"]["sha256"],
            "nativeSha256": self.entry["native"]["sha256"], "environmentId": self.plan["environmentId"],
            "projectId": self.plan["projectId"], "coordinatorId": self.plan["coordinatorId"]}
        self.saved["bundle"]["context"]["threads"] = self.threads

    def read(self, reference):
        return json.loads((self.root / reference["path"]).read_bytes())

    def save(self):
        self.route["sourceHistory"] = fixtures.ref(self.root, "terminal-history.json", self.history)
        self.route["sourceRecord"] = fixtures.ref(self.root, self.route["sourceRecord"]["path"], self.saved)
        (self.root / "product-evidence-index.json").write_bytes(fixtures.encode(self.index))
        return fixtures.V.Evidence(self.root)

    def replay(self):
        fixtures.V.source_context(self.save(), self.entry, self.plan, self.native, self.route, self.saved["bundle"])

    def test_fixed_replay_accepts_terminal_failure_without_replacing_original_success(self):
        original = copy.deepcopy(self.native)
        self.replay()
        self.assertEqual(self.native, original)
        self.assertEqual(self.history["historicalOnlyThreadIds"], ["invented-later-failed-worker"])

    def test_original_raw_byte_hashes_are_required(self):
        for field in ("planSha256", "nativeSha256"):
            with self.subTest(field=field):
                before = self.history["source"][field]
                self.history["source"][field] = "0" * 64
                with self.assertRaisesRegex(ValueError, "source terminal history replay failed"):
                    self.replay()
                self.history["source"][field] = before

    def test_plan_reserialization_cannot_keep_original_hash_binding(self):
        path = self.root / self.entry["plan"]["path"]
        path.write_text(json.dumps(self.plan, indent=4))
        self.entry["plan"]["sha256"] = fixtures.V.digest(path.read_bytes())
        with self.assertRaisesRegex(ValueError, "source terminal history replay failed"):
            self.replay()

    def test_source_pins_configs_files_and_session_cleanup_cannot_drift(self):
        mutations = [lambda h: h.update(temporarySessionRevoked=False),
            lambda h: h["files"]["after"]["repos"]["root"].update(sha="f" * 40),
            lambda h: h["files"]["after"]["repos"]["nested"].update(configSha256="e" * 64),
            lambda h: h["files"]["before"]["files"]["test"].update(sha256="e" * 64)]
        baseline = copy.deepcopy(self.history)
        for mutate in mutations:
            self.history = copy.deepcopy(baseline)
            mutate(self.history)
            with self.assertRaisesRegex(ValueError, "source terminal history replay failed"):
                self.replay()

    def test_new_history_cannot_change_owner_or_rewrite_original_records(self):
        baseline = copy.deepcopy(self.history)
        for mutate in (lambda p: p["thread"].update(projectId="foreign"),
                       lambda p: p["messages"][0].update(text="rewritten prior task"),
                       lambda p: p["subagents"][-1].update(childThreadId="foreign")):
            self.history = copy.deepcopy(baseline)
            for reads in self.history["reads"].values():
                mutate(reads[0]["response"]["projection"])
            with self.assertRaisesRegex(ValueError, "source terminal history replay failed"):
                self.replay()

    def test_pending_or_unread_descendant_cannot_claim_quiet(self):
        baseline = copy.deepcopy(self.history)
        for mutate in (lambda p: p["runs"][0].update(status="running"),
                       lambda p: p["runtimeRequests"].append({"id": "pending", "status": "pending"}),
                       lambda p: p["subagents"].append({"id": "grandchild", "status": "completed"})):
            self.history = copy.deepcopy(baseline)
            for reads in self.history["reads"].values():
                mutate(reads[2]["response"]["projection"])
            with self.assertRaisesRegex(ValueError, "source terminal history replay failed"):
                self.replay()

    def test_bundle_must_carry_exact_current_inventory_and_message_bytes(self):
        baseline = copy.deepcopy(self.saved)
        for mutate in (lambda b: b["context"]["threads"].pop(),
                       lambda b: b["context"]["threads"][-1]["messages"][0].update(text="invented success"),
                       lambda b: b.update(createdAt=self.history["startedAt"])):
            self.saved = copy.deepcopy(baseline)
            mutate(self.saved["bundle"])
            with self.assertRaisesRegex(ValueError, "source terminal history replay failed"):
                self.replay()

    def test_expanded_bundle_cannot_omit_supplement(self):
        evidence = self.save()
        del self.route["sourceHistory"]
        with self.assertRaisesRegex(ValueError, "requires terminal supplement"):
            fixtures.V.source_context(evidence, self.entry, self.plan, self.native, self.route, self.saved["bundle"])

    def test_original_inventory_remains_valid_without_supplement(self):
        evidence = self.save()
        del self.route["sourceHistory"]
        self.saved["bundle"]["context"]["threads"].pop()
        fixtures.V.source_context(evidence, self.entry, self.plan, self.native, self.route, self.saved["bundle"])

    def test_duplicate_carried_thread_is_rejected_before_replay(self):
        self.saved["bundle"]["context"]["threads"].append(copy.deepcopy(self.threads[0]))
        with self.assertRaisesRegex(ValueError, "duplicate carried source thread"):
            self.replay()

    def test_hash_tampering_or_path_traversal_is_rejected(self):
        evidence = self.save()
        self.route["sourceHistory"]["path"] = "../elsewhere.json"
        with self.assertRaisesRegex(ValueError, "unsafe evidence reference"):
            fixtures.V.source_context(evidence, self.entry, self.plan, self.native, self.route, self.saved["bundle"])
        evidence = self.save()
        (self.root / self.route["sourceHistory"]["path"]).write_text("{}")
        with self.assertRaisesRegex(ValueError, "evidence hash mismatch"):
            fixtures.V.source_context(evidence, self.entry, self.plan, self.native, self.route, self.saved["bundle"])

    def test_fixed_runner_ignores_index_selected_code_and_rejects_forged_report(self):
        evidence = self.save()
        self.route["validator"] = "/untrusted/code.mjs"
        real_run = fixtures.V.subprocess.run
        calls = []

        def record(argv, **kwargs):
            calls.append(argv)
            return real_run(argv, **kwargs)

        with patch.object(fixtures.V.subprocess, "run", side_effect=record):
            fixtures.V.source_context(evidence, self.entry, self.plan, self.native, self.route, self.saved["bundle"])
        self.assertEqual(calls[-1][1], str(fixtures.V.HISTORY_RUNNER))
        self.assertNotIn("/untrusted/code.mjs", calls[-1])
        with patch.object(fixtures.V, "node22", return_value=("fixed-node", {})), patch.object(
                fixtures.V.subprocess, "run", return_value=type("Result", (), {
                    "returncode": 0, "stderr": "", "stdout": '{"verified":true}'})()):
            with self.assertRaisesRegex(ValueError, "unexpected source history replay output"):
                fixtures.V.source_context(evidence, self.entry, self.plan, self.native, self.route, self.saved["bundle"])

    def test_full_gate_rejects_expanded_context_before_claiming_route_success(self):
        source = self.read(self.route["sourceRecord"])
        source["bundle"]["context"]["threads"].append({"threadId": "foreign", "messages": []})
        source["bundle"]["digest"] = fixtures.V.digest(fixtures.V.canonical(
            {k: v for k, v in source["bundle"].items() if k != "digest"}))
        self.route["sourceRecord"] = fixtures.ref(self.root, self.route["sourceRecord"]["path"], source)
        (self.root / "product-evidence-index.json").write_bytes(fixtures.encode(self.index))
        with self.assertRaisesRegex(ValueError, "requires terminal supplement"):
            fixtures.V.product_handoff(self.root)

    def test_full_gate_accepts_replayed_supplement_with_exact_transferred_context(self):
        bundle = self.saved["bundle"]
        bundle["digest"] = fixtures.V.digest(fixtures.V.canonical({k: v for k, v in bundle.items() if k != "digest"}))
        plan, native = self.read(self.route["plan"]), self.read(self.route["native"])
        context = fixtures.encode(bundle)
        fixtures.set_context(plan, native, context)
        self.route["context"] = fixtures.ref(self.root, self.route["context"]["path"], context)
        self.route["plan"] = fixtures.ref(self.root, self.route["plan"]["path"], plan)
        self.route["native"] = fixtures.ref(self.root, self.route["native"]["path"], native)
        destination = self.read(self.route["destinationRecord"])
        destination["digest"] = bundle["digest"]
        self.route["destinationRecord"] = fixtures.ref(self.root, self.route["destinationRecord"]["path"], destination)
        ui = self.read(self.route["ui"])
        ui["bundleDigest"] = bundle["digest"]
        self.route["ui"] = fixtures.ref(self.root, self.route["ui"]["path"], ui)
        self.save()
        fixtures.V.product_handoff(self.root)


class PreviewMetadataTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix="invented-preview-metadata-")
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name).resolve()
        self.index = fixtures.invented_evidence(self.root)
        self.route = self.index["handoff"]["routes"][0]
        self.destination = self.read(self.route["destinationRecord"])
        self.bundle = self.read(self.route["sourceRecord"])["bundle"]
        native = self.read(self.route["native"])
        first = next(r for r in native["parent"]["runs"] if r["id"] != native["outcome"]["automaticWakeRunId"])
        self.initial = next(m for m in native["parent"]["messages"] if m["id"] == first["userMessageId"])
        self.destination["metadata"] = {k: self.bundle[k] for k in (
            "manifest", "sourceEnvironmentId", "sourceProjectId", "sourceThreadId", "digest")}

    def read(self, reference):
        return json.loads((self.root / reference["path"]).read_bytes())

    def test_optional_metadata_requires_exact_five_transferred_fields(self):
        fixtures.V.product_launch(self.destination, self.initial, self.bundle)
        del self.destination["metadata"]
        fixtures.V.product_launch(self.destination, self.initial, self.bundle)

    def test_each_metadata_field_and_exact_inventory_is_bound(self):
        baseline = copy.deepcopy(self.destination)
        for field in baseline["metadata"]:
            for action in ("change", "remove"):
                with self.subTest(field=field, action=action):
                    self.destination = copy.deepcopy(baseline)
                    if action == "change":
                        self.destination["metadata"][field] = "foreign"
                    else:
                        del self.destination["metadata"][field]
                    with self.assertRaisesRegex(ValueError, "preview metadata"):
                        fixtures.V.product_launch(self.destination, self.initial, self.bundle)

    def test_null_extra_or_context_metadata_is_rejected(self):
        baseline = copy.deepcopy(self.destination["metadata"])
        for metadata in (None, {}, {**baseline, "context": self.bundle["context"]}):
            self.destination["metadata"] = metadata
            with self.assertRaisesRegex(ValueError, "preview metadata"):
                fixtures.V.product_launch(self.destination, self.initial, self.bundle)

    def test_metadata_does_not_relax_launch_or_native_first_message(self):
        self.initial["text"] += " extra seeded answer"
        with self.assertRaisesRegex(ValueError, "native first message"):
            fixtures.V.product_launch(self.destination, self.initial, self.bundle)

    def test_complete_handoff_accepts_actual_optional_metadata_schema(self):
        self.route["destinationRecord"] = fixtures.ref(
            self.root, self.route["destinationRecord"]["path"], self.destination)
        (self.root / "product-evidence-index.json").write_bytes(fixtures.encode(self.index))
        fixtures.V.product_handoff(self.root)
