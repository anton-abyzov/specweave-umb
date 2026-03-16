# Architecture Plan: 0488-skill-studio-status-ux

## Overview

Fix two bugs causing contradictory status display in the Skill Studio eval-ui, plus UX improvements for scroll containment and visual distinction of "not run" assertion indicators. All changes are scoped to the vskill project under `src/eval-server/` and `src/eval-ui/`.

## Component Map

```
eval-server/
  benchmark-runner.ts   -- Bug 1: empty assertions => false "pass"
  api-routes.ts         -- Bug 2: sidebar status uses stale per-case status

eval-ui/src/
  types.ts              -- Add "stale" to benchmarkStatus union
  pages/SkillListPage.tsx       -- Add "stale" entry to STATUS_CONFIG
  components/SkillCard.tsx      -- Add "stale" entry to STATUS_CONFIG
  pages/workspace/TestsPanel.tsx -- Scroll containment + dashed "not run" indicator
  styles/globals.css             -- Add --orange-muted design token
```

## Changes

### C1: Guard Empty Assertions in benchmark-runner.ts (US-001)

**File**: `src/eval-server/benchmark-runner.ts`, line 94

**Current code (buggy)**:
```ts
const status = assertionResults.every((a) => a.pass) ? "pass" : "fail";
```

`Array.every()` on an empty array returns `true`, so a case with zero assertions gets `status: "pass"` and `pass_rate: 0`. The `pass_rate` is already correctly handled (lines 90-93 return 0 for empty arrays), but `status` contradicts it.

**Fix**: Add an explicit length guard:
```ts
const status = assertionResults.length > 0 && assertionResults.every((a) => a.pass) ? "pass" : "fail";
```

Single-line change. Zero assertions now produce `status: "fail"` and `pass_rate: 0`, both consistent.

**Why fix at the source**: Patching downstream (in api-routes or UI) would leave the contradictory `status` field in `benchmark.json`, causing confusion for any consumer. The runner is the authoritative status producer.

### C2: Sidebar Badge Uses overall_pass_rate + Staleness Detection (US-002)

**File**: `src/eval-server/api-routes.ts`, lines 207-213

**Current code (buggy)**:
```ts
benchmarkStatus: benchmark
  ? benchmark.cases.every((c) => c.status === "pass")
    ? "pass"
    : "fail"
  : s.hasEvals
    ? "pending"
    : "missing",
```

Two problems:
1. Uses per-case `status` field (which can be stale/wrong) instead of `overall_pass_rate`
2. No staleness detection when benchmark references case IDs not in current evals

**Fix**: Extract a helper function:

```ts
function computeBenchmarkStatus(
  benchmark: BenchmarkResult | null,
  hasEvals: boolean,
  currentEvalIds: Set<number>
): "pass" | "fail" | "pending" | "missing" | "stale"
```

Logic:
1. No benchmark + no evals -> `"missing"`
2. No benchmark + has evals -> `"pending"`
3. Benchmark exists but any `case.eval_id` not in `currentEvalIds` -> `"stale"`
4. `overall_pass_rate === 1.0` -> `"pass"`
5. Otherwise -> `"fail"`

The `currentEvalIds` set comes from `loadAndValidateEvals` which is already called at line 198. Extract `new Set(evals.evals.map(e => e.id))` and pass it in.

**Data flow**:
```
loadAndValidateEvals(s.dir) --> evalIds: Set<number>
readBenchmark(s.dir) --------> benchmark: BenchmarkResult | null
                                    |
              computeBenchmarkStatus(benchmark, hasEvals, evalIds)
                                    |
                          "pass" | "fail" | "stale" | "pending" | "missing"
```

### C3: Add "stale" Status to Frontend Types and Config (US-002)

**File**: `src/eval-ui/src/types.ts`, line 31

Add `"stale"` to the `benchmarkStatus` union type:
```ts
benchmarkStatus: "pass" | "fail" | "pending" | "missing" | "stale";
```

**Files**: `src/eval-ui/src/pages/SkillListPage.tsx` and `src/eval-ui/src/components/SkillCard.tsx`

Add `stale` entry to both `STATUS_CONFIG` dictionaries:
```ts
stale: { bg: "var(--orange-muted)", text: "var(--orange)", dot: "var(--orange)", label: "Stale" },
```

**File**: `src/eval-ui/src/styles/globals.css`

Add `--orange-muted` design token (the `--orange` token already exists at line 28):
```css
--orange-muted: rgba(251, 146, 60, 0.12);
```

### C4: Scroll Containment for Prompt and Expected Output (US-003)

**File**: `src/eval-ui/src/pages/workspace/TestsPanel.tsx`

In the `CaseDetail` component, the prompt display div (lines 279-293) and expected-output display div (lines 315-329) both use `whiteSpace: "pre-wrap"` with no height constraint. Long content pushes assertions off-screen.

**Fix**: Add `maxHeight: 200` and `overflowY: "auto"` to both read-only display div style objects. The existing custom scrollbar styles in globals.css (lines 53-56) handle the scroll thumb appearance automatically.

The edit-mode `<textarea>` elements are already height-constrained by their `rows` prop and are not affected.

### C5: Dashed Border "Not Run" Indicator (US-004)

**File**: `src/eval-ui/src/pages/workspace/TestsPanel.tsx`, line 407

**Current code**:
```tsx
<span className="mt-0.5 w-[18px] h-[18px] rounded-full flex-shrink-0"
  style={{ background: "var(--surface-4)" }} />
```

A solid gray circle that is barely visible against the `--surface-2` assertion row background.

**Fix**: Replace with a dashed-border empty circle:
```tsx
<span className="mt-0.5 w-[18px] h-[18px] rounded-full flex-shrink-0"
  style={{
    border: "1.5px dashed var(--text-tertiary)",
    background: "transparent",
  }} />
```

Visual distinction: dashed outline = not run, solid green circle with check = pass, solid red circle with X = fail.

## Dependency Order

```
C1 (benchmark-runner.ts)     -- independent
C2 (api-routes.ts)           -- independent
C3 (types + UI configs)      -- depends on C2 (API must serve "stale" before UI renders it)
C4 (scroll containment)      -- independent
C5 (dashed indicator)        -- independent
```

Recommended implementation order: C1 -> C2 -> C3 -> C4 -> C5.

## Test Strategy

**Unit tests** (Vitest):
- `benchmark-runner.test.ts`: Test `runSingleCaseSSE` with 0 assertions returns `status: "fail"`, `pass_rate: 0`. Test with all-passing assertions returns `status: "pass"` (no regression).
- `computeBenchmarkStatus.test.ts` (or inline in `api-routes.test.ts`): Test the extracted function with: `overall_pass_rate: 0` -> `"fail"`, `overall_pass_rate: 1.0` -> `"pass"`, mismatched eval IDs -> `"stale"`, no benchmark -> `"pending"`/`"missing"`.

**Component tests** (if React Testing Library is in place):
- `AssertionRow`: Verify dashed border renders when no result, green check when pass, red X when fail.

**Manual verification**:
- Regenerate evals (changing IDs), then check sidebar shows "Stale" badge.
- Run a skill with 0 assertions, verify sidebar shows "Failing" not "Passing".
- Add a prompt with 1000+ characters, verify scroll containment.

## No ADRs Required

This increment is a bug fix and targeted UX polish. The changes are localized to existing components with no new abstractions, services, or patterns introduced. The `computeBenchmarkStatus` helper is a simple extraction of inline ternary logic, not a new architectural pattern.

## No Domain Skill Delegation Needed

This is a focused bug fix in an existing React + Node.js codebase. The changes are small (under 50 lines total across all files), well-scoped, and do not require frontend or backend architectural patterns beyond what already exists.
