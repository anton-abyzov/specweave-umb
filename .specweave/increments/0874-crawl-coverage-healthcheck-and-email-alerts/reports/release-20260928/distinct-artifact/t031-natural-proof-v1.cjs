'use strict';
// Read-only evidence helper. No network calls when imported for offline tests.
const fs = require('fs'), crypto = require('crypto'), cp = require('child_process');
const { createRequire } = require('module');
const BASE = '/tmp/cc-work-release-20260928/0874/';
const sha = x => crypto.createHash('sha256').update(typeof x === 'string' ? x : JSON.stringify(x)).digest('hex');
const artifact = p => (p || '').replace(/^\/+/, '').replace(/\/?SKILL\.md$/i, '');
const repo = p => (p || '').trim().replace(/^https?:\/\//, '').replace(/^www\./, '').replace(/\/+$/, '').replace(/\.git$/, '').toLowerCase();
const HASH = /^[a-f0-9]{64}$/;
const SUB_FIELDS = ['id', 'repoUrl', 'skillName', 'skillPath', 'sourceType', 'sourceId', 'artifactPath', 'userId'];
const SKILL_FIELDS = ['id', 'name', 'displayName', 'repoUrl', 'skillPath', 'ownerSlug', 'repoSlug', 'skillSlug', 'legacySlug', 'privacy', 'tenantId', 'repositoryId'];
const fingerprint = (r, fields) => sha(fields.map(k => r[k] ?? null));
function project(r) {
  const k = r.skill;
  return { rowIdSha256: sha(r.id), tupleSha256: r.tupleHash, protectedSha256: fingerprint(r, SUB_FIELDS),
    labelSha256: sha(r.skillName), pathSha256: sha(r.skillPath), state: r.state, userOwned: r.userId !== null,
    pathConsistent: artifact(r.skillPath) === r.artifactPath,
    linkedSkill: k ? { idSha256: sha(k.id), protectedSha256: fingerprint(k, SKILL_FIELDS),
      publicTenantless: k.privacy === 'PUBLIC' && k.tenantId === null,
      pathMatches: artifact(k.skillPath) === r.artifactPath, repoMatches: repo(k.repoUrl) === repo(r.repoUrl),
      repositoryMatches: !r.repositoryUrl || repo(r.repositoryUrl) === repo(r.repoUrl),
      versionTargets: r.versions.map(v => sha([v.id, v.skillId])).sort(), versionCount: r.versions.length } : null };
}
function compare(before, after) {
  const check = (v, msg) => { if (!v) throw Error(msg); };
  check(before.kind === 'baseline' && after.kind === 'readback', 'receipt_kind');
  check(before.schemaVersion === 1 && after.schemaVersion === 1, 'schema_version');
  check(before.items.length === 22 && before.oldRows.length === 10, 'baseline_cardinality');
  check(new Set(before.items.map(i=>i.itemIdentitySha256)).size === 22 && new Set(before.items.map(i=>i.tupleSha256)).size === 22, 'baseline_duplicates');
  check(after.baselineSha256 === sha(before), 'baseline_binding');
  check(before.readOnlyTransaction === true && after.readOnlyTransaction === true && before.rawIdentitiesExported === false && after.rawIdentitiesExported === false, 'readonly_receipt');
  check(after.checkpoint.sweepId === before.checkpoint.sweepId && after.checkpoint.schemaVersion === 2, 'same_sweep');
  check(JSON.stringify(after.checkpoint.containers) === JSON.stringify(before.checkpoint.containers), 'same_runtime');
  check(after.checkpoint.totalLost >= before.checkpoint.totalLost && after.checkpoint.totalErrors >= before.checkpoint.totalErrors, 'historical_counters');
  check(new Set(after.oldRows.map(r=>r.rowIdSha256)).size === after.oldRows.length, 'duplicate_old_rows');
  const old = new Map(after.oldRows.map(r => [r.rowIdSha256, r]));
  const oldIds = new Set(before.oldRows.map(r => r.rowIdSha256));
  const oldSkillIds = new Set(before.oldRows.flatMap(r => r.linkedSkill ? [r.linkedSkill.idSha256] : []));
  const oldChecks = before.oldRows.map(r => {
    const n = old.get(r.rowIdSha256), k = r.linkedSkill;
    return { rowIdSha256: r.rowIdSha256, present: Boolean(n), identityPreserved: n?.protectedSha256 === r.protectedSha256,
      existingLinkPreserved: !k || n?.linkedSkill?.idSha256 === k.idSha256,
      linkedSkillPreserved: !k || n?.linkedSkill?.protectedSha256 === k.protectedSha256,
      oldVersionTargetsPreserved: !k || k.versionTargets.every(v => n?.linkedSkill?.versionTargets.includes(v)),
      newLinkSafe: Boolean(n && (!n.linkedSkill || (n.linkedSkill.publicTenantless && n.linkedSkill.pathMatches && n.linkedSkill.repoMatches && n.linkedSkill.repositoryMatches))) };
  });
  const grouped = new Map();
  for (const r of after.canonicalRows) { const a = grouped.get(r.tupleSha256) || []; a.push(r); grouped.set(r.tupleSha256, a); }
  const unresolved = new Set(after.checkpoint.unresolvedHashes);
  const accepted = new Set(after.checkpoint.acceptedHashes);
  const progressed = after.checkpoint.sweepId === before.checkpoint.sweepId && (after.checkpoint.shardIndex > before.checkpoint.shardIndex || (after.checkpoint.shardIndex === before.checkpoint.shardIndex && after.checkpoint.page > before.checkpoint.page));
  const itemChecks = before.items.map(i => {
    const rows = grouped.get(i.tupleSha256) || [], r = rows[0], k = r?.linkedSkill;
    const valid = rows.length === 1 && !oldIds.has(r.rowIdSha256) && r.pathConsistent && !r.userOwned;
    const publicationSafe = !k || (!oldSkillIds.has(k.idSha256) && k.publicTenantless && k.pathMatches && k.repoMatches && k.repositoryMatches);
    return { itemIdentitySha256: i.itemIdentitySha256, tupleSha256: i.tupleSha256, rowCount: rows.length,
      distinctCanonicalRow: valid, durableQualifiedLabel: Boolean(r && r.labelSha256 === i.qualifiedLabelSha256),
      sourceSettled: Boolean(valid && !unresolved.has(i.itemIdentitySha256) && (accepted.has(i.itemIdentitySha256) || progressed)),
      state: r?.state ?? null, publicationSafe,
      publishedWithVersion: Boolean(valid && publicationSafe && r.state === 'PUBLISHED' && k && k.versionCount > 0),
      terminalRejected: Boolean(valid && ['REJECTED', 'TIER1_FAILED', 'BLOCKED'].includes(r.state)) };
  });
  const oldPreserved = oldChecks.every(c => Object.entries(c).every(([k,v]) => k === 'rowIdSha256' || v === true));
  const noDuplicateNewLinks = new Set(after.canonicalRows.flatMap(r => r.linkedSkill ? [r.linkedSkill.idSha256] : [])).size === after.canonicalRows.filter(r => r.linkedSkill).length;
  return { at: new Date().toISOString(), schemaVersion: 1, kind: 'comparison', baselineSha256: sha(before), readbackSha256: sha(after),
    protectedOldRowsPreserved: oldPreserved, newRowsAllDistinct: itemChecks.every(i=>i.distinctCanonicalRow),
    qualifiedLabelsPreserved: itemChecks.every(i=>i.durableQualifiedLabel), publicationIdentitySafe: itemChecks.every(i=>i.publicationSafe) && noDuplicateNewLinks,
    intakeSettled: itemChecks.every(i=>i.sourceSettled), publicationComplete: itemChecks.every(i=>i.publishedWithVersion || i.terminalRejected),
    published: itemChecks.filter(i=>i.publishedWithVersion).length, terminalRejected: itemChecks.filter(i=>i.terminalRejected).length,
    processingOrMissing: itemChecks.filter(i=>!i.publishedWithVersion && !i.terminalRejected).length,
    oldChecks, itemChecks, rawIdentitiesExported: false, completeSweepProven: false,
    limitation: 'Requires root deployment, final-version natural HTTP and required-CI receipts separately. Intake settlement is not complete publication or corpus coverage. Historical error counters are not reset.' };
}
const tupleExpr = `encode(sha256(convert_to(jsonb_build_array(s."sourceType"::text,s."sourceId",s."artifactPath")::text,'UTF8')),'hex')`;
const idExpr = `encode(sha256(convert_to(s.id,'UTF8')),'hex')`;
const SELECT = `SELECT s.id,s."repoUrl",s."skillName",s."skillPath",s."sourceType",s."sourceId",s."artifactPath",s."userId",s."skillId",s.state,${tupleExpr} AS "tupleHash",
 CASE WHEN k.id IS NULL THEN NULL ELSE jsonb_build_object('id',k.id,'name',k.name,'displayName',k."displayName",'repoUrl',k."repoUrl",'skillPath',k."skillPath",'ownerSlug',k."ownerSlug",'repoSlug',k."repoSlug",'skillSlug',k."skillSlug",'legacySlug',k."legacySlug",'privacy',k.privacy,'tenantId',k."tenantId",'repositoryId',k."repositoryId") END AS skill,
 repo.url AS "repositoryUrl", COALESCE((SELECT jsonb_agg(jsonb_build_object('id',v.id,'skillId',v."skillId")) FROM "SkillVersion" v WHERE v."skillId"=k.id),'[]'::jsonb) AS versions
 FROM "Submission" s LEFT JOIN "Skill" k ON k.id=s."skillId" LEFT JOIN "Repository" repo ON repo.id=k."repositoryId"`;
function remoteRead(rawItems) {
  const remote = `import json,subprocess
names=['scanner-worker-crawl-worker-1','scanner-worker-scanner-worker-1']
expected=['0c47dfee262668ab608c461e16896f76f2582aa12ce7df6a943f11d553f8db0a','2633c121f4f10ed37a6a23f0b7b762a228ab6bd3d12d2a149c30f2b79e8919ff']
cs=[]
for n,e in zip(names,expected):
 c=json.loads(subprocess.check_output(['docker','inspect',n]))[0]
 if c['Id']!=e or not c['State']['Running'] or c['State']['Paused']:raise SystemExit('container_identity_guard')
 cs.append({'id':c['Id'],'image':c['Image'],'restartCount':c['RestartCount']})
s=${JSON.stringify(`const f=require('fs'),c=require('crypto'),sha=x=>c.createHash('sha256').update(x).digest('hex'),x=JSON.parse(f.readFileSync('/tmp/crawl-state/github-sharded.json')),a=new Set(x.acceptedKeys||[]),p=x.pendingPage,key=r=>r.fullName+':'+r.skillPath;const u=(p?.repos||[]).filter(r=>!a.has(key(r)));console.log(JSON.stringify({sweepId:x.sweepId,schemaVersion:x.schemaVersion,shardIndex:x.shardIndex,page:x.page,phase:x.phase,pendingPageSha256:p?sha(JSON.stringify(p)):null,unresolvedHashes:u.map(r=>sha(key(r))).sort(),acceptedHashes:[...a].map(sha).sort(),totalLost:x.counters?.totalLost,totalErrors:x.counters?.totalErrors,${rawItems ? 'items:u' : 'rawIdentitiesExported:false'}}));`)}
x=json.loads(subprocess.check_output(['docker','exec',names[0],'node','-e',s],text=True));x['containers']=cs;print(json.dumps(x))
`;
  const out = cp.execFileSync('ssh', ['-oBatchMode=yes','-oConnectTimeout=10','root@5.161.56.136','python3 -'], {input:remote,encoding:'utf8',timeout:25000,maxBuffer:2*1024*1024,cwd:'/Users/antonabyzov/Projects/sw-easychamp',stdio:['pipe','pipe','pipe']});
  const x = JSON.parse(out);
  if (x.schemaVersion !== 2 || x.sweepId !== '026ba568-3ac5-4855-95fd-6c441c8007d2' || !Number.isSafeInteger(x.page) || !Number.isSafeInteger(x.shardIndex)) throw Error('checkpoint_guard');
  return x;
}
async function collect(mode, before) {
  const checkpoint = remoteRead(mode === 'baseline');
  const expected = JSON.parse(fs.readFileSync(BASE+'t030-pending-scope-read.json'));
  if (mode === 'baseline' && (checkpoint.pendingPageSha256 !== expected.pendingPageSha256 || JSON.stringify(checkpoint.unresolvedHashes) !== JSON.stringify(expected.items.map(i=>i.itemIdentitySha256).sort()))) throw Error('pending_identity_guard');
  const raw = fs.readFileSync('/Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/vskill-platform/.env.local','utf8');
  const uri = raw.match(/^\s*(?:export\s+)?DATABASE_URL\s*=\s*(.+)$/m)?.[1]?.trim().replace(/^['"]|['"]$/g,'');
  const u = new URL(uri);
  if (u.hostname !== '178.156.163.74' || u.pathname !== '/vskill_platform') throw Error('database_identity_guard');
  const req = createRequire('/Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/0874-vm-observations/package.json');
  const {Client}=req('pg'); const c=new Client({connectionString:uri,connectionTimeoutMillis:8000,query_timeout:20000,application_name:'codex-0874-distinct-artifact-proof-readonly'});
  await c.connect();
  try {
    await c.query('BEGIN TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY');
    await c.query("SET LOCAL statement_timeout='15s'");
    const guard = await c.query("SELECT current_setting('transaction_read_only') AS ro, current_database() AS db");
    if (guard.rows[0]?.ro !== 'on' || guard.rows[0]?.db !== 'vskill_platform') throw Error('readonly_guard');
    const query = async (where, values, max) => {
      const r = await c.query(SELECT+' WHERE '+where+' LIMIT '+(max+1), values);
      if (r.rows.length > max || r.rows.some(r=>r.versions.length>1000)) throw Error('row_budget_guard');
      return r.rows.map(project);
    };
    let items=[],oldRows=[],canonicalRows=[];
    if(mode==='baseline') {
      for (const item of checkpoint.items) {
        if(typeof item.fullName!=='string'||typeof item.skillName!=='string'||typeof item.repoUrl!=='string'||typeof item.skillPath!=='string') throw Error('item_shape_guard');
        const ids=await c.query('SELECT "repoId" FROM "repo_identities" WHERE "fullName"=$1 LIMIT 2',[item.fullName.toLowerCase()]);
        if(ids.rowCount!==1||!ids.rows[0].repoId)throw Error('source_identity_guard');
        const sourceId=String(ids.rows[0].repoId), path=artifact(item.skillPath);
        const digest=await c.query(`SELECT encode(sha256(convert_to(jsonb_build_array('github'::text,$1::text,$2::text)::text,'UTF8')),'hex') AS h`,[sourceId,path]);
        const rows=await query('s."repoUrl"=$1 AND s."skillName"=$2',[item.repoUrl,item.skillName],1);
        const current=await query('s."sourceType"=\'github\' AND s."sourceId"=$1 AND s."artifactPath"=$2',[sourceId,path],1);
        if(rows.length!==1||current.length!==0||!rows[0].pathConsistent||rows[0].userOwned||rows[0].linkedSkill&&(!rows[0].linkedSkill.publicTenantless||!rows[0].linkedSkill.pathMatches||!rows[0].linkedSkill.repoMatches))throw Error('baseline_changed');
        items.push({itemIdentitySha256:sha(item.fullName+':'+item.skillPath),tupleSha256:digest.rows[0].h,qualifiedLabelSha256:sha(item.skillName+' ('+path+')'),oldRowIdSha256:rows[0].rowIdSha256});
        oldRows.push(rows[0]);
      }
      oldRows=[...new Map(oldRows.map(r=>[r.rowIdSha256,r])).values()];
      if(items.length!==22||oldRows.length!==10)throw Error('baseline_cardinality');
    } else {
      if(before.kind!=='baseline'||before.items.length!==22||before.oldRows.length!==10||[...before.items.map(i=>i.tupleSha256),...before.oldRows.map(r=>r.rowIdSha256)].some(x=>!HASH.test(x)))throw Error('baseline_input_guard');
      oldRows=await query(idExpr+'=ANY($1::text[])',[before.oldRows.map(r=>r.rowIdSha256)],10);
      canonicalRows=await query(tupleExpr+'=ANY($1::text[])',[before.items.map(i=>i.tupleSha256)],22);
    }
    await c.query('ROLLBACK');
    delete checkpoint.items;
    const result={schemaVersion:1,kind:mode,at:new Date().toISOString(),readOnlyTransaction:true,rawIdentitiesExported:false,checkpoint,oldRows,canonicalRows};
    if(mode==='baseline') {
      result.items=items;
      result.summary={pendingItems:22,oldSubmissionRows:oldRows.length,linkedItemMatches:items.filter(i=>oldRows.find(r=>r.rowIdSha256===i.oldRowIdSha256)?.linkedSkill).length,distinctOldLinkedSkills:new Set(oldRows.flatMap(r=>r.linkedSkill?[r.linkedSkill.idSha256]:[])).size};
    } else result.baselineSha256=sha(before);
    return result;
  } finally { await c.end().catch(()=>{}); }
}
function writeNew(path,result){fs.writeFileSync(path,JSON.stringify(result,null,2)+'\n',{flag:'wx',mode:0o600});}
module.exports={compare,project,sha,artifact,repo};
if(require.main===module)(async()=>{try{
 const [mode,input,output]=process.argv.slice(2);let result;
 if(mode==='--baseline')result=await collect('baseline');
 else if(mode==='--readback')result=await collect('readback',JSON.parse(fs.readFileSync(input)));
 else if(mode==='--compare'){const afterPath=output,outputPath=process.argv[5];result=compare(JSON.parse(fs.readFileSync(input)),JSON.parse(fs.readFileSync(afterPath)));writeNew(outputPath,result);console.log(JSON.stringify({mode,output:outputPath,intakeSettled:result.intakeSettled,protectedOldRowsPreserved:result.protectedOldRowsPreserved,publicationComplete:result.publicationComplete}));return;}
 else throw Error('usage_guard');
 const path=mode==='--baseline'?input:output;writeNew(path,result);console.log(JSON.stringify({mode,output:path,sha256:sha(result),summary:result.summary,canonicalRows:result.canonicalRows.length}));
 }catch(e){console.log(JSON.stringify({failed:true,errorClass:/^[a-z_]+$/.test(e.message)?e.message:e.name,errorCode:/^[A-Z0-9_]+$/.test(String(e.code))?e.code:null,rawErrorExported:false}));process.exitCode=1;}})();
