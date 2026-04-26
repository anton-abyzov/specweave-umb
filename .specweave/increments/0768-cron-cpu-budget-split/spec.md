---
status: completed
---
# 0768 — Cron CPU budget split: light + heavy cohorts

## Problem

The single `*/10 * * * *` cron registered in `wrangler.jsonc` runs ALL stats refreshes serially in two `ctx.waitUntil(...)` blocks. Live `wrangler tail` output during 0763 verification confirmed:

- `[cron] reconciler ensure status=200 in 126ms`
- `[cron] vm-healthcheck status=200 in 1171ms`
- `[cron] queue-health-check status=200 in 1744ms`
- `[cron] ensureFreshStats completed in 5832ms`
- `"*/10 * * * *" @ 4/26/2026, 11:50:27 AM - Exceeded CPU Limit`

`refreshPlatformStats`, `refreshQueueStats` (full Phase 1+1b+2+3), `warmQueueListCache`, `refreshSkillsCache`, `refreshPublishersCache`, plus the second `waitUntil` (enrichment, reconciliation, discovery, search index) **never run**. Symptoms:
- `rejectionBreakdown` is missing from `/api/v1/submissions/stats` ⇒ queue page rejection sub-pills never render.
- `avgProcessingTimeMs` stays at `0` indefinitely.
- AVG SCORE was also stuck at 0 — fixed in 0763 by moving its compute into the watchdog (`ensureFreshStats`).

## Root cause

A single Cloudflare scheduled invocation has a CPU budget (~30s on the paid plan). The current handler queues ~9s of synchronous work plus several heavy parallel tasks via `waitUntil` — the handler exits within budget but the waitUntil tasks then exhaust the worker's remaining CPU before they all complete.

## User stories

### US-001: Heavy refresh cohort runs to completion every 10 minutes

**As a** queue dashboard viewer
**I want** rejection breakdown pills, avg processing time, and full platform stats to refresh on a regular cadence
**So that** I see live data, not values frozen at deploy time.

**Acceptance criteria**:
- [x] AC-US1-01: `wrangler.jsonc` registers two cron triggers: `*/10 * * * *` and `5,15,25,35,45,55 * * * *`.
- [x] AC-US1-02: `scheduled(controller, env, ctx)` branches on `controller.cron` to dispatch the light vs heavy cohort.
- [x] AC-US1-03: Light cohort (`*/10`) runs `ensureFreshStats`, vm-healthcheck, queue-health-check, recovery jobs, DB prewarm.
- [x] AC-US1-04: Heavy cohort (`5,15,...,55`) dispatches the full refresh chain via a `selfRef.fetch()` sub-request to `/api/v1/internal/cache-warm?async=1` — that endpoint returns 202 immediately and runs `refreshPlatformStats`, full `refreshQueueStats`, `warmQueueListCache`, `refreshSkillsCache`, `refreshPublishersCache` in its own ctx.waitUntil with its own CPU budget. Enrichment, reconciliation, discovery, and search-index rebuild stay inline in the heavy cohort with their existing minute/hour gates.
- [x] AC-US1-05: After deploy, `wrangler tail` shows both cohorts firing — `[cron] tick cron="*/10 * * * *" cohort=light` and `[cron] tick cron="5,15,25,35,45,55 * * * *" cohort=heavy` — and the heavy cohort's `[cron] heavy cache-warm dispatched status=202` log line confirms the offload path.
- [x] AC-US1-06: `/api/v1/submissions/stats` includes `rejectionBreakdown` within 15 min of deploy. Confirmed live on prod 2026-04-26 at 18:15 UTC: `{"rejectionBreakdown":{"admin":0,"other":4934,"security":0,"no_skillmd":0},"avgProcessingTimeMs":12780,"avgScore":97,...}`.

## Out of scope

- Moving cron work to a separate Worker / Durable Object. Two schedules on the same Worker is sufficient for the observed workload.
- Adjusting the schedule cadence (still 10 min total). If load grows further, the next step is a third cron or per-task isolation.
