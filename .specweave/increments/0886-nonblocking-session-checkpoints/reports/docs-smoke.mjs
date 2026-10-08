import { createServer } from 'node:http';
import { readFile, stat, writeFile } from 'node:fs/promises';
import { join, extname, resolve } from 'node:path';
import { createRequire } from 'node:module';
import assert from 'node:assert/strict';

const repo = '/Users/antonabyzov/.codex/worktrees/usage-checkpoint-docs/specweave';
const require = createRequire(join(repo, 'docs-site/package.json'));
const { chromium } = require('@playwright/test');
const buildDir = join(repo, 'docs-site/build');
const report = { headless: true, node: process.version, cases: [], pageErrors: [] };
const types = { '.html': 'text/html', '.js': 'text/javascript', '.css': 'text/css', '.svg': 'image/svg+xml', '.png': 'image/png', '.woff2': 'font/woff2', '.json': 'application/json' };
const server = createServer(async (req, res) => {
  try {
    let path = resolve(buildDir, '.' + decodeURIComponent(new URL(req.url, 'http://localhost').pathname));
    if (!path.startsWith(buildDir)) throw new Error('Invalid path');
    const info = await stat(path);
    if (info.isDirectory()) path = join(path, 'index.html');
    const data = await readFile(path);
    res.writeHead(200, { 'content-type': types[extname(path)] ?? 'application/octet-stream' });
    res.end(data);
  } catch { res.writeHead(404); res.end('Not found'); }
});
await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
const base = `http://127.0.0.1:${server.address().port}`;
report.base = base;
let browser;
try {
  browser = await chromium.launch({ headless: true });
  for (const width of [1440, 390, 320]) {
    for (const theme of ['light', 'dark']) {
      const context = await browser.newContext({ viewport: { width, height: 900 }, colorScheme: theme });
      await context.addInitScript(t => localStorage.setItem('theme', t), theme);
      const page = await context.newPage();
      page.on('pageerror', error => report.pageErrors.push(error.message));
      for (const path of ['/', '/pricing/']) {
        const response = await page.goto(base + path, { waitUntil: 'networkidle' });
        assert.equal(response.status(), 200, `HTTP ${path}`);
        if (path === '/pricing/') {
          await page.getByText('What gets saved automatically?', { exact: true }).click();
          await page.getByText('Silent local recovery checkpoints after turns', { exact: true }).waitFor({ state: 'visible' });
          assert.match(await page.locator('body').innerText(), /pickup does not apply automatic checkpoints/);
        } else {
          assert.match(await page.locator('body').innerText(), /keeps local recovery checkpoints after turns without interrupting work/);
        }
        const text = await page.locator('body').innerText();
        assert.doesNotMatch(text, /(?:at|passes) 90(?:%| percent)|threshold you pick/);
        const dimensions = await page.evaluate(() => ({ viewport: window.innerWidth, document: document.documentElement.scrollWidth, body: document.body.scrollWidth }));
        assert.ok(dimensions.document <= dimensions.viewport + 1, `${path} horizontal overflow ${JSON.stringify(dimensions)}`);
        report.cases.push({ path, theme, width, dimensions, newCopyPresent: true, oldQuotaPromiseAbsent: true });
      }
      await context.close();
    }
  }
  assert.deepEqual(report.pageErrors, []);
  report.ok = true;
} catch (error) {
  report.ok = false;
  report.error = error.stack;
  throw error;
} finally {
  if (browser) await browser.close();
  await new Promise(resolve => server.close(resolve));
  await writeFile('/tmp/specweave-0886-docs-smoke/result.json', JSON.stringify(report, null, 2) + '\n');
  console.log(JSON.stringify(report, null, 2));
}
