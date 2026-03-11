---
increment: 0495-comparison-progress-observability
title: "Comparison Progress Observability"
status: active
by_user_story:
  US-001: [T-001, T-002]
  US-002: [T-003, T-004]
  US-003: [T-005, T-006]
  US-004: [T-007]
  US-005: [T-008]
---

# Tasks: Comparison Progress Observability

## User Story: US-001 - Dynamic Heartbeat SSE Helper

**Linked ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04
**Tasks**: 2 total, all completed

---

### T-001: Implement `startDynamicHeartbeat()` in sse-helpers.ts

**User Story**: US-001
**Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03
**Status**: [x] completed

**Test Plan**:
- **Given** an `http.ServerResponse` mock and a call to `startDynamicHeartbeat(res, 100)`
- **When** the returned handle is inspected and timers are advanced
- **Then** it exposes `update()` and `stop()` methods, emits the initial tick immediately, emits updated payload after `update()`, and emits no further events after `stop()`

**Test Cases**:
1. **Unit**: `src/eval-server/__tests__/sse-helpers.test.ts`
   - `startDynamicHeartbeat_returnsHandle()`: verify returned object has `update` and `stop` functions
   - `startDynamicHeartbeat_firstTickImmediate()`: spy on `res.write`, call start, assert write called with initial phase/message before any interval fires
   - `startDynamicHeartbeat_updateChangesPayload()`: call `update({ phase: "generating_baseline", message: "..." })`, advance fake timers, assert next tick SSE contains new phase
   - `startDynamicHeartbeat_stopClearsTimer()`: call `stop()`, advance fake timers, assert `res.write` not called again
   - `startDynamicHeartbeat_stopIsIdempotent()`: call `stop()` twice, verify no error thrown
   - `startDynamicHeartbeat_elapsedMsIncremented()`: advance timers by 2 intervals, assert `elapsed_ms` grows on each tick
   - **Coverage Target**: 95%

**Implementation**:
1. Add `DynamicHeartbeat` interface (`update(data)` and `stop()`) to `src/eval-server/sse-helpers.ts`
2. Implement `startDynamicHeartbeat(res, intervalMs = 3000)`:
   - Store mutable `currentData` ref initialized with `generating_skill` default
   - Record `startedAt = Date.now()` for elapsed tracking
   - Fire first tick immediately via `sendSSE`
   - Start `setInterval` emitting `currentData + elapsed_ms` on each tick
   - `update(data)` replaces `currentData`
   - `stop()` calls `clearInterval` guarded by nullish check (idempotent)
3. Export `startDynamicHeartbeat` from the module
4. Run `npx vitest run src/eval-server/__tests__/sse-helpers.test.ts`

---

### T-002: Verify `withHeartbeat()` remains unchanged (regression guard)

**User Story**: US-001
**Satisfies ACs**: AC-US1-04
**Status**: [x] completed

**Test Plan**:
- **Given** a module import of `sse-helpers.ts` after `startDynamicHeartbeat` is added
- **When** `withHeartbeat` is imported and called with a mock response and a fast-resolving async fn
- **Then** it emits heartbeat events and resolves its promise, identical to pre-increment behavior

**Test Cases**:
1. **Unit**: `src/eval-server/__tests__/sse-helpers.test.ts` (add to existing suite)
   - `withHeartbeat_stillAvailableAfterRefactor()`: import both exports, run `withHeartbeat` with resolving async fn, assert SSE events emitted and promise resolves
   - **Coverage Target**: 90%

**Implementation**:
1. Check for any existing `withHeartbeat` tests in the test file
2. Add regression test confirming named export exists and behaves correctly
3. No changes to `withHeartbeat` implementation -- test confirms it is untouched
4. Run `npx vitest run src/eval-server/__tests__/sse-helpers.test.ts`

---

## User Story: US-002 - Progress Callback in Comparator

**Linked ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04
**Tasks**: 2 total, all completed

---

### T-003: Add `onProgress` callback to `generateComparisonOutputs()` and `runComparison()`

**User Story**: US-002
**Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03
**Status**: [x] completed

**Test Plan**:
- **Given** a mock `LlmClient` that resolves instantly and an `onProgress` spy function
- **When** `runComparison(prompt, skillContent, client, onProgress)` is awaited
- **Then** `onProgress` fires exactly 3 times in order: `generating_skill`, `generating_baseline`, `scoring`

**Test Cases**:
1. **Unit**: `src/eval/__tests__/comparator.test.ts` (add to existing suite)
   - `generateComparisonOutputs_firesGeneratingSkillBeforeLLMCall1()`: assert `onProgress("generating_skill", ...)` fires before first `client.generate` call
   - `generateComparisonOutputs_firesGeneratingBaselineBeforeLLMCall2()`: assert `onProgress("generating_baseline", ...)` fires before second `client.generate` call
   - `runComparison_firesScoringBeforeScoreComparison()`: assert `onProgress("scoring", ...)` fires before rubric scoring call
   - `runComparison_callbackFiredInOrder()`: verify full sequence `generating_skill` -> `generating_baseline` -> `scoring`
   - **Coverage Target**: 92%

**Implementation**:
1. Add `type ProgressCallback = (phase: string, message: string) => void` to `src/eval/comparator.ts`
2. Add optional `onProgress?: ProgressCallback` as 4th param to `generateComparisonOutputs()`
3. Fire `onProgress?.("generating_skill", "Generating skill output...")` before first `client.generate` call
4. Fire `onProgress?.("generating_baseline", "Generating baseline output...")` before second `client.generate` call
5. Add optional `onProgress?: ProgressCallback` as 4th param to `runComparison()`
6. Thread it to `generateComparisonOutputs()` and fire `onProgress?.("scoring", "Scoring responses...")` before `scoreComparison()`
7. Wrap each `onProgress` call in try/catch to prevent callback errors from killing the comparison
8. Run `npx vitest run src/eval/__tests__/comparator.test.ts`

---

### T-004: Verify no regression when `onProgress` is omitted

**User Story**: US-002
**Satisfies ACs**: AC-US2-04
**Status**: [x] completed

**Test Plan**:
- **Given** a call to `runComparison()` with no `onProgress` argument
- **When** all 3 LLM call boundaries are crossed
- **Then** it completes without error and returns a valid `ComparisonResult`

**Test Cases**:
1. **Unit**: `src/eval/__tests__/comparator.test.ts` (add to existing suite)
   - `runComparison_noCallbackNoError()`: call without 4th param, assert resolves to a valid result
   - `runComparison_existingTestsStillPass()`: confirm all pre-existing comparator test cases remain green
   - **Coverage Target**: 90%

**Implementation**:
1. Confirm optional-chaining `onProgress?.()` is used (no `if (onProgress)` guard blocks)
2. Run full comparator test suite: `npx vitest run src/eval/__tests__/comparator.test.ts`

---

## User Story: US-003 - Wire Dynamic Heartbeat in Compare Endpoint

**Linked ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04, AC-US3-05
**Tasks**: 2 total, all completed

---

### T-005: Replace `withHeartbeat()` with `startDynamicHeartbeat()` in compare endpoint

**User Story**: US-003
**Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04
**Status**: [x] completed

**Test Plan**:
- **Given** a mock `LlmClient` and mock `res` (ServerResponse), and the compare endpoint handler
- **When** a comparison is triggered for one eval case
- **Then** the SSE stream contains progress events with phases `generating_skill`, `generating_baseline`, `scoring`; and `stop()` is called in both success and error paths

**Test Cases**:
1. **Integration**: `src/eval-server/__tests__/compare-endpoint.test.ts` (new file)
   - `compareEndpoint_emitsGeneratingSkillPhase()`: assert SSE output includes `"generating_skill"` phase event
   - `compareEndpoint_emitsGeneratingBaselinePhase()`: assert SSE output includes `"generating_baseline"` phase event
   - `compareEndpoint_emitsScoringPhase()`: assert SSE output includes `"scoring"` phase event
   - `compareEndpoint_stopCalledOnSuccess()`: mock `startDynamicHeartbeat`, assert `stop()` called after `runComparison` resolves
   - `compareEndpoint_stopCalledOnError()`: make `runComparison` reject, assert `stop()` still called in finally
   - **Coverage Target**: 88%

**Implementation**:
1. In `src/eval-server/api-routes.ts`, locate the compare endpoint handler loop
2. Import `startDynamicHeartbeat` from `./sse-helpers.js`
3. Replace `withHeartbeat(res, async () => { ... })` with:
   - `const heartbeat = startDynamicHeartbeat(res)` before `runComparison`
   - `onProgress` callback: `(phase, message) => heartbeat.update({ phase, message, eval_id })`
   - `try { await runComparison(prompt, skill, client, onProgress) } finally { heartbeat.stop() }`
4. Remove any initial manual `sendSSE(res, "progress", { phase: "comparing", ... })` if present
5. Run `npx vitest run src/eval-server/__tests__/compare-endpoint.test.ts`

---

### T-006: Verify heartbeat ticks use latest phase between transitions

**User Story**: US-003
**Satisfies ACs**: AC-US3-05
**Status**: [x] completed

**Test Plan**:
- **Given** a running `startDynamicHeartbeat` with initial `phase: "generating_skill"`
- **When** `update({ phase: "generating_baseline", ... })` is called and a timer tick fires
- **Then** the emitted SSE event contains `"generating_baseline"` not the stale `"generating_skill"`

**Test Cases**:
1. **Unit**: `src/eval-server/__tests__/sse-helpers.test.ts`
   - `startDynamicHeartbeat_tickUsesLatestPhaseAfterUpdate()`: call `update` then advance fake timers, assert emitted payload contains the updated phase
   - **Coverage Target**: 95% (shared with T-001 test file)

**Implementation**:
1. Confirm T-001 implementation stores `currentData` as a mutable ref (not closed-over at start time)
2. Add explicit named test case if not already covered by T-001 suite
3. Run `npx vitest run src/eval-server/__tests__/sse-helpers.test.ts`

---

## User Story: US-004 - ProgressLog Phase Support

**Linked ACs**: AC-US4-01, AC-US4-02
**Tasks**: 1 total, all completed

---

### T-007: Add comparison phases to ProgressLog spinnerPhases and accentPhases Sets

**User Story**: US-004
**Satisfies ACs**: AC-US4-01, AC-US4-02
**Status**: [x] completed

**Test Plan**:
- **Given** `ProgressLog` rendered with entries for `generating_skill`, `generating_baseline`, and `scoring`
- **When** one entry is the latest and `isRunning` is true
- **Then** the active entry renders a spinner icon; completed entries render the accent-color dot (not green dot)

**Test Cases**:
1. **Component**: `src/eval-ui/src/components/__tests__/ProgressLog.test.tsx` (add to or create)
   - `progressLog_generatingSkillShowsSpinnerWhenLatestAndRunning()`: render with `generating_skill` as latest and `isRunning=true`, assert spinner present
   - `progressLog_generatingBaselineShowsSpinnerWhenLatest()`: same for `generating_baseline`
   - `progressLog_scoringShowsSpinnerWhenLatest()`: same for `scoring`
   - `progressLog_completedComparisonPhaseShowsAccentDot()`: render `generating_skill` as completed entry (not latest), assert accent-color dot (not green dot, not spinner)
   - `progressLog_unknownPhaseStillRendersGreenDot()`: render entry with phase `"other"`, assert green dot rendered (regression guard)
   - **Coverage Target**: 90%

**Implementation**:
1. Open `src/eval-ui/src/components/ProgressLog.tsx`
2. Find `spinnerPhases` Set, add: `"generating_skill"`, `"generating_baseline"`, `"scoring"`
3. Find `accentPhases` Set, add: `"generating_skill"`, `"generating_baseline"`, `"scoring"`
4. Run component tests: `npx vitest run src/eval-ui/src/components/__tests__/ProgressLog.test.tsx`

---

## User Story: US-005 - ProgressLog on ComparisonPage

**Linked ACs**: AC-US5-01, AC-US5-02, AC-US5-03
**Tasks**: 1 total, all completed

---

### T-008: Render ProgressLog in ComparisonPage using SSE progress events

**User Story**: US-005
**Satisfies ACs**: AC-US5-01, AC-US5-02, AC-US5-03
**Status**: [x] completed

**Test Plan**:
- **Given** `ComparisonPage` with a mocked `useSSE` hook that emits progress events
- **When** events arrive with phases `generating_skill`, `generating_baseline`, `scoring`
- **Then** `ProgressLog` renders with all 3 accumulated entries; when `running` becomes false the active spinner stops; a new `eval_id` causes fresh phase entries to appear

**Test Cases**:
1. **Component**: `src/eval-ui/src/pages/__tests__/ComparisonPage.test.tsx` (new file)
   - `comparisonPage_rendersProgressLogDuringRun()`: mock progress events, assert `ProgressLog` in DOM with entries for each phase
   - `comparisonPage_progressLogStopsSpinnerOnCompletion()`: set `running=false` after events, assert no active spinner
   - `comparisonPage_newEvalIdAppendsEntries()`: emit progress events for `eval_id=1` then `eval_id=2`, assert both entry sets visible
   - **Coverage Target**: 88%

**Implementation**:
1. Open `src/eval-ui/src/pages/ComparisonPage.tsx`
2. Import `ProgressLog` from `../components/ProgressLog` and `ProgressEntry` type from `../types`
3. Add `progressEntries` state (array of `ProgressEntry`, initialized to `[]`)
4. In the SSE event processing loop where `type === "progress"`, push event data into `progressEntries`
5. Render `<ProgressLog entries={progressEntries} isRunning={running} />` below the start controls, following the same pattern as `BenchmarkPage.tsx`
6. Run `npx vitest run src/eval-ui/src/pages/__tests__/ComparisonPage.test.tsx`
