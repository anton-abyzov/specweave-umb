---
increment: 0719-cron-offload-stats-to-vm
title: "Cron Offload — Stats Compute to Hetzner VM"
---

# Architecture & Implementation Plan

## Design

### Architecture diagram (text)

```
BEFORE (today, post-0713):
┌──────────────────────────────────────────────┐
│ CF Worker scheduled() handler — */10 cron    │
│  ctx.waitUntil(block-1):                     │
│   prewarm → platformStats → queueStats       │ ← these throw or
│   → listWarmup → skillsCache → publishCache  │   eat CPU budget
│  ctx.waitUntil(block-2):                     │
│   enrichment → recovery×4 → reconcile×2      │
└────────────┬─────────────────────────────────┘
             ↓ writes
        SUBMISSIONS_KV / platform-stats / submissions:stats-cache / etc.

AFTER (0719):
┌──────────────────────────────┐    ┌──────────────────────────────┐
│ Hetzner VM (ARM64)           │    │ CF Worker scheduled handler  │
│  systemd timer — */10        │    │  ctx.waitUntil(block-2 only):│
│  → stats-compute.js          │    │   enrichment → recovery×4    │
│    Prisma + Neon connection  │    │   → reconcile×2              │
│    computes 5 payloads       │    └──────────────────────────────┘
│  → POST X-Internal-Key       │                  │
└──────┬───────────────────────┘                  ↓
       ↓ HTTPS                              writes via existing bindings
       ↓                                     (SUBMISSION_QUEUE.send,
┌──────────────────────────────┐              KV mutations from request
│ CF Worker — write-only       │              context, etc.)
│   /api/v1/internal/stats/*   │
│   /api/v1/internal/cache/*   │
│   X-Internal-Key auth        │
│   → SUBMISSIONS_KV.put(...)  │
└──────────────────────────────┘
```

### VM-side module: `crawl-worker/sources/stats-compute.js`

Single-file Node module exporting `runStatsCompute(env)`. Pseudocode:

```js
import { PrismaClient } from "@prisma/client";

export async function runStatsCompute(env) {
  const prisma = new PrismaClient();
  try {
    const [queue, platform, lists, skills, publishers] = await Promise.allSettled([
      computeQueueStats(prisma),
      computePlatformStats(prisma),
      computeListWarmup(prisma),
      computeSkillsCache(prisma),
      computePublishersCache(prisma),
    ]);
    await Promise.allSettled([
      postStats("/api/v1/internal/stats/queue", queue, env),
      postStats("/api/v1/internal/stats/platform", platform, env),
      postStats("/api/v1/internal/stats/queue-list-warmup", lists, env),
      postStats("/api/v1/internal/cache/skills", skills, env),
      postStats("/api/v1/internal/cache/publishers", publishers, env),
    ]);
  } finally {
    await prisma.$disconnect();
  }
}

async function postStats(path, settled, env) {
  if (settled.status !== "fulfilled" || !settled.value) return;
  const res = await fetch(`https://verified-skill.com${path}`, {
    method: "POST",
    headers: {
      "X-Internal-Key": env.INTERNAL_BROADCAST_KEY,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(settled.value),
  });
  if (!res.ok) console.error(`[stats-compute] POST ${path} → ${res.status}`);
}
```

Each `compute*` function reuses the same SQL/Prisma logic that lives in `src/lib/cron/*-refresh.ts` today. We can either:

- **Option A (preferred)**: extract the pure compute functions into a shared package (e.g., `packages/stats-compute/`) consumed by both the VM script and the CF worker (so 0713's tests still cover them).
- **Option B (faster)**: copy the SQL into the VM module. Trade-off: drift risk if CF code is modified later. Acceptable as long as 0719 test suite covers the VM payload shape against the CF endpoint contract.

Decision: **Option B for ship-1**, refactor to A in a follow-up if stats logic evolves.

### CF-side endpoints (5 total)

Each endpoint follows an identical pattern (write-only, auth-gated, schema-validated):

```ts
// src/app/api/v1/internal/stats/queue/route.ts
import { NextRequest, NextResponse } from "next/server";
import { getCloudflareContext } from "@opennextjs/cloudflare";

export async function POST(request: NextRequest) {
  const { env } = await getCloudflareContext({ async: true });
  if (request.headers.get("X-Internal-Key") !== env.INTERNAL_BROADCAST_KEY) {
    return NextResponse.json({ error: "unauthorized" }, { status: 401 });
  }
  let body;
  try { body = await request.json(); }
  catch { return NextResponse.json({ error: "invalid_json" }, { status: 400 }); }

  // Validate shape
  if (!isQueueStatsPayload(body)) {
    return NextResponse.json({ error: "invalid_payload" }, { status: 400 });
  }

  await env.SUBMISSIONS_KV.put("submissions:stats-cache", JSON.stringify(body));
  return NextResponse.json({ ok: true, generatedAt: body.generatedAt });
}
```

The 5 endpoints differ only in:
- KV key (`submissions:stats-cache`, `platform:stats`, `submissions:list:<filter>::*`, `skills:cache`, `publishers:cache`)
- Schema validator function

Shared validation helpers live in `src/app/api/v1/internal/_shared/validators.ts` to keep endpoints under 30 LOC each.

### CF-side build-worker-entry.ts cleanup (US-002)

Remove these lines from `scripts/build-worker-entry.ts`:

```ts
// (delete imports)
import { refreshPlatformStats } from "../src/lib/cron/stats-refresh.js";
import { refreshQueueStats } from "../src/lib/cron/queue-stats-refresh.js";
import { warmQueueListCache } from "../src/lib/cron/queue-list-warmup.js";
import { refreshSkillsCache } from "../src/lib/cron/skills-cache-refresh.js";
import { refreshPublishersCache } from "../src/lib/cron/publishers-cache-refresh.js";

// (delete the entire first ctx.waitUntil block — block-1 stats chain)
```

Source files (`stats-refresh.ts` etc.) are NOT deleted — they remain importable for ad-hoc use, future re-wiring, and so 0713's 13 unit tests still target real code.

### CPU-budget band-aid removal (US-003)

After 24h of clean ticks, in a follow-up commit:

```diff
-  // 0713: bump per-event CPU budget so the cron chain (12+ tasks) finishes
-  // within budget after Phase 1 SQL + platform stats + queue stats. Default
-  // (30s scheduled) was too tight when both ctx.waitUntil blocks ran in
-  // parallel. Reduce back when stats compute moves to Hetzner VMs.
-  "limits": { "cpu_ms": 60000 },
+  // 0719 closure: stats compute moved to Hetzner VM; CF cron is lean
+  // (recovery + reconcile only). Default 30s scheduled CPU budget suffices.
```

## Rationale

### Why a thin write-only CF endpoint vs direct CF KV API
CF KV's HTTP API does exist, but using it from the VM:
- Couples the VM to a separate auth model (CF API tokens with KV write scope)
- Bypasses any future shape validation we want to add
- Loses the request-context observability (log lines per write)

A small Next.js endpoint gives us auth + validation + observability + a single secret to manage.

### Why X-Internal-Key vs OAuth/JWT
The same pattern is used by 6+ existing admin endpoints. Adding a second auth scheme just for stats endpoints would be inconsistent for no benefit. The key is rotated via `wrangler secret put` like all other secrets.

### Why batched queue-list-warmup vs N endpoints
The warmup writes 5+ KV keys (one per filter category). Sending them as `[{key, value}, ...]` in one POST avoids 5 round-trips per tick.

### Why VM not new dedicated stats Worker
A separate CF Worker would also work, but:
- Doubles CF cron schedules to monitor
- Each Worker has its own deploy lifecycle
- Stats compute is the heaviest tick — VM has more CPU headroom and persistent connections

The user already operates the VMs; this is the lower-marginal-cost path.

### Why retain unit tests in CF code path
0713 landed 13 unit tests for `_refreshQueueStatsImpl` + `shouldOverwriteStats` + `FAILURE_SENTINEL`. Those validate logic that's still relevant for any future "compute on demand" use case (e.g., admin dashboard might want to force-refresh) and serve as living documentation. Don't delete.

## Files to modify

| File | Change | AC |
|------|--------|---|
| `crawl-worker/sources/stats-compute.js` (NEW) | VM module computing all 5 payloads | US-001 |
| `crawl-worker/scheduler.js` (modified) | Register stats-compute on `*/10` cadence | US-001 |
| `src/app/api/v1/internal/_shared/validators.ts` (NEW) | Shared payload validators | US-001 |
| `src/app/api/v1/internal/stats/queue/route.ts` (NEW) | Queue stats write endpoint | US-001 |
| `src/app/api/v1/internal/stats/platform/route.ts` (NEW) | Platform stats write endpoint | US-001 |
| `src/app/api/v1/internal/stats/queue-list-warmup/route.ts` (NEW) | List warmup write endpoint | US-005 |
| `src/app/api/v1/internal/cache/skills/route.ts` (NEW) | Skills cache write endpoint | US-004 |
| `src/app/api/v1/internal/cache/publishers/route.ts` (NEW) | Publishers cache write endpoint | US-004 |
| `scripts/build-worker-entry.ts` | Remove block-1 stats chain | US-002 |
| `wrangler.jsonc` (later) | Remove `limits.cpu_ms: 60000` band-aid | US-003 |

## Sequencing

**Phase 1 — Endpoints first (no traffic yet)**:
1. T-001..T-008: Write the 5 internal CF endpoints + shared validators (RED tests, GREEN impl).
2. T-009: Deploy CF (endpoints exist but receive zero traffic until VM cron is enabled).

**Phase 2 — VM-side compute and connect**:
3. T-010..T-014: Write `crawl-worker/sources/stats-compute.js` + tests.
4. T-015: Register in `crawl-worker/scheduler.js`.
5. T-016: Enable systemd timer on ONE Hetzner VM (canary).

**Phase 3 — Verify and cut over**:
6. T-017: Watch one full hour of VM cron ticks; confirm KV keys updated; confirm CF cron still runs the OLD stats chain in parallel (no harm — last-write-wins).
7. T-018: Modify `build-worker-entry.ts` to remove the CF stats chain. Deploy.
8. T-019: Watch 24 hours. Zero `Exceeded CPU Limit`. Stats freshness < 11 min consistently.

**Phase 4 — Restore default CPU budget (optional clean-up)**:
9. T-020: Remove `limits.cpu_ms: 60000`. Deploy. Verify steady state for another 24 h.
10. T-021: Close increment.

## Verification

```bash
# Phase 1 — endpoint smoke
curl -X POST https://verified-skill.com/api/v1/internal/stats/queue \
  -H "X-Internal-Key: $INTERNAL_BROADCAST_KEY" \
  -H "Content-Type: application/json" \
  -d '{"total":107761,"active":0,"published":102727,"rejected":5028,"blocked":6,"onHold":0,"avgScore":98,"avgProcessingTimeMs":0,"generatedAt":"...","degraded":false}'
# Expect: 200, {ok:true, generatedAt:...}

curl -X POST https://verified-skill.com/api/v1/internal/stats/queue \
  -H "X-Internal-Key: WRONG"
# Expect: 401

# Phase 2 — VM compute smoke
ssh hetzner-vm-1 'cd ~/crawl-worker && node sources/stats-compute.js --once'
# Expect: console output of 5 computed payloads + 5 successful POSTs

# Phase 3 — cutover validation
wrangler tail verified-skill-com --search 'queue stats refresh' --format pretty
# (over 30 min after the cutover deploy: ZERO matching log lines)

curl -s https://verified-skill.com/api/v1/submissions/stats | jq '.generatedAt'
# Expect: timestamp < 11 min old, repeated every 5 min for 24 h
```

## ADR references

- 0708 introduced the `*/10` cron cadence and the new bindings (UpdateHub, scan queues) that were eating CF cron CPU.
- 0713 hotfix landed the disable + CPU bump + sentinel/guard.
- 0719 lifts the load architecturally — first instance of a VM↔CF write-only-endpoint pattern. Worth an ADR after closure if the pattern proves out.
