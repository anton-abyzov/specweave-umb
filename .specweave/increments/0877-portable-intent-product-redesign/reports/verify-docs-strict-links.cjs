const http = require('node:http');
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const {chromium} = require('/tmp/specweave-0877-root/docs-site/node_modules/@playwright/test');

const root = '/tmp/specweave-0877-root/docs-site/build';
const output = __dirname;
const artifacts = path.join(output, 'artifacts/docs-strict-links');
fs.mkdirSync(artifacts, {recursive: true});
const types = {'.html': 'text/html; charset=utf-8', '.js': 'application/javascript', '.css': 'text/css', '.svg': 'image/svg+xml', '.png': 'image/png', '.webp': 'image/webp', '.woff2': 'font/woff2', '.json': 'application/json'};
const server = http.createServer((req, res) => {
  let file;
  try {
    const pathname = decodeURIComponent(new URL(req.url, 'http://localhost').pathname);
    file = path.resolve(root, `.${pathname}`);
    if (file !== root && !file.startsWith(`${root}/`)) throw new Error('outside root');
    if (fs.statSync(file).isDirectory()) file = path.join(file, 'index.html');
    const data = fs.readFileSync(file);
    res.writeHead(200, {'Content-Type': types[path.extname(file)] || 'application/octet-stream'});
    res.end(data);
  } catch {
    res.writeHead(404, {'Content-Type': 'text/plain'});
    res.end('Not found');
  }
});

const routes = [
  '/docs/getting-started', '/docs/academy', '/docs/guides/compliance-standards',
  '/docs/guides/core-concepts/living-documentation',
  '/docs/skills/extensible/skill-development-guidelines',
  '/docs/skills/extensible/extensible-skills', '/docs/skills/extensible',
  '/docs/skills/extensible/extensible-skills-standard', '/docs/guides/lazy-plugin-loading',
  '/docs/reference/skills', '/product', '/integrations',
];

(async () => {
  const report = {at: new Date().toISOString(), headless: true, origin: null, routes: [], pageErrors: [], assertions: [], pass: false};
  let browser;
  try {
    await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
    report.origin = `http://127.0.0.1:${server.address().port}`;
    browser = await chromium.launch({headless: true});
    const page = await browser.newPage({viewport: {width: 1440, height: 1000}});
    page.on('pageerror', error => report.pageErrors.push({url: page.url(), message: error.message}));
    for (const route of routes) {
      const response = await page.goto(`${report.origin}${route}`, {waitUntil: 'networkidle', timeout: 30000});
      assert.equal(response.status(), 200, route);
      const title = await page.locator('h1').first().innerText();
      assert(title.length > 0 && title !== 'Page Title', route);
      report.routes.push({route, status: response.status(), title});
    }
    await page.goto(`${report.origin}/docs/skills/extensible/extensible-skills`, {waitUntil: 'networkidle'});
    assert.equal(await page.locator('article a[href="/docs/skills/extensible/extensible-skills"]').count(), 0);
    assert.match(await page.locator('article').innerText(), /not available in the published documentation/);
    report.assertions.push('Extensibility overview has no self-link and labels unpublished guide.');
    await page.screenshot({path: path.join(artifacts, 'extensibility-overview-desktop.png'), fullPage: true});
    await page.goto(`${report.origin}/docs/guides/lazy-plugin-loading`, {waitUntil: 'networkidle'});
    const gettingStarted = page.locator('article a[href="/docs/getting-started"]');
    assert.equal(await gettingStarted.innerText(), 'Getting Started');
    report.assertions.push('Lazy-loading related link honestly labels canonical getting started.');
    const template = await page.request.get(`${report.origin}/docs/_page-template`);
    assert.equal(template.status(), 404);
    report.assertions.push('Unpublished authoring template returns HTTP 404.');
    await page.setViewportSize({width: 390, height: 844});
    await page.goto(`${report.origin}/docs/skills/extensible/extensible-skills`, {waitUntil: 'networkidle'});
    assert.match(await page.locator('article').innerText(), /not available in the published documentation/);
    await page.screenshot({path: path.join(artifacts, 'extensibility-overview-mobile.png'), fullPage: true});
    report.assertions.push('Historical availability notice remains visible on mobile.');
    assert.deepEqual(report.pageErrors, []);
    report.pass = true;
  } catch (error) {
    report.error = error.stack;
    process.exitCode = 1;
  } finally {
    if (browser) await browser.close();
    await new Promise(resolve => server.close(resolve));
    fs.writeFileSync(path.join(output, 'docs-strict-links-headless.json'), JSON.stringify(report, null, 2));
    console.log(JSON.stringify(report, null, 2));
  }
})();
