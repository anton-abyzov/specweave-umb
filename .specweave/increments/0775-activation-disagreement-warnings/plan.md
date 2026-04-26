# Implementation Plan: Re-score activation-tester disagreements as warnings

## Overview

Pure scoring-logic + UI badge change in the vskill CLI repo. No new modules. No new dependencies. No server-route shape change. Three files touched (one source, one test, one UI), plus a bundle rebuild.

## Architecture

### Components

| File | Role | Change |
|---|---|---|
| `repositories/anton-abyzov/vskill/src/eval/activation-tester.ts` | Scoring engine | Add `Verdict` type, `computeVerdict()` helper. Extend `ActivationResult`/`ActivationSummary`. Update `testActivation()` to set `verdict` on each result. Update `computeSummary()` to count warnings and exclude them from `tp`/`tn`/`fp`/`fn`. |
| `repositories/anton-abyzov/vskill/src/eval/__tests__/activation-tester.test.ts` | Vitest unit tests | Add 4 RED tests for the new scoring rules. |
| `repositories/anton-abyzov/vskill/src/eval-ui/src/pages/workspace/ActivationPanel.tsx` | Trigger-tab UI | Add yellow `SCOPE_WARNING` / `DRIFT_WARNING` styles. Switch row badge to `verdict !== "ok"` priority over `classification`. Render warnings sub-row in confusion matrix. Filter warnings out of "Incorrect" callout. |

### Data Model

```ts
// New
export type Verdict = "ok" | "scope_warning" | "drift_warning";

// Extended
export interface ActivationResult {
  prompt: string;
  expected: "should_activate" | "should_not_activate";
  activate: boolean;
  confidence: "high" | "medium" | "low";
  reasoning: string;
  classification: "TP" | "TN" | "FP" | "FN"; // unchanged
  autoClassified?: boolean;
  verdict: Verdict; // NEW
}

// Extended
export interface ActivationSummary {
  results: ActivationResult[];
  precision: number;
  recall: number;
  reliability: number;
  total: number;
  tp: number; tn: number; fp: number; fn: number; // counts now exclude verdict !== "ok"
  scopeWarnings: number; // NEW
  driftWarnings: number; // NEW
  autoClassifiedCount: number;
}
```

### API Contracts

`/activation-test` SSE route at `src/eval-server/api-routes.ts:3309-3354` — **no contract change**. Final `done` event already serializes the full `ActivationSummary` via `sendSSEDone(res, { ...summary, description })`. New fields propagate automatically.

## Technology Stack

- **Language**: TypeScript (NodeNext module resolution, `.js` import extensions required per vskill convention).
- **Test framework**: Vitest, existing `mockClient(responses: string[])` factory pattern.
- **UI**: React + CSS variables (no new deps). Existing `var(--yellow)` / `var(--yellow-muted)` design tokens reused.

**Architecture Decisions**:
- **Add `verdict` field rather than expanding `classification` enum**: keeps backward compat for any consumer that depends on the 4-letter classification (debugging, logs, future analytics). Verdict is a parallel axis: "is this row a real win/loss or a soft warning?"
- **Only auto-classified rows can be warnings**: manual `+`/`!` prefixes signal user authority — disagreements there are real bugs, not classifier noise. Gating verdict on `autoClassified === true` aligns the data model with the design intent of 0472 (auto-classification is heuristic; manual is ground truth).
- **Keep `classification` populated even when verdict is a warning**: useful for the UI to show diagnostic context ("this would have been an FP under strict scoring") without making it the headline.

## Implementation Phases

### Phase 1: TDD RED — failing tests
Write 4 new vitest cases in `__tests__/activation-tester.test.ts`:
- `T-001` — auto-classified scope_warning bucket
- `T-002` — auto-classified drift_warning bucket
- `T-003` — manual disagreement remains FP
- `T-004` — precision denominator excludes warnings

Run `npx vitest run src/eval/__tests__/activation-tester.test.ts` — confirm 4 fails.

### Phase 2: TDD GREEN — implement scoring
- Add `Verdict` type export.
- Add `computeVerdict()` helper.
- Extend `ActivationResult` and `ActivationSummary`.
- Wire `verdict` into both happy-path and error-path result construction (lines ~153 and ~165 in current file).
- Update `computeSummary()` to count warnings and exclude them from `tp/tn/fp/fn`.

Run vitest — all 4 RED tests + existing tests pass.

### Phase 3: UI rendering
- Add `SCOPE_WARNING`/`DRIFT_WARNING` to `CLASSIFICATION_STYLES` (yellow tones).
- In the result row, when `result.verdict !== "ok"`, render a yellow pill labeled "scope warn" or "drift warn" instead of the red FP/FN pill.
- Render a `Warnings: N scope, M drift` sub-row beneath the 4-cell confusion matrix.
- Filter the "Incorrect" list at the top of the panel to `result.classification ∈ {FP, FN} && result.verdict === "ok"`.
- Tooltip strings on hover for both warning types.

### Phase 4: Build + smoke test
- `npm run build:eval-ui` — confirm clean bundle.
- Local studio: launch eval-server.ts, point at `hello-skill`, exercise three prompt forms (auto, `+`, `!`), confirm UI matches AC-US3-01..04.

## Testing Strategy

- **Unit (vitest)**: 4 new tests for the scoring rules; existing 8+ tests must still pass (verdict added with default `"ok"` so no breakage).
- **Integration**: not needed — server route is unchanged, SSE shape is automatically extended.
- **E2E (manual smoke)**: studio screenshot comparison on the three prompt variants.
- **Coverage target**: 90% on the modified file (existing coverage already high; new helper is small).

## Technical Challenges

### Challenge 1: UI bundle rebuild required for studio to pick up changes
**Solution**: per memory `project_vskill_studio_runtime`, the studio runtime is `eval-server.ts` serving a pre-built bundle from `dist/eval-ui`. Run `npm run build:eval-ui` after UI edits.
**Risk**: forgetting the rebuild → smoke test shows old behavior. Mitigation: build step is an explicit task (T-008).

### Challenge 2: Tests must use the existing `mockClient` factory pattern
**Solution**: extend the mock with the right number of canned responses per test (`classifyExpectation` consumes 1 response per auto-classified prompt; `testActivation` consumes 1 per prompt). Confirmed pattern in existing `__tests__/activation-tester.test.ts:6-15`.
**Risk**: response indexing off-by-one. Mitigation: read existing test cases as templates before writing new ones.

### Challenge 3: Backward compatibility for any other consumer of ActivationSummary
**Solution**: only ADD fields; existing field names and types preserved. `tp/tn/fp/fn` semantics tighten (warnings excluded), which is the intended fix — any consumer that summed `tp+tn+fp+fn === total` will break by exactly the warning count, and that's the bug we're fixing.
**Risk**: untracked consumers. Mitigation: grep for `ActivationSummary` references in vskill before merging.
