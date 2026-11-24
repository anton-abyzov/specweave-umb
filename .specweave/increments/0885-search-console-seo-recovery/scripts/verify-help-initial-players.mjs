import { chromium } from '/tmp/easychamp-seo-inventory-landing-20261007/node_modules/playwright/index.mjs';
import { JSDOM } from '/tmp/easychamp-seo-inventory-landing-20261007/node_modules/jsdom/lib/api.js';
import { readFile, writeFile } from 'node:fs/promises';
import assert from 'node:assert/strict';

const directory='/tmp/easychamp-seo-audit-20261007';
const base=process.env.HELP_VERIFY_BASE ?? 'http://localhost:3941';
const label=(base.startsWith('http://localhost')?'local':'public')+(process.env.HELP_VERIFY_SUFFIX?`-${process.env.HELP_VERIFY_SUFFIX}`:'');
const prior=JSON.parse(await readFile(`${directory}/help-all-raw-html-video-proof.json`,'utf8'));
const paths=prior.rows.filter(r=>r.rawHtmlVideoCount).map(r=>new URL(r.url).pathname);
const receipt={checkedAt:new Date().toISOString(),base,headless:true,rawHtml:[],geometry:[],playback:[]};
function nodesIn(document){
  const nodes=[];
  const visit=n=>{if(Array.isArray(n))return n.forEach(visit);if(n&&typeof n==='object'){if(n['@type'])nodes.push(n);Object.values(n).forEach(visit);}};
  document.querySelectorAll('script[type="application/ld+json"]').forEach(s=>visit(JSON.parse(s.textContent)));
  return nodes;
}
const frameBase=source=>{const url=new URL(source);return `${url.origin}${url.pathname}`;};
const browser=await chromium.launch({headless:true});
try{
  for(const path of paths){
    const response=await fetch(`${base}${path}`);
    const html=await response.text();
    const document=new JSDOM(html).window.document;
    const videos=nodesIn(document).filter(n=>n['@type']==='VideoObject');
    const frames=Array.from(document.querySelectorAll('iframe[src*="youtube-nocookie.com/embed/"]'));
    assert.equal(response.status,200,path);
    for(const video of videos){
      const matches=frames.filter(frame=>frameBase(frame.src)===video.embedUrl);
      assert.equal(matches.length,1,`${path}: ${video.embedUrl}`);
      const frame=matches[0];
      assert.ok(frame.title.trim());assert.equal(frame.getAttribute('loading'),'lazy');
      assert.notEqual(new URL(frame.src).searchParams.get('autoplay'),'1');
      assert.ok(!frame.getAttribute('allow').includes('autoplay'));
      assert.ok(Number(frame.width)>0&&Number(frame.height)>0);
      assert.ok(frame.parentElement.style.aspectRatio);
      assert.ok(!frame.parentElement.querySelector('button'));
    }
    receipt.rawHtml.push({path,httpStatus:response.status,videoObjects:videos.length,iframes:frames.length,frames:frames.map(f=>({src:f.src,title:f.title,loading:f.getAttribute('loading'),width:f.width,height:f.height,aspectRatio:f.parentElement.style.aspectRatio}))});
  }
  assert.equal(receipt.rawHtml.length,12);assert.equal(receipt.rawHtml.reduce((sum,r)=>sum+r.videoObjects,0),14);
  for(const width of [320,390,1440]){
    const context=await browser.newContext({viewport:{width,height:900},...(width<500?{isMobile:true,hasTouch:true}:{})});
    const page=await context.newPage();
    for(const path of paths){
      const response=await page.goto(`${base}${path}`,{waitUntil:'domcontentloaded'});
      await page.locator('[data-testid="help-video"] iframe').first().waitFor({state:'visible'});
      const geometries=[];
      const frames=page.locator('[data-testid="help-video"] iframe');
      for(let index=0;index<await frames.count();index++){
        await frames.nth(index).scrollIntoViewIfNeeded();
        const geometry=await frames.nth(index).evaluate(frame=>{
          const r=frame.getBoundingClientRect();const p=frame.parentElement.getBoundingClientRect();const style=getComputedStyle(frame);
          return {src:frame.src,title:frame.title,width:r.width,height:r.height,left:r.left,top:r.top,frameWidth:p.width,frameHeight:p.height,display:style.display,visibility:style.visibility,opacity:style.opacity,overlayButtons:frame.parentElement.querySelectorAll('button').length,expectedAspect:getComputedStyle(frame.parentElement).aspectRatio};
        });
        receipt.lastGeometry={path,width,...geometry};
        assert.ok(geometry.width>=200&&geometry.height>=200);assert.ok(geometry.left>=0&&geometry.left+geometry.width<=width+1);
        assert.ok(Math.abs(geometry.height-Math.max(200,geometry.width*9/16))<1);
        assert.equal(geometry.width,geometry.frameWidth);assert.equal(geometry.height,geometry.frameHeight);
        assert.notEqual(geometry.display,'none');assert.equal(geometry.visibility,'visible');assert.equal(geometry.opacity,'1');assert.equal(geometry.overlayButtons,0);
        geometries.push(geometry);
      }
      const scrollWidth=await page.evaluate(()=>document.documentElement.scrollWidth);
      assert.ok(scrollWidth<=width);assert.equal(response.status(),200);
      receipt.geometry.push({path,width,httpStatus:response.status(),scrollWidth,players:geometries});
      if(path===paths[0])await page.screenshot({path:`${directory}/help-initial-players-${label}-${width}.png`,fullPage:true});
    }
    await context.close();
  }
  if(!process.env.HELP_VERIFY_SKIP_PLAYBACK)for(const width of [320,390]){
  const context=await browser.newContext({viewport:{width,height:844},isMobile:true,hasTouch:true});
  const page=await context.newPage();
  await page.goto(`${base}${paths[0]}`,{waitUntil:'domcontentloaded'});
  const player=page.locator('iframe[src*="/embed/aHjrZktaWIU"]');await player.scrollIntoViewIfNeeded();
  const frame=await (await player.elementHandle()).contentFrame();
  const playback={path:paths[0],width,playerSrc:await player.getAttribute('src'),before:null,after:null};receipt.playback.push(playback);
  try{
    await frame.locator('video').waitFor({state:'attached',timeout:30000});
    playback.before=await frame.locator('video').evaluate(video=>({currentTime:video.currentTime,paused:video.paused,readyState:video.readyState}));
    assert.equal(playback.before.paused,true);assert.equal(playback.before.currentTime,0);
    await frame.getByRole('button',{name:'Play video',exact:true}).click({timeout:15000});
    await frame.waitForFunction(()=>{const video=document.querySelector('video');return video&&!video.paused&&video.currentTime>1;},null,{timeout:30000});
    playback.after=await frame.locator('video').evaluate(video=>({currentTime:video.currentTime,duration:video.duration,paused:video.paused,readyState:video.readyState}));
    assert.ok(playback.after.currentTime>1);assert.equal(playback.after.paused,false);playback.status='passed';
  }catch(error){playback.status='failed';playback.error=String(error);playback.playerText=await frame.locator('body').innerText().catch(()=>null);throw error;}
  finally{await page.screenshot({path:`${directory}/help-initial-players-${label}-playback-${width}.png`});await context.close();}
  }
  receipt.status='passed';
}catch(error){receipt.status='failed';receipt.error=String(error);process.exitCode=1;}
finally{await browser.close();await writeFile(`${directory}/help-initial-players-${label}-proof.json`,JSON.stringify(receipt,null,2));}
console.log(JSON.stringify({status:receipt.status,rawPages:receipt.rawHtml.length,rawVideos:receipt.rawHtml.reduce((sum,r)=>sum+r.videoObjects,0),geometryRows:receipt.geometry.length,playback:receipt.playback,receipt:`${directory}/help-initial-players-${label}-proof.json`}));
