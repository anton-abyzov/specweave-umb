import assert from 'node:assert/strict';
import {createRequire} from 'node:module';
import {writeFileSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
const require=createRequire('/Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specweave/package.json');
const {chromium}=require('playwright');
const browser=await chromium.launch({headless:true,channel:'chrome'});
try{
 const page=await browser.newPage({viewport:{width:1440,height:1000},reducedMotion:'reduce'});
 await page.route('**/*',route=>['spec-weave.com','www.spec-weave.com'].includes(new URL(route.request().url()).hostname)?route.continue():route.abort());
 const results=[];
 for(const [path,name] of [['/code/','live-landing'],['/code/download/','live-download']]){
  const response=await page.goto('https://spec-weave.com'+path,{waitUntil:'networkidle'});
  assert.equal(response.status(),200);
  const text=await page.locator('body').innerText();
  assert.doesNotMatch(text,/independent MIT fork|SpecWithCode is free and open source/i);
  assert.match(await page.locator('meta[property="og:image:alt"]').getAttribute('content'),/Free, source available/);
  const json=await page.locator('script[type="application/ld+json"]').allTextContents();
  const apps=json.flatMap(x=>{const d=JSON.parse(x);return d['@graph']??[d]}).filter(x=>x['@type']==='SoftwareApplication'&&x.name==='SpecWithCode');
  assert.equal(apps.length,1);assert.equal(apps[0].license,undefined);
  await page.screenshot({path:fileURLToPath(new URL(name+'.png',import.meta.url)),fullPage:true});
  results.push({url:page.url(),status:response.status(),licenseAbsent:true});
 }
 if(process.argv.includes('--guides')){
  const paths=['/docs/guides/claude-code-vs-codex/','/docs/guides/claude-code-usage-limit/','/docs/guides/switch-claude-code-to-codex/','/docs/compare/specwithcode-vs-opencode-t3-code/'];
  for(const path of paths){
   const response=await page.goto('https://spec-weave.com'+path,{waitUntil:'networkidle'});assert.equal(response.status(),200);
   const text=await page.locator('body').innerText();assert.doesNotMatch(text,/SpecWithCode is a free, open-source Mac app/);assert.match(text,/source available for inspection/);
   if(path.includes('specwithcode-vs')){const row=page.getByRole('row').filter({hasText:'Price and license'});assert.match(await row.locator('td').nth(1).innerText(),/no new project-wide license grant/);}
   results.push({url:page.url(),status:response.status(),correctSourceTerms:true});
  }
 }
 writeFileSync(new URL('./live-site-verification.json',import.meta.url),JSON.stringify({headless:true,results},null,2)+'\n');
 console.log(JSON.stringify(results));
}finally{await browser.close();}
