# Architecture Plan: Benchmark Comparison UX Improvements

## Overview

Four client-heavy improvements to the vskill Studio benchmark/comparison workflow. No server-side SSE format changes. One server-side change: add EMERGING tier to `verdict.ts`. Everything else is React UI work.

## Decision Log

### D-001: Client-Side Progressive Summary (no server changes)

The SSE stream already emits `outputs_ready` (with rubric scores) and `assertion_result` (with pass/fail) per case, followed by `case_complete`. The progressive summary can be computed entirely client-side by accumulating these events.

**Approach**: New `useProgressiveSummary` hook that derives running totals from the existing `events` array in ComparisonPage. No new SSE event types needed.

**Trade-off**: Client-side computation means re-deriving on every render. With up to 200 cases and ~4 assertions each, this is ~800 items -- trivially fast. If flicker occurs from rapid SSE bursts, use `useDeferredValue` (React 18+) rather than debounce, to avoid artificial latency.

### D-002: EMERGING Verdict Tier -- Shared Logic

The EMERGING tier must be recognized in three places: `verdict.ts` (computation), `ComparisonPage.tsx` (display styles), and the progressive summary. Rather than duplicating the style map, extract `VERDICT_STYLES` to a shared `verdict-styles.ts` module that both the final verdict card and the running verdict bar consume.

**Type change**: `EvalVerdict = "EFFECTIVE" | "MARGINAL" | "INEFFECTIVE" | "EMERGING" | "DEGRADING"` -- this is a breaking change for any code that exhaustively switches on the type. The `verdictColor` function and all `switch`/`Record` maps must be updated.

### D-003: Per-Case Fix Button -- Navigation Strategy

The improve endpoint already accepts `eval_id` to scope failures. The per-case Fix button navigates to `/workspace/{plugin}/{skill}?improve=true&eval_id={id}&notes={context}`, matching the existing `ActionItemsPanel.handleApplyFix` pattern. No new API endpoints needed.

**Placement**: Inside each comparison card, below the assertions section, only when failing assertions exist. This avoids cluttering passing cards.

### D-004: Button Tooltips -- Native Title vs Custom Component

For P2 button tooltips, use native `title` attribute. Custom tooltip components add complexity for minimal UX gain on desktop-only buttons. The spec does not require hover animations or positioned popovers.

## Component Architecture

```
ComparisonPage.tsx (modified)
  |
  +-- RunningVerdictBar (NEW)          <-- US-001: progressive summary
  |     reads: completedCases, totalCases, runningSkillAvg, runningBaselineAvg, previewVerdict
  |     uses: computeVerdict() from verdict.ts
  |
  +-- ComparisonCard (extracted)       <-- US-002: per-case Fix button
  |     existing card markup extracted into component
  |     +-- PerCaseFix (NEW)           <-- conditional on failing assertions
  |           navigates to /workspace/:plugin/:skill?improve=true&eval_id=X
  |
  +-- ActionItemsPanel (existing)      <-- unchanged
  +-- GroupedBarChart (existing)       <-- unchanged

BenchmarkPage.tsx (modified)
  +-- Button group                     <-- US-004: tooltips + visual hierarchy
        Run All: btn-primary (filled)  -- already has this
        Run Baseline: btn-ghost with secondary outline styling
        Run A/B: btn-purple            -- already has this

verdict.ts (modified)
  +-- EvalVerdict type                 <-- add "EMERGING"
  +-- computeVerdict()                 <-- add EMERGING branch
  +-- verdictColor()                   <-- add EMERGING color

verdict-styles.ts (NEW, shared)
  +-- VERDICT_STYLES map               <-- extracted from ComparisonPage, add EMERGING
```

## Data Flow: Progressive Summary

```
SSE Stream
  |
  v
useSSE hook (existing, accumulates events[])
  |
  v
ComparisonPage derives from events[]:
  1. comparisons[] -- from outputs_ready events (has rubric scores)
  2. assertionResults per case -- from assertion_result events
  3. caseCompleteEvents[] -- from case_complete events (has pass_rate)
  |
  v
useMemo: computeProgressiveSummary(comparisons, caseCompletes, totalCases)
  returns: { completedCount, totalCount, skillAvg, baselineAvg, delta, previewVerdict }
  |
  v
<RunningVerdictBar /> -- renders when running && completedCount > 0
  transitions to final verdict card when done (seamless: same data shape)
```

## Verdict Logic Change (verdict.ts)

Current logic (4 tiers):
```
passRate >= 0.8 AND skillAvg > baselineAvg + 1  => EFFECTIVE
passRate >= 0.6 AND skillAvg > baselineAvg       => MARGINAL
passRate >= 0.4                                   => INEFFECTIVE
else                                              => DEGRADING
```

New logic (5 tiers -- insert EMERGING before DEGRADING):
```
passRate >= 0.8 AND skillAvg > baselineAvg + 1   => EFFECTIVE
passRate >= 0.6 AND skillAvg > baselineAvg        => MARGINAL
passRate >= 0.4                                    => INEFFECTIVE
passRate < 0.4  AND skillAvg > baselineAvg         => EMERGING
else                                               => DEGRADING
```

This matches the spec: EMERGING = low pass rate but skill outperforms baseline (e.g., baseline=0%, skill=33%). DEGRADING = low pass rate AND skill does not outperform baseline.

## File Changes Summary

| File | Change Type | User Story |
|------|------------|------------|
| `src/eval/verdict.ts` | Modify: add EMERGING tier | US-003 |
| `src/eval-ui/src/utils/verdict-styles.ts` | New: shared VERDICT_STYLES map | US-001, US-003 |
| `src/eval-ui/src/components/RunningVerdictBar.tsx` | New: progressive summary bar | US-001 |
| `src/eval-ui/src/pages/ComparisonPage.tsx` | Modify: integrate RunningVerdictBar, extract VERDICT_STYLES, add per-case Fix, rename Delta to Rubric Delta | US-001, US-002, US-003 |
| `src/eval-ui/src/pages/BenchmarkPage.tsx` | Modify: tooltips, button styling, info text | US-004 |
| `src/eval-ui/src/components/ActionItemsPanel.tsx` | No change | -- |
| `src/eval-server/api-routes.ts` | No change (verdict computed server-side uses same verdict.ts) | US-003 |

## Edge Cases Handled

1. **Zero completed cases**: RunningVerdictBar shows "Comparing... 0/N" placeholder with progress indicator. No verdict preview until at least 1 case completes.

2. **No baseline data (comparison without baseline)**: The `outputs_ready` event always includes baseline scores (the comparison always runs both). If baseline score is 0 across all cases, EMERGING logic triggers correctly.

3. **SSE disconnect mid-run**: The `running` flag stays true until `useSSE` finally block sets it false. Summary freezes at last state. No crash because all derived state is from the immutable events array.

4. **Single case benchmark**: Shows 0/1 then 1/1. useMemo prevents intermediate renders since state transitions atomically.

5. **Rapid SSE events (200+ cases)**: Use `useMemo` with dependency on `events.length` to avoid recomputing on every render. The computation itself is O(N) where N = completed cases, which is trivially fast for 200 items.

6. **All cases pass**: No Fix buttons shown (AC-US2-02). Verdict is EFFECTIVE. RunningVerdictBar transitions cleanly to final verdict.

## Risk Mitigations

| Risk | Mitigation |
|------|-----------|
| Progressive summary flicker on rapid SSE | `useMemo` keyed on events.length; `useDeferredValue` if needed |
| EMERGING tier confusion | Tooltip on EMERGING pill: "Skill shows promise but pass rate is below 40%" |
| Type exhaustiveness broken by new tier | TypeScript compiler catches missing cases in switch/Record; fix all consumers |

## Non-Goals (confirmed from spec)

- No server-side SSE format changes
- No redesign of ActionItemsPanel
- No changes to the improve page itself
- No mobile/responsive changes
- No new verdict tiers beyond EMERGING

## Recommended Domain Skill

The implementation is entirely **React + TypeScript** frontend work (except one shared `verdict.ts` change). Recommend: `frontend:architect` for component design review if needed, but the scope is straightforward enough that direct implementation via `/sw:do` is appropriate.
