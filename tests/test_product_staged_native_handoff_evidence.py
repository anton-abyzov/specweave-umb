"""Invented staged-native records only; no operational/native acceptance proof."""
import copy
import struct
import unittest
import test_product_handoff_evidence as fixtures
V, ref = fixtures.V, fixtures.ref

class StagedNativeTests(unittest.TestCase):
    setUp = fixtures.NativeBundledClientTests.setUp
    read = fixtures.NativeBundledClientTests.read
    verify = fixtures.NativeBundledClientTests.verify

    def fixture(self):
        c = fixtures.CANDIDATE
        app_path = '/synthetic/SpecWithCode.app'
        identity = {'pid':4242, 'uid':501, 'parent':1, 'startedAt': self.app['startedAt'], 'executable': self.app['executable']}
        state = {'service':{'sourceCommit': c['sourceCommit'], 'version':c['version'], 'pid':123},
                 'profile':{'path':'/synthetic/profile','device':1,'inode':2}, 'defaultState':{},
                 'configurationHashes':{k:'a'*64 for k in ('settings.json','environment-id','credentials.json','auth.json','desktop-service-credentials.json','saved-environments.json')}}
        helper = ref(self.root, 'staged-producer.py', b'# invented inert producer bytes, never executed\n')
        binding = {'sourceCommit':c['sourceCommit'],'version':c['version'],'asarSha256':self.app['appAsarSha256'],
                   'runtimeArchiveSha256':'b'*64,'helperSha256':helper['sha256']}
        br = ref(self.root,'staged-binding.json',binding)
        ax = ('Window: "SpecWithCode", App: SpecWithCode.\n 1 HTML content SpecWithCode, URL: studio://app/#/settings/general\n'
              ' 2 heading Version '+c['version']+', Value: 3\n 3 text '+c['version']+'\n'
              ' 4 heading Update track, Value: 3\n 5 combo box (settable) Description: Update track, Value: Stable\n').encode()
        pixels = b'\x89PNG\r\n\x1a\n' + struct.pack('>I',13) + b'IHDR' + struct.pack('>II',640,480) + b'\x08\x02\x00\x00\x00'+b'\x00'*4
        ui_artifacts = {'accessibility':ref(self.root,'native.ax.txt',ax),'screenshot':ref(self.root,'native.png',pixels)}
        ui = {'method':'settings-general-ui','bridgeStateObserved':False,'securityWarningBypassed':False,'quitPerformed':False,
              'applicationPath':app_path,'observedVersion':c['version'],'observedTrack':'Stable',
              'processRaw':'4242 '+identity['startedAt']+' '+identity['executable'],
              'startedAt':'2026-10-13T12:01:31Z','observedAt':'2026-10-13T12:01:32Z','processObservedAt':'2026-10-13T12:01:32Z',
              'ax':{'path':'/synthetic/native.ax.txt','sha256':ui_artifacts['accessibility']['sha256']},
              'screenshot':{'path':'/synthetic/native.png','sha256':ui_artifacts['screenshot']['sha256']},'screenshotLimitation':'Invented image; not visual acceptance.'}
        ur = ref(self.root,'raw-ui.json',ui)
        stage = {'at':'2026-10-13T12:01:00Z','phase':'staged-only','installationPerformed':False,
                 'bindingSha256':br['sha256'],'helperSha256':helper['sha256'],'state':state,
                 'candidateProof':{'executable':identity['executable'],'version':c['version'],'treeSha256':'c'*64},
                 'originalProof':{'treeSha256':'e'*64}}
        start = {'at':'2026-10-13T12:01:10Z','argv':[identity['executable']],'cwd':'/synthetic',
                 'environmentOverrides':{'STUDIO_HOME':'/synthetic/.specweave-studio/m4','STUDIO_DISABLE_AUTO_UPDATE':'true'},'before':state}
        spawn = {'at':'2026-10-13T12:01:11Z','pid':4242,'executable':identity['executable']}
        launch = {'at':'2026-10-13T12:01:30Z','nativeMain':identity,'appPath':app_path,'asarSha256':self.app['appAsarSha256'],
                  'state':state,'nativeUpdaterAndRouteReadbackPending':True}
        readback = {'at':'2026-10-13T12:01:33Z','phase':'candidate-native-settings-ui-verified','nativeProcesses':[identity],
                    'appPath':app_path,'state':state,'originalApplicationsTreeSha256':'e'*64,
                    'sixRouteOwnerEvidenceRequired':True,'normalPublishedUpdaterTestStillRequired':False,
                    'nativeUpdateEvidence':{'method':'settings-general-ui','bridgeResponseObserved':False,
                    'receiptSha256':ur['sha256'],'receiptPath':'/synthetic/raw-ui.json','observedAt':ui['observedAt']}}
        self.proof = {'kind':'staged-native-observation','at':launch['at'],'binding':br,'helper':helper,
                      'uiObservation':ur,'uiOriginPath':'/synthetic/raw-ui.json','uiArtifacts':ui_artifacts}
        for key,value in [('stage',stage),('launchStart',start),('spawn',spawn),('launch',launch),('readback',readback)]:
            self.proof[key] = ref(self.root,key+'.json',value)
        self.app['nativeProcessProof'] = ref(self.root,'staged-proof.json',self.proof)

    def mutate(self, key, fn):
        self.fixture()
        value = self.read(self.proof[key]); fn(value)
        self.proof[key] = ref(self.root,key+'-changed.json',value)
        self.app['nativeProcessProof'] = ref(self.root,'staged-proof.json',self.proof)
        with self.assertRaises((ValueError,KeyError)):
            self.verify()

    def test_actual_split_record_shape_preserves_raw_phase(self):
        self.fixture();self.verify()
        self.assertEqual(self.read(self.proof['readback'])['phase'],'candidate-native-settings-ui-verified')
        self.assertNotIn('nativeProcess',self.proof)

    def test_changed_candidate_binding_rejected(self):
        self.mutate('binding',lambda d:d.update(sourceCommit='0'*40))

    def test_changed_retained_producer_rejected(self):
        self.fixture();self.proof['helper']=ref(self.root,'other.py',b'other')
        self.app['nativeProcessProof']=ref(self.root,'staged-proof.json',self.proof)
        with self.assertRaises(ValueError):self.verify()

    def test_launch_wrong_asar_rejected(self):
        self.mutate('launch',lambda d:d.update(asarSha256='0'*64))

    def test_launch_wrong_app_rejected(self):
        self.mutate('launch',lambda d:d.update(appPath='/other/SpecWithCode.app'))

    def test_spawn_wrong_pid_rejected(self):
        self.mutate('spawn',lambda d:d.update(pid=42))

    def test_candidate_readback_cannot_be_a_stage(self):
        self.mutate('readback',lambda d:d.update(phase='staged-only'))

    def test_launch_start_cannot_enable_updater(self):
        self.mutate('launchStart',lambda d:d['environmentOverrides'].update(STUDIO_DISABLE_AUTO_UPDATE='false'))

    def test_unknown_env_override_refused(self):
        self.mutate('launchStart',lambda d:d['environmentOverrides'].update(NODE_OPTIONS='--inspect'))

    def test_readback_protected_config_drift_rejected(self):
        self.mutate('readback',lambda d:d['state']['configurationHashes'].update({'auth.json':'0'*64}))

    def test_readback_service_identity_drift_rejected(self):
        self.mutate('readback',lambda d:d['state']['service'].update(pid=44))

    def test_reused_pid_with_new_start_rejected(self):
        self.mutate('readback',lambda d:d['nativeProcesses'][0].update(startedAt='Tue Oct 13 12:03:00 2026'))

    def test_foreign_child_executable_rejected(self):
        self.mutate('readback',lambda d:d['nativeProcesses'].append({'pid':4343,'uid':501,'executable':'/foreign/bin'}))

    def test_mismatched_ui_ref_rejected(self):
        self.mutate('readback',lambda d:d['nativeUpdateEvidence'].update(receiptSha256='0'*64))

    def test_fabricated_bridge_state_rejected(self):
        self.mutate('uiObservation',lambda d:d.update(bridgeStateObserved=True))

    def test_later_launch_cannot_backdate_proof(self):
        self.mutate('launch',lambda d:d.update(at='2026-10-13T12:02:00Z'))

    def test_slow_ui_observation_rejected(self):
        self.mutate('uiObservation',lambda d:d.update(startedAt='2026-10-13T12:00:30Z'))

    def test_wrong_optional_ui_source_rejected(self):
        self.mutate('uiObservation',lambda d:d.update(sourceCommit='0'*40))

    def test_unchanged_legacy_proof_still_passes(self):
        self.verify()

    def test_jpeg_magic_under_png_filename_is_truthful(self):
        data=b'\xff\xd8\xff\xc0\x00\x08\x08'+struct.pack('>HH',480,640)+b'\x01\xff\xd9'
        self.assertEqual(V.native_screenshot_shape(data),{'encoding':'jpeg','width':640,'height':480})

    def test_truncated_or_tiny_images_rejected(self):
        for data in [b'PNG',b'\xff\xd8\xff\xc0\x00\xff',b'\xff\xd8\xff\xd9',
                     b'\xff\xd8\xff\xc0\x00\x08\x08'+struct.pack('>HH',10,10)+b'\x01\xff\xd9']:
            with self.subTest(data=data),self.assertRaises(ValueError):V.native_screenshot_shape(data)

if __name__=='__main__':unittest.main()
