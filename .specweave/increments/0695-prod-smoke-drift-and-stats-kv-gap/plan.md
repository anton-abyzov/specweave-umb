---
increment: 0695-prod-smoke-drift-and-stats-kv-gap
title: "Fix prod smoke drift and stats KV write gap"
---

# Plan — prod-smoke-drift-and-stats-kv-gap

## Scope

Two parallel threads:

1. **Test maintenance** — update four smoke assertions in `tests/e2e/smoke.spec.ts` to target the current UI/API surface. Pure test-only changes for F1, F4, and (likely) F2.
2. **Source fix** — gate the stats-refresh watermark write on `kvWriteOk` in `src/lib/cron/stats-refresh.ts` so a single KV put failure cannot wedge the cron into a 6-hour short-circuit.

No broader refactor; no feature branch; main-only per user preference.

## Architecture touch points

### Stats refresh pipeline (US-002)

Current flow at [stats-refresh.ts:105](repositories/anton-abyzov/vskill-platform/src/lib/cron/stats-refresh.ts):

```
refreshPlatformStats(kv)
  1. Read watermark; if age < 6h AND modifiedCount == 0 AND _memStats → early return  [L110-126]
  2. Compute stats                                                                     [L135]
  3. statsAreConsistent(stats)? NO → early return (no writes)                          [L137-142]
  4. _memStats = stats; _cachedKV = kv                                                 [L144-145]
  5. try kv.put("platform:stats", …) → kvWriteOk = true/false; log on fail             [L149-155]
  6. try kv.put("platform:blocklist", …) (non-fatal)                                   [L158-168]
  7. try db.cachedStats.upsert(...)    (non-fatal)                                     [L171-181]
  8. try kv.put(STATS_WATERMARK_KEY, now)  ← BUG: runs even when kvWriteOk === false  [L183-188]
  9. Log completion                                                                    [L190-193]
```

**Fix (1 line + comment)**: wrap step 8 in `if (kvWriteOk)`. When the stats write failed, skip the watermark write and log the skip for observability. No other behavior changes. DB fallback upsert stays unconditional — it is the read-path safety net for `/api/v1/stats`.

**Rejected alternatives**:
- Bubble the KV-put error: would fail the whole cron tick including unrelated downstream tasks (queue warmup, enrichment) that share the same `scheduled` handler. Too blast-radius-heavy.
- Write a separate watermark key into its own try/catch and serialize: adds state without clarifying semantics.
- Retry `kv.put` N times in-loop: CF KV write failures are rare but can persist across minutes; retries inside a 30s cron invocation don't help and consume CPU budget.

### Smoke tests (US-001)

All four failing tests live in `tests/e2e/smoke.spec.ts` (single file, no shared test-util state). Fixes are localised:

- **F1 (hero count)**: keep `.hero-h1` visible check; add separate `getByText(/\d[\d,]*\s+verified/).first()` assertion on the count span.
- **F2 (skills rows)**: verify live first (headed Playwright + browser console). If page truly renders zero rows, fix the server-side root cause in `src/lib/skills-query.ts` (or `getSkills`). If rows render but test times out, extend wait + `waitForLoadState("networkidle")`.
- **F4 (metric cards)**: retarget to `/insights` page. Verify structure first. Fallback: API-level non-zero assertion on `/api/v1/stats`.

### ADR

No new ADR required — this is a hotfix within established patterns (existing cron handler, existing KV gate pattern).

## Files changed

| File | Kind | Reason |
|---|---|---|
| `src/lib/cron/stats-refresh.ts` | edit | Gate watermark put on `kvWriteOk` (US-002) |
| `src/lib/cron/__tests__/stats-refresh.watermark.test.ts` | new | RED test guarding US-002 invariant |
| `tests/e2e/smoke.spec.ts` | edit | Retarget F1, F2 (if test-side fix), F4 |
| `src/lib/skills-query.ts` (or equivalent) | conditional edit | Only if F2 live verification reveals a real bug |
| `.specweave/increments/0695-*/` | new | Spec, plan, tasks, metadata |

## Testing

- Unit: new `stats-refresh.watermark.test.ts` — asserts watermark is NOT written when `kv.put("platform:stats", …)` throws; asserts it IS written when the put succeeds.
- E2E: full smoke run against prod: `E2E_BASE_URL=https://verified-skill.com npx playwright test tests/e2e/smoke.spec.ts --project=chromium --reporter=list` → 11/11 pass.
- Live ops verification: after deploy, wait for the next `0 * * * *` UTC tick, then curl `/api/v1/stats/health` and confirm `status: "OK"`. Monitor 2-3 ticks.

## Rollout

- Main-only (no branch). Per-task commit.
- Build + deploy after the source fix lands: `npm run build:worker && npm run deploy` inside `repositories/anton-abyzov/vskill-platform`.
- Close via `/sw:done` → runs code-review + simplify + grill + judge-llm + PM validation; syncs to external tools.
