import { createRequire } from "node:module";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
const require = createRequire(import.meta.url);
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || "playwright");
const destination = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../reports/public-design");
const baseUrl = process.env.BASE_URL || "https://spec-weave.com";
const reportName = process.env.REPORT_NAME || "specweave";
fs.mkdirSync(destination, { recursive: true });
const browser = await chromium.launch({ headless: true });
const results = [];
const errors = [];
try {
  for (const width of [320, 1440]) {
    for (const theme of ["light", "dark"]) {
      const context = await browser.newContext({ viewport: { width, height: 900 }, colorScheme: theme });
      await context.addInitScript((value) => localStorage.setItem("theme", value), theme);
      const page = await context.newPage();
      for (const route of ["/", "/blog/", "/docs/getting-started/", "/docs/tags/", "/integrations/", "/pricing/", "/product/", "/search/"]) {
        const url = "https://spec-weave.com" + route;
        const response = await page.goto(baseUrl + route, { waitUntil: "networkidle", timeout: 45000 });
        await page.evaluate(() => window.scrollTo({ top: document.body.scrollHeight, behavior: "instant" }));
        await page.waitForTimeout(150);
        await page.evaluate(() => window.scrollTo({ top: 0, behavior: "instant" }));
        await page.waitForTimeout(150);
        const state = await page.evaluate(() => {
          const rgb = (value) => value.match(/[\d.]+/g).map(Number);
          const luminance = (value) => value.slice(0, 3).map(x => x / 255).map(x => x <= 0.04045 ? x / 12.92 : ((x + 0.055) / 1.055) ** 2.4).reduce((sum, x, i) => sum + x * [0.2126, 0.7152, 0.0722][i], 0);
          const contrastFailures = [];
          const linkContrasts = [];
          for (const link of document.querySelectorAll('article h2 a, article footer a, a[class*="tag"], .markdown a:not(.button)')) {
            if (!link.innerText.trim() || !link.getClientRects().length) continue;
            const styles = getComputedStyle(link);
            const layers = [];
            for (let parent = link; parent; parent = parent.parentElement) layers.push(rgb(getComputedStyle(parent).backgroundColor));
            let background = [255, 255, 255];
            for (const layer of layers.reverse()) {
              const alpha = layer.length > 3 ? layer[3] : 1;
              background = background.map((x, i) => layer[i] * alpha + x * (1 - alpha));
            }
            const foreground = rgb(styles.color);
            const alpha = foreground.length > 3 ? foreground[3] : 1;
            const color = foreground.slice(0, 3).map((x, i) => x * alpha + background[i] * (1 - alpha));
            const brightness = [luminance(color), luminance(background)].sort((a, b) => b - a);
            const ratio = (brightness[0] + 0.05) / (brightness[1] + 0.05);
            const large = parseFloat(styles.fontSize) >= 24 || (parseFloat(styles.fontSize) >= 18.66 && parseInt(styles.fontWeight) >= 700);
            linkContrasts.push(ratio);
            if (ratio < (large ? 3 : 4.5)) contrastFailures.push({ text: link.innerText.slice(0, 80), ratio, color: styles.color, background, required: large ? 3 : 4.5 });
          }
          return {
          title: document.title,
          canonical: document.querySelector('link[rel="canonical"]')?.href,
          heading: document.querySelector("h1")?.innerText,
          overflow: document.documentElement.scrollWidth > window.innerWidth + 1,
          theme: document.documentElement.dataset.theme,
          description: document.querySelector('meta[name="description"]')?.content,
          checkedLinks: linkContrasts.length,
          minimumLinkContrast: Math.min(...linkContrasts),
          contrastFailures
        }; });
        const status = response.status();
        const valid = status === 200 && state.title && state.canonical === url && state.heading && state.description && !state.overflow && state.theme === theme && !state.contrastFailures.length;
        const filename = reportName + "-" + width + "-" + theme + route.replaceAll("/", "_") + ".jpg";
        await page.screenshot({ path: path.join(destination, filename), type: "jpeg", quality: 72, fullPage: false });
        results.push({ url, width, theme, status, valid: Boolean(valid), ...state, screenshot: filename });
        if (!valid) errors.push({ url, width, theme, status, ...state });
      }
      await context.close();
    }
  }
} finally {
  await browser.close();
}
fs.writeFileSync(path.join(destination, reportName + ".json"), JSON.stringify({ checkedAt: new Date().toISOString(), baseUrl, passed: results.length - errors.length, failed: errors.length, results, errors }, null, 2) + "\n");
console.log(JSON.stringify({ passed: results.length - errors.length, failed: errors.length, errors }));
process.exitCode = errors.length ? 1 : 0;
