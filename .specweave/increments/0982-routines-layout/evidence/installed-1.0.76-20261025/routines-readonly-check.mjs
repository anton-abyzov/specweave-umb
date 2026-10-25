// Read-only headless acceptance of the routines layout on the INSTALLED, running M4 service.
// The browser session holds only orchestration:read + diagnostics:read, so Run, Pause, Enable,
// save and delete are refused by the server even if pressed; this script never presses them.
// It reads, navigates, measures and screenshots. Usage: node routines-readonly-check.mjs <out-dir>
import * as NodeAssert from "node:assert/strict";
import { execFileSync } from "node:child_process";
import * as NodeFS from "node:fs";
import * as NodePath from "node:path";
import { createRequire } from "node:module";

process.env.PWDEBUG = "0";
process.env.PLAYWRIGHT_HTML_OPEN = "never";
const out = NodePath.resolve(process.argv[2] ?? "./run");
NodeFS.mkdirSync(out, { recursive: true });
const PROJECT = process.env.ROUTINES_PROJECT ?? "1332065e-795b-4f98-91c4-f114917e53f6";
// The CLI can print log lines before its JSON; take the last JSON line.
const pairJson = (text) => JSON.parse(text.split("\n").filter((l) => l.trim().startsWith("{")).at(-1));
const req = createRequire(
  "/Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specweave-studio/node_modules/.pnpm/playwright-core@1.60.0/node_modules/playwright-core/package.json",
);
const { chromium } = req("playwright-core");

// The loaded live service can miss the CLI's liveness probe; retry a few times.
let pair;
for (let attempt = 1; !pair; attempt++) {
  try {
    pair = pairJson(execFileSync("/Users/antonabyzov/.local/bin/specweave-studio", [
      "pair", "--json", "--ttl", "10m", "--label", "routines-readonly-check",
      "--scope", "orchestration:read", "--scope", "diagnostics:read",
    ], { encoding: "utf8", stdio: ["ignore", "pipe", "pipe"] }));
  } catch (error) {
    if (attempt >= 6) throw error;
    await new Promise((r) => setTimeout(r, 10000));
  }
}
const origin = pair.origin;
const receipt = {
  origin, scopes: ["orchestration:read", "diagnostics:read"], headless: true,
  startedAt: new Date().toISOString(), project: PROJECT, checks: [], screenshots: [], requests: [],
};
const pass = (name, detail) => receipt.checks.push({ name, ok: true, ...detail });
const browser = await chromium.launch({ headless: true });
let page;
const shot = async (name, opts = {}) => {
  const file = NodePath.join(out, name);
  await page.screenshot({ path: file, ...opts });
  receipt.screenshots.push(file);
};
// Switch the theme the way the app does: no transitions, the class, the inline background cleared.
const setDark = (on) =>
  page.evaluate((dark) => {
    const root = document.documentElement;
    root.classList.add("no-transitions");
    root.classList.toggle("dark", dark);
    root.style.backgroundColor = "";
    document.body.style.backgroundColor = "";
    void root.offsetHeight;
  }, on);
const overflow = () => page.evaluate(() => document.documentElement.scrollWidth > innerWidth + 1);
try {
  const context = await browser.newContext({ viewport: { width: 1440, height: 1000 }, reducedMotion: "reduce" });
  const session = await context.request.post(`${origin}/api/auth/browser-session`, {
    data: { credential: pair.token }, headers: { Origin: origin },
  });
  NodeAssert.equal(session.status(), 200);
  page = await context.newPage();
  page.setDefaultTimeout(120000);
  // Record every RPC the page sends, to prove no routine command left the browser.
  page.on("websocket", (ws) =>
    ws.on("framesent", (f) => {
      try {
        for (const m of [JSON.parse(String(f.payload))].flat()) if (m?._tag === "Request") receipt.requests.push(m.tag);
      } catch {}
    }),
  );
  await page.addInitScript(() =>
    localStorage.setItem("studio:client-settings:v1", JSON.stringify({ onboardingCompletedAt: "2026-10-12T00:00:00Z" })),
  );
  receipt.indexAsset = (await (await context.request.get(`${origin}/`)).text()).match(/assets\/index-[\w-]+\.js/)?.[0];

  // 1. Settings > Routines with the live routines, at three widths, light and dark.
  for (const [width, height] of [[1440, 1000], [900, 1000], [390, 844]]) {
    await page.setViewportSize({ width, height });
    await page.goto(`${origin}/settings/scheduled-tasks`);
    await page.locator("[data-slot='settings-row']").filter({ has: page.locator("button[aria-label^='Run ']") }).first().waitFor({ timeout: 180000 });
    await page.waitForTimeout(800);
    const rows = await page.locator("[data-slot='settings-row']").evaluateAll((list) =>
      list
        .filter((row) => row.querySelector("[role='switch'], button[aria-label^='Run ']"))
        .map((row) => {
          const r = row.getBoundingClientRect();
          const run = row.querySelector("button[aria-label^='Run ']");
          return {
            height: Math.round(r.height),
            right: Math.round(r.right),
            text: row.innerText,
            run: run ? { label: run.getAttribute("aria-label"), disabled: run.disabled } : null,
          };
        }),
    );
    const heading = await page.getByRole("heading", { name: "Routines" }).first().isVisible();
    const sideways = await overflow();
    NodeAssert.ok(heading, "no Routines heading");
    NodeAssert.ok(rows.length >= 50, `only ${rows.length} routine rows`);
    NodeAssert.equal(sideways, false, `${width}: page scrolls sideways`);
    for (const row of rows) {
      NodeAssert.ok(row.right <= width + 1, `${width}: a row spills past the viewport`);
      NodeAssert.doesNotMatch(row.text, /\d+\/\d+\/\d{4}/, "numeric date");
      NodeAssert.doesNotMatch(row.text, /\b(succeeded|never)\b/, "raw run status");
    }
    const stateWords = /\b(Active|Paused|On request|Listening|Running|Last run failed)\b/;
    const withState = rows.filter((r) => stateWords.test(r.text)).length;
    NodeAssert.equal(withState, rows.length, `${width}: rows without a state badge`);
    const heights = rows.map((r) => r.height).sort((a, b) => a - b);
    const nextShort = rows.filter((r) => /Next (Today|Tomorrow|Mon|Tue|Wed|Thu|Fri|Sat|Sun)/.test(r.text)).length;
    pass(`settings-routines-${width}`, {
      rows: rows.length,
      runButtons: rows.filter((r) => r.run).length,
      runDisabled: rows.filter((r) => r.run?.disabled).length,
      medianHeight: heights[Math.floor(heights.length / 2)],
      maxHeight: heights.at(-1),
      shortNextDates: nextShort,
      sideways,
    });
    await shot(`settings-routines-${width}.png`);
    if (width !== 900) {
      await setDark(true);
      await page.waitForTimeout(150);
      await shot(`settings-routines-${width}-dark.png`);
      await setDark(false);
    }
  }

  // 2. Navigation: settings search finds Routines, and the nav entry opens it.
  await page.setViewportSize({ width: 1440, height: 1000 });
  await page.goto(`${origin}/settings/general`);
  const search = page.getByRole("combobox", { name: "Search settings" });
  await search.waitFor();
  await search.fill("Routines");
  await page.waitForTimeout(300);
  await shot("settings-search-routines.png");
  await page.keyboard.press("Enter");
  await page.waitForURL(/\/settings\/scheduled-tasks/);
  pass("settings-search-opens-routines", { url: page.url().replace(origin, "") });
  await page.goto(`${origin}/settings/general`);
  await page.locator("[data-sidebar='menu-button'], a, button").filter({ hasText: /^Routines$/ }).first().click();
  await page.waitForURL(/\/settings\/scheduled-tasks/);
  pass("settings-nav-entry-opens-routines", { url: page.url().replace(origin, "") });

  // 3. The project's Routines pane, then its Manage routines link.
  for (const [width, height] of [[1440, 1000], [390, 844]]) {
    await page.setViewportSize({ width, height });
    await page.goto(`${origin}/projects/${PROJECT}`);
    await page.waitForTimeout(1500);
    const overview = page.getByRole("button", { name: /^Overview/ });
    if (width < 700 && (await overview.count())) await overview.first().click();
    await page.getByRole("tab", { name: /Routines/ }).first().click();
    const pane = page.locator("#sws-pane-scheduled");
    await pane.locator("li.sws-routine").first().waitFor({ timeout: 180000 });
    await page.waitForTimeout(500);
    const m = await pane.evaluate((root) => {
      const rows = [...root.querySelectorAll("li.sws-routine")];
      const paneRight = root.getBoundingClientRect().right;
      return {
        header: root.querySelector(".sws-routines-head")?.innerText ?? "",
        rows: rows.length,
        heights: rows.map((r) => Math.round(r.getBoundingClientRect().height)),
        spills: rows.filter((r) => r.getBoundingClientRect().right > paneRight + 1).length,
        coordinatorRepeat: rows.filter((r) => /Goes to the coordinator/.test(r.innerText)).length,
        numericDates: rows.filter((r) => /\d+\/\d+\/\d{4}/.test(r.innerText)).length,
        unalignedActions: rows.filter((r) => {
          const tops = new Set([...r.querySelectorAll(".sws-routine-actions button")].map((b) => Math.round(b.getBoundingClientRect().top)));
          return tops.size > 1;
        }).length,
        bareButtons: [...root.querySelectorAll(".sws-routine-actions button")].filter(
          (b) => getComputedStyle(b).borderTopWidth === "0px",
        ).length,
      };
    });
    NodeAssert.match(m.header, /Routines/);
    NodeAssert.match(m.header, /\d+ (active|paused|on request)/);
    NodeAssert.ok(m.rows >= 50, `pane has ${m.rows} rows`);
    NodeAssert.equal(m.spills, 0);
    NodeAssert.equal(m.coordinatorRepeat, 0);
    NodeAssert.equal(m.numericDates, 0);
    NodeAssert.equal(m.unalignedActions, 0);
    NodeAssert.equal(m.bareButtons, 0);
    NodeAssert.equal(await overflow(), false, `${width}: project page scrolls sideways`);
    const sorted = [...m.heights].sort((a, b) => a - b);
    pass(`project-routines-pane-${width}`, {
      header: m.header.split("\n").slice(0, 2).join(" | "),
      rows: m.rows,
      medianHeight: sorted[Math.floor(sorted.length / 2)],
      maxHeight: sorted.at(-1),
    });
    await shot(`project-routines-pane-${width}.png`);
    await setDark(true);
    await page.waitForTimeout(150);
    await shot(`project-routines-pane-${width}-dark.png`);
    await setDark(false);
    if (width === 1440) {
      const create = await pane.getByRole("link", { name: /New routine/ }).getAttribute("href");
      NodeAssert.match(create ?? "", /\/settings\/scheduled-tasks/);
      NodeAssert.match(create ?? "", /template=new/);
      NodeAssert.ok(create.includes(encodeURIComponent(PROJECT)) || create.includes(PROJECT), "New routine link lacks the project");
      pass("new-routine-link-names-project", { href: create });
      await pane.getByRole("link", { name: /Manage routines/ }).click();
      await page.waitForURL(/\/settings\/scheduled-tasks/);
      await page.locator("[data-slot='settings-row']").filter({ has: page.locator("button[aria-label^='Run ']") }).first().waitFor();
      pass("manage-routines-opens-settings", { url: page.url().replace(origin, "") });
      await shot("manage-routines-landing-1440.png");
    }
  }
  const routineCommands = receipt.requests.filter((t) => /^scheduledTasks\.(run|setEnabled|toggle|upsert|delete|update|create|rotateWebhookToken)/i.test(t));
  NodeAssert.deepEqual(routineCommands, [], "a routine command was sent");
  receipt.requestTags = [...new Set(receipt.requests)].sort();
  delete receipt.requests;
  pass("no-routine-commands-sent", { routineCommands });
  receipt.result = "pass";
} catch (error) {
  receipt.result = "fail";
  receipt.error = String(error?.stack ?? error).slice(0, 2000);
  if (page) await page.screenshot({ path: NodePath.join(out, "failure.png") }).catch(() => undefined);
  if (receipt.requests) { receipt.requestTags = [...new Set(receipt.requests)].sort(); delete receipt.requests; }
  process.exitCode = 1;
} finally {
  receipt.finishedAt = new Date().toISOString();
  NodeFS.writeFileSync(NodePath.join(out, "receipt.json"), JSON.stringify(receipt, null, 2));
  await browser.close();
  console.log(`routines read-only check: ${receipt.result}; ${out}`);
}
