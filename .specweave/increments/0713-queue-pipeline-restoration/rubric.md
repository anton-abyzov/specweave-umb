---
increment: 0713-queue-pipeline-restoration
title: "Queue Pipeline Restoration (P0)"
generated: "2026-04-24"
source: hand-authored
version: "1.0"
status: ready
---

# Quality Contract

This increment is a P0 production hotfix. The bar is "platform restored, observable, regression-tested" — not "polished UX." Phase 2 UX changes ride along because they're cheap and address the same user-visible pain.

## Quality Gates

| Gate | Threshold | Owner |
|------|-----------|-------|
| Type-check | `npx tsc --noEmit` exits 0 | Implementer |
| Unit tests | All new + existing in `tests/unit/{queue,submission,cron}/`, `tests/unit/scripts/` pass | Implementer |
| Integration tests | All new in `tests/integration/api-submissions-list-failure.test.ts` and `tests/integration/cron/recover-stale-received.test.ts` pass | Implementer |
| E2E tests | `npx playwright test tests/e2e/queue*.spec.ts` passes including new `queue-default-sort.spec.ts` and `queue-degraded-no-flip.spec.ts` | Implementer |
| TDD enforcement | Each task pair (RED → GREEN) demonstrably has failing test commits before passing implementation commits | Implementer |
| Coverage | New code in `src/lib/queue/queue-stats-freshness.ts`, `src/lib/queue/recovery.ts`, `scripts/drain-stuck-received.ts`, `scripts/backfill-state-history.ts` ≥ 90% lines | Implementer |
| Production verification — Phase 1 | `/api/v1/submissions/stats` returns `degraded:false` and `generatedAt < 11 min`; `/api/v1/submissions?state=all&limit=10` returns ≥ 10 items; the 6 hyperframes IDs leave RECEIVED within 60s of drain | Implementer |
| Production verification — Phase 2 | Visiting `/queue` does NOT redirect to `?filter=published`; `/queue?filter=all` renders rows sorted by `createdAt` desc; each tab shows ONE time column | Implementer |
| Pre-existing test triage | If `npx vitest run` reveals pre-existing failures unrelated to this increment, document them in PR description; do NOT extend scope to fix them | Implementer |

## Acceptance Criteria Coverage

Every AC in spec.md must be traceable to at least one task in tasks.md AND at least one passing test (unit, integration, or e2e).

| AC | Task(s) | Test(s) |
|----|---------|---------|
| AC-US1-01 | T-002 | T-005 (manual verify) |
| AC-US1-02 | T-002 | T-001, T-002 |
| AC-US1-03 | T-001, T-002 | T-001 |
| AC-US1-04 | T-001 | T-001 |
| AC-US1-05 | T-001, T-002 | T-001 |
| AC-US1-06 | T-002, T-004, T-005, T-012 | T-005 (post-deploy) |
| AC-US2-01 | T-006, T-007 | T-006 |
| AC-US2-02 | T-006, T-007 | T-006 |
| AC-US2-03 | T-006, T-007 | T-006 |
| AC-US2-04 | T-007 | T-006 |
| AC-US2-05 | T-008, T-012 | T-008 (post-deploy) |
| AC-US3-01 | T-014, T-015 | T-014 |
| AC-US3-02 | T-014, T-015 | T-014 |
| AC-US3-03 | T-016 | T-016 |
| AC-US3-04 | T-017 | T-017 (manual verify) |
| AC-US4-01 | T-009, T-010 | T-009 |
| AC-US4-02 | T-013 | T-013 (manual verify) |
| AC-US4-03 | T-011 | T-011 |
| AC-US4-04 | T-009, T-010 | T-009 |
| AC-US5-01 | T-018, T-019 | T-018 |
| AC-US5-02 | T-018, T-019 | T-018 |
| AC-US5-03 | T-020 | T-020 |
| AC-US5-04 | T-021 | T-021, T-022 |
| AC-US5-05 | T-021 | T-021 |
| AC-US5-06 | T-022, T-023, T-024 | T-022 |
| AC-US5-07 | T-022, T-023, T-024 | T-022 |

## Closure Gate Decisions

This rubric is consumed by `sw:done` and the closure gates (`sw:code-reviewer`, `/simplify`, `sw:grill`, `sw:judge-llm`, `sw:validate`).

- **Block closure** if any P0 production verification (Phase 1 verifications above) is unmet.
- **Block closure** if any AC has zero traceable tests.
- **Allow closure with warning** if Phase 2 UX changes ship but their e2e tests are flaky on first run; document and re-run before final deploy.
- **Allow closure** if the deferred items in spec.md "Out of Scope" are explicitly tracked as 0714/0715 increments — do not extend this increment to cover them.

## Operational verification

After closure, the following monitors must remain green for 24 hours:

1. `submissions:stats-cache` `generatedAt` recent (< 11 min) on every check
2. No `list_empty_total_mismatch` warnings in logs
3. RECEIVED-row count in DB does not climb above 50 (the recovery cron's per-tick limit)
4. No 503 spike on `/api/v1/submissions` in CF analytics

If any of these fail, cut a follow-up hotfix increment immediately.
