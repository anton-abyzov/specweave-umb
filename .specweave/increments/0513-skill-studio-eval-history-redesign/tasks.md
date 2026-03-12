---
increment: "0513-skill-studio-eval-history-redesign"
title: "Skill Studio: eval history redesign + comparison fix"
total_tasks: 10
completed_tasks: 10
---

# Tasks: Skill Studio Eval History Redesign + Comparison Fix

## User Story: US-001 - Fix comparison mode per-case SSE rendering

**Linked ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05
**Tasks**: 3 total, 3 completed

---

### T-001: Add `assertion_result` and `case_complete` SSE emissions to comparison endpoint

**User Story**: US-001
**Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-04
**Status**: [x] completed

**Test Plan**:
- **Given** a comparison run processes assertions for a case in `api-routes.ts`
- **When** `judgeAssertion` returns a result inside the assertion loop
- **Then** the server emits an `assertion_result` SSE event per assertion with fields `eval_id`, `assertion_id`, `text`, `pass`, `reasoning` matching the benchmark-runner.ts shape; and after all assertions, emits `case_complete` with `eval_id`, `status`, `pass_rate`, `durationMs`, `tokens`; and the existing `outputs_ready` and `comparison_scored` events are still emitted

**Test Cases**:
1. **Unit**: `src/eval-server/__tests__/api-routes-comparison-sse.test.ts`
   - `emitsAssertionResultPerAssertionDuringComparisonRun()`: mock `sendSSE`, run comparison handler with 2 assertions, assert 2 `assertion_result` calls with correct shape
   - `emitsCaseCompleteAfterAllAssertionsDuringComparisonRun()`: assert 1 `case_complete` call with `pass_rate` = passing/total and `status` derived from all-pass vs any-fail
   - `preservesExistingOutputsReadyAndComparisonScoredEvents()`: assert `outputs_ready` and `comparison_scored` still emitted after new events
   - **Coverage Target**: 90%

**Implementation**:
1. Open `src/eval-server/api-routes.ts`, locate the comparison endpoint assertion loop (~line 725)
2. After `assertionResults.push(result)`, emit `sendSSE(res, "assertion_result", { eval_id, assertion_id, text, pass, reasoning })`
3. After the assertion loop, compute `casePassRate` and `caseStatus`, then emit `sendSSE(res, "case_complete", { eval_id, status, pass_rate, durationMs, tokens })`
4. Run: `npx vitest run src/eval-server/__tests__/api-routes-comparison-sse.test.ts`

---

### T-002: Add `outputs_ready` handler to `handleSSEEvent` in WorkspaceContext

**User Story**: US-001
**Satisfies ACs**: AC-US1-03
**Status**: [x] completed

**Test Plan**:
- **Given** a comparison SSE stream emits an `outputs_ready` event with `skillOutput`, `skillDurationMs`, and `skillTokens`
- **When** `handleSSEEvent` in `WorkspaceContext.tsx` processes the event
- **Then** the inline result accumulator for that case has `output` set to `skillOutput`, `durationMs` set to `skillDurationMs`, and `tokens` set to `skillTokens`

**Test Cases**:
1. **Unit**: `src/eval-ui/src/__tests__/handleSSEEvent.test.ts`
   - `outputsReadyPopulatesCaseOutput()`: dispatch `outputs_ready` event, assert accumulator `output === skillOutput`
   - `outputsReadyPopulatesDurationAndTokens()`: assert `durationMs` and `tokens` populated from event data
   - `outputsReadyDoesNotAffectOtherCases()`: two accumulators, verify only the matching `eval_id` is mutated
   - `outputsReadyHandlesMissingTimingFields()`: event with only `skillOutput` (no timing fields) leaves existing `durationMs` unchanged
   - **Coverage Target**: 90%

**Implementation**:
1. Open `src/eval-ui/src/pages/workspace/WorkspaceContext.tsx`, locate `handleSSEEvent` (~line 44)
2. After the existing `output_ready` (singular) handler block, add an `else if (evt.event === "outputs_ready")` branch
3. In that branch: `r.output = data.skillOutput as string`, then conditionally set `r.durationMs` and `r.tokens`
4. Run: `npx vitest run src/eval-ui/src/__tests__/handleSSEEvent.test.ts`

---

### T-003: Integration test -- per-case cards render assertions during Compare All

**User Story**: US-001
**Satisfies ACs**: AC-US1-05
**Status**: [x] completed

**Test Plan**:
- **Given** the server emits `outputs_ready`, then `assertion_result` per assertion, then `case_complete` for a comparison run case
- **When** the client processes the full SSE sequence
- **Then** the per-case card displays its assertion list with pass/fail indicators and a numeric pass rate percentage identical to what benchmark run cards show

**Test Cases**:
1. **Integration**: `src/eval-ui/src/__tests__/comparison-card-render.test.tsx`
   - `caseCardShowsAssertionListAfterComparisonSSESequence()`: render `WorkspaceContext` with mocked SSE stream replaying `outputs_ready` then `assertion_result` x2 then `case_complete`, assert card DOM contains assertion rows and pass rate `%` text
   - `caseCardPassRateMatchesBenchmarkCardFormat()`: compare rendered markup between a benchmark-driven card and a comparison-driven card, assert identical structure
   - **Coverage Target**: 85%

**Implementation**:
1. Write integration test using `@testing-library/react` rendering the workspace with a mock SSE event sequence
2. Assert assertion rows and pass rate `%` text are present after event replay
3. Run: `npx vitest run src/eval-ui/src/__tests__/comparison-card-render.test.tsx`

---

## User Story: US-002 - Split-lane timeline for per-case eval history

**Linked ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04, AC-US2-05
**Tasks**: 3 total, 3 completed

---

### T-004: Extract lane-partitioning logic for CaseHistorySection

**User Story**: US-002
**Satisfies ACs**: AC-US2-02, AC-US2-03, AC-US2-04
**Status**: [x] completed

**Test Plan**:
- **Given** an array of `CaseHistoryEntry` objects with types `benchmark`, `baseline`, `comparison`, and `improve`
- **When** the `getLane` helper is called for each entry type
- **Then** `benchmark` returns `"left"`, `baseline` returns `"right"`, `comparison` returns `"full"`, and `improve`/`instruct`/other non-core types return `"left"`

**Test Cases**:
1. **Unit**: `src/eval-ui/src/__tests__/caseHistoryLane.test.ts`
   - `partitionsBenchmarkToLeft()`: entry `type: "benchmark"` -> lane `"left"`
   - `partitionsBaselineToRight()`: entry `type: "baseline"` -> lane `"right"`
   - `partitionsComparisonToFull()`: entry `type: "comparison"` -> lane `"full"`
   - `partitionsImproveToLeft()`: entry `type: "improve"` -> lane `"left"`
   - `partitionsInstructToLeft()`: entry `type: "instruct"` -> lane `"left"`
   - `preservesTimestampOrderDescendingAfterPartitioning()`: mixed entries sorted newest-first retain order
   - **Coverage Target**: 95%

**Implementation**:
1. In `src/eval-ui/src/pages/workspace/TestsPanel.tsx`, extract a pure `getLane(type: string): "left" | "right" | "full"` function
2. Add `partitionEntries(entries)` that maps each entry to `{ entry, lane }` preserving timestamp-desc order
3. Export `getLane` for testability
4. Run: `npx vitest run src/eval-ui/src/__tests__/caseHistoryLane.test.ts`

---

### T-005: Render two-column CSS grid with column headers and empty-column placeholders

**User Story**: US-002
**Satisfies ACs**: AC-US2-01, AC-US2-05
**Status**: [x] completed

**Test Plan**:
- **Given** `CaseHistorySection` renders with only benchmark entries and no baseline entries
- **When** the grid layout renders
- **Then** a "Skill" header is visible above the left column, a "Baseline" header above the right column, and the right column shows "No baseline runs" in `var(--text-tertiary)` at font-size 12px

**Test Cases**:
1. **Unit**: `src/eval-ui/src/__tests__/CaseHistorySection.test.tsx`
   - `rendersSkillAndBaselineColumnHeaders()`: render with one benchmark entry, assert text "Skill" and "Baseline" present in DOM
   - `rendersNoBaselineRunsPlaceholderWhenNoBaselineEntries()`: render with only benchmark entries, assert "No baseline runs" text with `color: var(--text-tertiary)` and `fontSize: "12px"`
   - `rendersNoSkillRunsPlaceholderWhenNoSkillEntries()`: render with only baseline entries, assert "No skill runs" placeholder in left column
   - `gridContainerHasTwoColumnTemplate()`: assert container has `display: "grid"` and `gridTemplateColumns: "1fr 1fr"`
   - **Coverage Target**: 90%

**Implementation**:
1. In `TestsPanel.tsx`, replace the flat `space-y-2` container in `CaseHistorySection` with a grid container: `style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 8 }}`
2. Add column header row: two `<div>` cells with "Skill" and "Baseline" labels, `var(--text-tertiary)`, font-size 11px, uppercase, tracking-wider
3. After rendering all entries, check if left column is empty and inject "No skill runs" placeholder; same for right column
4. Run: `npx vitest run src/eval-ui/src/__tests__/CaseHistorySection.test.tsx`

---

### T-006: Render comparison entries as full-width merged cards with delta and verdict badge

**User Story**: US-002
**Satisfies ACs**: AC-US2-04
**Status**: [x] completed

**Test Plan**:
- **Given** a history entry with `type: "comparison"` and `comparisonDetail` containing rubric scores
- **When** `CaseHistorySection` renders it in the grid
- **Then** the card spans both columns via `gridColumn: "1 / -1"`, shows a `+X.X%` or `-X.X%` delta badge, and shows a winner badge of "skill", "baseline", or "tie"

**Test Cases**:
1. **Unit**: `src/eval-ui/src/__tests__/CaseHistorySection.test.tsx`
   - `rendersComparisonEntryWithGridColumnSpan()`: render with one comparison entry, assert its wrapper has `gridColumn: "1 / -1"`
   - `rendersPositiveDeltaBadgeWhenSkillWins()`: skill scores > baseline scores -> assert `+X.X%` badge text
   - `rendersNegativeDeltaBadgeWhenBaselineWins()`: baseline scores > skill scores -> assert `-X.X%` badge
   - `rendersWinnerBadgeSkill()`: skill rubric avg > baseline rubric avg -> badge text "skill"
   - `rendersWinnerBadgeTie()`: equal scores -> badge text "tie"
   - **Coverage Target**: 90%

**Implementation**:
1. In the grid render loop, when `lane === "full"`, wrap entry card in `<div style={{ gridColumn: "1 / -1" }}>`
2. Compute delta: `delta = (skillContentScore + skillStructureScore) / 2 - (baselineContentScore + baselineStructureScore) / 2`
3. Render delta badge with sign and 1 decimal place; render winner badge (positive delta = "skill", negative = "baseline", zero = "tie")
4. Run: `npx vitest run src/eval-ui/src/__tests__/CaseHistorySection.test.tsx`

---

## User Story: US-003 - Dual-line MiniTrend sparkline

**Linked ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04, AC-US3-05, AC-US3-06, AC-US3-07
**Tasks**: 4 total, 4 completed

---

### T-007: Add `baselinePassRate` field to `CaseHistoryEntry` types (server + client)

**User Story**: US-003
**Satisfies ACs**: AC-US3-01
**Status**: [x] completed

**Test Plan**:
- **Given** the `CaseHistoryEntry` interfaces in `src/eval-ui/src/types.ts` and `src/eval/benchmark-history.ts`
- **When** a TypeScript consumer constructs a `CaseHistoryEntry` object
- **Then** `baselinePassRate` is accepted as an optional `number | undefined` field on both interfaces, and omitting it does not cause a type error

**Test Cases**:
1. **Unit** (compile-time check): `src/eval/__tests__/caseHistoryEntryType.test.ts`
   - `serverTypeAcceptsBaselinePassRateField()`: construct a server `CaseHistoryEntry` with `baselinePassRate: 0.75`, confirm TypeScript does not error
   - `clientTypeAcceptsBaselinePassRateField()`: same for client type from `types.ts`
   - `baselinePassRateIsOptional()`: construct entry without `baselinePassRate`, assert compiles cleanly
   - **Coverage Target**: 80%

**Implementation**:
1. In `src/eval/benchmark-history.ts`, locate `CaseHistoryEntry` interface (~line 31-42), add `baselinePassRate?: number;`
2. In `src/eval-ui/src/types.ts`, locate client `CaseHistoryEntry` interface (~line 159-170), add `baselinePassRate?: number;`
3. Run `npx tsc --noEmit` to confirm no type errors
4. Run: `npx vitest run src/eval/__tests__/caseHistoryEntryType.test.ts`

---

### T-008: Derive `baselinePassRate` from `comparisonDetail` rubric scores in `getCaseHistory`

**User Story**: US-003
**Satisfies ACs**: AC-US3-02
**Status**: [x] completed

**Test Plan**:
- **Given** `getCaseHistory` reads a history file with a comparison-type entry containing `comparisonDetail.baselineContentScore = 80` and `comparisonDetail.baselineStructureScore = 60`
- **When** `getCaseHistory` processes that entry
- **Then** the returned `CaseHistoryEntry` has `baselinePassRate = (80 + 60) / 200 = 0.70`

**Test Cases**:
1. **Unit**: `src/eval/__tests__/benchmark-history.test.ts`
   - `derivesBaselinePassRateFromRubricScoresForComparisonEntry()`: mock history JSON with `comparisonDetail`, call `getCaseHistory`, assert `baselinePassRate === 0.70`
   - `returnsUndefinedBaselinePassRateForBenchmarkEntry()`: benchmark-type entry with no `comparisonDetail` -> `baselinePassRate === undefined`
   - `handlesZeroRubricScores()`: both scores = 0 -> `baselinePassRate === 0` (not undefined)
   - `handlesMissingComparisonDetail()`: comparison-type entry with no `comparisonDetail` field -> `baselinePassRate === undefined`
   - **Coverage Target**: 95%

**Implementation**:
1. In `src/eval/benchmark-history.ts`, `getCaseHistory` function (~line 180-221), locate the entry parsing loop
2. When building each entry, if `entry.type === "comparison" && entry.comparisonDetail`, compute: `baselinePassRate = (entry.comparisonDetail.baselineContentScore + entry.comparisonDetail.baselineStructureScore) / 200`
3. Assign to the returned entry; leave `undefined` for all other types
4. Run: `npx vitest run src/eval/__tests__/benchmark-history.test.ts`

---

### T-009: Rewrite MiniTrend with dual SVG polylines and type-filtered data sources

**User Story**: US-003
**Satisfies ACs**: AC-US3-03, AC-US3-04, AC-US3-05, AC-US3-06, AC-US3-07
**Status**: [x] completed

**Test Plan**:
- **Given** `MiniTrend` receives entries of types `benchmark`, `baseline`, `comparison`, and `improve`
- **When** the component renders
- **Then** a blue polyline (`var(--accent)`) contains skill pass-rate points from `benchmark` and `comparison` entries; a gray polyline (`var(--text-tertiary)`) contains baseline pass-rate points from `baseline` entries (`pass_rate`) and `comparison` entries (`baselinePassRate`); and `improve`-type entries are excluded from both polylines

**Test Cases**:
1. **Unit**: `src/eval-ui/src/__tests__/MiniTrend.test.tsx`
   - `rendersTwoPolylineElementsWithMixedEntries()`: 2 benchmark + 2 baseline entries -> 2 `<polyline>` in SVG
   - `skillPolylineUsesAccentColor()`: skill polyline has `stroke="var(--accent)"`
   - `baselinePolylineUsesTextTertiaryColor()`: baseline polyline has `stroke="var(--text-tertiary)"`
   - `benchmarkEntryContributesToSkillLineOnly()`: 2 benchmark entries -> skill polyline has 2 points, gray polyline absent
   - `baselineEntryContributesToBaselineLineOnly()`: 2 baseline entries -> gray polyline has 2 points, blue polyline absent
   - `comparisonEntryContributesToBothLines()`: 2 comparison entries with `baselinePassRate` -> both polylines rendered
   - `improveEntryExcludedFromBothLines()`: 2 improve entries only -> returns null
   - `returnsNullWhenBothLinesHaveFewerThanTwoPoints()`: single benchmark entry -> returns null
   - `rendersOnlySkillLineWhenBaselineHasFewerThanTwoPoints()`: 3 benchmarks + 1 baseline -> only blue polyline rendered
   - `svgDimensionsRemain80x24()`: assert SVG `width="80"` and `height="24"` unchanged
   - **Coverage Target**: 95%

**Implementation**:
1. In `src/eval-ui/src/utils/historyUtils.tsx`, open `MiniTrend` component (~line 22-51)
2. Define `EXCLUDED_TYPES = new Set(["improve","instruct","model-compare","ai-generate","eval-generate"])`
3. Filter `coreEntries` (exclude above types), reverse to chronological for shared x-axis
4. Compute `skillPoints` from `benchmark` + `comparison` entries using `pass_rate`; compute `baselinePoints` from `baseline` entries using `pass_rate` and from `comparison` entries using `baselinePassRate` (skip if undefined)
5. Render blue `<polyline>` for skill points (guard: length >= 2) and gray `<polyline>` for baseline points (guard: length >= 2); return null if both have < 2 points
6. Add blue dot on last skill point; add gray dot on last baseline point if baseline line rendered
7. Run: `npx vitest run src/eval-ui/src/__tests__/MiniTrend.test.tsx`

---

### T-010: Integration test -- history panel renders dual sparkline and split-lane correctly

**User Story**: US-003
**Satisfies ACs**: AC-US3-03
**Status**: [x] completed

**Test Plan**:
- **Given** a case has history entries of types `benchmark`, `baseline`, and `comparison` with `baselinePassRate` populated
- **When** the eval UI renders the case history panel
- **Then** `CaseHistorySection` shows "Skill" and "Baseline" column headers, `MiniTrend` renders exactly two `<polyline>` elements, and no console errors occur

**Test Cases**:
1. **Integration**: `src/eval-ui/src/__tests__/history-display-integration.test.tsx`
   - `rendersCaseHistoryWithSplitLaneAndDualSparkline()`: mount the case panel with mocked `getCaseHistory` returning mixed-type entries, assert "Skill" and "Baseline" headers present and 2 polyline elements in sparkline SVG
   - `noConsoleErrorsDuringRender()`: spy on `console.error`, render, assert zero calls
   - **Coverage Target**: 85%

**Implementation**:
1. Write integration test mounting the case panel component tree with fixture history data (2 benchmark, 2 baseline, 1 comparison)
2. Assert column headers, polyline count, and error-free render
3. Run full suite: `npx vitest run` to confirm no regressions across all affected files
