#!/usr/bin/env python3
"""Read back the positive guard receipt, live M4 runtime and installed desktop."""
import datetime
import hashlib
import json
import pathlib
import plistlib
import re
import subprocess
import sys
import urllib.request

receipt_path = pathlib.Path(sys.argv[1])
output_path = pathlib.Path(sys.argv[2])
receipt = json.loads(receipt_path.read_text())
assert receipt['phase'] == 'verified', 'No positive guarded receipt'
for key in ['preservedRowsAuthAndIdentity', 'originalServicesPreserved', 'onlyKnownOwnedServiceRestarted']:
    assert receipt[key] is True, key
assert receipt['completeDatabaseContinuity'] == 'verified'
base = pathlib.Path.home() / '.specweave-studio/m4'
installation = json.loads((base / 'installation.json').read_text())
runtime = json.loads((base / 'userdata/server-runtime.json').read_text())
expected_sha = '600a4c54e381cbaed29c7e530e19ae424e70ac80ba5da7d41104566b97951830'
expected_source = '54aa7e7d7ba1c59bb2b7af2f31f7f6ab86a0e06f'
assert installation['version'] == '1.0.7'
assert installation['sourceCommit'] == expected_source
assert installation['archiveSha256'] == expected_sha
assert receipt['after']['archiveSha256'] == expected_sha
assert receipt['after']['artifactSourceCommit'] == expected_source
assert runtime['pid'] == receipt['after']['servicePid']
assert runtime['host'] == '127.0.0.1' and runtime['port'] == 8319
command = subprocess.check_output(['ps', '-p', str(runtime['pid']), '-o', 'command='], text=True)
assert str(installation['release']) + '/bin.mjs' in command
with urllib.request.urlopen('http://127.0.0.1:8319/', timeout=10) as response:
    assert response.status == 200
    html = response.read().decode()
asset = re.search(r'<script[^>]*src="(/assets/[^\"]+\.js)"', html)
assert asset, 'Production UI asset missing'
with urllib.request.urlopen('http://127.0.0.1:8319' + asset.group(1), timeout=10) as response:
    assert response.status == 200
    assert len(response.read()) > 100
app = pathlib.Path('/Applications/SpecWithCode.app')
desktop = plistlib.loads((app / 'Contents/Info.plist').read_bytes())
assert desktop['CFBundleShortVersionString'] == '1.0.7'
assert desktop['CFBundleVersion'] == '1.0.7'
processes = subprocess.check_output(['ps', '-axo', 'pid=,comm='], text=True).splitlines()
desktop_pids = [int(line.strip().split(None, 1)[0]) for line in processes if line.strip().endswith('/Applications/SpecWithCode.app/Contents/MacOS/SpecWithCode')]
assert desktop_pids, 'Desktop is not running from installed bundle'
summary = {'checkedAt': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'version': '1.0.7', 'sourceCommit': expected_source, 'archiveSha256': expected_sha, 'guardReceipt': str(receipt_path), 'guardReceiptSha256': hashlib.sha256(receipt_path.read_bytes()).hexdigest(), 'phase': receipt['phase'], 'completeDatabaseContinuity': receipt['completeDatabaseContinuity'], 'rowPreservation': receipt['rowPreservation'], 'runtimePid': runtime['pid'], 'runtimeHTTP': 200, 'webAssetHTTP': 200, 'desktopVersion': desktop['CFBundleShortVersionString'], 'desktopPids': desktop_pids, 'googleAccessVerified': False}
output_path.write_text(json.dumps(summary, indent=2) + '\n')
print(json.dumps(summary))
