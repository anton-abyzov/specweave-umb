---
increment: 0624-studio-comparison-ux-clarity
type: plan
status: draft
---

# Architecture Plan: vSkill Studio Comparison UX Clarity

## Summary

Pure UI + pure-function changes across two files (`verdict.ts`, `RunPanel.tsx`) with tests extended in one existing test file (`verdict.test.ts`). No data model changes, no new dependencies, no new files beyond tests. All data already exists in memory — this is a rendering-only increment.

## Files Modified

| File | Change Type | Lines Affected | ACs Satisfied |
|------|-------------|----------------|---------------|
| `src/eval/verdict.ts` | Add function | +15 lines | AC-US2-05..09, AC-US2-10 |
| `src/eval/__tests__/verdict.test.ts` | Add test suite | +30 lines | AC-US2-05..10 |
| `src/eval-ui/src/pages/workspace/RunPanel.tsx` | Modify | ~80 lines changed | AC-US1-01..05, AC-US2-01..04, AC-US3-01..07 |

## Component Design

### C1: `verdictLabel()` — Pure Mapping Function

**Location**: `src/eval/verdict.ts` (alongside existing `verdictColor()` at line 107)

**Signature**:
```typescript
export function verdictLabel(verdict: string): string
```

**Mapping**:
| Input | Output |
|-------|--------|
| `"EFFECTIVE"` | `"Strong Improvement"` |
| `"MARGINAL"` | `"Moderate Improvement"` |
| `"EMERGING"` | `"Early Promise"` |
| `"INEFFECTIVE"` | `"Needs Work"` |
| `"DEGRADING"` | `"Regression"` |
| anything else | raw string passthrough |

**Design decisions**:
- Accepts `string` (not `EvalVerdict`) because `latestBenchmark.verdict` is typed as `string | undefined` in `BenchmarkResult` (types.ts:114). Casting at the call site would add unnecessary coupling.
- Uses a `Record<string, string>` lookup with fallback — simpler than a switch and handles unknown verdicts gracefully per spec edge case.
- Placed in `verdict.ts` for cohesion with `verdictColor()` and `verdictExplanation()`. Not in `verdict-styles.ts` because that file is UI-specific and already has a `label` field in `VERDICT_STYLES` which maps to Title Case versions of the enum names (e.g., "Effective", "Marginal") — different from the user-friendly labels specified here.

**TDD**: Write failing tests first mapping each EvalVerdict + unknown fallback.

### C2: Dynamic Pass Rate Label

**Location**: `RunPanel.tsx` lines 217-219 (summary card)

**Current**: Hardcoded `"Overall Pass Rate"`

**New logic**:
```typescript
function passRateLabel(type?: string): string {
  if (type === "baseline") return "Baseline Pass Rate";
  return "Skill Pass Rate"; // covers "benchmark", "comparison", undefined
}
```

Inline helper at top of RunPanel — not exported, single-use. Called as `passRateLabel(latestBenchmark.type)`.

**ACs**: AC-US1-01 (comparison -> "Skill Pass Rate"), AC-US1-02 (baseline -> "Baseline Pass Rate"), AC-US1-03 (benchmark/undefined -> "Skill Pass Rate").

### C3: Comparison Provenance Line

**Location**: `RunPanel.tsx` lines 267-269 (inside comparison section, below "Skill vs Baseline" header)

**Data sources**: `latestBenchmark.model` (string), `latestBenchmark.timestamp` (ISO string) — both already loaded.

**Format**: `"claude-sonnet-4-5 · Mar 19, 2026 7:30 PM"`

**Implementation**:
- Format timestamp with `new Date(ts).toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric", hour: "numeric", minute: "2-digit" })`.
- If both model and timestamp are falsy, hide the line entirely.
- If only one is present, show only that field (no dangling separator).
- Styled as `text-[10px]` with `color: var(--text-tertiary)` — matches existing provenance patterns in the summary section (line 232-238).

**AC**: AC-US1-04.

### C4: Human-Readable Delta Statement

**Location**: `RunPanel.tsx` below the delta line (~line 279)

**Data sources**:
- `latestBenchmark.comparison.delta` — rate difference (0-1)
- `latestBenchmark.cases` — to compute total assertion count

**Computation**:
```typescript
const totalAssertions = latestBenchmark.cases.reduce((s, c) => s + c.assertions.length, 0);
const assertionDiff = Math.round(Math.abs(comparison.delta) * totalAssertions);
const caseCount = latestBenchmark.cases.length;
```

**Variants**:
| Condition | Text |
|-----------|------|
| `delta > 0` | `"Your skill passes {N} more assertions across {M} test cases"` |
| `delta < 0` | `"Your skill passes {N} fewer assertions across {M} test cases"` |
| `delta === 0` | `"Your skill performs the same as the baseline across {M} test cases"` |

**Styling**: `text-[11px]`, `color: var(--text-tertiary)`, `mt-1`.

**AC**: AC-US1-05 (positive delta). Spec edge cases cover zero and negative.

### C5: Button Relabeling + Tooltips

**Location**: `RunPanel.tsx` lines 124-132 (bulk buttons)

**Changes**:

| Current Label | New Label | `title` Tooltip |
|---------------|-----------|-----------------|
| `"Compare All"` | `"Run A/B Test"` | `"Runs both your skill and the baseline, then compares results side by side"` |
| `"Skill Only"` | `"Test Skill"` | `"Runs benchmark using your skill only"` |
| `"Baseline Only"` | `"Test Baseline"` | `"Runs benchmark using the baseline (no skill) for reference"` |

Per-case buttons (`"Compare"`, `"Skill"`, `"Base"` at lines 356-358) remain unchanged per spec Out of Scope.

**Implementation**: Add `title` attribute to each `<button>`. Native HTML tooltip — no library needed per spec constraint.

**ACs**: AC-US2-01..04.

### C6: Verdict Label in Comparison Section

**Location**: `RunPanel.tsx` line 278

**Current**: `{latestBenchmark.verdict && ` | ${latestBenchmark.verdict}`}`

**New**: `{latestBenchmark.verdict && ` | ${verdictLabel(latestBenchmark.verdict)}`}`

**Import**: Add `import { verdictLabel } from "../../../../eval/verdict.js"` at top of RunPanel.tsx.

**ACs**: AC-US2-05..09 (label mapping applied at render site).

### C7: Per-Case ComparisonDetail Row

**Location**: `RunPanel.tsx` inside `RunCaseCard` component, below the assertions section (after line 428)

**Data flow**:
1. `RunPanel` already finds `benchCase` per case (line 186): `latestBenchmark?.cases.find((bc) => bc.eval_id === c.id)`
2. Pass `comparisonDetail={benchCase?.comparisonDetail}` as new prop to `RunCaseCard`
3. In `RunCaseCard`, render a comparison row when `comparisonDetail` is defined

**Rendered content** (when `comparisonDetail` is present):
```
Content: Skill 85% / Baseline 60%
Structure: Skill 90% / Baseline 70%
[Winner badge]
```

**Winner badge styling**:
| Winner | Label | Color |
|--------|-------|-------|
| `"skill"` | `"Skill wins"` | `var(--accent)` |
| `"baseline"` | `"Baseline wins"` | `var(--text-tertiary)` |
| `"tie"` | `"Tie"` | `var(--text-tertiary)` |

**Styling**: Uses existing CSS variables. Row styled with `px-4 pb-3` container (matching assertions section pattern), `text-[11px]` size, `bg: var(--surface-2)` rounded inner container for visual distinction.

**Prop addition to RunCaseCard**:
```typescript
comparisonDetail?: ComparisonCaseDetail;
```

Import `ComparisonCaseDetail` from `../../types`.

**ACs**: AC-US3-01..07.

## Implementation Order

The order is designed for TDD (red-green-refactor) and minimal merge conflicts:

1. **T-001**: `verdictLabel()` + tests (verdict.ts, verdict.test.ts) — pure function, zero UI coupling
2. **T-002**: Dynamic pass rate label (RunPanel.tsx summary section)
3. **T-003**: Comparison provenance line (RunPanel.tsx comparison section)
4. **T-004**: Human-readable delta statement (RunPanel.tsx comparison section)
5. **T-005**: Button relabeling + tooltips (RunPanel.tsx controls section)
6. **T-006**: Verdict label rendering (RunPanel.tsx comparison section — uses C1)
7. **T-007**: Per-case comparisonDetail rendering (RunPanel.tsx RunCaseCard)

Tasks 2-6 can be combined into fewer commits since they all touch RunPanel.tsx, but are separated for TDD granularity.

## Testing Strategy

### Unit Tests (Vitest)

- **verdict.test.ts**: New `describe("verdictLabel")` block — 7 test cases (5 known verdicts + unknown fallback + undefined-safe behavior)
- **RunPanel rendering**: The UI changes are best validated via the existing workspace test patterns using mocked `useWorkspace()` context. Key assertions:
  - Summary card label changes based on `latestBenchmark.type`
  - Button text and `title` attributes
  - Provenance line appears when model/timestamp exist
  - ComparisonDetail row appears/hides based on data presence

### Test File Locations

| Test | File |
|------|------|
| `verdictLabel()` | `src/eval/__tests__/verdict.test.ts` (extend existing) |
| RunPanel UI | `src/eval-ui/src/pages/workspace/__tests__/RunPanel.test.tsx` (new file — no existing RunPanel tests) |

## Constraints & Non-Goals

- **No new dependencies** — native `title` for tooltips, `Date` API for formatting
- **No data model changes** — `ComparisonCaseDetail`, `BenchmarkResult.type`, `BenchmarkResult.timestamp`, `BenchmarkResult.model` all exist
- **No changes to `computeVerdict()` logic** — only adding a display mapper
- **No History tab changes** — Phase 2
- **`VERDICT_STYLES` unchanged** — its `label` field serves a different purpose (title-cased enum names for the RunningVerdictBar pill badge)

## Risk Mitigations

- **Button label confusion**: Tooltips explain each mode; new labels are strictly more descriptive
- **Verdict label disagreement**: Labels map to algorithm-computed tiers, not raw delta. `verdictLabel()` is pure and easily adjustable if labels need tuning post-release
- **Timestamp formatting**: Using `toLocaleDateString` with explicit options ensures consistent output across locales
