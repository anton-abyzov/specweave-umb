// Optional exact canonical-row readback. No database statement can write.
const fs=require('fs'),crypto=require('crypto'),{createRequire}=require('module');
const req=createRequire('/Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/0874-intake-identity/package.json');
const {Client}=req('pg'),sha=x=>crypto.createHash('sha256').update(String(x)).digest('hex');
const expected={row:'7821b066b63a6920b563d8c2cc71461e231b2c4a6f1531991a487de29075de02',source:'85136bf1b8ddbdba05226c47bdf77d114d6633d9a735f173d4dd74506f9e6d59',artifact:'c101124f447dbba36b8258c2cb8c8e45e7965015df5fd95453766076ec9684d7'};
(async()=>{let c;try{
 const raw=fs.readFileSync('/Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/vskill-platform/.env.local','utf8');
 const uri=raw.match(/^\s*(?:export\s+)?DATABASE_URL\s*=\s*(.+)$/m)?.[1]?.trim().replace(/^['"]|['"]$/g,'');const u=new URL(uri);
 if(u.hostname!=='178.156.163.74'||u.pathname!=='/vskill_platform')throw Error('database_identity_guard');
 c=new Client({connectionString:uri,connectionTimeoutMillis:8000,query_timeout:15000,application_name:'codex-0874-natural-row-readonly'});await c.connect();
 await c.query('BEGIN TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY');await c.query("SET LOCAL statement_timeout='15s'");
 const q=await c.query(`SELECT s.id,s.state,s."userId",s."skillId",k.privacy,k."tenantId" FROM "Submission" s LEFT JOIN "Skill" k ON k.id=s."skillId" WHERE s."sourceType"='github' AND encode(sha256(convert_to(s."sourceId",'UTF8')),'hex')=$1 AND encode(sha256(convert_to(s."artifactPath",'UTF8')),'hex')=$2 LIMIT 2`,[expected.source,expected.artifact]);
 await c.query('ROLLBACK');const rows=q.rows.map(x=>({rowIdSha256:sha(x.id),sameOriginalRow:sha(x.id)===expected.row,state:x.state,userIdPresent:x.userId!==null,linkedSkillPresent:x.skillId!==null,linkedSkillPublic:x.privacy==='PUBLIC',linkedSkillTenantPresent:x.tenantId!==null}));
 const verified=rows.length===1&&rows[0].sameOriginalRow&&rows[0].linkedSkillPublic&&!rows[0].linkedSkillTenantPresent;
 console.log(JSON.stringify({at:new Date().toISOString(),readOnlyTransaction:true,sourceIdSha256:expected.source,artifactPathSha256:expected.artifact,matchingRows:rows.length,rows,canonicalRowAndPublicScopePreserved:verified,limitation:'Separate from scheduler acceptance; lifecycle state may change through normal existing rescan policy.'},null,2));if(!verified)process.exitCode=2;
 }catch(e){console.log(JSON.stringify({readFailed:true,errorCode:/^[A-Z0-9_]+$/.test(String(e.code))?e.code:null,errorClass:e.message==='database_identity_guard'?e.message:e.name}));process.exitCode=1;}finally{if(c)await c.end().catch(()=>{});}})();
