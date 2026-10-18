// Pure supplement replay. The original successful native cycle is always replayed unchanged.
import assert from 'node:assert/strict';
import {isDeepStrictEqual} from 'node:util';
import {sha256,verifyReceipt,isQuiet,assertInitialState} from './product_native_evidence.mjs';
const HASH=/^[a-f0-9]{64}$/;
const TERMINAL=new Set(['completed','failed','interrupted','cancelled']);
const FIELDS=['runs','providerTurns','attempts','turnItems','nodes','subagents','runtimeRequests','messages','plans','checkpointScopes','checkpoints','contextHandoffs','contextTransfers'];
const exact=(x,keys,why)=>{assert.ok(x&&typeof x==='object'&&!Array.isArray(x),why);assert.deepEqual(Object.keys(x).sort(),[...keys].sort(),why);};
const one=(xs,why)=>{assert.equal(xs.length,1,why);return xs[0];};
const time=x=>{assert.equal(typeof x,'string');const n=Date.parse(x);assert.ok(Number.isFinite(n),'history-timestamp-required');return n;};
const omit=(x,keys)=>Object.fromEntries(Object.entries(x).filter(([k])=>!keys.includes(k)));
export const projectionReadPath=id=>'/api/orchestration/threads/'+encodeURIComponent(id);
export function sourceHistoryBindings(planBytes,nativeBytes){return {planSha256:sha256(planBytes),nativeSha256:sha256(nativeBytes)};}
function uniqueRows(xs,why){assert.ok(Array.isArray(xs),why);const ids=new Set();for(const x of xs){assert.equal(typeof x.id,'string',why);assert.ok(!ids.has(x.id),why);ids.add(x.id);}return ids;}
function terminalProjection(plan,p){
  assert.ok(p&&p.thread,'raw-projection-required');assert.equal(p.thread.projectId,plan.projectId,'foreign-history-project');assert.equal(p.thread.deletedAt,null,'deleted-history-thread');
  for(const field of FIELDS)uniqueRows(p[field]??[],'duplicate-history-'+field);
  assert.ok(isQuiet(p),'history-not-quiescent');
  for(const field of ['runs','providerTurns'])for(const row of p[field]??[])assert.ok(TERMINAL.has(row.status),'nonterminal-history-'+field);
  for(const s of p.providerSessions??[])assert.ok(['ready','stopped','error'].includes(s.status),'provider-session-not-idle');
  for(const msg of p.messages??[]){assert.equal(msg.threadId,p.thread.id,'message-thread-mismatch');assert.equal(msg.streaming,false,'streaming-history-message');assert.ok(['system','user','assistant'].includes(msg.role));assert.equal(typeof msg.text,'string');time(msg.createdAt);}
  for(const row of p.runs??[])assert.equal(row.threadId,p.thread.id,'run-thread-mismatch');
}
function stableThread(old,current){for(const k of ['id','projectId','createdAt','createdBy','creationSource','lineage','forkedFrom','deletedAt'])if(Object.hasOwn(old,k))assert.deepEqual(current[k],old[k],'historical-thread-identity-changed-'+k);}
// The server reuses the named root checkpoint ID (CheckpointService.makeRootScope;
// ProjectionStore checkpoint-scope.created UPSERT). Only these four values retarget.
function rootScopeTransition(plan,oldParent,parent,old,current){
  assert.deepEqual(omit(current,['runId','nodeId','createdAt','providerThreadId']),omit(old,['runId','nodeId','createdAt','providerThreadId']),'root-scope-stable-identity-changed');
  assert.equal(old.id,'checkpoint-scope:thread:'+encodeURIComponent(plan.coordinatorId)+':name:root');assert.equal(old.threadId,plan.coordinatorId);assert.equal(old.kind,'root_run');assert.equal(old.cwd,plan.workspaceRoot);assert.equal(old.parentScopeId,null);assert.equal(old.ordinalWithinParent,0);assert.equal(old.advancesAppRunCount,true);
  const before=one(oldParent.runs.filter(r=>r.id===old.runId),'old-scope-run-missing'),after=one(parent.runs.filter(r=>r.id===current.runId),'new-scope-run-missing');
  assert.ok(!oldParent.runs.some(r=>r.id===after.id),'scope-retarget-not-new-run');assert.ok(Number.isInteger(after.ordinal)&&after.ordinal>before.ordinal,'scope-ordinal-not-advanced');
  assert.equal(old.nodeId,before.rootNodeId);assert.equal(old.providerThreadId,before.providerThreadId);assert.equal(current.nodeId,after.rootNodeId);assert.equal(current.providerThreadId,after.providerThreadId);assert.equal(current.createdAt,after.requestedAt);assert.ok(time(current.createdAt)>=time(old.createdAt));
  const node=one(parent.nodes.filter(n=>n.id===current.nodeId),'scope-root-node-missing');assert.equal(node.threadId,plan.coordinatorId);assert.equal(node.runId,after.id);assert.equal(node.kind,'root_turn');assert.equal(node.parentNodeId,null);assert.equal(node.rootNodeId,node.id);assert.equal(node.checkpointScopeId,current.id);assert.equal(node.providerThreadId,current.providerThreadId);
  const provider=one(parent.providerThreads.filter(t=>t.id===current.providerThreadId),'scope-provider-thread-missing');assert.equal(provider.appThreadId,plan.coordinatorId);assert.equal(provider.providerInstanceId,after.providerInstanceId);
}
function preservedProjection(plan,old,current,isParent){
  stableThread(old.thread,current.thread);
  for(const field of FIELDS)for(const row of old[field]??[]){const now=one((current[field]??[]).filter(x=>x.id===row.id),'historical-record-missing-or-duplicated');
    if(isParent&&field==='checkpointScopes'&&!isDeepStrictEqual(row,now))rootScopeTransition(plan,old,current,row,now);
    else assert.deepEqual(now,row,'historical-record-changed-'+field);
  }
}
function stableSnapshot(p){return {thread:omit(p.thread,['updatedAt','lastVisitedAt']),...Object.fromEntries(FIELDS.map(k=>[k,p[k]??[]]))};}
export function exportedHistoryThread(p,parentId){return {threadId:p.thread.id,title:p.thread.title,branch:p.thread.branch??null,worktreePath:p.thread.worktreePath??null,kind:p.thread.id===parentId?'coordinator':'worker',messages:(p.messages??[]).filter(m=>m.role==='user'||m.role==='assistant').map(m=>({id:m.id,role:m.role,text:m.text,createdAt:new Date(m.createdAt).toISOString()}))};}
function readProjection(read,plan,history){
  exact(read,['method','path','requestedAt','receivedAt','response'],'unknown-history-read');assert.equal(read.method,'GET');assert.ok(read.response&&read.response.projection,'raw-api-response-required');
  const p=read.response.projection;assert.equal(read.path,projectionReadPath(p.thread.id),'raw-read-path-mismatch');assert.ok(time(read.requestedAt)>=time(history.startedAt)&&time(read.receivedAt)>=time(read.requestedAt)&&time(read.receivedAt)<=time(history.finishedAt),'history-read-time-window');
  terminalProjection(plan,p);return p;
}
export function verifySourceHistory(plan,native,history,bindings,bundle=null){
  verifyReceipt(plan,native);assert.equal(native.status,'passed','original-successful-proof-required');assert.equal(plan.mode,'source');assert.equal(plan.host,'m4');assert.equal(native.temporarySessionRevoked,true);
  exact(bindings,['planSha256','nativeSha256'],'original-hash-bindings-required');for(const x of Object.values(bindings))assert.match(x,HASH);
  exact(history,['version','kind','host','source','startedAt','finishedAt','configRead','reads','files','historicalOnlyThreadIds','temporarySessionRevoked'],'unknown-source-history');
  assert.equal(history.version,1);assert.equal(history.kind,'source-terminal-history-supplement');assert.equal(history.host,'m4');assert.equal(history.temporarySessionRevoked,true,'history-session-not-revoked');
  assert.deepEqual(history.source,{...bindings,environmentId:plan.environmentId,projectId:plan.projectId,coordinatorId:plan.coordinatorId},'source-history-binding-mismatch');
  assert.ok(time(history.startedAt)>=time(native.startedAt)&&time(history.finishedAt)>=time(history.startedAt),'history-predates-original-proof');
  exact(history.configRead,['method','path','requestedAt','receivedAt','response'],'unknown-runtime-read');assert.equal(history.configRead.method,'RPC');assert.equal(history.configRead.path,'server.getConfig');assert.equal(history.configRead.response?.environment?.environmentId,plan.environmentId,'history-wrong-environment');
  assert.ok(time(history.configRead.requestedAt)>=time(history.startedAt)&&time(history.configRead.receivedAt)>=time(history.configRead.requestedAt)&&time(history.configRead.receivedAt)<=time(history.finishedAt));
  exact(history.files,['before','after'],'unknown-file-readbacks');for(const state of Object.values(history.files)){assertInitialState(plan,state);assert.deepEqual(state,native.baseline,'source-checkpoint-or-fixture-changed');}
  exact(history.reads,['before','after'],'unknown-history-readbacks');assert.ok(Array.isArray(history.reads.before)&&history.reads.before.length>=2&&history.reads.before.length<=100,'bounded-source-thread-inventory-required');assert.equal(history.reads.after.length,history.reads.before.length);
  const before=history.reads.before.map(r=>readProjection(r,plan,history)),after=history.reads.after.map(r=>readProjection(r,plan,history));
  for(const rows of [before,after])assert.equal(new Set(rows.map(p=>p.thread.id)).size,rows.length,'duplicate-source-thread');
  assert.ok(Math.max(...history.reads.before.map(r=>time(r.receivedAt)))<=Math.min(...history.reads.after.map(r=>time(r.requestedAt))),'readbacks-not-sequential');
  const parent=one(after.filter(p=>p.thread.id===plan.coordinatorId),'current-parent-missing');
  assert.deepEqual(parent.thread.lineage,{parentThreadId:null,relationshipToParent:null,rootThreadId:plan.coordinatorId},'parent-reparented');assert.equal(parent.thread.forkedFrom,null);
  preservedProjection(plan,native.rawParent,parent,true);
  const tasks=parent.subagents??[];assert.ok(tasks.length>=1&&tasks.length<100);const known=new Set([plan.coordinatorId]);
  for(const task of tasks){assert.equal(task.origin,'app_owned','foreign-task-origin');assert.equal(task.threadId,plan.coordinatorId,'foreign-parent-task');assert.ok(TERMINAL.has(task.status),'nonterminal-app-child');assert.equal(typeof task.childThreadId,'string');assert.ok(!known.has(task.childThreadId),'duplicate-or-parent-as-child');known.add(task.childThreadId);
    const child=one(after.filter(p=>p.thread.id===task.childThreadId),'owned-child-readback-missing');assert.deepEqual(child.thread.lineage,{parentThreadId:plan.coordinatorId,relationshipToParent:'subagent',rootThreadId:plan.coordinatorId},'child-reparented');assert.deepEqual(child.thread.forkedFrom,{type:'node',nodeId:task.id},'child-delegation-origin-mismatch');assert.equal((child.subagents??[]).length,0,'unread-descendant-work');
  }
  assert.equal(after.length,known.size,'foreign-source-thread');
  for(const p of before){assert.ok(known.has(p.thread.id),'foreign-source-thread');const now=one(after.filter(x=>x.thread.id===p.thread.id),'history-readback-missing');assert.deepEqual(stableSnapshot(now),stableSnapshot(p),'source-history-changed-during-collection');}
  const oldChildIds=new Set(native.rawParent.subagents.filter(s=>s.origin==='app_owned').map(s=>s.childThreadId));
  const additions=after.filter(p=>p.thread.id!==plan.coordinatorId&&!oldChildIds.has(p.thread.id)).map(p=>p.thread.id).sort();
  assert.ok(additions.length>0,'supplement-needs-added-terminal-history');assert.deepEqual(history.historicalOnlyThreadIds,additions,'historical-only-inventory-mismatch');assert.ok(!additions.includes(native.outcome.workerThreadId),'successful-cycle-replaced');
  const worker=one(after.filter(p=>p.thread.id===native.outcome.workerThreadId),'original-successful-worker-missing');preservedProjection(plan,native.worker,worker,false);
  for(const p of after){for(const m of p.messages??[])assert.ok(time(m.createdAt)<=time(history.startedAt),'message-postdates-history-start');for(const r of p.runs??[])if(r.completedAt)assert.ok(time(r.completedAt)<=time(history.startedAt),'history-was-active-at-collection-start');}
  const threads=after.map(p=>exportedHistoryThread(p,plan.coordinatorId));
  if(bundle){assert.equal(bundle.sourceEnvironmentId,plan.environmentId);assert.equal(bundle.sourceProjectId,plan.projectId);assert.equal(bundle.sourceThreadId,plan.coordinatorId);assert.ok(time(bundle.createdAt)>=time(history.finishedAt),'bundle-predates-terminal-history');assert.equal(bundle.context.threads.length,threads.length,'supplement-bundle-inventory-mismatch');
    for(const expected of threads)assert.deepEqual(one(bundle.context.threads.filter(t=>t.threadId===expected.threadId),'supplement-bundle-thread-missing'),expected,'supplement-bundle-history-mismatch');
  }
  return {threadIds:[...known],historicalOnlyThreadIds:additions,threads,originalSuccessfulWorkerId:native.outcome.workerThreadId};
}
