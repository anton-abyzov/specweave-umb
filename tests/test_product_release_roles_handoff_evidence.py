"""Explicitly synthetic release-role fixtures; never operational acceptance."""
import copy
import json
from pathlib import Path
import tempfile
import unittest

from test_product_handoff_evidence import (
    V, CANDIDATE, encode, ref, invented_evidence, invented_release_evidence, invented_worker_service,
)


class ReleasedWorkerRoleTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='synthetic-release-roles-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.index = invented_evidence(self.root)
        invented_release_evidence(self.root, self.index)
        self.release = self.read(self.index['release'])
        self.build = self.read(self.release['build'])
        self.fingerprint = {'sha256': 'd' * 64, 'files': 3}
        owner = {'source': CANDIDATE['sourceCommit'], 'command': self.build['argv'],
                 'cwd': self.build['cwd'], 'startedAt': self.build['startedAt'],
                 'completedAt': self.build['finishedAt'], 'exitCode': 0,
                 'sourceUnchanged': True, 'log': '/synthetic/build.log',
                 'serverDistFingerprint': self.fingerprint}
        self.build['ownerReceipt'] = ref(self.root, 'build-owner.json', owner)
        self.build['combinedOutput'] = dict(self.build.pop('stdout'), originPath=owner['log'])
        del self.build['stderr']
        self.release['build'] = ref(self.root, self.release['build']['path'], self.build)
        code = self.read(self.index['code'])
        code['checks'][2]['command'] = self.release['build']
        self.index['code'] = ref(self.root, self.index['code']['path'], code)
        artifact = ref(self.root, 'synthetic-worker-runtime.tar.gz', b'Invented archive bytes only.')
        self.binding = {'verified': True, 'sourceCommit': CANDIDATE['sourceCommit'],
                        'buildReceiptSha256': self.build['ownerReceipt']['sha256'],
                        'archive': Path(artifact['path']).name, 'sha256': artifact['sha256'],
                        'bytes': len(b'Invented archive bytes only.'),
                        'serverDistFingerprint': self.fingerprint, 'completedAt': '2026-10-13T00:00:02Z'}
        self.publication = {'sourceCommit': CANDIDATE['sourceCommit'], 'version': CANDIDATE['version'],
                            'artifactSha256': artifact['sha256'], 'downloadedArtifact': artifact,
                            'url': 'https://example.invalid/synthetic-worker-runtime.tar.gz'}
        self.release['runtimeArchive'] = {'artifact': artifact}
        self.runtimes, self.raws, self.owners = {}, {}, {}
        for host in V.HOSTS:
            runtime, raw, owner = invented_worker_service(self.root, host)
            runtime.update(kind='released-worker-service', installedFromArchiveSha256=artifact['sha256'])
            raw['archiveSha256'] = owner['readback']['archiveSha256'] = artifact['sha256']
            self.runtimes[host], self.raws[host], self.owners[host] = runtime, raw, owner

    def read(self, reference):
        return json.loads((self.root / reference['path']).read_bytes())

    def save(self):
        archive = self.release['runtimeArchive']
        archive['buildBinding'] = ref(self.root, 'runtime-build-binding.json', self.binding)
        archive['publication'] = ref(self.root, 'runtime-publication.json', self.publication)
        for host, runtime in self.runtimes.items():
            runtime['serviceReadback'] = ref(self.root, host + '-service.raw.json', self.raws[host])
            runtime['serviceOwnerReadback'] = ref(self.root, host + '-service-owner.raw.json', self.owners[host])
            row = next(row for row in self.release['hosts'] if row['host'] == host)
            row['readback'] = ref(self.root, host + '-released-worker.json', runtime)
        self.index['release'] = ref(self.root, 'release.json', self.release)
        (self.root / 'product-evidence-index.json').write_bytes(encode(self.index))

    def verify(self):
        self.save()
        V.product_release(self.root)

    def test_native_m4_and_two_explicit_worker_roles_pass(self):
        self.verify()

    def test_worker_kind_is_not_transfer_proof(self):
        self.save()
        row = next(row for row in self.release['hosts'] if row['host'] == 'm1')
        with self.assertRaisesRegex(ValueError, 'wrong runtime evidence kind'):
            V.runtime(V.Evidence(self.root), row['readback'], 'm1')

    def test_worker_cannot_replace_m4_native_app(self):
        self.save()
        runtime = copy.deepcopy(self.runtimes['m1'])
        runtime.update(host='m4', environmentId='synthetic-env-m4',
                       serverReadback=ref(self.root, 'm4-worker-server.json', {
                           'sourceCommit': CANDIDATE['sourceCommit'], 'version': CANDIDATE['version'],
                           'environmentId': 'synthetic-env-m4'}))
        reference = ref(self.root, 'm4-invalid-worker.json', runtime)
        with self.assertRaisesRegex(ValueError, 'remote service proof'):
            V.runtime(V.Evidence(self.root), reference, 'm4', released=True)

    def test_native_role_still_requires_native_proof(self):
        self.runtimes['m1']['kind'] = 'released-native-app'
        with self.assertRaisesRegex(ValueError, 'cannot replace native UI'):
            self.verify()

    def test_worker_cannot_claim_native_wrapper_fields(self):
        self.runtimes['m1']['appReadback'] = {'path': 'unused', 'sha256': 'f' * 64}
        with self.assertRaisesRegex(ValueError, 'cannot replace native UI'):
            self.verify()

    def test_public_archive_cannot_be_the_desktop_artifact(self):
        self.publication['downloadedArtifact'] = self.release['artifact']
        with self.assertRaisesRegex(ValueError, 'public runtime archive'):
            self.verify()

    def test_missing_public_archive_is_not_accepted(self):
        del self.publication['downloadedArtifact']
        with self.assertRaises((ValueError, KeyError)):
            self.verify()

    def test_changed_public_source_or_version_is_rejected(self):
        for key, value in [('sourceCommit', '0' * 40), ('version', '0.0.0')]:
            with self.subTest(key=key):
                before = self.publication[key]
                self.publication[key] = value
                with self.assertRaisesRegex(ValueError, 'public runtime archive'):
                    self.verify()
                self.publication[key] = before

    def test_installed_archive_must_equal_downloaded_archive(self):
        self.raws['m1']['archiveSha256'] = self.owners['m1']['readback']['archiveSha256'] = 'a' * 64
        with self.assertRaisesRegex(ValueError, 'differs from public release'):
            self.verify()

    def test_rehashed_wrong_archive_build_binding_is_rejected(self):
        for key, value in [('sourceCommit', '0' * 40), ('buildReceiptSha256', '0' * 64),
                           ('sha256', '0' * 64), ('bytes', 1), ('verified', False),
                           ('archive', 'other.tar.gz'), ('completedAt', '2026-10-12T00:00:00Z'),
                           ('serverDistFingerprint', {'sha256': 'f' * 64, 'files': 3})]:
            with self.subTest(key=key):
                old = self.binding[key]
                self.binding[key] = value
                with self.assertRaises(ValueError):
                    self.verify()
                self.binding[key] = old

    def test_worker_process_and_environment_checks_remain_required(self):
        for field, value in [('environmentId', 'foreign-environment'), ('sourceCommit', 'f' * 40)]:
            with self.subTest(field=field):
                old = self.raws['m1'][field]
                self.raws['m1'][field] = value
                with self.assertRaises(ValueError):
                    self.verify()
                self.raws['m1'][field] = old

    def test_worker_role_requires_full_service_record(self):
        self.save()
        del self.runtimes['m1']['serviceReadback']
        reference = ref(self.root, 'missing-service.json', self.runtimes['m1'])
        with self.assertRaisesRegex(ValueError, 'remote service proof'):
            V.runtime(V.Evidence(self.root), reference, 'm1', released=True)


if __name__ == '__main__':
    unittest.main()
