# Tasks: Reduce GitHub API Calls Phase 2

## Phase 1: Tests (TDD Red)

### T-001: Write tests for rate-limit budget module

**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04
**Status**: [x] Completed

**Test Plan**:
- **TC-001**: Given no state file → When getRemainingBudget() → Then returns 5000 (default)
- **TC-002**: Given state file with remaining=100 → When checkBudget() → Then returns false (below 200 threshold)
- **TC-003**: Given state file with remaining=4000 → When decrementBudget() → Then file updated to 3999
- **TC-004**: Given state file older than 5min → When checkBudget() → Then validates via actual API call
- **TC-005**: Given concurrent decrements → When two processes write → Then no data loss (atomic)

### T-002: Write tests for reconciler lock

**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03
**Status**: [x] Completed

**Test Plan**:
- **TC-006**: Given no lock → When acquireLock() → Then lock file created with PID
- **TC-007**: Given fresh lock (< 5min) → When acquireLock() → Then returns false (skip)
- **TC-008**: Given stale lock (> 5min) → When acquireLock() → Then cleans up and acquires

### T-003: Write tests for persistent label cache and skip-linked-issues

**User Story**: US-003, US-004 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US4-01, AC-US4-02
**Status**: [x] Completed

**Test Plan**:
- **TC-009**: Given disk cache with labels → When ensureLabels() → Then 0 API calls
- **TC-010**: Given no disk cache → When ensureLabels() → Then creates + persists
- **TC-011**: Given metadata has issue number → When sync runs → Then skips createWithProtection()
- **TC-012**: Given direct edit mode → When updating body → Then 1 API call (not 2)

## Phase 2: Implementation (TDD Green)

### T-004: Implement github-rate-limit-budget.ts

**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04
**Status**: [x] Completed

**Implementation**: New module at `src/sync/github-rate-limit-budget.ts`:
- `checkBudget(): Promise<boolean>` — reads state file, returns false if < 200
- `decrementBudget(): Promise<void>` — atomic decrement
- `validateBudget(): Promise<void>` — calls `gh api rate_limit`, updates state file
- Integrate into `GitHubClientV2` — wrap every `execFileNoThrow('gh', ...)` call

### T-005: Implement reconciler lock

**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03
**Status**: [x] Completed

**Implementation**: Add lock logic to `github-reconciler.ts`:
- `acquireLock(): boolean` — check/create `.specweave/state/reconciler.lock`
- `releaseLock(): void` — delete lock file
- In `reconcile()`: acquire at start, release at end (finally block)
- Stale detection: PID not running OR timestamp > 5min

### T-006: Implement persistent label cache and skip-linked-issues

**User Story**: US-003, US-004 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US4-01, AC-US4-02
**Status**: [x] Completed

**Implementation**:
- Modify `label-cache.ts`: add `loadFromDisk()` / `saveToDisk()` using `.specweave/state/github-label-cache.json`
- Modify `github-feature-sync.ts`: check metadata for issue number before calling `createWithProtection()`; if linked, call `updateIssue()` directly

## Phase 3: Verify

### T-007: Run tests and measure API reduction

**User Story**: US-001, US-002, US-003, US-004 | **Satisfies ACs**: All
**Status**: [x] Completed

**Verification**:
1. `npx vitest run` — all 77 tests pass across 6 test files
2. Measure: `BEFORE=$(gh api rate_limit --jq '.rate.remaining') && specweave sync-living-docs 0615 && AFTER=$(gh api rate_limit --jq '.rate.remaining') && echo "Used: $(($BEFORE - $AFTER))"`
3. Target: < 10 calls for repeat sync of existing 3-US increment
