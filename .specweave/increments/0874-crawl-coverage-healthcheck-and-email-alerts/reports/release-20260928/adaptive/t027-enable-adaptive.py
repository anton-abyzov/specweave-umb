"""Guarded VM3 SHARD_BISECT enablement; default is read-only preflight."""
import argparse, hashlib, json, os, pathlib, re, subprocess, tempfile, time, urllib.request
from datetime import datetime, timezone
p = argparse.ArgumentParser()
p.add_argument('--merge-sha', required=True)
p.add_argument('--image-id', required=True)
p.add_argument('--apply', action='store_true')
args = p.parse_args()
assert re.fullmatch('[0-9a-f]{40}', args.merge_sha)
assert re.fullmatch('sha256:[0-9a-f]{64}', args.image_id)
NAME = 'scanner-worker-crawl-worker-1'
OLD_ID = '6b4993745009807c3ac61bd3a8b6d8f2775da9d29c55137d87183775cd2d694a'
OLD_IMAGE = 'sha256:52ff7bbdd69eeb895bd34f16c501aad3d898ba5546fa0ddee4e3c5c574e31d14'
SCANNER = 'scanner-worker-scanner-worker-1'
SCANNER_ID = '2633c121f4f10ed37a6a23f0b7b762a228ab6bd3d12d2a149c30f2b79e8919ff'
EXPECTED = {
 '/opt/scanner-worker/.env': '94a681b1f67f786a39d20fbce9c41c492c1c9a3b85cb25f891e61d5ca076055e',
 '/opt/crawl-worker/.env': '8d7f11b89c1f3a9ef67abb417d8603b32076966711199ef167b838ec7c5f28d7',
}
COMPOSE = '/opt/scanner-worker/docker-compose.yml'
COMPOSE_SHA = '3d17aee7fbf5876cb28ad8331e2310b133ba7bcbebba9c1cf3a0f4feb5b7e875'
def digest(b): return hashlib.sha256(b).hexdigest()
def inspect(name): return json.loads(subprocess.check_output(['docker','inspect',name]))[0]
def emit(phase, **data): print(json.dumps({'at':datetime.now(timezone.utc).isoformat(),'phase':phase,**data}), flush=True)
def guard(expected):
 c=inspect(NAME)
 assert c['Id']==OLD_ID and c['Image']==OLD_IMAGE, 'Crawler identity changed'
 assert c['State']['Running'] and not c['State']['Paused'], 'Crawler deliberately stopped or paused'
 assert inspect(SCANNER)['Id']==SCANNER_ID, 'Protected scanner changed'
 assert digest(pathlib.Path(COMPOSE).read_bytes())==COMPOSE_SHA, 'Compose changed'
 assert all(digest(pathlib.Path(n).read_bytes())==h for n,h in expected.items()), 'Environment changed'
 assert any(m.get('Name')=='scanner-worker_crawl-state' and m['Destination']=='/tmp/crawl-state' for m in c['Mounts']), 'State mount changed'
 status=json.load(urllib.request.urlopen('http://127.0.0.1:9600/status',timeout=10))
 assert status['activeCrawls']==0, 'Manual crawl active'
 assert status['scheduler'].get('running') is True, 'Scheduler deliberately stopped'
 sources=status['scheduler']['sources']
 assert set(sources)=={'github-sharded','skills-sh','submission-scanner'}, 'Source assignment changed'
 assert all(s['status'] in ['idle','cooldown'] for s in sources.values()), 'Scheduled source active'
 js="const fs=require('fs');process.exit(fs.existsSync((process.env.CRAWL_STATE_DIR||'/tmp/crawl-state')+'/github-sharded.json')?1:0)"
 assert subprocess.run(['docker','exec',NAME,'node','-e',js]).returncode==0, 'Coarse checkpoint exists'
 return {name:s['status'] for name,s in sources.items()}
originals={}; metadata={}; replacements={}; applied=[]; attempted=[]; backup=None
try:
 statuses=guard(EXPECTED)
 image=inspect('vskill-crawl-worker:'+args.merge_sha)
 assert image['Id']==args.image_id and image['Config']['Labels']['org.opencontainers.image.revision']==args.merge_sha, 'Candidate image differs'
 for name in EXPECTED:
  file=pathlib.Path(name); b=file.read_bytes(); originals[name]=b; metadata[name]=file.stat()
  matches=[line for line in b.splitlines() if line.startswith(b'SHARD_BISECT=')]
  assert len(matches)<=1 and (not matches or matches[0] in [b'SHARD_BISECT=0',b'SHARD_BISECT=false']), 'Adaptive prestate changed'
  if matches: out=b''.join(b'SHARD_BISECT=1\n' if line.startswith(b'SHARD_BISECT=') else line for line in b.splitlines(keepends=True))
  else: out=b+(b'' if b.endswith(b'\n') else b'\n')+b'SHARD_BISECT=1\n'
  replacements[name]=out
 emit('ready',mergeSha=args.merge_sha,image=args.image_id,sourceStatuses=statuses,files={n:{'before':EXPECTED[n],'after':digest(b)} for n,b in replacements.items()},changedKeys=['SHARD_BISECT'],apply=args.apply)
 if not args.apply: raise SystemExit(0)
 backup=pathlib.Path('/root/vskill-release-backups')/('0874-adaptive-'+time.strftime('%Y%m%dT%H%M%SZ',time.gmtime()))
 backup.mkdir(mode=0o700,exist_ok=False)
 for index,(name,b) in enumerate(originals.items()):
  fd=os.open(backup/(str(index)+'.env'),os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
  with os.fdopen(fd,'wb') as f: f.write(b); f.flush(); os.fsync(f.fileno())
 fd=os.open(backup,os.O_RDONLY|os.O_DIRECTORY)
 try: os.fsync(fd)
 finally: os.close(fd)
 fd=os.open(backup.parent,os.O_RDONLY|os.O_DIRECTORY)
 try: os.fsync(fd)
 finally: os.close(fd)
 expected=dict(EXPECTED)
 for name,b in replacements.items():
  file=pathlib.Path(name); m=metadata[name]
  fd,staging=tempfile.mkstemp(prefix='.0874-adaptive-',dir=file.parent)
  try:
   with os.fdopen(fd,'wb') as f:
    f.write(b); f.flush(); os.fchown(f.fileno(),m.st_uid,m.st_gid); os.fchmod(f.fileno(),m.st_mode&0o777); os.fsync(f.fileno())
   guard(expected) # all-source idle and checkpoint check immediately before EACH replacement
   current=file.stat()
   assert (current.st_uid,current.st_gid,current.st_mode)==(m.st_uid,m.st_gid,m.st_mode), 'File metadata changed'
   assert file.read_bytes()==originals[name], 'File bytes changed before replace'
   assert inspect(NAME)['Id']==OLD_ID and inspect(SCANNER)['Id']==SCANNER_ID, 'Container changed before replace'
   attempted.append(name)
   os.replace(staging,file)
   receipt={'path':name,'sha256':digest(b),'replacementCompleted':True,'readbackMatches':None}
   applied.append(receipt); emit('replacementCompleted',**receipt)
   fd=os.open(file.parent,os.O_RDONLY|os.O_DIRECTORY)
   try: os.fsync(fd)
   finally: os.close(fd)
   receipt['readbackMatches']=file.read_bytes()==b
   emit('readback',**receipt)
   assert receipt['readbackMatches'], 'File readback mismatch'
   expected[name]=digest(b)
  finally:
   if os.path.exists(staging): os.unlink(staging)
 emit('applied',mergeSha=args.merge_sha,backupDirectory=str(backup),changedKeys=['SHARD_BISECT'],files=applied,restarted=False)
except Exception as error:
 emit('partial_or_uncertain' if attempted else 'not-applied',errorType=type(error).__name__,reason=str(error)[:200],replaceAttempted=attempted,applied=applied,backupDirectory=str(backup) if backup else None,restarted=False,requireFreshReadback=bool(attempted))
 raise SystemExit(1)
