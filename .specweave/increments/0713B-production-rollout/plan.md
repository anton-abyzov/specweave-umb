---
increment: 0713B-production-rollout
title: "Queue Pipeline Restoration (P0) — Production Rollout Plan"
parent: 0713-queue-pipeline-restoration
---

# Plan

## Why this is a separate increment

0713 was scoped as "fix the bugs + ship to prod + verify." During implementation it became clear that:

1. The implementation work (US-001 through US-005) was bounded, parallelizable across agents, and fully tested locally.
2. The production execution work (deploy, drain, backfill, smoke verify) is operator-only — agents lack credentials and the team prompt explicitly forbade auto-execution.

Splitting these into 0713 (code) and 0713B (rollout) lets 0713 close cleanly at "implementation complete" without blocking on Anton's production calendar, while keeping the rollout work tracked and discoverable.

## What lands here vs in 0713

| Work | Increment |
|------|-----------|
| Code, unit/integration/e2e tests, types, scripts | **0713** (closed) |
| `wrangler deploy` Phase 1 | **0713B** (T-101) |
| Stats cron live verification | **0713B** (T-102) |
| List endpoint live smoke | **0713B** (T-103) |
| Drain stuck hyperframes RECEIVED rows in prod DB | **0713B** (T-104) |
| Backfill state-history against prod DB | **0713B** (T-105) |
| `wrangler deploy` Phase 2 | **0713B** (T-106) |
| Queue page UX live verification | **0713B** (T-107) |

## Risk

- The shipped code is gated behind `npm run build` + Cloudflare Workers deploy. If the build breaks against the production environment (env vars, bindings), the deploy itself will surface the issue.
- The drain script and backfill script have local unit tests but have not run against production data. Both are guarded with `--dry-run` to mitigate.
- If Phase 1 deploy succeeds but stats stay frozen for > 11 min, the rollback path is `wrangler rollback` to the previous worker version. The bug is recoverable — the cron will retry.

## Closure criteria

This increment closes when all 7 tasks (T-101..T-107) are checked off AND the 24h post-deploy operational monitor (per 0713 rubric) reports green.
