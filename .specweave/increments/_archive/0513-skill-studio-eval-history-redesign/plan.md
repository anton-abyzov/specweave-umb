# Architecture Plan: Eval History Redesign + Comparison Fix

## Overview

Three coordinated changes across server and client:

1. **Bug fix (US-001)**: Comparison endpoint emits `assertion_result` + `case_complete` SSE events so per-case cards render during "Compare All"
2. **UI redesign (US-002)**: CaseHistorySection becomes a two-column split-lane (Skill | Baseline)
3. **Sparkline upgrade (US-003)**: MiniTrend renders dual-line polylines; `baselinePassRate` derived from rubric scores

No new dependencies. All changes are additive or in-place replacements within the existing React + Vite + Node.js stack.

## Component Map

```
Server (Node.js)                         Client (React + Vite)
─────────────────                        ─────────────────────
api-routes.ts                            WorkspaceContext.tsx
  /compare endpoint                        handleSSEEvent()
  ├── (existing) outputs_ready               ├── (existing) output_ready
  ├── (existing) comparison_scored           ├── (new) outputs_ready handler
  ├── (NEW) assertion_result ──SSE──────────►├── (existing) assertion_result
  └── (NEW) case_complete    ──SSE──────────►└── (existing) case_complete

benchmark-history.ts                     TestsPanel.tsx
  getCaseHistory()                         CaseHistorySection
  └── (NEW) baselinePassRate               ├── (NEW) split-lane layout
      from comparisonDetail                └── comparison merged row

                                         historyUtils.tsx
types.ts (client)                          MiniTrend
  CaseHistoryEntry                         └── (NEW) dual polylines
  └── (NEW) baselinePassRate?

benchmark-history.ts (server)
  CaseHistoryEntry
  └── (NEW) baselinePassRate?
```

## Decision 1: SSE Event Strategy (US-001)

### Problem

The comparison endpoint (`/api/skills/:plugin/:skill/compare`) emits `outputs_ready` and `comparison_scored` events. The client's `handleSSEEvent` only handles `output_ready` (singular), `assertion_result`, and `case_complete` -- events the comparison endpoint never sends. Result: per-case cards show nothing during comparison runs.

### Decision: Additive emission

The comparison endpoint already runs `judgeAssertion` per assertion (line 724 in api-routes.ts) and accumulates results into `assertionResults[]`, but only emits the batch `comparison_scored` event at the end. The fix is to emit `assertion_result` inside the assertion loop and `case_complete` after each case -- mirroring the exact shapes from benchmark-runner.ts (lines 84-90, 113-119).

**No events removed.** `outputs_ready` and `comparison_scored` remain for backward compatibility. The new events are emitted alongside them.

### Server Changes

**File**: `src/eval-server/api-routes.ts`, comparison endpoint (lines 640-861)

1. **Inside the assertion loop** (after line 725, `assertionResults.push(result)`):
   ```
   sendSSE(res, "assertion_result", {
     eval_id: evalCase.id,
     assertion_id: result.id,
     text: result.text,
     pass: result.pass,
     reasoning: result.reasoning,
   });
   ```
   Shape matches benchmark-runner.ts line 84-90 exactly.

2. **After the assertion loop, before `comparison_scored`** (after line 733):
   ```
   const casePassRate = assertionResults.length > 0
     ? assertionResults.filter(a => a.pass).length / assertionResults.length
     : 0;
   const caseStatus = assertionResults.every(a => a.pass) ? "pass" : "fail";

   sendSSE(res, "case_complete", {
     eval_id: evalCase.id,
     status: caseStatus,
     pass_rate: casePassRate,
     durationMs: comparison.skillDurationMs,
     tokens: comparison.skillTokens,
   });
   ```
   Shape matches benchmark-runner.ts lines 113-119.

### Client Changes

**File**: `src/eval-ui/src/pages/workspace/WorkspaceContext.tsx`, `handleSSEEvent` (lines 44-81)

Add handler for `outputs_ready` (plural) to bridge the naming gap:

```
if (evt.event === "outputs_ready") {
  r.output = data.skillOutput as string;
  if (data.skillDurationMs != null) r.durationMs = data.skillDurationMs as number;
  if (data.skillTokens != null) r.tokens = data.skillTokens as number | null;
}
```

This is positioned after the existing `output_ready` (singular) handler. The `assertion_result` and `case_complete` handlers already exist and will process the new server events with no modification.

### Event Sequence Per Case (After Fix)

```
case_start              (existing, unchanged)
progress: generating    (existing heartbeat)
outputs_ready           (existing, now also handled by client)
progress: judging       (existing)
assertion_result        (NEW, per assertion)
case_complete           (NEW, per case)
comparison_scored       (existing, unchanged)
```

## Decision 2: Split-Lane Timeline (US-002)

### Problem

CaseHistorySection renders a flat `space-y-2` list of history entries with no visual separation between benchmark, baseline, and comparison runs.

### Decision: CSS Grid two-column layout

Use a 2-column CSS grid with a shared center gutter for comparison entries. No new dependencies -- pure inline styles matching existing patterns in the codebase.

### Layout Structure

```
┌─ Skill ──────────────────┐  ┌─ Baseline ────────────────┐
│ [benchmark entry]        │  │ [baseline entry]           │
│ [benchmark entry]        │  │                            │
├──────────────────────────┴──┴────────────────────────────┤
│           [comparison entry: delta + verdict]             │
├──────────────────────────┬──┬────────────────────────────┤
│ [benchmark entry]        │  │ "No baseline runs"         │
└──────────────────────────┘  └────────────────────────────┘
```

### Implementation

**File**: `src/eval-ui/src/pages/workspace/TestsPanel.tsx`, CaseHistorySection (lines 800-933)

1. **Partition entries** into lane assignments at render time:
   - `"left"` (Skill column): entries where `type === "benchmark"`. Also `improve`, `instruct`, and other non-core types (they run against skill output).
   - `"right"` (Baseline column): entries where `type === "baseline"`
   - `"full"` (spans both): entries where `type === "comparison"`

2. **Interleave by timestamp**: Merge all entries into a single timeline ordered by timestamp (newest first, matching current behavior). Each entry carries its lane tag.

3. **Grid rendering**:
   - Container: `display: grid; grid-template-columns: 1fr 1fr; gap: 8px`
   - Column headers: "Skill" (left), "Baseline" (right) -- `text-[11px] font-semibold uppercase tracking-wider` in `var(--text-tertiary)`
   - Left-lane entries: `grid-column: 1`
   - Right-lane entries: `grid-column: 2`
   - Comparison entries: `grid-column: 1 / -1` with delta badge centered

4. **Empty column placeholders**: When one side has zero entries, render placeholder text ("No baseline runs" or "No skill runs") in `var(--text-tertiary)` at `font-size: 12px`.

5. **Comparison merged card**: Reuses existing entry card styles but spans both columns. Shows:
   - Timestamp + model + "comparison" pill (existing)
   - Assertion list (existing, now populated thanks to US-001)
   - Delta: `+X.X%` or `-X.X%` badge derived from `comparisonDetail` rubric scores
   - Winner badge: "skill" / "baseline" / "tie"

### Why Grid Over Flexbox

Grid naturally handles the merged comparison row (`grid-column: 1 / -1`) without wrapper gymnastics. Flexbox would require conditional wrapping or absolute positioning for the full-width comparison span.

### Timeline Interleaving Algorithm

```
Input: entries[] sorted by timestamp desc
Output: grid items with lane assignment

for each entry:
  if entry.type === "benchmark" || entry.type in [improve, instruct, ...]
    lane = "left"
  else if entry.type === "baseline"
    lane = "right"
  else if entry.type === "comparison"
    lane = "full"

  // Left-lane entries at a given row need an empty spacer in column 2
  // Right-lane entries need an empty spacer in column 1
  // Full-lane entries span 1 / -1, no spacer needed
```

Since grid auto-placement won't correctly pair left/right items at the same row, each single-lane entry is wrapped in a fragment that includes itself in the correct column and an invisible spacer in the opposite column. This ensures rows align correctly.

## Decision 3: Dual-Line MiniTrend (US-003)

### Problem

MiniTrend renders a single polyline from all entries regardless of type. Skill and baseline trends are indistinguishable.

### Decision: Two polylines, type-filtered data sources

### Type Changes

**Server** (`src/eval/benchmark-history.ts`, CaseHistoryEntry interface, line 31-42):
```typescript
baselinePassRate?: number;
```

**Client** (`src/eval-ui/src/types.ts`, CaseHistoryEntry interface, line 159-170):
```typescript
baselinePassRate?: number;
```

### baselinePassRate Derivation

**File**: `src/eval/benchmark-history.ts`, `getCaseHistory()` (lines 180-221)

When iterating history files, if a matching case has `comparisonDetail`, compute:

```
baselinePassRate = (comparisonDetail.baselineContentScore
                  + comparisonDetail.baselineStructureScore) / 200
```

The scores are 0-100 integers from the LLM rubric. Dividing by 200 averages and normalizes to 0-1. This matches the `pass_rate` range for the skill line.

For non-comparison entries, `baselinePassRate` stays `undefined`.

### MiniTrend Rendering

**File**: `src/eval-ui/src/utils/historyUtils.tsx`, MiniTrend (lines 22-51)

1. **Filter entries** by type:
   - Skill line data: entries where `type` is `benchmark` or `comparison` (using `pass_rate`)
   - Baseline line data: entries where `type` is `baseline` (using `pass_rate`) or `comparison` (using `baselinePassRate`)
   - Exclude: `improve`, `instruct`, `model-compare`, `ai-generate`, `eval-generate`

2. **Render two polylines** within the existing 80x24 SVG:
   - Blue line (`var(--accent)`, strokeWidth 1.5): skill data points
   - Gray line (`var(--text-tertiary)`, strokeWidth 1.5): baseline data points

3. **Shared x-axis**: Both lines share the same temporal x-axis. Points are positioned by their index within the full filtered+reversed timeline (oldest first). Each comparison entry contributes one x position to both lines. Each benchmark or baseline entry contributes one x position to only its line. This means the x-axis represents "runs in chronological order" and both polylines advance through the same time progression.

4. **Latest-point dot**: Blue dot on the skill line's last point (existing behavior). Gray dot on the baseline line's last point if baseline data exists.

5. **Guard**: If either line has fewer than 2 points, only render the line that has 2+ points. If both have <2 points, return null.

### Why Not Interpolation

Interpolating missing baseline points between known values would be misleading -- the baseline was not actually run at those times. Gap-skipping is honest and visually clear.

## Data Flow Diagram

```
                      COMPARISON RUN
                      ──────────────
                           │
           ┌───────────────┼───────────────┐
           ▼               ▼               ▼
    outputs_ready   assertion_result   case_complete
    (existing)       (NEW per assert)   (NEW per case)
           │               │               │
           ▼               ▼               ▼
    handleSSEEvent  handleSSEEvent  handleSSEEvent
    (NEW handler)   (existing)      (existing)
           │               │               │
           └───────┬───────┘               │
                   ▼                       ▼
           InlineResult updated      passRate set
                   │
                   ▼
           Per-case card renders
           with assertions + pass rate


                    HISTORY DISPLAY
                    ───────────────
                           │
                    getCaseHistory()
                           │
                    ┌──────┴──────┐
                    │  For each   │
                    │  history    │
                    │  entry:     │
                    │             │
                    │ if comparison│
                    │  + detail:  │
                    │  derive     │
                    │  baseline   │
                    │  PassRate   │
                    └──────┬──────┘
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
         Split-Lane    MiniTrend    Comparison
         Timeline      dual-line    merged card
```

## File Change Summary

| File | Change | Scope |
|------|--------|-------|
| `src/eval-server/api-routes.ts` | Add `assertion_result` + `case_complete` emissions in comparison loop | ~10 lines added |
| `src/eval-ui/src/pages/workspace/WorkspaceContext.tsx` | Add `outputs_ready` handler in `handleSSEEvent` | ~5 lines added |
| `src/eval/benchmark-history.ts` | Add `baselinePassRate?` to `CaseHistoryEntry`; populate in `getCaseHistory` from `comparisonDetail` | ~8 lines |
| `src/eval-ui/src/types.ts` | Add `baselinePassRate?` to `CaseHistoryEntry` | 1 line |
| `src/eval-ui/src/pages/workspace/TestsPanel.tsx` | Rewrite `CaseHistorySection` with grid layout, lane partitioning, comparison merged card | ~150 lines (rewrite of existing ~130) |
| `src/eval-ui/src/utils/historyUtils.tsx` | Rewrite `MiniTrend` with dual polylines and type filtering | ~60 lines (rewrite of existing ~30) |

## Implementation Phases

### Phase 1: Type changes (foundation)
- Add `baselinePassRate?` to both `CaseHistoryEntry` definitions (types.ts + benchmark-history.ts)

### Phase 2: Server-side fixes
- Add `assertion_result` + `case_complete` emissions inside comparison loop in api-routes.ts
- Derive `baselinePassRate` from rubric scores in `getCaseHistory`

### Phase 3: Client-side SSE fix
- Add `outputs_ready` handler in `handleSSEEvent` (WorkspaceContext.tsx)

### Phase 4: UI redesign
- Replace flat list with split-lane grid layout (TestsPanel.tsx)
- Replace single-polyline MiniTrend with dual-polyline (historyUtils.tsx)

## Risk Mitigations

1. **Backward compatibility**: No events removed from comparison endpoint. `outputs_ready` and `comparison_scored` continue to fire.
2. **No new LLM calls**: `baselinePassRate` derived from existing `comparisonDetail` rubric scores already stored in history JSON.
3. **Layout stability**: MiniTrend stays 80x24px. Grid layout uses existing CSS variable tokens -- no new design tokens.
4. **Type safety**: Both server and client `CaseHistoryEntry` get `baselinePassRate?` as optional field. Existing consumers unaffected.

## Testing Strategy

- **Server SSE events**: Extend existing `benchmark-runner.test.ts` pattern to assert `assertion_result` and `case_complete` events in comparison flow
- **getCaseHistory**: Unit test with mock history JSON containing `comparisonDetail` to verify `baselinePassRate` derivation (scores 0-100 -> 0-1 normalization)
- **MiniTrend**: Unit test with mixed-type entries to verify correct line filtering and point assignment
- **CaseHistorySection**: Render tests for three configurations: skill-only, baseline-only, mixed with comparison entries
- **handleSSEEvent**: Unit test verifying `outputs_ready` event populates `output` from `skillOutput` field
- **Integration**: Manual "Compare All" run verifying per-case cards populate in real time
