---
increment: 0578-fix-eval-comparison-metrics
type: bug-fix
complexity: medium
estimated_tasks: 7
---

# Architecture Plan: Fix Eval Comparison Metrics

## Problem Analysis

Four interconnected bugs in the eval comparison pipeline plus one prompt quality issue:

```
┌─────────────────────────────────────────────────────────────────┐
│  COMPARISON PIPELINE (current broken flow)                      │
│                                                                 │
│  runComparison() ──► skillOutput + baselineOutput               │
│       │                    │              │                      │
│       │            judgeAssertion()    [IGNORED] ◄── Bug 1      │
│       │                    │                                    │
│       │              skillPassRate     baselinePassRate = 0      │
│       │                    │                                    │
│       ▼                    ▼                                    │
│  delta = rubricAvg - rubricAvg  ◄──────────────── Bug 2         │
│       │    (1-5 scale, displayed as %)                          │
│       ▼                                                         │
│  computeVerdict(passRate, skillRubric, baselineRubric)          │
│       │    catch-all: passRate >= 0.4 → INEFFECTIVE ◄── Bug 3  │
│       ▼                                                         │
│  overall_pass_rate = skillPassRate only  ◄────────── Bug 4      │
└─────────────────────────────────────────────────────────────────┘
```

## Architecture Decision: In-Place Fix (No New Components)

All bugs are in existing code paths. No new files, modules, or abstractions needed. Changes are surgical edits to 5 existing files.

**Rationale**: This is a computation correctness fix, not a feature. Adding abstractions would over-engineer the solution. The data flow is correct in structure — just the values and logic within it are wrong.

## Component Changes

### 1. Baseline Assertion Judging (`api-routes.ts`)

**Current** (line 912-932): Single loop judges assertions against `comparison.skillOutput` only.

**Fix**: Add a second judging pass against `comparison.baselineOutput` using the same `judgeAssertion` function.

```
for each assertion:
  skillResult    = judgeAssertion(comparison.skillOutput, assertion, client)
  baselineResult = judgeAssertion(comparison.baselineOutput, assertion, client)
```

**Data structure change** — `comparisonResults` array items gain `baselineAssertionResults`:

```typescript
// Before
{ eval_id, eval_name, comparison, assertionResults }

// After
{ eval_id, eval_name, comparison, assertionResults, baselineAssertionResults }
```

**SSE events**: Add `baseline_assertion_result` event type alongside existing `assertion_result`, emitted after each baseline assertion is judged. This enables the UI to show per-assertion baseline status in the future without blocking this fix.

**Performance note**: This doubles LLM judge calls per comparison. Accepted per spec — comparisons are not latency-critical, and the skill+baseline judge calls for each assertion can run concurrently with `Promise.all`.

### 2. Delta Calculation Fix (`api-routes.ts`)

**Current** (line 1065-1068):
```typescript
baselinePassRate: 0,                           // hardcoded
delta: skillRubricAvg - baselineRubricAvg,     // rubric scale 1-5
```

**Fix**:
```typescript
baselinePassRate: baselinePassRate,             // computed from baseline assertions
delta: passRate - baselinePassRate,             // pass rate scale 0-1
```

Where `baselinePassRate` is computed the same way as `passRate` but from `baselineAssertionResults`:
```typescript
const baselinePassed = comparisonResults.reduce(
  (s, r) => s + r.baselineAssertionResults.filter(a => a.pass).length, 0);
const baselinePassRate = totalAssertions > 0 ? baselinePassed / totalAssertions : 0;
```

The UI code (`RunPanel.tsx:232`) already formats delta correctly for 0-1 scale: `(delta * 100).toFixed(1)%`. No UI change needed for the delta display itself.

### 3. Verdict Logic Redesign (`verdict.ts`)

**Current signature**: `computeVerdict(assertionPassRate, skillRubricAvg, baselineRubricAvg)`

**New signature**: `computeVerdict(assertionPassRate, skillRubricAvg, baselineRubricAvg, baselinePassRate)`

**Decision tree redesign**:

```
                    assertionPassRate >= 0.8?
                    /                      \
                  YES                       NO
                  /                          \
        passRate > baseline + 0.15      assertionPassRate >= 0.5?
        AND rubric > baseline + 1?       /                     \
          /           \                YES                      NO
        YES            NO              /                         \
         |              |      passRate > baseline?       rubric > baseline?
     EFFECTIVE      MARGINAL     /          \              /           \
                               YES           NO          YES           NO
                                |             |           |             |
                            MARGINAL     INEFFECTIVE  EMERGING     DEGRADING
```

Key changes from current logic:
- **EFFECTIVE** requires both high absolute pass rate (>= 0.8) AND meaningful delta over baseline (pass rate > baseline + 0.15) AND rubric advantage (> baseline + 1)
- **INEFFECTIVE** now means "skill doesn't improve over baseline" (correct semantics), not "pass rate is mediocre"
- **MARGINAL** expands to cover "good pass rate, slight improvement" zone
- **Catch-all branch removed** — every path explicitly checks baseline comparison
- 100% pass rate can never hit INEFFECTIVE unless baseline also passes at 100% AND rubric is worse

### 4. RunPanel UI Fix (`RunPanel.tsx`)

**ScoreBar** (lines 226-227): Currently shows `skillPassRate` and `baselinePassRate` from comparison data. Once `baselinePassRate` is computed correctly (not hardcoded to 0), the ScoreBar will display correct values with no code change.

**Delta display** (line 232): Already formats as `(delta * 100).toFixed(1)%` — once delta is pass-rate-based, display is correct. No code change needed.

**Net UI change**: Zero lines changed. The fix is entirely data-side.

### 5. Prompt Improvements (`skill-create-routes.ts`, `prompt-builder.ts`)

Add anti-rigidity guidance to two prompts:

**EVAL_SYSTEM_PROMPT** (`skill-create-routes.ts`): Add after existing assertion rules:
- "Assert on FUNCTIONAL correctness, not formatting"
- "Never assert on: blank lines, paragraph count, whitespace, exact heading levels, bullet formatting"
- "Prefer: semantic presence of content, logical structure, correct data values"

**BEST_PRACTICES** (`prompt-builder.ts`): Add new best practice item:
- "Avoid rigid formatting assertions — test WHAT the output says, not HOW it's formatted"
- Examples of bad vs good assertions

### 6. Existing Test Updates

**`verdict.test.ts`**: Update all `computeVerdict` calls to include 4th parameter (`baselinePassRate`). Add new test cases for baseline-aware logic:
- 100% skill pass rate, 50% baseline → EFFECTIVE
- 80% skill, 80% baseline → MARGINAL (no improvement)
- 30% skill, 70% baseline → DEGRADING
- Equal pass rates, skill rubric better → MARGINAL

**`comparison-sse-events.test.ts`**: Update mocks to include `baselineAssertionResults`. Add test for `baseline_assertion_result` SSE event emission.

## File Impact Summary

| File | Change Type | Lines ~Changed |
|------|------------|---------------|
| `src/eval-server/api-routes.ts` | Bug fix: baseline judging, delta, pass rate | ~40 |
| `src/eval/verdict.ts` | Redesign: add param, new decision tree | ~20 |
| `src/eval/__tests__/verdict.test.ts` | Update: new param, new test cases | ~60 |
| `src/eval-server/__tests__/comparison-sse-events.test.ts` | Update: baseline assertion events | ~30 |
| `src/eval-server/skill-create-routes.ts` | Prompt text addition | ~10 |
| `src/eval/prompt-builder.ts` | Prompt text addition | ~10 |

**Total**: ~170 lines changed across 6 files. No new files.

## Backwards Compatibility

Old history entries have `baselinePassRate: 0` and rubric-based delta. The UI already handles `baselinePassRate: 0` (shows 0% bar) — these entries will simply show the old (incorrect) values. No migration needed. New runs will produce correct data.

## Implementation Order

1. **verdict.ts** — Add `baselinePassRate` param, redesign logic (enables everything else)
2. **verdict.test.ts** — Update tests for new signature and logic
3. **api-routes.ts** — Add baseline assertion judging, fix delta, fix pass rate
4. **comparison-sse-events.test.ts** — Update SSE test mocks
5. **skill-create-routes.ts** — Prompt improvements
6. **prompt-builder.ts** — Prompt improvements

Order rationale: Verdict signature change is the foundation — callers in api-routes.ts depend on it. Tests follow their implementation. Prompt changes are independent and come last.

## Risks & Mitigations

| Risk | Mitigation |
|------|-----------|
| Doubled LLM judge calls | Use `Promise.all` for concurrent skill+baseline judging per assertion |
| Verdict behavior change surprises users | Old history preserved; verdicts only change for new runs |
| `computeVerdict` callers break | Only 1 caller in api-routes.ts; update in same PR |
