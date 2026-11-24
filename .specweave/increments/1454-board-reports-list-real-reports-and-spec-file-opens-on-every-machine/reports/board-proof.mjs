// Headless proof for 1454: opens the Board's increment panel on a scratch
// project whose folder lags its remote, clicks Spec file and Reports, and
// saves screenshots and a JSON of what the viewer showed.
// Usage: node board-proof.mjs <playwright-core dir> <chromium exe> <pair url> <out dir> <label>
import { createRequire } from "node:module";
import * as fs from "node:fs";
import * as path from "node:path";

const [playwrightDir, executablePath, pairUrl, outDir, label] = process.argv.slice(2);
const require = createRequire(import.meta.url);
const { chromium } = require(playwrightDir);
fs.mkdirSync(outDir, { recursive: true });
const result = { label, steps: [] };
const note = (step, value) => {
  result.steps.push({ step, value });
  console.log(step, JSON.stringify(value).slice(0, 400));
};

const browser = await chromium.launch({ headless: true, executablePath });
const page = await browser.newPage({ viewport: { width: 1440, height: 960 } });
const shot = (name) => page.screenshot({ path: path.join(outDir, `${label}-${name}.png`) });
try {
  await page.goto(pairUrl);
  await page.waitForURL((url) => !url.pathname.startsWith("/pair"), { timeout: 30_000 });
  await page.waitForTimeout(2_000);
  const keep = page.getByRole("button", { name: /Keep Supervised/i });
  if (await keep.count()) await keep.first().click();
  // The project, then its Board.
  await page.getByText("Atlas", { exact: true }).first().click();
  await page.waitForTimeout(1_500);
  const boardTab = page.getByRole("tab", { name: /^Board/ });
  if (await boardTab.count()) await boardTab.first().click();
  else await page.getByRole("button", { name: /^Board/ }).first().click();
  await page.waitForTimeout(2_500);
  await shot("board");
  await page.getByText("0042", { exact: true }).first().click();
  await page.waitForTimeout(2_500);
  const view = page.locator(".sws-board-view").first();
  note("source", await page.locator(".sws-board-view-source").first().textContent().catch(() => null));
  note(
    "reports section",
    await page
      .locator('section[aria-label="Reports"]')
      .first()
      .innerText()
      .catch(() => null),
  );
  await shot("panel");

  await view.getByRole("button", { name: "Spec file", exact: true }).evaluate((el) => el.click());
  await page.waitForTimeout(2_500);
  const viewer = page.locator("[data-library-viewer]").first();
  note("spec viewer", (await viewer.innerText().catch(() => "")).slice(0, 600));
  await shot("spec-file");
  const close = page.getByRole("button", { name: /^Close/ });
  await page.keyboard.press("Escape");
  await page.waitForTimeout(800);

  await view.getByRole("button", { name: "Reports", exact: true }).evaluate((el) => el.click());
  await page.waitForTimeout(2_500);
  note("reports viewer", (await viewer.innerText().catch(() => "")).slice(0, 600));
  note(
    "reports viewer title",
    await page
      .locator(".viewer-overlay-title, [data-viewer-title]")
      .first()
      .textContent()
      .catch(() => null),
  );
  await shot("reports");
  // Step through what the viewer offers.
  for (let index = 0; index < 4; index += 1) {
    const next = page.getByRole("button", { name: "Next file" });
    if (!(await next.count())) break;
    await next.first().evaluate((el) => el.click());
    await page.waitForTimeout(2_000);
    note(`reports next ${index + 1}`, {
      text: (await viewer.innerText().catch(() => "")).slice(0, 200),
      image: await viewer.locator("img").count(),
      frame: await viewer.locator("iframe").count(),
    });
    await shot(`reports-next-${index + 1}`);
  }
} catch (error) {
  note("error", String(error));
  await shot("error").catch(() => {});
} finally {
  fs.writeFileSync(path.join(outDir, `${label}.json`), JSON.stringify(result, null, 2));
  await browser.close();
}
