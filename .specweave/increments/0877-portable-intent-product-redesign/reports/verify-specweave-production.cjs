// Prepared for the post-Pages-deployment check. Never run against old production.
// Adapts docs-site/scripts/continuity-e2e.cjs; adds all six corrected guide routes,
// two device sizes, deployed artwork identity and per-route machine-readable evidence.
'use strict';
process.env.PWDEBUG = '0';
process.env.PLAYWRIGHT_HTML_OPEN = 'never';
if (process.env.VERIFY_DEPLOYED_SPECWEAVE !== '1') {
  console.error('Not executed: wait for confirmed Pages deployment, then set VERIFY_DEPLOYED_SPECWEAVE=1.');
  process.exit(2);
}
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const { createRequire } = require('node:module');
const repo = process.env.SPECWEAVE_VERIFY_REPO || '/tmp/specweave-0877-root';
const localRequire = createRequire(path.join(repo, 'docs-site/package.json'));
const { chromium, expect } = localRequire('@playwright/test');
const origin = 'https://spec-weave.com';
const artifactDir = path.join(__dirname, 'artifacts', 'production-specweave');
const resultFile = path.join(__dirname, 'specweave-production-verification.json');
const expectedAssetHash = '3f84480b6f3b4b3d4e7e53c83ee4982b5e9047a67fe1a08ab87833e06ea13c5d';
const expectedSource = '048751d3c986f5c28686ef1464b90deddb755637';
const routes = [
  ['/', ['Change agents.', 'Keep the thread.'], ['Your tools will change.', 'Example data above.']],
  ['/product', ['The work outlives', 'the session.'], ['Moving a card is a planning action.', 'Missing telemetry stays unknown.']],
  ['/integrations', ['Keep your tracker.', 'Connect the evidence.'], ['The current pull command reports external changes for review.', 'Run SpecWeave locally']],
  ['/docs/guides/model-selection', ['Models and execution context'], ['does not route model requests', 'no model API calls']],
  ['/docs/guides/analytics-dashboard', ['Work board and dashboard'], ['Moving a card to Done does not complete', 'every 15 seconds']],
  ['/docs/reference/cost-tracking', ['Usage and cost estimates'], ['Unknown is not zero.', 'March 2026 legacy API estimates']],
  ['/docs/guides/dashboard/hooks', ['Hooks'], ['two default lifecycle hooks', 'does not install PreToolUse, PostToolUse or PreCompact']],
  ['/docs/academy/specweave-essentials/08-ai-model-selection', ['Lesson 8: AI Model Selection'], ['Historical 1.x material', 'does not describe SpecWeave 2.1 defaults']],
  ['/docs/glossary/terms/intelligent-model-selection', ['Intelligent Model Selection'], ['Historical 1.x material', 'does not describe SpecWeave 2.1 defaults']],
];
const report = {
  origin, expectedSource, startedAt: new Date().toISOString(), headless: true,
  status: 'running', asset: null, routes: [], runtimeErrors: [], consoleErrors: [],
  failedRequests: [], failures: [],
};
function fail(label, error) {
  report.failures.push({ label, error: error instanceof Error ? error.message : String(error) });
}
async function main() {
  fs.mkdirSync(artifactDir, { recursive: true });
  const browser = await chromium.launch({ headless: true });
  try {
    for (const device of [
      { name: 'desktop', viewport: { width: 1440, height: 1000 }, isMobile: false, hasTouch: false },
      { name: 'mobile', viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true },
    ]) {
      const context = await browser.newContext({
        viewport: device.viewport, isMobile: device.isMobile, hasTouch: device.hasTouch,
        permissions: ['clipboard-read', 'clipboard-write'],
      });
      const page = await context.newPage();
      let activeRoute = '';
      page.on('pageerror', error => report.runtimeErrors.push({ device: device.name, route: activeRoute, error: error.message }));
      page.on('console', message => {
        if (message.type() === 'error') report.consoleErrors.push({ device: device.name, route: activeRoute, text: message.text() });
      });
      page.on('requestfailed', request => {
        report.failedRequests.push({ device: device.name, route: activeRoute, url: request.url(), error: request.failure()?.errorText });
      });
      for (const [route, headingParts, bodyParts] of routes) {
        activeRoute = route;
        const item = { device: device.name, route, status: null, assertions: [], screenshot: null, passed: false };
        report.routes.push(item);
        try {
          const response = await page.goto(origin + route, { waitUntil: 'load', timeout: 45000 });
          item.status = response?.status();
          expect(item.status, `${route} HTTP status`).toBe(200);
          await expect(page.getByRole('heading', { level: 1 })).toBeVisible();
          const heading = await page.getByRole('heading', { level: 1 }).innerText();
          const body = (await page.locator('main').innerText()).toLowerCase();
          for (const part of headingParts) expect(heading.toLowerCase()).toContain(part.toLowerCase());
          for (const part of bodyParts) expect(body).toContain(part.toLowerCase());
          item.assertions.push('Expected deployed heading and current semantic copy');
          expect(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth + 1), `${route} horizontal overflow`).toBe(false);
          await expect(page.locator('footer a[href*="/discussions"]')).toHaveCount(0);
          expect(await page.locator('footer a[href="https://github.com/anton-abyzov/specweave/issues"]').count()).toBeGreaterThan(0);
          item.assertions.push('No viewport overflow; Issues support replaces disabled Discussions');
          if (route === '/') {
            const artwork = page.locator('img[src="/img/product/continuity.webp"]');
            await expect(artwork).toBeVisible();
            await expect.poll(() => artwork.evaluate(image => image.complete && image.naturalWidth === 2048 && image.naturalHeight === 1152)).toBe(true);
            if (!report.asset) {
              const assetResponse = await context.request.get(origin + '/img/product/continuity.webp');
              expect(assetResponse.status()).toBe(200);
              expect(assetResponse.headers()['content-type']).toContain('image/webp');
              const hash = crypto.createHash('sha256').update(await assetResponse.body()).digest('hex');
              expect(hash).toBe(expectedAssetHash);
              report.asset = { url: origin + '/img/product/continuity.webp', sha256: hash, matchesExpected: true };
            }
            await page.getByRole('button', { name: 'Copy installation command' }).click();
            await expect(page.getByRole('status')).toHaveText('Installation command copied.');
            // Assert without logging any unexpected clipboard contents.
            const clipboardMatches = await page.evaluate(async () => (await navigator.clipboard.readText()) === 'npm install -g specweave');
            expect(clipboardMatches, 'Copied exact installation command').toBe(true);
            const review = page.getByRole('button', { name: /Preserve work across agents/ });
            await review.click();
            await expect(review).toHaveAttribute('aria-pressed', 'true');
            await expect(page.locator('[aria-live="polite"]')).toContainText('Review and verification still decide');
            const small = page.getByRole('button', { name: /Make exports accessible/ });
            await small.focus();
            await page.keyboard.press('Enter');
            await expect(small).toHaveAttribute('aria-pressed', 'true');
            await expect(page.locator('[aria-live="polite"]')).toContainText('An intent can start small.');
            item.assertions.push('Artwork decoded and matches shipped generated asset; clipboard; mouse and keyboard board interaction');
            if (device.isMobile) {
              await page.getByRole('button', { name: 'Toggle navigation bar' }).click();
              await expect(page.getByRole('link', { name: 'Product', exact: true })).toBeVisible();
              await page.getByRole('button', { name: 'Close navigation bar' }).click();
              item.assertions.push('Mobile navigation opens and closes');
            }
            const start = page.getByRole('link', { name: /Start with your project/ });
            await expect(start).toHaveAttribute('href', '/docs/getting-started');
          }
          if (route === '/integrations') {
            await page.getByText('Will changing a card update Jira?', { exact: true }).click();
            await expect(page.getByText('A board state change is local.', { exact: false })).toBeVisible();
            item.assertions.push('Integration disclosure opens with explicit local-state boundary');
          }
          const slug = route === '/' ? 'home' : route.slice(1).replaceAll('/', '-');
          item.screenshot = path.join(artifactDir, `${device.name}-${slug}.png`);
          await page.screenshot({ path: item.screenshot, fullPage: !route.startsWith('/docs/') });
          item.passed = true;
        } catch (error) { fail(`${device.name} ${route}`, error); }
      }
      await context.close();
    }
    if (report.runtimeErrors.length) fail('JavaScript runtime errors', JSON.stringify(report.runtimeErrors));
    if (report.consoleErrors.length) fail('Browser console errors', JSON.stringify(report.consoleErrors));
  } finally {
    await browser.close();
    report.finishedAt = new Date().toISOString();
    report.status = report.failures.length ? 'failed' : 'passed';
    fs.writeFileSync(resultFile, JSON.stringify(report, null, 2) + '\n');
  }
  console.log(`${report.status.toUpperCase()}: ${report.routes.filter(r => r.passed).length}/${report.routes.length} page/device checks; ${report.runtimeErrors.length} runtime errors; ${report.consoleErrors.length} console errors. Evidence: ${resultFile}`);
  if (report.failures.length) process.exitCode = 1;
}
main().catch(error => {
  fail('Runner', error);
  report.status = 'failed';
  report.finishedAt = new Date().toISOString();
  fs.writeFileSync(resultFile, JSON.stringify(report, null, 2) + '\n');
  console.error(error.message);
  process.exitCode = 1;
});
