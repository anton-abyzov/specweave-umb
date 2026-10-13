#!/usr/bin/env python3
"""Run the unchanged published installer while its launchd scheduler is reserved."""
import datetime
import hashlib
import json
import os
import pathlib
import subprocess
import sys
import time

home = pathlib.Path.home()
base = home / '.specweave-studio/m4'
evidence = home / '.local/share/specweave-studio/verification/0901/install-live'
helpers = base / 'updates/helpers/1.0.7/studio-1.0.7-deployment-helpers-54aa7e7d7ba1/scripts/studio-fleet'
archive = base / 'updates/downloads/1.0.7/studio-1.0.7-54aa7e7d7ba1.tar.gz'
source = home / '.codex/worktrees/aide-google-health/specweave-umb/repositories/anton-abyzov/specweave-studio'
sha = '600a4c54e381cbaed29c7e530e19ae424e70ac80ba5da7d41104566b97951830'
sys.dont_write_bytecode = True
sys.path.insert(0, str(helpers))
import update_agent as agent

lock = agent.acquire_lock(base / 'updates/agent.lock', home)
assert lock is not None, 'Another updater owns the lock'
assert subprocess.run(['/bin/launchctl', 'print', 'gui/501/com.specweave.studio.m4.updater'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode != 0, 'Scheduler reservation missing'
assert not (base / 'updates/install-in-progress.json').exists(), 'Install already running'
assert hashlib.sha256(archive.read_bytes()).hexdigest() == sha
expected = subprocess.check_output(['git', 'show', '54aa7e7d7ba1c59bb2b7af2f31f7f6ab86a0e06f:scripts/studio-fleet/update.py'], cwd=source)
assert (helpers / 'update.py').read_bytes() == expected, 'Published helper changed'
stamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
prestate = evidence / ('prestate-' + stamp + '.json')
receipt = evidence / ('update-' + stamp + '.json')
env = dict(os.environ, STUDIO_UPDATE_APPLY_BUDGET='1500', PWDEBUG='0', PLAYWRIGHT_HTML_OPEN='never')
command = ['/usr/bin/python3', '-B', str(helpers / 'update.py'), '--identity', 'm4']
start = time.monotonic()
for attempt in range(3):
    log = evidence / ('snapshot-' + stamp + '-' + str(attempt) + '.log')
    with log.open('wb') as output:
        result = subprocess.run(command + ['--snapshot', str(prestate)], env=env, stdout=output, stderr=subprocess.STDOUT, pass_fds=(lock,), timeout=600)
    if result.returncode == 0:
        break
    tail = log.read_text()[-4000:]
    if 'has unexpected descendants' not in tail or 'REFUSAL descendants git=1' not in tail or attempt == 2:
        print(json.dumps({'phase': 'snapshot-refused', 'exitCode': result.returncode, 'log': str(log)}), flush=True)
        sys.exit(result.returncode)
    time.sleep(5)
print(json.dumps({'phase': 'prestate-captured', 'seconds': round(time.monotonic() - start, 2), 'prestate': str(prestate), 'receipt': str(receipt)}), flush=True)
log = evidence / ('update-' + stamp + '.log')
with log.open('wb') as output:
    process = subprocess.Popen(command + ['--prestate', str(prestate), '--archive', str(archive), '--sha256', sha, '--output', str(receipt), '--allow-existing-browser-heartbeat'], env=env, stdout=output, stderr=subprocess.STDOUT, pass_fds=(lock,))
    print(json.dumps({'phase': 'applying', 'pid': process.pid, 'receipt': str(receipt)}), flush=True)
    code = process.wait()
data = json.loads(receipt.read_text()) if receipt.exists() else {}
summary = {'at': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'seconds': round(time.monotonic() - start, 2), 'exitCode': code, 'receiptPath': str(receipt), 'receiptSha256': hashlib.sha256(receipt.read_bytes()).hexdigest() if receipt.exists() else None}
summary.update({key: data.get(key) for key in ['phase', 'result', 'error', 'pointers', 'preservedRowsAuthAndIdentity', 'originalServicesPreserved', 'onlyKnownOwnedServiceRestarted', 'completeDatabaseContinuity']})
(evidence / ('summary-' + stamp + '.json')).write_text(json.dumps(summary, indent=2) + '\n')
print(json.dumps(summary), flush=True)
os.close(lock)
sys.exit(code)
