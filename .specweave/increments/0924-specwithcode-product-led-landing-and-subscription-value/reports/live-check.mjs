// Headless live readback of https://spec-weave.com/code/ and /studio/ (0924 AC-05).
// usage: node live-check.mjs <outdir>
import {createRequire} from 'module';
const require = createRequire('/Users/antonabyzov/Projects/github/specweave-l2-landing/docs-site/package.json');
const {chromium} = require('playwright');
import fs from 'fs';
const out = process.argv[2];
fs.mkdirSync(out, {recursive: true});
const browser = await chromium.launch({headless: true});
const res = {checkedAt: new Date().toISOString(), pages: [], studio: null};
for (const mode of ['light', 'dark']) for (const w of [1440, 375]) {
  const ctx = await browser.newContext({viewport: {width: w, height: w > 800 ? 900 : 812}, deviceScaleFactor: w > 800 ? 1 : 2, colorScheme: mode});
  await ctx.addInitScript(m => { try { localStorage.setItem('theme', m); } catch {} }, mode);
  const page = await ctx.newPage();
  const errs = [];
  page.on('pageerror', e => errs.push(String(e)));
  const r = await page.goto('https://spec-weave.com/code/?live=' + Date.now(), {waitUntil: 'networkidle'});
  await page.waitForTimeout(1200);
  const info = await page.evaluate(() => ({
    title: document.title,
    canonical: document.querySelector('link[rel=canonical]')?.href || null,
    theme: document.documentElement.dataset.theme || null,
    h1: document.querySelector('h1')?.innerText || null,
    hasYourAgents: document.body.innerText.includes('Your agents.'),
    hasTwoMeters: document.body.innerText.includes('Same work, two meters'),
    scrollWidth: document.documentElement.scrollWidth,
    innerWidth: innerWidth,
  }));
  await page.screenshot({path: `${out}/${mode}-${w}-top.png`});
  await page.screenshot({path: `${out}/${mode}-${w}-full.jpg`, type: "jpeg", quality: 70, fullPage: true});
  res.pages.push({mode, w, status: r.status(), finalUrl: page.url(), ...info, errs});
  await ctx.close();
}
{
  const ctx = await browser.newContext();
  const page = await ctx.newPage();
  const r = await page.goto('https://spec-weave.com/studio/?live=' + Date.now(), {waitUntil: 'networkidle'});
  await page.waitForTimeout(2500);
  res.studio = {status: r.status(), finalUrl: page.url()};
  await ctx.close();
}
await browser.close();
fs.writeFileSync(`${out}/live-check.json`, JSON.stringify(res, null, 1));
console.log(JSON.stringify(res));
const bad = res.pages.filter(p => p.status !== 200 || !p.hasYourAgents || !p.hasTwoMeters || p.canonical !== 'https://spec-weave.com/code/' || p.scrollWidth > p.innerWidth || p.theme !== p.mode || p.errs.length);
const studioOk = res.studio.status === 200 && new URL(res.studio.finalUrl).pathname === '/code/';
if (bad.length || !studioOk) { console.error('LIVE CHECK FAILED', JSON.stringify({bad, studio: res.studio})); process.exit(1); }
console.log('LIVE CHECK PASS: 4 viewports (1440/375 x light/dark) + /studio/ -> /code/');
