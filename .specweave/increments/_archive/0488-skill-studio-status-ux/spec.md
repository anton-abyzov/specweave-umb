---
increment: 0488-skill-studio-status-ux
title: Fix sidebar status badge contradiction and improve Tests panel UX
status: completed
priority: P1
type: bug
created: 2026-03-11T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Fix Sidebar Status Badge Contradiction and Improve Tests Panel UX

## Problem Statement

The Skill Studio eval-ui has two bugs causing contradictory status display and several UX issues reducing readability in the Tests panel.

**Bug 1 -- False "Passing" badge**: When a test case has zero assertions, `Array.every()` on an empty array returns `true`, setting `status: "pass"`. The sidebar `/api/skills` endpoint then uses this stale case-level status (`benchmark.cases.every(c => c.status === "pass")`) instead of `overall_pass_rate`, so the sidebar shows "Passing" while the header correctly shows "0%". When evals are regenerated with new IDs, `benchmark.json` still references old case IDs, further compounding the stale display.

**UX issues**: Long prompt/expected-output content pushes assertions off-screen with no scroll containment. "Not run yet" assertion indicators (gray circles) are visually indistinct from the background. Overall visual hierarchy needs tightening.

## Goals

- Eliminate contradictory status display between sidebar badge and header pass rate
- Add staleness detection when benchmark references obsolete eval IDs
- Improve Tests panel readability with scroll containment and visual distinction

## User Stories

### US-001: Correct Empty-Assertions Case Status
**Project**: vskill

**As a** skill author
**I want** a test case with zero assertions to report `status: "fail"` (not "pass")
**So that** the sidebar badge never falsely displays "Passing" for untested cases

**Acceptance Criteria**:
- [x] **AC-US1-01**: Given a test case with an empty assertions array, when `runSingleCaseSSE` computes the case status, then `status` is `"fail"` and `pass_rate` is `0`
- [x] **AC-US1-02**: Given a test case with one or more assertions all passing, when the case status is computed, then `status` is `"pass"` (no regression to existing behavior)

---

### US-002: Sidebar Badge Uses Overall Pass Rate
**Project**: vskill

**As a** skill author
**I want** the sidebar benchmark status badge to reflect the actual `overall_pass_rate` from the latest benchmark
**So that** it never contradicts the header pass-rate display

**Acceptance Criteria**:
- [x] **AC-US2-01**: Given a skill with a latest benchmark where `overall_pass_rate` is 0, when the `/api/skills` endpoint computes `benchmarkStatus`, then the status is `"fail"` (not `"pass"`)
- [x] **AC-US2-02**: Given a skill with a latest benchmark where `overall_pass_rate` is 1.0, when the endpoint computes `benchmarkStatus`, then the status is `"pass"`
- [x] **AC-US2-03**: Given a skill whose latest benchmark references case IDs that no longer exist in `evals.json`, when the endpoint computes `benchmarkStatus`, then the status is `"stale"` to signal outdated results

---

### US-003: Tests Panel Scroll Containment
**Project**: vskill

**As a** skill author
**I want** long prompt and expected-output content to be contained within a scrollable area
**So that** assertions and action buttons remain visible without excessive scrolling

**Acceptance Criteria**:
- [x] **AC-US3-01**: Given a prompt longer than 200px of rendered height, when the case detail is displayed, then the prompt section has `max-height` with `overflow-y: auto` and shows a scroll indicator
- [x] **AC-US3-02**: Given an expected-output section longer than 200px, when displayed, then it has the same scroll containment behavior as the prompt section

---

### US-004: Distinct "Not Run" Assertion Indicators
**Project**: vskill

**As a** skill author
**I want** assertions that have not been evaluated to display a visually distinct indicator
**So that** I can immediately distinguish "not run" from "running" or "passed/failed" states

**Acceptance Criteria**:
- [x] **AC-US4-01**: Given an assertion with no result (not yet evaluated), when displayed, then it shows a circle with a dashed border instead of a solid gray fill
- [x] **AC-US4-02**: Given an assertion with a pass/fail result, when displayed, then it continues to show the existing green check or red X icon (no regression)

## Out of Scope

- Refactoring the benchmark persistence format (e.g., migrating away from file-based storage)
- Redesigning the entire Tests panel layout or navigation structure
- Adding new functionality to the eval runner (only fixing existing logic)

## Technical Notes

### Dependencies
- `benchmark-runner.ts` -- case status computation (line 94)
- `api-routes.ts` -- `/api/skills` endpoint `benchmarkStatus` logic (lines 207-209)
- `TestsPanel.tsx` -- `CaseDetail`, `AssertionRow` components
- `SkillListPage.tsx` -- `STATUS_CONFIG` needs a "stale" entry
- `types.ts` -- `benchmarkStatus` union type needs `"stale"` added

### Constraints
- All changes are in the vskill project under `src/eval-server/` and `src/eval-ui/`
- No external API or service changes required

### Architecture Decisions
- Use `overall_pass_rate` as the single source of truth for sidebar badge status, replacing the per-case `status` field check
- Staleness is detected by comparing benchmark case `eval_id` values against current `evals.json` IDs; if any benchmark case references an ID not present in current evals, the benchmark is stale
- Empty assertions edge case is guarded at the source (benchmark-runner) rather than patched downstream

## Success Metrics

- Sidebar badge and header pass rate are always consistent (zero contradictions)
- Stale benchmarks (after eval regeneration) show "stale" instead of false "Passing"
- Prompt/expected-output sections with 500+ character content remain scrollable without pushing assertions off-screen
