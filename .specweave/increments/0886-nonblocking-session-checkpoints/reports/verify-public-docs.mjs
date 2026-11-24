import { createServer } from 'node:http';
import { readFile, stat, writeFile, mkdir } from 'node:fs/promises';
import { join, extname, resolve } from 'node:path';
import { createRequire } from 'node:module';
import assert from 'node:assert/strict';
const repo=resolve(process.env.SPECWEAVE_DOCS_ROOT??process.cwd());
const require=createRequire(join(repo,'docs-site/package.json'));
const {chromium}=require('@playwright/test');
const publicMode=process.argv.includes('--public');
const proofRoot=process.env.SPECWEAVE_DOCS_PROOF_DIR??'/tmp/specweave-0886-docs-panel';
const out=join(proofRoot,publicMode?'public':'local');
await mkdir(out,{recursive:true});
let server;
let base='https://spec-weave.com';
if(!publicMode){
 const dir=join(repo,'docs-site/build');
 const types={'.html':'text/html','.js':'text/javascript','.css':'text/css','.svg':'image/svg+xml','.png':'image/png','.woff2':'font/woff2','.json':'application/json'};
 server=createServer(async(req,res)=>{try{let path=resolve(dir,'.'+decodeURIComponent(new URL(req.url,'http://localhost').pathname)); if(!path.startsWith(dir)) throw new Error('invalid path'); if((await stat(path)).isDirectory())path=join(path,'index.html'); const data=await readFile(path);res.writeHead(200,{'content-type':types[extname(path)]??'application/octet-stream'});res.end(data);}catch{res.writeHead(404);res.end('Not found');}});
 await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));base=`http://127.0.0.1:${server.address().port}`;
}
const report={at:new Date().toISOString(),headless:true,base,node:process.version,cases:[],pricingCases:[],pageErrors:[],screenshots:[]};
let browser;
try{
 browser=await chromium.launch({headless:true});
 const settings=[...([1440,390,320].flatMap(width=>['light','dark'].map(theme=>({width,theme,motion:'no-preference'})))),...(['light','dark'].map(theme=>({width:1440,theme,motion:'reduce'})))];
 for(const {width,theme,motion}of settings){
  const context=await browser.newContext({viewport:{width,height:900},colorScheme:theme,reducedMotion:motion});
  await context.addInitScript(t=>localStorage.setItem('theme',t),theme);
  const page=await context.newPage();page.on('pageerror',e=>report.pageErrors.push(e.message));
  const response=await page.goto(base+'/',{waitUntil:'networkidle',timeout:30000});assert.equal(response.status(),200);
  for(const [index,beat]of ['spec','task','handoff','pickup'].entries()){
   const step=page.locator(`#how li[data-step="${index}"]`);
   await step.locator(':scope > p').scrollIntoViewIfNeeded();
   await page.waitForFunction(i=>Number(getComputedStyle(document.querySelector(`#how li[data-step="${i}"]`)).opacity)>.99,index);
   const artSelector=width>=1000?`#how div[aria-hidden="true"] [data-beat="${beat}"]`:`#how li[data-step="${index}"] [data-beat="${beat}"]`;
   if(width<1000)await page.locator(artSelector).scrollIntoViewIfNeeded();
   await page.waitForFunction(selector=>{
    const art=document.querySelector(selector);const panel=art?.parentElement?.parentElement;
    if(!art||!panel)return false;const r=panel.getBoundingClientRect();
    return Number(getComputedStyle(panel).opacity)>.99&&getComputedStyle(panel).display!=='none'&&r.width>0&&r.height>0&&(innerWidth<1000||getComputedStyle(panel).transform==='none');
   },artSelector);
   await page.waitForFunction(selector=>[...document.querySelectorAll(selector+' img')].every(img=>img.complete&&img.naturalWidth>0),artSelector);
   const state=await page.evaluate(selector=>{
    const art=document.querySelector(selector),panel=art.parentElement.parentElement,r=panel.getBoundingClientRect();
    return{opacity:Number(getComputedStyle(panel).opacity),transform:getComputedStyle(panel).transform,panelWidth:r.width,panelHeight:r.height,panelInViewport:r.bottom>60&&r.top<innerHeight,viewport:innerWidth,documentWidth:document.documentElement.scrollWidth,theme:document.documentElement.getAttribute('data-theme')};
   },artSelector);
   assert.equal(state.theme,theme);assert.ok(state.documentWidth<=width+1,`overflow ${JSON.stringify(state)}`);assert.ok(state.panelInViewport);assert.ok(state.opacity>.99);
   if(width>=1000)assert.equal(state.transform,'none');
   report.cases.push({width,theme,motion,beat,...state});
   if(beat==='handoff'&&width!==320){const shot=`${out}/landing-${width}-${theme}-${motion}.png`;await page.screenshot({path:shot});report.screenshots.push(shot);}
  }
  if(motion==='no-preference'){
   const response=await page.goto(base+'/pricing/',{waitUntil:'networkidle'});assert.equal(response.status(),200);
   const faq=page.getByText('What gets saved automatically?',{exact:true});await faq.click();
   assert.match(await page.locator('body').innerText(),/pickup does not apply automatic checkpoints/);
   const size=await page.evaluate(()=>({viewport:innerWidth,documentWidth:document.documentElement.scrollWidth}));assert.ok(size.documentWidth<=width+1);
   report.pricingCases.push({width,theme,...size,faqExpanded:true});
   if(width!==320){await faq.scrollIntoViewIfNeeded();const shot=`${out}/pricing-${width}-${theme}.png`;await page.screenshot({path:shot});report.screenshots.push(shot);}
  }
  await context.close();
 }
 assert.deepEqual(report.pageErrors,[]);report.ok=true;
}catch(error){report.ok=false;report.error=error.stack;throw error;}
finally{
 if(browser)await browser.close();if(server)await new Promise(resolve=>server.close(resolve));
 await writeFile(`${out}/report.json`,JSON.stringify(report,null,2)+'\n');
 console.log(JSON.stringify({ok:report.ok,base,cases:report.cases.length,pricingCases:report.pricingCases.length,pageErrors:report.pageErrors,screenshots:report.screenshots,error:report.error},null,2));
}
