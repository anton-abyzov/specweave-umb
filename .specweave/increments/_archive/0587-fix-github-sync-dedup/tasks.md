---
increment: 0587-fix-github-sync-dedup
title: "Fix GitHub Sync Duplication and Progress Comment Spam"
status: active
---

# Tasks: Fix GitHub Sync Duplication and Progress Comment Spam

## Task Notation

- `[ ]`: Not started | `[x]`: Completed
- TDD: RED tasks write failing tests first; GREEN tasks make them pass

---

## P0: US-001 — Progress Comment Deduplication

### T-001: [RED] Tests for github-body-utils fingerprint build/extract/normalize
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04
**Status**: [x] Completed
**Test**: Given a new `github-body-utils.test.ts` importing `buildFingerprint`, `extractFingerprint`, `normalizeIssueBody` from a file that does not yet exist → When the test suite runs → Then all tests fail with "cannot find module" confirming the RED baseline

### T-002: [GREEN] Create github-body-utils.ts with fingerprint and normalization helpers
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04
**Status**: [x] Completed
**Test**: Given `plugins/specweave/lib/integrations/github/github-body-utils.ts` exports the three functions → When T-001 tests run → Then `buildFingerprint(3, 5)` returns `"<!-- sw-progress:3/5 -->"`, `extractFingerprint` returns `"3/5"` when fingerprint is present and `null` when absent, and `normalizeIssueBody` strips trailing whitespace per line and collapses multiple blank lines to one

### T-003: [RED] Tests for postACProgressComments fingerprint dedup skip
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03
**Status**: [x] Completed
**Test**: Given a test where the mocked `gh issue list` returns an existing comment containing `<!-- sw-progress:3/5 -->` and current AC progress is also 3/5 → When `postACProgressComments` is called → Then the test asserts `gh issue comment` is never invoked, but the test fails because the current implementation unconditionally posts at lines 92-96 of `github-ac-comment-poster.ts`

### T-004: [GREEN] Add fingerprint dedup to github-ac-comment-poster.ts
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04
**Status**: [x] Completed
**Test**: Given `postACProgressComments` fetches the last SpecWeave comment via `gh issue list --label sw-progress`, extracts its fingerprint, and skips posting when fingerprint matches current progress → When T-003 tests run → Then unchanged-progress skips `gh issue comment`, changed-progress posts one comment with the updated `<!-- sw-progress:4/5 -->` fingerprint, and a first-sync with no prior comment posts one comment with the initial fingerprint embedded

---

## P0: US-002 — Duplicate Issue Prevention

### T-005: [RED] Tests for duplicate-detector Phase 3 enabled by default
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02
**Status**: [x] Completed
**Test**: Given a test that calls `DuplicateDetector.createWithProtection()` with no environment variables set and a `verifyAfterCreate` spy → When the call completes → Then the test asserts `verifyAfterCreate` was invoked, but the test fails because line 489 of `duplicate-detector.ts` gates Phase 3 behind `SPECWEAVE_VERIFY_DUPLICATES === '1'`

### T-006: [GREEN] Invert Phase 3 env var in duplicate-detector.ts
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02
**Status**: [x] Completed
**Test**: Given line 489 of `duplicate-detector.ts` now reads `process.env.SPECWEAVE_SKIP_VERIFY_DUPLICATES !== '1'` → When T-005 tests run with no env var → Then Phase 3 runs by default and the spy is called; when `SPECWEAVE_SKIP_VERIFY_DUPLICATES=1` is set the spy is not called; the old `SPECWEAVE_VERIFY_DUPLICATES=1` env var has no effect (treated as no-op)

### T-007: [RED] Tests for LockManager replacing in-memory lock in github-feature-sync.ts
**User Story**: US-002 | **Satisfies ACs**: AC-US2-03, AC-US2-04, AC-US2-05
**Status**: [x] Completed
**Test**: Given a test that asserts `github-feature-sync.ts` source no longer contains `syncLocks` Map and instead calls `LockManager.acquire` → When the source is inspected via import and the test checks for the Map → Then the test fails because `static syncLocks: Map<string, number>` is still present at lines 60-63

### T-008: [GREEN] Replace in-memory lock with LockManager in github-feature-sync.ts
**User Story**: US-002 | **Satisfies ACs**: AC-US2-03, AC-US2-04, AC-US2-05
**Status**: [x] Completed
**Test**: Given `github-feature-sync.ts` imports `LockManager`, wraps `syncFeature()` with `acquire("github-sync-{owner}-{repo}")` / `release()` using a 120s stale threshold, and the `static syncLocks: Map<string, number>` is removed → When T-007 tests run → Then the Map is absent, concurrent calls are serialized by the file lock, and the lock key matches the `github-sync-{owner}-{repo}` format from AD-2

---

## P1: US-003 — Unnecessary API Call Prevention

### T-009: [RED] Tests for body diff skip in updateUserStoryIssue
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01
**Status**: [x] Completed
**Test**: Given a test where `gh issue view` returns a body that is identical to what `updateUserStoryIssue` would compute (after normalization) → When `updateUserStoryIssue` is called → Then the test asserts `gh issue edit` is never invoked, but the test fails because lines 1021-1031 of `github-feature-sync.ts` call `gh issue edit` unconditionally

### T-010: [GREEN] Add body diff check to updateUserStoryIssue in github-feature-sync.ts
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01
**Status**: [x] Completed
**Test**: Given `updateUserStoryIssue` fetches the current body via `gh issue view`, applies `normalizeIssueBody` to both current and computed bodies, and skips `gh issue edit` when they match → When T-009 tests run → Then the no-change test passes with zero `gh issue edit` calls, the changed-body test passes with one call, and a 404 from `gh issue view` is handled gracefully (treated as "needs recreation", not a crash)

### T-011: [RED] Tests for SyncThrottle class
**User Story**: US-003 | **Satisfies ACs**: AC-US3-02, AC-US3-03, AC-US3-04
**Status**: [x] Completed
**Test**: Given a new `sync-throttle.test.ts` importing `SyncThrottle` from `src/core/sync-throttle.ts` which does not exist → When the test suite runs → Then all tests fail with "cannot find module" establishing the RED baseline

### T-012: [GREEN] Create sync-throttle.ts with SyncThrottle class
**User Story**: US-003 | **Satisfies ACs**: AC-US3-02, AC-US3-03, AC-US3-04
**Status**: [x] Completed
**Test**: Given `src/core/sync-throttle.ts` exports `SyncThrottle` with `shouldSkip(key: string, forceBypass?: boolean): boolean` and `record(key: string): void` backed by file state at `.specweave/state/sync-throttle.json` → When T-011 tests run → Then the first call to `shouldSkip` returns false, the second call within the window returns true, a call with `forceBypass=true` always returns false, and after the window expires the next call returns false

### T-013: [RED] Tests for SyncThrottle wiring in trigger paths
**User Story**: US-003 | **Satisfies ACs**: AC-US3-02, AC-US3-03
**Status**: [x] Completed
**Test**: Given tests that mock `SyncThrottle.shouldSkip` returning true for `status-change-sync-trigger.ts` and `sync-progress.ts` → When each trigger path executes → Then each test asserts no downstream sync calls are made, but both tests fail because neither file currently imports or checks `SyncThrottle`

### T-014: [GREEN] Wire SyncThrottle into all three trigger paths
**User Story**: US-003 | **Satisfies ACs**: AC-US3-02, AC-US3-03, AC-US3-04
**Status**: [x] Completed
**Test**: Given `status-change-sync-trigger.ts`, `sync-progress.ts`, and `auto-create-external-issue.ts` each import `SyncThrottle` and call `throttle.shouldSkip(incrementId)` before executing sync logic, and `sync-progress.ts` passes `forceBypass=true` when `--force` CLI flag is present → When T-013 tests run → Then throttled calls are skipped in all three paths, `--force` bypasses the throttle in `sync-progress.ts`, and `record()` is called after each successful non-throttled sync

### T-015: Integration smoke — full sync cycle with all dedup guards active
**User Story**: US-001, US-002, US-003 | **Satisfies ACs**: AC-US1-01, AC-US2-03, AC-US3-01
**Status**: [x] Completed
**Test**: Given a full simulated sync cycle runs twice in rapid succession with mocked GitHub API responses returning unchanged issue bodies and an existing `<!-- sw-progress:3/5 -->` comment → When both sync runs complete → Then zero duplicate `gh issue comment` calls occur, zero redundant `gh issue edit` calls occur, and the second run is either throttled by `SyncThrottle` or short-circuited by fingerprint and body-diff checks
