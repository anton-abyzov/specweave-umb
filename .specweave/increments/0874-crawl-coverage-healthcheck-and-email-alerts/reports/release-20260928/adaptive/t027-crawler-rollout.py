"""Guarded crawler-only PR75 rollout. Default validates without changing state."""
import argparse, hashlib, json, pathlib, re, subprocess, urllib.request
from datetime import datetime, timezone

p = argparse.ArgumentParser()
p.add_argument('--merge-sha', required=True)
p.add_argument('--image-id', required=True)
p.add_argument('--scanner-env-sha', required=True)
p.add_argument('--crawler-env-sha', required=True)
p.add_argument('--apply', action='store_true')
args = p.parse_args()
assert re.fullmatch('[0-9a-f]{40}', args.merge_sha)
assert re.fullmatch('sha256:[0-9a-f]{64}', args.image_id)
assert all(re.fullmatch('[0-9a-f]{64}', h) for h in [args.scanner_env_sha, args.crawler_env_sha])
NAME = 'scanner-worker-crawl-worker-1'
OLD_ID = '6b4993745009807c3ac61bd3a8b6d8f2775da9d29c55137d87183775cd2d694a'
OLD_IMAGE = 'sha256:52ff7bbdd69eeb895bd34f16c501aad3d898ba5546fa0ddee4e3c5c574e31d14'
SCANNER = 'scanner-worker-scanner-worker-1'
SCANNER_ID = '2633c121f4f10ed37a6a23f0b7b762a228ab6bd3d12d2a149c30f2b79e8919ff'
FILES = {
    '/opt/scanner-worker/.env': args.scanner_env_sha,
    '/opt/crawl-worker/.env': args.crawler_env_sha,
    '/opt/scanner-worker/docker-compose.yml': '3d17aee7fbf5876cb28ad8331e2310b133ba7bcbebba9c1cf3a0f4feb5b7e875',
}
HASHES = {
    'server.js': '107e47757cbc0df85af1927ff40f5e64116035f6e969078f7a537d3f8bf79c67',
    'scheduler.js': 'ea8f2b9ca9842454324915e9a33542080d104035eb6f2e2306521be21630cc38',
    'sources/github-sharded.js': '2bc504dc50f1f52d88e85342bab3cd844e0e9cd05b8de6e811c82b9985b2b427',
    'lib/adaptive-search-plan.js': '6ee3988d568b668d6e3119f80a2c08fbcdf11e88a75997b7f2baf7ee40dcecee',
    'lib/inline-submitter.js': 'dcede5c9ec6be5a5b1b4a2851ac7b56161c23cb48c54c9cc299ca4282bc814b1',
    'lib/source-result.js': 'ec84beaeeb63bf208aa50c491610cce4df6dd9bcdba5e369c7f21d5a94bc24ac',
}
def inspect(name): return json.loads(subprocess.check_output(['docker','inspect',name]))[0]
def emit(phase, **data): print(json.dumps({'at':datetime.now(timezone.utc).isoformat(),'phase':phase,**data}), flush=True)
def hashes(command):
    raw = subprocess.check_output(command + ['sha256sum', *HASHES], text=True)
    return dict((line.split()[1],line.split()[0]) for line in raw.splitlines())
def guard(expected_tag=OLD_IMAGE):
    c = inspect(NAME)
    assert c['Id']==OLD_ID and c['Image']==OLD_IMAGE, 'Crawler identity changed'
    assert c['State']['Running'] and not c['State']['Paused'], 'Crawler deliberately stopped or paused'
    assert inspect(SCANNER)['Id']==SCANNER_ID, 'Protected scanner changed'
    assert all(hashlib.sha256(pathlib.Path(n).read_bytes()).hexdigest()==h for n,h in FILES.items()), 'Configuration changed'
    assert inspect('scanner-worker-crawl-worker')['Id']==expected_tag, 'Compose image tag changed'
    assert any(m.get('Name')=='scanner-worker_crawl-state' and m['Destination']=='/tmp/crawl-state' for m in c['Mounts']), 'State mount changed'
    status = json.load(urllib.request.urlopen('http://127.0.0.1:9600/status',timeout=10))
    assert status['activeCrawls']==0, 'Manual crawl active'
    assert status['scheduler'].get('running') is True, 'Scheduler deliberately stopped'
    sources = status['scheduler']['sources']
    assert set(sources)=={'github-sharded','skills-sh','submission-scanner'}, 'Source assignment changed'
    assert all(s['status'] in ['idle','cooldown'] for s in sources.values()), 'Scheduled source active'
    js = "const fs=require('fs');process.exit(fs.existsSync((process.env.CRAWL_STATE_DIR||'/tmp/crawl-state')+'/github-sharded.json')?1:0)"
    assert subprocess.run(['docker','exec',NAME,'node','-e',js]).returncode==0, 'Existing checkpoint must not be interrupted'
    return {name:s['status'] for name,s in sources.items()}

attempted = False
try:
    status = guard()
    image = inspect('vskill-crawl-worker:'+args.merge_sha)
    assert image['Id']==args.image_id and image['Config']['Labels']['org.opencontainers.image.revision']==args.merge_sha, 'Candidate image differs'
    assert hashes(['docker','run','--rm','--entrypoint','/usr/bin/env','vskill-crawl-worker:'+args.merge_sha])==HASHES, 'Candidate source differs'
    for name in ['/opt/scanner-worker/.env','/opt/crawl-worker/.env']:
        lines = pathlib.Path(name).read_text().splitlines()
        assert [line for line in lines if line.startswith('SHARD_BISECT=')]==['SHARD_BISECT=1'], 'Adaptive config not enabled exactly'
    emit('ready', mergeSha=args.merge_sha, image=args.image_id, sourceStatuses=status, files=FILES, sourceHashes=HASHES, apply=args.apply)
    if not args.apply: raise SystemExit(0)
    # Preserve the previous immutable image; no volume or other service is touched.
    subprocess.run(['docker','tag',OLD_IMAGE,'vskill-crawl-worker:rollback-0874-6b499374'],check=True)
    status = guard()  # repeat immediately before changing the service image tag
    emit('prestate',crawlerId=OLD_ID,scannerId=SCANNER_ID,oldImage=OLD_IMAGE,newImage=args.image_id,sourceStatuses=status)
    attempted = True
    emit('promotion-attempted',mergeSha=args.merge_sha)
    subprocess.run(['docker','tag','vskill-crawl-worker:'+args.merge_sha,'scanner-worker-crawl-worker'],check=True)
    emit('promotion-completed',image=args.image_id)
    guard(args.image_id)  # last idle/checkpoint/config check immediately before recreation
    result = subprocess.run(['docker','compose','up','-d','--no-deps','--no-build','--force-recreate','crawl-worker'],cwd='/opt/scanner-worker',capture_output=True,text=True)
    emit('compose-returned',exitCode=result.returncode)
    c = inspect(NAME)
    env = dict(x.split('=',1) for x in c['Config']['Env'] if '=' in x)
    assert c['Id']!=OLD_ID and c['Image']==args.image_id, 'New container image mismatch'
    assert c['State']['Running'] and not c['State']['Paused'], 'New crawler not running'
    assert inspect(SCANNER)['Id']==SCANNER_ID, 'Protected scanner changed'
    assert c['Config']['Labels'].get('org.opencontainers.image.revision')==args.merge_sha, 'Runtime revision mismatch'
    assert env.get('SHARD_BISECT')=='1' and env.get('SHARD_MODE')=='size-date', 'Runtime shard config mismatch'
    assert len([t for t in env.get('GITHUB_TOKENS','').split(',') if t.strip()])==1, 'Runtime token count changed'
    assert env.get('ASSIGNED_SOURCES')=='github-sharded,skills-sh,submission-scanner', 'Runtime sources changed'
    assert any(m.get('Name')=='scanner-worker_crawl-state' and m['Destination']=='/tmp/crawl-state' for m in c['Mounts']), 'Runtime state mount changed'
    assert hashes(['docker','exec',NAME])==HASHES, 'Runtime source differs'
    assert all(hashlib.sha256(pathlib.Path(n).read_bytes()).hexdigest()==h for n,h in FILES.items()), 'Post-rollout configuration changed'
    emit('readback',crawlerId=c['Id'],image=c['Image'],revision=args.merge_sha,scannerId=SCANNER_ID,tokenCount=1,shardMode=env.get('SHARD_MODE'),adaptive=True,sources=env.get('ASSIGNED_SOURCES'),stateVolume='scanner-worker_crawl-state',sourceHashes=HASHES)
    assert result.returncode==0, 'Compose returned failure despite readback; inspect before further actions'
except Exception as error:
    emit('partial_or_uncertain' if attempted else 'not-applied',errorType=type(error).__name__,reason=str(error)[:200],requireFreshReadback=attempted)
    raise SystemExit(1)
