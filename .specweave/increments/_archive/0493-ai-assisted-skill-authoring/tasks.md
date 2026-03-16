---
increment: 0493-ai-assisted-skill-authoring
generated_by: sw:test-aware-planner
test_mode: TDD
coverage_target: 90
total_tasks: 13
completed_tasks: 13
---

# Tasks: AI-Assisted Skill Authoring in Skill Studio

**Test file**: `src/eval-ui/src/components/__tests__/CreateSkillInline.test.tsx`
**Component**: `src/eval-ui/src/components/CreateSkillInline.tsx`

---

## User Story: US-001 - AI Mode Toggle

**Linked ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04
**Tasks**: 3 total, 3 completed

### T-001: Remove passive banner and creatorStatus code

**User Story**: US-001
**Satisfies ACs**: AC-US1-04
**Status**: [x] completed

**Test Plan**:
- **Given** the CreateSkillInline component renders
- **When** the DOM is queried for "Run /skill-creator" or "AI-Assisted Authoring Available"
- **Then** no such text is present in the rendered output

**Test Cases**:
1. **Unit**: `src/eval-ui/src/components/__tests__/CreateSkillInline.test.tsx`
   - `bannerRemoved_noSkillCreatorText()`: Render component, assert `queryByText(/skill-creator/i)` returns null
   - `bannerRemoved_noPassiveBannerText()`: Assert `queryByText(/AI-Assisted Authoring Available/i)` returns null
   - **Coverage Target**: 95%

**Implementation**:
1. Remove `creatorStatus` state and its `useState` declaration
2. Remove `api.getSkillCreatorStatus()` call from `useEffect`
3. Remove `showCreatorBanner` computed value
4. Remove the `{showCreatorBanner && (...)}` JSX block (lines 114-136)
5. Remove `SkillCreatorStatus` from the types import
6. Run tests: confirm no regressions

---

### T-002: Add new state, refs, and imports for AI mode

**User Story**: US-001
**Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03
**Status**: [x] completed

**Test Plan**:
- **Given** the component file is updated with new imports and state
- **When** TypeScript compilation runs
- **Then** no type errors; all new state variables are correctly typed

**Test Cases**:
1. **Unit**: `src/eval-ui/src/components/__tests__/CreateSkillInline.test.tsx`
   - `stateInit_modeIsManualByDefault()`: Render component, assert manual mode UI is visible and AI prompt section is absent
   - **Coverage Target**: 90%

**Implementation**:
1. Update React import: add `useRef`, `useCallback`
2. Add type imports: `GeneratedEval` (from `../types`), `ProgressLog` + `ProgressEntry` (from `./ProgressLog`), `ErrorCard` + `ClassifiedError` (from `./ErrorCard`)
3. Add inline `SparkleIcon` SVG component (4-line, local to file)
4. Remove `SkillCreatorStatus` import, add `GeneratedEval` import
5. Add new state declarations after existing ones:
   - `mode: "manual" | "ai"` (default `"manual"`)
   - `aiPrompt: string` (default `""`)
   - `generating: boolean` (default `false`)
   - `aiReasoning: string | null` (default `null`)
   - `aiError: string | null` (default `null`)
   - `aiClassifiedError: ClassifiedError | null` (default `null`)
   - `aiProgress: ProgressEntry[]` (default `[]`)
   - `pendingEvals: GeneratedEval[] | null` (default `null`)
6. Add refs: `promptRef`, `abortRef`
7. Run `tsc --noEmit`

---

### T-003: Render Manual/AI toggle in header

**User Story**: US-001
**Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03
**Status**: [x] completed

**Test Plan**:
- **Given** the component renders
- **When** the toggle is inspected
- **Then** "Manual" and "AI-Assisted" buttons are visible with Manual active by default
- **When** "AI-Assisted" is clicked
- **Then** the AI prompt section appears and the manual form fields are hidden
- **When** "Manual" is clicked
- **Then** the manual form fields reappear and the AI section is hidden

**Test Cases**:
1. **Unit**: `src/eval-ui/src/components/__tests__/CreateSkillInline.test.tsx`
   - `toggle_defaultIsManual()`: Assert "Manual" button has active styling; "AI-Assisted" does not
   - `toggle_clickAiShowsPromptSection()`: Click "AI-Assisted" → assert textarea with generate placeholder is visible, manual form fields absent
   - `toggle_clickManualRestoresForm()`: Switch to AI then back to Manual → assert manual form fields visible
   - **Coverage Target**: 95%

**Implementation**:
1. Replace the `<p>Define your skill's...</p>` subtitle with the mode toggle in the header:
   - Two buttons: "Manual" and "AI-Assisted" (with SparkleIcon)
   - Active button uses purple accent `#a855f7` background; inactive uses `var(--surface-3)`
2. Wrap existing `{layoutLoading ? ... : layout ? ...}` in `{mode === "manual" && (...)}`
3. Add `{mode === "ai" && (...)}` placeholder section (content filled in T-005)
4. Auto-focus `promptRef` when switching to AI mode (via `useEffect` on `mode`)
5. Run tests: T-003 test cases must pass

---

## User Story: US-002 - AI Prompt and Generation

**Linked ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04, AC-US2-05
**Tasks**: 3 total, 3 completed

### T-004: Write failing tests for AI prompt section and SSE generation

**User Story**: US-002
**Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04, AC-US2-05
**Status**: [x] completed

**Test Plan**:
- **Given** the test file is created with mocked fetch and api
- **When** the tests run before implementation
- **Then** all tests in this task fail (RED phase of TDD)

**Test Cases**:
1. **Unit**: `src/eval-ui/src/components/__tests__/CreateSkillInline.test.tsx`
   - `aiMode_showsTextareaAndGenerateButton()`: Switch to AI mode → assert textarea and "Generate Skill" button present (AC-US2-01)
   - `aiMode_generateButtonDisabledWhenEmpty()`: Assert generate button has `disabled` attribute / not-allowed cursor with empty prompt (AC-US2-02)
   - `aiMode_callsFetchWithPromptOnGenerate()`: Type prompt, click generate → assert `fetch` called with `/api/skills/generate?sse` and correct body (AC-US2-03)
   - `aiMode_populatesFormOnDoneEvent()`: Mock fetch returning SSE `done` event → assert form fields populated, mode switches to manual (AC-US2-04)
   - `aiMode_storesPendingEvalsFromDoneEvent()`: Mock SSE done with evals → assert pendingEvals stored and passed to `api.createSkill` on create (AC-US2-05)
   - **Coverage Target**: 90%

**Implementation**:
1. Create `src/eval-ui/src/components/__tests__/CreateSkillInline.test.tsx`
2. Set up `vi.hoisted()` for ESM-compatible mocks
3. Mock `../api` with `vi.mock()`: stub `getProjectLayout`, `getConfig`, `createSkill`
4. Mock global `fetch` for SSE tests with a helper that returns a `ReadableStream` of encoded SSE lines
5. Write all test cases listed above (they fail until T-005 is implemented)
6. Run `npx vitest run` and confirm RED

---

### T-005: Implement AI prompt section JSX and handleGenerate

**User Story**: US-002
**Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04, AC-US2-05
**Status**: [x] completed

**Test Plan**:
- **Given** the AI prompt section is rendered and fetch is mocked
- **When** the user types a prompt and clicks "Generate Skill"
- **Then** fetch is called with SSE endpoint; on done event form fields populate and mode switches to manual

**Test Cases**:
1. Same test cases as T-004 — they must now pass (GREEN phase)
   - **Coverage Target**: 90%

**Implementation**:
1. Add `{mode === "ai" && (...)}` JSX block containing:
   - `<textarea>` bound to `aiPrompt` with placeholder "Describe what your skill should do..."
   - "Generate Skill" button (disabled when `aiPrompt.trim() === ""` or `generating`)
   - "Cancel Generation" button shown when `generating` (wired in T-008)
2. Implement `handleGenerate()`:
   - Validate: empty prompt → set `aiError`, return (no fetch)
   - Create `AbortController`, store in `abortRef`
   - Set `generating = true`, clear `aiError`, `aiProgress`, `aiClassifiedError`
   - `fetch("/api/skills/generate?sse", { method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify({ prompt: aiPrompt, provider, model }), signal })`
   - Read `ReadableStream` with `TextDecoder`; parse SSE lines (`event:` / `data:`)
   - On `progress` event: append to `aiProgress`
   - On `done` / `complete` event: populate name, description, model, allowedTools, body, aiReasoning, pendingEvals; switch `mode` to `"manual"`
   - On `error` event: set `aiClassifiedError` (if `category` present) or `aiError`
   - On `AbortError`: reset `generating`
3. Add `useEffect` cleanup: `return () => abortRef.current?.abort()` on unmount
4. Run tests: T-004 test cases must now pass

---

### T-006: Modify handleCreate to pass pendingEvals

**User Story**: US-002
**Satisfies ACs**: AC-US2-05
**Status**: [x] completed

**Test Plan**:
- **Given** AI generation completed and stored pendingEvals
- **When** the user clicks "Create Skill"
- **Then** `api.createSkill` is called with the evals field included

**Test Cases**:
1. **Unit**: `src/eval-ui/src/components/__tests__/CreateSkillInline.test.tsx`
   - `handleCreate_includesPendingEvalsWhenPresent()`: Set pendingEvals, fill required fields, click Create → assert `api.createSkill` called with `evals` matching stored pendingEvals
   - `handleCreate_noEvalsWhenManualOnly()`: Create skill without AI generation → assert `api.createSkill` called without `evals` key (or with `undefined`)
   - **Coverage Target**: 90%

**Implementation**:
1. Update `handleCreate()`: add `evals: pendingEvals ?? undefined` to the `api.createSkill()` call
2. Run tests: T-006 test cases must pass
3. Run full suite: `npx vitest run`

---

## User Story: US-003 - Loading State and Progress

**Linked ACs**: AC-US3-01, AC-US3-02, AC-US3-03
**Tasks**: 2 total, 2 completed

### T-007: Write failing tests for loading state and progress display

**User Story**: US-003
**Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03
**Status**: [x] completed

**Test Plan**:
- **Given** tests are written before the cancel button and ProgressLog are rendered
- **When** tests run
- **Then** they fail (RED phase)

**Test Cases**:
1. **Unit**: `src/eval-ui/src/components/__tests__/CreateSkillInline.test.tsx`
   - `generating_showsCancelButton()`: Mock never-resolving fetch, click generate → assert "Cancel Generation" button visible and textarea disabled (AC-US3-01)
   - `generating_showsProgressLog()`: Mock fetch emitting progress events → assert `ProgressLog` rendered with messages (AC-US3-02)
   - `cancel_abortsStreamAndResetsUI()`: Click cancel → assert `AbortController.abort()` called; generating resets to false, textarea re-enabled (AC-US3-03)
   - **Coverage Target**: 90%

**Implementation**:
1. Add these test cases to the existing test file
2. Run `npx vitest run` and confirm RED for new tests

---

### T-008: Render Cancel button and ProgressLog during generation

**User Story**: US-003
**Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03
**Status**: [x] completed

**Test Plan**:
- **Given** generation is in progress
- **When** the AI prompt section renders
- **Then** "Cancel Generation" button appears, textarea is disabled, and ProgressLog shows progress messages

**Test Cases**:
1. Same test cases as T-007 — they must now pass (GREEN phase)
   - **Coverage Target**: 90%

**Implementation**:
1. Inside the `{mode === "ai"}` section:
   - Show "Cancel Generation" button (replaces "Generate Skill") when `generating === true`
   - Disable `<textarea>` when `generating`
   - Render `{generating && <ProgressLog entries={aiProgress} />}` below textarea
2. Implement `handleCancelGenerate()`: call `abortRef.current?.abort()`, set `generating = false`
3. Wire "Cancel Generation" `onClick` to `handleCancelGenerate`
4. Run tests: T-007 test cases must now pass

---

## User Story: US-004 - AI Reasoning Display

**Linked ACs**: AC-US4-01, AC-US4-02
**Tasks**: 2 total, 2 completed

### T-009: Write failing tests for reasoning banner

**User Story**: US-004
**Satisfies ACs**: AC-US4-01, AC-US4-02
**Status**: [x] completed

**Test Plan**:
- **Given** tests are written before the reasoning banner is rendered
- **When** tests run
- **Then** they fail (RED phase)

**Test Cases**:
1. **Unit**: `src/eval-ui/src/components/__tests__/CreateSkillInline.test.tsx`
   - `reasoning_bannerVisibleAfterGeneration()`: Mock SSE done with reasoning text → after generation, assert reasoning banner visible with reasoning text in manual mode (AC-US4-01)
   - `reasoning_showsEvalCount()`: Mock SSE done with 3 evals → assert banner shows "3 evals" badge (AC-US4-01)
   - `reasoning_dismissClearsEvals()`: Click dismiss (X) button → assert banner gone and pendingEvals cleared (AC-US4-02)
   - **Coverage Target**: 90%

**Implementation**:
1. Add these test cases to the existing test file
2. Run `npx vitest run` and confirm RED for new tests

---

### T-010: Render collapsible reasoning banner in manual mode

**User Story**: US-004
**Satisfies ACs**: AC-US4-01, AC-US4-02
**Status**: [x] completed

**Test Plan**:
- **Given** AI generation completed with reasoning and evals
- **When** manual mode form is shown
- **Then** reasoning banner appears at top; dismiss button clears it and pendingEvals

**Test Cases**:
1. Same test cases as T-009 — they must now pass (GREEN phase)
   - **Coverage Target**: 90%

**Implementation**:
1. Add `{mode === "manual" && aiReasoning && (...)}` reasoning banner block at the top of the manual mode section, before the LocationCard:
   - Purple-accented card with SparkleIcon and reasoning text
   - Eval count badge: `{pendingEvals?.length} pending evals`
   - Dismiss (X) button that calls: `setAiReasoning(null); setPendingEvals(null)`
2. Run tests: T-009 test cases must now pass
3. Run `npx vitest run`

---

## User Story: US-005 - Error Handling with Retry

**Linked ACs**: AC-US5-01, AC-US5-02, AC-US5-03, AC-US5-04
**Tasks**: 2 total, 2 completed

### T-011: Write failing tests for error scenarios

**User Story**: US-005
**Satisfies ACs**: AC-US5-01, AC-US5-02, AC-US5-03, AC-US5-04
**Status**: [x] completed

**Test Plan**:
- **Given** tests are written before error display and retry are implemented
- **When** tests run
- **Then** they fail (RED phase)

**Test Cases**:
1. **Unit**: `src/eval-ui/src/components/__tests__/CreateSkillInline.test.tsx`
   - `error_classifiedErrorShowsErrorCard()`: Mock SSE error event with `category` → assert `ErrorCard` renders with error details and "Retry" button (AC-US5-01)
   - `error_unclassifiedErrorShowsInlineMessage()`: Mock fetch rejection → assert inline error div visible (AC-US5-02)
   - `error_retryReattemptsGeneration()`: Click "Retry" after error → assert fetch called again with same prompt (AC-US5-03)
   - `error_emptyPromptShowsInlineError()`: Click generate with empty textarea → assert inline error "Describe what your skill should do" visible; fetch NOT called (AC-US5-04)
   - **Coverage Target**: 90%

**Implementation**:
1. Add these test cases to the existing test file
2. Run `npx vitest run` and confirm RED for new tests

---

### T-012: Render ErrorCard and inline error with retry

**User Story**: US-005
**Satisfies ACs**: AC-US5-01, AC-US5-02, AC-US5-03, AC-US5-04
**Status**: [x] completed

**Test Plan**:
- **Given** AI generation fails
- **When** the error is classified
- **Then** ErrorCard renders with retry; when unclassified, inline error message appears; retry re-attempts generation

**Test Cases**:
1. Same test cases as T-011 — they must now pass (GREEN phase)
   - **Coverage Target**: 90%

**Implementation**:
1. Inside the `{mode === "ai"}` section, below ProgressLog:
   - `{aiClassifiedError && <ErrorCard error={aiClassifiedError} onRetry={handleGenerate} />}`
   - `{!aiClassifiedError && aiError && <div ... style={{color:"var(--red)"}}>{aiError}</div>}`
   - Add a "Retry" link/button below the inline error that calls `handleGenerate()`
2. In `handleGenerate()`, add empty-prompt guard: `if (!aiPrompt.trim()) { setAiError("Describe what your skill should do"); return; }`
3. Run tests: T-011 test cases must now pass
4. Run `npx vitest run`

---

## User Story: US-006 - Manual Flow Preservation

**Linked ACs**: AC-US6-01, AC-US6-02
**Tasks**: 1 total, 1 completed

### T-013: Verify manual creation flow is unaffected

**User Story**: US-006
**Satisfies ACs**: AC-US6-01, AC-US6-02
**Status**: [x] completed

**Test Plan**:
- **Given** the component loads with Manual mode selected by default
- **When** the user fills in name, description, body and clicks "Create Skill"
- **Then** `api.createSkill` is called with the correct fields and no AI-related calls are made

**Test Cases**:
1. **Unit**: `src/eval-ui/src/components/__tests__/CreateSkillInline.test.tsx`
   - `manual_createSkillCallsApiWithCorrectFields()`: Fill name, description, body → click Create Skill → assert `api.createSkill` called with matching fields; assert `fetch` never called (AC-US6-01, AC-US6-02)
   - `manual_createButtonDisabledWhenFieldsEmpty()`: Assert Create Skill button disabled when name or description is empty (existing behavior preserved)
   - **Coverage Target**: 95%

**Implementation**:
1. Run `npx vitest run` — all existing manual-path tests must still pass
2. If any regression exists, trace to the T-002/T-003 changes and fix
3. Confirm `fetch` is not called in manual-only test scenarios
4. Run full suite: `npx vitest run` — all 13 task test cases pass
5. Final type check: `tsc --noEmit` from `src/eval-ui/`
