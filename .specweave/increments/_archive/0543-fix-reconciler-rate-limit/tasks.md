# Tasks: Fix GitHub API Rate Limit Exhaustion in Reconciler

## US-001: Status-Based Search Filtering

### T-001: Add mockWriteFile to hoisted mocks in test file
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05
**Status**: [x] Completed
**Test**: Given the test file's hoisted mock block, when `mockWriteFile` is added to `vi.hoisted()` and `vi.mock('fs', ...)` includes `writeFile`, then all tests that exercise negative cache write-back compile and run without "not a function" errors.

---

### T-002: Write failing tests for status-based search filtering (RED)
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05
**Status**: [x] Completed
**Test**: Given a `describe('status-based search filtering')` block in `github-reconciler.test.ts`, when tests assert that `mockSearchIssuesByFeature` is NOT called for `completed`, `abandoned`, `created` statuses and IS called for `active`, `planning`, `in-progress`, `backlog`, `ready_for_review`, `paused` statuses, then running `npx vitest run` shows all new tests FAILING (RED).

---

### T-003: Implement SEARCHABLE_STATUSES constant and status filter in scanIncrements (GREEN)
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05
**Status**: [x] Completed
**Test**: Given `SEARCHABLE_STATUSES = ['active','planning','in-progress','backlog','ready_for_review','paused']` defined at module level in `github-reconciler.ts`, and a guard `const status = metadata.status || 'unknown'; if (!SEARCHABLE_STATUSES.includes(status)) { /* skip search */ }` added before the existing search call at line 354, when `npx vitest run` is executed, then all status-filter tests from T-002 pass (GREEN).

---

### T-004: Refactor status filter to handle missing status field edge case (REFACTOR)
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05
**Status**: [x] Completed
**Test**: Given the status guard uses `metadata.status || 'unknown'` so a missing field defaults to `'unknown'` (not in allowlist), when a new test supplies metadata with no `status` field and asserts `mockSearchIssuesByFeature` is NOT called, then `npx vitest run` passes all status-filter tests including the missing-status edge case.

---

## US-002: Negative Search Cache in Metadata

### T-005: Write failing tests for negative cache read guard (RED)
**User Story**: US-002 | **Satisfies ACs**: AC-US2-02
**Status**: [x] Completed
**Test**: Given a `describe('negative cache - read guard')` block where metadata for an active increment contains `github: { noIssuesFound: true }`, when `scanIncrements()` is called, then `mockSearchIssuesByFeature` is NOT called, and the test runs RED before the guard is implemented.

---

### T-006: Implement noIssuesFound read guard in scanIncrements (GREEN)
**User Story**: US-002 | **Satisfies ACs**: AC-US2-02
**Status**: [x] Completed
**Test**: Given `if (metadata.github?.noIssuesFound === true) { /* skip search */ }` added after the status filter check in `scanIncrements()`, when `npx vitest run` is executed, then the T-005 test passes (GREEN) and no pre-existing tests regress.

---

### T-007: Write failing tests for negative cache write-back (RED)
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-03, AC-US2-04
**Status**: [x] Completed
**Test**: Given three tests — (a) empty search result with no main issue causes `mockWriteFile` to be called with `github.searched=true`, `github.searchedAt`, `github.noIssuesFound=true`; (b) non-empty result does NOT call `mockWriteFile` with negative markers; (c) empty result but `metadata.github.issue` is present does NOT write negative markers — when `npx vitest run` is executed, then all three tests run RED.

---

### T-008: Implement negative cache write-back after confirmed empty search result (GREEN)
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-03, AC-US2-04
**Status**: [x] Completed
**Test**: Given logic added to `searchGitHubForIssues()` that after finding zero results checks `!state.mainIssue` and writes `{ ...metadata.github, searched: true, searchedAt: new Date().toISOString(), noIssuesFound: true }` back to `metadataPath` via `fs.writeFile` wrapped in try/catch, when `npx vitest run` is executed, then all three T-007 tests pass (GREEN) and `mockWriteFile` call arguments match expected JSON.

---

### T-009: Refactor write-back to be non-fatal on disk failure (REFACTOR)
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-03, AC-US2-04
**Status**: [x] Completed
**Test**: Given `mockWriteFile` configured to reject (simulating disk failure) in a new test, when `scanIncrements()` runs, then it does NOT throw and `result.errors` remains empty, confirming the try/catch wrapper swallows write failures with a `logger.warn` call only.

---

## US-003: Session Search Cache in GitHub Client

### T-010: Write failing tests for searchIssuesByFeature session cache (RED)
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03
**Status**: [x] Completed
**Test**: Given a dedicated test file or describe block that imports `GitHubClientV2` directly and mocks `execFileNoThrow`, when three tests assert — (a) first call with "FS-100" executes `execFileNoThrow` once and stores result in cache; (b) second call within 30s returns cached result without calling `execFileNoThrow` again; (c) call after cache TTL expiry (mock `Date.now()` to advance 31s) triggers a fresh `execFileNoThrow` call — then all three run RED.

---

### T-011: Add static searchCache Map to GitHubClientV2 and wrap searchIssuesByFeature (GREEN)
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03
**Status**: [x] Completed
**Test**: Given `private static searchCache = new Map<string, { data: GitHubIssue[]; fetchedAt: number }>()` added after the existing `issueCache` declaration in `github-client-v2.ts`, and `searchIssuesByFeature()` updated to compute `cacheKey = \`\${this.fullRepo}#search:\${featureId}\${userStoryId ? ':' + userStoryId : ''}\``, check the map before `execFileNoThrow`, and set the map after, when `npx vitest run` is executed, then all three T-010 tests pass (GREEN).

---

### T-012: Refactor searchCache to use existing CACHE_TTL_MS constant (REFACTOR)
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03
**Status**: [x] Completed
**Test**: Given the TTL check in `searchIssuesByFeature()` uses `GitHubClientV2.CACHE_TTL_MS` (the existing 30s constant, not a magic number), when `npx vitest run` is executed, then all three cache tests still pass and the implementation is consistent with the `issueCache` pattern already in the file.

---

## US-004: Search Budget Per Scan

### T-013: Write failing tests for per-scan search budget cap (RED)
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-04
**Status**: [x] Completed
**Test**: Given four tests — (a) exactly 20 increments needing search all trigger `mockSearchIssuesByFeature` (budget not exhausted); (b) 21st increment needing search is skipped and `mockSearchIssuesByFeature` is called exactly 20 times; (c) increment with existing `metadata.github.issue: 42` when budget is exhausted still appears in reconcile results (no data loss); (d) a second `scanIncrements()` call resets counter to 0 and search runs again — when `npx vitest run` shows all four RED.

---

### T-014: Implement per-scan search budget counter in scanIncrements (GREEN)
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-04
**Status**: [x] Completed
**Test**: Given `let searchesMade = 0; let skippedDueToBudget = 0` declared before the loop in `scanIncrements()`, a guard `if (searchesMade >= 20) { skippedDueToBudget++; continue; }` before calling `searchGitHubForIssues()`, `searchesMade++` after each search call, and `if (skippedDueToBudget > 0) this.logger.log(...)` after the loop, when `npx vitest run` is executed, then all four T-013 tests pass (GREEN).

---

### T-015: Refactor budget log message format and verify no data loss for metadata-backed increments (REFACTOR)
**User Story**: US-004 | **Satisfies ACs**: AC-US4-02, AC-US4-03
**Status**: [x] Completed
**Test**: Given the post-loop log reads `Skipped N search(es) due to budget exhaustion (limit: 20)`, when an increment has `metadata.github.issue: 42` and budget is exhausted, then it still appears in `scanIncrements()` results and `npx vitest run` confirms all budget tests pass with the exact log message string.

---

## Integration Verification

### T-016: Run full test suite and verify no regressions
**User Story**: US-001, US-002, US-003, US-004 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05, AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04, AC-US3-01, AC-US3-02, AC-US3-03, AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-04
**Status**: [x] Completed
**Test**: Given all implementation tasks T-001 through T-015 are complete, when `npx vitest run tests/unit/sync/github-reconciler.test.ts` is executed, then all pre-existing tests pass unchanged and all new tests pass, confirming full AC coverage with no regressions.
