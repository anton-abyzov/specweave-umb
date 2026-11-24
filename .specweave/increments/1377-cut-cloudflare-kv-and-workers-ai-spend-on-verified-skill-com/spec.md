# 1377 Cut Cloudflare KV and Workers AI spend on verified-skill-com

## Problem

The `verified-skill-com` Worker (`repositories/anton-abyzov/vskill-platform`) billed $305.23 from October 24 to November 17, 2026. KV writes were $170 of it (34.89M writes); in June to September they were $10 to $20 a month. Workers AI adds $27 to $65 a month, and October's scanning job billed $3,145.67 with no AI Gateway spend limit.

Evidence (Cloudflare GraphQL, November 16, 2026, one day; raw files in `~/.specwithcode/m4/scratch/2026-11-17-vskill-kv-cost/`):

| Namespace | Writes attempted | Of which 429 | Main writer |
|---|---|---|---|
| SUBMISSIONS_KV `d21d89b0` (+ ALERTS_KV, FALLBACK_LOG_KV) | 911k | 27 | `sub:`/`hist:` state copy, caches, recovery |
| QUEUE_METRICS_KV `65c54f6d` | 800k | 153k | per-message metrics, scan log, inflight, DLQ index |
| RATE_LIMIT_KV `de6c0b7a` | 345k | 182k | fixed-window counters (`rl:bulk-submit:*`) |
| SEARCH_CACHE_KV `4570fe03` | 128k | 33 | `scanner-etag:*`, search index rebuild |

Root causes found:

1. **Hot-key read-modify-write counters.** Every queue message does about 6 QUEUE_METRICS_KV writes (`src/lib/queue/metrics-store.ts`, `scan-log-store.ts`, inflight put/delete in `consumer.ts:521`). `qm:totals`, the hourly bucket and `scanlog:index` are single keys shared by every consumer, so KV answers 429 above one write per second per key.
2. **DLQ consumer error loop.** `submission-dlq` took 125k messages in 2 days (62k a day). `handleDLQ` (`src/lib/queue/dlq-consumer.ts`) writes a DLQ entry with no TTL, then the shared `dlq:index` and `qm:totals`; the 429 on those keys throws, the DLQ message is retried, and each retry writes another entry. A 75-second `wrangler tail --status error` sample showed 32 of 37 Worker errors were `KV PUT failed: 429 Too Many Requests` from `queue:submission-dlq`; the other 5 were `exceededMemory` on `submission-processing`.
3. **Intake retry self-loop.** `bulk_intake_retry` messages (added September 28, 2026, `e9f05437`; parallelised October 3 and 20) re-POST `/api/v1/submissions/bulk` through `WORKER_SELF_REFERENCE` every 60 s on any non-accepted result (`src/lib/queue/bulk-intake-retry.ts`). These calls arrive as IP `::1` and were 70% of bulk-submit rate-limit hits (2,311 of 3,282 in the 13:00 UTC hour on November 17). After 3 retries they reach the DLQ with no `submissionId`, where `settle` calls `updateState(undefined, "REJECTED")` (58 log lines a minute in a 60-second tail).
4. **Workers AI without a gateway.** The VM scanner (`crawl-worker/lib/tier2-scan.js:100`) calls Workers AI over REST first for every tier-2 scan, then a second model on failure. The Worker calls it from `src/lib/ai/ai-router.ts:110` for private and person-lane scans. Neither goes through AI Gateway.

## Scope

In: rate-limit counters and queue telemetry moved off KV to SQLite Durable Objects behind flags; DLQ consumer and intake retry loop fixes; no-op state rewrites skipped; unchanged ETag rewrites skipped; Workers AI routed through AI Gateway when a gateway id is configured; a report with before numbers, expected reductions and the deploy plan.

Out: deploying, creating the AI Gateway or its spend limit, changing Cloudflare account settings, the VM deploy of `crawl-worker`, the search index rebuild design, the `exceededMemory` batches on `submission-processing` (reported as follow-up), rotating the token in `crawl-worker/.env` (reported).

## Acceptance Criteria

- [ ] AC-01: With `RATE_LIMIT_STORE=do`, `checkRateLimit`/`applyRateLimit` keep their limits and fixed windows but write nothing to RATE_LIMIT_KV; counters live in a SQLite Durable Object, survive isolate eviction, and the limiter fails open when the object is unreachable. Worker-originated intake retries (`X-Bulk-Intake-Retry` with a valid internal key) skip the bulk-submit limiter.
- [ ] AC-02: With `QUEUE_METRICS_STORE=do`, per-message metrics, scan log, inflight markers and DLQ entries write nothing to QUEUE_METRICS_KV; all readers (admin queue metrics/status/logs/dlq, queue health, alerts evaluator, queue-stats refresh, recovery) return the same shapes from the Durable Object; for 25 hours after cutover a missing key is read through from KV. One message costs at most 2 Durable Object requests for telemetry.
- [ ] AC-03: The DLQ consumer never throws because a telemetry write failed, acks every message once, and does not call `updateState` for a message without a `submissionId`.
- [ ] AC-04: A deferred `bulk_intake_retry` backs off (300 s, then 1,200 s, then 3,600 s) instead of retrying every 60 s.
- [ ] AC-05: `updateState` skips both KV puts when the stored state is the same terminal state with the same message and the call is not forced; scanning states, `RECEIVED` and forced calls still write; the DB write always runs.
- [ ] AC-06: The skill-update scanner skips the `scanner-etag` put when the ETag equals the cached one.
- [ ] AC-07: With `AI_GATEWAY_ID` set, the Worker's Workers AI calls pass `{ gateway: { id } }`, and with `CF_AI_GATEWAY_ID` set the VM scanner sends `cf-aig-gateway-id: <id>` on its Workers AI REST calls; with neither set, behaviour is unchanged.
- [ ] AC-08: Both Durable Objects are bound, migrated (`v5`, SQLite) and exported, and both flags are declared; release 1 ships them with the flags at `kv`; the targeted tests pass and the platform typecheck adds no errors over `main` (`e0e6a72c`, 339 pre-existing errors). Changed November 17, 2026 from "the typecheck passes", which `main` itself fails.

## Approach

**Why Durable Objects, not Analytics Engine or the Rate Limiting binding.** Five in-Worker readers (alerts evaluator, queue health, queue-stats refresh, admin status, recovery) read the hourly buckets and inflight markers; Analytics Engine has no in-Worker reader and would need an API-token secret and SQL API calls. The Rate Limiting binding only supports 10 s or 60 s periods with one limit per binding, while the app has about 20 limits with 60 s to 3,600 s windows (login is 5 per 900 s). A SQLite Durable Object keeps exact semantics, serialises the read-modify-write (removing the 429s), and its rows written are included up to 50M a month; requests cost $0.15 per million after 1M (Cloudflare pricing page, November 13, 2026).

**Rollout.** Cloudflare blocks a rollback across a Durable Object class change ("A Durable Object class lifecycle change ... has occurred between the version in the active deployment and the version selected to roll back to", Rollbacks page). The work is three stacked branches, one release each:

1. `fix/1377-1-durable-objects`: the classes, migration `v5`, the store code, flags at `kv`. Near-inert (the only behaviour change is the bulk-submit limiter skipping intake retries). It cannot be rolled back past, so it carries nothing else.
2. `fix/1377-2-loop-fixes`: DLQ fix, intake backoff, no-op skips, AI Gateway routing. Rollback lands on release 1.
3. `fix/1377-3-flip-to-durable-objects`: both flags to `do`. Rollback lands on release 2, which works on KV.

Files, in order:

1. `src/lib/rate-limit-do.ts` (new `RateLimiterDO`, one object per limit key, fixed window stored as one row, alarm deletes it after the window) and `src/lib/rate-limit.ts` (`checkRateLimit` takes a KV or a DO store; `rateLimitStore(env)` picks by flag). Callers that pass `env.RATE_LIMIT_KV` switch to `rateLimitStore(env)`. `src/app/api/v1/submissions/bulk/route.ts` skips the limiter for authenticated intake retries.
2. `src/lib/queue/queue-metrics-do.ts` (new `QueueMetricsDO`, a single object; storage adapter with TTL and hourly GC alarm; runs the existing `metrics-store`, `scan-log-store` and `dlq-store` functions against its own storage) and `src/lib/queue/queue-metrics-client.ts` (`queueMetricsStore(env)`: `get`, `recordOutcome`, `startInflight`, `deadLetter`, `dlqIndex`/`dlqEntry`/`markReplayed`, `scanLogs`, `metricsWindow`; KV implementation for the flag `kv`). Consumer, DLQ consumer and readers switch to it. `queue:paused` stays in KV (written only by an admin).
3. `src/lib/queue/dlq-consumer.ts`, `src/lib/queue/bulk-intake-retry.ts`.
4. `src/lib/submission/kv-store.ts`, `src/lib/skill-update/scanner.ts`.
5. `src/lib/ai/ai-router.ts`, `crawl-worker/lib/tier2-scan.js`.
6. `wrangler.jsonc`, `scripts/build-worker-entry.ts`, `src/lib/env.d.ts`.

Risks: the queue telemetry object is a single instance (about 3 to 10 requests a second at current volume, well under one object's throughput); counters reset at cutover except what the 25-hour read-through restores; the alerts evaluator's scan-success-rate detector may see fewer samples for the first hour.

Expected billed writes per 30 days after release 3. "Now" is the October 24 to November 17 total of successful writes scaled to 30 days (34.18M successful writes in that window against 34.89M billed and 2.15M refused with 429, which suggests refused writes are not billed; not confirmed). Estimates:

| Namespace | Now | After | Basis |
|---|---|---|---|
| RATE_LIMIT_KV | ~8.5M | <0.05M | `checkRateLimit` counters move; `scan-lock:`, the rescan route's own limiter and `install:unmatched` stay on KV (small) |
| QUEUE_METRICS_KV | ~11.4M | <0.01M | only `queue:paused` stays |
| SUBMISSIONS_KV | ~17.7M | ~16M to 17M (guess) | terminal-state no-op skips only; not measured per prefix |
| SEARCH_CACHE_KV | ~3.3M | ~3M (guess) | ETag skip; search index rebuild untouched |

The 3M a month target is not met by this increment alone: SUBMISSIONS_KV stays the largest writer. Next step after release 3 is a per-prefix measurement of SUBMISSIONS_KV writes.

## Decisions

### Asked
- none (the task brief settled direction; deviations are recorded below)

### Defaulted (change any before sw-do)
- D-01 Queue metrics go to a Durable Object, not Analytics Engine → in-Worker readers need the same buckets; AE needs a token and SQL API (reversible).
- D-02 Rate limits go to a Durable Object, not the Rate Limiting binding → exact windows and limits kept (reversible).
- D-03 Three stacked releases with `RATE_LIMIT_STORE`/`QUEUE_METRICS_STORE` vars → rollbacks across DO migrations are blocked by Cloudflare, so the migration ships alone.
- D-06 No-op skip limited to terminal states → scanning-state rewrites refresh `updatedAt`, which stale-scan recovery reads.
- D-04 Workers AI binding kept; gateway routing inert until `AI_GATEWAY_ID`/`CF_AI_GATEWAY_ID` is set → private and person-lane scans still use it.
- D-05 Provider order in the VM scanner unchanged → the VM `.env` shows no Gemini key, so moving Gemini first would drop tier-2 scans.

### Open
- Creating the AI Gateway, its spend limit, and the two releases need Anton's yes.

## Tasks

### T-01 Rate limit counters in a Durable Object
- AC: AC-01 | Files: repositories/anton-abyzov/vskill-platform/src/lib/rate-limit-do.ts, repositories/anton-abyzov/vskill-platform/src/lib/rate-limit.ts, repositories/anton-abyzov/vskill-platform/src/lib/__tests__/rate-limit-do.test.ts, repositories/anton-abyzov/vskill-platform/src/app/api/v1/submissions/bulk/route.ts, repositories/anton-abyzov/vskill-platform/src/app/api/v1/submissions/route.ts, repositories/anton-abyzov/vskill-platform/src/app/api/v1/problem-reports/route.ts, repositories/anton-abyzov/vskill-platform/src/app/api/v1/account/repos/[id]/resync/route.ts, repositories/anton-abyzov/vskill-platform/src/lib/crawl-dispatch.ts, repositories/anton-abyzov/vskill-platform/src/lib/external-scan-dispatch.ts | Test: cd repositories/anton-abyzov/vskill-platform && npx vitest run src/lib/__tests__/rate-limit-do.test.ts src/lib/__tests__/rate-limit.test.ts src/lib/__tests__/rate-limit-bypass.test.ts --maxWorkers=4

### T-02 Queue telemetry in a Durable Object
- AC: AC-02 | Files: repositories/anton-abyzov/vskill-platform/src/lib/queue/queue-metrics-do.ts, repositories/anton-abyzov/vskill-platform/src/lib/queue/queue-metrics-client.ts, repositories/anton-abyzov/vskill-platform/src/lib/queue/__tests__/queue-metrics-do.test.ts, repositories/anton-abyzov/vskill-platform/src/lib/queue/consumer.ts, repositories/anton-abyzov/vskill-platform/src/app/api/v1/admin/queue, repositories/anton-abyzov/vskill-platform/src/app/api/v1/queue, repositories/anton-abyzov/vskill-platform/src/app/api/v1/internal/alerts-evaluator/route.ts, repositories/anton-abyzov/vskill-platform/src/lib/cron/queue-stats-refresh.ts, repositories/anton-abyzov/vskill-platform/src/lib/queue/recovery.ts | Test: cd repositories/anton-abyzov/vskill-platform && npx vitest run src/lib/queue/__tests__/queue-metrics-do.test.ts src/lib/queue/__tests__/consumer.test.ts src/lib/queue/__tests__/metrics-store.test.ts --maxWorkers=4

### T-03 DLQ consumer and intake retry loop
- AC: AC-03, AC-04 | Files: repositories/anton-abyzov/vskill-platform/src/lib/queue/dlq-consumer.ts, repositories/anton-abyzov/vskill-platform/src/lib/queue/bulk-intake-retry.ts, repositories/anton-abyzov/vskill-platform/src/lib/queue/__tests__/dlq-consumer.test.ts, repositories/anton-abyzov/vskill-platform/src/lib/queue/__tests__/bulk-intake-retry.test.ts | Test: cd repositories/anton-abyzov/vskill-platform && npx vitest run src/lib/queue/__tests__/dlq-consumer.test.ts src/lib/queue/__tests__/bulk-intake-retry.test.ts --maxWorkers=4

### T-04 Skip no-op state and ETag rewrites
- AC: AC-05, AC-06 | Files: repositories/anton-abyzov/vskill-platform/src/lib/submission/kv-store.ts, repositories/anton-abyzov/vskill-platform/src/lib/skill-update/scanner.ts, repositories/anton-abyzov/vskill-platform/src/lib/submission/__tests__/kv-store-noop.test.ts | Test: cd repositories/anton-abyzov/vskill-platform && npx vitest run src/lib/submission/__tests__/kv-store-noop.test.ts src/lib/skill-update --maxWorkers=4

### T-05 Workers AI through AI Gateway when configured
- AC: AC-07 | Files: repositories/anton-abyzov/vskill-platform/src/lib/ai/ai-router.ts, repositories/anton-abyzov/vskill-platform/crawl-worker/lib/tier2-scan.js, repositories/anton-abyzov/vskill-platform/src/lib/ai/__tests__/ai-router-gateway.test.ts | Test: cd repositories/anton-abyzov/vskill-platform && npx vitest run src/lib/ai --maxWorkers=4

### T-06 Wiring, flags and the release plan
- AC: AC-08 | Files: repositories/anton-abyzov/vskill-platform/wrangler.jsonc, repositories/anton-abyzov/vskill-platform/scripts/build-worker-entry.ts, repositories/anton-abyzov/vskill-platform/src/lib/env.d.ts, repositories/anton-abyzov/vskill-platform/src/lib/__tests__/kv-spend-1377-wiring.test.ts, .specweave/increments/1377-cut-cloudflare-kv-and-workers-ai-spend-on-verified-skill-com/reports/kv-spend-report.md | Test: cd repositories/anton-abyzov/vskill-platform && npx vitest run src/lib/__tests__/kv-spend-1377-wiring.test.ts src/lib/__tests__/rate-limit-do.test.ts src/lib/queue/__tests__/queue-metrics-do.test.ts --maxWorkers=4 (typecheck compared with `main` through `specweave-studio checks run`, evidence in the report)

Verify and close 1377.
