---
increment: 0624-studio-comparison-ux-clarity
type: tasks
status: active
tdd_mode: strict
---

# Tasks: vSkill Studio Comparison UX Clarity

## US-001: Context-Aware Labels & Comparison Provenance

### T-001: verdictLabel() Pure Function + Tests
**User Story**: US-002 | **Satisfies ACs**: AC-US2-05, AC-US2-06, AC-US2-07, AC-US2-08, AC-US2-09, AC-US2-10
**Status**: [ ] Not Started

**Files**:
- `repositories/anton-abyzov/vskill/src/eval/verdict.ts` — add `verdictLabel()` export
- `repositories/anton-abyzov/vskill/src/eval/__tests__/verdict.test.ts` — extend with new `describe("verdictLabel")` block

**TDD Cycle**: RED first — write 7 failing tests, then GREEN — implement, then REFACTOR.

**Test Plan**:
- Given `verdictLabel("EFFECTIVE")` is called → When function executes → Then returns `"Strong Improvement"`
- Given `verdictLabel("MARGINAL")` is called → When function executes → Then returns `"Moderate Improvement"`
- Given `verdictLabel("EMERGING")` is called → When function executes → Then returns `"Early Promise"`
- Given `verdictLabel("INEFFECTIVE")` is called → When function executes → Then returns `"Needs Work"`
- Given `verdictLabel("DEGRADING")` is called → When function executes → Then returns `"Regression"`
- Given `verdictLabel("UNKNOWN_CODE")` is called with an unrecognized verdict → When function executes → Then returns `"UNKNOWN_CODE"` (raw passthrough)
- Given `verdictLabel` is imported → When inspected → Then it is a pure function with no side effects (no I/O, no state mutation)

**Implementation Notes**:
- Use `Record<string, string>` lookup with fallback: `return MAP[verdict] ?? verdict`
- Accepts `string` (not `EvalVerdict`) because `BenchmarkResult.verdict` is typed `string | undefined`
- Place after existing `verdictColor()` at line 107 of `verdict.ts`
- Run: `cd repositories/anton-abyzov/vskill && npx vitest run src/eval/__tests__/verdict.test.ts`

---

### T-002: Dynamic Pass Rate Label Based on Benchmark Type
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03
**Status**: [ ] Not Started

**Files**:
- `repositories/anton-abyzov/vskill/src/eval-ui/src/pages/workspace/RunPanel.tsx` — replace hardcoded "Overall Pass Rate"
- `repositories/anton-abyzov/vskill/src/eval-ui/src/pages/workspace/__tests__/RunPanel.test.tsx` — NEW file, create with label assertions

**TDD Cycle**: RED first — write 3 failing render tests, then GREEN — add `passRateLabel()` helper + replace hardcoded label, then REFACTOR.

**Test Plan**:
- Given `latestBenchmark.type === "comparison"` → When `RunPanel` renders the summary card → Then the pass rate label reads `"Skill Pass Rate"`
- Given `latestBenchmark.type === "baseline"` → When `RunPanel` renders the summary card → Then the pass rate label reads `"Baseline Pass Rate"`
- Given `latestBenchmark.type === "benchmark"` (or `type` is `undefined`) → When `RunPanel` renders the summary card → Then the pass rate label reads `"Skill Pass Rate"`

**Implementation Notes**:
- Add inline helper at top of RunPanel (not exported, single-use):
  ```typescript
  function passRateLabel(type?: string): string {
    if (type === "baseline") return "Baseline Pass Rate";
    return "Skill Pass Rate";
  }
  ```
- Replace `"Overall Pass Rate"` at ~line 217-219 with `{passRateLabel(latestBenchmark?.type)}`
- Run: `cd repositories/anton-abyzov/vskill && npx vitest run src/eval-ui/src/pages/workspace/__tests__/RunPanel.test.tsx`

---

### T-003: Comparison Provenance Line (Model + Timestamp)
**User Story**: US-001 | **Satisfies ACs**: AC-US1-04
**Status**: [ ] Not Started

**Files**:
- `repositories/anton-abyzov/vskill/src/eval-ui/src/pages/workspace/RunPanel.tsx` — insert provenance line in comparison section
- `repositories/anton-abyzov/vskill/src/eval-ui/src/pages/workspace/__tests__/RunPanel.test.tsx` — extend with provenance assertions

**TDD Cycle**: RED first — write failing tests for provenance rendering, then GREEN — implement, then REFACTOR.

**Test Plan**:
- Given `latestBenchmark.comparison` is present, `model = "claude-sonnet-4-5"`, `timestamp = "2026-03-19T19:30:00Z"` → When `RunPanel` renders the "Skill vs Baseline" section → Then a provenance line appears with text matching `"claude-sonnet-4-5 · Mar 19, 2026"`
- Given `latestBenchmark.model` is null but `timestamp` is present → When provenance line renders → Then only the formatted timestamp is shown (no dangling `·` separator)
- Given both `latestBenchmark.model` and `latestBenchmark.timestamp` are null/undefined → When the comparison section renders → Then no provenance line appears at all

**Implementation Notes**:
- Format: `new Date(ts).toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric", hour: "numeric", minute: "2-digit" })`
- Build `parts = [model, formattedDate].filter(Boolean).join(" · ")` — handles partial data
- Style: `text-[10px]` + `color: var(--text-tertiary)` below "Skill vs Baseline" header (~line 267-269)
- Run: `cd repositories/anton-abyzov/vskill && npx vitest run src/eval-ui/src/pages/workspace/__tests__/RunPanel.test.tsx`

---

### T-004: Human-Readable Delta Statement
**User Story**: US-001 | **Satisfies ACs**: AC-US1-05
**Status**: [ ] Not Started

**Files**:
- `repositories/anton-abyzov/vskill/src/eval-ui/src/pages/workspace/RunPanel.tsx` — insert delta statement below delta line
- `repositories/anton-abyzov/vskill/src/eval-ui/src/pages/workspace/__tests__/RunPanel.test.tsx` — extend with delta statement assertions

**TDD Cycle**: RED first — write 3 failing tests (positive/zero/negative delta), then GREEN — implement, then REFACTOR.

**Test Plan**:
- Given `comparison.delta > 0` (e.g., `delta = 0.6`) and 5 cases each with 1 assertion → When delta line renders → Then statement reads `"Your skill passes 3 more assertions across 5 test cases"`
- Given `comparison.delta === 0` and 4 cases → When delta line renders → Then statement reads `"Your skill performs the same as the baseline across 4 test cases"`
- Given `comparison.delta < 0` (e.g., `delta = -0.4`) and 5 cases each with 2 assertions → When delta line renders → Then statement reads `"Your skill passes 4 fewer assertions across 5 test cases"`

**Implementation Notes**:
- Compute: `totalAssertions = cases.reduce((s,c) => s + c.assertions.length, 0)`
- Compute: `assertionDiff = Math.round(Math.abs(delta) * totalAssertions)`
- Variants: positive = "more", negative = "fewer", zero = "performs the same as the baseline"
- Style: `text-[11px]`, `color: var(--text-tertiary)`, `mt-1`, placed below delta line (~line 279)
- Run: `cd repositories/anton-abyzov/vskill && npx vitest run src/eval-ui/src/pages/workspace/__tests__/RunPanel.test.tsx`

---

## US-002: Clear Benchmark Controls & Verdict Labels

### T-005: Button Relabeling + Title Tooltips
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04
**Status**: [ ] Not Started

**Files**:
- `repositories/anton-abyzov/vskill/src/eval-ui/src/pages/workspace/RunPanel.tsx` — update bulk button labels and add `title` attributes
- `repositories/anton-abyzov/vskill/src/eval-ui/src/pages/workspace/__tests__/RunPanel.test.tsx` — extend with button label and title assertions

**TDD Cycle**: RED first — write 6 failing tests (3 labels + 3 titles), then GREEN — update JSX, then REFACTOR.

**Test Plan**:
- Given the benchmark controls section renders → When querying button text → Then buttons read `"Run A/B Test"`, `"Test Skill"`, and `"Test Baseline"` (not "Compare All", "Skill Only", "Baseline Only")
- Given the `"Run A/B Test"` button renders → When inspecting `title` attribute → Then it equals `"Runs both your skill and the baseline, then compares results side by side"`
- Given the `"Test Skill"` button renders → When inspecting `title` attribute → Then it equals `"Runs benchmark using your skill only"`
- Given the `"Test Baseline"` button renders → When inspecting `title` attribute → Then it equals `"Runs benchmark using the baseline (no skill) for reference"`
- Given per-case buttons (`"Compare"`, `"Skill"`, `"Base"`) → When rendered → Then their labels are unchanged (out of scope)

**Implementation Notes**:
- Target: `RunPanel.tsx` lines 124-132 (bulk buttons)
- Add `title="..."` native HTML attribute to each `<button>` — no tooltip library
- Do NOT change per-case buttons at lines 356-358
- Run: `cd repositories/anton-abyzov/vskill && npx vitest run src/eval-ui/src/pages/workspace/__tests__/RunPanel.test.tsx`

---

### T-006: Verdict Label Rendering Using verdictLabel()
**User Story**: US-002 | **Satisfies ACs**: AC-US2-05, AC-US2-06, AC-US2-07, AC-US2-08, AC-US2-09
**Status**: [ ] Not Started

**Files**:
- `repositories/anton-abyzov/vskill/src/eval-ui/src/pages/workspace/RunPanel.tsx` — replace raw verdict string with `verdictLabel()` call
- `repositories/anton-abyzov/vskill/src/eval-ui/src/pages/workspace/__tests__/RunPanel.test.tsx` — extend with verdict display assertions

**TDD Cycle**: RED first — write 5 failing render tests (one per verdict), then GREEN — add import + replace render site, then REFACTOR.

**Prerequisite**: T-001 must be complete (verdictLabel exported from verdict.ts).

**Test Plan**:
- Given `latestBenchmark.verdict === "EFFECTIVE"` → When comparison section renders → Then displayed text contains `"Strong Improvement"` (not `"EFFECTIVE"`)
- Given `latestBenchmark.verdict === "MARGINAL"` → When comparison section renders → Then displayed text contains `"Moderate Improvement"`
- Given `latestBenchmark.verdict === "EMERGING"` → When comparison section renders → Then displayed text contains `"Early Promise"`
- Given `latestBenchmark.verdict === "INEFFECTIVE"` → When comparison section renders → Then displayed text contains `"Needs Work"`
- Given `latestBenchmark.verdict === "DEGRADING"` → When comparison section renders → Then displayed text contains `"Regression"`

**Implementation Notes**:
- Add import: `import { verdictLabel } from "../../../../eval/verdict.js"` at top of RunPanel.tsx
- Replace at ~line 278: `` `| ${latestBenchmark.verdict}` `` → `` `| ${verdictLabel(latestBenchmark.verdict)}` ``
- Run: `cd repositories/anton-abyzov/vskill && npx vitest run src/eval-ui/src/pages/workspace/__tests__/RunPanel.test.tsx`

---

## US-003: Per-Case Comparison Detail Rendering

### T-007: Per-Case ComparisonDetail Row in RunCaseCard
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04, AC-US3-05, AC-US3-06, AC-US3-07
**Status**: [ ] Not Started

**Files**:
- `repositories/anton-abyzov/vskill/src/eval-ui/src/pages/workspace/RunPanel.tsx` — pass `comparisonDetail` prop to `RunCaseCard`, render comparison row in `RunCaseCard`
- `repositories/anton-abyzov/vskill/src/eval-ui/src/pages/workspace/__tests__/RunPanel.test.tsx` — extend with comparisonDetail row assertions

**TDD Cycle**: RED first — write 7 failing render tests (presence, scores, winners, absence), then GREEN — add prop + render row, then REFACTOR.

**Test Plan**:
- Given a `BenchmarkCase` with `comparisonDetail` non-null → When the case card renders → Then a comparison row is visible below the assertions section
- Given a visible comparison row with `skillContentScore=0.85`, `baselineContentScore=0.60` → When rendered → Then text includes `"Content: Skill 85% / Baseline 60%"`
- Given a visible comparison row with `skillStructureScore=0.90`, `baselineStructureScore=0.70` → When rendered → Then text includes `"Structure: Skill 90% / Baseline 70%"`
- Given a visible comparison row with `winner === "skill"` → When rendered → Then `"Skill wins"` label appears with `color: var(--accent)` styling
- Given a visible comparison row with `winner === "baseline"` → When rendered → Then `"Baseline wins"` label appears with `color: var(--text-tertiary)` styling
- Given a visible comparison row with `winner === "tie"` → When rendered → Then `"Tie"` label appears with `color: var(--text-tertiary)` styling
- Given a `BenchmarkCase` with `comparisonDetail` undefined or null → When the case card renders → Then no comparison row appears

**Implementation Notes**:
- In `RunPanel`: `benchCase` already found at line 186 — add `comparisonDetail={benchCase?.comparisonDetail}` prop to `<RunCaseCard>`
- Add prop to `RunCaseCard`: `comparisonDetail?: ComparisonCaseDetail`
- Import: `import type { ComparisonCaseDetail } from "../../types"` in RunPanel.tsx
- Render row only when `comparisonDetail` is defined (guard with `&&`)
- Scores displayed as percentages: `Math.round(score * 100)`
- Container style: `px-4 pb-3`, inner row `bg: var(--surface-2)` rounded, `text-[11px]`
- Winner badge uses inline `style={{ color: winner === "skill" ? "var(--accent)" : "var(--text-tertiary)" }}`
- Run: `cd repositories/anton-abyzov/vskill && npx vitest run src/eval-ui/src/pages/workspace/__tests__/RunPanel.test.tsx`

---

## AC Coverage Map

| AC ID | Task | Status |
|-------|------|--------|
| AC-US1-01 | T-002 | [ ] |
| AC-US1-02 | T-002 | [ ] |
| AC-US1-03 | T-002 | [ ] |
| AC-US1-04 | T-003 | [ ] |
| AC-US1-05 | T-004 | [ ] |
| AC-US2-01 | T-005 | [ ] |
| AC-US2-02 | T-005 | [ ] |
| AC-US2-03 | T-005 | [ ] |
| AC-US2-04 | T-005 | [ ] |
| AC-US2-05 | T-001, T-006 | [ ] |
| AC-US2-06 | T-001, T-006 | [ ] |
| AC-US2-07 | T-001, T-006 | [ ] |
| AC-US2-08 | T-001, T-006 | [ ] |
| AC-US2-09 | T-001, T-006 | [ ] |
| AC-US2-10 | T-001 | [ ] |
| AC-US3-01 | T-007 | [ ] |
| AC-US3-02 | T-007 | [ ] |
| AC-US3-03 | T-007 | [ ] |
| AC-US3-04 | T-007 | [ ] |
| AC-US3-05 | T-007 | [ ] |
| AC-US3-06 | T-007 | [ ] |
| AC-US3-07 | T-007 | [ ] |
