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

    def update_task(self, data, task):
        receipt = data['receipt']
        for key in ('parent', 'rawParent'):
            next(i for i in receipt[key]['turnItems'] if i.get('toolName') == 'studio-code.delegate_task')['input']['task'] = task
        record = next(r for r in receipt['approvals'] if 'delegationRouting' in r['payload'])
        record['payload']['action']['input']['task'] = task
        fixtures.rehash_native(receipt)

    def test_context_bearing_prose_does_not_determine_executable_paths(self):
        for prose in ('Read fixture/{case.mjs,case.check.mjs,README.md}.',
                      'Read case.mjs, case.check.mjs, README.md under the fixture directory.',
                      'Continue the transferred diagnostic.',
                      'Historical /foreign/source is reference material only.'):
            data = self.inherited()
            self.update_task(data, ' '.join([prose, *data['plan']['contextRequired']]))
            self.replay(data)
        for task in ('', ' ', 'x' * 40000):
            data = self.inherited()
            self.update_task(data, task)
            with self.assertRaises(ValueError): self.replay(data)

    def test_prose_does_not_authorize_foreign_actual_read_or_edit(self):
        for operation in ('read', 'edit'):
            data = self.inherited()
            self.update_task(data, ' '.join(['Continue the diagnostic.', *data['plan']['contextRequired']]))
            if operation == 'read':
                item = next(i for i in data['receipt']['worker']['turnItems']
                            if i['type'] == 'command_execution')
                item['input'] = '/bin/cat /foreign/case.mjs'
            else:
                item = next(i for i in data['receipt']['worker']['turnItems'] if i['type'] == 'file_change')
                item['changes'][0]['path'] = '/foreign/case.mjs'
            fixtures.rehash_native(data['receipt'])
            with self.assertRaises(ValueError): self.replay(data)

    def test_actual_frozen_reads_remain_required(self):
        for kind in ('read-context', 'read-continuation', 'read-test', 'read-readme', 'read-implementation'):
            data = self.inherited()
            receipt = data['receipt']
            output = next(o for o in receipt['outputs'] if o['kind'] == kind and o['role'] == 'worker')
            receipt['outputs'].remove(output)
            receipt['worker']['turnItems'] = [i for i in receipt['worker']['turnItems'] if i['id'] != output['itemId']]
            with self.assertRaises(ValueError): self.replay(data)


class NativeWorkerCapabilitiesReplayTests(unittest.TestCase):
    """Invented data tests one automatic read without adding worker permissions."""
    setUp = NativeDiscoveryReplayTests.setUp
    replay = NativeDiscoveryReplayTests.replay

    def fixture(self, mode):
        data = json.loads((fixtures.FIXTURES / f"product_native_{mode}.json").read_bytes())
        self.assertTrue(data["synthetic"])
        data["receipt"]["temporarySessionRevoked"] = True
        worker = data["receipt"]["worker"]
        worker["turnItems"].append({"id": "invented-worker-capabilities", "type": "dynamic_tool",
            "toolName": "studio-code.orchestrator_capabilities", "input": {}, "status": "completed",
            "threadId": worker["thread"]["id"], "runId": worker["runs"][0]["id"]})
        return data

    def reject(self, mutate):
        for mode in ("source", "destination"):
            data = self.fixture(mode)
            mutate(data["receipt"]["worker"])
            with self.assertRaisesRegex(ValueError, "native evidence replay failed"):
                self.replay(data)

    def test_single_empty_completed_capability_read_remains_replayable(self):
        for mode in ("source", "destination"):
            self.replay(self.fixture(mode))

    def test_extra_inputs_null_and_nonobject_are_rejected(self):
        for value in (None, [], {"projectId": "foreign"}, {"machine": "local"}, {"readOnly": True}):
            self.reject(lambda worker: worker["turnItems"][-1].update(input=value))
        self.reject(lambda worker: worker["turnItems"][-1].pop("input"))

    def test_duplicate_capability_read_is_rejected(self):
        def duplicate(worker):
            worker["turnItems"].append({**worker["turnItems"][-1], "id": "second"})
        self.reject(duplicate)

    def test_other_worker_tools_and_foreign_namespace_remain_rejected(self):
        for name in ("studio-code.delegate_task", "studio-code.studio_thread_list",
                     "studio-code.task_status", "studio-code.studio_thread_read",
                     "foreign.orchestrator_capabilities"):
            self.reject(lambda worker: worker["turnItems"][-1].update(toolName=name))

    def test_pending_failed_or_unknown_status_never_proves_completed_read(self):
        for status in ("running", "waiting", "failed", "interrupted", "unknown", None):
            self.reject(lambda worker: worker["turnItems"][-1].update(status=status))
        self.reject(lambda worker: worker["turnItems"][-1].pop("status"))

    def test_capabilities_cannot_substitute_worker_profile_or_single_run(self):
        self.reject(lambda worker: worker["thread"]["modelSelection"].update(model="foreign"))
        self.reject(lambda worker: worker["runs"].append({"id": "extra", "status": "completed"}))


def invented_graph(native):
    """Upgrade only invented data; original operational source receipts stay intact."""
    def times(value, key=None):
        if isinstance(value, dict): return {k: times(v, k) for k, v in value.items()}
        if isinstance(value, list): return [times(v) for v in value]
        if key in ('startedAt', 'completedAt', 'createdAt', 'requestedAt', 'updatedAt') and isinstance(value, str):
            return value.replace('2026-10-13T12:01:', '2026-10-13T12:07:').replace('2026-10-13T12:02:', '2026-10-13T12:08:')
        return value
    r = times(native)
    r['workflowVersion'] = 2
    w = r.pop('worker')
    r['workers'] = [w]
    parent, task = r['parent'], r['parent']['subagents'][0]
    delegate = next(i for i in parent['turnItems'] if i.get('toolName') == 'studio-code.delegate_task')
    task.update(threadId=parent['thread']['id'], createdBy='agent', prompt=delegate['input']['task'],
                startedAt=delegate['startedAt'])
    w['thread'].update(lineage={'parentThreadId': parent['thread']['id'], 'relationshipToParent': 'subagent',
                               'rootThreadId': parent['thread']['id']}, forkedFrom={'type': 'node', 'nodeId': task['id']})
    run = w['runs'][0]
    run.update(threadId=w['thread']['id'], userMessageId=w['thread']['id'] + '-start',
               requestedAt=task['startedAt'], startedAt=task['startedAt'], completedAt=task['completedAt'])
    w['messages'] = [dict(id=run['userMessageId'], threadId=w['thread']['id'], runId=run['id'],
                         createdBy='agent', creationSource='mcp', senderThreadId=parent['thread']['id'],
                         text=task['prompt'], createdAt=task['startedAt'])]
    for projection in (parent, w):
        ids = {i.get('providerTurnId') for i in projection['turnItems'] + projection['runtimeRequests']}
        known = {t['id'] for t in projection['providerTurns']}
        projection['providerTurns'].extend(dict(id=i, status='completed') for i in sorted(ids - {None} - known))
    wake = next(x for x in parent['runs'] if x['id'] == r['outcome']['automaticWakeRunId'])
    wake.update(startedAt='2026-10-13T12:08:00Z', completedAt='2026-10-13T12:09:00Z')
    r['rawParent'] = copy.deepcopy(parent)
    old = r['outcome']
    r['outcome'] = dict(initialRunId=task['runId'], completionRunId=wake['id'],
        workerThreadIds=[w['thread']['id']], editingWorkerThreadId=w['thread']['id'],
        edges=[dict(taskId=task['id'], parentRunId=task['runId'], workerThreadId=w['thread']['id'],
                    workerRunId=run['id'], wakeRunId=wake['id'], completionState='delivered')],
        workerTexts=[dict(threadId=w['thread']['id'], text=old['workerText'])], relayText=old['relayText'])
    for output in r['outputs']:
        if output['kind'] == 'read-implementation':
            output['implementationSha256'] = fixtures.V.digest(output['response']['output'].encode())
    fixtures.rehash_native(r)
    return r


class NativeGraphEnvelopeTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix='invented-graph-envelope-')
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name).resolve()
        self.index = fixtures.invented_evidence(self.root)
        for route in self.index['handoff']['routes']:
            old = route['native']
            native = invented_graph(json.loads((self.root / old['path']).read_bytes()))
            route['native'] = fixtures.ref(self.root, old['path'], native)
        self.save()

    def save(self):
        (self.root / 'product-evidence-index.json').write_bytes(fixtures.encode(self.index))

    def update(self, mutate):
        route = self.index['handoff']['routes'][0]
        p, n = (json.loads((self.root / route[k]['path']).read_bytes()) for k in ('plan', 'native'))
        mutate(p, n)
        fixtures.rehash_native(n)
        for key, value in [('plan', p), ('native', n)]:
            route[key] = fixtures.ref(self.root, route[key]['path'], value)
        self.save()

    def test_six_graph_routes_replay_with_unchanged_legacy_sources(self):
        fixtures.V.product_handoff(self.root)

    def test_every_graph_worker_interval_is_bracketed(self):
        route = self.index['handoff']['routes'][0]
        n = json.loads((self.root / route['native']['path']).read_bytes())
        n['workers'].append({'runs': [{'startedAt': '2026-10-13T13:00:00Z',
                                      'completedAt': '2026-10-13T13:01:00Z'}]})
        self.assertIn('2026-10-13T13:01:00Z', fixtures.V.native_times(n))
        n['workers'][-1]['runs'][0]['completedAt'] = '2026-10-13T12:59:00Z'
        with self.assertRaisesRegex(ValueError, 'interval invalid'): fixtures.V.native_times(n)

    def test_forged_initial_run_cannot_replace_persisted_product_start(self):
        self.update(lambda p, n: n['outcome'].update(initialRunId='wake'))
        with self.assertRaisesRegex(ValueError, 'native evidence replay failed'): fixtures.V.product_handoff(self.root)

    def test_unexplained_worker_or_changed_completion_never_enters_envelope(self):
        self.update(lambda p, n: n['outcome']['workerThreadIds'].append('unrelated'))
        with self.assertRaisesRegex(ValueError, 'native evidence replay failed'): fixtures.V.product_handoff(self.root)

    def test_prerequisite_worker_cannot_supply_missing_editor_context(self):
        def change(p, n):
            output = next(o for o in n['outputs'] if o['kind'] == 'read-context' and o['role'] == 'worker')
            output['threadId'] = 'unrelated'
        self.update(change)
        with self.assertRaisesRegex(ValueError, 'native evidence replay failed'): fixtures.V.product_handoff(self.root)


class NativeSyntheticApprovalParentTests(unittest.TestCase):
    def projection(self):
        native = {'driver': 'codex', 'nativeId': 'mcp-elicitation:studio-code', 'strength': 'strong'}
        return {'thread': {'id': 'owned'}, 'runs': [{'id': 'run'}], 'providerTurns': [{'id': 'turn'}],
            'nodes': [{'id': 'approval-node', 'threadId': 'owned', 'runId': 'run', 'providerTurnId': 'turn',
                'kind': 'approval_request', 'parentNodeId': 'node:provider:codex:native-item:mcp-elicitation%3Astudio-code',
                'nativeItemRef': native, 'runtimeRequestId': 'request'}],
            'runtimeRequests': [{'id': 'request', 'nodeId': 'approval-node', 'providerTurnId': 'turn',
                'kind': 'mcp-elicitation', 'nativeRequestRef': native}],
            'turnItems': [{'id': 'display', 'type': 'approval_request', 'requestId': 'request',
                'threadId': 'owned', 'runId': 'run', 'nodeId': 'approval-node', 'providerTurnId': 'turn',
                'nativeItemRef': native, 'appName': 'studio-code', 'requestKind': 'mcp-elicitation'}]}

    def run_binding(self, value):
        import subprocess
        node, env = fixtures.V.node22()
        module = fixtures.V.RUNNER.with_name('product_native_evidence.mjs').as_uri()
        script = ('import fs from "node:fs"; import {assertProjectionBindings} from ' + json.dumps(module)
                  + '; assertProjectionBindings(JSON.parse(fs.readFileSync(0,"utf8")));')
        return subprocess.run([node, '--input-type=module', '-e', script], input=json.dumps(value),
                              text=True, capture_output=True, env=env).returncode

    def test_exact_codex_synthetic_approval_parent_is_supported(self):
        self.assertEqual(self.run_binding(self.projection()), 0)

    def test_missing_parent_exception_cannot_hide_foreign_or_wrong_kind_rows(self):
        mutations = [lambda p: p['nodes'][0].update(parentNodeId='foreign'),
            lambda p: p['nodes'][0].update(kind='tool_call'),
            lambda p: p['turnItems'][0].update(appName='foreign'),
            lambda p: p['turnItems'][0].update(runId='foreign'),
            lambda p: p['runtimeRequests'][0].update(nativeRequestRef={'driver': 'codex', 'nativeId': 'foreign', 'strength': 'strong'})]
        for mutate in mutations:
            with self.subTest(mutate=mutate):
                value = self.projection(); mutate(value)
                self.assertNotEqual(self.run_binding(value), 0)
