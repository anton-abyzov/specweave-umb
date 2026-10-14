// Pure product-native receipt validation. No network, filesystem, process or private imports.
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {basename, dirname, isAbsolute, relative, resolve} from 'node:path';
import {isDeepStrictEqual} from 'node:util';

export const sha256 = value => createHash('sha256').update(value).digest('hex');
const HEX40 = /^[a-f0-9]{40}$/;
const HEX64 = /^[a-f0-9]{64}$/;
const UUID = /^[a-f0-9]{8}-[a-f0-9]{4}-[1-8][a-f0-9]{3}-[89ab][a-f0-9]{3}-[a-f0-9]{12}$/;
const PENDING = new Set(['idle', 'pending', 'queued', 'preparing', 'starting', 'running', 'waiting']);
const SETTLED = new Set(['acknowledged', 'delivered', 'disposed']);
const ARRAY_FIELDS = ['runs','providerTurns','attempts','turnItems','nodes','subagents','runtimeRequests','messages','plans','checkpointScopes','checkpoints','contextHandoffs','contextTransfers'];
const SHARED_GIT_KINDS=new Set(['branch','add','commit','diff','git-final-head']);
const GIT = '/Library/Developer/CommandLineTools/usr/bin/git';
const q = s => "'" + s.replaceAll("'", "'\\''") + "'";
const requireObject = x => assert.ok(x && typeof x === 'object' && !Array.isArray(x), 'object-required');
const exactKeys = (x, allowed) => { requireObject(x); assert.ok(Object.keys(x).every(k => allowed.includes(k)), 'unexpected-input-key'); };
const one = (xs, why) => { assert.equal(xs.length, 1, why); return xs[0]; };
const includesAll = (text, values, why) => { assert.equal(typeof text, 'string', why); for (const v of values) assert.ok(text.includes(v), why); };
const abs = p => { assert.equal(typeof p, 'string'); assert.ok(isAbsolute(p) && resolve(p) === p && !/[\r\n\0]/.test(p), 'canonical-absolute-path-required'); return p; };
const below = (root, path) => { const r = relative(root, path); assert.ok(r && !r.startsWith('../') && r !== '..' && !isAbsolute(r), 'path-outside-owned-root'); return r; };

export function validatePlan(p) {
  requireObject(p); assert.ok(!Object.hasOwn(p,'_graph'),'reserved-internal-plan-key'); assert.equal(p.version, 1); assert.ok(['m4','m1','m3'].includes(p.host));
  assert.ok(['source','destination'].includes(p.mode));
  for (const k of ['environmentId','projectId','coordinatorId']) assert.ok(typeof p[k] === 'string' && p[k].length > 0);
  assert.equal(p.coordinatorId, 'project-coordinator:' + p.projectId);
  abs(p.workspaceRoot); abs(p.nestedRoot); below(p.workspaceRoot, p.nestedRoot);
  for (const k of ['root','nested']) assert.match(p.originalShas[k], HEX40);
  requireObject(p.paths); requireObject(p.frozen);
  for (const k of ['implementation','test','readme','continuation']) abs(p.paths[k]);
  below(p.nestedRoot, p.paths.implementation); below(p.nestedRoot, p.paths.test); below(p.nestedRoot, p.paths.readme);
  below(p.workspaceRoot, p.paths.continuation);
  assert.ok(p.paths.implementation.endsWith('/case.mjs') && p.paths.test.endsWith('/case.check.mjs') && p.paths.readme.endsWith('/README.md'));
  assert.equal(new Set(Object.values(p.paths)).size, Object.values(p.paths).length, 'aliased-fixture-paths');
  for (const k of ['implementation','test','readme','continuation']) assert.match(p.frozen[k], HEX64);
  abs(p.nodePath); assert.ok(p.nodePath.endsWith('/node'), 'node22-path-required');
  assert.ok(Number.isInteger(p.expectedTestCount) && p.expectedTestCount > 0 && p.expectedTestCount <= 100);
  assert.ok(Array.isArray(p.contextRequired) && p.contextRequired.length >= 2 && p.contextRequired.every(s => typeof s === 'string' && s.length >= 5 && s.length < 2000), 'validation-context-required');
  assert.deepEqual(p.profile, {coordinator:{instanceId:'codex',model:'gpt-6.1-sol'},worker:{instanceId:'codex',model:'gpt-6.1-sol'}});
  if (p.mode === 'destination') {
    assert.match(p.operationId, UUID); assert.equal(p.projectId, 'machine-handoff:' + p.operationId);
    abs(p.paths.context); assert.match(p.frozen.context, HEX64); abs(p.receiveReceiptPath);
    assert.match(p.branch, /^codex\/0907-product-[a-z0-9-]+-(?:m1|m3)$/);
    assert.match(p.commitMessage, /^0907: Complete [a-z0-9-]+ handoff diagnostic$/);
  } else { abs(p.priorProjectionPath); assert.ok(typeof p.startMessageId === 'string' && p.startMessageId.length > 0, 'source-start-message-binding-required'); }
  if (p.timeoutMs !== undefined) assert.ok(Number.isInteger(p.timeoutMs) && p.timeoutMs >= 1000 && p.timeoutMs <= 900000);
  return p;
}

// Deliberately small shell grammar: literal words, quoting, and at most one cd &&.
// No substitutions, redirections, pipes, comments, globs, variables or command lists.
export function shellWords(text) {
  assert.ok(typeof text === 'string' && text.length > 0 && text.length < 20000 && !/[\r\n\0`$]/.test(text), 'unsafe-shell-syntax');
  const result = []; let word = '', active = false, quote = null;
  for (let i = 0; i < text.length; i++) {
    const c = text[i];
    if (quote) { if (c === quote) quote = null; else if (c === '\\' && quote === '"') { assert.ok(i + 1 < text.length); word += text[++i]; } else word += c; active = true; continue; }
    if (c === "'" || c === '"') { quote = c; active = true; continue; }
    if (/\s/.test(c)) { if (active) { result.push(word); word = ''; active = false; } continue; }
    if (c === '\\') { assert.ok(i + 1 < text.length); word += text[++i]; active = true; continue; }
    if (c === '&' && text[i + 1] === '&') { if (active) { result.push(word); word = ''; active = false; } result.push('&&'); i++; continue; }
    assert.ok(!/[;&|<>()[\]{}*?!#~]/.test(c), 'unsafe-shell-operator'); word += c; active = true;
  }
  assert.equal(quote, null, 'unterminated-shell-quote'); if (active) result.push(word);
  assert.ok(result.length > 0, 'empty-command'); return result;
}
export function commandWords(input) {
  let words = shellWords(input.trim());
  if (['/bin/zsh','/bin/bash'].includes(words[0])) { assert.equal(words.length, 3, 'unexpected-shell-wrapper'); assert.equal(words[1], '-lc'); words = shellWords(words[2]); }
  assert.ok(!words.includes('/bin/zsh') && !words.includes('/bin/bash'), 'nested-shell-wrapper'); return words;
}
export function buildCommandPolicy(p) {
  const entries = [];
  const add = (role, kind, argv, required = false) => entries.push({role,kind,argv,required,command:argv.map(x => x === '&&' ? x : q(x)).join(' ')});
  for (const [rootKey,root] of [['root',p.workspaceRoot],['nested',p.nestedRoot]]) {
    for (const [kind,args] of [['head',['rev-parse','--show-toplevel','HEAD']], ['branch',['branch','--show-current']], ['origin',['remote','get-url','origin']], ['status',['status','--porcelain=v1','--untracked-files=all']]])
      add('worker','git-' + rootKey + '-' + kind,[GIT,'--no-optional-locks','-C',root,...args],kind === 'head');
  }
  for (const key of ['implementation','test','readme','continuation', ...(p.mode === 'destination' ? ['context'] : [])]) {
    add('worker','read-' + key,['/bin/cat',p.paths[key]], true);
    if (key === 'context'||p._graph) add('coordinator','read-' + key,['/bin/cat',p.paths[key]], false);
  }
  add('worker','node-version',[p.nodePath,'--version']);
  add('worker','test',['cd',p.nestedRoot,'&&',p.nodePath,'--test',p.paths.test],true);
  if (p.mode === 'destination') {
    const rel = relative(p.nestedRoot,p.paths.implementation);
    add('worker','diff',[GIT,'--no-optional-locks','-C',p.nestedRoot,'diff','--',rel]);
    add('worker','diff',[GIT,'--no-optional-locks','-C',p.nestedRoot,'diff','--cached','--',rel]);
    add('worker','branch',[GIT,'-c','core.hooksPath=/dev/null','-C',p.nestedRoot,'switch','-c',p.branch],true);
    add('worker','add',[GIT,'-C',p.nestedRoot,'add','--',rel],true);
    add('worker','commit',[GIT,'-c','core.hooksPath=/dev/null','-c','commit.gpgSign=false','-C',p.nestedRoot,'commit','-m',p.commitMessage,'--',rel],true);
    add('worker','git-final-head',[GIT,'--no-optional-locks','-C',p.nestedRoot,'rev-parse','HEAD'],true);
  }
  if(p.mode==='destination')for(const entry of entries.filter(e=>SHARED_GIT_KINDS.has(e.kind)))entries.push({...entry,role:'coordinator',required:false});
  return entries;
}
export function classifyCommand(plan, input, role) {
  let words = commandWords(input), cwd = plan.workspaceRoot;
  if (words[0] === 'cd') {
    assert.equal(words[2],'&&','only-cd-and-one-command'); cwd = resolve(cwd,words[1]);
    assert.ok([plan.workspaceRoot,plan.nestedRoot].includes(cwd),'command-cwd-outside-scope'); words = words.slice(3);
  }
  assert.ok(!words.includes('&&'),'multiple-shell-commands-refused');
  if (['cat','/bin/cat','/usr/bin/cat'].includes(words[0])) {
    assert.equal(words.length,2); words = ['/bin/cat',resolve(cwd,words[1])];
  } else if (words[0] === plan.nodePath && words.length===2 && words[1]==='--version') {
    words=[plan.nodePath,'--version'];
  } else if (words[0] === plan.nodePath) {
    const args=[];let reporters=0;for(let i=1;i<words.length;i++) {
      if(words[i]==='--test-reporter=tap'){assert.ok(args.length<2,'reporter-must-precede-test-path');reporters++;continue;}
      if(words[i]==='--test-reporter'){assert.ok(args.length<2,'reporter-must-precede-test-path');assert.equal(words[++i],'tap','tap-reporter-required');reporters++;continue;}
      args.push(words[i]);
    }
    assert.ok(reporters<=1,'duplicate-test-reporter');assert.equal(args.length,2);assert.equal(args[0],'--test');
    words = ['cd',plan.nestedRoot,'&&',plan.nodePath,'--test',resolve(cwd,args[1])];
  } else if (['git','/usr/bin/git',GIT].includes(words[0])) {
    let at = 1, root = cwd, optional = false; const configs = [];
    while (at < words.length) {
      if (words[at] === '--no-optional-locks') { assert.ok(!optional); optional = true; at++; }
      else if (words[at] === '-C') { assert.ok(words[at + 1]); root = resolve(root,words[at + 1]); at += 2; }
      else if (words[at] === '-c') { assert.ok(words[at + 1]); configs.push(words[at + 1]); at += 2; }
      else break;
    }
    assert.ok([plan.workspaceRoot,plan.nestedRoot].includes(root),'git-root-outside-scope');
    const args = words.slice(at);
    if(args[0]==='checkout'&&args[1]==='-b'){assert.equal(args.length,3,'exact-checkout-branch-required');args.splice(0,2,'switch','-c');}
    const write = ['switch','add','commit'].includes(args[0]);
    const expectedConfigs = args[0] === 'switch' ? ['core.hooksPath=/dev/null'] : args[0] === 'commit' ? ['core.hooksPath=/dev/null','commit.gpgSign=false'] : [];
    assert.deepEqual(configs,expectedConfigs,'unexpected-git-config-override');
    const separator = args.indexOf('--');
    if (separator >= 0) {
      assert.equal(args.length,separator + 2,'one-git-path-required');
      args[separator + 1] = relative(root,resolve(root,args[separator + 1]));
    }
    words = [GIT,...(!write ? ['--no-optional-locks'] : []),...configs.flatMap(c => ['-c',c]),'-C',root,...args];
  }
  return one(buildCommandPolicy(plan).filter(e => e.role === role && JSON.stringify(e.argv) === JSON.stringify(words)), 'command-not-allowlisted');
}

export function quiescence(p) {
  return {
    threadId:p.thread.id,
    runs:(p.runs ?? []).filter(x => PENDING.has(x.status)).map(x => x.id),
    turns:(p.providerTurns ?? []).filter(x => PENDING.has(x.status)).map(x => x.id),
    requests:(p.runtimeRequests ?? []).filter(x => x.status === 'pending').map(x => x.id),
    // Resolved requests can retain a historical waiting approval display item.
    // runtimeRequests is authoritative for pending approval, not that display.
    work:(p.turnItems ?? []).filter(x => ['command_execution','dynamic_tool','subagent','file_change'].includes(x.type) && PENDING.has(x.status)).map(x => x.id),
    tasks:(p.subagents ?? []).filter(x => PENDING.has(x.status)).map(x => x.id),
    deliveries:(p.subagents ?? []).filter(x => x.origin === 'app_owned' && !SETTLED.has(x.completionDelivery?.state)).map(x => x.id),
  };
}
export const isQuiet = p => Object.entries(quiescence(p)).every(([k,v]) => k === 'threadId' || v.length === 0);
function assertRootScopeRetarget(p,prior,old,current,plan) {
  const stable = x => Object.fromEntries(Object.entries(x).filter(([k]) => !['runId','nodeId','createdAt'].includes(k)));
  assert.ok(current,'historical-root-scope-missing'); assert.deepEqual(stable(current),stable(old),'historical-root-scope-identity-changed');
  assert.equal(old.id,'checkpoint-scope:thread:'+encodeURIComponent(plan.coordinatorId)+':name:root');
  assert.equal(old.threadId,plan.coordinatorId); assert.equal(old.kind,'root_run'); assert.equal(old.cwd,plan.workspaceRoot);
  assert.equal(old.parentScopeId,null); assert.equal(old.ordinalWithinParent,0); assert.equal(old.advancesAppRunCount,true);
  const before=one(prior.runs.filter(r=>r.id===old.runId),'historical-scope-run-missing');
  const after=one(p.runs.filter(r=>r.id===current.runId),'new-scope-run-missing');
  assert.ok(!prior.runs.some(r=>r.id===after.id),'scope-retargeted-to-historical-run');
  assert.equal(old.nodeId,before.rootNodeId); assert.equal(current.nodeId,after.rootNodeId);
  assert.equal(after.threadId,plan.coordinatorId); assert.equal(after.providerThreadId,old.providerThreadId);
  assert.ok(Number.isInteger(after.ordinal)&&after.ordinal>before.ordinal,'scope-run-ordinal-not-advanced');
  assert.equal(current.createdAt,after.requestedAt); assert.ok(Date.parse(current.createdAt)>=Date.parse(old.createdAt),'scope-created-at-invalid');
  const node=one(p.nodes.filter(n=>n.id===current.nodeId),'new-scope-root-node-missing');
  assert.equal(node.threadId,plan.coordinatorId); assert.equal(node.runId,after.id); assert.equal(node.kind,'root_turn');
  assert.equal(node.parentNodeId,null); assert.equal(node.rootNodeId,node.id); assert.equal(node.checkpointScopeId,current.id);
  assert.equal(node.providerThreadId,current.providerThreadId);
}
export function scopeProjection(p, prior, plan) {
  assert.equal(p.thread.id,plan.coordinatorId); assert.equal(p.thread.projectId,plan.projectId);
  if (!prior) return p;
  assert.equal(prior.thread.id,p.thread.id); assert.ok(isQuiet(prior),'historical-projection-was-active');
  const scoped = structuredClone(p),retargetedScopes=new Set();
  for (const field of ARRAY_FIELDS) {
    for (const old of prior[field] ?? []) {
      const current=one((p[field] ?? []).filter(x=>x.id===old.id),'historical-record-missing-or-duplicated');
      if(field==='checkpointScopes' && current && !isDeepStrictEqual(current,old)) {
        assertRootScopeRetarget(p,prior,old,current,plan); retargetedScopes.add(old.id);
      } else assert.deepEqual(current,old,'historical-record-changed');
    }
    const oldIds = new Set((prior[field] ?? []).map(x => x.id)); scoped[field] = (p[field] ?? []).filter(x => !oldIds.has(x.id)||(field==='checkpointScopes'&&retargetedScopes.has(x.id)));
  }
  if(retargetedScopes.size)assertParentOwnership(plan,scoped);
  return scoped;
}
export function toolOperation(item) {
  for (const prefix of ['studio-code.','mcp__studio_code__','mcp__studio-code__']) if (item.toolName?.startsWith(prefix)) return item.toolName.slice(prefix.length);
  return null;
}
export function assertAutomaticWake(parent, task, runId) {
  const run = one(parent.runs.filter(x => x.id === runId),'wake-run-missing');
  const msg = one(parent.messages.filter(x => x.id === run.userMessageId && x.runId === run.id),'wake-message-missing');
  assert.notEqual(run.id,task.runId); assert.equal(msg.createdBy,'agent'); assert.equal(msg.creationSource,'server');
  assert.equal(msg.delegatedCompletion?.parentRunId,task.runId); assert.deepEqual(msg.delegatedCompletion?.taskIds,[task.id]);
  assert.ok(['claimed','delivered','acknowledged'].includes(task.completionDelivery?.state),'completion-delivery-not-claimed');
  return {run,msg};
}
export function assertParentOwnership(plan,parent) {
  const firstRuns = parent.runs.filter(r => !(parent.messages ?? []).find(m => m.id === r.userMessageId)?.delegatedCompletion);
  assert.ok(firstRuns.length <= 1,'unrelated-new-coordinator-run');
  if (!firstRuns.length) { assert.equal(parent.runs.length,0); assert.equal(parent.subagents.length,0); return null; }
  const first = firstRuns[0], msg = one(parent.messages.filter(m => m.id === first.userMessageId),'start-message-required');
  if (plan.mode === 'source') assert.equal(msg.id,plan.startMessageId,'source-start-message-mismatch');
  else includesAll(msg.text,[`Continue handoff ${plan.operationId}.`,plan.paths.context,plan.workspaceRoot],'product-start-context-mismatch');
  if(plan._graph){assertGraphOwnership(plan,parent);return first;}
  assert.ok(parent.subagents.length <= 1,'extra-child-before-ownership');
  for (const child of parent.subagents) { assert.equal(child.origin,'app_owned'); assert.equal(child.runId,first.id,'child-not-owned-by-start'); }
  for (const run of parent.runs.filter(r => r.id !== first.id)) assertAutomaticWake(parent,one(parent.subagents,'wake-needs-owned-child'),run.id);
  return first;
}
export function assertMcp(plan, parent, item, worker = null) {
  const op = toolOperation(item), x = item.input; requireObject(x);
  assert.ok(['orchestrator_capabilities','studio_thread_list','delegate_task','task_status','studio_thread_read'].includes(op),'unexpected-mcp-tool');
  const tools = parent.turnItems.filter(i => i.type === 'dynamic_tool'&&(!plan._graph||i.runId===item.runId));
  assert.ok(tools.filter(i => toolOperation(i) === op).length <= 1,'duplicate-mcp-operation');
  if (op === 'orchestrator_capabilities') { exactKeys(x,[]); return; }
  if (op === 'studio_thread_list') {
    // a26cf OrchestratorMcpService resolves omission to this calling thread's project.
    // No machine or pagination/filter overrides: one bounded local discovery only.
    exactKeys(x,['projectId','includeSubagents','limit']);
    assert.equal(parent.thread.id,plan.coordinatorId,'discovery-caller-mismatch');assert.equal(parent.thread.projectId,plan.projectId,'discovery-caller-project-mismatch');
    if(x.projectId!==undefined)assert.equal(x.projectId,plan.projectId,'discovery-project-mismatch');
    if(x.includeSubagents!==undefined)assert.equal(typeof x.includeSubagents,'boolean','discovery-subagent-option-invalid');
    if(x.limit!==undefined)assert.ok(Number.isInteger(x.limit)&&x.limit>=1&&x.limit<=100,'discovery-limit-invalid');
    return;
  }
  if (op === 'delegate_task') {
    exactKeys(x,['task','target','title','mode','clientRequestId','runtimeMode','machine','role','interactionMode']);
    if(x.mode!==undefined)assert.equal(x.mode,'async');
    if(x.machine!==undefined)assert.equal(x.machine,'local');
    if(x.runtimeMode!==undefined)assert.ok(['inherit','approval-required'].includes(x.runtimeMode),'delegation-runtime-mode-refused');
    if(x.interactionMode!==undefined)assert.ok(x.interactionMode==='inherit'||x.interactionMode===parent.thread.interactionMode,'delegation-interaction-mode-refused');
    if(x.role!==undefined)assert.ok(['implementation','research','review','design','test','general'].includes(x.role),'delegation-role-refused');
    if (x.target !== undefined) assert.deepEqual(x.target,{providerInstanceId:plan.profile.worker.instanceId,model:plan.profile.worker.model});
    if(x.clientRequestId!==undefined)assert.ok(typeof x.clientRequestId === 'string' && x.clientRequestId.length > 0 && x.clientRequestId.length < 200);
    if(x.title!==undefined)assert.ok(typeof x.title === 'string' && x.title.length > 0 && x.title.length < 200);
    assert.ok(typeof x.task === 'string' && x.task.trim().length > 0 && x.task.length < 40000);
    if(plan.mode==='source')includesAll(x.task,plan.contextRequired,'delegation-context-incomplete');
    // Delegation prose is context, not an executable path specification.
    // Actual workspace, reads, edits and commit scope are validated separately.
    return;
  }
  assert.equal(tools.filter(i => ['task_status','studio_thread_read'].includes(toolOperation(i))).length,1,'result-polling-refused');
  const task = one(parent.subagents.filter(s => s.origin === 'app_owned'&&(!plan._graph||(op==='task_status'?s.id===x.taskId:s.childThreadId===x.threadId))),'owned-child-required');
  assert.equal(task.status,'completed');
  if (op === 'task_status') { exactKeys(x,['taskId']); assert.equal(x.taskId,task.id); }
  else {
    exactKeys(x,['threadId','view','limit','runLimit','maxCharsPerItem']); assert.equal(x.threadId,task.childThreadId);
    if (x.view !== undefined) assert.ok(typeof x.view === 'string' && x.view.length <= 32);
    for (const [key,max] of [['limit',50],['runLimit',4],['maxCharsPerItem',32000]]) if (x[key] !== undefined) assert.ok(Number.isInteger(x[key]) && x[key] > 0 && x[key] <= max,'child-read-limit-exceeded');
  }
  const {msg} = assertAutomaticWake(parent,task,item.runId);
  assert.ok(Number.isFinite(Date.parse(item.startedAt)) && Date.parse(item.startedAt) >= Date.parse(task.completedAt) && Date.parse(item.startedAt) >= Date.parse(msg.createdAt),'result-read-before-completion');
  if (worker) { assert.equal(worker.thread.id,task.childThreadId); assert.equal(worker.runs.length,1); assert.equal(worker.runs[0].status,'completed'); assert.ok(isQuiet(worker),'child-still-active'); }
}

// The complete structured operations list is mandatory. Older Codex adapters
// publish only changes[0]; accepting their fileName/diffStr would be unsafe.
export function assertFileChange(plan, item) {
  assert.equal(plan.mode,'destination','source-must-not-edit');
  assert.equal(item.type,'file_change'); assert.ok(Array.isArray(item.changes),'complete-file-change-list-required');
  const change = one(item.changes,'single-file-edit-required');
  assert.ok(['update','modify','edit'].includes(change.operation),'update-only');
  assert.equal(change.oldPath,undefined,'rename-refused');
  assert.ok(change.fileType === undefined || change.fileType === 'file','nonregular-file-refused');
  const normalize = path => isAbsolute(path) ? resolve(path) : resolve(plan.workspaceRoot,path);
  assert.equal(normalize(change.path),plan.paths.implementation,'foreign-change-path');
  assert.equal(normalize(item.fileName),plan.paths.implementation,'displayed-change-path-mismatch');
  assert.ok(typeof item.diffStr === 'string' && item.diffStr.length > 0 && item.diffStr.length < 100000,'bounded-diff-required');
  assert.ok(!/(?:^|\n)(?:rename from|rename to|new file mode|deleted file mode|old mode|new mode|GIT binary patch|\*\*\* (?:Add|Delete|Move) File:)/.test(item.diffStr),'non-update-diff-refused');
  const headers = [...item.diffStr.matchAll(/^(?:---|\+\+\+) ([^\t\r\n]+)(?:\t[^\n]*)?$/gm)].map(m => m[1]);
  for (const path of headers) {
    const trimmed = path.startsWith('a/') || path.startsWith('b/') ? path.slice(2) : path;
    assert.ok([plan.paths.implementation,relative(plan.workspaceRoot,plan.paths.implementation),relative(plan.nestedRoot,plan.paths.implementation)].includes(trimmed),'foreign-diff-path');
  }
  for (const match of item.diffStr.matchAll(/^diff --git (.+)$/gm)) {
    const names = shellWords(match[1]); assert.equal(names.length,2);
    for (const name of names) assert.equal(name.slice(2),relative(plan.nestedRoot,plan.paths.implementation),'foreign-git-diff-path');
  }
  for (const match of item.diffStr.matchAll(/^\*\*\* Update File: (.+)$/gm)) assert.equal(normalize(match[1]),plan.paths.implementation,'foreign-patch-path');
  return {fileName:item.fileName,changes:item.changes,diffStr:item.diffStr};
}

// Captured from two fresh normal project/workspace reads immediately before acceptance.
// An omitted MCP target is safe only when this coordinator has an explicit saved worker choice.
export function delegationRouting(plan, project, workspace) {
  assert.equal(project?.id,plan.projectId,'delegation-project-mismatch');
  assert.equal(project?.workspaceRoot,plan.workspaceRoot,'delegation-workspace-mismatch');
  assert.equal(workspace?.settings?.coordinatorThreadId,plan.coordinatorId,'delegation-coordinator-mismatch');
  assert.deepEqual(project.defaultModelSelection,plan.profile.worker,'delegation-worker-default-mismatch');
  assert.ok(!workspace.settings.workerMachine && !workspace.settings.autoResume,'delegation-nonlocal-routing');
  return {projectId:project.id,workspaceRoot:project.workspaceRoot,coordinatorThreadId:workspace.settings.coordinatorThreadId,defaultModelSelection:project.defaultModelSelection,workerMachine:workspace.settings.workerMachine??null,autoResume:workspace.settings.autoResume??false};
}
export function assertDelegationRouting(plan, routing) {
  requireObject(routing);exactKeys(routing,['projectId','workspaceRoot','coordinatorThreadId','defaultModelSelection','workerMachine','autoResume']);
  assert.deepEqual(routing,delegationRouting(plan,{id:routing.projectId,workspaceRoot:routing.workspaceRoot,defaultModelSelection:routing.defaultModelSelection},{settings:{coordinatorThreadId:routing.coordinatorThreadId,workerMachine:routing.workerMachine,autoResume:routing.autoResume}}),'delegation-routing-incomplete');
}
export function needsDelegationRouting(action) { return action.type==='dynamic_tool' && toolOperation(action)==='delegate_task' && (action.input.target===undefined||action.input.machine===undefined||action.input.runtimeMode===undefined||action.input.runtimeMode==='inherit'||action.input.role!==undefined||action.input.interactionMode!==undefined||action.input.mode===undefined); }
export function approvalPayload(plan, projection, parent, requestId, worker = null, routing = null) {
  assert.equal(projection.thread.projectId,plan.projectId);
  const req = one(projection.runtimeRequests.filter(r => r.id === requestId),'request-not-found');
  assert.equal(req.status,'pending'); assert.equal(req.responseCapability.type,'live');
  const approval = one(projection.turnItems.filter(i => i.type === 'approval_request' && i.requestId === req.id),'ambiguous-approval');
  assert.equal(approval.providerTurnId,req.providerTurnId); assert.equal(approval.requestKind,req.kind);
  const run = one(projection.runs.filter(r => r.id === approval.runId),'approval-outside-owned-run'); assert.ok(PENDING.has(run.status),'approval-on-terminal-run');
  const coordinator = projection.thread.id === plan.coordinatorId; let action;
  if (req.kind === 'mcp-elicitation') {
    assert.ok(coordinator,'worker-cannot-call-mcp');
    action = one(projection.turnItems.filter(i => i.type === 'dynamic_tool' && i.providerTurnId === req.providerTurnId && PENDING.has(i.status)),'ambiguous-mcp-action');
    assertMcp(plan,parent,action,worker); assert.equal(approval.appName,'studio-code');
    assert.equal(approval.prompt,`Allow the studio-code MCP server to run tool "${toolOperation(action)}"?`);
    if (toolOperation(action) === 'delegate_task') {if(plan._graph){assert.ok(parent.subagents.length<3,'worker-budget-exceeded');assert.ok(parent.subagents.every(s=>s.status==='completed'&&['claimed','delivered','acknowledged'].includes(s.completionDelivery?.state)),'previous-worker-not-settled');}else assert.equal(parent.subagents.length,0,'child-already-created');}
  } else {
    assert.ok(['command','file-change'].includes(req.kind),'unsupported-request-kind');
    assert.ok(req.nativeRequestRef?.nativeId && req.nativeRequestRef.driver === 'codex' && req.nativeRequestRef.strength === 'strong','native-action-binding-required');
    action = one(projection.turnItems.filter(i => i.type === (req.kind === 'command' ? 'command_execution' : 'file_change') && i.providerTurnId === req.providerTurnId && i.nativeItemRef?.nativeId === req.nativeRequestRef.nativeId),'ambiguous-native-action');
    assert.ok(PENDING.has(action.status),'action-already-settled');
    if (req.kind === 'command') { classifyCommand(plan,action.input,coordinator ? 'coordinator' : 'worker'); assert.equal(approval.prompt,action.input); }
    else { assert.ok(!coordinator,'coordinator-cannot-edit'); assert.equal(approval.grantRoot,null,'file-write-grant-must-be-explicitly-absent'); assertFileChange(plan,action); }
  }
  assert.equal(action.runId,approval.runId); assert.equal(action.providerTurnId,req.providerTurnId);
  const inherited = needsDelegationRouting(action);
  if(inherited){assertDelegationRouting(plan,routing);assert.equal(parent.thread.id,plan.coordinatorId);assert.equal(parent.thread.projectId,plan.projectId);assert.equal(parent.thread.runtimeMode,'approval-required');assert.ok(parent.thread.worktreePath==null||parent.thread.worktreePath===plan.workspaceRoot);assert.deepEqual({instanceId:parent.thread.modelSelection.instanceId,model:parent.thread.modelSelection.model},plan.profile.coordinator);}
  return {threadId:projection.thread.id,request:req,approval,action,...(inherited?{delegationRouting:routing}:{})};
}

export function assertRetainedItem(projectionItem, response, kind = null) {
  const item = response?.item; assert.ok(item,'retained-item-missing');
  for (const key of ['id','threadId','runId','providerTurnId','type','input','status','exitCode','updatedAt']) assert.deepEqual(item[key],projectionItem[key],'retained-item-binding-mismatch');
  const emptyIsMeaningful = ['git-root-status','git-nested-status','add','diff'].includes(kind);
  assert.ok(typeof item.output === 'string' || (item.output === null && emptyIsMeaningful),'retained-output-required'); assert.ok(!item.outputOmitted,'output-still-omitted');
  if (typeof item.output === 'string') assert.ok(!item.output.includes('… output truncated for transport'),'retained-output-truncated'); return item;
}
export function assertNativeRead(plan,kind,item,finalHead = null) {
  if(kind==='node-version')assert.match(item.output.trim(),/^v22\.\d+\.\d+$/,'node22-version-output-required');
  if (kind.startsWith('read-')&&!(plan._graph&&kind==='read-implementation')) assert.equal(sha256(item.output),plan.frozen[kind.slice(5)],'frozen-native-read-output-mismatch');
  if (kind === 'git-root-head' || kind === 'git-nested-head') {
    const key = kind === 'git-root-head' ? 'root' : 'nested', path = key === 'root' ? plan.workspaceRoot : plan.nestedRoot;
    assert.equal(item.output.trimEnd(),path + '\n' + plan.originalShas[key],'native-git-path-or-head-mismatch');
  }
  if (kind === 'git-final-head') { assert.equal(plan.mode,'destination'); assert.match(finalHead,HEX40); assert.notEqual(finalHead,plan.originalShas.nested); assert.equal(item.output.trimEnd(),finalHead,'native-final-head-mismatch'); }
}
export function assertTap(item, count, mode) {
  assert.ok(item.status==='completed'||(mode==='source'&&item.status==='failed'),'test-command-not-terminal');
  assert.equal(item.exitCode,mode === 'source' ? 1 : 0,'unexpected-test-exit');
  const text = item.output;
  const value = name => Number(one([...text.matchAll(new RegExp('^# ' + name + ' (\\d+)\\s*$','gm'))], 'tap-count-missing-' + name)[1]);
  assert.match(text,/^TAP version 13$/m); assert.equal(value('tests'),count);
  for (const key of ['cancelled','skipped','todo']) assert.equal(value(key),0,'incomplete-or-skipped-tests');
  assert.equal(value('pass') + value('fail'),count);
  if (mode === 'source') { assert.ok(value('fail') > 0); assert.match(text,/ERR_ASSERTION/); assert.ok(!/(?:SyntaxError|ReferenceError|ERR_MODULE_NOT_FOUND|ERR_UNKNOWN_FILE_EXTENSION|Cannot find module)/.test(text),'invalid-source-red-test'); }
  else { assert.equal(value('fail'),0); assert.equal(value('pass'),count); assert.ok(!/^not ok /m.test(text)); }
  return {tests:count,pass:value('pass'),fail:value('fail'),exitCode:item.exitCode};
}
export function assertCommandResult(plan,kind,item) {
  assert.ok(item.status==='completed'||((plan.mode==='source'||plan._graph)&&kind==='test'&&item.status==='failed'&&item.exitCode===1),'unexpected-command-status');
  if(kind!=='test')assert.equal(item.exitCode,0,'native-command-failed');
}

export function assertFrozen(plan,state) {
  for (const key of ['test','readme','continuation', ...(plan.mode === 'destination' ? ['context'] : ['implementation'])]) assert.equal(state.files[key].sha256,plan.frozen[key],'frozen-file-changed-' + key);
}
export function assertInitialState(plan,state) {
  assertFrozen(plan,state); assert.equal(state.files.implementation.sha256,plan.frozen.implementation);
  for (const key of ['root','nested']) { assert.equal(state.repos[key].sha,plan.originalShas[key]); assert.equal(state.repos[key].status,'','initial-checkout-dirty'); }
}

export function assertWorkerReadsBeforeEdit(plan,observer,edit,owningThreadId=edit.threadId) {
  if(plan.mode!=='destination')return;
  assert.ok(typeof owningThreadId==='string'&&owningThreadId&&owningThreadId!==plan.coordinatorId,'editing-worker-identity-required');if(edit.threadId!==undefined)assert.equal(edit.threadId,owningThreadId,'editing-worker-identity-mismatch');
  for(const key of ['context','continuation','implementation','readme','test']) {
    const reads=[...observer.outputs.values()].filter(o=>o.role==='worker'&&o.threadId===owningThreadId&&o.kind==='read-'+key&&sha256(o.response.output)===plan.frozen[key]);
    assert.ok(reads.some(o=>Number.isFinite(Date.parse(o.response.completedAt))&&Number.isFinite(Date.parse(edit.startedAt))&&Date.parse(o.response.completedAt)<=Date.parse(edit.startedAt)),'worker-frozen-read-required-before-edit-'+key);
  }
}

export function assertLocalMutation(plan,kind,state,baseline,testRecords) {
  assertFrozen(plan,state);
  assert.equal(state.repos.root.sha,baseline.repos.root.sha); assert.equal(state.repos.root.status,'','umbrella-changed');
  for (const key of ['root','nested']) assert.equal(state.repos[key].configSha256,baseline.repos[key].configSha256,'git-config-changed');
  if (kind === 'branch') { assert.equal(state.repos.nested.sha,plan.originalShas.nested); assert.equal(state.repos.nested.status,''); assert.equal(state.repos.nested.branch,baseline.repos.nested.branch); }
  if (kind === 'file-change' || kind === 'add' || kind === 'commit') {
    assert.equal(state.repos.nested.branch,plan.branch,'owned-branch-required'); assert.equal(state.repos.nested.sha,plan.originalShas.nested,'unexpected-existing-commit');
    const rel = relative(plan.nestedRoot,plan.paths.implementation);
    assert.ok(state.repos.nested.status.split('\n').filter(Boolean).every(line => [' M '+rel,'M  '+rel,'MM '+rel].includes(line)),'unrelated-working-tree-changes');
  }
  if (kind === 'commit') {
    const latest = testRecords.at(-1); assert.ok(latest?.mode === 'destination','passing-test-required-before-commit'); assert.equal(latest.implementationSha256,state.files.implementation.sha256,'code-changed-after-test');
    assert.equal(state.repos.nested.status,'M  ' + relative(plan.nestedRoot,plan.paths.implementation),'exact-staged-implementation-required');
  }
  if (kind === 'git-final-head') { assert.equal(state.repos.nested.branch,plan.branch); assert.equal(state.repos.nested.status,''); assert.notEqual(state.repos.nested.sha,plan.originalShas.nested,'final-head-before-commit'); }
}
export function validateFinalState(plan,baseline,state,testRecords,readGit = () => { throw new Error("collected-git-evidence-required"); }) {
  assertFrozen(plan,state); assert.equal(state.repos.root.sha,baseline.repos.root.sha); assert.equal(state.repos.root.branch,baseline.repos.root.branch); assert.equal(state.repos.root.status,'');
  for (const k of ['root','nested']) assert.equal(state.repos[k].configSha256,baseline.repos[k].configSha256);
  const test = testRecords.at(-1); assert.ok(test,'actual-test-output-required'); assert.equal(test.mode,plan.mode); assert.equal(test.implementationSha256,state.files.implementation.sha256,'final-code-not-tested');
  if (plan.mode === 'source') { assert.deepEqual(state,baseline,'source-was-mutated'); return {unfinished:true}; }
  assert.equal(state.repos.nested.branch,plan.branch); assert.equal(state.repos.nested.status,'','final-working-tree-dirty');
  assert.notEqual(state.repos.nested.sha,plan.originalShas.nested,'no-implementation-commit');
  const evidence = {
    parents:readGit(plan.nestedRoot,['show','-s','--format=%P','HEAD']),
    subject:readGit(plan.nestedRoot,['show','-s','--format=%s','HEAD']),
    paths:readGit(plan.nestedRoot,['diff','--name-only',plan.originalShas.nested,'HEAD']),
    modifiedPaths:readGit(plan.nestedRoot,['diff','--diff-filter=M','--name-only',plan.originalShas.nested,'HEAD']),
  };
  assert.equal(evidence.parents,plan.originalShas.nested,'not-one-direct-commit'); assert.equal(evidence.subject,plan.commitMessage,'commit-subject-mismatch');
  assert.equal(evidence.paths,relative(plan.nestedRoot,plan.paths.implementation),'commit-touches-other-files');
  assert.equal(evidence.modifiedPaths,relative(plan.nestedRoot,plan.paths.implementation),'commit-is-not-file-update');
  return {commit:state.repos.nested.sha,parent:plan.originalShas.nested,changedPath:relative(plan.nestedRoot,plan.paths.implementation),evidence};
}

export function makeObserver(plan) {
  return {plan,tools:new Map(),commands:new Map(),files:new Map(),approved:new Map(),testRecords:[],outputs:new Map(),threads:new Set(),runs:new Set(),turns:new Set(),attempts:new Set()};
}
export function observe(observer,p,parent) {
  const plan = observer.plan, coordinator = p.thread.id === plan.coordinatorId;
  assert.equal(p.thread.projectId,plan.projectId); assert.equal(p.thread.runtimeMode,'approval-required');
  assert.ok(p.thread.worktreePath == null || p.thread.worktreePath === plan.workspaceRoot,'thread-workspace-changed');
  assert.deepEqual({instanceId:p.thread.modelSelection.instanceId,model:p.thread.modelSelection.model},plan.profile[coordinator ? 'coordinator' : 'worker']);
  observer.threads.add(p.thread.id); for (const r of p.runs) observer.runs.add(r.id);
  for (const t of p.providerTurns ?? []) observer.turns.add(t.id); for (const a of p.attempts ?? []) observer.attempts.add(a.id);
  assert.ok(observer.threads.size <= (plan._graph?4:2) && observer.runs.size <= (plan._graph?7:3) && observer.turns.size <= (plan._graph?7:3) && observer.attempts.size <= (plan._graph?7:3),'native-budget-exceeded');
  assert.ok(p.runs.every(r => !['failed','interrupted','cancelled'].includes(r.status)),'native-run-failed');
  assert.ok((p.subagents ?? []).length <= (coordinator ? (plan._graph?3:1) : 0),'extra-native-worker');
  assert.ok((p.subagents ?? []).every(s => s.origin === 'app_owned' && s.childThreadId),'provider-subagent-refused');
  assert.ok(!(p.nodes ?? []).some(n => n.kind === 'hook'),'unexpected-hook');
  for (const item of p.turnItems ?? []) {
    assert.ok(!['web_search','file_search','user_input_request','error'].includes(item.type),'unapproved-native-operation');
    if (item.type === 'dynamic_tool') {
      if(coordinator)assertMcp(plan,parent,item);
      else {
        assert.equal(toolOperation(item),'orchestrator_capabilities','worker-mcp-refused');
        assert.deepEqual(item.input,{},'worker-capabilities-empty-input-required');
        assert.equal(p.turnItems.filter(i=>i.type==='dynamic_tool').length,1,'duplicate-worker-capabilities-read');
      }
      const h = sha256(JSON.stringify({toolName:item.toolName,input:item.input})); assert.ok(!observer.tools.has(item.id) || observer.tools.get(item.id) === h,'mcp-input-changed'); observer.tools.set(item.id,h);
    }
    if (item.type === 'command_execution') {
      const entry = classifyCommand(plan,item.input,coordinator ? 'coordinator' : 'worker');
      assert.ok(!observer.commands.has(item.id) || observer.commands.get(item.id).input === item.input,'command-input-changed');
      observer.commands.set(item.id,{...entry,input:item.input}); assert.ok(observer.commands.size <= 40,'command-budget-exceeded');
      if (coordinator) assert.ok([...observer.commands.values()].filter(x => x.role === 'coordinator'&&x.kind==='read-context').length<=1,'coordinator-context-read-once');
      if (entry.kind === 'test') assert.ok([...observer.commands.values()].filter(x => x.kind === 'test').length <= (plan.mode === 'source' ? 1 : 4),'test-command-budget-exceeded');
      if (['branch','add','commit'].includes(entry.kind)) {
        assert.equal([...observer.commands.values()].filter(x => x.kind === entry.kind).length,1,'duplicate-git-mutation');
        if (item.status === 'completed') assert.ok(observer.approved.has(item.id),'git-mutation-without-scoped-approval');
      }
      if (['completed','failed'].includes(item.status)) assertCommandResult(plan,entry.kind,item);
    }
    if (item.type === 'file_change') {
      assert.ok(!coordinator,'coordinator-file-edit-refused'); const payload = assertFileChange(plan,item), h = sha256(JSON.stringify(payload));
      assert.ok(!observer.files.has(item.id) || observer.files.get(item.id) === h,'file-change-payload-changed'); observer.files.set(item.id,h);
      assert.ok(observer.files.size <= 4,'file-edit-budget-exceeded'); if (item.status === 'completed') assert.ok(observer.approved.has(item.id),'file-edit-without-scoped-approval');
    }
  }
}
export function assertProjectionBindings(p) {
  const by=(field)=>{const rows=p[field]??[],map=new Map(rows.map(x=>[x.id,x]));assert.equal(map.size,rows.length,'duplicate-'+field+'-record');return map;};
  const runs=by('runs'),turns=by('providerTurns'),nodes=by('nodes'),attempts=by('attempts');
  const maps={runId:runs,providerTurnId:turns,nodeId:nodes,parentNodeId:nodes,rootNodeId:nodes,runAttemptId:attempts};
  for(const field of ['runs','providerTurns','attempts','turnItems','nodes','runtimeRequests','messages','subagents'])for(const row of p[field]??[]){
    if(row.threadId!=null)assert.equal(row.threadId,p.thread.id,'foreign-'+field+'-thread');
    for(const [key,map]of Object.entries(maps))if(row[key]!=null){assert.ok(map.has(row[key]),'foreign-'+field+'-'+key);const target=map.get(row[key]);if(row.runId!=null&&target.runId!=null)assert.equal(target.runId,row.runId,'cross-run-'+field+'-'+key);}
    if(row.providerTurnId!=null&&row.runId!=null){const turn=turns.get(row.providerTurnId),attempt=attempts.get(turn.runAttemptId),node=nodes.get(turn.nodeId);for(const owner of [attempt,node].filter(Boolean))assert.equal(owner.runId,row.runId,'foreign-provider-turn-run');}
  }
}
export function assertGraphOwnership(plan,parent,workers=null) {
  assert.equal(parent.thread.id,plan.coordinatorId);assert.equal(parent.thread.projectId,plan.projectId);assertProjectionBindings(parent);
  const firstRuns=parent.runs.filter(r=>!parent.messages.find(m=>m.id===r.userMessageId)?.delegatedCompletion);
  assert.ok(firstRuns.length<=1,'unrelated-new-coordinator-run');
  if(!firstRuns.length){assert.equal(parent.runs.length,0);assert.equal(parent.subagents.length,0);return null;}
  const first=firstRuns[0],msg=one(parent.messages.filter(m=>m.id===first.userMessageId),'start-message-required');
  includesAll(msg.text,[`Continue handoff ${plan.operationId}.`,plan.paths.context,plan.workspaceRoot],'product-start-context-mismatch');
  assert.ok(parent.subagents.length<=3,'worker-budget-exceeded');
  const childIds=new Set(),parentRuns=new Set();
  for(const task of parent.subagents){
    assert.equal(task.origin,'app_owned');assert.equal(task.threadId,parent.thread.id);assert.equal(task.createdBy,'agent');
    assert.ok(task.childThreadId&&!childIds.has(task.childThreadId),'duplicate-or-missing-worker');childIds.add(task.childThreadId);assert.ok(!parentRuns.has(task.runId),'parallel-child-delegation-refused');parentRuns.add(task.runId);one(parent.runs.filter(r=>r.id===task.runId),'delegating-run-missing');
    const delegated=one(parent.turnItems.filter(i=>i.type==='dynamic_tool'&&toolOperation(i)==='delegate_task'&&i.runId===task.runId),'task-delegation-tool-missing');
    const input=delegated.input,expected=input.role===undefined||input.role==='general'?input.task:`Act as the ${input.role} sub-agent for this task.\n\n${input.task}`;assert.equal(task.prompt,expected,'delegated-prompt-changed');
    assert.ok(Number.isFinite(Date.parse(task.startedAt))&&Number.isFinite(Date.parse(delegated.startedAt))&&Date.parse(task.startedAt)>=Date.parse(delegated.startedAt),'task-start-precedes-delegation');
  }
  for(const run of parent.runs.filter(r=>r.id!==first.id)){
    const message=one(parent.messages.filter(m=>m.id===run.userMessageId),'wake-message-missing');
    const task=one(parent.subagents.filter(s=>message.delegatedCompletion?.taskIds?.includes(s.id)),'wake-needs-owned-child');assertAutomaticWake(parent,task,run.id);assert.ok(Number.isFinite(Date.parse(task.completedAt))&&Date.parse(message.createdAt)>=Date.parse(task.completedAt),'wake-before-worker-completion');
  }
  for(const task of parent.subagents.filter(s=>s.runId!==first.id)){
    const run=one(parent.runs.filter(r=>r.id===task.runId),'delegation-run-missing'),message=one(parent.messages.filter(m=>m.id===run.userMessageId),'delegation-wake-missing');
    const previous=one(parent.subagents.filter(s=>message.delegatedCompletion?.taskIds?.includes(s.id)),'serial-delegation-needs-completed-predecessor');
    assert.equal(previous.status,'completed');assert.equal(previous.completionDelivery?.observedByRunId,run.id);assert.ok(['claimed','delivered','acknowledged'].includes(previous.completionDelivery?.state));assert.ok(Date.parse(task.startedAt)>=Date.parse(message.createdAt)&&Date.parse(task.startedAt)>=Date.parse(previous.completedAt),'overlapping-child-work');
  }
  assert.ok(parent.subagents.filter(s=>PENDING.has(s.status)).length<=1,'overlapping-workers-refused');
  if(workers){for(const w of workers)assertProjectionBindings(w);assert.equal(workers.length,childIds.size);const seen=new Set();for(const worker of workers){assert.ok(childIds.has(worker.thread.id)&&!seen.has(worker.thread.id),'foreign-or-duplicate-worker');seen.add(worker.thread.id);assert.equal(worker.thread.projectId,plan.projectId);assert.ok(worker.runs.length<=1,'worker-has-unrelated-run');
    const task=one(parent.subagents.filter(s=>s.childThreadId===worker.thread.id),'child-task-missing');assert.deepEqual(worker.thread.lineage,{parentThreadId:parent.thread.id,relationshipToParent:'subagent',rootThreadId:parent.thread.id});assert.deepEqual(worker.thread.forkedFrom,{type:'node',nodeId:task.id});
    if(worker.runs.length){const run=worker.runs[0],message=one(worker.messages.filter(m=>m.id===run.userMessageId),'child-start-message-missing');assert.equal(run.threadId,worker.thread.id);assert.equal(message.threadId,worker.thread.id);assert.equal(message.runId,run.id);assert.equal(message.createdBy,'agent');assert.equal(message.creationSource,'mcp');assert.equal(message.senderThreadId,parent.thread.id);assert.equal(message.text,task.prompt,'child-task-context-changed');assert.ok(Date.parse(run.requestedAt)>=Date.parse(task.startedAt),'child-run-precedes-delegation');if(run.startedAt!=null)assert.ok(Number.isFinite(Date.parse(run.startedAt))&&Date.parse(run.startedAt)>=Date.parse(run.requestedAt),'child-start-before-request');if(run.completedAt!=null)assert.ok(Number.isFinite(Date.parse(run.startedAt))&&Date.parse(run.completedAt)>=Date.parse(run.startedAt),'child-completed-before-start');if(task.status==='completed'){assert.equal(run.status,'completed');assert.ok(Number.isFinite(Date.parse(run.completedAt))&&Date.parse(task.completedAt)>=Date.parse(run.completedAt),'task-before-child-completed');}}
  }}
  return first;
}
export function assertCausalPath(initialRunId,completionRunId,edges,runs) {
  const visited=new Set([initialRunId]),tasks=new Set();let cursor=initialRunId;
  while(true){const next=edges.filter(e=>e.parentRunId===cursor);if(!next.length)break;assert.equal(next.length,1,'causal-branch-refused');const edge=next[0];assert.ok(!tasks.has(edge.taskId)&&!visited.has(edge.wakeRunId),'causal-cycle-refused');tasks.add(edge.taskId);cursor=edge.wakeRunId;visited.add(cursor);}
  assert.equal(cursor,completionRunId,'causal-terminal-mismatch');assert.equal(tasks.size,edges.length,'disconnected-causal-task');assert.deepEqual([...visited].sort(),runs.map(r=>r.id).sort(),'disconnected-causal-run');
}
export function validateGraphOutcome(plan,parent,workers,observer,finalCommit) {
  const initial=assertGraphOwnership(plan,parent,workers);assert.ok(initial);assert.ok(workers.length>=1&&workers.length<=3);
  assert.ok([parent,...workers].every(p=>p.runs.every(r=>r.status==='completed')&&isQuiet(p)),'graph-not-completed-and-quiet');
  assert.ok([parent,...workers].every(w=>w.turnItems.filter(i=>i.type==='dynamic_tool').every(i=>i.status==='completed')),'graph-tool-not-completed');
  const editors=workers.filter(w=>w.turnItems.some(i=>i.type==='file_change')),editor=one(editors,'exactly-one-editing-worker-required');
  const edges=parent.subagents.map(task=>{const worker=one(workers.filter(w=>w.thread.id===task.childThreadId),'missing-worker');assert.equal(worker.runs.length,1);assert.equal(task.status,'completed');assert.ok(['delivered','acknowledged'].includes(task.completionDelivery?.state));const wakeRunId=task.completionDelivery.observedByRunId;assertAutomaticWake(parent,task,wakeRunId);return {taskId:task.id,parentRunId:task.runId,workerThreadId:worker.thread.id,workerRunId:worker.runs[0].id,wakeRunId,completionState:task.completionDelivery.state};});
  assert.equal(parent.runs.length,edges.length+1,'unexplained-coordinator-runs');
  const finalEdge=one(edges.filter(e=>!edges.some(next=>next.parentRunId===e.wakeRunId)),'one-terminal-wake-required');
  assertCausalPath(initial.id,finalEdge.wakeRunId,edges,parent.runs);
  const text=(p,run)=>p.turnItems.filter(i=>i.type==='assistant_message'&&i.runId===run).map(i=>i.text).join('\n');
  const workerTexts=workers.map(w=>({threadId:w.thread.id,text:text(w,w.runs[0].id)})),relayText=text(parent,finalEdge.wakeRunId);
  assert.match(finalCommit,HEX40);includesAll(relayText,[plan.originalShas.root,plan.originalShas.nested,finalCommit],'final-code-pins-not-relayed');
  assert.ok(workerTexts.find(w=>w.threadId===editor.thread.id).text.trim(),'editing-worker-result-required');
  assert.ok([...relayText.matchAll(/studio:\/\/thread\/([^\s)]+)/g)].some(([,value])=>{try{return decodeURIComponent(value)===editor.thread.id;}catch{return false;}}),'editing-child-link-not-relayed');
  for(const worker of workers)assert.ok([...observer.outputs.values()].some(o=>o.threadId===worker.thread.id&&o.kind==='read-context'),'every-worker-must-read-retained-context');
  for(const entry of buildCommandPolicy(plan).filter(e=>e.required))assert.ok([...observer.outputs.values()].some(o=>o.kind===entry.kind&&(SHARED_GIT_KINDS.has(entry.kind)||o.threadId===editor.thread.id)),'required-editor-native-output-missing-'+entry.kind);
  return {initialRunId:initial.id,completionRunId:finalEdge.wakeRunId,workerThreadIds:workers.map(w=>w.thread.id),editingWorkerThreadId:editor.thread.id,edges,workerTexts,relayText};
}

export function validateOutcome(plan,parent,worker,observer,finalCommit = null) {
  assert.equal(parent.runs.length,2); assert.equal(worker.runs.length,1); assert.ok([...parent.runs,...worker.runs].every(r => r.status === 'completed'));
  assert.ok(isQuiet(parent) && isQuiet(worker),'native-not-quiescent');
  assert.ok(worker.turnItems.filter(i=>i.type==='dynamic_tool').every(i=>i.status==='completed'),'worker-capabilities-not-completed');
  const task = one(parent.subagents,'one-worker-required'); assert.equal(task.origin,'app_owned'); assert.equal(task.childThreadId,worker.thread.id); assert.equal(task.status,'completed');
  const wake = one(parent.runs.filter(r => r.id !== task.runId),'one-wake-required'); assertAutomaticWake(parent,task,wake.id);
  assert.ok(['delivered','acknowledged'].includes(task.completionDelivery.state)); assert.equal(task.completionDelivery.observedByRunId,wake.id);
  const text = (p,run) => p.turnItems.filter(i => i.type === 'assistant_message' && i.runId === run).map(i => i.text).join('\n');
  const workerText = text(worker,worker.runs[0].id), relayText = text(parent,wake.id);
  const pins = [plan.originalShas.root,plan.originalShas.nested];
  for (const s of [workerText,relayText]) includesAll(s,[...plan.contextRequired,...pins],'context-and-code-pins-not-carried-through-worker-and-relay');
  if (plan.mode === 'destination') {
    assert.match(finalCommit,HEX40,'final-commit-required');includesAll(relayText,[finalCommit],'final-commit-not-relayed');
    if([...observer.commands.values()].some(e=>e.role==='worker'&&e.kind==='commit'))includesAll(workerText,[finalCommit],'worker-commit-not-reported');
  }
  assert.ok([...relayText.matchAll(/studio:\/\/thread\/([^\s)]+)/g)].some(([,value]) => {try{return decodeURIComponent(value) === worker.thread.id;}catch{return false;}}),'child-link-not-relayed');
  for (const entry of buildCommandPolicy(plan).filter(e => e.required)) assert.ok([...observer.outputs.values()].some(o => (o.role === entry.role || (plan.mode==='destination'&&SHARED_GIT_KINDS.has(entry.kind))) && o.kind === entry.kind),'required-native-output-missing-' + entry.role + '-' + entry.kind);
  return {workerText,relayText,workerThreadId:worker.thread.id,automaticWakeRunId:wake.id,completionState:task.completionDelivery.state};
}

function actionIdentity(item) {
  return Object.fromEntries(['id','type','threadId','runId','providerTurnId','nativeItemRef','input','toolName','fileName','changes','diffStr'].filter(k => Object.hasOwn(item,k)).map(k => [k,item[k]]));
}
function approvalIdentity(item) {
  return Object.fromEntries(['id','type','requestId','requestKind','runId','providerTurnId','prompt','appName','grantRoot'].filter(k => Object.hasOwn(item,k)).map(k => [k,item[k]]));
}
// Pure replay. This verifies evidence relationships; the parent additionally
// pins the entire plan/receipt bytes with SHA256 in its public acceptance proof.
export function verifyReceipt(plan,receipt) {
  validatePlan(plan); requireObject(receipt);assert.ok(receipt.workflowVersion===undefined||receipt.workflowVersion===2,'unknown-workflow-version');assert.ok(receipt.workflowVersion!==2||plan.mode==='destination','graph-destination-only');const graph=plan.mode==='destination'&&receipt.workflowVersion===2;if(graph)plan={...plan,_graph:true};
  for (const key of ['mode','host','projectId','coordinatorId']) assert.equal(receipt[key],plan[key],'receipt-plan-binding');
  assert.equal(receipt.operationId,plan.operationId ?? null); assertInitialState(plan,receipt.baseline);
  const parent=receipt.parent,workers=graph?receipt.workers:[receipt.worker];assert.ok(parent&&Array.isArray(workers)&&workers.length&&workers.every(Boolean)&&receipt.rawParent,'final-projections-required');const worker=graph?workers.find(w=>w.turnItems.some(i=>i.type==='file_change')):receipt.worker;assert.ok(worker,'editing-worker-required');
  assert.deepEqual(scopeProjection(receipt.rawParent,receipt.prior ?? null,plan),parent,'final-history-scope-mismatch');
  if(graph)assertGraphOwnership(plan,parent,workers);else{assertParentOwnership(plan,parent);assert.equal(worker.thread.id,one(parent.subagents,'one-child-required').childThreadId);}
  const observer = makeObserver(plan), seenRequests = new Set();
  for (const record of receipt.approvals) {
    assert.ok(!seenRequests.has(record.requestId),'duplicate-approval-receipt'); seenRequests.add(record.requestId);
    assert.equal(record.decision,'accept'); const payload = record.payload;
    assert.equal(record.payloadSha256,sha256(JSON.stringify(payload)),'approval-receipt-hash-mismatch');
    assert.equal(record.threadId,payload.threadId); assert.equal(record.itemId,payload.action.id); assert.equal(record.requestId,payload.request.id);
    const p = record.threadId === plan.coordinatorId ? parent : one(workers.filter(w=>w.thread.id===record.threadId),'foreign-approved-worker'); assert.equal(p.thread.id,record.threadId,'foreign-approved-thread');
    const req = one(p.runtimeRequests.filter(r => r.id === record.requestId),'approved-request-missing');
    assert.equal(req.status,'resolved'); assert.equal(req.decision,'accept');
    for (const key of ['id','providerTurnId','kind','nativeRequestRef','responseCapability']) assert.deepEqual(req[key],payload.request[key],'approval-request-binding-changed');
    const action = one(p.turnItems.filter(i => i.id === record.itemId),'approved-action-missing');
    assert.deepEqual(actionIdentity(action),actionIdentity(payload.action),'approved-action-binding-changed');
    const approval = one(p.turnItems.filter(i => i.type === 'approval_request' && i.requestId === req.id),'approved-display-missing');
    assert.deepEqual(approvalIdentity(approval),approvalIdentity(payload.approval),'approved-display-binding-changed');
    // Rebuild the retained pending payload with genuine final ownership/context.
    const atApproval = cloneProjection(p); atApproval.runtimeRequests = atApproval.runtimeRequests.map(r => r.id === req.id ? payload.request : r);
    atApproval.turnItems = atApproval.turnItems.map(i => i.id === action.id ? payload.action : i.id === approval.id ? payload.approval : i);
    atApproval.runs = atApproval.runs.map(r => r.id === action.runId ? {...r,status:'running'} : r);
    let parentAtApproval = record.threadId === plan.coordinatorId ? atApproval : parent;
    if (action.type === 'dynamic_tool' && toolOperation(action) === 'delegate_task') { atApproval.subagents = graph?atApproval.subagents.filter(s=>s.runId!==action.runId&&s.completionDelivery?.observedByRunId===action.runId):[]; parentAtApproval = atApproval; }
    const revalidated = approvalPayload(plan,atApproval,parentAtApproval,record.requestId,graph?null:worker,payload.delegationRouting??null);
    assert.equal(sha256(JSON.stringify(revalidated)),record.payloadSha256,'approval-payload-replay-mismatch');
    const kind = action.type === 'file_change' ? 'file-change' : action.type === 'command_execution' ? classifyCommand(plan,action.input,record.threadId === plan.coordinatorId ? 'coordinator' : 'worker').kind : 'mcp';
    assert.equal(record.kind,kind,'approval-kind-summary-forged'); assert.ok(!observer.approved.has(action.id),'action-approved-twice'); observer.approved.set(action.id,record.payloadSha256);
  }
  observe(observer,parent,parent);for(const w of workers)observe(observer,w,parent);
  const sourceItems = [...parent.turnItems,...workers.flatMap(w=>w.turnItems)].filter(i => i.type === 'command_execution');
  assert.equal(receipt.outputs.length,sourceItems.length,'missing-or-extra-retained-outputs');
  const tests = [];
  for (const output of receipt.outputs) {
    assert.ok(!observer.outputs.has(output.itemId),'duplicate-retained-output');
    const projectionItem = one(sourceItems.filter(i => i.id === output.itemId),'foreign-output-item');
    const entry = observer.commands.get(projectionItem.id);
    const actual = assertRetainedItem(projectionItem,{item:output.response},entry.kind);
    assertCommandResult(plan,entry.kind,actual);
    assert.equal(output.sha256,sha256(JSON.stringify(actual)),'retained-output-hash-mismatch');
    assert.equal(output.threadId,actual.threadId); assert.equal(output.runId,actual.runId); assert.equal(output.input,actual.input);
    assert.equal(output.kind,entry.kind); assert.equal(output.role,entry.role);
    assertNativeRead(plan,entry.kind,actual,receipt.after?.repos?.nested?.sha);
    if(graph&&entry.kind==='read-implementation')assert.equal(output.implementationSha256,sha256(actual.output),'observed-implementation-read-hash-mismatch');
    if (entry.kind === 'test') {
      const mode = actual.exitCode === 0 ? 'destination' : 'source'; assert.ok(plan.mode === 'destination' || mode === 'source','source-was-not-red');
      const derived = assertTap(actual,plan.expectedTestCount,mode), saved = one(receipt.testRecords.filter(t => t.itemId === actual.id),'test-summary-missing');
      for (const key of ['tests','pass','fail','exitCode']) assert.equal(saved[key],derived[key],'test-summary-forged'); assert.equal(saved.mode,mode);
      assert.match(saved.implementationSha256,HEX64); tests.push(saved);
    } else assert.equal(actual.exitCode,0);
    observer.outputs.set(actual.id,output);
  }
  assert.equal(receipt.testRecords.length,tests.length,'extra-test-summary'); assert.ok(tests.length > 0);
  assert.deepEqual(tests,receipt.testRecords,'test-order-mismatch');
  const nativeTests = workers.flatMap(w=>w.turnItems).filter(i => i.type === 'command_execution' && classifyCommand(plan,i.input,'worker').kind === 'test');
  assert.deepEqual(tests.map(t => t.itemId),nativeTests.map(t => t.id),'retained-test-order-mismatch');
  const outcome = graph?validateGraphOutcome(plan,parent,workers,observer,receipt.after?.repos?.nested?.sha):validateOutcome(plan,parent,worker,observer,receipt.after?.repos?.nested?.sha); assert.deepEqual(receipt.outcome,outcome,'outcome-summary-forged');
  const evidence = receipt.git?.evidence;
  const readGit = (_root,args) => args.includes('--format=%P') ? evidence?.parents : args.includes('--format=%s') ? evidence?.subject : args.includes('--diff-filter=M') ? evidence?.modifiedPaths : evidence?.paths;
  const git = validateFinalState(plan,receipt.baseline,receipt.after,tests,readGit); assert.deepEqual(receipt.git,git,'git-summary-forged');
  if (plan.mode === 'destination') {
    const lastTest = nativeTests.at(-1), changes = worker.turnItems.filter(i => i.type === 'file_change'); assert.ok(changes.length > 0,'no-native-file-edit');
    for(const change of changes)assertWorkerReadsBeforeEdit(plan,observer,change,worker.thread.id);
    const branch=one(sourceItems.filter(i=>observer.commands.get(i.id)?.kind==='branch'),'one-native-branch-required');
    for(const change of changes)assert.ok(Number.isFinite(Date.parse(branch.completedAt))&&Date.parse(branch.completedAt)<=Date.parse(change.startedAt),'edit-before-owned-branch');
    assert.ok(Number.isFinite(Date.parse(lastTest.startedAt)) && Number.isFinite(Date.parse(lastTest.completedAt)),'native-test-time-required');
    for (const change of changes) assert.ok(Number.isFinite(Date.parse(change.completedAt)) && Date.parse(change.completedAt) <= Date.parse(lastTest.startedAt),'final-edit-after-successful-test');
    const commit = one(sourceItems.filter(i => observer.commands.get(i.id)?.kind === 'commit'),'one-native-commit-required');
    assert.ok(Number.isFinite(Date.parse(commit.startedAt)) && Date.parse(commit.startedAt) >= Date.parse(lastTest.completedAt),'commit-before-successful-test');
    if(graph&&commit.threadId===parent.thread.id){const message=one(parent.messages.filter(m=>m.runId===commit.runId&&m.delegatedCompletion),'coordinator-commit-needs-completion-wake');assert.ok(Date.parse(commit.startedAt)>=Date.parse(message.createdAt),'coordinator-commit-before-wake');}
    const commitOutput = observer.outputs.get(commit.id).response.output;
    const abbreviated = one([...commitOutput.matchAll(/^\[[^\r\n]* ([a-f0-9]{7,40})\] /gm)],'native-commit-output-missing')[1];
    assert.ok(receipt.after.repos.nested.sha.startsWith(abbreviated),'native-commit-output-sha-mismatch');
    const finalRead = one(sourceItems.filter(i => observer.commands.get(i.id)?.kind === 'git-final-head'),'one-final-head-read-required');
    assert.ok(Number.isFinite(Date.parse(finalRead.startedAt)) && Number.isFinite(Date.parse(commit.completedAt)) && Date.parse(finalRead.startedAt) >= Date.parse(commit.completedAt),'final-head-read-before-commit');
  }
  assert.deepEqual(receipt.quiescence,[quiescence(parent),...workers.map(quiescence)],'quiescence-summary-forged');
  return {verified:true,mode:plan.mode,operationId:plan.operationId ?? null,projectId:plan.projectId,...(graph?{workerThreadIds:workers.map(w=>w.thread.id),initialRunId:outcome.initialRunId,completionRunId:outcome.completionRunId}:{workerThreadId:worker.thread.id}),tests:tests.at(-1),git};
}
const cloneProjection = p => structuredClone(p);


export {PENDING, SETTLED, GIT};
