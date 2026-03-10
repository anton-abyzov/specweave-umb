---
increment: 0458-eval-run-history
title: Eval Run History & A/B Benchmarking
type: feature
priority: P1
status: completed
created: 2026-03-09T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Eval Run History & A/B Benchmarking

## Problem Statement

The vskill eval system has basic benchmark history and A/B comparison, but the stored data lacks granularity (no per-case token breakdowns, no input/output token split, no baseline-only assertion results). Users cannot filter history, compare arbitrary past runs, visualize trends, or run baseline-only evaluations. This limits the ability to track skill quality over time and make data-driven decisions about skill effectiveness.

## Goals

- Enrich history entries with full per-case metrics (token breakdown, duration, per-assertion pass/fail)
- Enable baseline-only eval runs (without skill) as a first-class run mode
- Provide history filtering by model, run type, and date range
- Support cross-session comparison of any two historical runs with regression diffing
- Visualize pass rate trends over time on the HistoryPage
- Add rerun capabilities (with-skill, baseline, full A/B) to both HistoryPage and BenchmarkPage

## User Stories

### US-001: Enriched History Data Model (P1)
**Project**: vskill
**As a** skill author
**I want** history entries to store full per-case metrics including input/output token breakdown, duration in seconds, and per-assertion pass/fail results
**So that** I can analyze exactly how each eval case performed across runs

**Acceptance Criteria**:
- [x] **AC-US1-01**: Given a benchmark run completes, when the history entry is written, then each case includes `inputTokens`, `outputTokens`, `durationMs`, and the full `assertions` array with individual pass/fail
- [x] **AC-US1-02**: Given a comparison run completes, when the history entry is written, then each case includes a `comparisonDetail` object with `skillDurationMs`, `skillTokens`, `baselineDurationMs`, `baselineTokens`, `skillContentScore`, `skillStructureScore`, `baselineContentScore`, `baselineStructureScore`, and `winner`
- [x] **AC-US1-03**: Given an old history entry without enriched fields is loaded, when displayed in the UI, then missing fields show "--" or "N/A" instead of errors
- [x] **AC-US1-04**: Given the new fields are added, when existing code reads a history entry, then all new fields are optional (backward compatible) and the system does not break on old entries

---

### US-002: Baseline-Only Run Mode (P1)
**Project**: vskill
**As a** skill author
**I want** to run all eval cases without the skill (baseline mode) and have those results saved to history
**So that** I can measure how well the LLM performs without my skill for comparison

**Acceptance Criteria**:
- [x] **AC-US2-01**: Given the eval server is running, when a POST request is made to `/api/skills/:plugin/:skill/baseline`, then all eval cases are executed with a plain "You are a helpful AI assistant" system prompt (no skill content)
- [x] **AC-US2-02**: Given a baseline run completes, when the result is saved, then the history entry has `type: "baseline"` and includes per-case assertions, tokens, and duration
- [x] **AC-US2-03**: Given a baseline run is in progress, when the client listens to the SSE stream, then it receives the same event types as benchmark (`case_start`, `output_ready`, `assertion_result`, `case_complete`, `done`)
- [x] **AC-US2-04**: Given a baseline run completes, when viewing history, then the entry is visually distinguished from benchmark and comparison entries

---

### US-003: History Filtering (P1)
**Project**: vskill
**As a** skill author
**I want** to filter history entries by model, run type (benchmark/comparison/baseline), and date range
**So that** I can quickly find relevant past runs

**Acceptance Criteria**:
- [x] **AC-US3-01**: Given the history API endpoint, when query parameters `model`, `type`, `from`, and `to` are provided, then only matching entries are returned
- [x] **AC-US3-02**: Given the HistoryPage UI, when a user selects filter values, then the timeline updates to show only matching runs
- [x] **AC-US3-03**: Given multiple filters are applied simultaneously, when the user clears one filter, then the remaining filters stay active
- [x] **AC-US3-04**: Given no runs match the current filters, when viewing the HistoryPage, then an empty state message indicates no matching runs

---

### US-004: Cross-Session Run Comparison (P1)
**Project**: vskill
**As a** skill author
**I want** to select any two historical runs and see a side-by-side diff showing per-case regressions and improvements
**So that** I can understand how changes to my skill affected evaluation outcomes

**Acceptance Criteria**:
- [x] **AC-US4-01**: Given the HistoryPage timeline, when a user checks exactly two run checkboxes, then a "Compare" button becomes visible
- [x] **AC-US4-02**: Given the user clicks "Compare" with two runs selected, when the comparison loads, then a side-by-side view shows per-case pass/fail status for both runs with regressions highlighted in red and improvements in green
- [x] **AC-US4-03**: Given a compare API endpoint `GET /api/skills/:plugin/:skill/history-compare?a={timestamp}&b={timestamp}`, when called with two valid timestamps, then it returns per-case diff data using the existing `computeRegressions` function
- [x] **AC-US4-04**: Given one run has eval cases that the other does not (different eval sets), when comparing, then unmatched cases are shown with a "new" or "removed" indicator

---

### US-005: Trend Visualization (P2)
**Project**: vskill
**As a** skill author
**I want** to see a pass rate over time chart on the HistoryPage, color-coded by run type
**So that** I can spot quality trends and regressions at a glance

**Acceptance Criteria**:
- [x] **AC-US5-01**: Given the HistoryPage has history entries, when the page loads, then a fixed-width SVG trend chart renders above the timeline showing pass rate (0-100%) on Y axis and runs chronologically on X axis
- [x] **AC-US5-02**: Given runs of different types exist, when the chart renders, then benchmark runs are one color, comparison runs are another, and baseline runs are a third
- [x] **AC-US5-03**: Given the chart is rendered, when hovering over a data point, then a tooltip shows the run timestamp, model, type, and pass rate
- [x] **AC-US5-04**: Given fewer than 2 history entries exist, when the HistoryPage loads, then the trend chart is not displayed

---

### US-006: Rerun Capabilities (P2)
**Project**: vskill
**As a** skill author
**I want** rerun buttons that let me re-execute a past run as with-skill, baseline-only, or full A/B comparison
**So that** I can quickly re-test after making changes to my skill

**Acceptance Criteria**:
- [x] **AC-US6-01**: Given the HistoryPage detail view for a selected run, when displayed, then three rerun buttons appear: "Rerun Benchmark" (with-skill), "Run Baseline", and "Run A/B Comparison"
- [x] **AC-US6-02**: Given the BenchmarkPage, when displayed, then alongside the existing "Run All" button, a "Run Baseline" button and a "Run A/B Comparison" button appear
- [x] **AC-US6-03**: Given a user clicks any rerun button, when the run starts, then the UI navigates to the appropriate page (BenchmarkPage for benchmark/baseline, ComparisonPage for A/B) and starts the run
- [x] **AC-US6-04**: Given a baseline rerun completes, when history is refreshed, then the new baseline entry appears in the timeline

---

### US-007: Frontend API Client Extensions (P2)
**Project**: vskill
**As a** developer
**I want** the frontend API client to support all new endpoints (baseline, filtered history, history-compare)
**So that** the UI components can consume the new backend capabilities

**Acceptance Criteria**:
- [x] **AC-US7-01**: Given the api client, when `api.runBaseline(plugin, skill)` is called, then it initiates an SSE connection to `POST /api/skills/:plugin/:skill/baseline`
- [x] **AC-US7-02**: Given the api client, when `api.getHistory(plugin, skill, filters)` is called with optional filter params, then query parameters are appended to the history GET request
- [x] **AC-US7-03**: Given the api client, when `api.compareRuns(plugin, skill, timestampA, timestampB)` is called, then it fetches from `GET /api/skills/:plugin/:skill/history-compare`
- [x] **AC-US7-04**: Given the frontend types, when `HistorySummary` type is updated, then it includes the `"baseline"` option in the `type` union and optional enriched fields

### US-008: Per-Test-Case History (P1)
**Project**: vskill
**As a** skill author
**I want** to view the history of a specific eval case (test case) across all runs, seeing how it performed with different models and over time
**So that** I can track individual test case quality and spot which cases regress when switching models

**Acceptance Criteria**:
- [x] **AC-US8-01**: Given the API endpoint `GET /api/skills/:plugin/:skill/history/case/:evalId`, when called with a valid eval ID, then it returns an array of per-run results for that case extracted from all history files, each including: timestamp, model, type, pass_rate, durationMs, tokens, inputTokens, outputTokens, assertions array, and provider
- [x] **AC-US8-02**: Given the BenchmarkPage shows eval case results, when a user clicks on a completed eval case card, then a per-case history panel expands below it showing all historical results for that case sorted newest-first, with model, pass rate, time, and tokens for each
- [x] **AC-US8-03**: Given the per-case history view, when multiple runs exist for that case, then a mini trend line shows pass rate across runs with model labels on each data point
- [x] **AC-US8-04**: Given the per-case history endpoint, when called with optional `?model=X` query param, then only results from that model are returned

---

## Out of Scope

- Deleting or archiving history entries
- Exporting history to CSV or external formats
- Multi-skill aggregate comparisons (comparing skill A vs skill B)
- Server-side trend calculation or aggregation APIs
- History entry deduplication or compaction
- Backfilling old history entries with enriched fields

## Technical Notes

- All new fields on `BenchmarkCase`, `BenchmarkResult`, and `HistorySummary` must be optional to preserve backward compatibility
- New `ComparisonCaseDetail` interface holds per-case A/B metrics stored alongside each `BenchmarkCase` in comparison history entries
- Baseline endpoint reuses the benchmark SSE handler pattern but with a plain system prompt and `type: "baseline"` on the result
- History filtering is done server-side by reading JSON filenames (for date range) and file contents (for model/type)
- The `TrendChart` is a pure SVG component with no charting library dependency
- The `HistorySummary.type` union expands from `"benchmark" | "comparison"` to `"benchmark" | "comparison" | "baseline"`

## Success Metrics

- All 7 user stories have passing acceptance criteria with TDD coverage
- Enriched history entries contain complete per-case metrics for new runs
- Old history entries render without errors in the updated UI
- Baseline runs produce results comparable in structure to benchmark runs
