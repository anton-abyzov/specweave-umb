"""Run over existing SSH stdin. GET status + read checkpoint; no mutable endpoint."""
import datetime,json,subprocess,urllib.request
names=['scanner-worker-crawl-worker-1','scanner-worker-scanner-worker-1']
expected=['0c47dfee262668ab608c461e16896f76f2582aa12ce7df6a943f11d553f8db0a','2633c121f4f10ed37a6a23f0b7b762a228ab6bd3d12d2a149c30f2b79e8919ff']
containers=[]
for name,identity in zip(names,expected):
 c=json.loads(subprocess.check_output(['docker','inspect',name]))[0]
 if c['Id']!=identity:raise SystemExit('container_identity_changed')
 containers.append({'id':c['Id'],'image':c['Image'],'running':c['State']['Running'],'paused':c['State']['Paused'],'startedAt':c['State']['StartedAt'],'restartCount':c['RestartCount']})
js=r"""
const fs=require('fs'),crypto=require('crypto'),sha=x=>crypto.createHash('sha256').update(x).digest('hex');
const raw=fs.readFileSync('/tmp/crawl-state/github-sharded.json'),s=JSON.parse(raw),target='e3b3310ba35a22b2930f29b8482c17577a288bb7253c97ffd493c62a76dd4b50';
const accepted=new Set(s.acceptedKeys||[]),pending=s.pendingPage?.repos||[],key=r=>`${r.fullName}:${r.skillPath}`;
const targetPending=pending.filter(r=>sha(key(r))===target),unresolved=pending.filter(r=>!accepted.has(key(r)));
const counterNames=['totalDiscovered','totalSubmitted','totalCreated','totalSkipped','totalKnownSkipped','totalLost','totalErrors','totalRejected','totalPrivateFiltered','totalVisibilityUnknown'];
const counters=Object.fromEntries(counterNames.map(k=>[k,s.counters?.[k]??null]));
console.log(JSON.stringify({schemaVersion:s.schemaVersion,checkpointSha256:sha(raw),sweepId:s.sweepId,configSignature:s.configSignature,startedAt:s.startedAt,phase:s.phase,shardIndex:s.shardIndex,page:s.page,
leafSha256:s.leaves?.[s.shardIndex]?sha(JSON.stringify(s.leaves[s.shardIndex])):null,pendingPagePresent:Boolean(s.pendingPage),pendingPageSha256:s.pendingPage?sha(JSON.stringify(s.pendingPage)):null,pendingPageCount:pending.length,pendingUnresolvedCount:unresolved.length,
targetIdentitySha256:target,targetPendingCount:targetPending.length,targetUnresolvedCount:targetPending.filter(r=>!accepted.has(key(r))).length,targetAccepted:[...accepted].some(k=>sha(k)===target),
acceptedCurrentLeaf:accepted.size,discoveredCurrentLeaf:s.discoveredKeys?.length??0,distinctDiscoveredLowerBound:s.distinctKeys?.length??0,distinctCountExact:!s.distinctCountSaturated,recoveredFailureCount:s.recoveredFailureCount,counters}));
"""
checkpoint=json.loads(subprocess.check_output(['docker','exec',names[0],'node','-e',js]))
status=json.load(urllib.request.urlopen('http://127.0.0.1:9600/status',timeout=10))
s=status.get('scheduler',{}).get('sources',{}).get('github-sharded',{})
projection={k:s.get(k) for k in ['status','lastRunAt','runCount','continuationCount','errorCount','consecutiveErrors']}
print(json.dumps({'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'containers':containers,'checkpoint':checkpoint,'sourceStatus':projection,'source':'existing VM3 status GET + checkpoint read; no discovery/intake requests'},indent=2))
