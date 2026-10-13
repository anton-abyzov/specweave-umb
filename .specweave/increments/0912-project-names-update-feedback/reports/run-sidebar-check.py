"""Own one ephemeral fixture process; retain evidence and stop only that exact PID."""
import subprocess, socket, time, os, json, hashlib
from pathlib import Path
out=Path(__file__).parent
node='/Users/antonabyzov/.local/share/specweave-studio/toolchains/node-v24.13.1-darwin-arm64/bin/node'
python=Path('/Users/antonabyzov/Projects/research/studio-project-names-release-2026-10-13/venv/bin/python')
repo=Path('/Users/antonabyzov/.codex/worktrees/project-names-release/specweave-umb/repositories/anton-abyzov/specweave-studio')
build=json.loads((out/'build-receipt.json').read_text())
source=subprocess.check_output(['git','rev-parse','HEAD'],cwd=repo,text=True).strip()
assert source==build['source'] and build['sourceUnchanged'] and build['clientIntegrated']
for step in build['steps']:
 assert step['exitCode']==0 and hashlib.sha256(Path(step['log']).read_bytes()).hexdigest()==step['sha256']
with socket.socket() as sock:
 sock.bind(('127.0.0.1',0)); port=sock.getsockname()[1]
env=dict(os.environ,SIDEBAR_VERIFY_PORT=str(port),PWDEBUG='0',PLAYWRIGHT_HTML_OPEN='never')
with (out/'sidebar-server.log').open('w') as log:
 process=subprocess.Popen([node,str(out/'serve-sidebar.mjs')],cwd=repo,env=env,stdout=log,stderr=subprocess.STDOUT)
 try:
  for attempt in range(120):
   if process.poll() is not None: raise RuntimeError('Owned fixture exited; see sidebar-server.log')
   with socket.socket() as sock:
    if sock.connect_ex(('127.0.0.1',port))==0: break
   time.sleep(.25)
  else: raise RuntimeError('Owned fixture not listening')
  result=subprocess.run([str(python),str(out/'browser-check.py')],cwd=repo,env=env)
  if result.returncode: raise SystemExit(result.returncode)
 finally:
  process.terminate()
  try: process.wait(timeout=10)
  except subprocess.TimeoutExpired:
   process.kill(); process.wait(timeout=5)
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=repo,text=True).strip()==source
assert not subprocess.check_output(['git','status','--porcelain'],cwd=repo,text=True).strip()
print('Verified retained production builds and headless Sidebar UI at '+source)
