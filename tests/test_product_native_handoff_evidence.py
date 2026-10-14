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


class NativeReadDiscoveryReplayTests(unittest.TestCase):
    """Invented inputs exercise the fixed public module, never a host command."""
    def invoke(self, body, value):
        import subprocess
        node, env = fixtures.V.node22()
        module = fixtures.V.RUNNER.with_name('product_native_evidence.mjs').as_uri()
        script = ('import fs from "node:fs"; import assert from "node:assert/strict"; import * as M from '
                  + json.dumps(module) + '; const x=JSON.parse(fs.readFileSync(0,"utf8"));' + body)
        result = subprocess.run([node, '--input-type=module', '-e', script], input=json.dumps(value),
                                text=True, capture_output=True, env=env)
        self.assertEqual(result.returncode, 0, result.stderr)

    def data(self):
        data = json.loads((fixtures.FIXTURES / 'product_native_destination.json').read_bytes())
        self.assertTrue(data['synthetic'])
        data['receipt'] = invented_graph(data['receipt'])
        return data

    def test_literal_metadata_batch_stays_read_only_and_binds_actual_output(self):
        self.invoke('''const p={...x.plan,_graph:true}, b=x.receipt.baseline;
          const input="git rev-parse HEAD\\ngit status --porcelain=v1\\ngit -C "
            +p.nestedRoot+" rev-parse HEAD\\ngit -C "+p.nestedRoot+" status --porcelain=v1";
          const e=M.classifyCommand(p,input,"worker"); assert.equal(e.kind,"git-read-batch");
          const o={response:{output:b.repos.root.sha+"\\n"+b.repos.nested.sha+"\\n"},readState:b};
          M.assertDiscoveryOutput(p,e,o,b); o.response.output="forged\\n";
          assert.throws(()=>M.assertDiscoveryOutput(p,e,o,b));
          const changed=structuredClone(b); changed.repos.nested.branch="codex/foreign";
          assert.throws(()=>M.assertLocalMutation(p,e.kind,changed,b,[]));
          for(const suffix of ["git push","cat .env","git status; touch bad","git -C /foreign rev-parse HEAD"])
            assert.throws(()=>M.classifyCommand(p,"git rev-parse HEAD\\n"+suffix,"worker"));
          assert.throws(()=>M.classifyCommand(x.plan,input,"worker"));''', self.data())

    def test_instruction_discovery_requires_exact_path_and_real_absence_output(self):
        self.invoke('''const p={...x.plan,_graph:true}, path=p.nestedRoot+"/AGENTS.md";
          const e=M.classifyCommand(p,"cat '"+path+"'","worker");
          assert.equal(e.kind,"instructions-nested");
          const o={discovery:{path,parentRealpath:p.nestedRoot,exists:false},
            response:{status:"failed",exitCode:1,output:"cat: "+path+": No such file or directory\\n"}};
          M.assertDiscoveryOutput(p,e,o,x.receipt.baseline);
          for(const output of ["permission denied\\n","","cat: /foreign/AGENTS.md: No such file or directory\\n"])
            assert.throws(()=>M.assertDiscoveryOutput(p,e,{...o,response:{...o.response,output}},x.receipt.baseline));
          for(const file of [p.nestedRoot+"/.env",p.nestedRoot+"/child/AGENTS.md","/foreign/AGENTS.md"])
            assert.throws(()=>M.classifyCommand(p,"cat '"+file+"'","worker"));
          assert.throws(()=>M.assertInstructionSnapshot(p,e.kind,{...o.discovery,parentRealpath:"/foreign"}));''', self.data())

    def test_existing_instruction_bytes_require_matching_hash(self):
        self.invoke('''const p={...x.plan,_graph:true}, path=p.nestedRoot+"/AGENTS.md", text="Read only.\\n";
          const e={kind:"instructions-nested"}, o={discovery:{path,parentRealpath:p.nestedRoot,exists:true,
            realpath:path,isFile:true,isSymbolicLink:false,size:text.length,sha256:M.sha256(text)},
            response:{status:"completed",exitCode:0,output:text}};
          M.assertDiscoveryOutput(p,e,o,x.receipt.baseline);
          assert.throws(()=>M.assertDiscoveryOutput(p,e,{...o,response:{...o.response,output:"changed"}},x.receipt.baseline));
          assert.throws(()=>M.assertInstructionSnapshot(p,e.kind,{...o.discovery,isSymbolicLink:true}));''', self.data())

    def test_old_sha_after_commit_cannot_replace_required_final_native_head(self):
        self.invoke('''const p=x.plan,r=x.receipt; M.verifyReceipt(p,r);
          const out=r.outputs.find(o=>o.kind==="git-final-head"), item=r.workers[0].turnItems.find(i=>i.id===out.itemId);
          item.output=p.originalShas.nested+"\\n"; out.response=structuredClone(item);
          out.sha256=M.sha256(JSON.stringify(item));
          assert.throws(()=>M.verifyReceipt(p,r),/post-commit-final-head-stale/);''', self.data())


class NativeRawPathAndBatchRegressionTests(unittest.TestCase):
    """Pure observer regressions ported from reviewed private suites; invented data only."""
    data = NativeReadDiscoveryReplayTests.data

    def run_ported(self, body):
        import subprocess
        node, env = fixtures.V.node22()
        module = fixtures.V.RUNNER.with_name('product_native_evidence.mjs').as_uri()
        script = ('import fs from "node:fs"; import assert from "node:assert/strict"; '
                  'import {relative} from "node:path"; import * as M from ' + json.dumps(module)
                  + '; const x=JSON.parse(fs.readFileSync(0,"utf8")); '
                  + 'const {classifyCommand,sha256,assertFileReadBatchSnapshot,assertFileReadBatchOutput,'
                  'assertWorkerReadsBeforeEdit,makeObserver,verifyReceipt,approvalPayload,assertLocalMutation,'
                  'assertDiscoveryOutput,assertMetadataBatchState}=M; '
                  + 'const cases=[]; const test=(name,run)=>{try { const result=run(); '
                  'assert.ok(!result?.then,"pure synchronous cases only"); cases.push(name); '
                  '} catch(error) {throw new Error(name+": "+error.stack);}}; '
                  + body + '; console.log(JSON.stringify(cases));')
        result = subprocess.run([node, '--input-type=module', '-e', script],
                                input=json.dumps(self.data()), text=True, capture_output=True, env=env)
        self.assertEqual(result.returncode, 0, result.stderr)
        cases = json.loads(result.stdout)
        self.assertTrue(cases)
        self.assertEqual(len(cases), len(set(cases)))

    def test_raw_parent_path_boundaries(self):
        self.run_ported(r'''
const p={...x.plan,_graph:true};
const q=s=>"'"+s.replaceAll("'","'\\''")+"'";
const parentAlias=path=>path.replace(/\/([^/]+)$/, '/link/../$1');
const forbidden=[
  ['instruction-cat', `cat ${q(p.workspaceRoot+'/link/../AGENTS.md')}`],
  ['fixture-cat', `cat ${q(parentAlias(p.paths.implementation))}`],
  ['relative-cat', 'cat link/../AGENTS.md'],
  ['cd', `cd ${q(p.workspaceRoot+'/link/..')} && git rev-parse HEAD`],
  ['git-C', `git -C ${q(p.nestedRoot+'/link/..')} rev-parse HEAD`],
  ['node-test', `${q(p.nodePath)} --test ${q(parentAlias(p.paths.test))}`],
  ['git-diff', `git -C ${q(p.nestedRoot)} diff -- ${q(parentAlias(p.paths.implementation))}`],
  ['git-add', `git -C ${q(p.nestedRoot)} add -- ${q(parentAlias(p.paths.implementation))}`],
  ['git-batch', `git -C ${q(p.workspaceRoot)} rev-parse HEAD\ngit -C ${q(p.nestedRoot+'/link/..')} status --porcelain=v1`],
  ['wrapped', `/bin/zsh -lc ${q('cat '+q(p.workspaceRoot+'/link/../AGENTS.md'))}`],
  ['quoted-component', `cat ${q(p.workspaceRoot)}'/link/'".."'/AGENTS.md'`],
];
for(const [name,input] of forbidden)test('refuse raw parent traversal: '+name,()=>assert.throws(()=>classifyCommand(p,input,'worker'),/raw-parent-path-segment-refused/));
for(const [name,input,kind]of [
  ['instruction',`cat ${q(p.workspaceRoot+'/AGENTS.md')}`,'instructions-root'],
  ['instruction-dot','cat ./AGENTS.md','instructions-root'],
  ['context',`cat ${q(p.paths.context)}`,'read-context'],
  ['test',`cd ${q(p.nestedRoot)} && ${q(p.nodePath)} --test ${q(p.paths.test)}`,'test'],
  ['git',`git -C ${q(p.nestedRoot)} rev-parse HEAD`,'git-final-head'],
])test('preserve intended command: '+name,()=>assert.equal(classifyCommand(p,input,'worker').kind,kind));
''')

    def test_exact_multifile_read_evidence(self):
        self.run_ported(r'''
const clone=structuredClone,q=s=>"'"+s.replaceAll("'","'\\''")+"'";
const keys=['implementation','test','readme','continuation','context'];
const frozenBody='frozen fixture body\n';
function fixture(){const f={p:structuredClone(x.plan),receipt:structuredClone(x.receipt)};return {...f,plan:{...f.p,_graph:true}};}
const command=(p,ks=keys.slice(0,3))=>'/bin/cat '+ks.map(k=>q(p.paths[k])).join(' ');
const snapshots=(p,ks=keys.slice(0,3),bodies={})=>ks.map(key=>{const data=Buffer.from(bodies[key]??frozenBody);return {key,path:p.paths[key],size:data.length,sha256:sha256(data),base64:data.toString('base64')};});
function record(p,ks=keys.slice(0,3)){const input=command(p,ks);return {threadId:'worker',role:'worker',kind:'file-read-batch',input,readFiles:snapshots(p,ks),readState:{files:Object.fromEntries(keys.map(k=>[k,{path:p.paths[k],sha256:p.frozen[k]}]))},response:{status:'completed',exitCode:0,output:frozenBody.repeat(ks.length),completedAt:'2026-10-13T12:00:14Z'}};}
for(const count of [2,3,4,5])test('cat accepts '+count+' exact unique frozen files',()=>{const {plan:p}=fixture(),ks=keys.slice(0,count);for(const role of ['worker','coordinator'])for(const cmd of [command(p,ks),`cd ${q(p.nestedRoot)} && cat ${ks.map(k=>q(relative(p.nestedRoot,p.paths[k]))).join(' ')}`,`/bin/zsh -lc ${q(command(p,ks))}`]){if(cmd.includes('..'))continue;const entry=classifyCommand(p,cmd,role);assert.equal(entry.kind,'file-read-batch');assert.deepEqual(entry.parts.map(e=>e.kind),ks.map(k=>'read-'+k));assertFileReadBatchOutput(p,entry,record(p,ks));}});
for(const [name,make]of Object.entries({duplicate:p=>command(p,['implementation','implementation']),duplicateAlias:p=>command(p,['implementation'])+' '+q(p.paths.implementation.replace('/case.mjs','/./case.mjs')),six:p=>command(p,keys)+' '+q(p.paths.implementation),foreign:p=>command(p,['implementation'])+' /etc/hosts',instructions:p=>command(p,['implementation'])+' '+q(p.workspaceRoot+'/AGENTS.md'),flag:p=>'/bin/cat -n '+keys.slice(0,2).map(k=>q(p.paths[k])).join(' '),flagEnd:p=>command(p)+' --',chain:p=>command(p)+' && git status',semicolon:p=>command(p)+'; touch bad',substitution:p=>command(p)+' $(whoami)',rawParent:p=>command(p,['implementation'])+' '+q(p.paths.test.replace('/case.check.mjs','/link/../case.check.mjs')),quotedParent:p=>command(p,['implementation'])+' '+q(p.nestedRoot)+"'/link/'\"..\"'/case.check.mjs'",newline:p=>command(p)+'\n'+command(p)}))test('multi-cat refuses '+name,()=>{const {plan:p}=fixture();assert.throws(()=>classifyCommand(p,make(p),'worker'));});
test('legacy and source grammar stay single-file only',()=>{const {p}=fixture();assert.throws(()=>classifyCommand(p,command(p),'worker'));assert.throws(()=>classifyCommand({...p,mode:'source'},command(p),'worker'));});
for(const [name,change]of Object.entries({missing:o=>o.readFiles.pop(),extra:o=>o.readFiles.push(clone(o.readFiles[0])),reordered:o=>o.readFiles.reverse(),foreignPath:o=>o.readFiles[0].path='/etc/hosts',wrongKey:o=>o.readFiles[0].key='context',forgedHash:o=>o.readFiles[0].sha256='f'.repeat(64),changedBytes:o=>o.readFiles[0].base64=Buffer.from('changed').toString('base64'),noncanonicalBase64:o=>o.readFiles[0].base64+='\n',missingSize:o=>delete o.readFiles[0].size,wrongSize:o=>o.readFiles[0].size++,oversize:o=>o.readFiles[0].size=2097152,extraKey:o=>o.readFiles[0].pretend=true,truncated:o=>o.response.output=o.response.output.slice(0,-1),extraOutput:o=>o.response.output+='forged',nonzero:o=>o.response.exitCode=1,failed:o=>o.response.status='failed'}))test('complete retained batch validation rejects '+name,()=>{const {plan:p}=fixture(),o=record(p),entry=classifyCommand(p,o.input,o.role);change(o);assert.throws(()=>assertFileReadBatchOutput(p,entry,o));});
test('byte boundaries bind varied content and ordering including empty/non-newline files',()=>{const {plan:p}=fixture(),bodies={implementation:'first',test:'',readme:'third\n'};for(const key of Object.keys(bodies))p.frozen[key]=sha256(bodies[key]);const o=record(p);o.readFiles=snapshots(p,keys.slice(0,3),bodies);o.response.output='firstthird\n';const e=classifyCommand(p,o.input,'worker');assertFileReadBatchOutput(p,e,o);o.readFiles.reverse();assert.throws(()=>assertFileReadBatchOutput(p,e,o));});
test('invalid UTF8 cannot masquerade as complete original bytes',()=>{const {plan:p}=fixture(),o=record(p),bytes=Buffer.from([255]);p.frozen.implementation=sha256(bytes);o.readState.files.implementation.sha256=sha256(bytes);Object.assign(o.readFiles[0],{size:1,sha256:sha256(bytes),base64:bytes.toString('base64')});o.response.output='�'+frozenBody.repeat(2);assert.throws(()=>assertFileReadBatchOutput(p,classifyCommand(p,o.input,'worker'),o),/output-bytes/);});
test('each batch file counts only for its actual worker before its edit',()=>{const {plan:p}=fixture(),o=makeObserver(p),r=record(p,keys);o.outputs.set('batch',r);const edit={threadId:'worker',startedAt:'2026-10-13T12:00:17Z'};assertWorkerReadsBeforeEdit(p,o,edit);r.threadId='prerequisite-worker';assert.throws(()=>assertWorkerReadsBeforeEdit(p,o,edit),/worker-frozen-read/);r.threadId='worker';r.response.completedAt='2026-10-13T12:00:18Z';assert.throws(()=>assertWorkerReadsBeforeEdit(p,o,edit),/worker-frozen-read/);r.response.completedAt='2026-10-13T12:00:14Z';r.readFiles[0].sha256='f'.repeat(64);assert.throws(()=>assertWorkerReadsBeforeEdit(p,o,edit));});
function batchReceipt(ks=keys.slice(0,3)){const f=fixture(),r=f.receipt,w=r.workers[0],remove=w.turnItems.filter(i=>i.type==='command_execution'&&ks.some(k=>classifyCommand(f.plan,i.input,'worker').kind==='read-'+k));const item=clone(remove[0]);Object.assign(item,{id:'batch-read',input:command(f.plan,ks),output:frozenBody.repeat(ks.length),nativeItemRef:{driver:'codex',strength:'strong',nativeId:'batch-native'}});w.turnItems=w.turnItems.filter(i=>!remove.some(old=>old.id===i.id));w.turnItems.push(item);r.outputs=r.outputs.filter(o=>!remove.some(old=>old.id===o.itemId));const a=clone(r.approvals.find(a=>a.kind==='branch'));Object.assign(a,{requestId:'batch-request',itemId:item.id,kind:'file-read-batch',readFiles:snapshots(f.plan,ks),readState:clone(r.baseline)});Object.assign(a.payload.request,{id:a.requestId,nativeRequestRef:clone(item.nativeItemRef)});a.payload.action={...clone(item),status:'waiting'};Object.assign(a.payload.approval,{id:'batch-approval',requestId:a.requestId,prompt:item.input});a.payloadSha256=sha256(JSON.stringify(a.payload));w.runtimeRequests.push({...clone(a.payload.request),status:'resolved',decision:'accept'});w.turnItems.push({...clone(a.payload.approval),status:'completed'});r.approvals.push(a);r.outputs.push({...record(f.plan,ks),itemId:item.id,runId:item.runId,response:clone(item),sha256:sha256(JSON.stringify(item))});return f;}
test('pure final replay accepts real batch relationships without inventing individual commands',()=>{const f=batchReceipt();assert.equal(verifyReceipt(f.p,f.receipt).verified,true);assert.equal(f.receipt.outputs.filter(o=>o.kind==='file-read-batch').length,1);});
for(const [name,change]of Object.entries({missingApproval:r=>r.approvals.pop(),approvalBytes:r=>r.approvals.at(-1).readFiles[0].base64+='AA',outputBytes:r=>r.outputs.at(-1).readFiles[0].base64+='AA',forgedOutput:r=>{r.outputs.at(-1).response.output+='forged';r.outputs.at(-1).sha256=sha256(JSON.stringify(r.outputs.at(-1).response));},missingFile:r=>r.outputs.at(-1).readFiles.pop(),lateRead:r=>{const i=r.workers[0].turnItems.find(i=>i.id==='batch-read');i.completedAt='2026-10-13T12:00:18Z';const o=r.outputs.at(-1);o.response=clone(i);o.sha256=sha256(JSON.stringify(i));}}))test('final batch replay rejects '+name,()=>{const f=batchReceipt();change(f.receipt);assert.throws(()=>verifyReceipt(f.p,f.receipt));});
test('all five files may share one actual cat, including retained context',()=>{const f=batchReceipt(keys);assert.equal(verifyReceipt(f.p,f.receipt).verified,true);});
test('post-edit implementation reread is exact current state but cannot earn original-read credit',()=>{const {plan:p}=fixture(),o=record(p,keys),bytes=Buffer.from('legitimate edited implementation\n');Object.assign(o.readFiles[0],{size:bytes.length,sha256:sha256(bytes),base64:bytes.toString('base64')});o.readState.files.implementation.sha256=sha256(bytes);o.response.output=bytes.toString('utf8')+frozenBody.repeat(4);assertFileReadBatchOutput(p,classifyCommand(p,o.input,'worker'),o);const observer=makeObserver(p);observer.outputs.set('post-edit-read',o);assert.throws(()=>assertWorkerReadsBeforeEdit(p,observer,{threadId:'worker',startedAt:'2026-10-13T12:00:17Z'}),/before-edit-implementation/);o.readState.files.implementation.sha256=p.frozen.implementation;assert.throws(()=>assertFileReadBatchOutput(p,classifyCommand(p,o.input,'worker'),o),/state-hash/);});
test('final replay retains a later changed implementation batch separately from original reads',()=>{const f=batchReceipt(),r=f.receipt,w=r.workers[0],oldApproval=r.approvals.at(-1),a=clone(oldApproval),o=clone(r.outputs.at(-1)),bytes=Buffer.from('edited implementation\n');r.after.files.implementation.sha256=sha256(bytes);r.testRecords[0].implementationSha256=sha256(bytes);const state=clone(r.baseline);state.repos.nested.branch=f.p.branch;state.files.implementation.sha256=sha256(bytes);const files=clone(a.readFiles);Object.assign(files[0],{size:bytes.length,sha256:sha256(bytes),base64:bytes.toString('base64')});a.itemId='reread-batch';a.requestId='reread-request';a.readFiles=files;a.readState=state;a.payload.request.id=a.requestId;a.payload.request.nativeRequestRef.nativeId='reread-native';Object.assign(a.payload.action,{id:a.itemId,nativeItemRef:clone(a.payload.request.nativeRequestRef),startedAt:'2026-10-13T12:00:18Z',completedAt:'2026-10-13T12:00:19Z',updatedAt:'2026-10-13T12:00:19Z',output:bytes.toString('utf8')+frozenBody.repeat(2)});Object.assign(a.payload.approval,{id:'reread-display',requestId:a.requestId});a.payloadSha256=sha256(JSON.stringify(a.payload));const item={...clone(a.payload.action),status:'completed'};w.turnItems.push(item,{...clone(a.payload.approval),status:'completed'});w.runtimeRequests.push({...clone(a.payload.request),status:'resolved',decision:'accept'});Object.assign(o,{itemId:a.itemId,readFiles:clone(files),readState:clone(state),response:clone(item),sha256:sha256(JSON.stringify(item))});r.approvals.push(a);r.outputs.push(o);assert.equal(verifyReceipt(f.p,r).verified,true);r.outputs=r.outputs.filter(x=>x.itemId!=='batch-read');assert.throws(()=>verifyReceipt(f.p,r));});
''')

    def test_metadata_states_and_head_provenance(self):
        self.run_ported(r'''
const clone=structuredClone;
const q=s=>"'"+s.replaceAll("'","'\\''")+"'";
function fixture(){const f={p:structuredClone(x.plan),receipt:structuredClone(x.receipt)};return {...f,plan:{...f.p,_graph:true}};}
const command=(p,head='rev-parse HEAD')=>`git -C ${q(p.nestedRoot)} ${head}\ngit -C ${q(p.nestedRoot)} status --porcelain=v1`;
function states(f){
  const original=clone(f.receipt.baseline),owned=clone(original),edited=clone(original),staged=clone(original),both=clone(original),committed=clone(f.receipt.after);
  const path=relative(f.p.nestedRoot,f.p.paths.implementation);
  for(const s of [owned,edited,staged,both])s.repos.nested.branch=f.p.branch;
  for(const [s,status]of [[edited,' M '],[staged,'M  '],[both,'MM ']]){s.repos.nested.status=status+path;s.files.implementation.sha256=f.receipt.after.files.implementation.sha256;}
  return {original,owned,edited,staged,both,committed};
}
function output(state,withPath=false){return (withPath?state.repos.nested.path+'\n':'')+state.repos.nested.sha+'\n'+(state.repos.nested.status?state.repos.nested.status+'\n':'');}
for(const name of ['original','owned','edited','staged','both','committed'])test('metadata batch accepts exact '+name+' state',()=>{
  const f=fixture(),state=states(f)[name];
  assertLocalMutation(f.plan,'git-read-batch',state,f.receipt.baseline,[]);
  for(const head of ['rev-parse HEAD','rev-parse --show-toplevel HEAD']){
    const entry=classifyCommand(f.plan,command(f.p,head),'worker');
    const record={readState:state,response:{output:output(state,head.includes('toplevel'))}};
    assertDiscoveryOutput(f.plan,entry,record,f.receipt.baseline);
    record.response.output+='unexpected\n';
    assert.throws(()=>assertDiscoveryOutput(f.plan,entry,record,f.receipt.baseline),/native-git-batch-output/);
  }
});
for(const [name,change]of Object.entries({
  foreignBranch:s=>s.repos.nested.branch='codex/foreign',
  rootHead:s=>s.repos.root.sha='f'.repeat(40),
  rootBranch:s=>s.repos.root.branch='foreign',
  rootDirty:s=>s.repos.root.status=' M file',
  rootPath:s=>s.repos.root.path='/foreign',
  nestedPath:s=>s.repos.nested.path='/foreign',
  rootConfig:s=>s.repos.root.configSha256='f'.repeat(64),
  nestedConfig:s=>s.repos.nested.configSha256='f'.repeat(64),
  testChanged:s=>s.files.test.sha256='f'.repeat(64),
  contextChanged:s=>s.files.context.sha256='f'.repeat(64),
  implementationPath:s=>s.files.implementation.path='/foreign',
  invalidImplementationHash:s=>s.files.implementation.sha256='not-hash',
  invalidHead:s=>s.repos.nested.sha='not-sha',
  foreignDirty:s=>s.repos.nested.status=' M foreign-file',
  multipleDirty:s=>s.repos.nested.status+='\n M foreign',
  newFile:s=>s.repos.nested.status='?? case.mjs',
  deletedFile:s=>s.repos.nested.status=s.repos.nested.status.replace(' M ',' D '),
}))test('metadata batch rejects '+name,()=>{
  const f=fixture(),state=states(f).edited;change(state);
  assert.throws(()=>assertLocalMutation(f.plan,'git-read-batch',state,f.receipt.baseline,[]));
  const entry=classifyCommand(f.plan,command(f.p),'worker');
  assert.throws(()=>assertDiscoveryOutput(f.plan,entry,{readState:state,response:{output:output(state)}},f.receipt.baseline));
});
for(const [name,stateKey,change]of [
  ['original branch changed head','original',s=>s.repos.nested.sha='f'.repeat(40)],
  ['original branch dirty','original',s=>s.repos.nested.status=' M diagnostic/case.mjs'],
  ['original branch changed bytes','original',s=>s.files.implementation.sha256='f'.repeat(64)],
  ['clean original head changed bytes','owned',s=>s.files.implementation.sha256='f'.repeat(64)],
  ['postcommit dirty','committed',s=>s.repos.nested.status=' M diagnostic/case.mjs'],
])test('metadata phase rejects '+name,()=>{
  const f=fixture(),state=states(f)[stateKey];change(state);
  assert.throws(()=>assertMetadataBatchState(f.plan,state,f.receipt.baseline));
});
function replaceHead(f,kind,readState,withPath=false){
  const r=f.receipt,w=r.workers[0],item=w.turnItems.find(i=>i.type==='command_execution'&&classifyCommand(f.plan,i.input,'worker').kind===kind);
  assert.ok(item);item.input=command(f.p,withPath?'rev-parse --show-toplevel HEAD':'rev-parse HEAD');item.output=output(readState,withPath);
  const record=r.outputs.find(o=>o.itemId===item.id);
  Object.assign(record,{kind:'git-read-batch',input:item.input,response:clone(item),sha256:sha256(JSON.stringify(item)),readState:clone(readState),origins:{}});
  return {item,record};
}
for(const withPath of [false,true])test('native postcommit batch proves final SHA'+(withPath?' with path':''),()=>{
  const f=fixture();replaceHead(f,'git-final-head',f.receipt.after,withPath);
  assert.equal(verifyReceipt(f.p,f.receipt).verified,true);
});
for(const stateKey of ['original','owned','edited','staged'])test('initial nested HEAD credit requires actual original SHA in '+stateKey+' batch',()=>{
  const f=fixture();replaceHead(f,'git-nested-head',states(f)[stateKey]);
  assert.equal(verifyReceipt(f.p,f.receipt).verified,true);
});
test('a final-SHA batch cannot substitute for original nested HEAD discovery',()=>{
  const f=fixture();replaceHead(f,'git-nested-head',f.receipt.after);
  assert.throws(()=>verifyReceipt(f.p,f.receipt),/required-editor-native-output-missing-git-nested-head/);
});
test('removing initial discovery still fails despite genuine postcommit HEAD batch',()=>{
  const f=fixture(),w=f.receipt.workers[0];replaceHead(f,'git-final-head',f.receipt.after);
  const initial=w.turnItems.find(i=>i.type==='command_execution'&&classifyCommand(f.plan,i.input,'worker').kind==='git-nested-head');
  w.turnItems=w.turnItems.filter(i=>i!==initial);f.receipt.outputs=f.receipt.outputs.filter(o=>o.itemId!==initial.id);
  assert.throws(()=>verifyReceipt(f.p,f.receipt),/required-editor-native-output-missing-git-nested-head/);
});
test('postcommit batch with stale original SHA is not final proof',()=>{
  const f=fixture();replaceHead(f,'git-final-head',states(f).owned);
  assert.throws(()=>verifyReceipt(f.p,f.receipt),/post-commit-final-head-stale/);
});
for(const time of ['2026-10-13T12:00:25Z','invalid'])test('final batch must start after completed native commit: '+time,()=>{
  const f=fixture(),{item,record}=replaceHead(f,'git-final-head',f.receipt.after);
  item.startedAt=time;record.response=clone(item);record.sha256=sha256(JSON.stringify(item));
  assert.throws(()=>verifyReceipt(f.p,f.receipt),/one-final-head-read-required/);
});
test('batch cannot mismatch recorded current SHA and native output',()=>{
  const f=fixture(),{item,record}=replaceHead(f,'git-final-head',f.receipt.after);
  item.output=f.p.originalShas.nested+'\n';record.response=clone(item);record.sha256=sha256(JSON.stringify(item));
  assert.throws(()=>verifyReceipt(f.p,f.receipt),/native-git-batch-output-mismatch/);
});
test('postcommit batch state with another clean commit cannot stand in for final commit',()=>{
  const f=fixture(),state=clone(f.receipt.after);state.repos.nested.sha='f'.repeat(40);replaceHead(f,'git-final-head',state);
  assert.throws(()=>verifyReceipt(f.p,f.receipt),/post-commit-final-head-stale/);
});
''')


class NativeBranchDenialReplayTests(unittest.TestCase):
    """Invented no-effect denials; successful native branch evidence remains mandatory."""
    data = NativeReadDiscoveryReplayTests.data
    invoke = NativeReadDiscoveryReplayTests.invoke
    SETUP = r'''
const clone=structuredClone,at=n=>`2026-10-13T12:00:${String(n).padStart(2,'0')}Z`;
const p={...x.plan,_graph:true},r=x.receipt,w=r.workers[0];
const success=r.approvals.find(a=>a.kind==='branch'),branch=w.turnItems.find(i=>i.id===success.itemId);
const commonDir='/invented/fleet/specweave/.git',refName='refs/heads/'+p.branch;
const before={state:clone(r.baseline),git:{gitDir:commonDir+'/worktrees/invented',commonDir,
  refName,refPath:commonDir+'/'+refName,refValue:'',refExists:false}};
const item={...clone(branch),id:'invented-denied-branch',status:'failed',exitCode:128,
  nativeItemRef:{driver:'codex',strength:'strong',nativeId:'invented-denied-native'},
  startedAt:at(13),completedAt:at(14),updatedAt:at(14),
  output:`fatal: cannot lock ref '${refName}': unable to create directory for ${before.git.refPath}\n`};
const a=clone(success);Object.assign(a,{itemId:item.id,requestId:'invented-denied-request',branchBefore:clone(before)});
Object.assign(a.payload.request,{id:a.requestId,nativeRequestRef:clone(item.nativeItemRef)});
Object.assign(a.payload.approval,{id:'invented-denied-display',requestId:a.requestId,prompt:item.input});
a.payload.action={...clone(item),status:'waiting',exitCode:undefined,output:undefined,completedAt:undefined};
a.payloadSha256=M.sha256(JSON.stringify(a.payload));success.branchBefore=clone(before);
const output={threadId:item.threadId,itemId:item.id,runId:item.runId,role:'worker',kind:'branch',
  input:item.input,response:clone(item),nativeResponse:{item:clone(item)},
  sha256:M.sha256(JSON.stringify(item)),branchAfter:clone(before)};
r.approvals.push(a);r.outputs.push(output);w.turnItems.push(item,{...clone(a.payload.approval),status:'completed'});
w.runtimeRequests.push({...clone(a.payload.request),status:'resolved',decision:'accept'});
function observer(){const o=M.makeObserver(p);for(const approval of r.approvals)o.approved.set(approval.itemId,approval.payloadSha256);return o;}
function rehash(o){o.sha256=M.sha256(JSON.stringify(o.response));o.nativeResponse={item:clone(o.response)};}
'''

    def test_one_denial_and_one_scoped_success_replay_with_both_outputs_retained(self):
        self.invoke(self.SETUP + r'''
M.verifyReceipt(x.plan,r);assert.equal(r.outputs.filter(o=>o.kind==='branch').length,2);
for(const kind of ['branch','add','commit'])assert.throws(()=>M.assertCommandResult(p,kind,{status:'failed',exitCode:128}));
''', self.data())

    def test_error_bytes_state_ref_and_ownership_are_bound(self):
        self.invoke(self.SETUP + r'''
const changes=[o=>o.response.output+='extra\n',o=>o.response.output=o.response.output.trimEnd(),
  o=>o.response.output=o.response.output.replace('/invented/fleet','/foreign'),
  o=>o.response.output='fatal: branch already exists\n',o=>o.response.exitCode=1,
  o=>o.threadId='foreign',o=>o.runId='foreign',o=>o.input+=' --force',
  o=>o.branchAfter.state.files.implementation.sha256='f'.repeat(64),
  o=>o.branchAfter.state.files.test.sha256='f'.repeat(64),
  o=>o.branchAfter.state.repos.nested.sha='f'.repeat(40),
  o=>o.branchAfter.state.repos.nested.branch=p.branch,
  o=>o.branchAfter.state.repos.root.branch='foreign',
  o=>o.branchAfter.state.repos.nested.configSha256='f'.repeat(64),
  o=>o.branchAfter.git.commonDir='/foreign',o=>o.branchAfter.git.gitDir+='/foreign',
  o=>o.branchAfter.git.refPath+='/foreign',o=>o.branchAfter.git.refPath+='/../target',
  o=>o.branchAfter.git.refValue='foreign-ref',o=>o.branchAfter.git.refExists=true,
  o=>o.response.completedAt='invalid',o=>o.response.completedAt=at(12)];
for(const change of changes){const bad=clone(output);change(bad);rehash(bad);
  assert.throws(()=>M.registerBranchDenial(observer(),bad,a,r.baseline));
  const receipt=clone(r);receipt.outputs[receipt.outputs.length-1]=bad;
  assert.throws(()=>M.verifyReceipt(x.plan,receipt));}
for(const field of ['sha256','nativeResponse','branchAfter']){const bad=clone(output);delete bad[field];assert.throws(()=>M.registerBranchDenial(observer(),bad,a,r.baseline));}
assert.throws(()=>M.registerBranchDenial(M.makeObserver(p),output,a,r.baseline));
''', self.data())

    def test_retry_is_identical_owned_later_and_single(self):
        self.invoke(self.SETUP + r'''
const o=observer();M.registerBranchDenial(o,output,a,r.baseline);M.assertBranchRetry(o,branch,before);
for(const change of [i=>i.id=item.id,i=>i.threadId='foreign',i=>i.runId='foreign',
  i=>i.providerTurnId='foreign',i=>i.input+=' ',i=>i.startedAt=at(13),
  i=>i.startedAt='invalid',i=>i.nativeItemRef.nativeId=item.nativeItemRef.nativeId,
  i=>i.nativeItemRef.strength='weak']){const bad=clone(branch);change(bad);assert.throws(()=>M.assertBranchRetry(o,bad,before));}
const changed=clone(before);changed.state.repos.nested.status=' M foreign';assert.throws(()=>M.assertBranchRetry(o,branch,changed));
assert.throws(()=>M.registerBranchDenial(o,output,a,r.baseline),/second-branch-denial/);
w.turnItems.push({...clone(branch),id:'third-branch',status:'waiting'});
assert.throws(()=>M.observe(o,w,r.parent),/duplicate-git-mutation/);
''', self.data())

    def test_denied_branch_cannot_supply_completion_or_success_chronology(self):
        self.invoke(self.SETUP + r'''
const missing=clone(r),mw=missing.workers[0];
mw.turnItems=mw.turnItems.filter(i=>i.id!==branch.id&&i.requestId!==success.requestId);
mw.runtimeRequests=mw.runtimeRequests.filter(q=>q.id!==success.requestId);
missing.approvals=missing.approvals.filter(a=>a.itemId!==branch.id);
missing.outputs=missing.outputs.filter(o=>o.itemId!==branch.id);
assert.throws(()=>M.verifyReceipt(x.plan,missing),/required-editor-native-output-missing-branch/);
branch.completedAt=at(20);const committed=r.outputs.find(o=>o.itemId===branch.id);
committed.response=clone(branch);committed.sha256=M.sha256(JSON.stringify(branch));
assert.throws(()=>M.verifyReceipt(x.plan,r),/edit-before-owned-branch/);
''', self.data())


class NativeOutputProofReplayTests(unittest.TestCase):
    """Invented metadata and raw envelopes; no operational receipts are published."""
    data = NativeReadDiscoveryReplayTests.data
    invoke = NativeReadDiscoveryReplayTests.invoke

    def test_detached_branch_empty_stdout_is_state_bound(self):
        self.invoke(r'''
const p={...x.plan,_graph:true},r=x.receipt;
r.baseline.repos.root.branch='';r.baseline.repos.nested.branch='';
for(const kind of ['git-root-branch','git-nested-branch']){
  const entry=M.buildCommandPolicy(p).find(e=>e.kind===kind&&e.role==='worker');
  const item={id:'invented-empty',threadId:'worker',runId:'child-run',providerTurnId:'child-turn',
    type:'command_execution',input:entry.command,status:'completed',exitCode:0,output:null};
  const output={response:item,readState:structuredClone(r.baseline)};
  assert.equal(M.assertRetainedItem(item,{item},kind).output,null);
  M.assertDiscoveryOutput(p,entry,output,r.baseline);
  for(const value of [undefined,'foreign\n']){const changed={...item,output:value};
    assert.throws(()=>{M.assertRetainedItem(item,{item:changed},kind);
      M.assertDiscoveryOutput(p,entry,{...output,response:changed},r.baseline);});}
  assert.throws(()=>M.assertRetainedItem(item,{item:{...item,outputOmitted:true}},kind));
  for(const other of ['read-test','read-context','read-implementation','test','git-root-head','git-final-head','branch','commit'])
    assert.throws(()=>M.assertRetainedItem(item,{item},other));
}
''', self.data())

    def test_branch_output_cannot_disagree_with_owned_state(self):
        self.invoke(r'''
const p={...x.plan,_graph:true},r=x.receipt,entry=M.buildCommandPolicy(p).find(e=>e.kind==='git-nested-branch');
const output={response:{output:p.branch+'\n'},readState:structuredClone(r.baseline)};
output.readState.repos.nested.branch=p.branch;
M.assertDiscoveryOutput(p,entry,output,r.baseline);
assert.throws(()=>M.assertDiscoveryOutput(p,entry,{...output,response:{output:null}},r.baseline));
for(const change of [s=>s.repos.nested.branch='foreign',s=>s.repos.root.sha='f'.repeat(40),
  s=>s.repos.nested.configSha256='f'.repeat(64),s=>s.files.test.sha256='f'.repeat(64),
  s=>s.repos.nested.status=' M unrelated']){const bad=structuredClone(output);change(bad.readState);
  assert.throws(()=>M.assertDiscoveryOutput(p,entry,bad,r.baseline));}
''', self.data())

    def test_raw_envelopes_bind_to_projection_and_credited_outputs(self):
        self.invoke(r'''
const r=x.receipt,items=[r.parent,...r.workers].flatMap(p=>p.turnItems).filter(i=>i.type==='command_execution');
r.retainedItems=r.outputs.map(o=>({threadId:o.threadId,itemId:o.itemId,
  projectionItem:structuredClone(items.find(i=>i.id===o.itemId)),nativeResponse:{item:structuredClone(o.response)},
  sha256:M.sha256(JSON.stringify({item:o.response}))}));
M.verifyReceipt(x.plan,r);
for(const change of [r=>r.retainedItems.pop(),r=>r.retainedItems.push(structuredClone(r.retainedItems[0])),
  r=>r.retainedItems[0].sha256='f'.repeat(64),r=>r.retainedItems[0].threadId='foreign',
  r=>r.retainedItems[0].projectionItem.runId='foreign',r=>r.retainedItems[0].nativeResponse.item.output+='x',
  r=>r.retainedItems[0].fetchFailure={message:'missing'}]){const bad=structuredClone(r);change(bad);
  assert.throws(()=>M.verifyReceipt(x.plan,bad));}
''', self.data())
