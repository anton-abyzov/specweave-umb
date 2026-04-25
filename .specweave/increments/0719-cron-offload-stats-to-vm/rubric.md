---
increment: 0719-cron-offload-stats-to-vm
title: "Cron Offload — Stats Compute to Hetzner VM"
generated: "2026-04-25"
source: hand-authored
version: "1.0"
status: ready
---

# Quality Contract

This is a follow-up architectural fix to the 0713 hotfix. Bar: zero CF cron CPU-limit hits over 7 days, stats freshness < 11 min sustained, and clean removal of the 0713 band-aid.

## Quality Gates

| Gate | Threshold | Owner |
|------|-----------|-------|
| Type-check | `npx tsc --noEmit` exits 0 | Implementer |
| Unit tests | All new in `src/app/api/v1/internal/**/__tests__/` + `crawl-worker/__tests__/stats-compute.test.js` pass | Implementer |
| Integration smoke | Each of 5 endpoints accepts a valid payload + rejects 401/400 cases | Implementer |
| Production cron health | Zero `Exceeded CPU Limit` log for `*/10` schedule over 24h post-cutover | Implementer |
| Stats freshness | `generatedAt` < 11 min for 99% of polls over 24h | Implementer |
| Band-aid removal verification | After 24h clean cron ticks, `wrangler.jsonc` no longer contains `limits.cpu_ms` | Implementer |
| Pre-existing tests | 0713's 13 unit tests for `_refreshQueueStatsImpl` + `shouldOverwriteStats` + `FAILURE_SENTINEL` remain green | Implementer |

## Acceptance Criteria Coverage

Every AC in spec.md must trace to at least one task and one passing test (or a manual verification step).

| AC | Task(s) | Test(s) |
|----|---------|---------|
| AC-US1-01 | T-010, T-011 | T-010 |
| AC-US1-02 | T-010, T-011 | T-010 |
| AC-US1-03 | T-012 | T-010 |
| AC-US1-04 | T-001..T-004 | T-003 |
| AC-US1-05 | T-005 | T-005 |
| AC-US1-06 | T-013, T-015 | T-014 (manual) |
| AC-US1-07 | T-014, T-016, T-019 | T-019 (24h prod) |
| AC-US1-08 | All | 0713's 13 tests still green |
| AC-US2-01 | T-017 | bundle inspection |
| AC-US2-02 | T-017 | bundle inspection |
| AC-US2-03 | T-018, T-019 | tail observation |
| AC-US2-04 | T-019 | tail observation |
| AC-US2-05 | T-019 | 24h prod monitoring |
| AC-US3-01 | T-020 | manual |
| AC-US3-02 | T-020 | 24h prod monitoring |
| AC-US3-03 | T-020 | code review |
| AC-US4-01 | T-011 | T-010 |
| AC-US4-02 | T-007, T-008 | T-007, T-008 |
| AC-US4-03 | T-019 | manual smoke |
| AC-US5-01 | T-011 | T-010 |
| AC-US5-02 | T-006 | T-006 |
| AC-US5-03 | T-019 | manual TTFB measurement |

## Closure Gate Decisions

- **Block closure** if any cron `Exceeded CPU Limit` occurs in the 24h post-cutover window.
- **Block closure** if `wrangler.jsonc` still contains the 0713 band-aid (`limits.cpu_ms`) after T-020.
- **Allow closure with warning** if Phase 4 (band-aid removal) is deferred to a follow-up — record as known debt.
- **Block closure** if any AC has zero traceable tests.

## Operational verification (post-closure, 7-day window)

1. Cron CPU: zero `Exceeded CPU Limit` for `*/10` schedule.
2. Stats freshness: `submissions:stats-cache.generatedAt` < 11 min on every check.
3. VM health: stats-compute systemd timer reports zero `failed` units.
4. CF endpoint health: zero 401s/400s in production logs (would indicate auth/payload regressions).
