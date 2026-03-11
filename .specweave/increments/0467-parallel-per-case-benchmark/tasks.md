---
increment: 0467-parallel-per-case-benchmark
total_tasks: 14
completed_tasks: 14
---

# Tasks: Parallel Per-Case Benchmark Execution



## User Story: US-001 - Run a Single Test Case Independently

**Linked ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04
**Tasks**: 3 total, 3 completed



### T-001: Create Semaphore concurrency primitive

**User Story**: US-001
**Satisfies ACs**: AC-US1-03, AC-US3-03
**Status**: [x] completed

**Test Plan**:
- **Given** a Semaphore with max=2
- **When** 3 callers call `acquire()` concurrently
- **Then** at most 2 resolve immediately and the 3rd waits; calling `release()` unblocks the 3rd

**Test Cases**:
1. **Unit**: `repositories/anton-abyzov/vskill/src/eval-server/concurrency.test.ts`
   - `testSemaphoreEnforcesMaxConcurrency()`: Acquire max slots, 3rd blocks until release
   - `testSemaphoreQueuingBehavior()`: FIFO queue — callers unblock in order
   - `testSemaphoreReleaseIdempotent()`: Extra `release()` calls are no-ops (no underflow)
   - `testSemaphoreAvailableAndPending()`: `available` and `pending` getters reflect correct counts
   - **Coverage Target**: 95%

**Implementation**:
1. Create `repositories/anton-abyzov/vskill/src/eval-server/concurrency.ts`
2. Implement `Semaphore` class with `acquire()`, `release()`, `available`, `pending`
3. Export `DEFAULT_CONCURRENCY = 3`
4. All imports use `.js` extensions (ESM)
5. Run `npx vitest run concurrency.test` to verify



### T-002: Extract `runSingleCaseSSE` from benchmark runner and add per-case API routes

**User Story**: US-001
**Satisfies ACs**: AC-US1-03, AC-US1-04
**Status**: [x] completed

**Test Plan**:
- **Given** a POST to `/api/skills/:plugin/:skill/benchmark/case/:evalId`
- **When** the server handles the request
- **Then** it executes only that one eval case, streams SSE events scoped to that evalId, and releases the semaphore slot in `finally`

**Test Cases**:
1. **Unit**: `repositories/anton-abyzov/vskill/src/eval-server/benchmark-runner.test.ts`
   - `testRunSingleCaseSSESuccessPath()`: Mock LlmClient, verify SSE event sequence (start → result → done)
   - `testRunSingleCaseSSEErrorPath()`: LlmClient throws, case transitions to error, no other cases affected
   - `testRunSingleCaseSSEAbortPath()`: AbortController aborted mid-run, SSE stream closes cleanly
   - `testAssembleBulkResult()`: Correct aggregate pass_rate and duration from array of BenchmarkCase results
   - **Coverage Target**: 90%

2. **Integration**: `repositories/anton-abyzov/vskill/src/eval-server/api-routes.test.ts`
   - `testPerCaseEndpointRespondsWithSSE()`: Route exists, returns SSE content-type, emits done event
   - `testPerCaseEndpointSemaphoreReleasedOnError()`: Semaphore slot is released when handler throws
   - **Coverage Target**: 85%

**Implementation**:
1. In `benchmark-runner.ts`: extract `runSingleCaseSSE(opts: SingleCaseRunOptions): Promise<BenchmarkCase>`
2. Add `assembleBulkResult(cases, meta): BenchmarkResult` helper
3. In `api-routes.ts`: add `POST .../benchmark/case/:evalId` and `POST .../baseline/case/:evalId` routes
4. Add `POST .../benchmark/bulk-save` route
5. Implement per-skill Semaphore registry (`getSkillSemaphore`)
6. Use `res.on('close')` safety net with double-release guard
7. All `.js` extensions in imports



### T-003: Add `scope` field to `BenchmarkResult` type

**User Story**: US-001
**Satisfies ACs**: AC-US1-03, AC-US4-01, AC-US4-02
**Status**: [x] completed

**Test Plan**:
- **Given** a `BenchmarkResult` produced by a single-case run
- **When** the `scope` field is checked
- **Then** it equals `"single"`; a bulk result has `scope: "bulk"`; legacy results with no field are handled as bulk

**Test Cases**:
1. **Unit**: `repositories/anton-abyzov/vskill/src/eval/benchmark.test.ts`
   - `testBenchmarkResultScopeFieldAcceptsAllValues()`: Type accepts `"single"`, `"bulk"`, and `undefined`
   - **Coverage Target**: 80%

**Implementation**:
1. In `src/eval/benchmark.ts`: add `scope?: "single" | "bulk"` to `BenchmarkResult` interface
2. Single-case endpoint sets `scope: "single"` before calling `writeHistoryEntry`
3. Bulk-save endpoint sets `scope: "bulk"`



## User Story: US-002 - Cancel a Running Case Independently

**Linked ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04
**Tasks**: 2 total, 2 completed



### T-004: Implement `useMultiSSE` hook with per-case AbortController management

**User Story**: US-002
**Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US6-02
**Status**: [x] completed

**Test Plan**:
- **Given** a `useMultiSSE` hook managing two active SSE streams (cases A and B)
- **When** `stopCase(A)` is called
- **Then** only case A's AbortController is aborted; case B's stream continues; case B eventually reaches `"done"` status

**Test Cases**:
1. **Unit**: `repositories/anton-abyzov/vskill/src/eval-ui/src/sse.test.ts`
   - `testStartCaseCreatesIndependentStream()`: `startCase` creates separate AbortController per evalId
   - `testStopCaseAbortsOnlyTargetCase()`: `stopCase(1)` aborts case 1, case 2's controller unaffected
   - `testStopAllAbortsEveryStream()`: `stopAll()` aborts all active controllers
   - `testMemoryCleanupOnDone()`: AbortController reference cleared when stream reaches `done`
   - `testRestartCaseCreatesNewStream()`: Calling `startCase(1)` after `stopCase(1)` creates a fresh stream
   - **Coverage Target**: 90%

**Implementation**:
1. In `src/eval-ui/src/sse.ts`: add `CaseStream` interface and `useMultiSSE` hook
2. `streams` state is `Map<number, CaseStream>` (new Map instance on each update for React re-render)
3. `startCase(evalId, url, body?)`: create AbortController, fetch with SSE parsing, append events
4. `stopCase(evalId)`: abort controller for that evalId only
5. `stopAll()`: iterate all controllers, abort each
6. Preserve existing `useSSE` hook unchanged



### T-005: Wire cancel controls in reducer and context; hide Cancel button for non-running cases

**User Story**: US-002
**Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04
**Status**: [x] completed

**Test Plan**:
- **Given** the workspace reducer with `CASE_RUN_CANCEL` action
- **When** the action fires for case A while case B is running
- **Then** case A's state becomes `"cancelled"` and case B's state remains `"running"`

**Test Cases**:
1. **Unit**: `repositories/anton-abyzov/vskill/src/eval-ui/src/pages/workspace/workspaceReducer.test.ts`
   - `testCaseRunCancelSetsStatusToCancelled()`: CASE_RUN_CANCEL sets target case to cancelled
   - `testCaseRunCancelDoesNotAffectOtherCases()`: Other cases' states unchanged
   - `testCancelledCaseCanRestartWithCaseRunStart()`: CASE_RUN_START from cancelled → running
   - **Coverage Target**: 90%

**Implementation**:
1. In `workspaceReducer.ts`: add `CASE_RUN_CANCEL` handler
2. In `WorkspaceContext.tsx`: implement `cancelCase(evalId)` — calls `multiSSE.stopCase`, dispatches `CASE_RUN_CANCEL`
3. In `TestsPanel.tsx` / `RunPanel.tsx`: render Cancel button only when `caseRunStates.get(evalId)?.status === "running"`
4. Cancel button disabled/hidden for idle, complete, error, cancelled states (AC-US2-04)



## User Story: US-003 - Parallel Bulk Execution with Concurrency Control

**Linked ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04, AC-US3-05
**Tasks**: 3 total, 3 completed



### T-006: Implement `BULK_RUN_START` and `BULK_RUN_COMPLETE` reducer actions

**User Story**: US-003
**Satisfies ACs**: AC-US3-01, AC-US3-04, AC-US6-04
**Status**: [x] completed

**Test Plan**:
- **Given** a workspace state with 5 idle cases
- **When** `BULK_RUN_START` action fires with all 5 evalIds
- **Then** all 5 cases transition to `"queued"`, `bulkRunActive` becomes `true`, and `runMode` is set

**Test Cases**:
1. **Unit**: `repositories/anton-abyzov/vskill/src/eval-ui/src/pages/workspace/workspaceReducer.test.ts`
   - `testBulkRunStartSetsAllCasesToQueued()`: All specified evalIds set to "queued"
   - `testBulkRunStartSetsBulkRunActive()`: `bulkRunActive` becomes true
   - `testBulkRunCompleteStoresBenchmarkResult()`: Result stored, `bulkRunActive` false, iterationCount incremented
   - `testBulkRunCompleteDoesNotAffectActiveCases()`: Cases that errored remain in their state
   - **Coverage Target**: 90%

**Implementation**:
1. In `workspaceReducer.ts`: add `BULK_RUN_START` handler (set all evalIds to "queued", `bulkRunActive=true`)
2. Add `BULK_RUN_COMPLETE` handler (store benchmark, `bulkRunActive=false`, increment iterationCount)
3. Update initial state: `caseRunStates: new Map()`, `bulkRunActive: false`



### T-007: Implement `runAll()` with server-side semaphore-limited parallel execution

**User Story**: US-003
**Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04, AC-US3-05
**Status**: [x] completed

**Test Plan**:
- **Given** 5 cases and a server Semaphore with max=3
- **When** `runAll()` fires all 5 per-case fetches simultaneously
- **Then** server processes at most 3 concurrently; queued cases start as slots free; all 5 complete via `Promise.allSettled` (no fail-fast)

**Test Cases**:
1. **Unit**: `repositories/anton-abyzov/vskill/src/eval-server/concurrency.test.ts`
   - `testSemaphoreLimitsToMaxConcurrent()`: With 5 acquirers and max=3, at most 3 resolve before any release
   - `testSemaphoreAllSettledNoFailFast()`: One rejected acquire does not block others
   - **Coverage Target**: 90%

2. **Integration**: `repositories/anton-abyzov/vskill/src/eval-server/api-routes.test.ts`
   - `testBulkSaveRouteWritesHistoryWithBulkScope()`: POST /bulk-save stores BenchmarkResult with `scope: "bulk"`
   - **Coverage Target**: 85%

**Implementation**:
1. In `WorkspaceContext.tsx`: implement `runAll(mode?)`:
   - Dispatch `BULK_RUN_START`
   - For each evalId call `multiSSE.startCase(evalId, url, { bulk: true })`
   - All fetches fired immediately; server Semaphore limits concurrency
2. Monitor `multiSSE.streams` in useEffect; when all done/error, POST to `/benchmark/bulk-save`
3. Dispatch `BULK_RUN_COMPLETE` with assembled result



### T-008: Implement per-case status transitions (queued → running → complete/error)

**User Story**: US-003
**Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-05, AC-US6-01, AC-US6-04
**Status**: [x] completed

**Test Plan**:
- **Given** a case in `"queued"` state
- **When** its per-case SSE stream emits its first event (server acquired semaphore slot)
- **Then** the case transitions from `"queued"` to `"running"`; when stream completes it transitions to `"complete"`

**Test Cases**:
1. **Unit**: `repositories/anton-abyzov/vskill/src/eval-ui/src/pages/workspace/workspaceReducer.test.ts`
   - `testCaseRunStartFromQueuedToRunning()`: CASE_RUN_START sets queued case to running
   - `testCaseRunCompleteFromRunning()`: CASE_RUN_COMPLETE sets running case to complete, stores result
   - `testCaseRunErrorDoesNotAffectOtherCases()`: CASE_RUN_ERROR on case A; case B stays running
   - **Coverage Target**: 90%

**Implementation**:
1. In `workspaceReducer.ts`: add `CASE_RUN_START`, `CASE_RUN_COMPLETE`, `CASE_RUN_ERROR` handlers
2. CASE_RUN_START: set target case to "running", clear previous inline result
3. CASE_RUN_COMPLETE: set to "complete", merge InlineResult into `inlineResults` map
4. CASE_RUN_ERROR: set to "error", store error message
5. In `WorkspaceContext.tsx`: SSE event processing useEffect dispatches these actions per stream



## User Story: US-004 - Per-Case History Saving

**Linked ACs**: AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-04
**Tasks**: 2 total, 2 completed



### T-009: Save single-case and bulk-run history entries with `scope` field

**User Story**: US-004
**Satisfies ACs**: AC-US4-01, AC-US4-02, AC-US4-04
**Status**: [x] completed

**Test Plan**:
- **Given** a single-case run that completes on the per-case endpoint (no `bulk` flag)
- **When** the server writes the history entry
- **Then** the entry has `scope: "single"` and contains exactly one case; a bulk-save entry has `scope: "bulk"` and contains all completed cases

**Test Cases**:
1. **Integration**: `repositories/anton-abyzov/vskill/src/eval-server/api-routes.test.ts`
   - `testSingleCaseEndpointWritesHistoryWithSingleScope()`: History file written with `scope: "single"`, one case
   - `testBulkSaveWritesHistoryWithBulkScope()`: History written with `scope: "bulk"`, all cases present
   - `testGetCaseHistoryIncludesSingleAndBulkEntries()`: Per-case history query returns entries from both run types
   - **Coverage Target**: 85%

**Implementation**:
1. Single-case endpoint: after `runSingleCaseSSE` completes (no `bulk: true` in body), call `writeHistoryEntry` with `scope: "single"`
2. `bulk-save` endpoint: call `writeHistoryEntry` with assembled result having `scope: "bulk"`
3. No changes needed to `writeHistoryEntry` signature — `scope` propagates via BenchmarkResult
4. Existing `getCaseHistory` query naturally includes single-case entries (AC-US4-04)



### T-010: Display `scope` differentiation in history panel UI

**User Story**: US-004
**Satisfies ACs**: AC-US4-03
**Status**: [x] completed

**Test Plan**:
- **Given** a history panel displaying benchmark runs
- **When** a history entry with `scope: "single"` is rendered
- **Then** it shows "Single: {case-name}" label; entries with `scope: "bulk"` or `undefined` show "Full Run"

**Test Cases**:
1. **Unit**: component render test for history panel
   - `testHistoryEntryLabelForSingleScope()`: Renders "Single: case-name" for scope="single"
   - `testHistoryEntryLabelForBulkScope()`: Renders "Full Run" for scope="bulk" and undefined
   - **Coverage Target**: 80%

**Implementation**:
1. In the history panel component: check `entry.scope === "single"` to set label
2. Single-scope label: `"Single: ${entry.cases[0]?.name ?? entry.cases[0]?.id}"`
3. Bulk/undefined label: `"Full Run"`



## User Story: US-005 - Cancel All Running Cases

**Linked ACs**: AC-US5-01, AC-US5-02, AC-US5-03
**Tasks**: 1 total, 1 completed



### T-011: Implement `cancelAll()` — abort all running/queued cases and release semaphore slots

**User Story**: US-005
**Satisfies ACs**: AC-US5-01, AC-US5-02, AC-US5-03
**Status**: [x] completed

**Test Plan**:
- **Given** 4 cases — 2 in "running" state and 2 in "queued" state
- **When** `cancelAll()` is called
- **Then** all 4 cases transition to "cancelled", `bulkRunActive` becomes false, and server semaphore slots are released for the aborted requests (via `res.on('close')` safety net)

**Test Cases**:
1. **Unit**: `repositories/anton-abyzov/vskill/src/eval-ui/src/pages/workspace/workspaceReducer.test.ts`
   - `testCancelAllSetsRunningCasesToCancelled()`: Running cases → cancelled
   - `testCancelAllSetsQueuedCasesToCancelled()`: Queued cases → cancelled
   - `testCancelAllSetsBulkRunActiveFalse()`: `bulkRunActive` becomes false
   - `testCancelAllPreservesIdleAndCompleteCases()`: Idle/complete cases untouched
   - **Coverage Target**: 90%

2. **Unit**: `repositories/anton-abyzov/vskill/src/eval-ui/src/sse.test.ts`
   - `testStopAllAbortsAllActiveControllers()`: All active AbortControllers are aborted
   - **Coverage Target**: 90%

**Implementation**:
1. In `workspaceReducer.ts`: add `CANCEL_ALL` handler (set running/queued → cancelled, `bulkRunActive=false`)
2. In `WorkspaceContext.tsx`: `cancelAll()` calls `multiSSE.stopAll()`, dispatches `CANCEL_ALL`
3. Server: `res.on('close')` with double-release guard ensures semaphore slots freed for disconnected requests (AC-US5-03)
4. "Cancel All" button in RunPanel visible when `bulkRunActive || isAnyRunning(state)`



## User Story: US-006 - Independent UI State Per Case

**Linked ACs**: AC-US6-01, AC-US6-02, AC-US6-03, AC-US6-04, AC-US6-05
**Tasks**: 3 total, 3 completed



### T-012: Replace `isRunning` with `caseRunStates` map in workspace types and initial state

**User Story**: US-006
**Satisfies ACs**: AC-US6-01, AC-US6-04
**Status**: [x] completed

**Test Plan**:
- **Given** the `WorkspaceState` type definition
- **When** the type is checked
- **Then** `isRunning: boolean` and `runScope` are absent; `caseRunStates: Map<number, CaseRunState>` and `bulkRunActive: boolean` are present

**Test Cases**:
1. **Unit**: `repositories/anton-abyzov/vskill/src/eval-ui/src/pages/workspace/workspaceTypes.test.ts`
   - `testCaseRunStatusValues()`: All 6 status values compile — idle, queued, running, complete, error, cancelled
   - `testWorkspaceStateHasCaseRunStatesMap()`: Initial state has caseRunStates Map and bulkRunActive=false
   - **Coverage Target**: 80%

**Implementation**:
1. In `workspaceTypes.ts`:
   - Add `CaseRunStatus = "idle" | "queued" | "running" | "complete" | "error" | "cancelled"`
   - Add `CaseRunState { status: CaseRunStatus; startedAt?: number }`
   - Remove `isRunning: boolean` and `runScope: RunScope | null` from `WorkspaceState`
   - Add `caseRunStates: Map<number, CaseRunState>` and `bulkRunActive: boolean`
2. Add new action union types: `CASE_RUN_START`, `CASE_RUN_COMPLETE`, `CASE_RUN_ERROR`, `CASE_RUN_CANCEL`, `BULK_RUN_START`, `BULK_RUN_COMPLETE`, `CANCEL_ALL`
3. Update initial state in reducer: `caseRunStates: new Map()`, `bulkRunActive: false`



### T-013: Update WorkspaceContext API — replace `runBenchmark`/`cancelRun` with per-case functions

**User Story**: US-006
**Satisfies ACs**: AC-US6-02, AC-US6-03, AC-US6-05
**Status**: [x] completed

**Test Plan**:
- **Given** the `WorkspaceContextValue` interface
- **When** inspected
- **Then** `runBenchmark` and `cancelRun` are absent; `runCase`, `runAll`, `cancelCase`, and `cancelAll` are present

**Test Cases**:
1. **Unit**: `repositories/anton-abyzov/vskill/src/eval-ui/src/pages/workspace/WorkspaceContext.test.tsx`
   - `testRunCaseDispatchesCaseRunStart()`: `runCase(1)` dispatches CASE_RUN_START for evalId=1
   - `testCancelCaseDispatchesCaseRunCancel()`: `cancelCase(1)` stops stream and dispatches CASE_RUN_CANCEL
   - `testRunAllDispatchesBulkRunStart()`: `runAll()` dispatches BULK_RUN_START with all evalIds
   - `testCancelAllDispatchesCancelAll()`: `cancelAll()` stops all streams and dispatches CANCEL_ALL
   - **Coverage Target**: 85%

**Implementation**:
1. In `WorkspaceContext.tsx`: replace `useSSE` with `useMultiSSE` for benchmark runs
2. Implement `runCase(evalId, mode?)`: dispatch CASE_RUN_START, call `multiSSE.startCase`
3. Implement `runAll(mode?)`: dispatch BULK_RUN_START, call `multiSSE.startCase` for each evalId
4. Implement `cancelCase(evalId)`: call `multiSSE.stopCase`, dispatch CASE_RUN_CANCEL
5. Implement `cancelAll()`: call `multiSSE.stopAll`, dispatch CANCEL_ALL
6. Update `applyImproveAndRerun` to call `runCase(evalId)` instead of `runBenchmark(...)`
7. Keep `useSSE` for comparison mode and activation testing



### T-014: Update RunPanel and TestsPanel to use per-case state; add per-case Run/Cancel controls

**User Story**: US-006
**Satisfies ACs**: AC-US6-01, AC-US6-03, AC-US6-04, AC-US6-05, AC-US1-01, AC-US1-02, AC-US2-04
**Status**: [x] completed

**Test Plan**:
- **Given** case A is running and case B is complete in `caseRunStates`
- **When** the RunPanel renders
- **Then** case A shows a spinner and a Cancel button; case B shows its result, an enabled Run button, and no Cancel button; the UI is not blocked

**Test Cases**:
1. **Unit**: component tests for `RunPanel` and `TestsPanel`
   - `testRunCaseCardShowsSpinnerWhenRunning()`: Status "running" renders spinner icon
   - `testRunCaseCardShowsClockWhenQueued()`: Status "queued" renders clock/queue icon
   - `testRunCaseCardRunButtonDisabledWhenRunning()`: Run button disabled for running case
   - `testRunCaseCardRunButtonEnabledWhenComplete()`: Run button enabled for complete case
   - `testRunCaseCardCancelButtonVisibleOnlyWhenRunning()`: Cancel button shown only for running state
   - `testCancelAllButtonVisibleWhenBulkActive()`: Cancel All shown when `bulkRunActive` true
   - **Coverage Target**: 85%

**Implementation**:
1. In `RunPanel.tsx`:
   - Replace `isRunning` checks with `caseRunStates.get(evalId)?.status` lookups
   - "Run All" button calls `runAll()`
   - "Cancel All" button visible when `bulkRunActive || isAnyRunning(state)`
   - Remove scope selector (all/selected) — replaced by per-case Run buttons and Run All
   - Per-case status icons: spinner (running), clock (queued), checkmark (complete), X (error), dash (cancelled)
   - Bulk progress bar: `(running count + complete count) / total`
2. In `TestsPanel.tsx`:
   - `CaseDetail`: per-case Cancel button visible only when that case is running
   - Run/A/B buttons disabled only when that specific case is running
   - Status pills update from per-case SSE events independently
