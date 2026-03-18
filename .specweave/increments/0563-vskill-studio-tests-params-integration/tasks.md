# Tasks: vSkill Studio: Test Tabs, Parameter Store, Integration Tests, AI Gen

## Task Notation

- `[T###]`: Task ID
- `[P]`: Parallelizable
- `[ ]`: Not started
- `[x]`: Completed
- Model hints: haiku (simple), opus (default)

## Phase 1: US-001 — Tab Filter Bug Fix

### T-003: RED — Write failing tests for selectedCaseId reset on filter change

**Description**: Create TestsPanel-tabFilter.test.tsx with tests verifying that changing the filter tab auto-selects the first visible case.

**References**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04

**Test Plan**:
- **File**: `src/eval-ui/src/pages/workspace/__tests__/TestsPanel-tabFilter.test.tsx`
- **Tests**:
  - **TC-001**: Given unit case selected + filter to "integration" → dispatch SELECT_CASE to first integration case
  - **TC-002**: Given only unit tests + filter to "integration" → shows "No integration tests yet"
  - **TC-003**: Given filter is "All" → all cases visible
  - **TC-004**: Given allCases.length === 0 → full empty state
  - **TC-005**: Given evals is null → shows validation error
  - **TC-006**: Given filter to "integration" with no integration cases → dispatch SELECT_CASE with null

**Dependencies**: None
**Status**: [x] Completed

### T-004: GREEN — Add useEffect for selectedCaseId sync on filter change

**Description**: Add useEffect in TestsPanel.tsx (after line 124) that dispatches SELECT_CASE when the current selectedCaseId is not in the filtered cases list.

**References**: AC-US1-01, AC-US1-02

**Implementation Details**:
- Added `useEffect` that checks if `selectedCaseId` exists in `cases`
- If not found, dispatches `SELECT_CASE` with the first case in filtered list or null

**Dependencies**: T-003
**Status**: [x] Completed

## Phase 2: US-002 — Parameter Store UI

### T-005: RED — Write failing tests for ParameterStorePanel

**Description**: Create ParameterStorePanel.test.tsx verifying credential list rendering, status badges, masked values, and add parameter section.

**References**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-05

**Test Plan**:
- **File**: `src/eval-ui/src/pages/workspace/__tests__/ParameterStorePanel.test.tsx`
- **Tests**:
  - **TC-005**: Credential list with ready/missing badges
  - **TC-006**: Masked values with show/hide toggle
  - **TC-007**: Edit button for credential values
  - **TC-008**: Add New Parameter section
  - **TC-009**: Empty state when no parameters

**Dependencies**: None
**Status**: [x] Completed

### T-006: GREEN — Implement ParameterStorePanel component

**Description**: Create new React component that fetches credentials and params from API, renders them with status badges, masked values, edit capabilities, and add-new-param section.

**References**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04, AC-US2-05

**Implementation Details**:
- Created `ParameterStorePanel.tsx` with credential/param management UI
- Uses existing `api.getCredentials()`, `api.getParams()`, `api.setCredential()` endpoints
- Merges credential statuses with param values from .env.local
- Status badges (ready/missing), masked values, show/hide toggle
- Edit inline with Save/Cancel
- Add New Parameter section with key + value inputs

**Dependencies**: T-005
**Status**: [x] Completed

### T-007: Integrate ParameterStorePanel into TestsPanel

**Description**: Import and render ParameterStorePanel in the left sidebar of TestsPanel when integration tests exist.

**References**: AC-US2-01

**Implementation Details**:
- Added import for ParameterStorePanel
- Rendered below "+ Add Test Case" button when `hasIntegrationTests` is true
- Separated by border-top divider

**Dependencies**: T-006
**Status**: [x] Completed

## Phase 3: US-003 — Integration Type UX Verification

### T-009: Write verification tests for integration type UX

**Description**: Create NewCaseForm-integration.test.tsx verifying that integration badges, tab counts, type toggle, and save schema work correctly.

**References**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04

**Test Plan**:
- **File**: `src/eval-ui/src/pages/workspace/__tests__/NewCaseForm-integration.test.tsx`
- **Tests**:
  - **TC-010**: Left panel shows Integration badge
  - **TC-011**: Tab counts reflect unit vs integration
  - **TC-012**: Clickable type badge exists
  - **TC-013**: Integration save includes testType, requiredCredentials, requirements
  - **TC-014**: Unit save does not include integration fields

**Dependencies**: None
**Status**: [x] Completed (all tests pass — code already existed)

## Phase 4: US-004 — AI Gen Model Forwarding Verification

### T-011: Write verification tests for model forwarding

**Description**: Create generate-evals-model.test.ts verifying that provider/model from request body are forwarded to createLlmClient, integration testType triggers buildIntegrationEvalPrompt, and empty body uses defaults.

**References**: AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-04

**Test Plan**:
- **File**: `src/eval-server/__tests__/generate-evals-model.test.ts`
- **Tests**:
  - **TC-015**: Provider and model forwarded to createLlmClient
  - **TC-016**: testType="integration" uses buildIntegrationEvalPrompt
  - **TC-017**: Empty body falls back to defaults

**Dependencies**: None
**Status**: [x] Completed (all tests pass — code already existed)

## Phase 5: Verification

### T-013: Run full test suite

**Description**: Run `npx vitest run` and confirm all 1623 tests pass with zero regressions.

**Dependencies**: T-004, T-007, T-009, T-011
**Status**: [x] Completed — 114 test files, 1623 tests, all passing
