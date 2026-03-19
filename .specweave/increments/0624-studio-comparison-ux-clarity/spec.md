---
increment: 0624-studio-comparison-ux-clarity
title: vSkill Studio Comparison UX Clarity
type: feature
priority: P1
status: completed
created: 2026-03-19T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: vSkill Studio Comparison UX Clarity

## Problem Statement

The vSkill Studio Run page (`RunPanel.tsx`) displays comparison benchmark results with ambiguous labels, missing provenance, misleading verdict terminology, unclear button purposes, and hidden per-case detail data. Users cannot tell which pass rate belongs to which run, have no context for when/how comparison data was generated, see internal verdict codes like "MARGINAL" instead of user-friendly language, don't understand what the benchmark buttons do, and miss per-case comparison scores that exist in the data but are never rendered.

## Goals

- Make every label on the Run page unambiguous — users instantly know what data they're looking at
- Surface comparison provenance (model, timestamp) so users trust the data
- Replace internal verdict codes with user-friendly language that accurately conveys improvement magnitude
- Make benchmark action buttons self-explanatory with descriptive labels and tooltips
- Render per-case `comparisonDetail` data that's already computed but not displayed

## User Stories

### US-001: Context-Aware Labels & Comparison Provenance (P1)
**Project**: vskill

**As a** skill developer reviewing benchmark results
**I want** the pass rate label to identify which run it represents and the comparison section to show when and how the comparison was produced
**So that** I can trust the displayed data and understand its context without guessing

**Acceptance Criteria**:
- [x] **AC-US1-01**: Given a completed benchmark with `type === "comparison"`, when the summary card renders, then the pass rate label reads "Skill Pass Rate" instead of "Overall Pass Rate"
- [x] **AC-US1-02**: Given a completed benchmark with `type === "baseline"`, when the summary card renders, then the pass rate label reads "Baseline Pass Rate"
- [x] **AC-US1-03**: Given a completed benchmark with `type === "benchmark"` or `type` is undefined, when the summary card renders, then the pass rate label reads "Skill Pass Rate"
- [x] **AC-US1-04**: Given a completed comparison with `latestBenchmark.comparison` present, when the "Skill vs Baseline" section renders, then a provenance line below the section header displays the model name and formatted timestamp (e.g., "claude-sonnet-4-5 · Mar 19, 2026 7:30 PM")
- [x] **AC-US1-05**: Given a completed comparison with `delta > 0`, when the delta line renders, then a human-readable statement appears below it (e.g., "Your skill passes 3 more assertions across 5 test cases")

---

### US-002: Clear Benchmark Controls & Verdict Labels (P1)
**Project**: vskill

**As a** skill developer running benchmarks
**I want** the action buttons to describe what they do and verdict labels to use friendly language
**So that** I can choose the right benchmark mode confidently and interpret results without learning internal terminology

**Acceptance Criteria**:
- [x] **AC-US2-01**: Given the benchmark controls section, when buttons render, then the three bulk buttons read "Run A/B Test", "Test Skill", and "Test Baseline" (replacing "Compare All", "Skill Only", "Baseline Only")
- [x] **AC-US2-02**: Given the "Run A/B Test" button, when the user hovers, then a tooltip displays "Runs both your skill and the baseline, then compares results side by side"
- [x] **AC-US2-03**: Given the "Test Skill" button, when the user hovers, then a tooltip displays "Runs benchmark using your skill only"
- [x] **AC-US2-04**: Given the "Test Baseline" button, when the user hovers, then a tooltip displays "Runs benchmark using the baseline (no skill) for reference"
- [x] **AC-US2-05**: Given a verdict value of "EFFECTIVE", when rendered in the comparison section, then the display text reads "Strong Improvement"
- [x] **AC-US2-06**: Given a verdict value of "MARGINAL", when rendered in the comparison section, then the display text reads "Moderate Improvement"
- [x] **AC-US2-07**: Given a verdict value of "EMERGING", when rendered in the comparison section, then the display text reads "Early Promise"
- [x] **AC-US2-08**: Given a verdict value of "INEFFECTIVE", when rendered in the comparison section, then the display text reads "Needs Work"
- [x] **AC-US2-09**: Given a verdict value of "DEGRADING", when rendered in the comparison section, then the display text reads "Regression"
- [x] **AC-US2-10**: Given the verdict label mapping, when `verdictLabel()` is called from `src/eval/verdict.ts`, then it is a pure function that maps `EvalVerdict` to the user-friendly string with no side effects

---

### US-003: Per-Case Comparison Detail Rendering (P1)
**Project**: vskill

**As a** skill developer analyzing comparison results
**I want** each test case card to show the per-case comparison breakdown (content scores, structure scores, winner)
**So that** I can identify which specific cases my skill excels at or struggles with

**Acceptance Criteria**:
- [x] **AC-US3-01**: Given a `BenchmarkCase` with a non-null `comparisonDetail`, when the case card renders in the results list, then a comparison row is visible below the assertions section
- [x] **AC-US3-02**: Given a visible comparison row, when rendered, then it displays `skillContentScore` and `baselineContentScore` as labeled percentage pairs (e.g., "Content: Skill 85% / Baseline 60%")
- [x] **AC-US3-03**: Given a visible comparison row, when rendered, then it displays `skillStructureScore` and `baselineStructureScore` as labeled percentage pairs (e.g., "Structure: Skill 90% / Baseline 70%")
- [x] **AC-US3-04**: Given a visible comparison row with `winner === "skill"`, when rendered, then a "Skill wins" label is shown in the accent color
- [x] **AC-US3-05**: Given a visible comparison row with `winner === "baseline"`, when rendered, then a "Baseline wins" label is shown in the tertiary text color
- [x] **AC-US3-06**: Given a visible comparison row with `winner === "tie"`, when rendered, then a "Tie" label is shown in the tertiary text color
- [x] **AC-US3-07**: Given a `BenchmarkCase` with `comparisonDetail` undefined or null, when the case card renders, then no comparison row appears

## Out of Scope

- History tab changes — Phase 2
- Chart libraries or data visualization beyond existing bar components
- Database schema changes — all data already exists in `BenchmarkResult` JSON
- New icon libraries or custom SVG icons
- Per-case button changes (the individual case "Compare"/"Skill"/"Base" buttons remain as-is)
- Changes to `computeVerdict()` logic — only adding a display-label mapping function
- Mobile/responsive layout changes
- Internationalization/localization of labels

## Technical Notes

### Dependencies
- `RunPanel.tsx` — main file for all rendering changes (labels, buttons, tooltips, comparison detail)
- `verdict.ts` — add `verdictLabel()` export mapping `EvalVerdict → string`
- `types.ts` — no changes needed, `ComparisonCaseDetail` type already exists (lines 59-73)

### Constraints
- All data for `comparisonDetail` is already computed and present in the `BenchmarkCase` object — no new API calls or data fetching required
- Tooltip implementation must use native `title` attribute or existing CSS tooltip pattern — no new tooltip library

### Architecture Decisions
- `verdictLabel()` lives in `verdict.ts` alongside `computeVerdict()` for cohesion — it's a pure mapping function, not a UI component
- Provenance data (model, timestamp) comes from `latestBenchmark.model` and `latestBenchmark.timestamp` which are already loaded

## Non-Functional Requirements

- **Performance**: No additional API calls — all rendered data is already in memory from existing benchmark results
- **Accessibility**: Tooltips must be accessible via `title` attribute on buttons; comparison scores use sufficient color contrast
- **Compatibility**: Works in all browsers supported by the existing eval-ui (Chromium-based, Firefox, Safari)

## Edge Cases

- **Missing model/timestamp**: If `latestBenchmark.model` or `latestBenchmark.timestamp` is null/undefined, provenance line shows only the available field or is hidden entirely
- **Zero delta**: When `delta === 0`, the human-readable statement reads "Your skill performs the same as the baseline across N test cases"
- **Negative delta**: When `delta < 0`, the human-readable statement reads "Your skill passes N fewer assertions across M test cases"
- **Unknown verdict**: If `verdict` string doesn't match any `EvalVerdict`, `verdictLabel()` returns the raw string as fallback
- **All cases missing comparisonDetail**: When no cases have comparison data, no comparison rows appear — the UI looks identical to a non-comparison run

## Risks

| Risk | Probability | Impact | Severity | Mitigation |
|------|-------------|--------|----------|------------|
| Button label change confuses existing users | 0.3 | 3 | 0.9 | Tooltips explain behavior; labels are more descriptive than before |
| Verdict label disagreement ("Moderate" for +50%) | 0.2 | 2 | 0.4 | Labels map to computed verdict tiers, not raw delta — trust the algorithm |

## Success Metrics

- Every label on the Run page is unambiguous — no user needs to guess what a number represents
- `comparisonDetail` data is visible for all cases that have it
- Zero new runtime errors from null/undefined edge cases
