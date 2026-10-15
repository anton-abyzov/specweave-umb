// Re-checks the two review.md findings against the live page (headless).
import {createRequire} from 'module';
const require = createRequire('/Users/antonabyzov/Projects/github/specweave-l2-landing/docs-site/package.json');
const {chromium} = require('playwright');
const url = 'https://spec-weave.com/code/?live=' + Date.now();
const browser = await chromium.launch({headless: true});
const out = {};
{
  const ctx = await browser.newContext({viewport: {width: 1440, height: 900}, reducedMotion: 'reduce'});
  const page = await ctx.newPage();
  await page.goto(url, {waitUntil: 'networkidle'});
  out.reducedScrollBehavior = await page.evaluate(() => getComputedStyle(document.documentElement).scrollBehavior);
  const btns = page.locator('button', {hasText: /./}).filter({has: page.locator(':scope')});
  const steps = await page.evaluate(() => [...document.querySelectorAll('section button')].map(b => b.innerText.trim()).filter(Boolean).slice(0, 8));
  out.stepButtons = steps;
  const all = page.locator('section button');
  const n = await all.count();
  if (n >= 3) {
    const y0 = await page.evaluate(() => scrollY);
    await all.nth(2).click();
    const y1 = await page.evaluate(() => scrollY);
    await page.waitForTimeout(100);
    const y2 = await page.evaluate(() => scrollY);
    await page.waitForTimeout(1200);
    const y3 = await page.evaluate(() => scrollY);
    out.reducedClickScroll = {y0, immediate: y1, after100ms: y2, after1300ms: y3, instant: y1 === y3};
  }
  await ctx.close();
}
{
  const ctx = await browser.newContext({viewport: {width: 1440, height: 900}, javaScriptEnabled: false});
  const page = await ctx.newPage();
  await page.goto(url, {waitUntil: 'load'});
  out.noJsVisibleSectionButtons = await page.evaluate(() => [...document.querySelectorAll('section button')].filter(b => { const r = b.getBoundingClientRect(); const s = getComputedStyle(b); return r.width > 0 && r.height > 0 && s.visibility !== 'hidden' && s.display !== 'none'; }).map(b => b.innerText.trim()));
  out.noJsAnchors = await page.evaluate(() => [...document.querySelectorAll('section a[href^="#"]')].map(a => a.getAttribute('href')).slice(0, 10));
  await ctx.close();
}
await browser.close();
console.log(JSON.stringify(out, null, 1));
