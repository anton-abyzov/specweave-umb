"""Invented Git objects and native receipts; never operational acceptance evidence."""
import base64
import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
import test_product_handoff_evidence as f

PATHS = [
    '.specweave/increments/0651-goals-assists-leaderboards/scripts/console/node_modules',
    '.specweave/increments/0651-goals-assists-leaderboards/scripts/web/node_modules',
    '.specweave/increments/_archive/0554-ai-power-real-host-youtube-launch/artifacts/edit/node_modules']


def objects(extra_change=False, deleted_mode="120000", omitted=False, foreign=False, wrong_parent=False):
    rows = {}
    def put(kind, data):
        oid = hashlib.sha1((kind + ' ' + str(len(data)) + '\0').encode() + data).hexdigest()
        rows[oid] = dict(type=kind, oid=oid, base64=base64.b64encode(data).decode())
        return oid
    old = {'keep.txt': ('100644', 'f' * 40)}
    for i, path in enumerate(PATHS[:-1] if omitted else PATHS):
        if foreign and i == 0: path = 'foreign/node_modules'
        cursor = old
        for part in path.split('/')[:-1]:
            cursor = cursor.setdefault(part, {})
        cursor['node_modules'] = (deleted_mode, put('blob', ('/Users/antonabyzov/Projects/sw-easychamp/test'+str(i)).encode()))
    def tree(entries):
        data = b''
        for name in sorted(entries):
            value = entries[name]
            mode, oid = ('40000', tree(value)) if isinstance(value, dict) else value
            data += (mode + ' ' + name + '\0').encode() + bytes.fromhex(oid)
        return put('tree', data)
    before_tree = tree(old)
    after_tree = tree({'keep.txt': ('100644', ('e' if extra_change else 'f') * 40)})
    before = put('commit', ('tree '+before_tree+'\nauthor Synthetic <test@example.invalid> 1 +0000\n\nold\n').encode())
    after = put('commit', ('tree '+after_tree+'\nparent '+('0'*40 if wrong_parent else before)+'\nauthor Synthetic <test@example.invalid> 2 +0000\n\ncleanup\n').encode())
    return before, after, list(rows.values())


class CheckpointTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix='invented-checkpoint-')
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name).resolve()
        self.index = f.invented_evidence(self.root)
        self.plan, self.native = f.invented_native('source', 'sw-easychamp', 'm4')
        self.make_checkpoint()

    def make_checkpoint(self, extra_change=False, **options):
        old, new, rows = objects(extra_change, **options)
        text = json.dumps([self.plan, self.native]).replace(self.plan['originalShas']['root'], old)
        text = text.replace(self.plan['workspaceRoot'], '/synthetic/product-source-checkouts/sw-easychamp')
        self.plan, self.native = json.loads(text)
        f.rehash_native(self.native)
        self.entry = {'plan': f.ref(self.root, 'advance-source-plan.json', self.plan),
                      'native': f.ref(self.root, 'advance-source-native.json', self.native)}
        row = {'path': self.plan['workspaceRoot'], 'projectKey': 'sw-easychamp', 'kind': 'root',
               'head': old, 'branch': self.native['baseline']['repos']['root']['branch'],
               'statusSha256': f.V.digest(b''), 'gitConfigSha256': self.native['baseline']['repos']['root']['configSha256'],
               'indexSha256': '1' * 64}
        output = next(o['response']['output'] for o in self.native['outputs'] if o['kind'] == 'test')
        test = {'argv': [self.plan['nodePath'], '--test', self.plan['paths']['test']],
                'cwd': self.plan['nestedRoot'], 'exitCode': 1, 'stdout': output, 'stderr': '',
                'startedAt': '2026-10-13T17:00:01Z', 'finishedAt': '2026-10-13T17:00:02Z'}
        self.advance = {'version': 1, 'kind': 'source-checkpoint-symlink-cleanup', 'key': 'sw-easychamp',
            'source': {'planSha256': self.entry['plan']['sha256'], 'nativeSha256': self.entry['native']['sha256'],
                **{k: self.plan[k] for k in ('environmentId', 'projectId', 'coordinatorId')}},
            'startedAt': '2026-10-13T17:00:00Z', 'finishedAt': '2026-10-13T17:00:05Z',
            'originalShas': self.plan['originalShas'], 'newShas': dict(root=new, nested=self.plan['originalShas']['nested']),
            'objects': rows, 'files': {'before': copy.deepcopy(self.native['baseline']), 'after': copy.deepcopy(self.native['baseline'])},
            'preservation': {'before': row, 'after': dict(row, head=new, indexSha256='2'*64)},
            'tests': {'before': test, 'after': dict(test, startedAt='2026-10-13T17:00:03Z', finishedAt='2026-10-13T17:00:04Z')},
            'context': {'contextRequired': self.plan['contextRequired'], 'workerThreadId': self.native['outcome']['workerThreadId'],
                'workerTextSha256': f.V.digest(self.native['outcome']['workerText'].encode()),
                'relayTextSha256': f.V.digest(self.native['outcome']['relayText'].encode())}}
        self.advance['files']['after']['repos']['root']['sha'] = new

    def evidence(self):
        (self.root/'product-evidence-index.json').write_bytes(f.encode(self.index))
        return f.V.Evidence(self.root)

    def replay(self, bundle=None):
        reference = f.ref(self.root, 'checkpoint.json', self.advance)
        source_record = f.ref(self.root, 'advance-record.json', {'bundle': bundle}) if bundle else None
        return f.V.source_checkpoint(self.evidence(), self.entry, reference, source_record)

    def test_direct_child_three_symlink_cleanup_keeps_old_native_proof(self):
        original = copy.deepcopy(self.native)
        result = self.replay()
        self.assertEqual(result['newShas'], self.advance['newShas'])
        self.assertEqual(self.native, original)
        self.assertNotEqual(result['newShas']['root'], self.plan['originalShas']['root'])

    def test_hash_bound_tree_rejects_other_actual_file_change(self):
        self.make_checkpoint(extra_change=True)
        with self.assertRaises(ValueError): self.replay()

    def test_rehashed_git_diff_rejects_nonlinks_foreign_missing_and_wrong_parent(self):
        for options in [dict(deleted_mode='100644'), dict(omitted=True), dict(foreign=True), dict(wrong_parent=True)]:
            self.make_checkpoint(**options)
            with self.assertRaises(ValueError): self.replay()

    def test_same_count_but_changed_assertion_names_rejected(self):
        self.advance['tests']['after']['stdout'] = self.advance['tests']['after']['stdout'].replace('unfinished', 'different')
        with self.assertRaises(ValueError): self.replay()

    def test_tampered_object_and_parent_inventory(self):
        for mutate in [lambda a: a['objects'].pop(),
                       lambda a: a['objects'].append(copy.deepcopy(a['objects'][0])),
                       lambda a: a['objects'][0].update(base64='YWJj'),
                       lambda a: a['newShas'].update(root=a['originalShas']['root'])]:
            original = copy.deepcopy(self.advance)
            mutate(self.advance)
            with self.assertRaises(ValueError): self.replay()
            self.advance = original

    def test_changed_code_context_config_or_original_binding_rejected(self):
        cases = [lambda a: a['source'].update(nativeSha256='0'*64),
                 lambda a: a['newShas'].update(nested='0'*40),
                 lambda a: a['files']['after']['files']['test'].update(sha256='0'*64),
                 lambda a: a['files']['after']['repos']['root'].update(configSha256='0'*64),
                 lambda a: a['context'].update(workerThreadId='other'),
                 lambda a: a['context'].update(relayTextSha256='0'*64),
                 lambda a: a['preservation']['after'].update(branch='other'),
                 lambda a: a['preservation']['before'].update(statusSha256='0'*64),
                 lambda a: a.update(key='jobweave'),
                 lambda a: a.update(allowOtherChanges=True)]
        for mutate in cases:
            original = copy.deepcopy(self.advance)
            mutate(self.advance)
            with self.assertRaises(ValueError): self.replay()
            self.advance = original

    def test_red_tests_are_real_bound_complete_and_ordered(self):
        cases = [lambda a: a['tests']['after'].update(exitCode=0),
                 lambda a: a['tests']['after'].update(stderr='failure'),
                 lambda a: a['tests']['after'].update(stdout='not a test'),
                 lambda a: a['tests']['after'].update(argv=['echo', 'success']),
                 lambda a: a['tests']['after'].update(cwd='/foreign'),
                 lambda a: a['tests']['after'].update(startedAt='2026-10-13T16:59:00Z'),
                 lambda a: a.update(startedAt='2026-10-13T10:00:00Z')]
        for mutate in cases:
            original = copy.deepcopy(self.advance)
            mutate(self.advance)
            with self.assertRaises(ValueError): self.replay()
            self.advance = original

    def test_bundle_must_publish_new_pin_after_cleanup(self):
        bundle = {k: self.plan[k] for k in ()}
        bundle.update(sourceEnvironmentId=self.plan['environmentId'], sourceProjectId=self.plan['projectId'],
            sourceThreadId=self.plan['coordinatorId'], createdAt='2026-10-13T17:01:00Z',
            manifest={'repositories': [{'relativePath': '.', 'head': self.advance['newShas']['root']},
                                     {'relativePath': 'repositories/owner/code', 'head': self.advance['newShas']['nested']}]})
        self.replay(bundle)
        for field, value in [('sourceProjectId', 'foreign'), ('createdAt', '2026-10-13T16:00:00Z')]:
            bad = dict(bundle, **{field: value})
            with self.assertRaises(ValueError): self.replay(bad)
        bundle['manifest']['repositories'][0]['head'] = self.plan['originalShas']['root']
        with self.assertRaises(ValueError): self.replay(bundle)

    def test_preservation_only_accepts_exact_reviewed_root_transition(self):
        report = self.replay()
        refs = self.index['handoff']['preservation']
        preserved = json.loads((self.root/refs[0]['path']).read_bytes())
        self.assertEqual(preserved['host'], 'm4')
        for phase in ('before', 'after'):
            row = next(r for r in preserved[phase] if r['projectKey']=='sw-easychamp' and r['kind']=='root')
            row.update(report['preservation'][phase])
        for phase in ('configFilesBefore', 'configFilesAfter'):
            preserved[phase][0]['path'] = self.plan['workspaceRoot']+'/.specweave/config.json'
        preserved['afterAt']='2026-10-13T18:00:00Z'
        refs[0]=f.ref(self.root, refs[0]['path'], preserved)
        f.V.preservation(self.evidence(),refs,{'sw-easychamp':report})
        with self.assertRaises(ValueError): f.V.preservation(self.evidence(),refs)
        preserved['after'][1]['indexSha256']='9'*64
        refs[0]=f.ref(self.root,refs[0]['path'],preserved)
        with self.assertRaises(ValueError): f.V.preservation(self.evidence(),refs,{'sw-easychamp':report})


if __name__ == '__main__':
    unittest.main()
