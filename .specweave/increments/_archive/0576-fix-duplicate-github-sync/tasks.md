# Tasks: Fix duplicate GitHub sync during specweave complete

## Task Notation

- `[T###]`: Task ID
- `[P]`: Parallelizable
- `[ ]`: Not started
- `[x]`: Completed
- Model hints: haiku (simple), opus (default)

## Phase 1: Core Fix

### US-001: Eliminate redundant GitHub API calls during completion (P1)

#### T-001: Remove syncGitHubProject from onIncrementDone

**Description**: Remove the redundant `syncGitHubProject` async function, `shouldSyncGitHubProject` flag, and simplify the `Promise.all` to a direct `await syncClosure()` call. Update the Step 2 comment.

**References**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04

**Implementation Details**:
- Remove `shouldSyncGitHubProject` flag (line ~219)
- Remove `syncGitHubProject` async function (lines ~266-283)
- Remove `syncGitHubProject()` entry from `Promise.all` (line ~305); simplify to `await syncClosure()`
- Update Step 2 comment to reflect only JIRA/ADO closure runs (not "direct GitHub sync in parallel")

**Test Plan**:
- **File**: `tests/unit/core/hooks/lifecycle-hook-dispatcher.test.ts`
- **Tests**:
  - **TC-001**: syncFeatureToGitHub called exactly once per completion
    - Given `onIncrementDone()` is called with living docs sync and GitHub sync enabled
    - When the method completes
    - Then `syncFeatureToGitHub` is called exactly once (via LivingDocsSync chain only)

**Dependencies**: None
**Status**: [x] Completed

---

#### T-002: Update unit tests — remove obsolete GitHub project sync tests

**Description**: Remove tests for the deleted `syncGitHubProject` code path and clean up unused mocks.

**References**: AC-US1-05, AC-US1-06

**Implementation Details**:
- Remove TC-017 (`sync_to_github_project=true` dispatches GitHub sync directly)
- Remove TC-018 (`sync_to_github_project=false` skips GitHub sync)
- Remove TC-020 (feature ID resolution for GitHub project sync)
- Update TC-019 to remove any reference to GitHub project sync failure
- Remove `mockSyncFeatureToGitHub` and `mockResolveFeatureId` from test mocks if no longer used
- Add TC-NEW: verify `syncFeatureToGitHub` called exactly once when both living docs and GitHub sync are enabled

**Test Plan**:
- **File**: `tests/unit/core/hooks/lifecycle-hook-dispatcher.test.ts`
- **Tests**:
  - **TC-NEW**: syncFeatureToGitHub invoked exactly once
    - Given completion is triggered with `sync_living_docs=true` and GitHub configured
    - When `onIncrementDone()` runs
    - Then `syncFeatureToGitHub` mock count equals 1

**Dependencies**: T-001
**Status**: [x] Completed

## Phase 2: Verification

#### T-003: Run full test suite and confirm no regressions

**Description**: Execute the Vitest suite in the specweave repo to confirm all existing tests pass after the removal.

**References**: AC-US1-05, AC-US1-06

**Implementation Details**:
- Run `npx vitest run` in `repositories/anton-abyzov/specweave/`
- Confirm JIRA/ADO closure sync tests pass
- Confirm living docs sync tests pass

**Test Plan**:
- All tests green — zero failures

**Dependencies**: T-001, T-002
**Status**: [x] Completed
