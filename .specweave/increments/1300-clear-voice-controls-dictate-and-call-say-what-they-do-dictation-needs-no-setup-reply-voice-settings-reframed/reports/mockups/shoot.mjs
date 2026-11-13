// Headless screenshots of the 1300 mockup: node shoot.mjs
// STUDIO_PLAYWRIGHT_MODULE = path to playwright-core, STUDIO_CHROME = headless Chromium binary.
import * as NodeModule from "node:module";
import * as NodePath from "node:path";
import * as NodeURL from "node:url";

process.env.PWDEBUG = "0";
process.env.PLAYWRIGHT_HTML_OPEN = "never";
const here = NodePath.dirname(NodeURL.fileURLToPath(import.meta.url));
const { chromium } = NodeModule.createRequire(import.meta.url)(
  process.env.STUDIO_PLAYWRIGHT_MODULE ?? "playwright-core",
);
const browser = await chromium.launch({ headless: true, executablePath: process.env.STUDIO_CHROME });
const shots = [
  ["compare", 1100, 700],
  ["before-composer", 1280, 720],
  ["before-first-use", 1280, 720],
  ["before-settings", 1280, 900],
  ["after-composer", 1280, 720],
  ["after-narrow", 760, 720],
  ["after-dictating", 1280, 720],
  ["after-call-card", 1280, 720],
  ["after-call-blocked", 1280, 720],
  ["after-settings", 1280, 1090],
];
let failed = false;
for (const theme of ["light", "dark"]) {
  for (const [view, width, height] of shots) {
    const page = await browser.newPage({ viewport: { width, height }, deviceScaleFactor: 2 });
    await page.goto(
      `${NodeURL.pathToFileURL(NodePath.join(here, "mockup.html"))}?view=${view}&theme=${theme}`,
    );
    // Anything cut off by the window or by its own box would hide part of the design.
    const clipped = await page.evaluate(() => {
      const root = document.documentElement;
      const out = [];
      if (root.scrollWidth > root.clientWidth) out.push("page-x");
      if (root.scrollHeight > root.clientHeight) out.push("page-y");
      for (const el of document.querySelectorAll(".page,.dlg,.lane,.thread,.card,.tip,.vbar")) {
        // Popups carry an arrow outside their own box, so only their position is checked.
        const popup = el.matches(".card,.tip");
        if (!popup && (el.scrollHeight > el.clientHeight + 1 || el.scrollWidth > el.clientWidth + 1))
          out.push(el.className);
        const box = el.getBoundingClientRect();
        if (box.right > innerWidth + 0.5 || box.bottom > innerHeight + 0.5 || box.left < -0.5 || box.top < -0.5)
          out.push(`${el.className} off-screen`);
      }
      return out;
    });
    await page.screenshot({ path: NodePath.join(here, `${view}-${theme}.png`) });
    console.log(`${view}-${theme}.png ${clipped.length ? `CLIPPED: ${clipped.join(", ")}` : "ok"}`);
    if (clipped.length) failed = true;
    await page.close();
  }
}
await browser.close();
process.exit(failed ? 1 : 0);
