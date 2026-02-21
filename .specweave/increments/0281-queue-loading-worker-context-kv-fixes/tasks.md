# Tasks: Queue Loading, Worker-Context, and KV Fixes

## Task Notation

- `[T###]`: Task ID
- `[P]`: Parallelizable
- `[ ]`: Not started
- `[x]`: Completed
- Model hints: haiku (simple), opus (default)

## Phase 1: Parallel KV reads in getSubmissionsFresh

### US-001: Parallel KV reads in getSubmissionsFresh (P1)

#### T-001: Write failing tests for parallel getSubmissionsFresh

**Description**: Add unit tests that verify `getSubmissionsFresh()` reads KV keys in parallel, not sequentially. Tests should verify parallel invocation and graceful error handling for individual key failures.

**References**: AC-US1-01, AC-US1-02, AC-US1-03

**Implementation Details**:
- Add tests to `src/lib/__tests__/submission-store.test.ts`
- Test 1: Verify all KV.get calls are initiated before any resolve (parallel behavior)
- Test 2: Verify that a failing/missing key does not block other keys from being read
- Test 3: Verify empty array input returns empty array

**Test Plan**:
- **File**: `src/lib/__tests__/submission-store.test.ts`
- **Tests**:
  - **TC-050**: getSubmissionsFresh reads all keys in parallel
    - Given 5 submission IDs
    - When getSubmissionsFresh is called
    - Then all 5 KV.get calls are initiated concurrently (not sequentially)
  - **TC-051**: getSubmissionsFresh handles individual key failures
    - Given 3 submission IDs where 1 key returns null
    - When getSubmissionsFresh is called
    - Then 2 valid submissions are returned, the missing one is skipped
  - **TC-052**: getSubmissionsFresh handles empty input
    - Given an empty array
    - When getSubmissionsFresh is called
    - Then an empty array is returned without KV calls

**Dependencies**: None
**Status**: [x] Completed

---

#### T-002: Refactor getSubmissionsFresh to use Promise.allSettled

**References**: AC-US1-01, AC-US1-02, AC-US1-03

**Implementation Details**:
- Replaced sequential `for` loop with `Promise.allSettled(ids.map(...))` in `src/lib/submission-store.ts`

**Dependencies**: T-001
**Status**: [x] Completed

## Phase 2: Worker-context hardening

### US-002: Worker-context race condition safety (P1)

#### T-003: Write failing tests for getKV defensive fallback

**References**: AC-US2-01, AC-US2-03

**Dependencies**: None
**Status**: [x] Completed

---

#### T-004: Add defensive error handling to getKV

**References**: AC-US2-01, AC-US2-03

**Implementation Details**:
- Wrapped `getCloudflareContext()` in try/catch in `src/lib/submission-store.ts::getKV()` — throws `"SUBMISSIONS_KV unavailable: not in worker or Next.js request context"` on failure

**Dependencies**: T-003
**Status**: [x] Completed

---

#### T-005: Verify consumer clearWorkerEnv safety

**References**: AC-US2-02

**Implementation Details**:
- Added TC-054 to `src/lib/queue/__tests__/consumer.test.ts`; also fixed pre-existing `makeEnv()` bug (missing KV `.get` mock)

**Dependencies**: None
**Status**: [x] Completed

## Phase 3: Integration verification

### US-003: Queue page initial load data accuracy (P1)

#### T-006: Verify submissions route handler merge logic

**References**: AC-US3-01, AC-US3-02

**Implementation Details**:
- Added TC-055 to `src/app/api/v1/submissions/__tests__/route.pagination.test.ts` — verifies stale RECEIVED state is overridden by fresh TIER1_SCANNING from re-hydration

**Dependencies**: T-002
**Status**: [x] Completed

---

#### T-007: Run full test suite and verify no regressions

**References**: AC-US3-03

**Result**: 754 passed | 5 pre-existing failures in unrelated files (bulk-submission, discovery-enrichment — db mock issues, not related to this increment)

**Dependencies**: T-002, T-004, T-005, T-006
**Status**: [x] Completed
