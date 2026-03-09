# Architecture Plan: Eval Run History & A/B Benchmarking

## 1. Architecture Overview

This feature extends the existing eval system across three layers: data model enrichment (backend types), new API endpoints and run modes (server), and enhanced UI with filtering/comparison/trends (frontend). The design prioritizes backward compatibility by making all new fields optional and reusing existing patterns (SSE streaming, JSON file storage, `computeRegressions`).

```
┌──────────────────────────────────────────────────────────────────────┐
│                        eval-ui (React + Vite)                        │
│                                                                      │
│  HistoryPage                  BenchmarkPage       ComparisonPage     │
│  ┌────────────────────┐      ┌──────────────┐    ┌──────────────┐   │
│  │ TrendChart (SVG)   │      │ + Baseline   │    │ (unchanged)  │   │
│  │ FilterBar          │      │   button     │    │              │   │
│  │ Timeline + Select  │      │ + A/B button │    │              │   │
│  │ CompareView        │      └──────────────┘    └──────────────┘   │
│  │ Rerun Buttons      │                                             │
│  └────────────────────┘                                             │
│                                                                      │
│  api.ts  ── runBaseline() | getHistory(filters) | compareRuns()      │
├──────────────────────────────────────────────────────────────────────┤
│                     eval-server (Node.js HTTP)                       │
│                                                                      │
│  api-routes.ts                                                       │
│  ┌────────────────────────────────────────────────────────────────┐  │
│  │ POST /baseline            ── baseline-only SSE run            │  │
│  │ GET  /history?filters     ── filtered history listing         │  │
│  │ GET  /history-compare     ── cross-session diff               │  │
│  │ POST /benchmark           ── (enriched case data)             │  │
│  │ POST /compare             ── (enriched comparison detail)     │  │
│  └────────────────────────────────────────────────────────────────┘  │
│                                                                      │
│  benchmark-runner.ts (NEW -- extracted SSE loop)                     │
├──────────────────────────────────────────────────────────────────────┤
│                         eval/ (core logic)                           │
│                                                                      │
│  benchmark.ts        ── BenchmarkCase gains inputTokens,             │
│                         outputTokens fields                          │
│  benchmark-history.ts ── listHistory gains filter params,            │
│                         HistorySummary gains "baseline" type         │
│  comparator.ts       ── (unchanged)                                  │
└──────────────────────────────────────────────────────────────────────┘
```

## 2. Design Decisions

### D-001: All new type fields are optional

New fields (`inputTokens`, `outputTokens`, `comparisonDetail`) are added as optional properties on existing interfaces. This ensures old JSON files on disk deserialize without error. The UI shows "--" for missing fields.

**Rationale**: The spec explicitly requires backward compatibility (AC-US1-03, AC-US1-04). Optional fields are the simplest way to achieve this without migration scripts.

### D-002: Baseline endpoint reuses benchmark SSE handler pattern

The `POST /api/skills/:plugin/:skill/baseline` endpoint is implemented by extracting the core benchmark loop into a shared helper function (`runBenchmarkSSE` in a new `benchmark-runner.ts` module) that accepts a system prompt parameter. The benchmark handler passes the skill-enhanced prompt; the baseline handler passes `"You are a helpful AI assistant."`.

**Rationale**: The benchmark and baseline handlers have identical SSE event flows (`case_start`, `output_ready`, `assertion_result`, `case_complete`, `done`). Extracting a shared function eliminates ~80 lines of duplication and ensures baseline SSE events match benchmark events exactly (AC-US2-03). This also keeps api-routes.ts under the 1500-line limit.

### D-003: History filtering is server-side with in-memory scanning

The `listHistory` function already reads all JSON files and parses them. Adding filter parameters (`model`, `type`, `from`, `to`) to this function is a minimal change -- filter after parse. Date range filtering uses the filename-embedded timestamp (already file-safe ISO format) for fast pre-filtering before JSON parse.

**Rationale**: History volumes are small (tens to low hundreds of files per skill). Server-side filtering avoids sending unnecessary data to the client while keeping the implementation simple. No indexing or caching needed.

### D-004: Cross-session comparison reuses `computeRegressions`

The `GET /history-compare?a={timestamp}&b={timestamp}` endpoint loads two history entries via `readHistoryEntry`, then calls the existing `computeRegressions` function. It also computes a case-level diff for unmatched eval cases (new/removed indicator per AC-US4-04).

**Rationale**: `computeRegressions` already handles per-assertion diffing with the exact regression/improvement classification needed. The only addition is detecting unmatched cases, which is a simple set difference on `eval_id`.

### D-005: TrendChart is a pure SVG React component (no library)

Following the existing `GroupedBarChart` pattern, `TrendChart` is a pure SVG line chart with data points. No charting library is introduced.

**Rationale**: The `GroupedBarChart` already proves pure SVG works well in this codebase. A line chart with tooltips is straightforward SVG. Adding a charting library would increase bundle size for one component.

### D-006: Rerun buttons use programmatic navigation

Rerun buttons on HistoryPage set URL params and navigate to BenchmarkPage (for benchmark/baseline) or ComparisonPage (for A/B). The target page reads URL search params to auto-start the run on mount.

**Rationale**: This reuses existing page components without duplicating run logic. The `useSSE` hook already supports starting a run programmatically via `start()`. Adding an `autostart` search param is the minimal glue needed.

### D-007: Extract benchmark SSE loop into benchmark-runner.ts

The core SSE loop (currently lines 290-422 of api-routes.ts) is extracted into `src/eval-server/benchmark-runner.ts`. This module exports a single function used by both `/benchmark` and `/baseline` routes. api-routes.ts is already ~678 lines; adding baseline, filtered history, and history-compare would push it toward 900+. The extraction keeps both files well under 1500 lines.

**Rationale**: Separation of concerns. The SSE benchmark loop is a self-contained unit of work. api-routes.ts becomes a route registration file; benchmark-runner.ts becomes the execution engine.

## 3. Component Breakdown

### 3.1 Backend: Type Enrichment (benchmark.ts)

**File**: `src/eval/benchmark.ts`

Add optional fields to `BenchmarkCase`:

```
BenchmarkCase (existing)             BenchmarkCase (extended)
──────────────────────────           ──────────────────────────
eval_id       number                 eval_id       number
eval_name     string                 eval_name     string
status        "pass"|"fail"|"error"  status        "pass"|"fail"|"error"
error_message string | null          error_message string | null
pass_rate     number                 pass_rate     number
durationMs?   number                 durationMs?   number
tokens?       number | null          tokens?       number | null
assertions    AssertionResult[]      assertions    AssertionResult[]
                                     inputTokens?  number        [NEW]
                                     outputTokens? number        [NEW]
                                     comparisonDetail?            [NEW]
                                       ComparisonCaseDetail
```

Add new interface for comparison detail:

```
ComparisonCaseDetail (NEW)
──────────────────────────────
skillDurationMs       number
skillTokens           number | null
baselineDurationMs    number
baselineTokens        number | null
skillContentScore     number
skillStructureScore   number
baselineContentScore  number
baselineStructureScore number
winner                "skill" | "baseline" | "tie"
```

### 3.2 Backend: History Module (benchmark-history.ts)

**File**: `src/eval/benchmark-history.ts`

Changes:
1. `HistorySummary.type` union expands to `"benchmark" | "comparison" | "baseline"`
2. `listHistory` gains optional filter parameter:

```typescript
interface HistoryFilter {
  model?: string;
  type?: "benchmark" | "comparison" | "baseline";
  from?: string;  // ISO timestamp
  to?: string;    // ISO timestamp
}
```

Filter logic:
- `from`/`to`: Compare filename timestamp before parsing JSON for fast pre-filtering
- `model`/`type`: Filter after JSON parse (already happening in current code)

### 3.3 Backend: Benchmark Runner (NEW)

**File**: `src/eval-server/benchmark-runner.ts`

Extracted from api-routes.ts benchmark handler. Single exported function:

```typescript
export async function runBenchmarkSSE(opts: {
  res: http.ServerResponse;
  skillDir: string;
  systemPrompt: string;
  runType: "benchmark" | "baseline";
  filterIds: Set<number> | null;
  client: LlmClient;
  onAborted: () => boolean;
}): Promise<void>
```

Handles: SSE event emission, LLM generation, assertion judging, result assembly, history writing. Populates `inputTokens`/`outputTokens` from the LLM client result (which already provides `genResult.inputTokens` and `genResult.outputTokens`).

### 3.4 Backend: API Routes (api-routes.ts)

**File**: `src/eval-server/api-routes.ts`

New/modified routes:

| Route | Method | Changes |
|-------|--------|---------|
| `/api/skills/:p/:s/baseline` | POST | NEW -- delegates to `runBenchmarkSSE` with plain system prompt |
| `/api/skills/:p/:s/history` | GET | Parse `?model`, `?type`, `?from`, `?to` query params, pass to `listHistory` |
| `/api/skills/:p/:s/history-compare` | GET | NEW -- loads two entries, runs `computeRegressions`, returns diff |
| `/api/skills/:p/:s/benchmark` | POST | Delegates to `runBenchmarkSSE` (refactored) |
| `/api/skills/:p/:s/compare` | POST | Add `comparisonDetail` per case in history write |

**History-compare response shape**:

```
GET /api/skills/:p/:s/history-compare?a={timestamp}&b={timestamp}

Response: {
  regressions: RegressionEntry[],
  improvements: RegressionEntry[],
  runA: { timestamp, model, passRate, type },
  runB: { timestamp, model, passRate, type },
  caseDiffs: Array<{
    eval_id: number,
    eval_name: string,
    statusA: "pass"|"fail"|"error"|"missing",
    statusB: "pass"|"fail"|"error"|"missing",
    passRateA: number | null,
    passRateB: number | null,
  }>
}
```

### 3.5 Frontend: Types (types.ts)

**File**: `src/eval-ui/src/types.ts`

Changes:
- `HistorySummary.type` expands to `"benchmark" | "comparison" | "baseline"`
- `BenchmarkCase` gains optional `inputTokens`, `outputTokens`, `comparisonDetail`
- `BenchmarkResult.type` expands to include `"baseline"`
- New `HistoryCompareResult` interface for the compare API response
- New `HistoryFilter` interface for filter params

### 3.6 Frontend: API Client (api.ts)

**File**: `src/eval-ui/src/api.ts`

New/modified methods:

```typescript
getHistory(plugin, skill, filters?: HistoryFilter): Promise<HistorySummary[]>
// Appends ?model=X&type=Y&from=Z&to=W query params

compareRuns(plugin, skill, a: string, b: string): Promise<HistoryCompareResult>
// GET /api/skills/:p/:s/history-compare?a=...&b=...
```

Note: `runBaseline` is not a method on the api object because baseline runs use SSE (via `useSSE.start()`). The baseline URL is constructed inline: `POST /api/skills/:p/:s/baseline`.

### 3.7 Frontend: TrendChart Component (NEW)

**File**: `src/eval-ui/src/components/TrendChart.tsx`

Props:
```typescript
interface TrendChartProps {
  entries: HistorySummary[];  // chronologically sorted (oldest first)
}
```

Design:
- Fixed-width SVG container in `glass-card` wrapper (matching GroupedBarChart)
- CHART_HEIGHT = 180, Y-axis: 0-100% pass rate
- Data points as circles (r=5) connected by polyline segments
- Color scheme per type: benchmark `#6383ff`, comparison `#a78bfa`, baseline `#fb923c`
- Tooltip: HTML div positioned absolutely on hover (simpler than SVG foreignObject)
- Legend row below title showing type colors
- Not rendered when `entries.length < 2` (AC-US5-04)

### 3.8 Frontend: HistoryPage Enhancements

**File**: `src/eval-ui/src/pages/HistoryPage.tsx`

Layout additions (top to bottom):

1. **TrendChart** -- rendered above the grid when 2+ entries exist
2. **FilterBar** -- inline above the timeline column:
   - Model dropdown (populated from `Set(history.map(h => h.model))`)
   - Type dropdown (benchmark/comparison/baseline)
   - Date range (two `<input type="date">`)
   - Filters stored in component state, passed to `api.getHistory()`
3. **Checkboxes** on timeline entries for comparison selection
4. **"Compare" button** -- appears when exactly 2 checkboxes are selected
5. **CompareView** -- renders in the detail panel (replaces single-run detail) showing:
   - Side-by-side per-case table with status columns
   - Color coding: red for regressions, green for improvements
   - "new"/"removed" badges for unmatched cases
6. **Rerun buttons** -- in the detail view header when a single run is selected:
   - "Rerun Benchmark" -> navigates to `/skills/:p/:s/benchmark?autostart=true`
   - "Run Baseline" -> navigates to `/skills/:p/:s/benchmark?mode=baseline&autostart=true`
   - "Run A/B Comparison" -> navigates to `/skills/:p/:s/compare?autostart=true`

### 3.9 Frontend: BenchmarkPage Enhancements

**File**: `src/eval-ui/src/pages/BenchmarkPage.tsx`

Changes:
- Add "Run Baseline" button next to "Run All" -> starts SSE to `/baseline` endpoint
- Add "Run A/B Comparison" button -> navigates to ComparisonPage with `?autostart=true`
- Support `?mode=baseline` search param: uses baseline URL in `useSSE.start()`
- Support `?autostart=true` search param: triggers run on mount via `useEffect`

### 3.10 Backend: Per-Test-Case History Endpoint

**New route in** `src/eval-server/api-routes.ts`:

```
GET /api/skills/:p/:s/history/case/:evalId?model=X
```

Implementation: Reads all history files via `listHistory`, then for each entry reads the full JSON and extracts the `BenchmarkCase` matching `eval_id`. Returns an array of per-run case results:

```typescript
interface CaseHistoryEntry {
  timestamp: string;
  model: string;
  type: "benchmark" | "comparison" | "baseline";
  provider?: string;
  pass_rate: number;
  durationMs?: number;
  tokens?: number | null;
  inputTokens?: number | null;
  outputTokens?: number | null;
  assertions: BenchmarkAssertionResult[];
}
```

This endpoint also lives in `benchmark-history.ts` as `getCaseHistory(skillDir, evalId, filter?)`.

### 3.11 Frontend: Per-Case History Panel on BenchmarkPage

**File**: `src/eval-ui/src/pages/BenchmarkPage.tsx`

When a completed eval case card is clicked, an expandable panel shows below it with:
- List of historical results for that case (newest first)
- Each entry: timestamp, model pill, pass rate, duration, tokens
- Mini trend line (reuses TrendChart with per-case data)
- Model filter dropdown to narrow results

### 3.12 Frontend: ComparisonPage Enhancement

**File**: `src/eval-ui/src/pages/ComparisonPage.tsx`

Changes:
- Support `?autostart=true` search param: auto-starts comparison on mount

## 4. Data Flow

### Baseline Run Flow

```
User clicks "Run Baseline"
  -> BenchmarkPage detects mode=baseline
  -> useSSE.start(POST /api/skills/:p/:s/baseline)
  -> Server: runBenchmarkSSE(systemPrompt="You are a helpful AI assistant", type="baseline")
  -> SSE events: case_start -> output_ready -> assertion_result -> case_complete -> done
  -> writeHistoryEntry(result with type:"baseline")
  -> UI renders results identically to benchmark (same CaseData processing)
```

### History Compare Flow

```
User checks 2 runs -> clicks "Compare"
  -> api.compareRuns(plugin, skill, timestampA, timestampB)
  -> Server: readHistoryEntry(A) + readHistoryEntry(B)
  -> computeRegressions(A, B) + compute caseDiffs
  -> Returns HistoryCompareResult
  -> UI renders CompareView: per-case table with color-coded diffs
```

### Enriched Data Write Flow

```
Benchmark/Baseline run completes:
  -> Server builds BenchmarkCase with inputTokens/outputTokens from LlmClient
  -> genResult already exposes .inputTokens and .outputTokens -- just map them

Comparison run completes:
  -> Server builds BenchmarkCase with comparisonDetail from ComparisonResult
  -> comparisonDetail = { skillDurationMs, skillTokens, ..., winner }
```

## 5. File Change Summary

| File | Action | Est. Lines |
|------|--------|------------|
| `src/eval/benchmark.ts` | MODIFY | +15 |
| `src/eval/benchmark-history.ts` | MODIFY | +40 |
| `src/eval-server/benchmark-runner.ts` | CREATE | ~150 |
| `src/eval-server/api-routes.ts` | MODIFY | -100, +80 (net -20 from extraction + new routes) |
| `src/eval-ui/src/types.ts` | MODIFY | +25 |
| `src/eval-ui/src/api.ts` | MODIFY | +20 |
| `src/eval-ui/src/components/TrendChart.tsx` | CREATE | ~130 |
| `src/eval-ui/src/pages/HistoryPage.tsx` | MODIFY | +180 |
| `src/eval-ui/src/pages/BenchmarkPage.tsx` | MODIFY | +100 (baseline button + per-case history panel) |
| `src/eval-ui/src/pages/ComparisonPage.tsx` | MODIFY | +10 |

## 6. Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| api-routes.ts growth | Maintainability | Extract benchmark SSE loop into `benchmark-runner.ts` (D-007) |
| HistoryPage complexity | Readability | TrendChart is a separate component; CompareView is a local sub-component; FilterBar is inline (small) |
| SVG tooltip hover jitter | UX | Use HTML overlay div with pointer-events management rather than SVG-native tooltips |
| Old history files missing new fields | Runtime errors | All new fields are optional at type level; UI checks for undefined and shows "--" (AC-US1-03) |
| Autostart race condition on page mount | Double runs | Guard with `useRef` flag to ensure `start()` is called only once per mount cycle |

## 7. Testing Strategy

- **benchmark.ts types**: Verified by TypeScript compiler (no runtime tests needed)
- **benchmark-history.ts filters**: Unit tests with fixture JSON files for each filter combination
- **benchmark-runner.ts**: Integration test with mock LLM client verifying SSE event sequence and enriched fields
- **api-routes.ts (history-compare)**: Unit test with two fixture entries verifying regression/improvement/unmatched detection
- **TrendChart.tsx**: Snapshot test for 0, 1, 2, and 10 entries (verifies conditional render and SVG output)
- **HistoryPage.tsx**: Component tests for filter state, checkbox selection logic, compare button visibility
- **api.ts**: Unit test for query string construction with various filter combinations

## 8. Implementation Phases

### Phase 1: Foundation (P1 stories)
1. Type enrichment (benchmark.ts, types.ts)
2. Extract benchmark-runner.ts from api-routes.ts
3. Baseline endpoint + SSE events
4. Enriched data writes (inputTokens, outputTokens, comparisonDetail)
5. History filtering (backend + frontend)
6. History-compare endpoint
7. Per-case history endpoint (getCaseHistory in benchmark-history.ts + route in api-routes.ts)

### Phase 2: UI Enhancement (P2 stories)
7. TrendChart component
8. HistoryPage compare view
9. Rerun buttons (HistoryPage + BenchmarkPage)
10. API client extensions
11. Autostart support for BenchmarkPage and ComparisonPage

## 9. No Domain Skill Delegation Required

This increment is a TypeScript/React feature within an established tech stack (Node.js HTTP server + React 19 + Tailwind + Vite + pure SVG charts). No specialized domain skills need to be invoked. Implementation proceeds directly to task planning.
