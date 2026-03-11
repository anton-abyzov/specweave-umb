# Tasks: AI commands not recording to history

## Task Notation

- `[T###]`: Task ID
- `[P]`: Parallelizable
- `[ ]`: Not started
- `[x]`: Completed
- Model hints: haiku (simple), sonnet (default), opus (complex)

## Phase 1: Backend Type Extensions

### T-001: Extend backend type unions for new history entry types
**User Story**: US-003 | **Satisfies ACs**: AC-US3-04 | **Status**: [ ] Not Started

**Description**: Add `"ai-generate"` and `"eval-generate"` to the type unions in `benchmark-history.ts` and `benchmark.ts`.

**Implementation Details**:
- In `src/eval/benchmark-history.ts`: extend `HistorySummary.type`, `HistoryFilter.type`, and `CaseHistoryEntry.type` unions to include `"ai-generate" | "eval-generate"`
- In `src/eval/benchmark.ts`: extend `BenchmarkResult.type` union if it has one (or the `writeHistoryEntry` parameter type)
- Add optional `generate?: { prompt: string; result: string }` field to `BenchmarkResult`

**Test Plan**:
- **File**: TypeScript compilation
- **Tests**:
  - **TC-001**: Type compilation succeeds with new type values
    - Given the updated type unions
    - When TypeScript compiles the project
    - Then no type errors related to the new values

**Dependencies**: None
**Model Hint**: haiku

---

## Phase 2: Backend History Recording

### T-002: Record history for AI eval generation
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03 | **Status**: [ ] Not Started

**Description**: Add `writeHistoryEntry` call in the `generate-evals` endpoint handler in `api-routes.ts`.

**Implementation Details**:
- In `src/eval-server/api-routes.ts`, in the `POST /api/skills/:plugin/:skill/generate-evals` handler
- After successful `parseGeneratedEvals`, before sending response
- Import `writeHistoryEntry` (already imported in this file)
- Call `writeHistoryEntry(skillDir, { timestamp, model, skill_name, cases: [], overall_pass_rate: undefined, type: "eval-generate", provider, generate: { prompt, result: JSON.stringify(evalsFile) } })`
- Wrap in try/catch so history write failure doesn't break the main response

**Test Plan**:
- **File**: `src/eval-server/__tests__/api-routes-generate-evals.test.ts` (or existing test file)
- **Tests**:
  - **TC-002**: History entry written after successful eval generation
    - Given a skill with SKILL.md exists
    - When `POST /api/skills/:plugin/:skill/generate-evals` succeeds
    - Then `writeHistoryEntry` is called with `type: "eval-generate"`
  - **TC-003**: History entry includes model and provider
    - Given eval generation completes
    - When history entry is examined
    - Then it contains the model name and provider used for generation

**Dependencies**: T-001
**Model Hint**: sonnet

---

### T-003: Record history for AI skill creation
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03 | **Status**: [ ] Not Started

**Description**: Add `writeHistoryEntry` call in the `POST /api/skills/create` handler when the skill was AI-generated (indicated by presence of `evals` in the request body).

**Implementation Details**:
- In `src/eval-server/skill-create-routes.ts`, in the `POST /api/skills/create` handler
- After successful skill creation (after `writeFileSync` for SKILL.md and evals)
- Only when `body.evals && body.evals.length > 0` (indicates AI generation was used)
- Import `writeHistoryEntry` from `../eval/benchmark-history.js`
- Call `writeHistoryEntry(targetDir, { timestamp, model: "unknown", skill_name: body.name, cases: [], overall_pass_rate: undefined, type: "ai-generate", provider: "unknown", generate: { prompt: body.description, result: content } })`
- Note: model/provider info is not available in the create request (it was used in the generate step). Store "unknown" or consider passing model info through.

**Test Plan**:
- **File**: `src/eval-server/__tests__/skill-create-routes.test.ts`
- **Tests**:
  - **TC-004**: History entry written when skill created with AI-generated evals
    - Given a valid create request with `evals` array
    - When `POST /api/skills/create` succeeds
    - Then `writeHistoryEntry` is called with `type: "ai-generate"`
  - **TC-005**: No history entry for manually created skills
    - Given a valid create request without `evals`
    - When `POST /api/skills/create` succeeds
    - Then `writeHistoryEntry` is NOT called

**Dependencies**: T-001
**Model Hint**: sonnet

---

## Phase 3: Frontend Fixes

### T-004: Extend frontend type unions
**User Story**: US-003 | **Satisfies ACs**: AC-US3-05 | **Status**: [ ] Not Started

**Description**: Update frontend TypeScript types to include all AI command history types.

**Implementation Details**:
- In `src/eval-ui/src/types.ts`:
  - `BenchmarkResult.type`: add `"ai-generate" | "eval-generate"` to the union
  - `HistorySummary.type`: add `"ai-generate" | "eval-generate"` to the union
  - `HistoryFilter.type`: add `"ai-generate" | "eval-generate"` to the union
  - `CaseHistoryEntry.type`: add `"improve" | "instruct" | "model-compare" | "ai-generate" | "eval-generate"` (currently only has `"benchmark" | "comparison" | "baseline"`)
- Add optional `generate?: { prompt: string; result: string }` to `BenchmarkResult`

**Test Plan**:
- **File**: TypeScript compilation
- **Tests**:
  - **TC-006**: Frontend compiles with updated types
    - Given updated type definitions
    - When `npm run build` runs for eval-ui
    - Then no type errors

**Dependencies**: T-001 (for consistency)
**Model Hint**: haiku

---

### T-005: Fix HistoryPanel filter and HistoryPage type badges
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03 | **Status**: [ ] Not Started

**Description**: Fix the workspace HistoryPanel filter type union and add missing TYPE_PILL entries and filter options in HistoryPage.

**Implementation Details**:
- In `src/eval-ui/src/pages/workspace/HistoryPanel.tsx`:
  - Line 20: Add `"instruct" | "ai-generate" | "eval-generate"` to the `filterType` state union
  - Add corresponding `<option>` elements in the filter dropdown (around line 148)
- In `src/eval-ui/src/pages/HistoryPage.tsx`:
  - Add to `TYPE_PILL` map (around line 47):
    - `"instruct": { bg: "rgba(168,85,247,0.15)", fg: "#a855f7", label: "AI Edit" }`
    - `"ai-generate": { bg: "rgba(34,197,94,0.15)", fg: "#22c55e", label: "AI Generate" }`
    - `"eval-generate": { bg: "rgba(251,146,60,0.15)", fg: "#fb923c", label: "Eval Generate" }`
  - `FilterBar` dropdown already has "AI Edit" (instruct) option but add options for "AI Generate" and "Eval Generate"

**Test Plan**:
- **File**: Manual UI verification
- **Tests**:
  - **TC-007**: All type badges render in history timeline
    - Given history entries of each type exist
    - When the History tab is viewed
    - Then each entry shows its correct colored badge
  - **TC-008**: Filter dropdown includes all AI types
    - Given the History tab is open
    - When the type filter dropdown is opened
    - Then options for AI Edit, AI Generate, and Eval Generate are available

**Dependencies**: T-004
**Model Hint**: haiku

---

## Phase 4: Validation

### T-006: Verify all acceptance criteria
**User Story**: All | **Satisfies ACs**: All | **Status**: [ ] Not Started

**Description**: Run existing tests, verify TypeScript compilation, and manually test the full flow.

**Implementation Details**:
- Run `npx vitest run` in vskill directory
- Verify no regressions in existing benchmark-history tests
- Verify TypeScript compiles cleanly

**Test Plan**:
- **File**: All test suites
- **Tests**:
  - **TC-009**: All existing tests pass
    - Given all changes are applied
    - When `npx vitest run` executes
    - Then all tests pass with no regressions

**Dependencies**: T-001, T-002, T-003, T-004, T-005
**Model Hint**: sonnet
