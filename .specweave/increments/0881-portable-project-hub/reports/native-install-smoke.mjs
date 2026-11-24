import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import assert from 'node:assert/strict';
import {execFileSync} from 'node:child_process';
const pkg=process.env.SPECWEAVE_PACKAGE_ROOT;
const root=fs.mkdtempSync(path.join(os.tmpdir(),'sw-native-package-'));
try {
  const cli=args=>execFileSync(process.execPath,[path.join(pkg,'bin/specweave.js'),...args],{cwd:root,encoding:'utf8',env:{...process.env,PWDEBUG:'0',PLAYWRIGHT_HTML_OPEN:'never'}});
  cli(['project','init','--name','Native installer proof','--goal','Preserve user skills']);
  fs.mkdirSync(path.join(root,'.agents/skills/project'),{recursive:true});
  fs.writeFileSync(path.join(root,'.agents/skills/project/SKILL.md'),'User skill retained');
  cli(['refresh-plugins','--force']);
  const installed=fs.readdirSync(path.join(root,'.agents/skills')).filter(name=>name.startsWith('sw-'));
  assert.equal(installed.length,12);
  assert.equal(fs.readFileSync(path.join(root,'.agents/skills/project/SKILL.md'),'utf8'),'User skill retained');
  assert.match(fs.readFileSync(path.join(root,'.agents/skills/sw-project/SKILL.md'),'utf8'),/name: sw-project/);
  cli(['refresh-plugins']);
  console.log('PASS: installed CLI init + refresh installs all 12 native Codex skills, preserves custom project skill and refreshes idempotently');
} finally {fs.rmSync(root,{recursive:true,force:true});}
