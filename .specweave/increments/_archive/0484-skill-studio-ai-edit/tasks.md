---
increment: 0484-skill-studio-ai-edit
title: "Skill Studio AI Edit Feature"
status: active
by_user_story:
  US-001:
    - T-001
    - T-002
    - T-003
  US-002:
    - T-004
    - T-005
    - T-006
    - T-007
---

# Tasks: Skill Studio AI Edit Feature

## User Story: US-001 - Freeform AI Edit via Inline Prompt Bar

**Linked ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05
**Tasks**: 3 total, 3 completed

---

### T-001: Extend backend /improve endpoint with instruct mode

**User Story**: US-001
**Satisfies ACs**: AC-US1-04
**Status**: [x] completed

**Test Plan**:
- **Given** a POST to `/api/skills/:plugin/:skill/improve` with `mode: "instruct"`, a non-empty `instruction`, and `content`
- **When** the handler processes the request
- **Then** it uses the instruct-focused system prompt (no benchmark context), records history with `type: "instruct"`, and returns `{ original, improved, reasoning }`

**Test Cases**:
1. **Unit**: `src/eval-server/__tests__/improve-routes.test.ts`
   - `instructMode_usesInstructPromptNotBenchmarkContext()`: Spy on `createLlmClient`, verify the system prompt passed does NOT contain "benchmark" text and DOES contain the instruction
   - `instructMode_validatesNonEmptyInstruction()`: POST with empty instruction returns 400
   - `instructMode_recordsHistoryWithTypeInstruct()`: Spy on `writeHistoryEntry`, verify `type: "instruct"` is recorded
   - `instructMode_returnsOriginalImprovedReasoning()`: Mock LLM response with `---REASONING---` separator, verify parsed response shape
   - `defaultMode_unchanged_whenNoModeParam()`: POST without `mode` field still runs existing benchmark flow (no regression)
   - **Coverage Target**: 90%

**Implementation**:
1. In `src/eval-server/improve-routes.ts`, extend request body type to include `mode?: "instruct"`, `instruction?: string`, `content?: string`
2. After body parsing, branch on `body.mode === "instruct"`:
   - Validate `body.instruction` is a non-empty string (400 if missing/empty)
   - Validate `body.content` is a non-empty string (400 if missing)
   - Use instruct-focused system prompt (from plan.md Backend section)
   - Build user prompt: `Instruction: {instruction}\n\n## SKILL.md content\n{content}`
   - Set `original = body.content` (not disk file read)
   - Call `createLlmClient`, parse `---REASONING---`, record history with `type: "instruct"`
   - Return `{ original, improved, reasoning }`
3. Existing `mode` omitted path falls through unchanged
4. Run tests: `npx vitest run src/eval-server/__tests__/improve-routes.test.ts`

---

### T-002: Extend workspace state and reducer with AI edit actions

**User Story**: US-001
**Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-05
**Status**: [x] completed

**Test Plan**:
- **Given** the workspace reducer receives AI edit actions
- **When** each action is dispatched
- **Then** the state transitions match the documented state design precisely

**Test Cases**:
1. **Unit**: `src/eval-ui/src/pages/workspace/__tests__/workspaceReducer.test.ts`
   - `OPEN_AI_EDIT_setsAiEditOpenAndClearsErrorAndResult()`: Dispatch `OPEN_AI_EDIT`, verify `aiEditOpen=true`, `aiEditError=null`, `aiEditResult=null`
   - `CLOSE_AI_EDIT_resetsAllAiEditState()`: Start with loading/result state, dispatch `CLOSE_AI_EDIT`, verify all four fields reset
   - `AI_EDIT_LOADING_disablesSubmitAndClearsError()`: Dispatch `AI_EDIT_LOADING`, verify `aiEditLoading=true`, `aiEditError=null`
   - `AI_EDIT_RESULT_setsResultAndClearsLoading()`: Dispatch `AI_EDIT_RESULT` with `{improved, reasoning}`, verify `aiEditLoading=false`, `aiEditResult` set
   - `AI_EDIT_ERROR_setsErrorAndClearsLoading()`: Dispatch `AI_EDIT_ERROR` with message, verify `aiEditLoading=false`, `aiEditError` set
   - **Coverage Target**: 95%

**Implementation**:
1. In `src/eval-ui/src/pages/workspace/workspaceTypes.ts`:
   - Add 4 fields to `WorkspaceState`: `aiEditOpen: boolean`, `aiEditLoading: boolean`, `aiEditResult: { improved: string; reasoning: string } | null`, `aiEditError: string | null`
   - Add 5 action types to `WorkspaceAction` union: `OPEN_AI_EDIT`, `CLOSE_AI_EDIT`, `AI_EDIT_LOADING`, `AI_EDIT_RESULT` (payload: `{ improved: string; reasoning: string }`), `AI_EDIT_ERROR` (payload: `{ message: string }`)
   - Add `submitAiEdit: (instruction: string) => Promise<void>` to `WorkspaceContextValue`
2. In `src/eval-ui/src/pages/workspace/workspaceReducer.ts`:
   - Add initial values to `initialWorkspaceState`: `aiEditOpen: false`, `aiEditLoading: false`, `aiEditResult: null`, `aiEditError: null`
   - Add 5 reducer cases matching the state transitions from plan.md State Design section
3. Run tests: `npx vitest run src/eval-ui/src/pages/workspace/__tests__/workspaceReducer.test.ts`

---

### T-003: Add instructEdit API method and submitAiEdit context action

**User Story**: US-001
**Satisfies ACs**: AC-US1-04, AC-US1-05
**Status**: [x] completed

**Test Plan**:
- **Given** the `submitAiEdit` context action is called with an instruction string
- **When** the API succeeds or fails
- **Then** the correct actions are dispatched in sequence (loading -> result OR loading -> error)

**Test Cases**:
1. **Unit**: `src/eval-ui/src/pages/workspace/__tests__/WorkspaceContext.test.tsx`
   - `submitAiEdit_dispatches_LOADING_then_RESULT_on_success()`: Mock `api.instructEdit` to resolve, call `submitAiEdit("add error handling")`, verify dispatch sequence: `AI_EDIT_LOADING` then `AI_EDIT_RESULT`
   - `submitAiEdit_dispatches_LOADING_then_ERROR_on_failure()`: Mock `api.instructEdit` to reject, verify dispatch sequence: `AI_EDIT_LOADING` then `AI_EDIT_ERROR`
   - `submitAiEdit_uses_skillContent_not_savedContent()`: Mock with controlled state where `skillContent !== savedContent`, verify `api.instructEdit` receives `skillContent`
   - **Coverage Target**: 90%
2. **Unit**: `src/eval-ui/src/__tests__/api.test.ts`
   - `instructEdit_posts_to_improve_endpoint_with_mode_instruct()`: Spy on `fetch`, call `api.instructEdit(...)`, verify URL and body shape

**Implementation**:
1. In `src/eval-ui/src/api.ts`:
   - Add `instructEdit(plugin: string, skill: string, opts: { instruction: string; content: string; provider?: string; model?: string }): Promise<ImproveResult>` method that POSTs to `/api/skills/${plugin}/${skill}/improve` with `{ mode: "instruct", ...opts }`
2. In `src/eval-ui/src/pages/workspace/WorkspaceContext.tsx`:
   - Add `submitAiEdit` async callback using `useCallback`:
     - Dispatch `AI_EDIT_LOADING`
     - Call `api.instructEdit(state.plugin, state.skill, { instruction, content: state.skillContent })`
     - On success: dispatch `AI_EDIT_RESULT` with `{ improved, reasoning }`
     - On failure: dispatch `AI_EDIT_ERROR` with `{ message: err.message }`
   - Include `submitAiEdit` in context value
3. Run tests: `npx vitest run src/eval-ui/src/pages/workspace/__tests__/WorkspaceContext.test.tsx`

---

## User Story: US-002 - Diff Review and Apply/Discard for AI Edits

**Linked ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04, AC-US2-05
**Tasks**: 4 total, 4 completed

---

### T-004: Create AiEditBar component

**User Story**: US-002
**Satisfies ACs**: AC-US1-01, AC-US1-03, AC-US1-05, AC-US2-05
**Status**: [x] completed

**Test Plan**:
- **Given** the AiEditBar component is rendered
- **When** user interacts with the textarea and buttons
- **Then** the correct callbacks are invoked and visual states reflect the loading/error props

**Test Cases**:
1. **Unit**: `src/eval-ui/src/components/__tests__/AiEditBar.test.tsx`
   - `AiEditBar_rendersTextareaAndSubmitButton()`: Render with `loading=false`, verify textarea and submit button present
   - `AiEditBar_autoFocusesTextareaOnMount()`: Verify textarea receives focus on mount
   - `AiEditBar_callsOnSubmit_whenEnterPressedInTextarea()`: Type instruction, press Enter, verify `onSubmit` called with instruction text
   - `AiEditBar_callsOnSubmit_whenSubmitButtonClicked()`: Type instruction, click button, verify `onSubmit` called
   - `AiEditBar_callsOnDismiss_whenEscapePressed()`: Press Escape in textarea, verify `onDismiss` called
   - `AiEditBar_disablesSubmitAndShowsSpinner_whenLoading()`: Render with `loading=true`, verify button disabled and spinner visible
   - `AiEditBar_displaysErrorMessage_whenErrorPropSet()`: Render with `error="Network error"`, verify error text displayed
   - `AiEditBar_doesNotSubmit_whenInstructionIsEmpty()`: Press Enter with empty textarea, verify `onSubmit` NOT called
   - **Coverage Target**: 95%

**Implementation**:
1. Create `src/eval-ui/src/components/AiEditBar.tsx`:
   - Props: `onSubmit: (instruction: string) => void`, `onDismiss: () => void`, `loading: boolean`, `error: string | null`
   - Local state: `instruction` string for textarea value
   - `useRef` + `useEffect` to call `ref.current?.focus()` on mount
   - `onKeyDown` handler on textarea: Enter (non-shift) calls `onSubmit(instruction.trim())` if non-empty; Escape calls `onDismiss()`
   - Submit button: `disabled={loading || !instruction.trim()}`, shows spinner icon when `loading=true`
   - Error display: renders error text below textarea when `error` prop is set
   - Approximately 80-100 lines
2. Run tests: `npx vitest run src/eval-ui/src/components/__tests__/AiEditBar.test.tsx`

---

### T-005: Integrate AiEditBar and Cmd/Ctrl+K shortcut into EditorPanel toolbar

**User Story**: US-002
**Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03
**Status**: [x] completed

**Test Plan**:
- **Given** the EditorPanel is rendered with workspace state
- **When** the user clicks the AI Edit toolbar button or presses Cmd/Ctrl+K
- **Then** `OPEN_AI_EDIT` is dispatched, and AiEditBar renders when `aiEditOpen=true`

**Test Cases**:
1. **Unit**: `src/eval-ui/src/pages/workspace/__tests__/EditorPanel.test.tsx`
   - `EditorPanel_showsAiEditToolbarButton()`: Render EditorPanel, verify AI Edit button (sparkle icon) present in toolbar
   - `EditorPanel_dispatchesOPEN_AI_EDIT_onToolbarButtonClick()`: Click AI Edit button, verify dispatch called with `{ type: "OPEN_AI_EDIT" }`
   - `EditorPanel_dispatchesOPEN_AI_EDIT_onCmdK()`: Simulate Cmd+K keydown on EditorPanel div, verify dispatch called with `{ type: "OPEN_AI_EDIT" }`
   - `EditorPanel_dispatchesOPEN_AI_EDIT_onCtrlK()`: Simulate Ctrl+K keydown, verify dispatch called
   - `EditorPanel_rendersAiEditBar_whenAiEditOpenTrue()`: Set `state.aiEditOpen=true`, render EditorPanel, verify AiEditBar in DOM
   - `EditorPanel_doesNotRenderAiEditBar_whenAiEditOpenFalse()`: Default state, verify AiEditBar not rendered
   - `EditorPanel_dispatchesCLOSE_AI_EDIT_whenAiEditBarDismissed()`: AiEditBar visible, call `onDismiss`, verify `CLOSE_AI_EDIT` dispatched
   - **Coverage Target**: 90%

**Implementation**:
1. In `src/eval-ui/src/pages/workspace/EditorPanel.tsx`:
   - Import `AiEditBar` from `../../components/AiEditBar`
   - Add AI Edit button to toolbar (sparkle/wand icon, dispatches `{ type: "OPEN_AI_EDIT" }`)
   - Register `onKeyDown` handler on the EditorPanel wrapper div: detect `(e.metaKey || e.ctrlKey) && e.key === "k"`, call `e.preventDefault()`, dispatch `OPEN_AI_EDIT` only when `!state.aiEditOpen`
   - Conditionally render `<AiEditBar>` below the editor textarea when `state.aiEditOpen === true`, wiring `onDismiss` to dispatch `CLOSE_AI_EDIT` and `onSubmit` to call `submitAiEdit` from context
   - Pass `loading={state.aiEditLoading}` and `error={state.aiEditError}` to AiEditBar
2. Run tests: `npx vitest run src/eval-ui/src/pages/workspace/__tests__/EditorPanel.test.tsx`

---

### T-006: Render AI edit diff panel with Apply/Discard in EditorPanel

**User Story**: US-002
**Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04
**Status**: [x] completed

**Test Plan**:
- **Given** `state.aiEditResult` is set with `{ improved, reasoning }`
- **When** the diff panel renders
- **Then** a reasoning box and unified diff with color-coded lines appear; Apply updates content and saves; Discard resets state

**Test Cases**:
1. **Unit**: `src/eval-ui/src/pages/workspace/__tests__/EditorPanel.test.tsx` (extended)
   - `EditorPanel_rendersReasoningBox_whenAiEditResultSet()`: Set `state.aiEditResult = { improved: "...", reasoning: "Added error handling" }`, verify reasoning text appears
   - `EditorPanel_rendersDiffLines_whenAiEditResultSet()`: Set result with content differing from `skillContent`, verify added/removed line indicators present
   - `EditorPanel_applyButton_dispatchesSET_CONTENT_andCallsApplyImprovement()`: Click Apply, verify `SET_CONTENT` dispatched with `improved`, `api.applyImprovement` called, then `CONTENT_SAVED` and `CLOSE_AI_EDIT` dispatched
   - `EditorPanel_discardButton_dispatchesCLOSE_AI_EDIT()`: Click Discard, verify `CLOSE_AI_EDIT` dispatched, `skillContent` unchanged
   - `EditorPanel_doesNotRenderDiffPanel_whenAiEditResultNull()`: Default state, verify diff panel not in DOM
   - **Coverage Target**: 90%

**Implementation**:
1. In `src/eval-ui/src/pages/workspace/EditorPanel.tsx`:
   - Import `computeDiff` from `../../utils/diff`
   - When `state.aiEditResult` is non-null, render a diff panel section below the AiEditBar area:
     - Reasoning box: displays `state.aiEditResult.reasoning`
     - Diff: calls `computeDiff(state.skillContent, state.aiEditResult.improved)`, renders each diff line with color coding (green for additions, red for removals, gray for context)
     - Apply button: dispatches `SET_CONTENT` with improved content, calls `api.applyImprovement(state.plugin, state.skill, improved)`, dispatches `CONTENT_SAVED`, dispatches `CLOSE_AI_EDIT`
     - Discard button: dispatches `CLOSE_AI_EDIT`
2. Run tests: `npx vitest run src/eval-ui/src/pages/workspace/__tests__/EditorPanel.test.tsx`

---

### T-007: Integration test - full AI edit flow end-to-end

**User Story**: US-002
**Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05, AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04, AC-US2-05
**Status**: [x] completed

**Test Plan**:
- **Given** the SkillWorkspace is rendered with a WorkspaceContext provider and mocked API
- **When** the user opens the prompt bar, types an instruction, submits, and applies or discards
- **Then** the full state transitions fire in order and the final state is correct for both happy path and error path

**Test Cases**:
1. **Integration**: `src/eval-ui/src/pages/workspace/__tests__/AiEditFlow.integration.test.tsx`
   - `aiEditFlow_openBarViaButton_typeInstruction_submit_seeDiff_apply()`:
     1. Render SkillWorkspace with mocked context
     2. Click AI Edit button -> verify AiEditBar visible
     3. Type "add error handling" in textarea, press Enter
     4. Mock `api.instructEdit` resolves with `{ original, improved, reasoning }`
     5. Verify diff panel appears with reasoning text
     6. Click Apply -> verify `api.applyImprovement` called, diff panel gone, content updated
   - `aiEditFlow_openBarViaCmdK_escape_dismisses()`:
     1. Simulate Cmd+K -> verify bar visible
     2. Press Escape -> verify bar dismissed, no API call made
   - `aiEditFlow_apiError_displaysErrorInBar()`:
     1. Open bar, type instruction, submit
     2. Mock `api.instructEdit` rejects with "Network error"
     3. Verify error message visible in bar, no diff panel shown
   - `aiEditFlow_discard_resetsDiffPanel()`:
     1. Complete happy path to diff panel
     2. Click Discard -> verify diff panel gone, `skillContent` unchanged
   - `aiEditFlow_noRegression_improveFlowStillWorks()`:
     1. Open SkillImprovePanel via existing path, verify it works normally alongside new AI edit state
   - **Coverage Target**: 85%

**Implementation**:
1. Create `src/eval-ui/src/pages/workspace/__tests__/AiEditFlow.integration.test.tsx`
2. Use React Testing Library to render the full component tree with a real reducer and mocked API
3. Mock `api` module at the test level using `vi.mock` with `vi.hoisted()`
4. Test both keyboard and click interaction paths
5. Run tests: `npx vitest run src/eval-ui/src/pages/workspace/__tests__/AiEditFlow.integration.test.tsx`
