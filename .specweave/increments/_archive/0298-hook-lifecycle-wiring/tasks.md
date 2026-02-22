# Tasks: Hook Lifecycle Wiring

## Task Notation

- `[T###]`: Task ID
- `[P]`: Parallelizable
- `[ ]`: Not started
- `[x]`: Completed
- Model hints: haiku (simple), opus (default)

## Phase 1: Core Dispatcher

### US-001: Post-Increment-Planning Hook Fires (P1)
### US-002: Post-Task-Completion Hook Fires (P1)
### US-003: Post-Increment-Done Hook Fires (P1)
### US-004: Config-Driven Behavior (P2)

#### T-001: Create LifecycleHookDispatcher module

**User Story**: US-001, US-002, US-003, US-004 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US2-01, AC-US2-02, AC-US2-03, AC-US3-01, AC-US3-02, AC-US3-03, AC-US4-01, AC-US4-02, AC-US4-03 | **Status**: [x] completed

**Description**: Create `src/core/hooks/LifecycleHookDispatcher.ts` with three static methods:

- `onIncrementPlanned(projectRoot, incrementId)` - reads `hooks.post_increment_planning` config, calls `autoCreateExternalIssue` if `auto_create_github_issue=true`
- `onTaskCompleted(projectRoot, incrementId)` - reads `hooks.post_task_completion` config, triggers sync if enabled
- `onIncrementDone(projectRoot, incrementId)` - reads `hooks.post_increment_done` config, triggers living docs sync / GitHub project sync / issue closure per settings

All methods: non-blocking (fire-and-forget async), error-isolated (catch + log), skip in test environment.

**Implementation**:
- [x] Create LifecycleHookDispatcher class with static methods
- [x] Read hooks config via ConfigManager
- [x] `onIncrementPlanned`: check `auto_create_github_issue`, call autoCreateExternalIssue
- [x] `onTaskCompleted`: check `sync_tasks_md` and `external_tracker_sync`, dispatch accordingly
- [x] `onIncrementDone`: check `sync_living_docs`, `sync_to_github_project`, `close_github_issue`, `update_living_docs_first`
- [x] Guard: skip all dispatch if `process.env.NODE_ENV === 'test'` or `process.env.VITEST`
- [x] Guard: skip if no `hooks` key in config (safe default)
- [x] Handle partial config gracefully (optional chaining)

**Test Plan**:
- **File**: `tests/unit/core/hooks/lifecycle-hook-dispatcher.test.ts`
- **Tests**:
  - **TC-001**: onIncrementPlanned calls autoCreateExternalIssue when auto_create_github_issue=true
    - Given config has hooks.post_increment_planning.auto_create_github_issue=true
    - When onIncrementPlanned is called with incrementId
    - Then autoCreateExternalIssue is called with correct args
  - **TC-002**: onIncrementPlanned skips when auto_create_github_issue=false
    - Given config has auto_create_github_issue=false
    - When onIncrementPlanned is called
    - Then autoCreateExternalIssue is NOT called
  - **TC-003**: onIncrementPlanned skips when hooks config is missing
    - Given config has no hooks key
    - When onIncrementPlanned is called
    - Then no sync functions are called
  - **TC-004**: onIncrementPlanned catches and logs errors (non-blocking)
    - Given autoCreateExternalIssue throws
    - When onIncrementPlanned is called
    - Then error is logged, no exception propagates
  - **TC-005**: onTaskCompleted dispatches sync when sync_tasks_md=true
    - Given config has hooks.post_task_completion.sync_tasks_md=true
    - When onTaskCompleted is called
    - Then task sync is triggered
  - **TC-006**: onTaskCompleted dispatches external tracker sync when enabled
    - Given config has hooks.post_task_completion.external_tracker_sync=true
    - When onTaskCompleted is called
    - Then external tracker sync is triggered
  - **TC-007**: onTaskCompleted skips all when both disabled
    - Given both sync_tasks_md and external_tracker_sync are false
    - When onTaskCompleted is called
    - Then no sync operations run
  - **TC-008**: onIncrementDone dispatches living docs sync when enabled
    - Given hooks.post_increment_done.sync_living_docs=true
    - When onIncrementDone is called
    - Then LivingDocsSync.syncIncrement is called
  - **TC-009**: onIncrementDone dispatches issue closure when close_github_issue=true
    - Given hooks.post_increment_done.close_github_issue=true
    - When onIncrementDone is called
    - Then SyncCoordinator.syncIncrementClosure is called
  - **TC-010**: onIncrementDone respects update_living_docs_first ordering
    - Given update_living_docs_first=true and sync_living_docs=true
    - When onIncrementDone is called
    - Then living docs sync completes before GitHub sync starts
  - **TC-011**: All methods skip in test environment
    - Given process.env.VITEST is set
    - When any dispatch method is called
    - Then nothing is dispatched
  - **TC-012**: Partial config is handled gracefully
    - Given hooks.post_increment_planning exists but post_task_completion does not
    - When onTaskCompleted is called
    - Then no error, method returns cleanly

**Dependencies**: None
**Model Hint**: opus

---

## Phase 2: Wiring

#### T-002: Wire onIncrementPlanned into createIncrementCommand

**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-03 | **Status**: [x] completed

**Description**: In `src/cli/commands/create-increment.ts`, after `createIncrementTemplates()` succeeds, call `LifecycleHookDispatcher.onIncrementPlanned()`. The call must be non-blocking (fire-and-forget).

**Implementation**:
- [x] Import LifecycleHookDispatcher
- [x] After `result.success` check, call `onIncrementPlanned(projectRoot, id)` in fire-and-forget pattern
- [x] Ensure errors don't affect the success output to user

**Test Plan**:
- **File**: `tests/unit/cli/commands/create-increment.test.ts` (extend existing or create)
- **Tests**:
  - **TC-013**: createIncrementCommand calls onIncrementPlanned after success
    - Given createIncrementTemplates returns success
    - When createIncrementCommand runs
    - Then LifecycleHookDispatcher.onIncrementPlanned is called
  - **TC-014**: createIncrementCommand does NOT call onIncrementPlanned on failure
    - Given createIncrementTemplates returns failure
    - When createIncrementCommand runs
    - Then onIncrementPlanned is NOT called

**Dependencies**: T-001
**Model Hint**: haiku

---

#### T-003: Wire onIncrementDone into completeIncrement

**User Story**: US-003 | **Satisfies ACs**: AC-US3-01 | **Status**: [x] completed

**Description**: In `src/core/increment/status-commands.ts` `completeIncrement()`, after successful status update to COMPLETED, call `LifecycleHookDispatcher.onIncrementDone()`. Must coordinate with existing StatusChangeSyncTrigger to avoid duplicate work.

**Implementation**:
- [x] Import LifecycleHookDispatcher (dynamic import to avoid circular deps)
- [x] After `MetadataManager.updateStatus(incrementId, COMPLETED)` succeeds, call `onIncrementDone`
- [x] Fire-and-forget pattern with error catching

**Test Plan**:
- **File**: `tests/unit/core/increment/status-commands.test.ts` (extend or create)
- **Tests**:
  - **TC-015**: completeIncrement calls onIncrementDone after successful completion
    - Given increment is active and validation passes
    - When completeIncrement runs successfully
    - Then LifecycleHookDispatcher.onIncrementDone is called with incrementId
  - **TC-016**: completeIncrement does NOT call onIncrementDone when validation fails
    - Given increment fails quality gates
    - When completeIncrement returns false
    - Then onIncrementDone is NOT called

**Dependencies**: T-001
**Model Hint**: haiku

---

## Phase 3: Verification

#### T-004: Run existing test suite and verify no regressions

**User Story**: US-004 | **Satisfies ACs**: AC-US4-01 | **Status**: [x] completed

**Description**: Run the full Vitest suite to confirm zero regressions. Ensure the test environment guard prevents real dispatch during tests.

**Implementation**:
- [x] Run `npm test` in the specweave repo
- [x] Verify all existing tests pass
- [x] Verify new tests pass
- [x] Confirm no accidental real API calls in test environment

**Test Plan**:
- **Tests**:
  - **TC-017**: Full test suite passes
    - Given all changes are applied
    - When `npm test` runs
    - Then all tests pass with 0 failures

**Dependencies**: T-001, T-002, T-003
**Model Hint**: haiku
