import { describe,it,expect } from '/Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specweave-studio/node_modules/vite-plus/dist/test/index.js';
import {readFileSync,writeFileSync} from 'node:fs';
import {isThreadWorking,createInboxReturnTracker,sortInboxThreadsByReturn} from '/Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specweave-studio/packages/client-runtime/src/state/threadInbox.ts';
import {derivePendingBackgroundWork,backgroundWorkHoldsCompletion} from '/Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specweave-studio/packages/shared/src/orchestrationV2PendingBackgroundWork.ts';
import {threadRunHealth,threadAwaitingPerson} from '/Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specweave-studio/packages/client-runtime/src/state/models.ts';
import {projectThreadGroup} from '/Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specweave-studio/apps/web/src/studio/projectWorkspaceModel.ts';
import {filterSidebarV2VisibleThreads,hasUnseenCompletion} from '/Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specweave-studio/apps/web/src/components/Sidebar.logic.ts';
import {reportBlocker} from '/Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specweave-studio/packages/shared/src/reportDocument.ts';
const dir=import.meta.dirname;
const rows=(f:string)=>readFileSync(`${dir}/${f}.jsonl`,'utf8').trim().split('\n').filter(Boolean).map(x=>JSON.parse(x));
const base=(id='a',status='running')=>({id,environmentId:'m4',createdAt:'2026-10-01T00:00:00Z',updatedAt:'2026-10-23T00:00:00Z',unsettledAt:null,latestRun:{runId:'r',status,requestedAt:'2026-10-01T00:00:00Z',completedAt:null},runtime:{status,activeRunId:'r'},hasPendingApprovals:false,hasPendingUserInput:false,hasActionableProposedPlan:false,interactionMode:'default',reportedBlocker:null,activeWork:null,archivedAt:null,settledOverride:null,lineage:{relationshipToParent:null}} as any);
const cases:any[]=[];
function check(name:string,fn:()=>unknown){it(name,()=>{const result=fn();cases.push({name,result});writeFileSync(`${dir}/checks.json`,JSON.stringify(cases,null,2));});}
describe('Working audit production helpers',()=>{
check('active phases fold; approvals and structured input escape',()=>{for(const s of ['preparing','queued','starting','running','waiting','idle'])expect(isThreadWorking(base('a',s))).toBe(true);for(const flag of ['hasPendingApprovals','hasPendingUserInput'])expect(isThreadWorking({...base(),[flag]:true})).toBe(false);for(const s of ['completed','failed','interrupted','cancelled','rolled_back'])expect(isThreadWorking(base('a',s))).toBe(false);return 'pass';});
check('reported blocker plus monitor stays folded while project pane needs user',()=>{const t={...base('b','idle'),reportedBlocker:'Choose A or B'};expect(isThreadWorking(t)).toBe(true);expect(projectThreadGroup(t)).toBe('Waiting on you');return {inbox:'Working',project:'Waiting on you'};});
check('stalled active run stays folded',()=>{const t=base();expect(threadRunHealth(t,Date.parse('2026-10-23T03:00:00Z'))?.state).toBe('stalled');expect(isThreadWorking(t)).toBe(true);return 'stalled but Working';});
check('sign-in request without input flags stays folded',()=>{const t={...base(),source:{pendingRuntimeRequest:{kind:'auth_refresh'}}};expect(threadAwaitingPerson(t)?.kind).toBe('sign-in');expect(isThreadWorking(t)).toBe(true);return 'auth_refresh is not checked by folding predicate';});
check('settled plan prompt escapes but active plan run folds',()=>{const t={...base('p','idle'),interactionMode:'plan',hasActionableProposedPlan:true,latestRun:{...base().latestRun,status:'completed'},runtime:{status:'idle',activeRunId:null}};expect(isThreadWorking(t)).toBe(false);expect(isThreadWorking({...t,latestRun:{...t.latestRun,status:'running'}})).toBe(true);return 'pass';});
check('monitor has Waiting runtime but Idle project group',()=>{expect(projectThreadGroup(base('m','idle'))).toBe('Idle');expect(isThreadWorking(base('m','idle'))).toBe(true);return {inbox:'Working',project:'Idle'};});
check('subagents excluded from inbox irrespective of beta',()=>{const t={...base(),lineage:{relationshipToParent:'subagent'}};expect(filterSidebarV2VisibleThreads([t],null)).toHaveLength(0);return 'hidden';});
check('observed return jumps to top; fresh client loses event time',()=>{const old=base('old');const newer={...base('new','completed'),createdAt:'2026-10-22T00:00:00Z'};const returned={...old,runtime:null};const tracker=createInboxReturnTracker();tracker.observe([old,newer]);tracker.observe([returned,newer]);expect(sortInboxThreadsByReturn([returned,newer],tracker.returnedAt)[0].id).toBe('old');const fresh=createInboxReturnTracker();fresh.observe([returned,newer]);expect(sortInboxThreadsByReturn([returned,newer],fresh.returnedAt)[0].id).toBe('new');tracker.observe(null);expect(tracker.returnedAt(returned)).toBeUndefined();return 'observed old first; fresh/off reset new first';});
check('unvisited completion is read; unread does not govern folding',()=>{const t={...base('a','idle'),latestRun:{...base().latestRun,completedAt:'2026-10-23T00:00:00Z'},lastVisitedAt:undefined};expect(hasUnseenCompletion(t)).toBe(false);expect(hasUnseenCompletion({...t,lastVisitedAt:'2026-10-22T00:00:00Z'})).toBe(true);expect(isThreadWorking(t)).toBe(true);return 'pass';});
check('commands do not hold completion; monitor and subagent do',()=>{expect(backgroundWorkHoldsCompletion([{kind:'command'}])).toBe(false);for(const kind of ['monitor','subagent','workflow','background_task'])expect(backgroundWorkHoldsCompletion([{kind} as any])).toBe(true);return 'pass';});
check('live rows reconstructed with production background predicate',()=>{
const threads=rows('live-threads').map(x=>JSON.parse(x.record).thread);
const runs=rows('live-runs').map(x=>JSON.parse(x.payload_json));
const providers=rows('live-provider-threads').map(x=>JSON.parse(x.payload_json));
const items=rows('live-pending-items').map(x=>JSON.parse(x.payload_json));
const messages=rows('live-last-messages').map(x=>JSON.parse(x.payload_json));
const requests=rows('live-requests');
const plans=rows('live-plans');
const out=threads.filter(t=>runs.some(r=>r.threadId===t.id)).map(t=>{
const run=runs.find(r=>r.threadId===t.id)!;
const tasks=derivePendingBackgroundWork({latestRun:run,providerThreads:providers.filter(x=>x.appThreadId===t.id),turnItems:items.filter(x=>x.threadId===t.id),activeProviderThreadId:t.activeProviderThreadId,runs:[run],pullRequests:t.pullRequests});
const req=requests.find(x=>x.thread_id===t.id);
const ms=messages.filter(x=>x.threadId===t.id);const assistant=ms.find(x=>x.role==='assistant');const user=ms.find(x=>x.role==='user');
const blocker=assistant && (!user || Date.parse(user.updatedAt)<Date.parse(assistant.updatedAt))?reportBlocker(assistant.text):null;
const runtimeStatus=backgroundWorkHoldsCompletion(tasks)&&run.status!=='failed'?'idle':run.status;
const shell={...base(t.id),...t,runtime:{status:runtimeStatus,activeRunId:['preparing','starting','running'].includes(run.status)?run.id:null},latestRun:{runId:run.id,status:run.status,requestedAt:run.requestedAt,completedAt:run.completedAt},hasPendingApprovals:['command','file-read','file-change','permission','mcp-elicitation'].includes(req?.kind),hasPendingUserInput:req?.kind==='user_input',hasActionableProposedPlan:plans.some(x=>x.thread_id===t.id),reportedBlocker:blocker};
return {id:t.id,title:t.title,runStatus:run.status,runtimeStatus,settled:t.settledOverride,subagent:t.lineage?.relationshipToParent==='subagent',tasks,blocker,workingPredicate:isThreadWorking(shell),projectGroup:projectThreadGroup(shell),createdAt:t.createdAt,completedAt:run.completedAt,updatedAt:t.updatedAt};
});writeFileSync(`${dir}/live-classification.json`,JSON.stringify({scope:'M4 sequential read-only snapshots; production helpers over reconstructed shell inputs, not captured installed UI. Runless native threads omitted.',rows:out},null,2));expect(out.length).toBeGreaterThan(200);return {rows:out.length,watched:out.filter(x=>x.tasks.some(t=>t.kind==='monitor')).map(x=>({title:x.title,status:x.runtimeStatus,projectGroup:x.projectGroup})),blockedMonitors:out.filter(x=>x.blocker&&x.workingPredicate).map(x=>x.title)};
});
});
