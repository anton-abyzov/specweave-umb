---
increment: 0458-eval-run-history
title: "Eval Run History & A/B Benchmarking"
coverage_target: 90
by_user_story:
  US-001: [T-001, T-002]
  US-002: [T-003, T-004]
  US-003: [T-005, T-006]
  US-004: [T-007, T-008]
  US-005: [T-009]
  US-006: [T-010]
  US-007: [T-011]
  US-008: [T-012, T-013]
---

# Tasks: Eval Run History & A/B Benchmarking

## User Story: US-001 - Enriched History Data Model

**Linked ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04
**Tasks**: 2 total, 2 completed

### T-001: Extend BenchmarkCase and add ComparisonCaseDetail types

**User Story**: US-001
**Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-04
**Status**: [x] completed

**Test Plan**:
- **Given** the `BenchmarkCase` interface in `benchmark.ts`
- **When** a benchmark or baseline run completes and builds a case result
- **Then** the case object includes optional `inputTokens`, `outputTokens`, and `comparisonDetail` fields without breaking existing code that omits them

**Test Cases**:
1. **Unit**: `repositories/anton-abyzov/vskill/src/eval/benchmark.test.ts`
   - testBenchmarkCaseAcceptsNewOptionalFields(): Asserts a case without the new fields still satisfies the TypeScript interface
   - testComparisonCaseDetailShape(): Constructs a full `ComparisonCaseDetail` object and verifies all required sub-fields are present
   - **Coverage Target**: 95%

**Implementation**:
1. In `src/eval/benchmark.ts`, add optional fields to `BenchmarkCase`: `inputTokens?: number`, `outputTokens?: number`, `comparisonDetail?: ComparisonCaseDetail`
2. Add new `ComparisonCaseDetail` interface with all fields from plan section 3.1
3. In `src/eval/benchmark-history.ts`, expand `HistorySummary.type` union to `"benchmark" | "comparison" | "baseline"`
4. Add `HistoryFilter` interface to `benchmark-history.ts`
5. Run `npx tsc --noEmit` to verify backward compatibility

---

### T-002: Backward-compatible UI rendering for missing enriched fields

**User Story**: US-001
**Satisfies ACs**: AC-US1-03, AC-US1-04
**Status**: [x] completed

**Test Plan**:
- **Given** an old history entry loaded from disk that lacks `inputTokens`, `outputTokens`, and `assertions` on each case
- **When** the HistoryPage detail view renders that entry
- **Then** all missing numeric fields display "--" and missing arrays render as empty (no runtime errors)

**Test Cases**:
1. **Unit**: `repositories/anton-abyzov/vskill/src/eval-ui/src/pages/HistoryPage.test.tsx`
   - testRendersOldEntryWithoutErrors(): Renders HistoryPage detail panel with a fixture entry missing new fields; asserts no thrown errors and "--" text appears for token fields
   - **Coverage Target**: 90%

**Implementation**:
1. Identify all places in `HistoryPage.tsx` and sub-components that display token counts, duration, or assertions
2. Add null/undefined guards using `?? "--"` for numeric fields and `?? []` for assertion arrays
3. Update `src/eval-ui/src/types.ts`: mark `inputTokens`, `outputTokens`, `comparisonDetail` as optional on `BenchmarkCase`; expand `BenchmarkResult.type` to include `"baseline"`
4. Run component tests to confirm no rendering errors with old fixture data

---

## User Story: US-002 - Baseline-Only Run Mode

**Linked ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04
**Tasks**: 2 total, 2 completed

### T-003: Extract benchmark-runner.ts and implement baseline endpoint

**User Story**: US-002
**Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03
**Status**: [x] completed

**Test Plan**:
- **Given** the eval server is running and a skill directory contains eval cases
- **When** a POST request is made to `/api/skills/:plugin/:skill/baseline`
- **Then** the server streams SSE events (`case_start`, `output_ready`, `assertion_result`, `case_complete`, `done`) with a plain system prompt, and the final history entry has `type: "baseline"` with per-case assertions, tokens, and duration

**Test Cases**:
1. **Integration**: `repositories/anton-abyzov/vskill/src/eval-server/benchmark-runner.test.ts`
   - testBaselineRunEmitsCorrectSSEEvents(): Uses mock LLM client; verifies event sequence and that no skill content appears in the system prompt
   - testBaselineHistoryEntryType(): Checks the written history JSON has `type: "baseline"`
   - testEnrichedFieldsPopulated(): Verifies `inputTokens` and `outputTokens` are written for each case when the LLM client returns them
   - **Coverage Target**: 90%

**Implementation**:
1. Create `src/eval-server/benchmark-runner.ts` — extract the SSE loop from `api-routes.ts` benchmark handler into `runBenchmarkSSE(opts)` accepting `systemPrompt`, `runType`, and other params per plan section 3.3
2. Update the existing `/benchmark` route in `api-routes.ts` to delegate to `runBenchmarkSSE`
3. Add `POST /api/skills/:plugin/:skill/baseline` route in `api-routes.ts` that calls `runBenchmarkSSE` with `systemPrompt: "You are a helpful AI assistant."` and `runType: "baseline"`
4. In `runBenchmarkSSE`, map `genResult.inputTokens` and `genResult.outputTokens` onto each `BenchmarkCase`
5. Run integration tests

---

### T-004: Baseline visual distinction in HistoryPage

**User Story**: US-002
**Satisfies ACs**: AC-US2-04
**Status**: [x] completed

**Test Plan**:
- **Given** the history timeline contains a mix of benchmark, comparison, and baseline entries
- **When** the HistoryPage renders the timeline
- **Then** baseline entries have a distinct visual label/badge (orange "baseline" pill) that differs from benchmark (blue) and comparison (purple)

**Test Cases**:
1. **Unit**: `repositories/anton-abyzov/vskill/src/eval-ui/src/pages/HistoryPage.test.tsx`
   - testBaselineEntryShowsDistinctBadge(): Renders timeline with a baseline entry and asserts a "baseline" text/badge element is present with a distinct CSS class
   - **Coverage Target**: 90%

**Implementation**:
1. In `HistoryPage.tsx`, locate the timeline entry rendering logic
2. Add a type-based badge: `"benchmark"` -> blue pill, `"comparison"` -> purple pill, `"baseline"` -> orange pill (Tailwind class matching `#fb923c`)
3. Run component test and visually verify

---

## User Story: US-003 - History Filtering

**Linked ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04
**Tasks**: 2 total, 2 completed

### T-005: Server-side history filtering in listHistory

**User Story**: US-003
**Satisfies ACs**: AC-US3-01
**Status**: [x] completed

**Test Plan**:
- **Given** a skill directory with multiple history JSON files of varying types, models, and timestamps
- **When** `listHistory` is called with filter params `{ model: "gpt-4o", type: "benchmark", from: "2026-01-01", to: "2026-12-31" }`
- **Then** only entries matching all provided filters are returned; unset filters are ignored

**Test Cases**:
1. **Unit**: `repositories/anton-abyzov/vskill/src/eval/benchmark-history.test.ts`
   - testListHistoryFilterByModel(): Creates 3 fixture history files with different models; asserts filter returns only the matching model
   - testListHistoryFilterByType(): Asserts type filter returns only `"baseline"` entries when specified
   - testListHistoryFilterByDateRange(): Asserts `from`/`to` timestamps pre-filter files before JSON parse
   - testListHistoryNoFilters(): Asserts original behavior unchanged when no filter provided
   - **Coverage Target**: 95%

**Implementation**:
1. Add `HistoryFilter` interface to `src/eval/benchmark-history.ts` (if not already done in T-001)
2. Update `listHistory` signature to accept optional `filter?: HistoryFilter`
3. Add date-range pre-filter using filename-embedded timestamp before JSON parse
4. Add model and type post-filter after JSON parse
5. Update the `GET /api/skills/:p/:s/history` route in `api-routes.ts` to parse `?model`, `?type`, `?from`, `?to` query params and pass to `listHistory`
6. Run unit tests

---

### T-006: FilterBar UI and empty state on HistoryPage

**User Story**: US-003
**Satisfies ACs**: AC-US3-02, AC-US3-03, AC-US3-04
**Status**: [x] completed

**Test Plan**:
- **Given** the HistoryPage with multiple history entries
- **When** the user selects a model filter that matches no entries, then clears the type filter
- **Then** the timeline shows an empty state message when no entries match, and clearing one filter while keeping another leaves the remaining filter active

**Test Cases**:
1. **Unit**: `repositories/anton-abyzov/vskill/src/eval-ui/src/pages/HistoryPage.test.tsx`
   - testFilterBarUpdatesTimeline(): Selects a model filter and asserts the timeline re-renders with only matching entries
   - testEmptyStateWhenNoMatch(): Applies a filter with no matches and asserts an empty-state message is displayed
   - testClearOneFilterKeepsOthers(): Applies model + type filters, clears type, asserts model filter remains active
   - **Coverage Target**: 90%

**Implementation**:
1. Add FilterBar state to `HistoryPage.tsx`: `filterModel`, `filterType`, `filterFrom`, `filterTo` as React state
2. Render FilterBar above the timeline: model `<select>` (options from unique models in history), type `<select>`, two `<input type="date">` fields, and a "Clear All" button
3. On filter change, call `api.getHistory(plugin, skill, filters)` (updated in T-011) and update the displayed list
4. When filtered list is empty, render an empty state `<p>` message
5. Run component tests

---

## User Story: US-004 - Cross-Session Run Comparison

**Linked ACs**: AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-04
**Tasks**: 2 total, 2 completed

### T-007: History-compare API endpoint

**User Story**: US-004
**Satisfies ACs**: AC-US4-03, AC-US4-04
**Status**: [x] completed

**Test Plan**:
- **Given** two history entries exist with timestamps A and B
- **When** `GET /api/skills/:plugin/:skill/history-compare?a={A}&b={B}` is called
- **Then** the response includes `regressions`, `improvements`, `runA`, `runB`, and `caseDiffs` with "missing" status for eval cases present in one run but not the other

**Test Cases**:
1. **Unit**: `repositories/anton-abyzov/vskill/src/eval-server/api-routes.test.ts`
   - testHistoryCompareReturnsRegressions(): Two fixture entries where a case changes from pass to fail; asserts regression appears in response
   - testHistoryCompareUnmatchedCases(): One fixture with 3 cases, other with 2 (different IDs); asserts `caseDiffs` includes a "missing" entry
   - testHistoryCompareMissingTimestamp(): Calls endpoint with non-existent timestamp; asserts 404 response
   - **Coverage Target**: 90%

**Implementation**:
1. Add `GET /api/skills/:p/:s/history-compare` route to `api-routes.ts`
2. Parse `?a` and `?b` query params; return 400 if either is missing
3. Load both history entries via `readHistoryEntry`; return 404 if either is not found
4. Call `computeRegressions(entryA.cases, entryB.cases)` from `comparator.ts`
5. Compute `caseDiffs` by building a set of eval IDs from both entries and marking unmatched as `"missing"`
6. Return the `HistoryCompareResult` shape from plan section 3.4
7. Run unit tests

---

### T-008: CompareView UI on HistoryPage with checkbox selection

**User Story**: US-004
**Satisfies ACs**: AC-US4-01, AC-US4-02, AC-US4-04
**Status**: [x] completed

**Test Plan**:
- **Given** the HistoryPage timeline with two entries having checkboxes
- **When** the user checks exactly two run checkboxes and clicks "Compare"
- **Then** the detail panel shows a side-by-side per-case table with regressions in red, improvements in green, and "new"/"removed" badges for unmatched cases

**Test Cases**:
1. **Unit**: `repositories/anton-abyzov/vskill/src/eval-ui/src/pages/HistoryPage.test.tsx`
   - testCompareButtonVisibleOnTwoSelections(): Selects 0, 1, 2, 3 checkboxes and asserts "Compare" button is visible only when exactly 2 are checked
   - testCompareViewShowsRegressionColors(): Mocks `api.compareRuns`; asserts cells for regressions have red CSS class and improvements have green
   - testCompareViewUnmatchedBadges(): Asserts "new"/"removed" badge text appears for unmatched cases
   - **Coverage Target**: 90%

**Implementation**:
1. Add `selectedRuns: Set<string>` state to `HistoryPage.tsx`
2. Add checkboxes to each timeline entry row, toggling their timestamp in `selectedRuns`
3. Show "Compare" button only when `selectedRuns.size === 2`
4. On "Compare" click, call `api.compareRuns(plugin, skill, ...selectedRuns)` and store result as `compareResult` state
5. Render `CompareView` local component in the detail panel: a table with columns `Case`, `Run A`, `Run B`
6. Color rows: `bg-red-950` for regressions, `bg-green-950` for improvements
7. Render "new" or "removed" badge (orange or gray pill) for cases with `"missing"` status
8. Run component tests

---

## User Story: US-005 - Trend Visualization

**Linked ACs**: AC-US5-01, AC-US5-02, AC-US5-03, AC-US5-04
**Tasks**: 1 total, 1 completed

### T-009: TrendChart SVG component for HistoryPage

**User Story**: US-005
**Satisfies ACs**: AC-US5-01, AC-US5-02, AC-US5-03, AC-US5-04
**Status**: [x] completed

**Test Plan**:
- **Given** a list of `HistorySummary` entries sorted oldest-first with mixed types
- **When** `<TrendChart entries={entries} />` is rendered
- **Then** an SVG element is present with one data point per entry colored by type (benchmark=`#6383ff`, comparison=`#a78bfa`, baseline=`#fb923c`), a tooltip appears on hover, and the component renders nothing when entries.length < 2

**Test Cases**:
1. **Unit**: `repositories/anton-abyzov/vskill/src/eval-ui/src/components/TrendChart.test.tsx`
   - testRendersSVGWithTwoOrMoreEntries(): Renders with 3 entries; asserts SVG element present and 3 circle elements
   - testDoesNotRenderWithOneEntry(): Renders with 1 entry; asserts no SVG in output
   - testDoesNotRenderWithZeroEntries(): Renders with 0 entries; asserts no SVG in output
   - testColorsByType(): Asserts benchmark circles use `#6383ff`, baseline circles use `#fb923c`
   - **Coverage Target**: 90%

**Implementation**:
1. Create `src/eval-ui/src/components/TrendChart.tsx`
2. Props: `{ entries: HistorySummary[] }` — return `null` when `entries.length < 2`
3. Compute SVG layout: `CHART_WIDTH = 600`, `CHART_HEIGHT = 180`, padding 30px on each side
4. Map each entry to `(x, y)`: x = evenly spaced, y = `(1 - passRate/100) * CHART_HEIGHT`
5. Render `<polyline>` connecting all points, then `<circle r={5}>` per point colored by type
6. Add hover state: on `onMouseEnter` per circle, set tooltip state; position HTML `<div>` absolutely showing timestamp, model, type, pass rate
7. Render a legend row below the chart header: colored squares + labels for each type
8. Mount `TrendChart` in `HistoryPage.tsx` above the filter bar, passing history sorted ascending
9. Run component tests

---

## User Story: US-006 - Rerun Capabilities

**Linked ACs**: AC-US6-01, AC-US6-02, AC-US6-03, AC-US6-04
**Tasks**: 1 total, 1 completed

### T-010: Rerun buttons on HistoryPage and BenchmarkPage with autostart support

**User Story**: US-006
**Satisfies ACs**: AC-US6-01, AC-US6-02, AC-US6-03, AC-US6-04
**Status**: [x] completed

**Test Plan**:
- **Given** a selected run in the HistoryPage detail view
- **When** the user clicks "Rerun Benchmark", "Run Baseline", or "Run A/B Comparison"
- **Then** the UI navigates to the correct page with `?autostart=true` (and `?mode=baseline` for baseline), and BenchmarkPage/ComparisonPage auto-starts the run on mount via a `useRef`-guarded `useEffect`

**Test Cases**:
1. **Unit**: `repositories/anton-abyzov/vskill/src/eval-ui/src/pages/HistoryPage.test.tsx`
   - testRerunBenchmarkNavigates(): Clicks "Rerun Benchmark"; asserts navigation to benchmark URL with `autostart=true`
   - testRunBaselineNavigates(): Clicks "Run Baseline"; asserts navigation with `mode=baseline&autostart=true`
   - testRunABNavigates(): Clicks "Run A/B Comparison"; asserts navigation to compare URL with `autostart=true`

2. **Unit**: `repositories/anton-abyzov/vskill/src/eval-ui/src/pages/BenchmarkPage.test.tsx`
   - testAutostartBenchmarkOnMount(): Renders BenchmarkPage with `?autostart=true`; asserts `useSSE.start()` called once
   - testAutostartBaselineOnMount(): Renders with `?mode=baseline&autostart=true`; asserts SSE started with baseline URL
   - testAutostartGuardedByRef(): Asserts start is called only once even if component re-renders
   - **Coverage Target**: 90%

**Implementation**:
1. In `HistoryPage.tsx` detail view header (when `selectedRuns.size === 1`), add three buttons: "Rerun Benchmark", "Run Baseline", "Run A/B Comparison"
2. Each button uses React Router `navigate()` to the appropriate route with search params
3. In `BenchmarkPage.tsx`, read `?autostart` and `?mode` from `useSearchParams`
4. Add `autostartRef = useRef(false)` guard; in `useEffect`, if `autostart === "true"` and `!autostartRef.current`, set flag and call `useSSE.start(baselineUrl or benchmarkUrl based on mode)`
5. In `ComparisonPage.tsx`, add same `?autostart=true` handling with ref guard
6. In `BenchmarkPage.tsx`, add "Run Baseline" button (starts SSE to `/baseline`) and "Run A/B Comparison" button (navigates to ComparisonPage with `?autostart=true`)
7. Run all related tests

---

## User Story: US-007 - Frontend API Client Extensions

**Linked ACs**: AC-US7-01, AC-US7-02, AC-US7-03, AC-US7-04
**Tasks**: 1 total, 1 completed

### T-011: Update api.ts with getHistory filters and compareRuns, update types.ts

**User Story**: US-007
**Satisfies ACs**: AC-US7-01, AC-US7-02, AC-US7-03, AC-US7-04
**Status**: [x] completed

**Test Plan**:
- **Given** the frontend API client
- **When** `api.getHistory(plugin, skill, { model: "gpt-4o", type: "baseline" })` is called
- **Then** the GET request URL includes `?model=gpt-4o&type=baseline` as query parameters; when `api.compareRuns(plugin, skill, tsA, tsB)` is called, it fetches from `/history-compare?a={tsA}&b={tsB}`

**Test Cases**:
1. **Unit**: `repositories/anton-abyzov/vskill/src/eval-ui/src/api.test.ts`
   - testGetHistoryWithAllFilters(): Mocks fetch; calls with all 4 filters; asserts URL query string contains all params
   - testGetHistoryWithNoFilters(): Asserts no query string appended when filters object is empty/undefined
   - testCompareRunsFetchesCorrectURL(): Asserts fetch called with correct `/history-compare?a=...&b=...` URL
   - **Coverage Target**: 90%

**Implementation**:
1. In `src/eval-ui/src/types.ts`:
   - Expand `HistorySummary.type` to `"benchmark" | "comparison" | "baseline"`
   - Add optional `inputTokens`, `outputTokens`, `comparisonDetail` to `BenchmarkCase`
   - Add `HistoryFilter` interface
   - Add `HistoryCompareResult` interface matching plan section 3.4 response shape
   - Add `CaseHistoryEntry` interface for US-008
2. In `src/eval-ui/src/api.ts`:
   - Update `getHistory` signature to accept optional `filters?: HistoryFilter` and append them as query params (skip undefined values)
   - Add `compareRuns(plugin: string, skill: string, a: string, b: string): Promise<HistoryCompareResult>` method
   - Note: `runBaseline` is NOT a method on api — baseline SSE uses `useSSE.start()` with the baseline URL constructed inline
3. Run unit tests

---

## User Story: US-008 - Per-Test-Case History

**Linked ACs**: AC-US8-01, AC-US8-02, AC-US8-03, AC-US8-04
**Tasks**: 2 total, 2 completed

### T-012: getCaseHistory backend function and API endpoint

**User Story**: US-008
**Satisfies ACs**: AC-US8-01, AC-US8-04
**Status**: [x] completed

**Test Plan**:
- **Given** a skill directory with 3 history files each containing an eval case with `eval_id: 42`
- **When** `GET /api/skills/:plugin/:skill/history/case/42` is called
- **Then** the response is an array of 3 `CaseHistoryEntry` objects sorted newest-first, each containing `timestamp`, `model`, `type`, `pass_rate`, `durationMs`, `tokens`, `inputTokens`, `outputTokens`, `assertions`, and `provider`

**Test Cases**:
1. **Unit**: `repositories/anton-abyzov/vskill/src/eval/benchmark-history.test.ts`
   - testGetCaseHistoryReturnsCasesFromAllFiles(): Creates 3 fixture history files; asserts all 3 `CaseHistoryEntry` results returned sorted newest-first
   - testGetCaseHistoryFilterByModel(): Calls with `?model=gpt-4o`; asserts only matching model entries returned
   - testGetCaseHistoryMissingEvalId(): Calls with an eval_id not present in any file; asserts empty array returned
   - **Coverage Target**: 90%

2. **Integration**: `repositories/anton-abyzov/vskill/src/eval-server/api-routes.test.ts`
   - testCaseHistoryEndpoint404OnMissingSkill(): Calls endpoint for non-existent skill; asserts 404

**Implementation**:
1. Add `getCaseHistory(skillDir: string, evalId: number, filter?: { model?: string }): Promise<CaseHistoryEntry[]>` to `src/eval/benchmark-history.ts`
2. Implementation: read all history files via `listHistory`, then for each summary read the full JSON file, extract the case matching `evalId`, map to `CaseHistoryEntry`, apply optional model filter, sort newest-first
3. Add `GET /api/skills/:p/:s/history/case/:evalId` route to `api-routes.ts`; parse `?model` query param; call `getCaseHistory`; return array
4. Run tests

---

### T-013: Per-case history panel on BenchmarkPage with mini trend line

**User Story**: US-008
**Satisfies ACs**: AC-US8-02, AC-US8-03
**Status**: [x] completed

**Test Plan**:
- **Given** the BenchmarkPage showing completed eval case cards
- **When** the user clicks on a completed eval case card
- **Then** an expandable panel appears below it showing historical results for that case sorted newest-first (model, pass rate, time, tokens per row) and a mini trend line

**Test Cases**:
1. **Unit**: `repositories/anton-abyzov/vskill/src/eval-ui/src/pages/BenchmarkPage.test.tsx`
   - testClickCaseCardExpandsHistoryPanel(): Clicks a case card; asserts a history panel element becomes visible
   - testHistoryPanelShowsNewestFirst(): Mocks `api.getCaseHistory` returning 3 entries; asserts entries rendered in newest-first order
   - testHistoryPanelMiniTrend(): Asserts a trend SVG element is rendered inside the panel when 2+ entries exist
   - testModelFilterNarrowsResults(): Changes the model dropdown; asserts API called with `?model=X`
   - **Coverage Target**: 85%

**Implementation**:
1. In `src/eval-ui/src/api.ts`, add `getCaseHistory(plugin: string, skill: string, evalId: number, model?: string): Promise<CaseHistoryEntry[]>` method fetching from `/history/case/:evalId?model=X`
2. In `BenchmarkPage.tsx`, add `expandedCaseId: number | null` state
3. On case card click, toggle `expandedCaseId`; when set, fetch from `api.getCaseHistory` and store in `caseHistory` state
4. Render the panel below the clicked card: a list of `CaseHistoryEntry` rows (timestamp, model pill, pass rate badge, duration, tokens)
5. Add model `<select>` dropdown inside the panel; on change, re-fetch with `?model=X`
6. Render mini trend line: small SVG (height 60px) mapping pass rates to y-coords with model labels — reuse TrendChart coordinate math in a simplified inline SVG
7. Run component tests
