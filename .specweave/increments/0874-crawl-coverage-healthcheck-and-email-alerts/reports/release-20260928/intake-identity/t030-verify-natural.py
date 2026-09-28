"""Pure receipt comparison. Never calls discovery, intake, scheduler mutations, or DB writes."""
import argparse,copy,datetime,hashlib,json,pathlib,re,subprocess,sys
ROOT=pathlib.Path(__file__).resolve().parent
EXPECTED_SWEEP='026ba568-3ac5-4855-95fd-6c441c8007d2'
TARGET='e3b3310ba35a22b2930f29b8482c17577a288bb7253c97ffd493c62a76dd4b50'
def stamp(s):return datetime.datetime.fromisoformat(s.replace('Z','+00:00'))
def evaluate(before,after,receipt,worker):
 b=before['checkpoint'];a=after['checkpoint']
 deployments=receipt.get('deployments',{}).get('deployments',[])
 latest=max(deployments,key=lambda d:stamp(d['created_on'])) if deployments else None
 versions=latest.get('versions',[]) if latest else []
 deployment_ok=len(versions)==1 and versions[0].get('version_id')==worker and versions[0].get('percentage')==100
 checks={
 'baseline_is_exact_blocked_item':b['sweepId']==EXPECTED_SWEEP and b['targetIdentitySha256']==TARGET and b['targetUnresolvedCount']==1 and b['acceptedCurrentLeaf']==399 and b['discoveredCurrentLeaf']==400,
 'worker_latest_at_100_percent':deployment_ok,
 'snapshot_after_deployment':bool(latest) and stamp(after['at'])>=stamp(latest['created_on']),
 'natural_run_started_after_deployment':bool(latest) and bool(after['sourceStatus'].get('lastRunAt')) and stamp(after['sourceStatus']['lastRunAt'])>=stamp(latest['created_on']),
 'same_containers_images_process_starts':all(x['id']==y['id'] and x['image']==y['image'] and x['startedAt']==y['startedAt'] and x['restartCount']==y['restartCount'] and y['running'] and not y['paused'] for x,y in zip(before['containers'],after['containers'])) and len(before['containers'])==len(after['containers'])==2,
 'same_existing_sweep_config':a['schemaVersion']==b['schemaVersion']==2 and a['sweepId']==b['sweepId']==EXPECTED_SWEEP and a['configSignature']==b['configSignature'] and a['startedAt']==b['startedAt'],
 'same_target_hash':a['targetIdentitySha256']==b['targetIdentitySha256']==TARGET,
 'historical_checkpoint_counters_retained':all(isinstance(a['counters'].get(k),(int,float)) and a['counters'][k]>=v for k,v in b['counters'].items() if isinstance(v,(int,float))),
 'historical_lost_694_retained':a['counters'].get('totalLost',-1)>=694,
 'historical_failure_counts_retained':a['recoveredFailureCount']>=b['recoveredFailureCount'] and after['sourceStatus']['errorCount']>=before['sourceStatus']['errorCount'],
 'distinct_lower_bound_not_reset':a['distinctDiscoveredLowerBound']>=b['distinctDiscoveredLowerBound'],
 }
 cursor_advanced=(a['shardIndex'],a['page'])>(b['shardIndex'],b['page'])
 accepted_here=a['shardIndex']==b['shardIndex'] and a['targetAccepted'] and a['acceptedCurrentLeaf']>=400
 old_batch_drained=(cursor_advanced and a['pendingPageSha256']!=b['pendingPageSha256']) or (accepted_here and a['pendingUnresolvedCount']==0)
 checks.update({'accepted_399_to_400_or_cursor_advanced':accepted_here or cursor_advanced,'original_pending_batch_drained':old_batch_drained,'target_no_longer_unresolved':a['targetUnresolvedCount']==0})
 return {'verified':all(checks.values()),'checks':checks,'progressMode':'cursor_advanced' if cursor_advanced else 'accepted_in_original_leaf' if accepted_here else 'still_pending','targetIdentitySha256':TARGET,'sweepId':a['sweepId'],'before':{'acceptedCurrentLeaf':b['acceptedCurrentLeaf'],'cursor':[b['shardIndex'],b['page']],'pendingUnresolvedCount':b['pendingUnresolvedCount'],'counters':b['counters']},'after':{'acceptedCurrentLeaf':a['acceptedCurrentLeaf'],'cursor':[a['shardIndex'],a['page']],'pendingUnresolvedCount':a['pendingUnresolvedCount'],'counters':a['counters']},'limitation':'Verifies this original blocked batch and retained history only; it does not claim entire sweep or corpus completion.'}
def selftest():
 b=json.loads((ROOT/'t030-natural-baseline.json').read_text());a=copy.deepcopy(b);a['at']='2026-09-29T00:02:00Z';a['sourceStatus']['lastRunAt']='2026-09-29T00:01:00Z';v='00000000-0000-4000-8000-000000000030';d={'deployments':{'deployments':[{'created_on':'2026-09-29T00:00:00Z','versions':[{'version_id':v,'percentage':100}]}]}}
 a['checkpoint'].update(targetAccepted=True,targetUnresolvedCount=0,acceptedCurrentLeaf=400,pendingUnresolvedCount=0)
 cases=[]
 def check(name,x,expected):
  actual=evaluate(b,x,d,v)['verified'];assert actual==expected,name;cases.append({'case':name,'passed':True})
 check('exact accepted400 clears old pending batch',a,True)
 c=copy.deepcopy(a);c['checkpoint'].update(shardIndex=2,page=1,targetAccepted=False,acceptedCurrentLeaf=1,pendingPageSha256='next-batch',pendingUnresolvedCount=3);check('cursor advancement clears old batch despite new unrelated pending work',c,True)
 for name,mutate in [('still blocked',lambda x:x['checkpoint'].update(targetAccepted=False,targetUnresolvedCount=1,acceptedCurrentLeaf=399,pendingUnresolvedCount=1)),('lost history reset',lambda x:x['checkpoint']['counters'].update(totalLost=0)),('new sweep',lambda x:x['checkpoint'].update(sweepId='another')),('restart',lambda x:x['containers'][0].update(restartCount=1)),('run before release',lambda x:x['sourceStatus'].update(lastRunAt='2026-09-28T23:59:00Z')),('cursor without batch replacement',lambda x:x['checkpoint'].update(targetAccepted=False,acceptedCurrentLeaf=399,page=5,pendingUnresolvedCount=1))]:
  x=copy.deepcopy(a);mutate(x);check(name,x,False)
 assert not evaluate(b,a,d,'00000000-0000-4000-8000-000000000031')['verified'];cases.append({'case':'wrong deployed version fails','passed':True})
 return {'cases':cases,'passed':len(cases),'productionRequests':0}
def main():
 p=argparse.ArgumentParser();p.add_argument('--self-test',action='store_true');p.add_argument('--baseline',type=pathlib.Path,default=ROOT/'t030-natural-baseline.json');p.add_argument('--snapshot',type=pathlib.Path);p.add_argument('--deployment-receipt',type=pathlib.Path);p.add_argument('--worker-version');p.add_argument('--output',type=pathlib.Path)
 a=p.parse_args()
 if a.self_test:print(json.dumps(selftest(),indent=2));return
 if not all([a.snapshot,a.deployment_receipt,a.worker_version,a.output]) or not re.fullmatch(r'[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}',a.worker_version or ''):p.error('exact worker version, deployment receipt, snapshot and output are required')
 inputs={str(x):hashlib.sha256(x.read_bytes()).hexdigest() for x in [a.baseline,a.snapshot,a.deployment_receipt]}
 result=evaluate(json.loads(a.baseline.read_text()),json.loads(a.snapshot.read_text()),json.loads(a.deployment_receipt.read_text()),a.worker_version)
 result.update(at=datetime.datetime.now(datetime.timezone.utc).isoformat(),workerVersion=a.worker_version,inputSha256=inputs)
 a.output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2));sys.exit(0 if result['verified'] else 2)
if __name__=='__main__':main()
