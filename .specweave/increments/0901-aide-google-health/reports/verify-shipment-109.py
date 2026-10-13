#!/usr/bin/env python3
"""Read-only release/install verification. Never starts providers or Google calls."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import plistlib
import re
import subprocess
import urllib.request

ROOT = Path(__file__).resolve().parent
PRODUCT = ROOT.parents[3] / 'repositories/anton-abyzov/specweave-studio'
SOURCE = '51c49ab4603c17c87362e9700cd242b24ed83e2e'
REVIEWED = '1ec4388aeb499745a92f3bd63f2d37ad6153f251'
ARCHIVE = '552c4c7101b5d71e62e43d9e6d59b8ed95e7edc803368dbe6dbf0a2e8c053a7f'
GUARD = Path.home() / '.local/share/specweave-studio/verification/0905/reservation-20261013T1241/install-attempt-1/update.json'
ABOUT = Path('/Users/antonabyzov/Projects/research/studio-readability-release-2026-10-13/desktop-about-capture-109.json')

def read(path):
    return json.loads(path.read_text())

def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()

published = ROOT / 'release-109-published.json'
assert sha(published) == '01825a497f2701b36b3a0e47943bdd4394d1be3e59bda40728b7111cc739a773'
release = read(published)
assert release['result'] == 'passed' and release['releaseState'] == 'published'
assert release['version'] == '1.0.9' and release['sourceCommit'] == SOURCE
assert len(release['releases']) == 2
for feed in release['releases']:
    assert feed['tag'] == 'v1.0.9' and not feed['draft'] and feed['assetsVerified'] == 11
assert any(f['repository'] == 'anton-abyzov/specwithcode' and f['publicUnauthenticatedReadback'] for f in release['releases'])

files = [
    'apps/web/src/components/settings/GoogleAccountSettings.tsx',
    'apps/web/src/components/settings/ScheduledTasksSettings.tsx',
    'apps/web/src/components/settings/scheduledTasksSettings.logic.ts',
    'apps/web/src/components/settings/scheduledTasksSettings.logic.test.ts',
    'apps/web/src/components/settings/ThemeSettings.tsx',
    'apps/web/src/components/settings/ScheduledTaskLink.tsx',
    'apps/web/src/components/chat/ThreadAutomationsPanel.tsx',
    'scripts/studio-google/verify.mjs',
]
def blob(commit, name):
    return subprocess.check_output(['git', '-C', str(PRODUCT), 'show', commit + ':' + name])
for name in files:
    assert blob(SOURCE, name) == blob(REVIEWED, name), name
timeline = blob(SOURCE, 'apps/web/src/components/chat/MessagesTimeline.tsx').decode()
assert 'import { ScheduledTaskLink }' in timeline and '<ScheduledTaskLink' in timeline

guard = read(GUARD)
result = read(GUARD.with_name('result.json'))
assert result['exitCode'] == 0 and result['guardedReceiptVerified'] and result['configPlistPreserved']
assert result['receiptSha256'] == sha(GUARD) == '796392c7d3ecfcab94479e34643358d71b84e43580bab722804e1b400eb92162'
assert guard['phase'] == 'verified' and guard['completeDatabaseContinuity'] == 'verified'
for key in ['preservedRowsAuthAndIdentity', 'originalServicesPreserved', 'onlyKnownOwnedServiceRestarted']:
    assert guard[key] is True, key
assert guard['after']['artifactSourceCommit'] == SOURCE and guard['after']['archiveSha256'] == ARCHIVE
base = Path.home() / '.specweave-studio/m4'
installation = read(base / 'installation.json')
runtime = read(base / 'userdata/server-runtime.json')
assert installation['version'] == '1.0.9' and installation['sourceCommit'] == SOURCE
assert installation['archiveSha256'] == ARCHIVE
assert runtime['pid'] == guard['after']['servicePid']
assert runtime['host'] == '127.0.0.1' and runtime['port'] == 8319
runtime_root = Path(installation['release'])
cmd = subprocess.check_output(['ps', '-p', str(runtime['pid']), '-o', 'command='], text=True)
assert str(runtime_root / 'bin.mjs') in cmd
manifest = read(runtime_root / 'studio-manifest.json')
assert manifest['version'] == '1.0.9' and manifest['sourceCommit'] == SOURCE
for entry in manifest['files']:
    path = runtime_root / entry['path']
    if entry['type'] == 'file':
        assert path.stat().st_size == entry['bytes'] and sha(path) == entry['sha256'], entry['path']
    elif entry['type'] == 'symlink':
        assert os.readlink(path) == entry['target'], entry['path']
    else:
        raise AssertionError('Unrecognized manifest entry type')
with urllib.request.urlopen('http://127.0.0.1:8319/', timeout=10) as response:
    assert response.status == 200
    html = response.read().decode()
asset = re.search(r'<script[^>]*src="(/assets/[^\"]+\.js)"', html)
assert asset
with urllib.request.urlopen('http://127.0.0.1:8319' + asset.group(1), timeout=10) as response:
    assert response.status == 200 and len(response.read()) > 100

app = Path('/Applications/SpecWithCode.app')
plist = plistlib.loads((app / 'Contents/Info.plist').read_bytes())
assert plist['CFBundleShortVersionString'] == '1.0.9'
assert sha(app / 'Contents/Resources/app.asar') == release['local']['desktop']['appAsarSha256']
subprocess.run(['codesign', '--verify', '--deep', '--strict', str(app)], check=True, capture_output=True)
about = read(ABOUT)
assert about['version'] == '1.0.9' and about['sourceCommitShort'] == SOURCE[:12]
desktop_command = subprocess.check_output(['ps', '-p', str(about['desktopPid']), '-o', 'comm='], text=True).strip()
assert desktop_command == str(app / 'Contents/MacOS/SpecWithCode')
receipt = {
    'checkedAt': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'version': '1.0.9', 'sourceCommit': SOURCE, 'result': 'passed',
    'publicReceiptSha256': sha(published), 'guardReceiptSha256': sha(GUARD),
    'nativeAboutReceiptSha256': sha(ABOUT), 'runtimeArchiveSha256': ARCHIVE,
    'reviewedNavigationFilesMatched': len(files), 'chatTimelineLinkRetained': True,
    'installedManifestEntriesVerified': len(manifest['files']),
    'runtimePid': runtime['pid'], 'runtimeHTTP': 200, 'webAssetHTTP': 200,
    'desktopPid': about['desktopPid'], 'desktopSignatureVerified': True,
    'nativeLoadedDesktopVersionVerified': True,
    'completeDatabaseContinuity': guard['completeDatabaseContinuity'],
    'rowPreservation': guard['rowPreservation'],
    'protectedAuthIdentityAndOriginalServicesPreserved': True,
    'googleProof': 'Separate real Aide proof on 1.0.8; no repeated Google calls',
}
(ROOT / 'shipment-109-verified.json').write_text(json.dumps(receipt, indent=2) + '\n')
print(json.dumps(receipt))
