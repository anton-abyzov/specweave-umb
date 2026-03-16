---
increment: 0497-comparison-action-items
title: "Comparison Action Items Engine"
status: completed
by_user_story:
  US-001: [T-001, T-002, T-003]
  US-002: [T-004, T-005]
  US-003: [T-006, T-007, T-008]
---

# Tasks: Comparison Action Items Engine

## Task Notation

- `[x]`: Completed
- `[ ]`: Pending

---

## User Story: US-001 - Action Items Data Model and Engine

**Linked ACs**: AC-US1-01, AC-US1-02, AC-US1-03
**Tasks**: 3 total, 3 completed

### T-001: Add ActionItems types to benchmark.ts and types.ts

**User Story**: US-001
**Satisfies ACs**: AC-US1-01
**Status**: [x] completed

**Test Plan**:
- **Given** the comparison result data model exists
- **When** ActionItems types are added to benchmark.ts and types.ts
- **Then** TypeScript compiles cleanly and downstream consumers can import the new types

**Test Cases**:
1. **Unit**: `repositories/anton-abyzov/vskill-platform/src/lib/benchmark.test.ts`
   - testActionItemsTypeShape(): Verify ActionItems interface has required fields (recommendation, weaknesses, ai_fix)
   - **Coverage Target**: 95%

**Implementation**:
1. Add `ActionItems` interface to `benchmark.ts`
2. Add type export to `types.ts`
3. Verify TypeScript compilation passes

---

### T-002: Create action-items.ts engine with LLM prompt

**User Story**: US-001
**Satisfies ACs**: AC-US1-02
**Status**: [x] completed

**Test Plan**:
- **Given** a completed A/B comparison result with verdict and metrics
- **When** the action items engine is invoked
- **Then** it returns structured action items with keep/remove/rewrite recommendation, specific SKILL.md weaknesses, and an AI-generated fix suggestion

**Test Cases**:
1. **Unit**: `repositories/anton-abyzov/vskill-platform/src/lib/action-items.test.ts`
   - testGenerateActionItemsReturnsStructured(): LLM response parsed into ActionItems shape
   - testGenerateActionItemsKeepRecommendation(): when A wins, recommendation is "keep"
   - testGenerateActionItemsRemoveRecommendation(): when B wins by large margin, recommendation is "remove"
   - **Coverage Target**: 90%

2. **Integration**: `repositories/anton-abyzov/vskill-platform/src/lib/action-items.integration.test.ts`
   - testActionItemsEngineWithMockedLLM(): End-to-end engine call with mocked LLM response
   - **Coverage Target**: 85%

**Implementation**:
1. Create `action-items.ts` in `src/lib/`
2. Write LLM prompt template for structured action items
3. Parse and validate LLM response into `ActionItems` shape
4. Export `generateActionItems(comparisonResult)` function

---

### T-003: Wire action items generation into compare endpoint in api-routes.ts

**User Story**: US-001
**Satisfies ACs**: AC-US1-03
**Status**: [x] completed

**Test Plan**:
- **Given** the compare API endpoint receives a valid comparison request
- **When** the comparison completes and the verdict is produced
- **Then** action items are generated and included in the API response JSON

**Test Cases**:
1. **Integration**: `repositories/anton-abyzov/vskill-platform/src/api-routes.test.ts`
   - testCompareEndpointIncludesActionItems(): POST /compare response body contains `action_items` field
   - testCompareEndpointActionItemsSchema(): action_items matches ActionItems interface shape
   - **Coverage Target**: 90%

**Implementation**:
1. Import `generateActionItems` into `api-routes.ts`
2. Call engine after verdict is produced
3. Append `action_items` to response payload

---

## User Story: US-002 - Action Items UI Panel

**Linked ACs**: AC-US2-01, AC-US2-02
**Tasks**: 2 total, 2 completed

### T-004: Create ActionItemsPanel UI component

**User Story**: US-002
**Satisfies ACs**: AC-US2-01
**Status**: [x] completed

**Test Plan**:
- **Given** an ActionItems object is passed as props
- **When** the ActionItemsPanel renders
- **Then** recommendation badge, weakness list, and AI fix suggestion are displayed in the correct sections

**Test Cases**:
1. **Unit**: `repositories/anton-abyzov/vskill-platform/src/components/ActionItemsPanel.test.tsx`
   - testRendersRecommendationBadge(): recommendation value shown in styled badge
   - testRendersWeaknessList(): each weakness item appears as a list entry
   - testRendersAiFix(): ai_fix text rendered in fix section
   - testHandlesEmptyWeaknesses(): gracefully handles empty weakness array
   - **Coverage Target**: 95%

**Implementation**:
1. Create `ActionItemsPanel.tsx` in `src/components/`
2. Style recommendation badge with colour coding (keep=green, rewrite=yellow, remove=red)
3. Render weakness list
4. Render AI fix section

---

### T-005: Integrate ActionItemsPanel into ComparisonPage

**User Story**: US-002
**Satisfies ACs**: AC-US2-02
**Status**: [x] completed

**Test Plan**:
- **Given** a comparison has completed and the result includes action_items
- **When** the ComparisonPage renders the result
- **Then** ActionItemsPanel is displayed below the verdict section

**Test Cases**:
1. **Unit**: `repositories/anton-abyzov/vskill-platform/src/app/comparison/ComparisonPage.test.tsx`
   - testActionItemsPanelShownAfterCompletion(): panel present in DOM after comparison completes
   - testActionItemsPanelHiddenDuringLoading(): panel absent while comparison is running
   - **Coverage Target**: 90%

**Implementation**:
1. Import `ActionItemsPanel` into `ComparisonPage`
2. Pass `result.action_items` as props
3. Conditionally render below verdict

---

## User Story: US-003 - Progress Observability and Noise Reduction

**Linked ACs**: AC-US3-01, AC-US3-02, AC-US3-03
**Tasks**: 3 total, 3 completed

### T-006: Add action_items phase to ProgressLog spinner

**User Story**: US-003
**Satisfies ACs**: AC-US3-01
**Status**: [x] completed

**Test Plan**:
- **Given** the comparison is in the action_items generation phase
- **When** the ProgressLog renders
- **Then** a spinner entry labeled "Generating action items..." is visible

**Test Cases**:
1. **Unit**: `repositories/anton-abyzov/vskill-platform/src/components/ProgressLog.test.tsx`
   - testActionItemsPhaseSpinnerShown(): spinner entry present for action_items phase
   - testActionItemsPhaseCompletedState(): spinner transitions to checkmark on completion
   - **Coverage Target**: 90%

**Implementation**:
1. Add `action_items` phase to `ProgressLog` phase list
2. Map phase to label string "Generating action items..."
3. Verify spinner/checkmark state transitions

---

### T-007: Fix 404 console noise on benchmark/latest

**User Story**: US-003
**Satisfies ACs**: AC-US3-02
**Status**: [x] completed

**Test Plan**:
- **Given** the benchmark/latest endpoint is polled before any benchmark exists
- **When** the endpoint returns 404
- **Then** no error is logged to the browser console (404 is handled silently)

**Test Cases**:
1. **Unit**: `repositories/anton-abyzov/vskill-platform/src/lib/benchmark.test.ts`
   - testLatestEndpoint404HandledSilently(): fetch returns 404, no console.error called
   - **Coverage Target**: 90%

**Implementation**:
1. Locate polling logic for `benchmark/latest`
2. Add 404 guard: treat 404 as "not yet available" instead of error
3. Remove or suppress error log for 404 responses

---

### T-008: Run tests — all 1076 pass, TypeScript clean

**User Story**: US-003
**Satisfies ACs**: AC-US3-03
**Status**: [x] completed

**Test Plan**:
- **Given** all implementation tasks T-001 through T-007 are complete
- **When** the full test suite runs with `npx vitest run` and TypeScript is compiled
- **Then** all 1076 tests pass with zero TypeScript errors

**Test Cases**:
1. **Integration**: Full test suite
   - All 1076 tests pass: `npx vitest run`
   - TypeScript clean: `tsc --noEmit`
   - **Coverage Target**: 90% overall

**Implementation**:
1. Run `npx vitest run` — verify 1076 passing
2. Run `tsc --noEmit` — verify zero errors
3. Fix any regressions found
