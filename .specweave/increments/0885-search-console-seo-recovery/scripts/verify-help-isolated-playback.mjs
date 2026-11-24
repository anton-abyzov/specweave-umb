import { chromium } from '/tmp/easychamp-seo-inventory-landing-20261007/node_modules/playwright/index.mjs';
import { writeFile } from 'node:fs/promises';
import assert from 'node:assert/strict';
const base=process.env.HELP_VERIFY_BASE??'http://localhost:3941';const width=Number(process.env.HELP_VERIFY_WIDTH??320);
const label=base.startsWith('http://localhost')?'local':'public';
const safeUrl=url=>{const u=new URL(url);return `${u.origin}${u.pathname}`;};
const browser=await chromium.launch({headless:true});
const receipt={checkedAt:new Date().toISOString(),headless:true,width,base,errors:[],requests:[],responses:[]};
try{
 const context=await browser.newContext({viewport:{width,height:844},isMobile:true,hasTouch:true});const page=await context.newPage();
 page.on('pageerror',error=>receipt.errors.push(String(error)));
 page.on('requestfailed',request=>{if(/youtube|googlevideo|ytimg/.test(request.url()))receipt.requests.push({url:safeUrl(request.url()),failure:request.failure()});});
 page.on('response',response=>{if(response.status()>=400&&/youtube|googlevideo|ytimg/.test(response.url()))receipt.responses.push({url:safeUrl(response.url()),status:response.status()});});
 await page.goto(`${base}/help/league-console/create-league-or-tournament`,{waitUntil:'networkidle'});
 const player=page.locator('iframe[src*="aHjrZktaWIU"]');await player.scrollIntoViewIfNeeded();
 const frame=await (await player.elementHandle()).contentFrame();
 await frame.getByRole('button',{name:'Play video',exact:true}).waitFor({state:'visible'});
 receipt.before=await frame.locator('video').evaluate(v=>({time:v.currentTime,paused:v.paused,readyState:v.readyState}));
 assert.equal(receipt.before.time,0);assert.equal(receipt.before.paused,true);
 await frame.getByRole('button',{name:'Play video',exact:true}).click();
 await frame.waitForFunction(()=>{const v=document.querySelector('video');return v&&!v.paused&&v.currentTime>1;},null,{timeout:30000});
 receipt.after=await frame.locator('video').evaluate(v=>({time:v.currentTime,paused:v.paused,readyState:v.readyState,duration:v.duration}));
 receipt.status='passed';await page.screenshot({path:`/tmp/easychamp-seo-audit-20261007/help-isolated-playback-${label}-${width}.png`});
}catch(error){receipt.status='failed';receipt.error=String(error);process.exitCode=1;}
finally{await browser.close();await writeFile(`/tmp/easychamp-seo-audit-20261007/help-isolated-playback-${label}-${width}.json`,JSON.stringify(receipt,null,2));}
console.log(JSON.stringify(receipt));
