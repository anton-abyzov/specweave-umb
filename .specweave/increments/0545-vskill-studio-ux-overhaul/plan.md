# Implementation Plan: vSkill Studio UX & Testing Overhaul

## Overview

This increment fixes three P0 bugs (pass rate color thresholds, history sort order, activation timeout) and adds four feature enhancements (file editing, test type classification, model comparison, verdict explanations). All changes target existing files in `src/eval-ui/` and `src/eval-server/` within the vskill repo -- no new files are created.

The implementation is structured for parallelization: bug fixes and backend schema changes can run concurrently in one lane, while frontend features depend on backend readiness and run sequentially after.

## Architecture

### Bug Analysis

**Bug 1 -- Pass Rate Color Thresholds (DetailHeader.tsx)**
The color logic on line 17-18 compares against 80/50 (integer scale) but `passRate` is 0-1 float. The display on line 115 already correctly does `Math.round(passRate * 100)`, so the thresholds must be `0.8` and `0.5` (not 80 and 50). Similarly, `passBackground` on lines 21-23 has the same wrong thresholds.

**Bug 2 -- History Timeline Sort Order (TrendChart.tsx + HistoryPanel.tsx)**
TrendChart maps entries by array index (line 48-49), so sort order depends on what the API returns. The history API in `HistoryPanel.tsx` line 42-44 compares `h[0]` vs `h[1]` assuming newest-first from server. The TrendChart renders left-to-right by index, so if the API returns newest-first, the chart shows newest on the left. Fix: reverse the entries array before passing to TrendChart so oldest is leftmost, and add per-run metadata (duration, tokens, model) to the tooltip.

**Bug 3 -- Activation Timeout (ActivationPanel.tsx + WorkspaceContext.tsx)**
There is no timeout on activation tests. The SSE connection runs indefinitely. Fix: add a 120s client-side timeout with an AbortController, plus a Cancel button with partial result preservation.

### Component Boundaries

```
┌──────────────────────────────────────────────────────────┐
│                     eval-server (backend)                 │
│                                                          │
│  api-routes.ts ──── PUT /api/skills/:p/:s/file           │
│                     (new route: write file to disk)       │
│                                                          │
│  schema.ts ──────── EvalCase.testType?: "unit"|"integration" │
│                     (additive field, backward compat)     │
│                                                          │
│  verdict.ts ─────── verdictExplanation() pure function   │
│                     (new export, no API calls)            │
└──────────────────────┬───────────────────────────────────┘
                       │ HTTP / SSE
┌──────────────────────▼───────────────────────────────────┐
│                     eval-ui (frontend)                    │
│                                                          │
│  DetailHeader.tsx ── fix passRate thresholds (0.7/0.4)   │
│                                                          │
│  TrendChart.tsx ──── reverse sort, add metadata tooltip  │
│                                                          │
│  ActivationPanel.tsx ── 120s timeout + Cancel button     │
│  WorkspaceContext.tsx ── timeout AbortController          │
│                                                          │
│  SkillFileBrowser.tsx ── file size display, edit button  │
│  EditorPanel.tsx ──────── save via PUT, syntax highlight │
│                                                          │
│  TestsPanel.tsx ───── testType badge, filter, cred gate  │
│  RunPanel.tsx ──────── (no changes needed)               │
│                                                          │
│  HistoryPanel.tsx ──── chronological sort, metadata      │
│                                                          │
│  types.ts ──────────── EvalCase.testType, new interfaces │
│  verdict-styles.ts ─── (no changes)                      │
└──────────────────────────────────────────────────────────┘
```

### Data Model Changes

**evals.json schema (additive only)**

| Field | Type | Default | Notes |
|-------|------|---------|-------|
| `evals[].testType` | `"unit" \| "integration"` | `"unit"` | Optional, backward compatible |
| `evals[].requiredCredentials` | `string[]` | `[]` | Env var names needed for integration tests |

These fields are optional in both backend `schema.ts` and frontend `types.ts`. The validator passes them through without requiring them.

**verdict.ts additions**

```typescript
export function verdictExplanation(
  verdict: EvalVerdict,
  score: number,
  rubric?: { criterion: string; score: number }[]
): { explanation: string; recommendations?: string[] }
```

Pure function, no API calls. Returns explanation text based on verdict tier + rubric scores, plus optional recommendations for low-scoring results.

### API Contracts

**PUT /api/skills/:plugin/:skill/file** (new route in api-routes.ts)

Request:
```json
{ "path": "evals/evals.json", "content": "..." }
```

Response:
```json
{ "ok": true, "path": "evals/evals.json", "size": 1234 }
```

Security: The handler resolves the path relative to the skill directory and validates that the resolved absolute path starts with the skill directory root. This prevents path traversal attacks (e.g., `../../etc/passwd`).

**No other new routes are needed.** The existing `GET /api/skills/:p/:s/files` and `GET /api/skills/:p/:s/file?path=...` already provide read access. The existing model-compare infrastructure (`compare-models` route) already handles per-case A/B comparison with SSE events.

### Comparison View Architecture (US-006)

The existing `ModelCompareModal.tsx` handles single-case A/B comparison. US-006 extends this to multi-prompt aggregate comparison. Rather than creating a new component, the `ComparisonPage.tsx` (already exists) will be enhanced:

1. **Data flow**: User selects 2+ models from history runs, the page fetches full results for each, groups by prompt, and computes aggregate stats client-side.
2. **Rubric visualization**: Horizontal bar chart using the existing SVG-based chart pattern from `TrendChart.tsx` (no chart library needed).
3. **Winner badge**: Simple comparison of aggregate pass rates per model.
4. **Side-by-side output**: Reuse the existing diff view pattern from `HistoryPanel.tsx` `ImproveDiffView`, but without diff highlighting (plain text per spec).

### Verdict Explanation Architecture (US-007)

`verdictExplanation()` is a pure client-side function added to `verdict.ts`. The frontend imports it directly (already has a cross-import path via `verdict-styles.ts` which imports from `../../../eval/verdict.js`).

Tooltip rendering uses `aria-describedby` for accessibility. The "Recommendations" section for INEFFECTIVE verdicts renders inline below results in TestsPanel.

## Technology Stack

- **Frontend**: React 18 + TypeScript, Vite, no external UI libs (all SVG charts hand-rolled)
- **State**: Context + useReducer (existing WorkspaceContext pattern)
- **Backend**: Node.js HTTP server (custom router), SSE streaming
- **Styling**: CSS variables (dark theme), Tailwind-style utility classes

**Architecture Decisions**:

1. **No chart library for rubric visualization**: The codebase already has hand-rolled SVG charts (TrendChart, GroupedBarChart). Adding recharts/d3 would be inconsistent and increase bundle size. Continue with inline SVG.

2. **Client-side timeout for activations**: Server-side timeout would require changing the eval engine's async model. A client-side AbortController + 120s timer achieves the same UX with less risk. The SSE connection closure causes the server to detect `aborted=true` and stop processing.

3. **File editing via existing server**: The eval server already serves the UI and has file read routes. Adding a PUT route is the minimal-surface approach vs. a separate file service.

4. **verdictExplanation as pure function**: No backend call needed. The verdict, score, and rubric data are already available client-side after a benchmark run. This keeps the function testable and latency-free.

5. **testType defaults to "unit"**: Ensures all existing evals.json files work unchanged. The schema validator ignores unknown fields, so no migration needed.

## Implementation Phases

### Phase 1: Bug Fixes + Backend Schema (Parallel Lane A)

Changes that unblock everything else and can be done independently:

1. **DetailHeader.tsx** -- Fix pass rate color thresholds from 80/50 to 0.7/0.4 scale (matches spec thresholds: green >= 0.7, yellow >= 0.4, red < 0.4)
2. **schema.ts** -- Add optional `testType` and `requiredCredentials` fields to `EvalCase`, pass through in validator
3. **types.ts** (frontend) -- Mirror the new fields
4. **verdict.ts** -- Add `verdictExplanation()` pure function
5. **api-routes.ts** -- Add `PUT /api/skills/:p/:s/file` with path traversal validation
6. **api.ts** (frontend) -- Add `saveSkillFile()` method

### Phase 2: Timeline + Activation Fixes (Parallel Lane A continued)

7. **TrendChart.tsx** -- Accept entries in any order, sort chronologically internally, show duration/tokens/model in tooltip
8. **HistoryPanel.tsx** -- Reverse history array before passing to TrendChart (oldest first for left-to-right), add per-run metadata (duration, tokens) to run list items, make timeline points clickable to navigate to detail
9. **ActivationPanel.tsx + WorkspaceContext.tsx** -- Add 120s timeout via AbortController, Cancel button, partial result display with "Cancelled" status for incomplete prompts

### Phase 3: Frontend Features (Parallel Lane B, after Phase 1)

10. **SkillFileBrowser.tsx** -- Add file size display (human-readable), Edit button per file
11. **EditorPanel.tsx** -- Wire Save button to PUT endpoint, JSON syntax highlighting for .json files, success toast
12. **TestsPanel.tsx** -- testType badge rendering, All/Unit/Integration filter tabs, credential gate (disabled Run button + missing creds message)
13. **ComparisonPage.tsx / HistoryPanel.tsx** -- Multi-model aggregate comparison: rubric bar chart, side-by-side output with 500-char truncation + expand toggle, winner badge
14. **TestsPanel.tsx** -- Verdict explanation tooltips (hover on verdict cell), "Recommendations" section for INEFFECTIVE results

## Testing Strategy

Each change has a corresponding unit test in the existing test infrastructure:

- **Bug fixes**: Test `passRateColor()` helper with 0-1 scale inputs; test TrendChart sort order with unsorted entries; test timeout/cancel behavior in workspace reducer
- **Schema**: Test `loadAndValidateEvals()` with and without `testType` field
- **verdict.ts**: Test `verdictExplanation()` for each tier (EFFECTIVE, MARGINAL, INEFFECTIVE, EMERGING, DEGRADING)
- **File editing**: Test PUT route path traversal rejection, success case
- **Comparison**: Test aggregate score computation, winner badge logic
- **TestsPanel**: Test filter logic, credential gate disable logic

All tests use Vitest. No E2E Playwright tests needed -- this is a localhost dev tool, not a production web app.

## Technical Challenges

### Challenge 1: Path Traversal in File PUT Endpoint
**Solution**: `resolve(skillDir, requestPath)` then check `resolvedPath.startsWith(skillDir)`. Reject with 403 if path escapes skill directory. Also reject absolute paths in the request.
**Risk**: Low. Standard pattern, well-tested.

### Challenge 2: Partial Results on Activation Cancel
**Solution**: The SSE `onEvent` handler already accumulates results one-at-a-time. Cancelling the SSE connection via `activationSSE.stop()` preserves all already-dispatched `ACTIVATION_RESULT` actions. Incomplete prompts simply never arrive. Add a `ACTIVATION_CANCEL` action that marks state as cancelled and labels missing prompts as "Cancelled".
**Risk**: Low. The existing `cancelCase` pattern in WorkspaceContext already demonstrates this approach.

### Challenge 3: TrendChart Performance with 100+ Points
**Solution**: The SVG-based chart already handles this -- SVG polylines render efficiently. For x-axis labels, the existing `labelIndices()` function already auto-spaces to avoid overlap. Add horizontal scrolling via `overflow-x: auto` on the container if points exceed viewport width.
**Risk**: Low. Spec requires < 200ms for 100 points, SVG handles this natively.

### Challenge 4: Comparison View Data Assembly
**Solution**: Client-side aggregation from existing history entries. No new API needed -- fetch full benchmark results for selected runs via `getHistoryEntry()`, group cases by `eval_id`, compute per-model stats. This avoids backend complexity and keeps the comparison logic testable.
**Risk**: Medium. If history entries are large (many prompts), fetching 3+ full results could be slow. Mitigated by the spec's "< 500ms for 3 models x 20 prompts" target, which is well within fetch capabilities.

## Parallelization Strategy (for Team Lead)

Two independent lanes:

**Lane A (Bug fixes + Backend)**: Tasks 1-9 above. One agent handles all three bugs plus backend schema changes. No frontend feature dependencies.

**Lane B (Frontend Features)**: Tasks 10-14. One agent handles file editing, test types, comparison, and verdict explanations. Depends on Lane A completing Phase 1 (schema + API changes).

Lane B can start as soon as Phase 1 merges. Lane A continues into Phase 2 independently.
