# Tasks: Auto-Close External Issues on status:complete Sync

## Task Notation

- `[T###]`: Task ID
- `[P]`: Parallelizable
- `[ ]`: Not started
- `[x]`: Completed
- Model hints: haiku (simple), opus (default)

## Phase 1: GitHub Auto-Close (US-001, US-004)

### T-001: Write failing tests for updateStatusLabels auto-close behavior
**User Story**: US-001, US-004 | **Satisfies ACs**: AC-US1-04, AC-US1-05, AC-US4-01, AC-US4-03 | **Status**: [x] completed
**Test**: Given updateStatusLabels() is called with overallComplete=true on an OPEN issue -> When the method completes -> Then `gh issue close` is called with a completion comment

**Description**: Create test file `tests/unit/plugins/github/github-feature-sync-auto-close.test.ts`. Write tests that mock `GitHubClientV2.getIssue()`, `execFileNoThrow`, and `CompletionCalculator` to verify:

1. **TC-001**: overallComplete=true + issue OPEN -> `gh issue close` called + completion comment posted
2. **TC-002**: overallComplete=true + issue CLOSED -> no close attempt (idempotent)
3. **TC-003**: overallComplete=false (status:active) -> no close attempt
4. **TC-004**: Calling twice with overallComplete=true on CLOSED issue -> zero side effects

**Implementation Details**:
- Mock `execFileNoThrow` to capture CLI args
- Mock `GitHubClientV2.getIssue()` to return `{ state: 'open', labels: [...] }` or `{ state: 'closed', labels: [...] }`
- Assert `gh issue close` is called with correct issue number and `--comment` flag
- Assert no `gh issue close` call when issue already closed

**File**: `repositories/anton-abyzov/specweave/tests/unit/plugins/github/github-feature-sync-auto-close.test.ts`

**Dependencies**: None
**Model**: opus

---

### T-002: Fix updateStatusLabels to close issue on status:complete
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03 | **Status**: [x] completed
**Test**: Given T-001 tests exist -> When the fix is applied -> Then all T-001 tests pass (TDD GREEN)

**Description**: Modify `updateStatusLabels()` in `github-feature-sync.ts` to close the issue after applying `status:complete` label.

**Implementation Details**:
- After Step 2 (adding the new status label), add a conditional block:
  ```
  if newStatusLabel === 'status:complete' AND issueData.state !== 'closed':
    build completion comment from calculator
    call gh issue close with --comment
    log closure
  ```
- The `issueData` is already fetched at line 978 (`this.client.getIssue(issueNumber)`)
- The `completion` object is already a parameter with `overallComplete`, `acsPercentage`, etc.
- Need to extend `completion` parameter type to include `acsCompleted`, `acsTotal`, `tasksCompleted`, `tasksTotal` fields needed by `buildCompletionComment()`
- Wrap close call in try/catch for non-blocking behavior (consistent with label update)

**File**: `repositories/anton-abyzov/specweave/plugins/specweave-github/lib/github-feature-sync.ts`

**Dependencies**: T-001
**Model**: opus

---

## Phase 2: Progress-Sync CLI Enhancement (US-002, US-003)

### T-003: Write failing test for progress-sync invoking AC provider sync
**User Story**: US-002, US-003 | **Satisfies ACs**: AC-US2-02, AC-US3-02 | **Status**: [x] completed
**Test**: Given progress-sync is called with JIRA/ADO configured -> When sync runs -> Then syncACProgressToProviders is invoked with correct config

**Description**: Extend `tests/unit/cli/commands/sync-progress.test.ts` to verify that the progress-sync CLI invokes `syncACProgressToProviders()` for all configured providers (not just GitHub checkbox sync).

**Implementation Details**:
- Mock `syncACProgressToProviders` from `ac-progress-sync.ts`
- Mock `parseAllUserStoryIds` to return test US IDs
- Assert `syncACProgressToProviders` is called with correct incrementId, US IDs, specPath, and config
- Test with JIRA enabled, ADO enabled, and both enabled scenarios

**File**: `repositories/anton-abyzov/specweave/tests/unit/cli/commands/sync-progress.test.ts`

**Dependencies**: None (parallel with T-001)
**Model**: opus

---

### T-004: Wire syncACProgressToProviders into sync-progress.ts CLI
**User Story**: US-002, US-003 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US3-01, AC-US3-02 | **Status**: [x] completed
**Test**: Given T-003 tests exist -> When the wiring is added -> Then T-003 tests pass (TDD GREEN)

**Description**: In `sync-progress.ts`, after the GitHub AC checkbox sync (Step 5/5), add a call to `syncACProgressToProviders()` to handle JIRA transitions and ADO state changes.

**Implementation Details**:
- Import `syncACProgressToProviders`, `parseAllUserStoryIds`, and `buildACProgressContext` from `ac-progress-sync.ts`
- After `syncCoordinator.syncACCheckboxesToGitHub()`, add:
  ```
  1. Parse all US IDs from spec.md using parseAllUserStoryIds()
  2. Build ACProgressSyncConfig from config.json and metadata.json
  3. Call syncACProgressToProviders(incrementId, usIds, specPath, syncConfig)
  4. Log results per provider
  ```
- Gate behind `permissionsOk` check (same as existing sync)
- Non-blocking: wrap in try/catch, log errors as warnings

**File**: `repositories/anton-abyzov/specweave/src/cli/commands/sync-progress.ts`

**Dependencies**: T-003
**Model**: opus

---

## Phase 3: Verification

### T-005: Verify all tests pass and no regressions
**User Story**: US-001, US-002, US-003, US-004 | **Satisfies ACs**: AC-US4-02 | **Status**: [ ] not started
**Test**: Given all changes from T-001..T-004 are applied -> When full test suite runs -> Then all existing tests pass + new tests pass

**Description**: Run the full test suite to verify no regressions.

**Implementation Details**:
- Run `npm test` in the specweave repo
- Verify: `tests/unit/plugins/github/github-feature-sync-auto-close.test.ts` passes
- Verify: `tests/unit/cli/commands/sync-progress.test.ts` passes
- Verify: `tests/unit/core/ac-progress-sync.test.ts` passes
- Verify: No existing test regressions

**Dependencies**: T-002, T-004
**Model**: haiku
