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


class NativeWorkerRoutingReplayTests(unittest.TestCase):
    """The inherited profile is evidence, not permission to guess a worker model."""
    setUp = NativeDiscoveryReplayTests.setUp
    replay = NativeDiscoveryReplayTests.replay
    def inherited(self):
        data = json.loads((fixtures.FIXTURES / 'product_native_destination.json').read_bytes())
        self.assertTrue(data['synthetic'])
        p, receipt = data['plan'], data['receipt']
        receipt['temporarySessionRevoked'] = True
        for key in ('parent', 'rawParent'):
            next(i for i in receipt[key]['turnItems'] if i.get('toolName') == 'studio-code.delegate_task')['input'].pop('target')
        record = next(r for r in receipt['approvals'] if r['payload']['action'].get('toolName') == 'studio-code.delegate_task')
        record['payload']['action']['input'].pop('target')
        record['payload']['delegationRouting'] = {'projectId': p['projectId'], 'workspaceRoot': p['workspaceRoot'],
            'coordinatorThreadId': p['coordinatorId'], 'defaultModelSelection': p['profile']['worker'],
            'workerMachine': None, 'autoResume': False}
        fixtures.rehash_native(receipt)
        return data

    def test_omitted_target_uses_exact_retained_project_routing(self):
        self.replay(self.inherited())

    def test_rehashed_missing_or_changed_routing_never_substitutes_worker_profile(self):
        mutations = [lambda r: r['payload'].pop('delegationRouting'),
                     lambda r: r['payload']['delegationRouting'].update(defaultModelSelection={'instanceId': 'codex', 'model': 'other'}),
                     lambda r: r['payload']['delegationRouting'].update(projectId='foreign'),
                     lambda r: r['payload']['delegationRouting'].update(workerMachine='m3'),
                     lambda r: r['payload']['delegationRouting'].update(autoResume=True)]
        for mutate in mutations:
            data = self.inherited()
            record = next(r for r in data['receipt']['approvals'] if 'delegationRouting' in r['payload'])
            mutate(record)
            fixtures.rehash_native(data['receipt'])
            with self.assertRaises(ValueError): self.replay(data)

    def test_actual_worker_cannot_differ_even_when_saved_default_matches(self):
        data = self.inherited()
        data['receipt']['worker']['thread']['modelSelection'] = {'instanceId': 'codex', 'model': 'other'}
        with self.assertRaises(ValueError): self.replay(data)

    def test_relative_paths_remain_anchored_to_exact_workspace_and_adjacent_test(self):
        data = self.inherited()
        p, receipt = data['plan'], data['receipt']
        task = ' '.join([p['workspaceRoot'], str(Path(p['paths']['implementation']).relative_to(p['workspaceRoot'])),
                         Path(p['paths']['test']).name, *p['contextRequired']])
        def update(text):
            for key in ('parent', 'rawParent'):
                next(i for i in receipt[key]['turnItems'] if i.get('toolName') == 'studio-code.delegate_task')['input']['task'] = text
            record = next(r for r in receipt['approvals'] if 'delegationRouting' in r['payload'])
            record['payload']['action']['input']['task'] = text
            fixtures.rehash_native(receipt)
        update(task)
        self.replay(data)
        for changed in [task.replace(p['workspaceRoot'], '/foreign'),
                        task.replace(Path(p['paths']['test']).name, 'foreign/'+Path(p['paths']['test']).name)]:
            update(changed)
            with self.assertRaises(ValueError): self.replay(data)
