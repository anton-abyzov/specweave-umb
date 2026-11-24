"""Invented offline source-execution records; no owner command is executed."""
import copy
import tempfile
import unittest
from pathlib import Path

import test_product_handoff_evidence as fixtures

V, ref, CANDIDATE = fixtures.V, fixtures.ref, fixtures.CANDIDATE


class RetainedSourceExecutionTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(); self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name).resolve()
        self.e = V.Evidence.__new__(V.Evidence)
        self.e.root, self.e.candidate = self.root, CANDIDATE

    def fixture(self, coverage=True):
        cwd, origin = '/synthetic/candidate', '/synthetic/evidence/check.json'
        header = {'cwd': cwd, 'command': ['node', 'node_modules/vite-plus/bin/vp', 'test', 'run',
                  '--outputFile=/synthetic/evidence/report.json'], 'startedAt': '2026-10-13T12:00:00Z'}
        if coverage:
            header.update(source=CANDIDATE['sourceCommit'], sourceTree='a'*40)
        else:
            header.update(sourceBefore={'source': CANDIDATE['sourceCommit'], 'tree': 'a'*40, 'status': ''},
                compilerSha256='c'*64, qualification='Standard TypeScript only; configured Effect diagnostics remain non-green.')
            header['command'] = [cwd+'/node_modules/.pnpm/@typescript+typescript-darwin-arm64@7.0.2/node_modules/@typescript/typescript-darwin-arm64/lib/tsc',
                                 '--noEmit', '-p', 'apps/server/tsconfig.json']
        owner = {**copy.deepcopy(header), 'endedAt': '2026-10-13T12:00:02Z', 'exitCode': 0, 'sourceUnchanged': True}
        output = ref(self.root, 'output.log', b'actual invented test output\n' if coverage else b'')
        if coverage:
            owner.update(tests=2, passed=2, failed=0, suites=1, coverage={})
        else:
            owner.update(sourceAfter=copy.deepcopy(header['sourceBefore']), log='/synthetic/evidence/check.log', logSha256=output['sha256'])
        proof = {'kind': 'coverage-run' if coverage else 'native-typescript',
                 'start': ref(self.root, 'start.json', header), 'completionOriginPath': origin,
                 'startOriginPath': '/synthetic/evidence/check.start.json'}
        command = {'candidateCommit': CANDIDATE['sourceCommit'], 'argv': header['command'], 'cwd': cwd,
            'startedAt': header['startedAt'], 'finishedAt': owner['endedAt'], 'exitCode': 0,
            'invocationProvenance': 'retained-r3-source-execution', 'executionProof': proof,
            'ownerReceipt': ref(self.root, 'owner.json', owner),
            'combinedOutput': {**output, 'originPath': '/synthetic/evidence/check.log'}}
        if coverage:
            producer = ("p=pathlib.Path('/synthetic/candidate')\nsource="+repr(CANDIDATE['sourceCommit'])+"\n"
                "assert git('rev-parse','HEAD')==source and not git('status','--porcelain')\n"
                "write('check.start.json',rec)\n"
                "with (r/'check.log').open('x') as f: result=subprocess.run(cmd,cwd=p,env=env,stdout=f,stderr=subprocess.STDOUT)\n"
                "rec.update(endedAt=now(),exitCode=result.returncode,sourceUnchanged=git('rev-parse','HEAD')==source and not git('status','--porcelain'))\n"
                "write('check.json',rec)\n")
            proof.update(producer=ref(self.root, 'producer.py', producer.encode()), producerOriginPath='/synthetic/evidence/run.py')
            command.update(testReport=ref(self.root, 'report.json', {'numTotalTests': 2, 'numPassedTests': 2,
                'numFailedTests': 0, 'numTotalTestSuites': 1}), testReportOriginPath='/synthetic/evidence/report.json')
        return command, owner, header

    def verify(self, command, coverage=True):
        return V.candidate_command(self.e, ref(self.root, 'command.json', command),
                                   'unit' if coverage else 'typecheck', command['cwd'])

    def test_coverage_maps_ended_at_and_preserves_combined_output(self):
        command, owner, _ = self.fixture(); before = copy.deepcopy(owner)
        self.assertEqual(self.verify(command)[1], 'actual invented test output\n')
        self.assertEqual(owner, before); self.assertNotIn('sourceBefore', owner)

    def test_native_typecheck_maps_actual_source_states_and_empty_log(self):
        command, owner, _ = self.fixture(False)
        self.assertEqual(self.verify(command, False)[1:], ('', ''))
        self.assertNotIn('source', owner); self.assertNotIn('completedAt', owner)

    def test_changed_source_command_cwd_time_failure_or_preservation_refused(self):
        for coverage in (True, False):
            for field, changed in [('command', ['echo', 'test']), ('cwd', '/foreign'),
                    ('startedAt', '2026-10-13T11:00:00Z'), ('endedAt', '2026-10-13T12:00:03Z'),
                    ('exitCode', 1), ('sourceUnchanged', False)]:
                command, owner, _ = self.fixture(coverage); owner[field] = changed
                command['ownerReceipt'] = ref(self.root, 'owner.json', owner)
                with self.subTest(coverage=coverage, field=field), self.assertRaises(ValueError): self.verify(command, coverage)

    def test_rehashed_start_mutation_is_rejected(self):
        for coverage in (True, False):
            command, _, start = self.fixture(coverage); start['cwd']='/foreign'
            command['executionProof']['start']=ref(self.root, 'start.json', start)
            with self.assertRaises(ValueError):self.verify(command, coverage)

    def test_added_or_omitted_proof_field_and_separated_stream_claim_rejected(self):
        for field in ('start', 'extra', 'stdout'):
            command, _, _=self.fixture()
            if field=='start':del command['executionProof']['start']
            elif field=='extra':command['executionProof']['extra']=True
            else:command['stdout']=command['combinedOutput']
            with self.assertRaises((ValueError, KeyError)):self.verify(command)

    def test_producer_foreign_candidate_checkout_log_or_spawn_is_rejected(self):
        for old, new in [(CANDIDATE['sourceCommit'], 'f'*40), ('/synthetic/candidate', '/foreign'),
                         ('check.log', 'other.log'), ('stderr=subprocess.STDOUT', 'stderr=subprocess.PIPE')]:
            command, _, _=self.fixture(); reference=command['executionProof']['producer']
            data=self.e.data(reference).decode().replace(old,new)
            command['executionProof']['producer']=ref(self.root,'producer.py',data.encode())
            with self.subTest(old=old), self.assertRaises(ValueError):self.verify(command)

    def test_report_counts_origin_and_raw_candidate_must_match(self):
        for change in ('count','origin','candidate','tree'):
            command,owner,_=self.fixture()
            if change=='count': owner['passed']=1
            elif change=='origin':command['testReportOriginPath']='/foreign/report.json'
            elif change=='candidate':owner['source']='f'*40
            else:owner['sourceTree']='latest'
            command['ownerReceipt']=ref(self.root,'owner.json',owner)
            with self.subTest(change=change), self.assertRaises(ValueError):self.verify(command)

    def test_typecheck_source_state_log_qualification_and_native_path_tampering_refused(self):
        for change in ('state','hash','qualification','compiler','native','arg'):
            command,owner,start=self.fixture(False)
            if change=='state':owner['sourceAfter']['source']='f'*40
            elif change=='hash':owner['logSha256']='f'*64
            elif change=='qualification':owner['qualification']=start['qualification']='All configured checks passed.'
            elif change=='compiler':owner['compilerSha256']=start['compilerSha256']='latest'
            else:
                command['argv'][0 if change=='native' else -1]='/foreign/tsc' if change=='native' else 'apps/other/tsconfig.json'
                owner['command']=start['command']=command['argv']
            command['ownerReceipt']=ref(self.root,'owner.json',owner);command['executionProof']['start']=ref(self.root,'start.json',start)
            with self.subTest(change=change), self.assertRaises(ValueError):self.verify(command,False)

    def test_start_or_log_from_another_invocation_rejected(self):
        for field in ('startOriginPath','completionOriginPath','combinedOutput'):
            command,_,_=self.fixture()
            if field=='combinedOutput':command[field]['originPath']='/synthetic/evidence/other.log'
            else:command['executionProof'][field]='/synthetic/evidence/other.json'
            with self.subTest(field=field), self.assertRaises(ValueError):self.verify(command)


    def test_dead_code_or_reordered_producer_steps_rejected(self):
        for kind in ('dead', 'reordered'):
            command,_,_=self.fixture();data=self.e.data(command['executionProof']['producer']).decode()
            lines=data.splitlines()
            if kind=='dead': data='\n'.join(lines[:2])+"\nif False:\n"+'\n'.join('    '+line for line in lines[2:])+'\n'
            else: lines[-1],lines[-2]=lines[-2],lines[-1];data='\n'.join(lines)+'\n'
            command['executionProof']['producer']=ref(self.root,'producer.py',data.encode())
            with self.subTest(kind=kind),self.assertRaises(ValueError):self.verify(command)

    def test_missing_or_fabricated_postrun_outcome_rejected(self):
        for change in ('missing','exit','source'):
            command,_,_=self.fixture();data=self.e.data(command['executionProof']['producer']).decode()
            if change=='missing':data='\n'.join(line for line in data.splitlines() if not line.startswith('rec.update'))+'\n'
            elif change=='exit':data=data.replace('exitCode=result.returncode','exitCode=0')
            else:data=data.replace("sourceUnchanged=git('rev-parse','HEAD')==source and not git('status','--porcelain')",'sourceUnchanged=True')
            command['executionProof']['producer']=ref(self.root,'producer.py',data.encode())
            with self.subTest(change=change),self.assertRaises(ValueError):self.verify(command)


class ExternalPrivateCacheTests(unittest.TestCase):
    def setUp(self):
        self.f=fixtures.ProductReleaseEvidenceTests();self.f.setUp();self.addCleanup(self.f.doCleanups)
    def fixture(self,cache,extra=False):
        f=self.f;reference,external,review=f.configured_external_case()
        config={'test':{'root':'/synthetic/independent-review','include':['permissions.test.ts'],
                       'environment':'node','testTimeout':60000,'hookTimeout':60000},'cacheDir':cache}
        if extra:config['resolve']={'alias':{'production':'fake'}}
        external['config']['bytes']=ref(f.root,'cache-config.mjs',b'export default '+fixtures.encode(config)+b';\n')
        bindings=f.read(external['harnessBindings'])
        bindings['harnessFiles'][1]['sha256']=external['config']['bytes']['sha256']
        f.replace(external['harnessBindings'],bindings)
        execution=f.read(external['command']);execution['externalHarnessBindings']=external['harnessBindings'];f.replace(external['command'],execution)
        external['review']=ref(f.root,'cache-review.txt',(review['reviewer']+' '+CANDIDATE['sourceCommit']+' '+external['harnessBindings']['sha256']).encode())
        review['cases']['denied-transfer']['command']=external['command']
        f.update_external(reference,external,review)
    def test_actual_private_harness_cache_path_is_supported(self):
        self.fixture('/synthetic/independent-review/cache');V.product_review(self.f.root)
    def test_other_cache_directory_is_rejected(self):
        self.fixture('/synthetic/candidate-studio/cache')
        with self.assertRaisesRegex(ValueError,'external cache'):V.product_review(self.f.root)
    def test_cache_does_not_allow_other_runner_overrides(self):
        self.fixture('/synthetic/independent-review/cache',True)
        with self.assertRaisesRegex(ValueError,'unreviewed runner overrides'):V.product_review(self.f.root)
