// Headless captures of the 1057 mockups. Run: PWDEBUG=0 PLAYWRIGHT_HTML_OPEN=never node capture.mjs
import { chromium } from "/Users/antonabyzov/.nvm/versions/node/v22.20.0/lib/node_modules/playwright/index.mjs";
import { fileURLToPath, pathToFileURL } from "node:url";
import path from "node:path";
const here = path.dirname(fileURLToPath(import.meta.url));
const page_url = pathToFileURL(path.join(here, "../mockups/agent-navigation.html")).href;
const browser = await chromium.launch({ headless: true });
const page = await browser.newPage({ viewport: { width: 1280, height: 900 }, deviceScaleFactor: 2 });
await page.goto(page_url);
await page.screenshot({ path: path.join(here, "mockups-full.png"), fullPage: true });
for (const id of ["shot-current", "shot-proposed", "shot-updates", "shot-filter", "shot-narrow"]) {
  await page.locator(`#${id}`).screenshot({ path: path.join(here, `${id}.png`) });
}
const overflow = await page.evaluate(() => [...document.querySelectorAll(".phone *")].filter((el) => el.scrollWidth > el.clientWidth + 1 && getComputedStyle(el).overflowX !== "hidden" && !el.classList.contains("t") && !el.classList.contains("r")).length);
console.log(JSON.stringify({ captured: 6, narrowOverflowElements: overflow }));
await browser.close();
