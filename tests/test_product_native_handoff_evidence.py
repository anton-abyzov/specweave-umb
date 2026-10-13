"""Invented replay evidence; never an operational native session receipt."""
import copy
import json
from pathlib import Path
import tempfile
import unittest

import test_product_handoff_evidence as fixtures


class NativeDiscoveryReplayTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="invented-native-discovery-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.evidence = fixtures.V.Evidence.__new__(fixtures.V.Evidence)
        self.evidence.root = self.root

    def fixture(self, mode, inputs=None):
        data = json.loads((fixtures.FIXTURES / f"product_native_{mode}.json").read_bytes())
        self.assertTrue(data["synthetic"])
        data["receipt"]["temporarySessionRevoked"] = True
        item = {"id": "invented-discovery", "type": "dynamic_tool", "runId": "first",
                "toolName": "studio-code.studio_thread_list", "input": inputs or {}, "status": "completed"}
        for key in ("parent", "rawParent"):
            data["receipt"][key]["turnItems"].insert(0, copy.deepcopy(item))
        return data

    def replay(self, data):
        plan = fixtures.ref(self.root, "plan.json", data["plan"])
        receipt = fixtures.ref(self.root, "receipt.json", data["receipt"])
        return fixtures.V.replay(self.evidence, plan, receipt)

    def reject_inputs(self, inputs):
        for mode in ("source", "destination"):
            for arguments in inputs:
                with self.subTest(mode=mode, arguments=arguments):
                    with self.assertRaisesRegex(ValueError, "native evidence replay failed"):
                        self.replay(self.fixture(mode, arguments))

    def test_implicit_owned_project_is_allowed_in_actual_fixed_replay(self):
        for mode in ("source", "destination"):
            for arguments in ({}, {"includeSubagents": True, "limit": 30}, {"limit": 100}):
                self.replay(self.fixture(mode, arguments))

    def test_explicit_owned_project_remains_allowed(self):
        for mode in ("source", "destination"):
            data = self.fixture(mode)
            for key in ("parent", "rawParent"):
                data["receipt"][key]["turnItems"][0]["input"] = {
                    "projectId": data["plan"]["projectId"], "includeSubagents": False, "limit": 1}
            self.replay(data)

    def test_foreign_or_null_project_cannot_inherit_scope(self):
        self.reject_inputs([{"projectId": "foreign"}, {"projectId": None}])

    def test_machine_and_unknown_options_remain_forbidden(self):
        self.reject_inputs([{"machine": "local"}, {"machine": "m3"}, {"cursor": 0}, {"view": "all"}])

    def test_limits_and_types_remain_bounded(self):
        self.reject_inputs([{"limit": 0}, {"limit": 101}, {"limit": 1.5}, {"limit": "30"},
                            {"includeSubagents": "true"}])

    def test_implicit_discovery_cannot_run_twice(self):
        for mode in ("source", "destination"):
            data = self.fixture(mode)
            for key in ("parent", "rawParent"):
                item = copy.deepcopy(data["receipt"][key]["turnItems"][0])
                item["id"] += "-duplicate"
                data["receipt"][key]["turnItems"].append(item)
            with self.assertRaisesRegex(ValueError, "native evidence replay failed"):
                self.replay(data)

    def test_implicit_discovery_is_not_available_to_worker(self):
        for mode in ("source", "destination"):
            data = self.fixture(mode)
            item = data["receipt"]["parent"]["turnItems"].pop(0)
            data["receipt"]["rawParent"]["turnItems"].pop(0)
            item["runId"] = data["receipt"]["worker"]["runs"][0]["id"]
            data["receipt"]["worker"]["turnItems"].append(item)
            with self.assertRaisesRegex(ValueError, "native evidence replay failed"):
                self.replay(data)

    def test_implicit_discovery_still_requires_exact_coordinator(self):
        for mode in ("source", "destination"):
            for field in ("id", "projectId"):
                data = self.fixture(mode)
                for key in ("parent", "rawParent"):
                    data["receipt"][key]["thread"][field] = "foreign"
                with self.assertRaisesRegex(ValueError, "native evidence replay failed"):
                    self.replay(data)


class PersistedProductLaunchTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="invented-product-launch-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.index = fixtures.invented_evidence(self.root)
        self.route = self.index["handoff"]["routes"][0]
        self.destination = self.read(self.route["destinationRecord"])
        native = self.read(self.route["native"])
        first = next(run for run in native["parent"]["runs"]
                     if run["id"] != native["outcome"]["automaticWakeRunId"])
        self.initial = next(m for m in native["parent"]["messages"] if m["id"] == first["userMessageId"])

    def read(self, reference):
        return json.loads((self.root / reference["path"]).read_bytes())

    def reject(self):
        with self.assertRaises(ValueError):
            fixtures.V.product_launch(self.destination, self.initial)

    def test_actual_launch_schema_binds_completed_native_message(self):
        fixtures.V.product_launch(self.destination, self.initial)

    def test_every_launch_identity_and_context_field_is_bound(self):
        baseline = copy.deepcopy(self.destination)
        for field in self.destination["launch"]:
            with self.subTest(field=field):
                self.destination = copy.deepcopy(baseline)
                self.destination["launch"][field] = "invented foreign value"
                self.reject()

    def test_missing_or_extra_launch_fields_fail(self):
        baseline = copy.deepcopy(self.destination)
        for field in baseline["launch"]:
            with self.subTest(field=field):
                self.destination = copy.deepcopy(baseline)
                del self.destination["launch"][field]
                self.reject()
        self.destination = baseline
        self.destination["launch"]["runtimeMode"] = "full-access"
        self.reject()

    def test_receive_replay_cannot_replace_original_persisted_record(self):
        self.destination["receipt"]["replayed"] = True
        self.reject()

    def test_native_text_alone_does_not_prove_launch_message_identity(self):
        self.initial["id"] = "unrelated-start-with-same-text"
        self.reject()

    def test_native_text_cannot_reseed_a_different_answer(self):
        self.initial["text"] += " The answer is already green."
        self.reject()

    def test_full_gate_rejects_missing_launch_even_with_completed_native_cycle(self):
        del self.destination["launch"]
        reference = self.route["destinationRecord"]
        reference.update(fixtures.ref(self.root, reference["path"], self.destination))
        (self.root / "product-evidence-index.json").write_bytes(fixtures.encode(self.index))
        with self.assertRaisesRegex(ValueError, "unexpected persisted destination record"):
            fixtures.V.product_handoff(self.root)

    def test_launch_intent_does_not_replace_actual_native_completion(self):
        native = self.read(self.route["native"])
        native["status"] = "failed"
        reference = self.route["native"]
        reference.update(fixtures.ref(self.root, reference["path"], native))
        (self.root / "product-evidence-index.json").write_bytes(fixtures.encode(self.index))
        with self.assertRaisesRegex(ValueError, "native supervision or temporary session cleanup incomplete"):
            fixtures.V.product_handoff(self.root)
