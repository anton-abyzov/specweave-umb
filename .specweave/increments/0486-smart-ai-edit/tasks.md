# Tasks: AI Edit with Eval Change Suggestions

<!--
increment: 0486-smart-ai-edit
generated_by: sw:test-aware-planner
coverage_target: 90%
by_user_story:
  US-001: [T-001, T-002]
  US-002: [T-003, T-004, T-005]
  US-003: [T-006, T-007]
  US-004: [T-008, T-009, T-010]
-->

## Task Notation

- `[P]`: Parallelizable with other [P] tasks at same level
- `[ ]`: Not started | `[x]`: Completed
- Model hints: haiku (simple/boilerplate), sonnet (default), opus (complex logic)

---

## User Story: US-001 - LLM Returns Eval Change Suggestions

**Linked ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04
**Tasks**: 2 total, all completed

### T-001: Extend Backend Types and API Shape for Eval Changes

**User Story**: US-001
**Satisfies ACs**: AC-US1-03
**Status**: [x] completed
**Model hint**: haiku [P]

**Test Plan**:
- **Given** the TypeScript types file for the improve route exists
- **When** `EvalChange` and `InstructEditResult` types are defined
- **Then** all action variants (`add`, `modify`, `remove`) are represented, `reason` is always present, `evalId` is required for modify/remove, `eval` is required for add/modify

**Test Cases**:
1. **Unit** (type-level): `repositories/anton-abyzov/vskill/src/eval-server/improve-routes.test.ts`
   - `evalChangeAddShape()`: EvalChange with action=add must have `eval`, no `evalId`
   - `evalChangeModifyShape()`: action=modify requires both `evalId` and `eval`
   - `evalChangeRemoveShape()`: action=remove requires `evalId`, no `eval`
   - **Coverage Target**: 90%

**Implementation**:
1. In `src/eval-server/improve-routes.ts` (or a co-located `types` block), define:
   ```typescript
   export interface EvalChange {
     action: "add" | "modify" | "remove";
     reason: string;
     evalId?: number;
     eval?: EvalCase;
   }
   ```
2. In `src/eval-ui/src/types.ts`, add `EvalChange` and extend `InstructEditResult`:
   ```typescript
   export interface InstructEditResult {
     original: string;
     improved: string;
     reasoning: string;
     evalChanges: EvalChange[];
   }
   ```
3. Extend `POST /improve` request body type: add `evals?: EvalsFile`

---

### T-002: Extend improve-routes.ts -- Prompt Construction, Response Parsing, Graceful Degradation

**User Story**: US-001
**Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-04
**Status**: [x] completed
**Model hint**: sonnet

**Test Plan**:
- **Given** a POST /improve request in instruct mode with evals provided
- **When** the LLM returns a 3-part response (content, reasoning, eval changes JSON)
- **Then** the endpoint returns `{ improved, original, reasoning, evalChanges: [...] }` with the parsed array

- **Given** a POST /improve request where `body.evals` is undefined
- **When** the LLM call is made
- **Then** the prompt sends `"evals": []` and the endpoint still returns valid `evalChanges`

- **Given** the LLM response has no `---EVAL_CHANGES---` section or contains malformed JSON
- **When** the endpoint parses the response
- **Then** `evalChanges` is `[]` and the SKILL.md result is returned normally

**Test Cases**:
1. **Unit**: `repositories/anton-abyzov/vskill/src/eval-server/improve-routes.test.ts`
   - `parseEvalChanges_valid3Part()`: splits on `---EVAL_CHANGES---`, parses JSON array
   - `parseEvalChanges_missingSection()`: returns `[]` when delimiter absent
   - `parseEvalChanges_malformedJson()`: returns `[]` on JSON parse error
   - `parseEvalChanges_emptyArray()`: returns `[]` for `[]` literal
   - `buildInstructPrompt_withEvals()`: prompt contains current evals JSON
   - `buildInstructPrompt_noEvals()`: prompt contains `"evals": []`
   - **Coverage Target**: 90%

**Implementation**:
1. In `improve-routes.ts` instruct mode handler, append eval analysis section to system prompt when `mode === "instruct"`:
   - Include eval analysis rules and output format instructions with `---EVAL_CHANGES---`
   - Append `body.evals ?? { evals: [] }` as JSON to the user prompt under `## Current Evals`
2. After parsing `---REASONING---`, split on `---EVAL_CHANGES---`:
   ```typescript
   const [reasoningText, evalChangesRaw] = reasoningPart.split("---EVAL_CHANGES---");
   let evalChanges: EvalChange[] = [];
   if (evalChangesRaw) {
     try { evalChanges = JSON.parse(evalChangesRaw.trim()); }
     catch { evalChanges = []; }
   }
   ```
3. Return `evalChanges` in the JSON response alongside existing fields

---

## User Story: US-002 - Combined Review Panel

**Linked ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04, AC-US2-05
**Tasks**: 3 total, all completed

### T-003: EvalChangeCard Component -- Summary, Action Badge, Expand/Collapse

**User Story**: US-002
**Satisfies ACs**: AC-US2-02, AC-US2-03, AC-US2-05
**Status**: [x] completed
**Model hint**: sonnet [P]

**Test Plan**:
- **Given** an eval change object with action="modify", a reason string, and original+proposed eval data
- **When** `EvalChangeCard` renders
- **Then** it shows the eval name, an "MODIFY" badge, the reason text, and a collapsed expand section

- **Given** the user clicks the expand toggle
- **When** the card is expanded for a modify action
- **Then** it shows a field-level diff of changed fields (name, prompt, expected_output, assertions)

- **Given** an eval change with action="add" (no original eval)
- **When** the card is expanded
- **Then** it shows the full proposed eval content (no diff)

- **Given** the checkbox is initially checked
- **When** the user clicks the checkbox
- **Then** `onToggle` is called with the change index

**Test Cases**:
1. **Unit**: `repositories/anton-abyzov/vskill/src/eval-ui/src/components/EvalChangeCard.test.tsx`
   - `renders_summaryLine()`: name + badge + reason visible
   - `renders_removeBadge()`: action="remove" shows red REMOVE badge
   - `renders_addBadge()`: action="add" shows green ADD badge
   - `renders_modifyBadge()`: action="modify" shows yellow MODIFY badge
   - `expand_showsFieldDiff_forModify()`: changed fields shown as "old -> new"
   - `expand_showsFullContent_forAdd()`: full eval JSON/fields shown for add
   - `checkbox_callsOnToggle()`: clicking checkbox fires onToggle(index)
   - `checkbox_checked_byDefault()`: checkbox is checked when selected=true
   - **Coverage Target**: 90%

**Implementation**:
1. Create `src/eval-ui/src/components/EvalChangeCard.tsx`:
   - Props: `change: EvalChange`, `originalEval?: EvalCase`, `index: number`, `selected: boolean`, `onToggle: (i: number) => void`
   - Render compact row: checkbox + badge (color by action) + eval name + reason
   - Expand toggle: shows field-level diff for modify, full content for add, full content for remove
   - Field diff: compare `name`, `prompt`, `expected_output`, `assertions` between `originalEval` and `change.eval`
2. Use existing CSS patterns from the eval-ui for badge colors

---

### T-004: EvalChangesPanel Component -- Grouping, Select All/Deselect All

**User Story**: US-002
**Satisfies ACs**: AC-US2-01, AC-US2-04
**Status**: [x] completed
**Model hint**: sonnet [P]

**Test Plan**:
- **Given** an array of eval changes with mixed actions
- **When** `EvalChangesPanel` renders
- **Then** changes are grouped in order: removes first, then modifies, then adds

- **Given** `evalChanges` is an empty array
- **When** `EvalChangesPanel` renders
- **Then** the entire section is hidden (returns null)

- **Given** some changes exist
- **When** the user clicks "Select All"
- **Then** `onSelectAll` is called; when they click "Deselect All", `onDeselectAll` is called

**Test Cases**:
1. **Unit**: `repositories/anton-abyzov/vskill/src/eval-ui/src/components/EvalChangesPanel.test.tsx`
   - `renders_null_whenEmpty()`: returns null for empty changes array
   - `sorts_removeFirst_thenModify_thenAdd()`: order of rendered cards matches sort
   - `selectAll_callsHandler()`: clicking Select All fires onSelectAll
   - `deselectAll_callsHandler()`: clicking Deselect All fires onDeselectAll
   - `showsSuggestionCount()`: header shows "(N suggestions)"
   - **Coverage Target**: 90%

**Implementation**:
1. Create `src/eval-ui/src/components/EvalChangesPanel.tsx`:
   - Props: `changes: EvalChange[]`, `selections: Map<number, boolean>`, `currentEvals: EvalCase[]`, `onToggle`, `onSelectAll`, `onDeselectAll`
   - Return null when `changes.length === 0`
   - Sort a copy: removes → modifies → adds (preserving original indices for selection keys)
   - Render header: "Eval Changes (N suggestions)" + Select All / Deselect All buttons
   - Render `EvalChangeCard` per change, passing `originalEval` looked up by `change.evalId`

---

### T-005: Integrate EvalChangesPanel into AiEditBar

**User Story**: US-002
**Satisfies ACs**: AC-US2-01, AC-US2-04, AC-US2-05
**Status**: [x] completed
**Model hint**: haiku

**Test Plan**:
- **Given** `AiEditBar` is in result state with `aiEditEvalChanges` populated
- **When** the component renders
- **Then** `EvalChangesPanel` appears below the SKILL.md diff

- **Given** `aiEditEvalChanges` is empty
- **When** the component renders
- **Then** no eval changes section is visible

**Test Cases**:
1. **Integration**: `repositories/anton-abyzov/vskill/src/eval-ui/src/components/AiEditBar.test.tsx`
   - `showsEvalChangesPanel_whenChangesExist()`: EvalChangesPanel renders in result state
   - `hidesEvalChangesPanel_whenNoChanges()`: EvalChangesPanel absent when empty
   - **Coverage Target**: 85%

**Implementation**:
1. In `AiEditBar.tsx`, import `EvalChangesPanel`
2. Wire workspace state: `aiEditEvalChanges`, `aiEditEvalSelections` from context
3. Wire dispatch callbacks: `TOGGLE_EVAL_CHANGE`, `SELECT_ALL_EVAL_CHANGES`, `DESELECT_ALL_EVAL_CHANGES`
4. Render `<EvalChangesPanel>` below the diff section, passing current evals from workspace state

---

## User Story: US-003 - Selective Apply of Eval Changes

**Linked ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04, AC-US3-05
**Tasks**: 2 total, all completed

### T-006: Implement mergeEvalChanges Utility

**User Story**: US-003
**Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-05
**Status**: [x] completed
**Model hint**: sonnet [P]

**Test Plan**:
- **Given** a current EvalsFile with 3 evals and a selections map where all changes are checked
- **When** `mergeEvalChanges` is called with remove, modify, and add changes
- **Then** the returned EvalsFile has the remove deleted, the modify replaced, and the add appended with a new id

- **Given** a selections map where the add change is unchecked
- **When** `mergeEvalChanges` is called
- **Then** the add is not present in the result

- **Given** a modify change references a non-existent evalId
- **When** `mergeEvalChanges` is called
- **Then** the change is silently skipped (no error, original evals preserved)

- **Given** no changes are selected
- **When** `mergeEvalChanges` is called
- **Then** the result equals the original evals

**Test Cases**:
1. **Unit**: `repositories/anton-abyzov/vskill/src/eval-ui/src/utils/mergeEvalChanges.test.ts`
   - `remove_deletesMatchingEval()`: eval with matching id is absent from result
   - `modify_replacesMatchingEval()`: eval replaced with new content, id preserved
   - `add_appendsWithNewId()`: new eval appended, id = max + 1
   - `add_multipleAdds_incrementIds()`: multiple adds get sequential IDs
   - `unchecked_changeIsIgnored()`: deselected change has no effect
   - `noChangesSelected_returnsOriginal()`: result equals original when all unchecked
   - `modifyUnmatchedId_isSkipped()`: no error on unknown evalId
   - `removeFirst_thenModify_thenAdd()`: processing order is correct
   - **Coverage Target**: 95%

**Implementation**:
1. Create `src/eval-ui/src/utils/mergeEvalChanges.ts`:
   ```typescript
   export function mergeEvalChanges(
     current: EvalsFile,
     changes: EvalChange[],
     selections: Map<number, boolean>
   ): EvalsFile
   ```
2. Filter to only selected changes (`selections.get(i) === true`)
3. Process in order: removes → modifies → adds
4. Removes: `evals.filter(e => e.id !== change.evalId)`
5. Modifies: replace by id, keep original id on the replacement
6. Adds: assign `id = Math.max(0, ...evals.map(e => e.id)) + 1` (incrementing for each add)
7. Return new EvalsFile object (do not mutate input)

---

### T-007: Extend applyAiEdit -- Merge and Save Evals with Error/Retry

**User Story**: US-003
**Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04, AC-US3-05
**Status**: [x] completed
**Model hint**: sonnet

**Test Plan**:
- **Given** the user clicks Apply with some eval changes checked
- **When** `applyAiEdit` runs
- **Then** SKILL.md is saved first, then `mergeEvalChanges` is called with only selected changes, and the result is PUT to /evals

- **Given** the SKILL.md save fails
- **When** `applyAiEdit` runs
- **Then** the evals save is NOT attempted and an error is shown

- **Given** SKILL.md save succeeds but PUT /evals fails
- **When** `applyAiEdit` runs
- **Then** SKILL.md content is preserved, `aiEditEvalsRetry` is set with the merged evals, and a retry error message is shown

- **Given** no eval changes are checked
- **When** `applyAiEdit` runs
- **Then** only SKILL.md is saved (PUT /evals is not called)

**Test Cases**:
1. **Integration**: `repositories/anton-abyzov/vskill/src/eval-ui/src/WorkspaceContext.test.tsx`
   - `applyAiEdit_savesSkillMd_thenEvals()`: both endpoints called in order
   - `applyAiEdit_skillMdFails_stopsPipeline()`: PUT /evals not called on SKILL.md failure
   - `applyAiEdit_evalsFail_setsRetryState()`: aiEditEvalsRetry holds merged evals
   - `applyAiEdit_noCheckedChanges_skipsPutEvals()`: PUT /evals skipped when all unchecked
   - `retryEvalsSave_callsPutEvals()`: retry uses stored merged evals
   - **Coverage Target**: 90%

**Implementation**:
1. In `WorkspaceContext.tsx`, extend `applyAiEdit`:
   - Call `mergeEvalChanges(currentEvals, aiEditEvalChanges, aiEditEvalSelections)`
   - If merged evals differ from current (any selected changes exist), call `PUT /evals` after SKILL.md save
   - On evals failure: dispatch `SET_EVALS_RETRY` with merged evals; show retry error
2. Add `retryEvalsSave()` function that calls `PUT /evals` with `aiEditEvalsRetry`
3. Add `aiEditEvalsRetry: EvalsFile | null` to WorkspaceState (clear on discard/close)
4. Expose `retryEvalsSave` from context

---

## User Story: US-004 - Workspace State for Eval Changes

**Linked ACs**: AC-US4-01, AC-US4-02, AC-US4-03
**Tasks**: 3 total, all completed

### T-008: Extend workspaceTypes.ts -- New State Fields and Action Types

**User Story**: US-004
**Satisfies ACs**: AC-US4-01, AC-US4-02
**Status**: [x] completed
**Model hint**: haiku [P]

**Test Plan**:
- **Given** the workspace types file is updated
- **When** TypeScript compiles the project
- **Then** `WorkspaceState` has `aiEditEvalChanges`, `aiEditEvalSelections`, `aiEditEvalsRetry` fields
- **Then** `WorkspaceAction` union includes `TOGGLE_EVAL_CHANGE`, `SELECT_ALL_EVAL_CHANGES`, `DESELECT_ALL_EVAL_CHANGES`
- **Then** `AI_EDIT_RESULT` action type includes `evalChanges: EvalChange[]`

**Test Cases**:
1. **Unit (compile-time)**: Verified by `tsc --noEmit` in the eval-ui package
   - All new fields have correct TypeScript types
   - `AI_EDIT_RESULT` action is backward-compatible (evalChanges defaults to `[]` if omitted in tests)
   - **Coverage Target**: N/A (type-level)

**Implementation**:
1. In `src/eval-ui/src/workspaceTypes.ts`:
   - Add to `WorkspaceState`:
     ```typescript
     aiEditEvalChanges: EvalChange[];
     aiEditEvalSelections: Map<number, boolean>;
     aiEditEvalsRetry: EvalsFile | null;
     ```
   - Extend `AI_EDIT_RESULT` action: add `evalChanges: EvalChange[]`
   - Add actions:
     ```typescript
     | { type: "TOGGLE_EVAL_CHANGE"; index: number }
     | { type: "SELECT_ALL_EVAL_CHANGES" }
     | { type: "DESELECT_ALL_EVAL_CHANGES" }
     | { type: "SET_EVALS_RETRY"; evalsFile: EvalsFile }
     ```
2. Initialize new fields in the initial state object

---

### T-009: Extend workspaceReducer.ts -- Handle New Actions

**User Story**: US-004
**Satisfies ACs**: AC-US4-01, AC-US4-02
**Status**: [x] completed
**Model hint**: sonnet [P]

**Test Plan**:
- **Given** the reducer receives `AI_EDIT_RESULT` with an `evalChanges` array
- **When** the action is handled
- **Then** `aiEditEvalChanges` is set and `aiEditEvalSelections` is initialized as a Map with all indices set to `true`

- **Given** `aiEditEvalSelections` has index 1 set to `true`
- **When** `TOGGLE_EVAL_CHANGE { index: 1 }` is dispatched
- **Then** `aiEditEvalSelections.get(1)` is `false`

- **Given** some selections are `false`
- **When** `SELECT_ALL_EVAL_CHANGES` is dispatched
- **Then** all selections are `true`

- **Given** `CLOSE_AI_EDIT` is dispatched
- **When** the reducer handles it
- **Then** `aiEditEvalChanges` is `[]` and `aiEditEvalSelections` is an empty Map

**Test Cases**:
1. **Unit**: `repositories/anton-abyzov/vskill/src/eval-ui/src/workspaceReducer.test.ts`
   - `aiEditResult_initializesEvalChanges()`: evalChanges stored and all selections true
   - `toggleEvalChange_flipsSelection()`: true→false and false→true
   - `selectAll_setsAllTrue()`: all entries become true
   - `deselectAll_setsAllFalse()`: all entries become false
   - `closeAiEdit_clearsEvalState()`: evalChanges=[], selections=empty Map
   - `aiEditResult_noEvalChanges_emptyState()`: empty array initializes empty Map
   - **Coverage Target**: 95%

**Implementation**:
1. In `workspaceReducer.ts`, extend `AI_EDIT_RESULT` case:
   - Set `aiEditEvalChanges: action.evalChanges`
   - Build `aiEditEvalSelections`: `new Map(action.evalChanges.map((_, i) => [i, true]))`
2. Add `TOGGLE_EVAL_CHANGE` case: create new Map, flip `selections.get(index)`
3. Add `SELECT_ALL_EVAL_CHANGES`: map all keys to `true`
4. Add `DESELECT_ALL_EVAL_CHANGES`: map all keys to `false`
5. Add `SET_EVALS_RETRY`: set `aiEditEvalsRetry`
6. Extend `CLOSE_AI_EDIT` / `DISCARD_AI_EDIT`: clear all three new fields

---

### T-010: Extend WorkspaceContext -- submitAiEdit Sends Evals and Dispatches Changes

**User Story**: US-004
**Satisfies ACs**: AC-US4-03
**Status**: [x] completed
**Model hint**: sonnet

**Test Plan**:
- **Given** the workspace has current evals loaded
- **When** `submitAiEdit` is called with an instruction
- **Then** `api.instructEdit` is called with the current evals included in the request body

- **Given** the API response contains an `evalChanges` array
- **When** `submitAiEdit` resolves
- **Then** `AI_EDIT_RESULT` is dispatched with `evalChanges` from the response

- **Given** the API response has `evalChanges: []`
- **When** `submitAiEdit` resolves
- **Then** `AI_EDIT_RESULT` is dispatched with an empty `evalChanges` array (no error)

**Test Cases**:
1. **Integration**: `repositories/anton-abyzov/vskill/src/eval-ui/src/WorkspaceContext.test.tsx`
   - `submitAiEdit_sendsCurrentEvals()`: instructEdit called with evals from state
   - `submitAiEdit_dispatchesEvalChanges()`: AI_EDIT_RESULT has evalChanges from response
   - `submitAiEdit_noEvals_sendsEmptyArray()`: works when workspace has no evals loaded
   - **Coverage Target**: 90%

**Implementation**:
1. In `WorkspaceContext.tsx`, find `submitAiEdit`:
   - Read `currentEvals` from workspace state
   - Pass `evals: currentEvals ?? undefined` to `api.instructEdit`
2. In the response handler, destructure `evalChanges` from the result
3. Dispatch `AI_EDIT_RESULT` with `evalChanges: evalChanges ?? []`
4. Extend `api.ts` `instructEdit` function signature to accept optional `evals` and return `InstructEditResult` (with `evalChanges`)
