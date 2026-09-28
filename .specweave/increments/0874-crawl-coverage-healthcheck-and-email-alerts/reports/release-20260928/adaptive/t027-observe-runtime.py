"""Read-only, identity-free runtime and durable progress receipt."""
import datetime, json, subprocess, urllib.request
name = 'scanner-worker-crawl-worker-1'
c = json.loads(subprocess.check_output(['docker','inspect',name]))[0]
s = json.load(urllib.request.urlopen('http://127.0.0.1:9600/status',timeout=10))
fields = ['status','lastRunAt','runCount','continuationCount','errorCount','consecutiveErrors']
result_fields = ['completed','phase','sweepId','sweepTotals','probesCompleted','probesPending','shardsTotal','shardsCompleted','shardsZeroResultCount','coverageComplete','cappedLeafCount','omittedLowerBound','discoveryCounting','distinctDiscoveredLowerBound','distinctCountExact','distinctKeysSha256','recoveredFailureCount','totalDiscovered','totalSubmitted','totalCreated','totalSkipped','totalKnownSkipped','totalLost','totalErrors','totalRejected','totalPrivateFiltered','totalVisibilityUnknown','retryAt','durationMs']
sources = {}
for key,value in s.get('scheduler',{}).get('sources',{}).items():
    sources[key] = {k:value.get(k) for k in fields}
    sources[key]['lastResult'] = {k:value.get('lastResult',{}).get(k) for k in result_fields} if isinstance(value.get('lastResult'),dict) else None
js = r"""
const fs=require('fs'),crypto=require('crypto');
const p=(process.env.CRAWL_STATE_DIR||'/tmp/crawl-state')+'/github-sharded.json';
const sha=x=>crypto.createHash('sha256').update(x).digest('hex');
let checkpoint={exists:false};
if(fs.existsSync(p)) {
 const raw=fs.readFileSync(p),s=JSON.parse(raw),m=fs.statSync(p);
 checkpoint={exists:true,sha256:sha(raw),mode:(m.mode&511).toString(8),schemaVersion:s.schemaVersion,
 sweepId:s.sweepId,configSignature:s.configSignature,startedAt:s.startedAt,phase:s.phase,
 probesCompleted:s.probesCompleted,probesPending:s.pending?.length,leaves:s.leaves?.length,
 shardsCompleted:s.shardIndex,page:s.page,zeroLeaves:s.shardsZeroResultCount,
 pendingPageItems:s.pendingPage?.repos?.length??0,acceptedCurrentLeaf:s.acceptedKeys?.length??0,
 discoveredCurrentLeaf:s.discoveredKeys?.length??0,counters:s.counters,recoveredFailureCount:s.recoveredFailureCount,
 distinctDiscoveredLowerBound:s.distinctKeys?.length??0,distinctCountExact:!s.distinctCountSaturated,
 distinctKeysSha256:sha(JSON.stringify([...(s.distinctKeys||[])].sort())),
 cappedLeafCount:s.leaves?.filter(x=>x.capped).length,coverageComplete:false};
}
console.log(JSON.stringify({node:process.version,adaptive:process.env.SHARD_BISECT,
shardMode:process.env.SHARD_MODE,assignedSources:process.env.ASSIGNED_SOURCES,
tokenCount:(process.env.GITHUB_TOKENS||'').split(',').filter(Boolean).length,checkpoint}));
"""
runtime=json.loads(subprocess.check_output(['docker','exec',name,'node','-e',js]))
scanner=json.loads(subprocess.check_output(['docker','inspect','scanner-worker-scanner-worker-1']))[0]
print(json.dumps({'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'crawlerId':c['Id'],'image':c['Image'],'revision':c['Config'].get('Labels',{}).get('org.opencontainers.image.revision'),'running':c['State']['Running'],'paused':c['State']['Paused'],'scannerId':scanner['Id'],'activeCrawls':s.get('activeCrawls'),'schedulerRunning':s.get('scheduler',{}).get('running'),'sources':sources,'runtime':runtime},indent=2))
