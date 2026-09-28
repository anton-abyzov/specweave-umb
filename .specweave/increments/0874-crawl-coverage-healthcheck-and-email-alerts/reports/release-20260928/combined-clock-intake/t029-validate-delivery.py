"""Validate retained reviewed-source, CI, deployment and natural-heartbeat receipts only."""
import argparse, datetime, hashlib, json, pathlib, re
p=argparse.ArgumentParser();p.add_argument('--worker',required=True);p.add_argument('--deployment',required=True);p.add_argument('--first',required=True);p.add_argument('--second',required=True);p.add_argument('--checkout',required=True);p.add_argument('--amendment-ci',required=True);p.add_argument('--public-smoke',required=True);p.add_argument('--merged-ci',required=True);a=p.parse_args()
r=pathlib.Path('/tmp/cc-work-release-20260928/0874')
load=lambda file:json.loads(pathlib.Path(file).read_text())
manifest=load(r/'t029-source-manifest.json');ci=load(r/'t029-ci-final.json')
assert ci['headRefOid']==manifest['head']=='1687ce4837c5a430321e5e1c2fbafb4d860716de'
assert {x['name'] for x in ci['statusCheckRollup']}=={'e2e','vitest','Payload scan','npm audit signatures'}
assert all(x['conclusion']=='SUCCESS' for x in ci['statusCheckRollup'])
amendment=load(r/'t029-clock-source-manifest.json');amendedCI=load(a.amendment_ci)
assert amendedCI['headRefOid']==amendment['head']=='7c6c4d827ad70b44a2c0b86dd14a66c27745af36'
assert {x['name'] for x in amendedCI['statusCheckRollup']}=={'e2e','vitest','Payload scan','npm audit signatures'}
assert all(x['conclusion']=='SUCCESS' for x in amendedCI['statusCheckRollup'])
mergedCI=load(a.merged_ci)
assert {x['name'] for x in mergedCI['check_runs']}=={'e2e','vitest','Payload scan','npm audit signatures'}
assert all(x['status']=='completed' and x['conclusion']=='success' and x['head_sha']=='7f86c79ceeee190d6017d6e2f857a68ea522067a' for x in mergedCI['check_runs'])
expectedFiles={**manifest['files'],**amendment['files']}
for file,digest in expectedFiles.items():
 assert hashlib.sha256((pathlib.Path(a.checkout)/file).read_bytes()).hexdigest()==digest, 'Reviewed source changed: '+file
deployed=load(a.deployment);assert deployed['allSixConsumersMatch'] is True
def stamp(s):
 # Python 3.9 accepts exactly 3 or 6 fractional digits; Cloudflare may send 5.
 normalized=re.sub(r'\.(\d{1,5})(?=Z|[+-]\d\d:\d\d$)',lambda m:'.'+m.group(1).ljust(6,'0'),s)
 return datetime.datetime.fromisoformat(normalized.replace('Z','+00:00'))
latest=max(deployed['deployments']['deployments'],key=lambda d:stamp(d['created_on']))
assert latest['versions']==[{'version_id':a.worker,'percentage':100}]
smoke=load(a.public_smoke);assert smoke['workerVersion']==a.worker
assert stamp(smoke['at'])>=stamp(latest['created_on'])
checks={(x['method'],x['path']):x for x in smoke['checks']}
assert checks['GET','/api/v1/skills?limit=3']['status']==200 and checks['GET','/api/v1/skills?limit=3']['recordCount']>0
assert checks['GET','/api/v1/queue/health']['status']==200 and checks['GET','/api/v1/queue/health']['schemaVersion']==2
assert checks['GET','/catalog']['status']==200 and checks['GET','/catalog']['finalUrl']=='https://verified-skill.com/skills'
for path in ['/api/v1/e2e-harness/healthz','/api/v1/_test/healthz']:
 assert checks['GET',path]['status']==404
first=load(a.first);second=load(a.second)
assert first['workerVersion']==second['workerVersion']==a.worker
assert stamp(first['at'])>=stamp(latest['created_on']) and stamp(second['at'])>stamp(first['at'])
expected={'5.161.69.232','91.107.239.24','5.161.56.136'}
previous={x['vmId']:x for x in first['vms']};current={x['vmId']:x for x in second['vms']}
assert set(previous)==set(current)==expected
proof=[]
for vm in sorted(expected):
 old,new=previous[vm],current[vm]
 assert old['readStatus']==new['readStatus']=='ok'
 assert new['receivedAt']>old['receivedAt'], 'No second natural heartbeat for '+vm
 assert all(s['vmIdMatches'] and s['serverTimeMatches'] for s in old['observations']+new['observations'])
 assert old['observations'] and new['observations'], 'Missing actual source observations for '+vm
 proof.append({'vmId':vm,'firstReceivedAt':old['receivedAt'],'secondReceivedAt':new['receivedAt'],'sources':sorted(x['source'] for x in new['observations'])})
old=next(x for x in previous['5.161.56.136']['observations'] if x['source']=='github-sharded')
new=next(x for x in current['5.161.56.136']['observations'] if x['source']=='github-sharded')
assert old['sweepId']==new['sweepId']=='026ba568-3ac5-4855-95fd-6c441c8007d2'
for field in ['discoveredTotal','submittedTotal','totalErrors','totalLost','probesCompleted','probesPending','shardsCompleted','shardsTotal','distinctDiscoveredLowerBound']:
 assert field in old and field in new, 'Dropped target metadata: '+field
assert new['completed'] is False and new['coverageComplete'] is False
print(json.dumps({'reviewedSource':manifest['head'],'reviewedClockAmendment':amendment['head'],'workerVersion':a.worker,'allFourChecksGreen':True,'allFourMergedSourceChecksGreen':True,'allTenReviewedFilesMatch':True,'sixConsumersUnchanged':True,'currentVersionPublicSmokePassed':True,'naturalHeartbeatRecords':proof,'targetSweepId':new['sweepId'],'targetFailedAttemptItems':new['totalLost'],'partialSweep':True,'fullBreadthProven':False},indent=2))
