// Headless routines layout, search and navigation check of the INSTALLED SpecWithCode build,
// served by the app's own bundled server in private throwaway state with synthetic routines.
// No real routine is read, run, enabled, paused or deleted: the live service is not contacted.
// Every synthetic routine is manual, paused, or scheduled outside the run window, and every
// provider is disabled, so nothing can start. Usage: node routines-private-installed-check.mjs <out-dir>
import * as NodeAssert from "node:assert/strict";
import { spawn } from "node:child_process";
import { createRequire } from "node:module";
import * as NodeFS from "node:fs";
import { homedir, tmpdir } from "node:os";
import * as NodePath from "node:path";
import { createServer } from "node:net";

process.env.PWDEBUG = "0";
process.env.PLAYWRIGHT_HTML_OPEN = "never";
const out = NodePath.resolve(process.argv[2] ?? "./private-run");
NodeFS.mkdirSync(out, { recursive: true });
const app = process.env.SPECWITHCODE_APP ?? "/Applications/SpecWithCode.app";
const entry = `${app}/Contents/Resources/app.asar/apps/server/dist/bin.mjs`;
const privateRoot = NodePath.join(homedir(), ".local/share/specweave-studio/verification/routines-installed");
NodeFS.mkdirSync(privateRoot, { recursive: true, mode: 0o700 });
const state = NodeFS.mkdtempSync(NodePath.join(privateRoot, "state-"));
const workspace = NodeFS.mkdtempSync(NodePath.join(tmpdir(), "swc-routines-ws-"));
NodeFS.mkdirSync(NodePath.join(state, "userdata"));
NodeFS.writeFileSync(NodePath.join(state, "userdata/settings.json"), JSON.stringify({
  providers: Object.fromEntries(
    ["claudeAgent", "codex", "cursor", "grok", "pi", "opencode", "antigravity"].map((id) => [id, { enabled: false }]),
  ),
}));
const port = await new Promise((done) => {
  const s = createServer();
  s.listen(0, "127.0.0.1", () => { const { port } = s.address(); s.close(() => done(port)); });
});
const origin = `http://127.0.0.1:${port}`;
const child = spawn(`${app}/Contents/MacOS/SpecWithCode`,
  [entry, "serve", "--no-browser", "--host", "127.0.0.1", "--port", String(port), "--base-dir", state],
  { cwd: state, env: { ...process.env, ELECTRON_RUN_AS_NODE: "1", STUDIO_DISABLE_AUTO_UPDATE: "true", SPECWEAVE_STUDIO_THREAD_ID: "" },
    stdio: ["ignore", "pipe", "pipe"] });
let output = "";
const credential = new Promise((done, reject) => {
  const timer = setTimeout(() => reject(new Error("startup timed out")), 90000);
  const observe = (c) => { output += c; const m = output.match(/(?:^|\n)Token: ([^\s]+)/); if (m) { clearTimeout(timer); done(m[1]); } };
  child.stdout.on("data", observe); child.stderr.on("data", observe);
  child.once("exit", (code) => { clearTimeout(timer); reject(new Error(`server exited ${code}: ${output.replace(/Token: \S+/g, "").slice(-1500)}`)); });
});
const req = createRequire(
  "/Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specweave-studio/node_modules/.pnpm/playwright-core@1.60.0/node_modules/playwright-core/package.json",
);
const { chromium } = req("playwright-core");
const PROJECT = "routines-check";
const MIN_ROWS = 50;
const receipt = {
  kind: "installed build, private throwaway state, synthetic routines",
  app, entry, pid: child.pid, state, origin, headless: true, project: PROJECT,
  startedAt: new Date().toISOString(), checks: [], screenshots: [], requests: [],
};
const pass = (name, detail) => receipt.checks.push({ name, ok: true, ...detail });
let browser, page;
const shot = async (name, opts = {}) => {
  const file = NodePath.join(out, name);
  await page.screenshot({ path: file, ...opts });
  receipt.screenshots.push(file);
};
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

// Synthetic routines. Enabled ones are manual, once in 2027, or fixed to a weekday and month day
// outside this run; the rest are paused. Providers are disabled besides.
function syntheticRoutines() {
  const base = { prompt: "Synthetic routine for a layout check. Do nothing.", projectId: PROJECT,
    workspaceStrategy: { type: "root" }, modelSelection: { instanceId: "claudeAgent", model: "claude-opus-5-5" },
    runtimeMode: "approval-required", interactionMode: "default" };
  const today = new Date().getDay();
  const otherDay = (today + 3) % 7;
  const topics = ["Dependency audit", "Release notes draft", "Docs link check", "Flaky test triage", "Changelog tidy",
    "Issue label sweep", "Bundle size report", "License scan", "Stale branch report", "Accessibility pass"];
  const list = [];
  for (let i = 0; i < 60; i++) {
    const topic = `${topics[i % topics.length]} ${String(i + 1).padStart(2, "0")}`;
    const kind = i % 6;
    const schedule =
      kind === 0 ? { type: "manual" }
      : kind === 1 ? { type: "once", at: `2027-0${(i % 9) + 1}-15T09:30:00Z` }
      : kind === 2 ? { type: "fixed_time", timeOfDay: "03:17", weekdays: [otherDay] }
      : kind === 3 ? { type: "interval", everyMs: 7 * 24 * 3600 * 1000 }
      : kind === 4 ? { type: "monthly", dayOfMonth: 1, timeOfDay: "04:05" }
      : { type: "fixed_time", timeOfDay: "09:00" };
    // Interval and daily rows are always paused; the others alternate.
    const enabled = kind === 3 || kind === 5 ? false : i % 4 !== 3;
    list.push({ ...base, title: topic, enabled, schedule });
  }
  list.push({ ...base, enabled: false, schedule: { type: "fixed_time", timeOfDay: "06:45", weekdays: [1, 3, 5] },
    title: "Weekly cross-repository dependency and security advisory review with a deliberately long routine name for wrapping" });
  list.push({ ...base, enabled: true, schedule: { type: "manual" }, title: "Ask before running",
    prompt: "A long prompt line. ".repeat(40).trim() });
  return list;
}
try {
  const token = await credential;
  browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({ viewport: { width: 1440, height: 1000 }, reducedMotion: "reduce" });
  NodeAssert.equal((await context.request.post(`${origin}/api/auth/browser-session`, {
    data: { credential: token }, headers: { Origin: origin } })).status(), 200);
  // One socket for setup RPCs, outside the page, so the page's own requests stay separate.
  const ticket = (await (await context.request.post(`${origin}/api/auth/websocket-ticket`, { headers: { Origin: origin } })).json()).ticket;
  const wsUrl = new URL(origin); wsUrl.protocol = "ws:"; wsUrl.pathname = "/ws";
  wsUrl.searchParams.set("wsTicket", ticket); wsUrl.searchParams.set("orchestrationProtocol", "2");
  const ws = new WebSocket(wsUrl);
  await new Promise((done, reject) => { ws.addEventListener("open", done); ws.addEventListener("error", reject); });
  const pending = new Map();
  ws.addEventListener("message", (e) => {
    for (const item of [JSON.parse(e.data)].flat()) {
      const wait = item._tag === "Exit" && pending.get(String(item.requestId));
      if (!wait) continue;
      pending.delete(String(item.requestId));
      item.exit?._tag === "Success" ? wait.done(item.exit.value) : wait.reject(new Error(`RPC ${wait.tag}: ${JSON.stringify(item.exit).slice(0, 600)}`));
    }
  });
  let nextId = 1;
  const rpc = (tag, payload) => new Promise((done, reject) => {
    const id = String(nextId++);
    const timer = setTimeout(() => { pending.delete(id); reject(new Error(`RPC timeout ${tag}`)); }, 30000);
    pending.set(id, { tag, done: (v) => { clearTimeout(timer); done(v); }, reject: (e) => { clearTimeout(timer); reject(e); } });
    ws.send(JSON.stringify({ _tag: "Request", id, tag, payload, headers: [] }));
  });
  const config = await rpc("server.getConfig", {});
  receipt.version = config.version ?? config.environment?.serverVersion ?? config.environment?.version ?? null;
  await rpc("projects.mutate", { type: "project.create", commandId: "rc-project", projectId: PROJECT,
    title: "Routines check", workspaceRoot: workspace, origin: "user" });
  const routines = syntheticRoutines();
  for (const routine of routines) await rpc("scheduledTasks.upsert", routine);
  const listed = await rpc("scheduledTasks.list", {});
  const tasks = listed.tasks ?? listed;
  receipt.synthetic = {
    created: tasks.length,
    enabled: tasks.filter((t) => t.enabled).length,
    byType: tasks.reduce((acc, t) => ({ ...acc, [t.schedule.type]: (acc[t.schedule.type] ?? 0) + 1 }), {}),
  };
  NodeAssert.equal(tasks.length, routines.length);
  const fingerprint = (list) => JSON.stringify(list.map((t) => [t.id, t.enabled, t.lastRunStatus ?? t.lastRun?.status ?? null, t.lastRunAt ?? null]).sort());
  const before = fingerprint(tasks);

  page = await context.newPage();
  page.setDefaultTimeout(60000);
  page.on("websocket", (socket) =>
    socket.on("framesent", (f) => {
      try {
        for (const m of [JSON.parse(String(f.payload))].flat()) if (m?._tag === "Request") receipt.requests.push(m.tag);
      } catch {}
    }),
  );
  await page.addInitScript(() =>
    localStorage.setItem("studio:client-settings:v1", JSON.stringify({ onboardingCompletedAt: "2026-10-12T00:00:00Z" })),
  );
  receipt.indexAsset = (await (await context.request.get(`${origin}/`)).text()).match(/assets\/index-[\w-]+\.js/)?.[0];

  // 1. Settings > Routines with the synthetic routines, at three widths, light and dark.
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
    NodeAssert.ok(rows.length >= MIN_ROWS, `only ${rows.length} routine rows`);
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
  // The project route takes a project key, so open the project from the sidebar once.
  await page.setViewportSize({ width: 1440, height: 1000 });
  await page.goto(`${origin}/`);
  await page.getByText("Routines check", { exact: true }).first().click();
  await page.waitForURL(/\/projects\//);
  const projectUrl = page.url();
  receipt.projectRoute = projectUrl.replace(origin, "");
  for (const [width, height] of [[1440, 1000], [390, 844]]) {
    await page.setViewportSize({ width, height });
    await page.goto(projectUrl);
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
    NodeAssert.ok(m.rows >= MIN_ROWS, `pane has ${m.rows} rows`);
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
  const routineCommands = receipt.requests.filter((t) => /^scheduledTasks\.(run|toggle|upsert|delete|update|create)/i.test(t));
  NodeAssert.deepEqual(routineCommands, [], "a routine command was sent");
  receipt.requestTags = [...new Set(receipt.requests)].sort();
  pass("no-routine-commands-sent", { routineCommands });
  // The synthetic routines are as created: none ran, toggled or disappeared.
  const afterList = await rpc("scheduledTasks.list", {});
  NodeAssert.equal(fingerprint(afterList.tasks ?? afterList), before, "a routine changed during the check");
  pass("routines-unchanged-after-check", { routines: (afterList.tasks ?? afterList).length });
  ws.close();
  receipt.result = "pass";
} catch (error) {
  receipt.result = "fail";
  receipt.error = String(error?.stack ?? error).slice(0, 2000);
  if (page) await page.screenshot({ path: NodePath.join(out, "failure.png") }).catch(() => undefined);
  process.exitCode = 1;
} finally {
  if (receipt.requests) { receipt.requestTags = [...new Set(receipt.requests)].sort(); delete receipt.requests; }
  receipt.finishedAt = new Date().toISOString();
  NodeFS.writeFileSync(NodePath.join(out, "receipt.json"), JSON.stringify(receipt, null, 2) + "\n");
  await browser?.close();
  if (child.exitCode === null) child.kill("SIGTERM");
  console.log(`routines private installed check: ${receipt.result}; ${out}`);
}
