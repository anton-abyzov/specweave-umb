import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {spawnSync} from 'node:child_process';
const bin=process.argv[2];
assert.ok(bin && fs.existsSync(bin));
const temp=fs.mkdtempSync(path.join(os.tmpdir(),'specweave-installed-proof-'));
const results=[];
function cli(cwd,args,expected){
 const start=Date.now();
 const r=spawnSync(bin,args,{cwd,encoding:'utf8',timeout:15000,env:{...process.env,PWDEBUG:'0',PLAYWRIGHT_HTML_OPEN:'never'}});
 assert.ifError(r.error);assert.equal(r.status,expected,r.stdout+r.stderr);
 results.push({cwd,args,exit:r.status,elapsedMs:Date.now()-start,output:(r.stdout+r.stderr).trim()});
 return r.stdout+r.stderr;
}
try {
 assert.equal(cli(temp,['--version'],0).trim(),'2.3.0');
 const bare=path.join(temp,'bare');const external=path.join(temp,'external');
 fs.mkdirSync(bare);fs.mkdirSync(external);
 fs.writeFileSync(path.join(external,'skills-lock.json'),'preserve-external');
 fs.symlinkSync(external,path.join(bare,'escape'));
 fs.symlinkSync('/System/Library',path.join(bare,'system-escape'));
 fs.writeFileSync(path.join(bare,'skills-lock.json'),'preserve-local');
 const old=new Date(Date.now()-60000);
 for(const p of [path.join(bare,'skills-lock.json'),path.join(external,'skills-lock.json')])fs.utimesSync(p,old,old);
 for(const hasBareDirectory of [false,true]){
  if(hasBareDirectory)fs.mkdirSync(path.join(bare,'.specweave'));
  const before=fs.readdirSync(bare).sort();
  assert.match(cli(bare,['refresh-plugins'],1),/No SpecWeave project found/);
  assert.equal(cli(bare,['refresh-plugins','--quiet'],1),'');
  assert.deepEqual(fs.readdirSync(bare).sort(),before);
  assert.equal(fs.readFileSync(path.join(bare,'skills-lock.json'),'utf8'),'preserve-local');
  assert.equal(fs.readFileSync(path.join(external,'skills-lock.json'),'utf8'),'preserve-external');
 }
 const project='/Users/antonabyzov/Projects/github/specweave-umb';
 for(const cwd of (process.argv.includes('--no-project-refresh') ? [] : [project,path.join(project,'repositories/anton-abyzov/specweave')]))assert.match(cli(cwd,['refresh-plugins'],0),/sw: (active|installed)/);
 const receipt={verifiedAt:new Date().toISOString(),bin,resolvedBin:fs.realpathSync(bin),results,noProjectWrites:true,localAndSymlinkTargetLocksPreserved:true,status:'PASS'};
 fs.writeFileSync('/tmp/specweave-installed-refresh-proof.json',JSON.stringify(receipt,null,2)+'\n');
 console.log(JSON.stringify(receipt,null,2));
} finally{fs.rmSync(temp,{recursive:true,force:true});}
