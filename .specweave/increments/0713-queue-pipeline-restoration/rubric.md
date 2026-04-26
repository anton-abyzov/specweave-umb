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
| Production verification — Phase 1 | Deferred to **0713B-production-rollout** (operator-only, requires `wrangler deploy` + production DB access) | Operator (Anton) |
| Production verification — Phase 2 | Deferred to **0713B-production-rollout** (operator-only, requires `wrangler deploy`) | Operator (Anton) |
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
| AC-US2-01 | T-006, T-007 | T-006 |
| AC-US2-02 | T-006, T-007 | T-006 |
| AC-US2-03 | T-006, T-007 | T-006 |
| AC-US2-04 | T-007 | T-006 |
| AC-US3-01 | T-014, T-015 | T-014 |
| AC-US3-02 | T-014, T-015 | T-014 |
| AC-US3-03 | T-016 | T-016 |
| AC-US4-01 | T-009, T-010 | T-009 |
| AC-US4-03 | T-011 | T-011 |
| AC-US4-04 | T-009, T-010 | T-009 |
| AC-US5-01 | T-018, T-019 | T-018 |
| AC-US5-02 | T-018, T-019 | T-018 |
| AC-US5-03 | T-020 | T-020 |
| AC-US5-04 | T-021 | T-021, T-022 |
| AC-US5-05 | T-021 | T-021 |

> AC-US1-06, AC-US2-05, AC-US3-04, AC-US4-02, AC-US5-06, AC-US5-07 are production-verification ACs — moved to **0713B-production-rollout** (AC-US101-02, AC-US101-03, AC-US103-02, AC-US102-02, AC-US104-02, AC-US104-03 respectively).

## Grill Verdicts (Phase 0 — sw:grill 2026-04-25)

| AC | Result | Evidence |
|----|--------|----------|
| AC-US1-01 | [x] PASS | `src/lib/cron/queue-stats-refresh.ts:67-93` — flat `COUNT(*) FILTER (...)` against `Submission`; deduped CTE removed |
| AC-US1-02 | [x] PASS | `src/lib/cron/queue-stats-refresh.ts:217-244` rewrites to FAILURE_SENTINEL on Phase 1 fail; sentinel writes both KV+`_memQueueStats` |
| AC-US1-03 | [x] PASS | `src/lib/queue/queue-stats-freshness.ts:50-59` `shouldOverwriteStats` — sentinel as next/prev always passes; tests at `queue-stats-refresh.test.ts:74-76,82-85` |
| AC-US1-04 | [x] PASS | `queue-stats-freshness.ts:57` `prev.total > 0 && next.total === 0 → false`; verified in `queue-stats-refresh.test.ts:78-80` |
| AC-US1-05 | [x] PASS | `queue-stats-freshness.ts:56` (sentinel→real recovery) + `queue-stats-refresh.ts:241` unconditional `_memQueueStats = candidate` |
| AC-US2-01 | [x] PASS | `src/app/api/v1/submissions/route.ts:81-120` — well-formed `{submissions:[],total:0}` returned as-is at line 106-108; JSON parse failure returns null |
| AC-US2-02 | [x] PASS | `route.ts:197-211` returns 503 with `Retry-After: 30` and `hint: "database_unavailable"` when KV miss + DB unavailable |
| AC-US2-03 | [x] PASS | `route.ts:497-512` logs `list_empty_total_mismatch` and adds warning to body when DB returns 0 but `_memQueueStats` indicates rows expected |
| AC-US2-04 | [x] PASS | `route.ts:515-562` outer catch routes DB errors to 503 fallback (with KV-cache rescue paths) instead of returning empty array |
| AC-US3-01 | [x] PASS | `src/lib/submission/state-history.ts:41-46` `buildStateHistoryEntry` throws on null `to`; allows null `from` only when `to === "RECEIVED"`; called by `db-persist.ts:185` before any DB write |
| AC-US3-02 | [!] PARTIAL | `hist:<id>` writes go through `buildStateHistoryEntry` (kv-store.ts:188,237). However, the on-disk JSON shape uses the legacy field names `state` (= AC's `to`) and `message` (= AC's `reason`). The skill code documents this as a deliberate back-compat translation (state-history.ts:17-21). Functionally satisfied, but the literal field names in the AC do not match disk. Doc-comment justification accepted. |
| AC-US3-03 | [x] PASS | `scripts/backfill-state-history.ts:80-110` planHistoryBackfill — pure decision function; idempotent via `metadata.backfilled === true` check; `--dry-run` flag honored at lines 175-180 |
| AC-US4-01 | [x] PASS (helper) | `src/lib/queue/recovery.ts:484-551` `drainStuckReceived(opts, env)` accepts `repoUrl?, ageMin, limit, dryRun` and runs the documented SQL+enqueue logic. **CAVEAT** — see scope-creep note below: the **CLI script does NOT call this helper** in production. |
| AC-US4-03 | [!] PARTIAL | `recoverStaleReceived` is wired into `.open-next/worker-with-queues.js:169` and runs on every cron tick. Two literal deviations from spec: (1) the cron runs every **10 min** (`*/10 * * * *` in wrangler.jsonc:189), not 30 min as AC text states. (2) The threshold is **`updatedAt` < NOW() - 15 min** (`submission/recovery.ts:18,75-95`), not `createdAt < NOW() - 30 min`. The behavior is more aggressive than required and self-throttles via `db.submission.update({updatedAt:new Date()})` (recovery.ts:614-617). Spirit satisfied; literal text not. |
| AC-US4-04 | [!] PARTIAL | The unit test `drain-stuck-received.test.ts:101-117` proves `drainStuckReceived` helper skips `inflight:<id>` markers in `QUEUE_METRICS_KV`. **However**, the production CLI script `scripts/drain-stuck-received.ts` does not invoke this helper — it POSTs to `/api/v1/admin/reenqueue`, whose `repoUrl` branch (`reenqueue/route.ts:111-194`) uses a different idempotency mechanism (`recovery:retried:<id>` markers in `SUBMISSIONS_KV`, capped at 3). Both paths are independently idempotent, but the test does not exercise the path the operator will actually run. (Already tracked as F-002 in the iteration-1 code-review.) |
| AC-US5-01 | [x] PASS | `src/app/queue/data.ts:80` `if (requestedFilter) return [requestedFilter]` is the first branch — URL filter always wins; tests at `choose-boot-candidates.test.ts:34-45` |
| AC-US5-02 | [x] PASS | `data.ts:81` `if (stats.degraded) return ["all"]` runs before the ranked-count fallback; test at `choose-boot-candidates.test.ts:47-59` |
| AC-US5-03 | [x] PASS | `QueueStatusBar.tsx:128-144` renders ribbon with `aria-live="polite"` and copy "Counters refreshing…" when `statsDegraded === true` |
| AC-US5-04 | [x] PASS | `QueuePageClient.tsx:75-80` `TAB_CONFIG` matches spec exactly (active=processingOrder asc, published/rejected/blocked=updatedAt desc, all=createdAt desc) |
| AC-US5-05 | [x] PASS | `QueuePageClient.tsx:75-80` timeColumn labels exactly match spec (Submitted/Updated/Last activity); applied at line 849 |

**Scope creep**: None detected — every implemented file traces to an AC.

## Closure Gate Decisions

This rubric is consumed by `sw:done` and the closure gates (`sw:code-reviewer`, `/simplify`, `sw:grill`, `sw:judge-llm`, `sw:validate`).

- **Block closure** if any AC has zero traceable tests.
- **Production verification is NOT a blocker for 0713 closure** — it was split out to **0713B-production-rollout** because operator credentials are required. 0713 closes at "implementation complete; production execution tracked in 0713B."
- **Allow closure with warning** if Phase 2 UX changes ship but their e2e tests are flaky on first run; document and re-run before final deploy.
- **Allow closure** if the deferred items in spec.md "Out of Scope" are explicitly tracked as 0714/0715 increments — do not extend this increment to cover them.

## Operational verification

After closure, the following monitors must remain green for 24 hours:

1. `submissions:stats-cache` `generatedAt` recent (< 11 min) on every check
2. No `list_empty_total_mismatch` warnings in logs
3. RECEIVED-row count in DB does not climb above 50 (the recovery cron's per-tick limit)
4. No 503 spike on `/api/v1/submissions` in CF analytics

If any of these fail, cut a follow-up hotfix increment immediately.
