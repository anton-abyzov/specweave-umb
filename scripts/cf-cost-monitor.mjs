#!/usr/bin/env node

/**
 * Cloudflare Cost Monitor
 *
 * Queries Cloudflare GraphQL Analytics + REST APIs to calculate
 * current-period usage and projected monthly costs.
 * Sends alerts via Slack webhook and/or macOS notifications.
 *
 * Required env vars:
 *   CF_API_TOKEN        - Cloudflare API token (see setup instructions below)
 *   CF_ACCOUNT_ID       - Your Cloudflare account ID
 *
 * Optional env vars:
 *   SLACK_WEBHOOK_URL   - Slack incoming webhook for alerts
 *   CF_BUDGET_WARN      - Warning threshold in USD (default: 50)
 *   CF_BUDGET_CRIT      - Critical threshold in USD (default: 100)
 *   CF_QUIET            - Set to "1" to only alert on warn/crit (skip green)
 *
 * API Token Permissions needed:
 *   - Account > Account Analytics > Read
 *   - Account > Workers Scripts > Read
 *   - Account > Account Settings > Read
 *
 * Create at: https://dash.cloudflare.com/profile/api-tokens
 * Template: "Read All Resources" covers these, or create custom.
 */

const CF_API = "https://api.cloudflare.com/client/v4";
const CF_GQL = "https://api.cloudflare.com/client/v4/graphql";

// --- Config ---
const ACCOUNT_ID = process.env.CF_ACCOUNT_ID;
const API_TOKEN = process.env.CF_API_TOKEN;
const SLACK_WEBHOOK = process.env.SLACK_WEBHOOK_URL;
const BUDGET_WARN = Number(process.env.CF_BUDGET_WARN || 50);
const BUDGET_CRIT = Number(process.env.CF_BUDGET_CRIT || 100);
const QUIET = process.env.CF_QUIET === "1";

if (!ACCOUNT_ID || !API_TOKEN) {
  console.error("Missing CF_ACCOUNT_ID or CF_API_TOKEN. See script header for setup.");
  process.exit(1);
}

// --- Cloudflare Pricing (Workers Paid Plan, as of 2025) ---
const PRICING = {
  workers: {
    includedRequests: 10_000_000,
    perMillionRequests: 0.30,
    includedCpuMs: 30_000_000,
    perMillionCpuMs: 0.02,
  },
  kv: {
    includedReads: 10_000_000,
    includedWrites: 1_000_000,
    includedDeletes: 1_000_000,
    includedLists: 1_000_000,
    includedStorageMB: 1024,
    perMillionReads: 0.50,
    perMillionWrites: 5.00,
    perMillionDeletes: 5.00,
    perMillionLists: 5.00,
    perGBStorage: 0.50,
  },
  queues: {
    includedOps: 1_000_000,
    perMillionOps: 0.40,
  },
  r2: {
    includedStorageGB: 10,
    includedClassA: 1_000_000,
    includedClassB: 10_000_000,
    perGBStorage: 0.015,
    perMillionClassA: 4.50,
    perMillionClassB: 0.36,
  },
  d1: {
    includedRowsRead: 25_000_000_000,
    includedRowsWritten: 50_000_000,
    includedStorageGB: 5,
    perMillionRowsRead: 0.001,
    perMillionRowsWritten: 1.00,
    perGBStorage: 0.75,
  },
  durableObjects: {
    includedRequests: 1_000_000,
    includedDurationGBs: 400_000,
    perMillionRequests: 0.15,
    perMillionGBs: 0.125,
  },
  ai: {
    // AI pricing varies by model; we estimate based on neuron-seconds
    // Most text models: ~$0.011 per 1K neurons
    perThousandNeurons: 0.011,
  },
};

// --- HTTP helpers ---
async function cfRest(path) {
  const res = await fetch(`${CF_API}${path}`, {
    headers: { Authorization: `Bearer ${API_TOKEN}` },
  });
  const json = await res.json();
  if (!json.success) {
    const errMsg = json.errors?.map((e) => e.message).join(", ") || "Unknown error";
    throw new Error(`CF API ${path}: ${errMsg}`);
  }
  return json.result;
}

async function cfGraphQL(query, variables = {}) {
  const res = await fetch(CF_GQL, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${API_TOKEN}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ query, variables }),
  });
  const json = await res.json();
  if (json.errors?.length) {
    throw new Error(`CF GraphQL: ${json.errors.map((e) => e.message).join(", ")}`);
  }
  return json.data;
}

// --- Date helpers ---
function getBillingPeriod() {
  const now = new Date();
  // Cloudflare billing resets on the 1st of each month
  const start = new Date(now.getFullYear(), now.getMonth(), 1);
  const end = new Date(now.getFullYear(), now.getMonth() + 1, 0); // last day
  const daysInMonth = end.getDate();
  const dayOfMonth = now.getDate();
  const fractionElapsed = dayOfMonth / daysInMonth;

  return {
    start: start.toISOString().split("T")[0] + "T00:00:00Z",
    end: now.toISOString(),
    daysInMonth,
    dayOfMonth,
    fractionElapsed,
  };
}

// --- Data fetchers ---
async function getWorkerAnalytics(period) {
  const query = `query {
    viewer {
      accounts(filter: {accountTag: "${ACCOUNT_ID}"}) {
        workersInvocationsAdaptive(
          limit: 50
          filter: {
            datetimeHour_geq: "${period.start}"
            datetimeHour_leq: "${period.end}"
          }
          orderBy: [sum_requests_DESC]
        ) {
          dimensions { scriptName }
          sum { requests errors subrequests cpuTimeUs duration wallTime }
        }
      }
    }
  }`;

  const data = await cfGraphQL(query);
  const workers = data?.viewer?.accounts?.[0]?.workersInvocationsAdaptive || [];
  return workers.map((w) => ({
    name: w.dimensions.scriptName,
    requests: w.sum.requests,
    errors: w.sum.errors,
    subrequests: w.sum.subrequests,
    cpuTimeMs: Math.round(w.sum.cpuTimeUs / 1000),
    durationMs: w.sum.duration,
  }));
}

async function getDurableObjectAnalytics(period) {
  const query = `query {
    viewer {
      accounts(filter: {accountTag: "${ACCOUNT_ID}"}) {
        durableObjectsInvocationsAdaptiveGroups(
          limit: 50
          filter: {
            datetimeHour_geq: "${period.start}"
            datetimeHour_leq: "${period.end}"
          }
        ) {
          sum { requests wallTime }
        }
      }
    }
  }`;

  try {
    const data = await cfGraphQL(query);
    const groups = data?.viewer?.accounts?.[0]?.durableObjectsInvocationsAdaptiveGroups || [];
    return groups.reduce(
      (acc, g) => ({
        requests: acc.requests + (g.sum.requests || 0),
        durationGBs: acc.durationGBs + (g.sum.wallTime || 0) / 1e9, // approx
      }),
      { requests: 0, durationGBs: 0 }
    );
  } catch {
    return { requests: 0, durationGBs: 0 };
  }
}

async function getKVAnalytics(period) {
  const query = `query {
    viewer {
      accounts(filter: {accountTag: "${ACCOUNT_ID}"}) {
        workersKvStorageAdaptiveGroups(
          limit: 50
          filter: {
            datetimeHour_geq: "${period.start}"
            datetimeHour_leq: "${period.end}"
          }
        ) {
          sum { readOperations writeOperations deleteOperations listOperations }
        }
      }
    }
  }`;

  try {
    const data = await cfGraphQL(query);
    const groups = data?.viewer?.accounts?.[0]?.workersKvStorageAdaptiveGroups || [];
    return groups.reduce(
      (acc, g) => ({
        reads: acc.reads + (g.sum.readOperations || 0),
        writes: acc.writes + (g.sum.writeOperations || 0),
        deletes: acc.deletes + (g.sum.deleteOperations || 0),
        lists: acc.lists + (g.sum.listOperations || 0),
      }),
      { reads: 0, writes: 0, deletes: 0, lists: 0 }
    );
  } catch {
    return { reads: 0, writes: 0, deletes: 0, lists: 0 };
  }
}

async function getR2Analytics() {
  try {
    const buckets = await cfRest(`/accounts/${ACCOUNT_ID}/r2/buckets`);
    return (buckets?.buckets || []).map((b) => ({
      name: b.name,
      storageGB: (b.storage_usage || 0) / 1e9,
    }));
  } catch {
    return [];
  }
}

async function getD1Analytics() {
  try {
    const dbs = await cfRest(`/accounts/${ACCOUNT_ID}/d1/database`);
    return (dbs || []).map((db) => ({
      name: db.name,
      sizeMB: (db.file_size || 0) / 1e6,
    }));
  } catch {
    return [];
  }
}

// --- Cost calculators ---
function calcOverageCost(used, included, perMillionRate) {
  const overage = Math.max(0, used - included);
  return (overage / 1_000_000) * perMillionRate;
}

function calcStorageCost(usedGB, includedGB, perGBRate) {
  return Math.max(0, usedGB - includedGB) * perGBRate;
}

function calculateCosts(usage, period) {
  const p = PRICING;
  const proj = 1 / period.fractionElapsed; // projection multiplier

  const totalRequests = usage.workers.reduce((s, w) => s + w.requests, 0);
  const totalCpuMs = usage.workers.reduce((s, w) => s + w.cpuTimeMs, 0);
  const totalErrors = usage.workers.reduce((s, w) => s + w.errors, 0);

  // Workers
  const workerReqCost = calcOverageCost(totalRequests, p.workers.includedRequests, p.workers.perMillionRequests);
  const workerCpuCost = calcOverageCost(totalCpuMs, p.workers.includedCpuMs, p.workers.perMillionCpuMs);

  // KV
  const kvReadCost = calcOverageCost(usage.kv.reads, p.kv.includedReads, p.kv.perMillionReads);
  const kvWriteCost = calcOverageCost(usage.kv.writes, p.kv.includedWrites, p.kv.perMillionWrites);
  const kvDeleteCost = calcOverageCost(usage.kv.deletes, p.kv.includedDeletes, p.kv.perMillionDeletes);
  const kvListCost = calcOverageCost(usage.kv.lists, p.kv.includedLists, p.kv.perMillionLists);

  // Durable Objects
  const doReqCost = calcOverageCost(
    usage.durableObjects.requests,
    p.durableObjects.includedRequests,
    p.durableObjects.perMillionRequests
  );

  // R2 storage
  const r2StorageGB = usage.r2.reduce((s, b) => s + b.storageGB, 0);
  const r2StorageCost = calcStorageCost(r2StorageGB, p.r2.includedStorageGB, p.r2.perGBStorage);

  // D1 storage
  const d1StorageGB = usage.d1.reduce((s, db) => s + db.sizeMB / 1024, 0);
  const d1StorageCost = calcStorageCost(d1StorageGB, p.d1.includedStorageGB, p.d1.perGBStorage);

  const basePlan = 5; // Workers Paid plan

  const items = [
    { service: "Workers Paid Plan", actual: basePlan, projected: basePlan },
    { service: "Worker Requests", actual: workerReqCost, projected: workerReqCost * proj },
    { service: "Worker CPU Time", actual: workerCpuCost, projected: workerCpuCost * proj },
    { service: "KV Reads", actual: kvReadCost, projected: kvReadCost * proj },
    { service: "KV Writes", actual: kvWriteCost, projected: kvWriteCost * proj },
    { service: "KV Deletes+Lists", actual: kvDeleteCost + kvListCost, projected: (kvDeleteCost + kvListCost) * proj },
    { service: "Durable Objects", actual: doReqCost, projected: doReqCost * proj },
    { service: "R2 Storage", actual: r2StorageCost, projected: r2StorageCost },
    { service: "D1 Storage", actual: d1StorageCost, projected: d1StorageCost },
  ];

  const actualTotal = items.reduce((s, i) => s + i.actual, 0);
  const projectedTotal = items.reduce((s, i) => s + i.projected, 0);

  return {
    items: items.filter((i) => i.actual > 0.01 || i.service === "Workers Paid Plan"),
    actualTotal,
    projectedTotal,
    totalRequests,
    totalCpuMs,
    totalErrors,
    period,
  };
}

// --- Formatting ---
function formatReport(costs, usage) {
  const { period } = costs;
  const level =
    costs.projectedTotal >= BUDGET_CRIT ? "CRITICAL" : costs.projectedTotal >= BUDGET_WARN ? "WARNING" : "OK";

  const emoji = level === "CRITICAL" ? "!!" : level === "WARNING" ? "!" : "";

  let report = `${emoji} Cloudflare Cost Report (Day ${period.dayOfMonth}/${period.daysInMonth})\n`;
  report += `${"=".repeat(55)}\n\n`;

  report += `Status: ${level} | Budget: warn=$${BUDGET_WARN} crit=$${BUDGET_CRIT}\n`;
  report += `Actual so far: $${costs.actualTotal.toFixed(2)}\n`;
  report += `Projected month-end: $${costs.projectedTotal.toFixed(2)}\n\n`;

  report += `Service                  Actual    Projected\n`;
  report += `${"-".repeat(55)}\n`;
  for (const item of costs.items) {
    const name = item.service.padEnd(24);
    const actual = `$${item.actual.toFixed(2)}`.padStart(10);
    const proj = `$${item.projected.toFixed(2)}`.padStart(12);
    report += `${name}${actual}${proj}\n`;
  }
  report += `${"-".repeat(55)}\n`;
  report += `${"TOTAL".padEnd(24)}${"$" + costs.actualTotal.toFixed(2)}`.padStart(10);
  report += `${"$" + costs.projectedTotal.toFixed(2)}`.padStart(12) + "\n\n";

  // Per-worker breakdown
  report += `Worker Breakdown (top 5):\n`;
  const topWorkers = [...usage.workers].sort((a, b) => b.requests - a.requests).slice(0, 5);
  for (const w of topWorkers) {
    const errRate = w.requests > 0 ? ((w.errors / w.requests) * 100).toFixed(1) : "0.0";
    report += `  ${w.name}: ${w.requests.toLocaleString()} req, ${w.errors.toLocaleString()} err (${errRate}%), ${w.cpuTimeMs.toLocaleString()}ms CPU\n`;
  }

  // Alerts
  if (costs.totalErrors > 10_000) {
    report += `\n!! HIGH ERROR COUNT: ${costs.totalErrors.toLocaleString()} errors this period\n`;
    report += `   This may indicate crash loops driving up costs.\n`;
  }

  return { report, level };
}

function formatSlackMessage(costs, usage) {
  const { period } = costs;
  const level =
    costs.projectedTotal >= BUDGET_CRIT ? "critical" : costs.projectedTotal >= BUDGET_WARN ? "warning" : "ok";

  const color = level === "critical" ? "#dc3545" : level === "warning" ? "#ffc107" : "#28a745";
  const icon = level === "critical" ? ":rotating_light:" : level === "warning" ? ":warning:" : ":white_check_mark:";

  const topWorkers = [...usage.workers]
    .sort((a, b) => b.requests - a.requests)
    .slice(0, 3)
    .map((w) => {
      const errRate = w.requests > 0 ? ((w.errors / w.requests) * 100).toFixed(1) : "0";
      return `*${w.name}*: ${w.requests.toLocaleString()} req (${errRate}% err)`;
    })
    .join("\n");

  const costLines = costs.items
    .filter((i) => i.projected > 0.5)
    .map((i) => `${i.service}: $${i.actual.toFixed(2)} actual / $${i.projected.toFixed(2)} projected`)
    .join("\n");

  return {
    attachments: [
      {
        color,
        blocks: [
          {
            type: "header",
            text: {
              type: "plain_text",
              text: `${icon} CF Cost Report - Day ${period.dayOfMonth}/${period.daysInMonth}`,
            },
          },
          {
            type: "section",
            fields: [
              { type: "mrkdwn", text: `*Actual:*\n$${costs.actualTotal.toFixed(2)}` },
              { type: "mrkdwn", text: `*Projected:*\n$${costs.projectedTotal.toFixed(2)}` },
              { type: "mrkdwn", text: `*Budget Warn:*\n$${BUDGET_WARN}` },
              { type: "mrkdwn", text: `*Budget Crit:*\n$${BUDGET_CRIT}` },
            ],
          },
          {
            type: "section",
            text: { type: "mrkdwn", text: `*Cost Breakdown:*\n${costLines}` },
          },
          {
            type: "section",
            text: { type: "mrkdwn", text: `*Top Workers:*\n${topWorkers}` },
          },
        ],
      },
    ],
  };
}

// --- Notification senders ---
async function sendSlack(costs, usage) {
  if (!SLACK_WEBHOOK) return;

  const payload = formatSlackMessage(costs, usage);
  const res = await fetch(SLACK_WEBHOOK, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    console.error(`Slack webhook failed: ${res.status} ${await res.text()}`);
  }
}

async function sendMacOSNotification(costs) {
  const level =
    costs.projectedTotal >= BUDGET_CRIT ? "CRITICAL" : costs.projectedTotal >= BUDGET_WARN ? "WARNING" : "OK";

  if (QUIET && level === "OK") return;

  const title = `CF Costs: ${level}`;
  const msg = `Projected: $${costs.projectedTotal.toFixed(2)} (actual: $${costs.actualTotal.toFixed(2)})`;

  const { execSync } = await import("child_process");
  try {
    execSync(
      `osascript -e 'display notification "${msg}" with title "${title}" sound name "Glass"'`,
      { stdio: "ignore" }
    );
  } catch {
    // terminal-notifier fallback
    try {
      execSync(
        `terminal-notifier -title "${title}" -message "${msg}" -sound Glass 2>/dev/null`,
        { stdio: "ignore" }
      );
    } catch {
      // No notification method available, that's fine
    }
  }
}

// --- Main ---
async function main() {
  console.log(`Cloudflare Cost Monitor - ${new Date().toISOString()}\n`);

  const period = getBillingPeriod();
  console.log(`Billing period: Day ${period.dayOfMonth} of ${period.daysInMonth} (${(period.fractionElapsed * 100).toFixed(0)}% elapsed)\n`);

  // Fetch all usage data in parallel
  console.log("Fetching usage data...");
  const [workers, kv, durableObjects, r2, d1] = await Promise.all([
    getWorkerAnalytics(period),
    getKVAnalytics(period),
    getDurableObjectAnalytics(period),
    getR2Analytics(),
    getD1Analytics(),
  ]);

  const usage = { workers, kv, durableObjects, r2, d1 };

  // Calculate costs
  const costs = calculateCosts(usage, period);

  // Format and print report
  const { report, level } = formatReport(costs, usage);
  console.log(report);

  // Send notifications
  await Promise.all([sendSlack(costs, usage), sendMacOSNotification(costs)]);

  if (SLACK_WEBHOOK) {
    console.log(`Slack notification sent (level: ${level})`);
  }

  // Exit with non-zero if critical (useful for CI/scripts)
  if (level === "CRITICAL") process.exit(2);
  if (level === "WARNING") process.exit(1);
}

main().catch((err) => {
  console.error("Fatal error:", err.message);
  process.exit(3);
});
