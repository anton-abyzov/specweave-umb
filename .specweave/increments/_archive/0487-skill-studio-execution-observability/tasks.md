---
increment: 0487-skill-studio-execution-observability
title: "Skill Studio Execution Observability"
generated_by: test-aware-planner
coverage_target: 90
by_user_story:
  US-001: [T-001, T-002, T-003]
  US-002: [T-004, T-005, T-006, T-007]
  US-003: [T-008, T-009]
  US-004: [T-010, T-011]
  US-005: [T-012, T-013, T-014]
---

# Tasks: Skill Studio Execution Observability

## User Story: US-001 - SSE Streaming for AI Operations

**Linked ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05
**Tasks**: 3 total, all completed

---

### T-001: Make withHeartbeat evalId optional in sse-helpers.ts

**User Story**: US-001
**Satisfies ACs**: AC-US1-04, AC-US1-05
**Status**: [x] completed

**Test Plan**:
- **Given** `withHeartbeat` is called without an `evalId` argument
- **When** the wrapped async function executes and 3 seconds pass
- **Then** a heartbeat progress SSE event is emitted with `{ phase, message, elapsed_ms }` shape and no evalId-related errors

**Test Cases**:
1. **Unit**: `src/eval-server/__tests__/sse-helpers.test.ts`
   - `withHeartbeatNoEvalId()`: Call withHeartbeat(res, undefined, "generating", "Calling LLM", fn) and verify SSE progress event emitted on timer
   - `withHeartbeatProgressShape()`: Verify emitted event contains phase, message, elapsed_ms fields
   - `withHeartbeatClearsTimer()`: Verify setInterval is cleared after wrapped fn resolves
   - **Coverage Target**: 90%

**Implementation**:
1. Open `src/eval-server/sse-helpers.ts`
2. Change `evalId: number` parameter in `withHeartbeat` signature to `evalId?: number` with default `0`
3. Verify the function body still works (evalId is likely only used for logging or not used in heartbeat payload)
4. Run existing sse-helpers tests to confirm no regression

---

### T-002: Create error-classifier.ts with all 7 error categories

**User Story**: US-001
**Satisfies ACs**: AC-US3-01, AC-US3-05
**Status**: [x] completed

**Test Plan**:
- **Given** an error is thrown during an LLM call (HTTP status error, CLI stderr text, or parse failure)
- **When** `classifyError(err, provider)` is called
- **Then** it returns a `ClassifiedError` with the correct category, title, description, hint, and optional `retryAfterMs`

**Test Cases**:
1. **Unit**: `src/eval-server/__tests__/error-classifier.test.ts`
   - `classifiesAnthropicRateLimit()`: Pass fake 429 HTTP error, expect `{ category: "rate_limit" }`
   - `classifiesAnthropicContextWindow()`: Pass fake 413/context error, expect `{ category: "context_window" }`
   - `classifiesAnthropicAuth()`: Pass 401 error, expect `{ category: "auth" }`
   - `classifiesAnthropicProviderUnavailable()`: Pass 503 error, expect `{ category: "provider_unavailable" }`
   - `classifiesCliRateLimit()`: Pass stderr "rate limit exceeded", expect `{ category: "rate_limit" }`
   - `classifiesCliContextWindow()`: Pass stderr "context window exceeded", expect `{ category: "context_window" }`
   - `classifiesCliTimeout()`: Pass stderr "timed out", expect `{ category: "timeout" }`
   - `classifiesCliProviderNotFound()`: Pass stderr "ENOENT", expect `{ category: "provider_unavailable" }`
   - `classifiesParseError()`: Pass JSON.parse SyntaxError, expect `{ category: "parse_error" }`
   - `classifiesUnknown()`: Pass generic Error, expect `{ category: "unknown" }`
   - `includesRetryAfterMs()`: Pass 429 error with retry-after header value, expect retryAfterMs populated
   - `handlesEmptyStderr()`: Pass empty string stderr, expect `{ category: "unknown" }`
   - **Coverage Target**: 95%

**Implementation**:
1. Create `src/eval-server/error-classifier.ts`
2. Export `ClassifiedError` interface with fields: `category`, `title`, `description`, `hint`, `retryAfterMs?`
3. Export `classifyError(err: unknown, provider: string): ClassifiedError`
4. Implement Anthropic HTTP status code checks (429, 401/403, 413, 503)
5. Implement CLI stderr regex pattern matching per error-classification matrix in plan.md
6. Implement JSON parse failure detection
7. Default to `"unknown"` category for unmatched errors

---

### T-003: Convert improve-routes.ts, api-routes.ts, skill-create-routes.ts to SSE

**User Story**: US-001
**Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05
**Status**: [x] completed

**Test Plan**:
- **Given** a POST request is made to `/api/skills/:plugin/:skill/improve` (or generate-evals or generate-skill)
- **When** the endpoint begins processing
- **Then** the response has `Content-Type: text/event-stream`, emits progress events for "preparing", "generating", and "parsing" phases in order, and ends with a `done` event containing the result payload

**Test Cases**:
1. **Integration**: `src/eval-server/__tests__/improve-routes.test.ts`
   - `improveEmitsSSEHeader()`: Verify response Content-Type is text/event-stream
   - `improveEmitsThreePhases()`: Capture SSE events, verify preparing -> generating -> parsing order
   - `improveDoneEventHasPayload()`: Verify done event contains { original, improved, reasoning }
   - `improveEmitsErrorEventOnFailure()`: Mock LLM to throw, verify error event with ClassifiedError shape
   - `instructModeEmitsSSE()`: Same as above for mode=instruct
2. **Integration**: `src/eval-server/__tests__/api-routes-evals.test.ts`
   - `generateEvalsEmitsSSEHeader()`: Verify SSE response
   - `generateEvalsEmitsThreePhases()`: Verify phase sequence
   - `generateEvalsDoneHasPayload()`: Verify done event has evals data
3. **Integration**: `src/eval-server/__tests__/skill-create-routes.test.ts`
   - `generateSkillEmitsSSEHeader()`: Verify SSE response
   - `generateSkillEmitsThreePhases()`: Verify phase sequence
   - `generateSkillDoneHasPayload()`: Verify done event has parsed skill data
   - **Coverage Target**: 85%

**Implementation**:
1. Modify `src/eval-server/improve-routes.ts`:
   - Replace `sendJson(res, ...)` with `initSSE(res, req)` at entry
   - Add `sendSSE(res, "progress", { phase: "preparing", message: "Building prompt...", elapsed_ms: 0 })`
   - Wrap `client.generate()` call with `withHeartbeat(res, undefined, "generating", "Calling LLM", async () => ...)`
   - Add `sendSSE(res, "progress", { phase: "parsing", message: "Extracting result...", elapsed_ms: N })`
   - Replace `sendJson` result with `sendSSEDone(res, { original, improved, reasoning })`
   - Add catch block: `classifyError(err, provider)` then `sendSSE(res, "error", classified)` then `res.end()`
   - Apply same pattern for both auto and instruct modes
2. Modify `src/eval-server/api-routes.ts` for generate-evals endpoint with same pattern
3. Modify `src/eval-server/skill-create-routes.ts` for generate-skill endpoint with same pattern

---

## User Story: US-002 - Progress UI for AI Operations

**Linked ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04, AC-US2-05
**Tasks**: 4 total, all completed

---

### T-004: Make ProgressLog component work without evalId

**User Story**: US-002
**Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04
**Status**: [x] completed

**Test Plan**:
- **Given** a ProgressLog is rendered with entries that have no `evalId`
- **When** phase transitions occur with "preparing", "generating", and "parsing" phases
- **Then** the correct phase icons are displayed and elapsed time is shown without errors

**Test Cases**:
1. **Component**: `src/eval-ui/src/components/__tests__/ProgressLog.test.tsx`
   - `rendersWithoutEvalId()`: Render with entry `{ phase: "preparing", message: "Building prompt...", elapsed_ms: 0 }` and verify no crash
   - `showsPreparingIcon()`: Verify icon for "preparing" phase renders
   - `showsParsingIcon()`: Verify icon for "parsing" phase renders
   - `showsElapsedTime()`: Verify elapsed_ms is displayed in human-readable form
   - `rendersMultiplePhases()`: Render preparing -> generating -> parsing sequence
   - **Coverage Target**: 90%

**Implementation**:
1. Open `src/eval-ui/src/components/ProgressLog.tsx`
2. Change `evalId: number` in `ProgressEntry` interface to `evalId?: number`
3. Add `"preparing"` and `"parsing"` to the `phaseIcon` function (or equivalent icon-selection logic)
4. Verify display logic does not reference `evalId` for rendering (it should be display-only)
5. Run component tests

---

### T-005: Add ProgressLog and Cancel to AiEditBar

**User Story**: US-002
**Satisfies ACs**: AC-US2-01, AC-US4-01, AC-US4-02, AC-US4-03
**Status**: [x] completed

**Test Plan**:
- **Given** AI Edit is submitted in AiEditBar
- **When** SSE progress events arrive
- **Then** ProgressLog appears below the input showing phase transitions and elapsed time, and the Submit button changes to "Cancel"

**Test Cases**:
1. **Component**: `src/eval-ui/src/components/__tests__/AiEditBar.test.tsx`
   - `showsProgressLogDuringGeneration()`: Mock useSSE running=true, verify ProgressLog renders
   - `showsCancelButtonDuringGeneration()`: Verify Submit changes to Cancel when running=true
   - `hidesProgressLogAfterSuccess()`: When done=true, verify ProgressLog collapses
   - `escapeCancelsGeneration()`: Fire Escape keydown, verify stop() called on useSSE
   - `preservesInstructionTextOnCancel()`: Verify input value unchanged after cancel
   - **Coverage Target**: 85%

**Implementation**:
1. Open `src/eval-ui/src/components/AiEditBar.tsx`
2. Store instruction text in state before starting SSE: `const [instruction, setInstruction] = useState("")`
3. Wire `useSSE` for the AI Edit call (replacing or wrapping the existing fetch)
4. Add `progressEntries` state, populate from SSE progress events
5. Render `<ProgressLog entries={progressEntries} />` below input when `running === true`
6. Change Submit button to "Cancel" (or show cancel affordance) when `running === true`
7. Add `onKeyDown` Escape handler that calls `sseControls.stop()`
8. On cancel: reset `running`, keep instruction text, hide ProgressLog

---

### T-006: Add ProgressLog to SkillImprovePanel

**User Story**: US-002
**Satisfies ACs**: AC-US2-02, AC-US2-05
**Status**: [x] completed

**Test Plan**:
- **Given** Auto-Improve is triggered in SkillImprovePanel
- **When** the improvement is running
- **Then** a ProgressLog appears showing progress phases and elapsed time, and collapses when done

**Test Cases**:
1. **Component**: `src/eval-ui/src/components/__tests__/SkillImprovePanel.test.tsx`
   - `showsProgressLogDuringImprovement()`: Mock useSSE running=true, verify ProgressLog renders
   - `hidesProgressLogOnSuccess()`: When done=true and result available, verify ProgressLog gone
   - `showsErrorCardOnFailure()`: When SSE error event received, verify ErrorCard renders
   - **Coverage Target**: 85%

**Implementation**:
1. Open `src/eval-ui/src/components/SkillImprovePanel.tsx`
2. Add local state: `progressEntries`, wire `useSSE` for the improve call
3. Accumulate progress events into `progressEntries`
4. Render `<ProgressLog entries={progressEntries} />` when running
5. On SSE done event: extract result, hide ProgressLog, show result as before
6. On SSE error event: set `classifiedError` state, render `<ErrorCard error={classifiedError} />`

---

### T-007: Add ProgressLog to TestsPanel (generate-evals) and CreateSkillPage (generate-skill)

**User Story**: US-002
**Satisfies ACs**: AC-US2-03, AC-US2-04, AC-US2-05
**Status**: [x] completed

**Test Plan**:
- **Given** Generate Evals or Generate Skill is triggered
- **When** generation is in progress
- **Then** ProgressLog appears showing phases, and collapses with result on completion

**Test Cases**:
1. **Component**: `src/eval-ui/src/pages/workspace/__tests__/TestsPanel.test.tsx`
   - `showsProgressLogDuringEvalGeneration()`: Mock SSE running=true, verify ProgressLog
   - `showsGeneratedEvalsOnDone()`: When done event fires, verify evals rendered
2. **Component**: `src/eval-ui/src/pages/__tests__/CreateSkillPage.test.tsx`
   - `showsProgressLogDuringSkillGeneration()`: Mock SSE running=true, verify ProgressLog
   - `showsSkillDataOnDone()`: When done event fires, verify skill data rendered
   - **Coverage Target**: 85%

**Implementation**:
1. Open `src/eval-ui/src/pages/workspace/TestsPanel.tsx`
   - Add `progressEntries` state, wire `useSSE` for generate-evals
   - Render `<ProgressLog>` when running, extract evals from done event
2. Open `src/eval-ui/src/pages/CreateSkillPage.tsx`
   - Add `progressEntries` state, wire `useSSE` for generate-skill
   - Render `<ProgressLog>` when running, extract skill data from done event

---

## User Story: US-003 - Error Classification and Structured Error Cards

**Linked ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04, AC-US3-05
**Tasks**: 2 total, all completed

---

### T-008: Create ErrorCard component

**User Story**: US-003
**Satisfies ACs**: AC-US3-02, AC-US3-03, AC-US3-04
**Status**: [x] completed

**Test Plan**:
- **Given** a `ClassifiedError` is passed to `ErrorCard`
- **When** rendered for different categories
- **Then** the correct icon, title, description, hint, and Retry button are shown; for `rate_limit` with `retryAfterMs`, a countdown timer is displayed

**Test Cases**:
1. **Component**: `src/eval-ui/src/components/__tests__/ErrorCard.test.tsx`
   - `rendersRateLimitCategory()`: Pass `{ category: "rate_limit", ... }`, verify "Rate Limit" title shown
   - `rendersContextWindowHint()`: Pass `{ category: "context_window", ... }`, verify context window hint text
   - `rendersRetryButton()`: Verify Retry button present for all categories
   - `showsCountdownForRateLimit()`: Pass `{ category: "rate_limit", retryAfterMs: 30000 }`, verify countdown renders
   - `countdownDecrementsOverTime()`: Use fake timers, verify countdown decrements each second
   - `rendersAuthCategory()`: Verify auth error shows API key hint
   - `rendersUnknownCategory()`: Verify unknown error shows generic hint
   - **Coverage Target**: 90%

**Implementation**:
1. Create `src/eval-ui/src/components/ErrorCard.tsx`
2. Accept `error: ClassifiedError` and `onRetry: () => void` props
3. Map category to icon (use existing icon set or emoji fallback)
4. Render title, description, hint text
5. For `rate_limit` with `retryAfterMs`: add `useState(retryAfterSeconds)` + `setInterval` countdown, disable Retry button until countdown reaches 0
6. Render Retry button calling `onRetry`
7. Add `ClassifiedError` type to `src/eval-ui/src/types.ts`

---

### T-009: Wire ErrorCard into all AI operation components

**User Story**: US-003
**Satisfies ACs**: AC-US3-01, AC-US3-04, AC-US3-05
**Status**: [x] completed

**Test Plan**:
- **Given** any AI operation returns an SSE error event with a `ClassifiedError` payload
- **When** the frontend receives the error event
- **Then** `ErrorCard` replaces the plain red error box in AiEditBar, SkillImprovePanel, TestsPanel, and CreateSkillPage

**Test Cases**:
1. **Integration**: `src/eval-ui/src/components/__tests__/AiEditBar.test.tsx`
   - `showsErrorCardOnSSEError()`: Emit error SSE event, verify ErrorCard renders (not plain red box)
2. **Integration**: `src/eval-ui/src/components/__tests__/SkillImprovePanel.test.tsx`
   - `showsErrorCardOnSSEError()`: Same pattern for SkillImprovePanel
   - **Coverage Target**: 85%

**Implementation**:
1. Add `ClassifiedError` interface to `src/eval-ui/src/types.ts` mirroring server definition
2. In AiEditBar: add `classifiedError` state, populate on SSE `error` event, render `<ErrorCard error={classifiedError} onRetry={handleRetry} />`
3. In SkillImprovePanel: same ErrorCard wiring
4. In TestsPanel: same ErrorCard wiring
5. In CreateSkillPage: same ErrorCard wiring
6. Remove old plain red error `<div>` in each component

---

## User Story: US-004 - Abort/Cancel Support for AI Edit

**Linked ACs**: AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-04
**Tasks**: 2 total, all completed

---

### T-010: Implement Escape key abort and server-side close detection in AI Edit

**User Story**: US-004
**Satisfies ACs**: AC-US4-01, AC-US4-02, AC-US4-03
**Status**: [x] completed

**Test Plan**:
- **Given** an AI Edit SSE stream is in progress
- **When** the user presses Escape
- **Then** `useSSE.stop()` is called which aborts the fetch via AbortController, and the UI returns to the instruction input with text preserved

**Test Cases**:
1. **Component**: `src/eval-ui/src/components/__tests__/AiEditBar.test.tsx`
   - `escapeAbortsSSEStream()`: Simulate Escape keydown while running=true, verify stop() invoked
   - `instructionPreservedAfterAbort()`: After abort, verify input still shows original instruction
   - `cancelButtonTriggersStop()`: Click Cancel button, verify stop() invoked
2. **Integration**: `src/eval-server/__tests__/improve-routes.test.ts`
   - `serverDetectsClientClose()`: Close response mid-stream, verify heartbeat interval cleared (no dangling intervals)
   - **Coverage Target**: 85%

**Implementation**:
1. In AiEditBar: store instruction in `useState` before calling `sseControls.start()`
2. Add `useEffect` with `keydown` listener: if `event.key === "Escape" && running` call `sseControls.stop()`
3. Show "Cancel" button text when `running === true`, revert to "Submit" when not running
4. After abort: `running` becomes false via useSSE, ProgressLog hides, input field keeps value
5. In `improve-routes.ts`: add `res.on("close", ...)` flag so withHeartbeat stops on close (verify withHeartbeat already handles this via its finally block)

---

### T-011: Handle unexpected SSE connection drops

**User Story**: US-004
**Satisfies ACs**: AC-US4-04
**Status**: [x] completed

**Test Plan**:
- **Given** an AI Edit SSE stream is in progress
- **When** the network drops unexpectedly (not a user abort)
- **Then** the frontend shows a "Connection lost" error state with a Retry button, without auto-retry

**Test Cases**:
1. **Component**: `src/eval-ui/src/components/__tests__/AiEditBar.test.tsx`
   - `showsConnectionLostOnNetworkError()`: Simulate fetch rejection (not AbortError), verify "Connection lost" message shown
   - `connectionLostHasRetryButton()`: Verify Retry button present in connection-lost state
   - `noAutoRetryOnConnectionLost()`: Verify `start()` is not automatically called again after drop
   - **Coverage Target**: 85%

**Implementation**:
1. In AiEditBar: distinguish between `AbortError` (user cancel) and other fetch errors (network drop)
2. The `useSSE` hook likely surfaces fetch errors in its `error` state -- check if it distinguishes AbortError
3. If not an AbortError and `running` just became false: set a local `connectionLost` state
4. Render "Connection lost. Check your connection." message with Retry button when `connectionLost === true`
5. Retry button calls `sseControls.start()` again with same args and resets `connectionLost`

---

## User Story: US-005 - API Client Migration to SSE

**Linked ACs**: AC-US5-01, AC-US5-02, AC-US5-03, AC-US5-04, AC-US5-05
**Tasks**: 3 total, all completed

---

### T-012: Wire WorkspaceContext to use useSSE for AI Edit and generate-evals

**User Story**: US-005
**Satisfies ACs**: AC-US5-01, AC-US5-02, AC-US5-03
**Status**: [x] completed

**Test Plan**:
- **Given** `improveSkill` or `instructEdit` is triggered from WorkspaceContext
- **When** SSE events arrive
- **Then** progress events dispatch to reducer as `AI_EDIT_PROGRESS` actions and the done event dispatches `AI_EDIT_DONE` with the result payload

**Test Cases**:
1. **Integration**: `src/eval-ui/src/pages/workspace/__tests__/WorkspaceContext.test.tsx`
   - `dispatchesProgressOnSSEEvent()`: Simulate SSE progress event, verify AI_EDIT_PROGRESS dispatched
   - `dispatchesDoneWithPayload()`: Simulate SSE done event, verify AI_EDIT_DONE with { original, improved } dispatched
   - `dispatchesErrorOnSSEError()`: Simulate SSE error event, verify reducer gets ClassifiedError
   - `generateEvalsDispatchesProgress()`: Same pattern for generate-evals flow
   - **Coverage Target**: 85%

**Implementation**:
1. Open `src/eval-ui/src/pages/workspace/WorkspaceContext.tsx`
2. Replace `api.improveSkill()` / `api.instructEdit()` fetch calls with `useSSE.start()` calls
3. In the SSE event handler: dispatch `AI_EDIT_PROGRESS` for progress events, `AI_EDIT_DONE` for done event, `AI_EDIT_ERROR` for error events
4. For generate-evals: replace `api.generateEvals()` with `useSSE.start()` and dispatch `GENERATE_EVALS_*` actions
5. Update `workspaceTypes.ts` with new state fields: `aiEditProgress: ProgressEntry[]`, `generateEvalsProgress: ProgressEntry[]`, `generateEvalsError: ClassifiedError | null`
6. Update `workspaceReducer.ts` to handle new actions

---

### T-013: Update workspaceTypes.ts and workspaceReducer.ts for progress state

**User Story**: US-005
**Satisfies ACs**: AC-US5-01, AC-US5-03
**Status**: [x] completed

**Test Plan**:
- **Given** the workspace reducer receives AI_EDIT_PROGRESS and GENERATE_EVALS_PROGRESS actions
- **When** these actions are dispatched
- **Then** the respective progress arrays in state are updated correctly

**Test Cases**:
1. **Unit**: `src/eval-ui/src/pages/workspace/__tests__/workspaceReducer.test.ts`
   - `appendsAiEditProgressEntry()`: Dispatch AI_EDIT_PROGRESS, verify aiEditProgress array grows
   - `clearsAiEditProgressOnStart()`: Dispatch AI_EDIT_START, verify aiEditProgress resets to []
   - `appendsGenerateEvalsProgressEntry()`: Dispatch GENERATE_EVALS_PROGRESS, verify array grows
   - `setsGenerateEvalsError()`: Dispatch GENERATE_EVALS_ERROR with ClassifiedError, verify state
   - `clearsGenerateEvalsError()`: Dispatch GENERATE_EVALS_START, verify error resets to null
   - **Coverage Target**: 90%

**Implementation**:
1. Open `src/eval-ui/src/pages/workspace/workspaceTypes.ts`
2. Add to `WorkspaceState`:
   - `aiEditProgress: ProgressEntry[]`
   - `generateEvalsLoading: boolean`
   - `generateEvalsProgress: ProgressEntry[]`
   - `generateEvalsError: ClassifiedError | null`
3. Add new action types: `AI_EDIT_START`, `AI_EDIT_PROGRESS`, `AI_EDIT_DONE`, `AI_EDIT_ERROR`, `GENERATE_EVALS_START`, `GENERATE_EVALS_PROGRESS`, `GENERATE_EVALS_DONE`, `GENERATE_EVALS_ERROR`
4. Open `src/eval-ui/src/pages/workspace/workspaceReducer.ts`
5. Handle each new action: append entries, reset arrays, set/clear errors

---

### T-014: Wire CreateSkillPage and SkillImprovePanel to SSE (generate-skill and auto-improve)

**User Story**: US-005
**Satisfies ACs**: AC-US5-04, AC-US5-05
**Status**: [x] completed

**Test Plan**:
- **Given** Generate Skill or Auto-Improve is triggered
- **When** SSE streams from the converted endpoints
- **Then** progress events populate the ProgressLog, the done event delivers the result, and error events render ErrorCard

**Test Cases**:
1. **Component**: `src/eval-ui/src/pages/__tests__/CreateSkillPage.test.tsx`
   - `generateSkillUsesSSE()`: Verify useSSE.start() called (not api.generateSkill fetch)
   - `extractsSkillFromDoneEvent()`: Simulate done event, verify skill data rendered
   - `showsErrorCardOnSSEError()`: Simulate error event, verify ErrorCard renders
2. **Component**: `src/eval-ui/src/components/__tests__/SkillImprovePanel.test.tsx`
   - `autoImproveUsesSSE()`: Verify useSSE.start() called for auto-improve
   - `extractsImprovedContentFromDone()`: Simulate done event, verify diff shows improved content
   - **Coverage Target**: 85%

**Implementation**:
1. Open `src/eval-ui/src/pages/CreateSkillPage.tsx`
   - Replace `api.generateSkill()` call with `useSSE.start(url, body)`
   - Handle progress events into local `progressEntries` state
   - On done event: extract generated skill data, show result
   - On error event: set `classifiedError`, render `<ErrorCard>`
2. Open `src/eval-ui/src/components/SkillImprovePanel.tsx`
   - Replace existing improve API call with `useSSE.start(url, body)`
   - Handle progress, done, and error events
   - Show `<ProgressLog>` and `<ErrorCard>` as appropriate
