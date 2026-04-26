# 0762 — Plan

## Files modified

| Path (under `repositories/anton-abyzov/vskill-platform/`) | Change |
|---|---|
| `crawl-worker/scheduler.js` | Add `stats-compute` to `SOURCE_TIMEOUTS` (5 min) and `SOURCE_COOLDOWNS` (10 min). |
| `src/lib/cron/queue-stats-refresh.ts` | New `ensureFreshStats(env)` exported helper: if KV `submissions:stats-cache` `generatedAt` > 15 min, run minimal `SELECT COUNT(*) FILTER ...` (6s budget) and write degraded snapshot with fresh `generatedAt`. No-op when KV is fresh. |
| `.open-next/worker-with-queues.js` | Wire `ensureFreshStats` as the first task in the scheduled handler (before the heavy refreshes), and call new `releaseStuckScanning` alongside `recoverStuckSubmissions`. |
| `src/lib/queue/recovery.ts` | New `releaseStuckScanning(env)`: Prisma `updateMany` where `state='TIER1_SCANNING' AND updatedAt < now-30min`, increment retry KV, write stateEvent and `sub:<id>` KV; reject after 3 releases. Cap 100 items per call. |
| `src/app/api/v1/submissions/[id]/route.ts` | Derive `stageTimings` from `stateHistory` and include in response. |
| `src/app/api/v1/queue/health/route.ts` | New file. `GET` returns stats freshness, oldest-active age, drain rate from KV metrics. 30 s KV cache (`queue-health:cache`). |
| `src/app/api/v1/submissions/route.ts:475` | Predicate change: cache only when `submissions.length > 0`. |
| `src/app/api/v1/submissions/route.ts:442` | Wrap `flushDbUpdates` to log per-rejection results. |
| `scripts/drain-verify.mjs` | New verification script: submits N items, polls active every 30 s, writes per-id timing matrix. |

## Reused helpers

- `withTimeout` from `src/lib/queue/queue-stats-cache.ts:67` — bound the new ensureFreshStats SQL.
- `dbCircuitAllows`, `getDb`, `withDbTimeout` from `src/lib/db.ts`.
- `updateState`, `getKV`, `ensureKVEntry` from `src/lib/submission-store.ts` — used by `releaseStuckScanning` to keep KV consistent.
- `parseUsableListCache` from `src/app/api/v1/submissions/route.ts` — used by `/api/v1/queue/health` to read cached list metadata.
- `getHourKey` from `src/lib/queue/metrics-store.ts` — used to compute drain rate from existing hourly buckets.

## TDD order

For each touched file, write the failing test first, then implement.

1. `crawl-worker/__tests__/scheduler.stats-compute.test.js` → register entries.
2. `src/lib/cron/__tests__/queue-stats-refresh.ensure-fresh.test.ts` → ensureFreshStats no-op when fresh, writes when stale.
3. `src/lib/queue/__tests__/recovery.scanning.test.ts` → CAS reset + retry cap + reject after 3 cycles.
4. `src/app/api/v1/submissions/[id]/__tests__/stage-timings.test.ts` → derivation + clamp negatives.
5. `src/app/api/v1/queue/health/__tests__/route.test.ts` → response shape + 30 s cache.
6. `src/app/api/v1/submissions/__tests__/route.cache-poison.test.ts` → empty submissions never cached.
7. `src/app/api/v1/submissions/__tests__/route.flush-logging.test.ts` → console.error on rejected updateMany.

## Deploy / verification

After tests pass:

```
cd repositories/anton-abyzov/vskill-platform
npx vitest run --reporter=basic
npm run build  # opennextjs-cloudflare build
git push       # CF Pages auto-deploys; the same push deploys the crawl-worker image, picked up by the watchdog.
```

Then run `scripts/drain-verify.mjs` and save the report under `.specweave/increments/0762-.../reports/`.

## Risks

- `ensureFreshStats` adds a small DB load every 10 min — bounded to one COUNT query so insignificant.
- If the Cloudflare Pages deploy doesn't redeploy the Hetzner image, the scheduler.js fix only lands when the VM container is next pulled. CF cron fallback alone restores stats freshness, so user impact is unblocked even if VMs stay broken.
- The `releaseStuckScanning` cap of 100 items/tick means the 153 stuck items take ~2 cron cycles to drain — acceptable, not a hot-loop risk.
