# Implementation Plan: Queue Observability Alerts

## Architecture

```
                         ┌──────────────────────────┐
   light cohort cron     │  /api/v1/internal/       │
   ─*/10 * * * *────────▶│  alerts-evaluator        │
                         │                          │
                         │  for each detector:      │
                         │    detect()  → Alert[]   │
                         │    dedup.shouldFire()    │
                         │    sendQueueHealthAlert()│
                         │    dedup.recordFired()   │
                         │    storeRecent()         │
                         └────────┬─────────────────┘
                                  │
                       ┌──────────┴──────────┐
                       ▼                     ▼
             ┌─────────────────┐    ┌─────────────────┐
             │ ALERTS_KV       │    │ SendGrid        │
             │  alerts:dedup:* │    │  → ALERT_       │
             │  alerts:recent  │    │    RECIPIENTS   │
             │  alerts:last-*  │    └─────────────────┘
             └─────────────────┘             ▲
                                             │
   heavy cohort cron     ┌──────────────────────────┐
   ─5,15,...─*─*─────────▶│  /api/v1/internal/       │
                         │  alerts-digest           │
                         │  (4× daily windows)      │
                         └──────────────────────────┘

   admin UI              ┌──────────────────────────┐
   /admin/queue          │  RecentAlertsPanel       │
                         │  GET /admin/alerts/recent│
                         │  POST /alerts/{id}/ack   │
                         └──────────────────────────┘
```

## Modules

### `src/lib/alerts/types.ts`
Shared types — `AlertKind`, `Severity`, `Alert`, `AlertEnv`. Pure types only.

### `src/lib/alerts/dedup.ts`
- `shouldFire(env, kind, key)` → boolean (returns false if dedup KV key exists).
- `recordFired(env, kind, key, alert)` → write dedup key with TTL based on severity, append to `alerts:recent` ring buffer (cap 100), and increment `alerts:digest:<kind>` counter for digest pass.
- `clearDedup(env, kind, key)` → delete the dedup key (used by ack).
- `dedupKey(kind, key)` → `alerts:dedup:{kind}:{key}` string.

Severity → TTL:
- `critical` → 3600 (1h)
- `warning` → 21600 (6h)
- `info` → no email; only digest counter

### `src/lib/alerts/detectors.ts`
Pure functions, each takes a snapshot input + env and returns `Alert[]`. Detector functions:
- `detectDrainStalled({ drainRate, oldestActive })`
- `detectHeartbeatStale({ vmHeartbeat, thresholdMs })`
- `detectOrphanGrowing({ orphanedActiveCount, lastBaselineCount, growthThreshold })`
- `detectLlmFallbackSpike({ fallbackCounts, threshold })`
- `detectSubmissionMaxRetries({ submissions })` — input: array of `{id, processingAttempts, state}`; emits one Alert per offender.

A top-level `runAllDetectors(env)` orchestrator fetches the inputs (queue-health snapshot, KV reads, DB query for retries) using `Promise.allSettled`, calls each pure detector, and returns the merged list.

### `src/lib/alerts/digest.ts`
- `buildDigest(env, since)` — reads `alerts:digest:*` counters + last-5 samples per kind from `alerts:recent`. Returns `{ counts: {kind: n}, samples: {kind: Alert[]} }`.
- `sendDigestIfNonEmpty(env, since)` — wraps email send; suppresses on empty.

### `src/lib/email.ts` extensions
- Replace `OPS_ALERT_TO` constant with `getAlertRecipients()` that reads `ALERT_RECIPIENTS` env, splits CSV, trims, dedups; default `['admin@easychamp.com']`.
- Extend `QueueHealthAlertParams` discriminated union with the new kinds.
- Add HTML branches inside `sendQueueHealthAlert()` (one per kind).
- Add `sendAlertDigest(digest)` function.

## Data flow per alert kind

| Kind | Severity | Source | Dedup key | Rationale |
|------|----------|--------|-----------|-----------|
| `vm-down` | critical | (existing) — vm-healthcheck | `vm-down:<ip>` | Already wired |
| `drain-stalled` | critical | drainRate.last1h + oldestActive | `drain-stalled:global` | One signal per cluster |
| `queue-stuck` | warning | (existing) | `queue-stuck:global` | Reused |
| `heartbeat-stale` | warning | vmHeartbeat.ageMs | `heartbeat-stale:global` | One signal |
| `orphan-growing` | warning | orphanedActive.count delta | `orphan-growing:global` | One signal |
| `submission-max-retries` | warning | DB Submission.processingAttempts | `submission-max-retries:<submissionId>` | Per offender |
| `llm-fallback-spike` | info | KV ai:fallback:*:<today> | `llm-fallback-spike:<YYYY-MM-DD>` | Daily, digest only |

## API routes

### `POST /api/v1/internal/alerts-evaluator`
- Auth: `x-cron-auth` header matches `CRON_AUTH` (existing pattern).
- Calls `runAllDetectors(env)`, then for each alert: `shouldFire` → `sendQueueHealthAlert` (skipping `info`) → `recordFired`.
- Special debug: if `alerts:debug:fire-once` KV key exists, fires a synthetic `heartbeat-stale` alert and deletes the key. Used for production smoke verification.
- Returns `{ checked: N, fired: M, suppressed: K }`.

### `POST /api/v1/internal/alerts-digest`
- Auth: cron-auth.
- Computes the current 6h window (00–06, 06–12, 12–18, 18–24 UTC) and only fires once per window (dedup key `digest:fired:<window-start>`).
- Calls `sendDigestIfNonEmpty`.

### `GET /api/v1/admin/alerts/recent`
- Auth: REVIEWER+ via `requireAdmin()`.
- Reads `alerts:recent` ring buffer, returns `{ alerts: [...], total }`.

### `POST /api/v1/admin/alerts/[id]/ack`
- Auth: REVIEWER+.
- Marks alert acknowledged in the ring buffer, clears the dedup KV key.
- Returns `{ acknowledged: true }`.

## Cron wiring

`src/lib/cron/cohort-dispatch.ts` already maps cron strings to handlers. Add:
- `*/10 * * * *` (light) → also call `alerts-evaluator`.
- `5,15,25,35,45,55 * * * *` (heavy) → also call `alerts-digest`.

## KV namespace

New `ALERTS_KV` namespace registered in `wrangler.jsonc`. Keys used:
- `alerts:dedup:{kind}:{key}` — TTL set per severity.
- `alerts:recent` — JSON-serialized ring buffer (last 100).
- `alerts:last-orphan-count` — number for delta detection.
- `alerts:digest:{kind}` — counter, daily TTL.
- `alerts:digest:samples:{kind}` — last 5 sample alerts, JSON array.
- `alerts:digest:fired:{window-start}` — dedup key for digest.
- `alerts:debug:fire-once` — one-shot escape hatch (manually written for prod smoke).

## ADR (inline)

**Decision**: New KV namespace `ALERTS_KV` instead of reusing existing buckets.
**Rationale**: separation of concerns — alert state has different TTLs and access patterns from queue stats. A clean namespace makes future migration to a DB table easier.
**Alternatives considered**: (1) Single `vskill:alerts:*` prefix in `SUBMISSIONS_KV` (rejected — pollutes hot KV). (2) DB table `Alert` (rejected for now — needs schema migration; KV is sufficient).

## Test strategy

| File | Type | Coverage |
|------|------|----------|
| `src/lib/alerts/__tests__/dedup.test.ts` | vitest unit | TTL math, severity routing, recent ring-buffer cap |
| `src/lib/alerts/__tests__/detectors.test.ts` | vitest unit | each detector — fires, doesn't fire, edge cases |
| `src/lib/alerts/__tests__/digest.test.ts` | vitest unit | empty digest skipped, populated digest formatted |
| `src/lib/email.ts` (existing test file extended) | vitest unit | recipient resolution + new kind HTML present |
| `src/app/api/v1/internal/alerts-evaluator/__tests__/route.test.ts` | vitest integration | auth, detector invocation, dedup honored, debug fire-once |
| `tests/e2e/admin-alerts.spec.ts` | Playwright | full UI flow: panel renders → ack → state flip |

TDD discipline: every detector has its test first (RED), implementation second (GREEN), then refactor.

## Deploy

1. `wrangler kv:namespace create ALERTS_KV` — record id, bind in wrangler.jsonc.
2. `wrangler secret put ALERT_RECIPIENTS` (optional — default kicks in if unset).
3. `npm run build && npm run build:worker && npm run deploy`.

## Risks & mitigations

| Risk | Mitigation |
|------|-----------|
| KV unavailable → dedup falls open | Email path wrapped in try/catch; dedup record only after successful send |
| First cron tick fires baseline alert with no data | Cold-start guard in `detectOrphanGrowing` (records baseline, no fire on first run) |
| Recipient list empty after misconfig | Default to `['admin@easychamp.com']` if `ALERT_RECIPIENTS` is empty/whitespace |
| Debug fire-once accidentally left enabled | Always delete the KV key at start of evaluator handler — auto-cleanup |
| Detector throws | `Promise.allSettled` ensures other detectors continue; failures logged |
