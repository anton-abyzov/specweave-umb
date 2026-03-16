# Tasks: Skill Studio AI-Assisted Create Improvements

## Task Notation

- `[T###]`: Task ID
- `[P]`: Parallelizable
- `[ ]`: Not started
- `[x]`: Completed
- Model hints: haiku (simple), opus (default)

## Phase 1: Shared Hook Extraction

### T-001: Create useCreateSkill shared hook
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01 | **Status**: [x] Completed

**Description**: Extract shared state and handler logic from CreateSkillPage and CreateSkillInline into a reusable `useCreateSkill` custom hook.

**Implementation Details**:
- Create `src/eval-ui/src/hooks/useCreateSkill.ts`
- Move to hook: layout detection, form state (name, description, model, allowedTools, body), AI generation (prompt, generating, progress, error), draft saving, plugin recommendation, path preview, kebab helper
- Hook accepts `onCreated: (plugin: string, skill: string) => void` callback
- Hook does NOT include pendingEvals (removed per US-001)
- Return: all state values + handlers (handleGenerate, handleCancelGenerate, handleCreate, setters)

**Test Plan**:
- **File**: `src/eval-ui/src/hooks/__tests__/useCreateSkill.test.ts`
- **Tests**:
  - **TC-001**: Hook initializes with default state values
    - Given the hook is initialized
    - When no actions are taken
    - Then mode is "manual", name/description/body are empty, generating is false
  - **TC-002**: handleCreate validates required fields
    - Given name is empty
    - When handleCreate is called
    - Then error is set to "Skill name is required"
  - **TC-003**: toKebab converts names correctly
    - Given input "My Cool Skill"
    - When toKebab is called
    - Then result is "my-cool-skill"

**Dependencies**: None

---

### T-002: Refactor CreateSkillInline to use shared hook
**User Story**: US-004 | **Satisfies ACs**: AC-US4-02, AC-US4-03 | **Status**: [x] Completed

**Description**: Replace duplicated state and logic in CreateSkillInline with the `useCreateSkill` hook. Keep only the JSX template and inline-specific behavior.

**Implementation Details**:
- Import and use `useCreateSkill` hook
- Remove all duplicated state declarations and handlers
- Pass `onCreated` callback from props
- Keep the inline-specific JSX layout (no breadcrumbs, no sidebar preview)

**Test Plan**:
- **File**: `src/eval-ui/src/components/__tests__/CreateSkillInline.test.tsx`
- **Tests**:
  - **TC-004**: Component renders without error
    - Given CreateSkillInline is rendered with mock props
    - When layout loads
    - Then the "Create a New Skill" heading is present

**Dependencies**: T-001

---

### T-003: Refactor CreateSkillPage to use shared hook
**User Story**: US-004 | **Satisfies ACs**: AC-US4-02, AC-US4-03 | **Status**: [x] Completed

**Description**: Replace duplicated state and logic in CreateSkillPage with the `useCreateSkill` hook. Keep only the page-specific JSX layout (breadcrumbs, sidebar preview, provider/model pickers).

**Implementation Details**:
- Import and use `useCreateSkill` hook
- Remove all duplicated state declarations and handlers
- Wrap `onCreated` to call `navigate()` for page context
- Keep page-specific: breadcrumbs, SKILL.md preview sidebar, explicit provider/model dropdowns

**Test Plan**:
- **File**: `src/eval-ui/src/pages/__tests__/CreateSkillPage.test.tsx`
- **Tests**:
  - **TC-005**: Component renders with breadcrumbs
    - Given CreateSkillPage is rendered
    - When layout loads
    - Then breadcrumb shows "Skills / New Skill"

**Dependencies**: T-001

## Phase 2: UI Cleanup

### T-004: Remove AI help text from create flow
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01 | **Status**: [x] Completed

**Description**: Remove the verbose help text paragraph below the AI prompt textarea in both create components.

**Implementation Details**:
- In CreateSkillInline: Remove the `<p>` tag at line 413-416 that says "Describe what the skill should do. The AI will generate..."
- In CreateSkillPage: Remove the `<p>` tag at line 455-459 with similar text
- Keep the textarea placeholder text which provides sufficient guidance
- Keep the "Cmd+Enter to generate" hint (move to after textarea if needed)

**Test Plan**:
- **Tests**:
  - **TC-006**: AI mode does not contain help text paragraph
    - Given AI mode is active
    - When the component renders
    - Then no text containing "The AI will generate" is present

**Dependencies**: T-002, T-003

---

### T-005: Remove eval generation from create flow
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02, AC-US1-03 | **Status**: [x] Completed

**Description**: Stop generating, storing, and passing evals during skill creation. The hook should ignore evals from the AI generation response.

**Implementation Details**:
- In useCreateSkill hook: Do not store `data.evals` from SSE response
- Do not pass `evals` to `api.createSkill()` or `api.saveDraft()`
- SkillFileTree: Always pass `hasEvals={false}` (or remove the prop usage in create context)

**Test Plan**:
- **Tests**:
  - **TC-007**: createSkill is called without evals field
    - Given AI generation completes with evals in response
    - When handleCreate is called
    - Then api.createSkill is called without evals in the request body
  - **TC-008**: SkillFileTree does not show evals directory
    - Given a skill is being created via AI
    - When the file tree renders
    - Then no "evals" directory node is present

**Dependencies**: T-001

---

### T-006: Change button label to always "Create Skill"
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02 | **Status**: [x] Completed

**Description**: Change the submit button text from conditional `aiGenerated ? "Save" : "Create Skill"` to always show "Create Skill".

**Implementation Details**:
- In CreateSkillInline: Change line 752 from `aiGenerated ? "Save" : "Create Skill"` to `"Create Skill"`
- In CreateSkillPage: Change line 923 similarly
- Remove `aiGenerated` state from the hook (no longer needed for UI decisions)

**Test Plan**:
- **Tests**:
  - **TC-009**: Button always shows "Create Skill"
    - Given AI generation has completed (aiGenerated was true)
    - When the form renders
    - Then submit button text is "Create Skill" (not "Save")

**Dependencies**: T-002, T-003

---

### T-007: Verify preview mode works correctly
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03 | **Status**: [x] Completed

**Description**: Verify that the Write/Preview toggle renders markdown correctly and empty state shows placeholder.

**Implementation Details**:
- Verify `renderMarkdown(body)` is called in preview mode
- Verify empty body shows "Start writing to see preview" placeholder
- No code changes expected — this is a verification task
- If any issues found, fix them

**Test Plan**:
- **Tests**:
  - **TC-010**: Preview mode renders markdown content
    - Given body contains "# Hello\n\nWorld"
    - When bodyViewMode is "preview"
    - Then rendered HTML contains heading and paragraph elements
  - **TC-011**: Empty preview shows placeholder
    - Given body is empty
    - When bodyViewMode is "preview"
    - Then "Start writing to see preview" text is shown

**Dependencies**: T-002, T-003

## Phase 3: Testing & Verification

### T-008: Run full test suite and verify
**User Story**: US-004 | **Satisfies ACs**: AC-US4-03 | **Status**: [x] Completed

**Description**: Run the full vitest suite to verify no regressions from the refactor.

**Implementation Details**:
- Run `cd repositories/anton-abyzov/vskill && npx vitest run`
- Fix any failing tests
- Verify all existing EvalChangesPanel tests still pass

**Test Plan**:
- **Tests**:
  - **TC-012**: All existing tests pass
    - Given the refactored codebase
    - When `npx vitest run` is executed
    - Then all tests pass with 0 failures

**Dependencies**: T-001 through T-007
