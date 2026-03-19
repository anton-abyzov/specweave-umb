# Tasks: GitHub Reconciler Recency Window

## Phase 1: Tests (TDD Red)

### T-001: Write tests for bulk fetch and reconciler optimization

**User Story**: US-001, US-002, US-003 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US2-01, AC-US2-02, AC-US3-01, AC-US3-02, AC-US3-03
**Status**: [x] Completed

**Test Plan**:
- **File**: `tests/unit/sync/github-reconciler-bulk.test.ts`
- **Tests**:
  - **TC-001**: Given GitHubClientV2 → When bulkFetchIssueStates() called → Then returns Map from single search
  - **TC-002**: Given pre-fetched map → When reconcileIssue() for issue in map → Then does NOT call getIssue()
  - **TC-003**: Given pre-fetched map → When reconcileIssue() for issue NOT in map → Then falls back to getIssue()
  - **TC-004**: Given default mode → When bulk fetch → Then limit is 100
  - **TC-005**: Given full mode → When bulk fetch → Then limit is 1000
  - **TC-006**: Given default mode → When milestone fetch → Then per_page=20 (no --paginate)
  - **TC-007**: Given full mode → When milestone fetch → Then uses --paginate
  - **TC-008**: Given ReconcileOptions full=true → Then propagated to both bulk fetch and milestones

**Dependencies**: None

## Phase 2: Implementation (TDD Green)

### T-002: Add bulkFetchIssueStates() to GitHubClientV2

**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-04
**Status**: [x] Completed

**Implementation Details**:
1. Add to `plugins/specweave/lib/integrations/github/github-client-v2.ts`
2. Uses `gh search issues "repo:{fullRepo} [FS- in:title" --json number,state --limit {limit}`
3. Returns `Map<number, 'open' | 'closed'>`
4. Default limit=100, full mode=1000

**Dependencies**: T-001

### T-003: Integrate bulk fetch into reconciler + milestone cap + --full flag

**User Story**: US-001, US-002, US-003 | **Satisfies ACs**: AC-US1-02, AC-US1-03, AC-US2-01, AC-US2-02, AC-US3-01, AC-US3-02, AC-US3-03
**Status**: [x] Completed

**Implementation Details**:
1. Add `full?: boolean` to `ReconcileOptions`
2. In `reconcile()`: call `bulkFetchIssueStates()`, pass map through
3. In `reconcileIssue()`: check map first, fallback to getIssue()
4. In `reconcileMilestones()`: replace `--paginate` with `per_page=20&sort=updated&direction=desc`
5. When full=true: restore --paginate and use limit=1000
6. Wire --full in CLI command

**Dependencies**: T-002

## Phase 3: Verify

### T-004: Run full test suite

**User Story**: US-001, US-002, US-003 | **Satisfies ACs**: All
**Status**: [ ] Not Started

**Dependencies**: T-002, T-003
