---
increment: 0713-queue-pipeline-restoration
title: "Queue Pipeline Restoration (P0) — Tasks"
test_mode: TDD
---

# Tasks

STRICT TDD: every task pair is RED → GREEN. Refactor folded inline where applicable.

## Phase 1 — P0 outage recovery (must ship first)

### T-001: RED — stats regression guard tests
**User Story**: US-001 | **Satisfies ACs**: AC-US1-03, AC-US1-04, AC-US1-05 | **Status**: [x] completed
**Test Plan**:
- Given a fresh in-memory `_memQueueStats` is null
- When the regression guard is asked to compare null prev vs `{total: 100, active: 5, ...}` next
- Then it returns `true` (overwrite)
- And given prev=`{total: 100, active: 5}`, next=`{total: 0, active: 0}` → returns `false` (block 0-after-positive)
- And given prev=`{total: 100, active: 5}`, next=`{total: -1, ...}` (sentinel) → returns `true` (record outage)
- And given prev=`{total: -1, ...}` (sentinel), next=`{total: 100, active: 5}` (real) → returns `true` (recovery)
- Test file: `tests/unit/cron/queue-stats-refresh.test.ts`
- Tests MUST fail before implementation.

### T-002: GREEN — implement stats sentinel + guard
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05 | **Status**: [x] completed
**Test Plan**:
- Given the stats cron runs against a healthy DB
- When `computeQueueStats` succeeds
- Then it writes `{total, active, ..., degraded: false}` to KV `submissions:stats-cache` and `_memQueueStats`
- Given the stats cron runs against a failing DB (timeout, throw)
- When `computeQueueStats` throws
- Then it writes `{total: -1, active: -1, ..., degraded: true, error: "<reason>"}` sentinel
- Given a sentinel is currently in `_memQueueStats`
- When the next successful cron run produces real stats
- Then the sentinel is overwritten unconditionally
- Implementation: drop the deduped CTE in `src/lib/cron/queue-stats-refresh.ts`; add `isFailureSentinel` to `src/lib/queue/queue-stats-freshness.ts`; update `shouldOverwriteStats` per plan.md.
- T-001 tests pass.

### T-003: REFACTOR — extract sentinel constants + types
**User Story**: US-001 | **Satisfies ACs**: code quality | **Status**: [x] completed
- Move `FAILURE_SENTINEL` to a shared constants file (`src/lib/queue/queue-stats-types.ts` if it doesn't exist).
- Tests still pass.

### T-004: GREEN — clamp -1 in /api/v1/submissions/stats response
**User Story**: US-001 | **Satisfies ACs**: AC-US1-06 | **Status**: [x] completed
**Test Plan**:
- Given KV `submissions:stats-cache` contains a sentinel `{total: -1, ...}`
- When `GET /api/v1/submissions/stats` is called
- Then the response body has `total: 0` (clamped) AND `degraded: true` (preserved)
- File: `src/app/api/v1/submissions/stats/route.ts` + new test in `tests/unit/api/submissions-stats.test.ts`

### T-005: VERIFY — manual stats cron tick
**User Story**: US-001 | **Satisfies ACs**: AC-US1-06 | **Status**: [ ] pending
- Run `wrangler tail` and trigger the cron manually (or wait for next 10-min tick).
- Confirm `submissions:stats-cache` `generatedAt` updates within 11 min and `degraded: false`.
- Document outcome in PR description.

### T-006: RED — list endpoint failure-surface tests
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04 | **Status**: [x] completed
**Test Plan**:
- Given KV cache contains `{submissions: [], total: 0}` (legitimate empty cached payload)
- When `parseUsableListCache` is called
- Then it returns the cached payload (NOT null)
- Given KV cache is missing
- When the GET handler runs and the DB query throws
- Then the response is 503 with `Retry-After: 30` and body `{error: "Service temporarily unavailable", hint: "database_unavailable"}`
- Given KV cache is missing AND DB returns 0 rows AND stats show `total > 0`
- When the GET handler runs
- Then the response is 200 with `{items: [], total: 0, warning: "list_empty_total_mismatch"}` AND a console.warn was emitted
- Test file: `tests/integration/api-submissions-list-failure.test.ts`
- Tests MUST fail before implementation.

### T-007: GREEN — implement list endpoint changes
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04, AC-US2-05 | **Status**: [x] completed
**Test Plan**:
- Update `parseUsableListCache` (`src/app/api/v1/submissions/route.ts:78-94`): only return null when JSON parse fails or required fields missing. A well-formed `{submissions: [], total: 0}` is a valid cached payload.
- Wrap non-category branch (lines 401-412) in try/catch routing to existing 503 path at lines 472-491.
- Add stats-vs-list mismatch check after successful DB query that returns 0 rows.
- T-006 tests pass.

### T-008: VERIFY — list endpoint smoke test
**User Story**: US-002 | **Satisfies ACs**: AC-US2-05 | **Status**: [ ] pending
- After deploy: `curl -s 'https://verified-skill.com/api/v1/submissions?state=all&sort=createdAt&sortDir=desc&limit=10' | jq '.items | length'` returns ≥ 10.
- `curl -s 'https://verified-skill.com/api/v1/submissions?state=active&limit=5' | jq` returns submission objects (or warning if truly empty).

### T-009: RED — drain script tests
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-04 | **Status**: [x] completed
**Test Plan**:
- Given a Submission with `state=RECEIVED` and `createdAt < NOW() - 5 min`
- When `drainStuckReceived({ageMin: 5})` is called
- Then it calls `SUBMISSION_QUEUE.send` with `{type: "process_submission", submissionId: row.id}` exactly once
- Given `--dry-run` is set
- When `drainStuckReceived({ageMin: 5, dryRun: true})` is called
- Then no `SUBMISSION_QUEUE.send` is invoked but the would-be drains are logged
- Given a Submission with `state=RECEIVED` and `KV inflight:<id>` is set
- When `drainStuckReceived` is called
- Then that submission is skipped (no enqueue)
- Test file: `tests/unit/scripts/drain-stuck-received.test.ts`

### T-010: GREEN — implement drain script + recovery helper
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02, AC-US4-04 | **Status**: [x] completed
**Test Plan**:
- Create `src/lib/queue/recovery.ts` exporting `drainStuckReceived({repoUrl?, ageMin, limit, dryRun, prisma, queue, kv})`.
- Create `scripts/drain-stuck-received.ts` CLI that parses argv and calls the helper.
- Logic per plan.md.
- T-009 tests pass.

### T-011: GREEN — wire `recoverStaleReceived` cron
**User Story**: US-004 | **Satisfies ACs**: AC-US4-03 | **Status**: [x] completed
**Test Plan**:
- Given the cron handler runs at its 30-min schedule
- When there is at least one Submission with `state=RECEIVED AND createdAt < NOW() - 30 min`
- Then `drainStuckReceived({ageMin: 30, limit: 50})` is invoked and at least one queue.send fires
- Test file: `tests/integration/cron/recover-stale-received.test.ts`
- Verify presence in `.open-next/worker-with-queues.js`'s `scheduled()` handler. If missing, add. If broken, fix.

### T-012: DEPLOY — Phase 1 to production
**User Story**: US-001, US-002, US-004 | **Satisfies ACs**: deployment | **Status**: [ ] pending
- `cd repositories/anton-abyzov/vskill-platform`
- `npm run build && npx wrangler deploy` (or the existing deploy script — check package.json `scripts.deploy` and CLAUDE.md notes)
- After deploy: T-005 + T-008 verifications pass.

### T-013: EXECUTE — drain stuck hyperframes rows
**User Story**: US-004 | **Satisfies ACs**: AC-US4-02 | **Status**: [ ] pending
- `node scripts/drain-stuck-received.ts --repo-url https://github.com/heygen-com/hyperframes --age-min 5 --dry-run` → review intended drains
- `node scripts/drain-stuck-received.ts --repo-url https://github.com/heygen-com/hyperframes --age-min 5` → execute
- Within 60s, all 6 IDs (`sub_4ce1d8a7…`, `sub_e64164f1…`, `sub_1ce97022…`, `sub_79d9e244…`, `sub_b8642378…`, `sub_4a5b43de…`) transition out of RECEIVED.

## Phase 2 — observability + UX (ship after Phase 1 verified)

### T-014: RED — state-history shape tests
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02 | **Status**: [ ] pending
**Test Plan**:
- Given a transition `from=RECEIVED, to=TIER1_SCANNING, reason="queue.consume"`
- When `appendStateHistory(...)` is called
- Then the entry written to DB and KV has `{timestamp: ISO, from: "RECEIVED", to: "TIER1_SCANNING", reason: "queue.consume"}`
- Given an attempt to write `{to: null}`
- When the writer is called
- Then it throws `Error("state history requires non-null 'to'")`
- Given an attempt to write `{from: null, to: "RECEIVED"}` (initial)
- When the writer is called
- Then it succeeds (initial RECEIVED is the only allowed null-from case)
- Test file: `tests/unit/submission/state-history.test.ts`

### T-015: GREEN — implement type-safe state-history writer
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02 | **Status**: [ ] pending
- Replace `src/lib/submission/db-persist.ts:190` per plan.md.
- Export `StateHistoryEntry` type if not already exported.
- T-014 tests pass.

### T-016: GREEN — backfill script for malformed history
**User Story**: US-003 | **Satisfies ACs**: AC-US3-03, AC-US3-04 | **Status**: [ ] pending
**Test Plan**:
- Given a Submission row with empty history
- When `backfillStateHistory({dryRun: false})` runs
- Then a single entry `{from: null, to: row.state, reason: "backfill:reconstructed", timestamp: row.updatedAt, backfilled: true}` is appended
- Given a Submission row whose latest history entry has `to: null`
- When backfill runs
- Then the malformed entry is replaced with reconstructed shape
- Idempotent: re-running detects `backfilled: true` and skips
- File: `scripts/backfill-state-history.ts` + `tests/unit/scripts/backfill-state-history.test.ts`

### T-017: EXECUTE — backfill against production
**User Story**: US-003 | **Satisfies ACs**: AC-US3-04 | **Status**: [ ] pending
- `node scripts/backfill-state-history.ts --dry-run | head -50` → review
- `node scripts/backfill-state-history.ts` → execute
- Verify 6 hyperframes records have well-formed history via `curl /api/v1/submissions/<id> | jq '.submission.stateHistory'`.

### T-018: RED — chooseBootCandidates tests
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01, AC-US5-02 | **Status**: [ ] pending
**Test Plan**:
- Given `requestedFilter = "active"` and any stats
- When `chooseBootCandidates(stats, "active")` is called
- Then it returns `["active"]` (URL filter wins unconditionally)
- Given `requestedFilter` is undefined and `stats.degraded === true`
- When called
- Then returns `["all"]` (never `["published"]`)
- Given `requestedFilter` is undefined and `stats.degraded === false` and `stats.active > 0`
- When called
- Then returns a ranked list starting with `"active"`
- Test file: `tests/unit/queue/choose-boot-candidates.test.ts`

### T-019: GREEN — implement chooseBootCandidates per plan
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01, AC-US5-02 | **Status**: [ ] pending
- Update `src/app/queue/data.ts:59-66` per plan.md.
- T-018 tests pass.

### T-020: GREEN — degraded-stats UI message
**User Story**: US-005 | **Satisfies ACs**: AC-US5-03 | **Status**: [ ] pending
- Locate the stats bar component (`src/app/queue/components/StatsBar.tsx` or where the 6 stat cards render).
- When `stats.degraded === true`, render an inline ribbon with copy "Counters refreshing…" and `aria-live="polite"`.
- Component test using existing test patterns.

### T-021: GREEN — per-tab default sort + single time column
**User Story**: US-005 | **Satisfies ACs**: AC-US5-04, AC-US5-05 | **Status**: [ ] pending
- Add `TAB_CONFIG` object to `src/app/queue/QueuePageClient.tsx` per plan.md.
- When URL `?sort=` and `?dir=` are absent, use `TAB_CONFIG[filter].defaultSort` for the API request.
- Replace dual time columns with single contextual column from `TAB_CONFIG[filter].timeColumn`.
- Component snapshot or behavior test.

### T-022: RED — e2e default-sort + no-flip tests
**User Story**: US-005 | **Satisfies ACs**: AC-US5-06, AC-US5-07 | **Status**: [ ] pending
**Test Plan**:
- E2E: visit `/queue?filter=all` → top row's `createdAt` is the max in the visible page
- E2E: mock `/api/v1/submissions/stats` to return `{degraded: true, active: 0, ...}`; visit `/queue` → URL stays `/queue` (no redirect to `?filter=published`)
- Files: `tests/e2e/queue-default-sort.spec.ts`, `tests/e2e/queue-degraded-no-flip.spec.ts`

### T-023: GREEN — fix any e2e gaps
**User Story**: US-005 | **Satisfies ACs**: AC-US5-06, AC-US5-07 | **Status**: [ ] pending
- T-022 tests pass.

### T-024: DEPLOY — Phase 2 to production
**User Story**: US-003, US-005 | **Satisfies ACs**: deployment | **Status**: [ ] pending
- `npx wrangler deploy`
- Manual verification: visit `/queue` and `/queue?filter=all` per the verification block in plan.md.

### T-025: VALIDATE — full regression sweep
**User Story**: All | **Satisfies ACs**: regression | **Status**: [ ] pending
- `npx vitest run` — all green
- `npx playwright test tests/e2e/queue*.spec.ts` — all green
- `npx tsc --noEmit` — clean
- Document any pre-existing failures (per `interview-0690-triage-preexisting-vitest-failures.json` there may be known gaps; flag them in PR description but do NOT extend scope).

## Test pattern reference

- **Vitest** (mirror `tests/integration/versions-compare-github.test.ts:1-48`):
  ```typescript
  import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
  import { readFileSync } from "node:fs";
  import { fileURLToPath } from "node:url";
  import path from "node:path";
  ```
- **Playwright** (mirror `tests/e2e/queue.spec.ts:1-26`):
  ```typescript
  import { test, expect } from "@playwright/test";
  test.describe("...", () => {
    test.setTimeout(60000);
    test.beforeEach(async ({ page }) => {
      await page.goto("/queue", { waitUntil: "domcontentloaded" });
      await expect(page.locator('[data-testid="queue-status-bar"]')).toBeVisible({ timeout: 30000 });
    });
  });
  ```
