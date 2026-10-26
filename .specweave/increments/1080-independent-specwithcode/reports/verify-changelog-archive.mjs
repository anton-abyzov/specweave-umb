import assert from 'node:assert/strict';
import {execFileSync} from 'node:child_process';
import {readFileSync,readdirSync,writeFileSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
const root=fileURLToPath(new URL('../../../../repositories/anton-abyzov/specweave/',import.meta.url));
const base='3b517233a09c3f5b02264c2b76306b1d8b3aa47c';
const original=execFileSync('git',['show',`${base}:CHANGELOG.md`],{cwd:root,encoding:'utf8'});
const current=readFileSync(`${root}/CHANGELOG.md`,'utf8');
const marker='\n<!-- historical-release-index -->\n';
assert.equal(current.split(marker).length,2);
const names=readdirSync(`${root}/changelog`).filter(x=>/^archive-\d+\.md$/.test(x)).sort();
assert.equal(names.length,3);
const texts=names.map(x=>readFileSync(`${root}/changelog/${x}`,'utf8'));
let relativeLinks=0;
const restored=texts.map((text,i)=>text.replace(/\]\(\.\.\/([^)]+)\)/g,(match,target)=>{
 relativeLinks++;
 const baseUrl='https://github.com/anton-abyzov/specweave/blob/develop/';
 assert.equal(new URL('../'+target,baseUrl+'changelog/'+names[i]).href,new URL(target,baseUrl+'CHANGELOG.md').href);
 return ']('+target+')';
}));
assert.equal(current.split(marker)[0]+restored.join(''),original,'historical text must survive except rebased relative link destinations');
assert.equal(relativeLinks,7);
for(const [name,text] of [['CHANGELOG.md',current],...names.map((name,i)=>[name,texts[i]])]){
 assert.ok(text.split('\n').length<=1500,`${name} exceeds file limit`);
}
assert.match(current,/## \[3\.0\.0\] - 2026-09-25/,'README version anchor remains available');
for(const name of names)assert.ok(current.includes(`](changelog/${name})`));
const report={base,exactHistoricalReconstructionAfterLinkRebasing:true,relativeLinksPreserved:relativeLinks,rootLines:current.trimEnd().split('\n').length,archives:names.map((name,i)=>({name,lines:texts[i].trimEnd().split('\n').length})),readmeAnchorPreserved:true};
writeFileSync(new URL('./changelog-archive-verification.json',import.meta.url),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify(report));
