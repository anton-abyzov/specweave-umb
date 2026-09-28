// Read-only comparison of hashed runtime discovery identities with new durable intake.
import fs from 'node:fs';
import { createHash } from 'node:crypto';
import { createRequire } from 'node:module';
import { execFileSync } from 'node:child_process';
const require=createRequire('/Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/0874-adaptive-resume/package.json');
const { Client }=require('pg');
const sha=x=>createHash('sha256').update(x).digest('hex');
const js=`const fs=require('fs'),crypto=require('crypto');
const p=(process.env.CRAWL_STATE_DIR||'/tmp/crawl-state')+'/github-sharded.json';
const s=JSON.parse(fs.readFileSync(p,'utf8'));
if(s.schemaVersion!==2)throw Error('Expected adaptive schema2');
const sha=x=>crypto.createHash('sha256').update(x).digest('hex');
console.log(JSON.stringify({sweepId:s.sweepId,startedAt:s.startedAt,configSignature:s.configSignature,
distinctDiscoveredLowerBound:s.distinctKeys.length,distinctCountExact:!s.distinctCountSaturated,
distinctKeysSha256:sha(JSON.stringify([...s.distinctKeys].sort())),
identityHashes:s.distinctKeys.map(sha),counters:s.counters}));`;
let client;
try {
 const observed=JSON.parse(execFileSync('ssh',['-o','BatchMode=yes','-o','ConnectTimeout=10','root@5.161.56.136','docker exec -i scanner-worker-crawl-worker-1 node'],{input:js,encoding:'utf8',maxBuffer:5*1024*1024}));
 const identities=new Set(observed.identityHashes); delete observed.identityHashes;
 const raw=fs.readFileSync('/Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/vskill-platform/.env.local','utf8');
 const connectionString=raw.match(/^\s*(?:export\s+)?DATABASE_URL\s*=\s*(.+)$/m)?.[1]?.trim().replace(/^['"]|['"]$/g,'');
 const url=new URL(connectionString);
 if(url.hostname!=='178.156.163.74'||url.pathname!=='/vskill_platform')throw Error('Database identity differs');
 client=new Client({connectionString,connectionTimeoutMillis:8000,application_name:'codex-0874-adaptive-readonly'});
 await client.connect(); await client.query('BEGIN READ ONLY'); await client.query("SET LOCAL statement_timeout='15s'");
 const rows=(await client.query(`SELECT s.id,s."repoUrl",s."skillPath",s.state,s."createdAt",s."sourceId",s."artifactPath",s."skillId",k.privacy,k."tenantId",k."createdAt" AS "skillCreatedAt" FROM "Submission" s LEFT JOIN "Skill" k ON k.id=s."skillId" WHERE s."createdAt">=$1 ORDER BY s."createdAt" LIMIT 20000`,[observed.startedAt])).rows;
 const matches=rows.filter(row=>{
   const fullName=/github\.com\/([^/\s]+)\/([^/\s#?]+)/i.exec(row.repoUrl);
   if(!fullName)return false;
   return identities.has(sha(`repo:${fullName[1].toLowerCase()}/${fullName[2].replace(/\.git$/i,'').toLowerCase()}:${row.skillPath||'SKILL.md'}`));
 });
 const states={}; for(const row of matches)states[row.state]=(states[row.state]||0)+1;
 const proof={at:new Date().toISOString(),transaction:'READ ONLY',database:{host:url.hostname,database:url.pathname.slice(1)},observed,
   attribution:'Exact hashed repo/path intersection with the live VM3 sweep and creation time after sweep start; other fleet sources can concurrently discover the same identity.',
   recentRowsExamined:rows.length,recentQuerySaturated:rows.length===20000,matchingNewSubmissions:matches.length,states,
   matchingKeyedSubmissions:matches.filter(x=>x.sourceId!==null&&x.artifactPath!==null).length,
   matchingPublishedPublicSkills:matches.filter(x=>x.skillId&&x.privacy==='PUBLIC'&&x.tenantId===null).length,
   examples:matches.slice(0,20).map(x=>({submissionIdSha256:sha(x.id),state:x.state,createdAt:x.createdAt,keyed:x.sourceId!==null&&x.artifactPath!==null,publicSkill:Boolean(x.skillId&&x.privacy==='PUBLIC'&&x.tenantId===null)}))};
 await client.query('ROLLBACK');
 console.log(JSON.stringify(proof,null,2));
} catch(error) { console.error('Read-only adaptive intake verification failed:',error.code??error.name); process.exitCode=1; }
finally { if(client)await client.end(); }
