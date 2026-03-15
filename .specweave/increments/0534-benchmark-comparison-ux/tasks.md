---
increment: 0534-benchmark-comparison-ux
generated: 2026-03-15
---

# Tasks: Benchmark Comparison UX Improvements

## US-001: Progressive Skill vs Baseline Summary

### T-001: Add EMERGING to EvalVerdict type and update computeVerdict logic
**User Story**: US-001, US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03
**Status**: [x] Completed
**Test**: Given `verdict.ts` is imported with the new EMERGING branch → When `computeVerdict({ passRate: 0.33, skillAvg: 5, baselineAvg: 0 })` is called → Then the returned verdict is `"EMERGING"` and TypeScript type `EvalVerdict` includes `"EMERGING"` with no compilation errors

### T-002: Create shared verdict-styles.ts module
**User Story**: US-001, US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-04
**Status**: [x] Completed
**Test**: Given `verdict-styles.ts` exports `VERDICT_STYLES` → When the map is accessed for all five verdict keys (EFFECTIVE, MARGINAL, INEFFECTIVE, EMERGING, DEGRADING) → Then each key returns a `{ bg, text, label }` object with no undefined entries and TypeScript exhaustiveness is satisfied

### T-003: Implement useProgressiveSummary hook (client-side computation)
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02, AC-US1-03, AC-US1-04
**Status**: [x] Completed
**Test**: Given a mock SSE events array with 3 `outputs_ready` events (rubric scores) and 3 `case_complete` events (pass_rate) out of 5 total cases → When `useProgressiveSummary(events, totalCases)` is called → Then it returns `{ completedCount: 3, totalCount: 5, skillAvg, baselineAvg, delta, previewVerdict }` where `previewVerdict` matches `computeVerdict()` with the accumulated data

### T-004: Build RunningVerdictBar component
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04
**Status**: [x] Completed
**Test**: Given `<RunningVerdictBar completedCount={0} totalCount={5} />` renders → When 0 cases have completed → Then a "Comparing..." placeholder is shown with a progress bar reading "0/5 cases"; and given `completedCount={5}`, the bar shows the final previewVerdict label with no flicker between the last progressive and final render

### T-011: Integrate RunningVerdictBar into ComparisonPage and wire useMemo progressive summary
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04
**Status**: [x] Completed
**Test**: Given ComparisonPage is rendered with a live SSE mock emitting 5 case_complete events one-by-one → When each SSE event fires → Then the RunningVerdictBar updates its completedCount and previewVerdict after each event, and after the `done` event the bar matches the final verdict with no layout shift

---

## US-002: Per-Case Fix with AI Button

### T-005: Add per-case Fix button to ComparisonCard
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03
**Status**: [x] Completed
**Test**: Given a `ComparisonCard` with `failingAssertions={2}` → When the card renders → Then a "Fix" button is visible in the card's bottom area; and given `failingAssertions={0}` or `totalAssertions={0}`, then no "Fix" button is rendered

### T-006: Wire Fix button navigation with eval_id and assertion context
**User Story**: US-002 | **Satisfies ACs**: AC-US2-04, AC-US2-05
**Status**: [x] Completed
**Test**: Given a ComparisonCard with `evalId="abc123"` and failing assertion context → When the user clicks the Fix button → Then `navigate` is called with URL `/workspace/{plugin}/{skill}?improve=true&eval_id=abc123` and the router state includes the failing assertion notes from that case

---

## US-003: Fix Contradictory Verdict Labels

### T-007: Rename "Delta" to "Rubric Delta" in all verdict displays
**User Story**: US-003 | **Satisfies ACs**: AC-US3-04
**Status**: [x] Completed
**Test**: Given ComparisonPage and RunningVerdictBar render a verdict bar → When the component tree is inspected → Then no element with text content "Delta" exists (without the "Rubric" prefix) in either the progressive summary bar or the final verdict card

### T-008: Verify full 5-tier verdict coverage in ComparisonPage display
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03
**Status**: [x] Completed
**Test**: Given ComparisonPage receives a completed comparison result with verdict EMERGING → When the final verdict card renders → Then the pill shows the "EMERGING" label with the correct background color from VERDICT_STYLES and no TypeScript exhaustiveness errors appear in the switch/Record consuming EvalVerdict

### T-012: Unit tests for computeVerdict covering all 5 tiers
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03
**Status**: [x] Completed
**Test**: Given the test suite for `verdict.ts` → When run against all boundary inputs (passRate 0.0, 0.39, 0.4, 0.6, 0.8; skillAvg above and below baselineAvg) → Then every expected tier is returned with 100% branch coverage and no cases fall into wrong buckets

---

## US-004: Clearer Button Group UX

### T-009: Add tooltips and info text to BenchmarkPage button group
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-05
**Status**: [x] Completed
**Test**: Given BenchmarkPage renders → When the DOM is queried for the Run All, Run Baseline, and Run A/B buttons → Then each button has a non-empty `title` attribute describing its mode, and an info text element is present below the button group explaining when to use A/B comparison

### T-010: Apply visual hierarchy styling to BenchmarkPage button group
**User Story**: US-004 | **Satisfies ACs**: AC-US4-04
**Status**: [x] Completed
**Test**: Given BenchmarkPage renders → When the button group is inspected → Then "Run All" has primary filled CSS class, "Run Baseline" has secondary outline CSS class, and "Run A/B" has accent purple CSS class, with no two buttons sharing the same style variant
