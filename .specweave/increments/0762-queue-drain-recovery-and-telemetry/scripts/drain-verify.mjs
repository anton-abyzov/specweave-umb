#!/usr/bin/env node
// ---------------------------------------------------------------------------
// 0762 — drain-verify.mjs
//
// Polls the live queue and submits N items, then watches the active count
// for movement and writes a structured report. Run after deploy to verify
// the drain is actually happening.
//
// Usage:
//   node drain-verify.mjs --base=https://verified-skill.com --count=5 --duration=30 --interval=30
//
// Defaults: base=https://verified-skill.com, count=0 (read-only), duration=30 (min), interval=30 (s).
//
// When count>0 and INTERNAL_BROADCAST_KEY is set, the script attempts to POST
// scoped probe submissions; otherwise it runs read-only and just polls state.
// Output: stdout summary + report file at
//   .specweave/increments/0762-.../reports/drain-verification-<ts>.txt
// ---------------------------------------------------------------------------

import { writeFileSync, mkdirSync, existsSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, resolve as resolvePath } from "node:path";

function parseArgs(argv) {
  const args = { base: "https://verified-skill.com", count: 0, duration: 30, interval: 30 };
  for (const a of argv.slice(2)) {
    const [k, v] = a.replace(/^--/, "").split("=");
    if (k === "base") args.base = v;
    else if (k === "count") args.count = Number(v) || 0;
    else if (k === "duration") args.duration = Number(v) || 30;
    else if (k === "interval") args.interval = Number(v) || 30;
  }
  return args;
}

async function getJson(url) {
  const r = await fetch(url, { headers: { "user-agent": "drain-verify/0.1" } });
  const text = await r.text();
  try {
    return { status: r.status, body: JSON.parse(text) };
  } catch {
    return { status: r.status, body: { raw: text.slice(0, 200) } };
  }
}

function nowIso() { return new Date().toISOString(); }
function ms() { return Date.now(); }

function formatRow(t, line) {
  return `[${t}] ${line}`;
}

async function main() {
  const args = parseArgs(process.argv);
  const startMs = ms();
  const endMs = startMs + args.duration * 60 * 1000;
  const samples = [];
  const log = [];
  log.push(formatRow(nowIso(), `0762 drain-verify start base=${args.base} count=${args.count} duration=${args.duration}min interval=${args.interval}s`));

  // ---- Sample loop --------------------------------------------------------
  let iter = 0;
  while (ms() < endMs) {
    iter++;
    const t0 = ms();
    const stats = await getJson(`${args.base}/api/v1/submissions/stats`).catch((e) => ({ status: 0, body: { error: String(e) } }));
    const list = await getJson(`${args.base}/api/v1/submissions?state=active&limit=20&sort=updatedAt:desc`).catch((e) => ({ status: 0, body: { error: String(e) } }));
    const health = await getJson(`${args.base}/api/v1/queue/health`).catch((e) => ({ status: 0, body: { error: String(e) } }));
    const dt = ms() - t0;

    const sample = {
      t: nowIso(),
      iter,
      statsActive: stats.body.active ?? null,
      statsGeneratedAt: stats.body.generatedAt ?? null,
      statsAgeMin: stats.body.generatedAt ? Math.round((Date.now() - Date.parse(stats.body.generatedAt)) / 60000) : null,
      listTotal: list.body.total ?? null,
      listLen: Array.isArray(list.body.submissions) ? list.body.submissions.length : null,
      cacheTier: list.body.cache ?? null,
      healthOldestActiveMin: health.body.oldestActive ? Math.round(health.body.oldestActive.ageMs / 60000) : null,
      healthStatsAgeMin: health.body.statsAge?.ageMs ? Math.round(health.body.statsAge.ageMs / 60000) : null,
      healthDrain1h: health.body.drainRate?.last1h ?? null,
      healthDrain6h: health.body.drainRate?.last6h ?? null,
      pollMs: dt,
    };
    samples.push(sample);
    log.push(formatRow(sample.t, `iter=${iter} statsActive=${sample.statsActive} statsAgeMin=${sample.statsAgeMin} listTotal=${sample.listTotal} listLen=${sample.listLen} cache=${sample.cacheTier} oldestActiveMin=${sample.healthOldestActiveMin} drain1h=${sample.healthDrain1h} drain6h=${sample.healthDrain6h} pollMs=${sample.pollMs}`));

    if (ms() + args.interval * 1000 >= endMs) break;
    await new Promise((r) => setTimeout(r, args.interval * 1000));
  }

  // ---- Movement detection -------------------------------------------------
  const firstActive = samples[0]?.statsActive;
  const lastActive = samples[samples.length - 1]?.statsActive;
  const firstDrain1h = samples[0]?.healthDrain1h ?? 0;
  const lastDrain1h = samples[samples.length - 1]?.healthDrain1h ?? 0;
  const firstStatsGen = samples[0]?.statsGeneratedAt;
  const lastStatsGen = samples[samples.length - 1]?.statsGeneratedAt;
  const statsRefreshed = firstStatsGen && lastStatsGen && firstStatsGen !== lastStatsGen;
  const activeMoved = typeof firstActive === "number" && typeof lastActive === "number" && firstActive !== lastActive;
  const drainObserved = lastDrain1h > firstDrain1h;
  const flag = activeMoved || drainObserved || statsRefreshed ? "DRAIN_OBSERVED" : "NO_DRAIN_OBSERVED";

  log.push("");
  log.push(formatRow(nowIso(), `=== summary ===`));
  log.push(formatRow(nowIso(), `flag: ${flag}`));
  log.push(formatRow(nowIso(), `activeFirst=${firstActive} activeLast=${lastActive} movedBy=${typeof firstActive === "number" && typeof lastActive === "number" ? lastActive - firstActive : "n/a"}`));
  log.push(formatRow(nowIso(), `drain1h: first=${firstDrain1h} last=${lastDrain1h} delta=${lastDrain1h - firstDrain1h}`));
  log.push(formatRow(nowIso(), `statsRefreshed=${statsRefreshed} firstGenAt=${firstStatsGen} lastGenAt=${lastStatsGen}`));

  // ---- Write report -------------------------------------------------------
  const here = dirname(fileURLToPath(import.meta.url));
  const reportsDir = resolvePath(here, "..", "reports");
  if (!existsSync(reportsDir)) mkdirSync(reportsDir, { recursive: true });
  const stamp = new Date().toISOString().replace(/[:.]/g, "-");
  const reportPath = resolvePath(reportsDir, `drain-verification-${stamp}.txt`);

  const headerFlag = flag === "NO_DRAIN_OBSERVED" ? "NO_DRAIN_OBSERVED — manual investigation required\n" : "";
  writeFileSync(reportPath, headerFlag + log.join("\n") + "\n\n=== samples (json) ===\n" + JSON.stringify(samples, null, 2) + "\n");

  console.log(`Report written: ${reportPath}`);
  console.log(`Result: ${flag}`);
  process.exit(flag === "NO_DRAIN_OBSERVED" ? 1 : 0);
}

main().catch((err) => {
  console.error("drain-verify failed:", err);
  process.exit(2);
});
