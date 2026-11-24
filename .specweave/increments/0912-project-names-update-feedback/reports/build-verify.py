import os, subprocess, json, hashlib, datetime
from pathlib import Path
repo=Path('/Users/antonabyzov/.codex/worktrees/project-names-release/specweave-umb/repositories/anton-abyzov/specweave-studio')
out=Path(__file__).parent
node22='/Users/antonabyzov/.nvm/versions/node/v22.20.0/bin/node'
node24='/Users/antonabyzov/.local/share/specweave-studio/toolchains/node-v24.13.1-darwin-arm64/bin/node'
source=subprocess.check_output(['git','rev-parse','HEAD'],cwd=repo,text=True).strip()
assert not subprocess.check_output(['git','status','--porcelain'],cwd=repo,text=True).strip()
receipt={'source':source,'startedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'steps':[],'proof':'production web and integrated server builds; no live store or providers'}
for name,cmd,cwd,node in [('web',[node24,str(repo/'node_modules/vite-plus/bin/vp'),'build'],repo/'apps/web',node24),('server',[node22,'apps/server/scripts/cli.ts','build'],repo,node22)]:
 env=dict(os.environ,PWDEBUG='0',PLAYWRIGHT_HTML_OPEN='never',PATH=str(Path(node).parent)+':'+str(repo/'node_modules/.bin')+':'+os.environ['PATH'])
 log=out/(name+'-build.log')
 with log.open('w') as f: code=subprocess.run(cmd,cwd=cwd,env=env,stdout=f,stderr=subprocess.STDOUT).returncode
 receipt['steps'].append({'name':name,'command':cmd,'cwd':str(cwd),'runtime':subprocess.check_output([node,'--version'],text=True).strip(),'exitCode':code,'log':str(log),'sha256':hashlib.sha256(log.read_bytes()).hexdigest()})
 (out/'build-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
 print(name,code,flush=True)
 if code: raise SystemExit(code)
receipt['sourceUnchanged']=subprocess.check_output(['git','rev-parse','HEAD'],cwd=repo,text=True).strip()==source and not subprocess.check_output(['git','status','--porcelain'],cwd=repo,text=True).strip()
receipt['clientIntegrated']=(repo/'apps/server/dist/client/index.html').is_file()
receipt['completedAt']=datetime.datetime.now(datetime.timezone.utc).isoformat()
(out/'build-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
assert receipt['sourceUnchanged'] and receipt['clientIntegrated']
