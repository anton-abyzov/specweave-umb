# Architecture Plan: Skill Builder Redesign -- Unified Workspace

## 1. Architecture Overview

Replace 4 disconnected pages (SkillDetailPage, BenchmarkPage, ComparisonPage, HistoryPage) with a single `SkillWorkspace` route. The workspace uses a CSS Grid shell with a fixed left rail (48px), a workspace header bar, and a main content area that renders one of 5 panels.

```
+--------+---------------------------------------------------+
| RAIL   | WorkspaceHeader (breadcrumb, pass rate, model)     |
| 48px   +---------------------------------------------------+
|        |                                                    |
| Editor | Active Panel Content                               |
| Tests  |                                                    |
| Run    |   (EditorPanel | TestsPanel | RunPanel |           |
| History|    HistoryPanel | DepsPanel)                       |
| Deps   |                                                    |
|        |                                                    |
+--------+---------------------------------------------------+
```

### Decision: React Context for Shared State

**Chosen**: `SkillWorkspaceProvider` wrapping a custom `useSkillWorkspace()` hook that uses `useReducer` internally and is exposed through React Context.

**Rejected alternatives**:
- `useState` per-panel (current approach) -- duplicates fetches, loses cross-panel state
- Lifting all state to `SkillWorkspace` and prop-drilling -- 5 panels with 15+ props each = unmaintainable
- External state manager (Zustand, Jotai) -- overkill for a single-route app; adds a dependency

**Why Context + useReducer**: Single data fetch on mount. All panels read from the same state slice. Actions like `runBenchmark`, `saveContent`, `selectCase` are dispatched centrally. URL sync (`?panel=`) is derived state, not source of truth. The context boundary is the `SkillWorkspace` route itself, so no unnecessary re-renders elsewhere.

### Decision: CSS Grid Layout (Not Flexbox)

The workspace shell uses a 2-column, 2-row CSS Grid:
```css
.workspace {
  display: grid;
  grid-template-columns: 48px 1fr;
  grid-template-rows: auto 1fr;
  height: 100%;
}
```
Rail spans full height (row 1-3). Header occupies row 1 col 2. Panel area occupies row 2 col 2 with `overflow: auto`.

**Why Grid over Flexbox**: Fixed rail width + fluid main area is a natural grid layout. Flexbox would require `flex-shrink: 0` hacks and nested flex containers.

### Decision: Panel = Direct Swap (No Nested Routes)

Panels are switched by a `panel` state variable synced to URL `?panel=`. No nested `<Route>` components. A simple conditional render in SkillWorkspace renders the active panel.

**Why**: react-router nested routes add complexity for zero benefit -- the panels share state via context, not URL params. Deep-linking is handled by `?panel=tests&case=3` query params.

---

## 2. Component Hierarchy

```
App.tsx
  Routes
    SkillWorkspace (route: /skills/:plugin/:skill)
      SkillWorkspaceProvider (context)
        WorkspaceShell (CSS Grid container)
          LeftRail (48px, icon buttons, always visible)
          WorkspaceHeader (breadcrumb, pass rate badge, model, dirty indicator)
          Panel Area (renders ONE of):
            EditorPanel
              EditorToolbar (view mode toggles, save button)
              RawEditor (textarea)
              MarkdownPreview (rendered preview)
              FrontmatterCards (structured key-value)
              SkillImprovePanel (reused existing component)
            TestsPanel
              TestCaseList (280px left sub-panel)
                TestCaseListItem (status pill, sparkline)
              TestCaseDetail (right sub-panel)
                PromptEditor (textarea)
                ExpectedOutputEditor (textarea)
                AssertionBuilder (CRUD + drag reorder)
                InlineRunResult (last run results)
                AssertionHealthBadges (flaky/non-disc/regression)
            RunPanel
              RunControls (Run All, Run Baseline, Run A/B, scope selector)
              RunProgress (progress bar, count)
              CaseResultCard (per-case, animated fade-in)
              ComparisonResultCard (for A/B mode)
              RunSummary (overall pass rate card + chart)
              GroupedBarChart (reused)
              ProgressLog (reused)
            HistoryPanel
              HistoryTabBar (Timeline | Per-Eval | Statistics)
              TimelineView
                TrendChart (reused)
                FilterBar (model, type, date range)
                RunTimeline (list of runs)
                SingleRunDetail / CompareView
              HistoryPerEval (reused)
              StatsPanel (reused)
            DepsPanel
              McpDependencies (reused)
```

---

## 3. State Management Design

### 3.1 Context Shape

```typescript
interface WorkspaceState {
  // Identity
  plugin: string;
  skill: string;

  // Skill content (SKILL.md)
  skillContent: string;
  savedContent: string;        // last saved version for dirty tracking
  isDirty: boolean;            // skillContent !== savedContent

  // Eval cases
  evals: EvalsFile | null;
  evalsLoading: boolean;

  // Panel navigation
  activePanel: PanelId;        // "editor" | "tests" | "run" | "history" | "deps"
  selectedCaseId: number | null;

  // Run state
  isRunning: boolean;
  runMode: "benchmark" | "baseline" | "comparison" | null;
  runScope: "all" | number | null;   // "all" or specific eval_id
  runEvents: SSEEvent[];             // raw SSE event stream
  iterationCount: number;

  // Results (shared across panels)
  inlineResults: Map<number, InlineResult>;
  latestBenchmark: BenchmarkResult | null;

  // Regression detection
  regressions: RegressionInfo[];     // derived from history + latest run

  // Improve state
  improveTarget: { evalId: number; assertionId?: string } | null;

  // Loading / errors
  loading: boolean;
  error: string | null;
}

type PanelId = "editor" | "tests" | "run" | "history" | "deps";
```

### 3.2 Actions (Dispatch)

```typescript
type WorkspaceAction =
  | { type: "SET_PANEL"; panel: PanelId }
  | { type: "SELECT_CASE"; caseId: number | null }
  | { type: "SET_CONTENT"; content: string }
  | { type: "CONTENT_SAVED"; content: string }
  | { type: "SET_EVALS"; evals: EvalsFile }
  | { type: "RUN_START"; mode: RunMode; scope: "all" | number }
  | { type: "RUN_EVENT"; event: SSEEvent }
  | { type: "RUN_COMPLETE"; result: BenchmarkResult }
  | { type: "SET_INLINE_RESULT"; evalId: number; result: InlineResult }
  | { type: "SET_LATEST_BENCHMARK"; benchmark: BenchmarkResult }
  | { type: "SET_REGRESSIONS"; regressions: RegressionInfo[] }
  | { type: "OPEN_IMPROVE"; target: { evalId: number; assertionId?: string } }
  | { type: "CLOSE_IMPROVE" }
  | { type: "INCREMENT_ITERATION" }
  | { type: "SET_ERROR"; error: string | null }
  | { type: "LOADED"; data: InitialData }
```

### 3.3 Context API

```typescript
interface WorkspaceContextValue {
  state: WorkspaceState;
  dispatch: React.Dispatch<WorkspaceAction>;

  // Convenience action creators (async, encapsulate API calls)
  saveContent: () => Promise<void>;
  runBenchmark: (evalIds?: number[]) => void;
  runBaseline: () => void;
  runComparison: () => void;
  saveEvals: (evals: EvalsFile) => Promise<void>;
  fixWithAI: (evalId: number, assertionId?: string) => void;
  applyAndRerun: (content: string, evalId: number) => Promise<void>;
  stopRun: () => void;
}
```

### 3.4 Data Flow

1. **Mount**: `SkillWorkspaceProvider` calls `api.getSkillDetail()`, `api.getEvals()`, `api.getLatestBenchmark()`, `api.getStats()` in parallel. Dispatches `LOADED` with combined result.
2. **Editor save**: User types in textarea -> dispatches `SET_CONTENT` (updates skillContent, isDirty=true). Ctrl+S -> calls `saveContent()` which PUTs to new `/content` endpoint, dispatches `CONTENT_SAVED`.
3. **Run benchmark**: `runBenchmark()` dispatches `RUN_START`, calls SSE start. SSE events dispatch `RUN_EVENT`. On SSE done, dispatches `RUN_COMPLETE` which updates `inlineResults` and `latestBenchmark`.
4. **Cross-panel**: "Fix with AI" in TestsPanel dispatches `OPEN_IMPROVE` + `SET_PANEL: "editor"`. EditorPanel reads `improveTarget` from context and opens SkillImprovePanel pre-populated.
5. **URL sync**: A `useEffect` in `SkillWorkspace` syncs `state.activePanel` and `state.selectedCaseId` to URL query params via `useSearchParams`. On mount, reads query params to set initial panel.

---

## 4. File Organization

All new workspace files under `src/pages/workspace/`:

```
src/
  pages/
    workspace/
      SkillWorkspace.tsx         -- route component, mounts Provider + Shell
      WorkspaceShell.tsx         -- CSS Grid layout container
      LeftRail.tsx               -- 48px icon rail with panel buttons
      WorkspaceHeader.tsx        -- breadcrumb, pass rate, model, dirty indicator
      SkillWorkspaceProvider.tsx -- React Context + useReducer
      useSkillWorkspace.ts       -- context consumer hook
      workspaceReducer.ts        -- reducer + action types
      workspaceTypes.ts          -- shared TypeScript interfaces
      panels/
        EditorPanel.tsx          -- SKILL.md editor + preview
        EditorToolbar.tsx        -- view mode toggles, save
        MarkdownPreview.tsx      -- simple markdown renderer
        FrontmatterCards.tsx     -- structured frontmatter display
        TestsPanel.tsx           -- test case list + detail
        TestCaseList.tsx         -- scrollable case list (280px)
        TestCaseListItem.tsx     -- single case row with status + sparkline
        TestCaseDetail.tsx       -- selected case editor
        AssertionBuilder.tsx     -- CRUD + drag reorder for assertions
        AssertionHealthBadge.tsx -- flaky/non-disc/regression badges
        Sparkline.tsx            -- inline SVG trend chart
        RunPanel.tsx             -- benchmark execution panel
        RunControls.tsx          -- run mode buttons + scope selector
        CaseResultCard.tsx       -- per-case result display
        ComparisonResultCard.tsx -- A/B comparison result display
        RunSummary.tsx           -- overall pass rate + chart
        HistoryPanel.tsx         -- history with sub-tabs
        TimelineView.tsx         -- timeline list + detail
        DepsPanel.tsx            -- thin wrapper around McpDependencies
      hooks/
        useKeyboardShortcuts.ts  -- Ctrl+1-5, Ctrl+S, Ctrl+Enter, Ctrl+Shift+Enter
        useSSEBridge.ts          -- bridges useSSE into workspace dispatch
        useURLSync.ts            -- syncs panel/case to URL query params
        useAssertionHealth.ts    -- computes flaky/non-disc/regression badges
  components/
    (existing components stay here -- no changes)
```

**Total new files**: ~28. **Max file size target**: 300 lines per component, 400 lines for reducer.

### Existing Components Reused Without Modification

| Component | Used In |
|-----------|---------|
| GroupedBarChart | RunPanel, HistoryPanel |
| StatsPanel | HistoryPanel statistics tab |
| TrendChart | HistoryPanel timeline tab |
| SkillImprovePanel | EditorPanel |
| McpDependencies | DepsPanel |
| ProgressLog | RunPanel |
| ModelCompareModal | TestsPanel |
| HistoryPerEval | HistoryPanel per-eval tab |

---

## 5. Backend Change

### 5.1 PUT /api/skills/:plugin/:skill/content

**File**: `api-routes.ts` (add to existing `registerRoutes`)

Accepts `{ content: string }` body. Writes to `SKILL.md`. Returns `{ ok: true }`. Last-write-wins.

This mirrors the existing `POST /api/skills/:plugin/:skill/apply-improvement` endpoint in `improve-routes.ts` (which also writes content to SKILL.md), but uses PUT semantics and a cleaner URL. The existing endpoint remains for backward compatibility.

### 5.2 API Client Addition

Add to `api.ts`:

```typescript
saveSkillContent(plugin: string, skill: string, content: string): Promise<{ ok: boolean }>
```

---

## 6. Route Changes

### App.tsx Modifications

**Remove routes**:
- `/skills/:plugin/:skill` -> SkillDetailPage
- `/skills/:plugin/:skill/benchmark` -> BenchmarkPage
- `/skills/:plugin/:skill/compare` -> ComparisonPage
- `/skills/:plugin/:skill/history` -> HistoryPage

**Add route**:
- `/skills/:plugin/:skill` -> SkillWorkspace (with `?panel=` query param)

**Unchanged**:
- `/` -> SkillListPage
- `/create` -> CreateSkillPage
- `/activation` -> ActivationTestPage

Old page files (SkillDetailPage.tsx, BenchmarkPage.tsx, ComparisonPage.tsx, HistoryPage.tsx) are deleted after workspace is feature-complete.

---

## 7. CSS Layout Strategy

### 7.1 Workspace Shell

```css
.workspace-shell {
  display: grid;
  grid-template-columns: 48px 1fr;
  grid-template-rows: auto 1fr;
  height: 100%;
  overflow: hidden;
}

.workspace-rail {
  grid-row: 1 / -1;
  grid-column: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding-top: 12px;
  gap: 4px;
  border-right: 1px solid var(--border-subtle);
  background: var(--surface-1);
}

.workspace-header {
  grid-row: 1;
  grid-column: 2;
  padding: 12px 24px;
  border-bottom: 1px solid var(--border-subtle);
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.workspace-panel {
  grid-row: 2;
  grid-column: 2;
  overflow: auto;
  padding: 24px;
}
```

### 7.2 Panel-Specific Layouts

- **EditorPanel**: CSS Grid split (adjustable via view mode: `1fr`, `1fr 1fr`, or `1fr`)
- **TestsPanel**: CSS Grid `280px 1fr` for list+detail split
- **RunPanel**: Single column, cards stack vertically
- **HistoryPanel**: Reuses existing 3-column grid for timeline tab

### 7.3 Styling Approach

Continue the existing pattern: Tailwind utility classes for layout/spacing + CSS variables for colors/theming + inline styles for dynamic values. No new CSS framework. New workspace-specific classes added to `globals.css`.

---

## 8. Panel Transition Strategy

**Instant swap** with the existing `animate-fade-in` CSS class. No transition library.

The `key={activePanel}` on the panel container forces React to remount on panel switch, triggering the CSS fade-in animation. Panels that need to preserve state (e.g., editor dirty content) rely on the context, not component-local state.

---

## 9. Keyboard Shortcuts Design

A single `useKeyboardShortcuts` hook registered at the `WorkspaceShell` level:

| Shortcut | Action |
|----------|--------|
| Ctrl+1 | Switch to Editor panel |
| Ctrl+2 | Switch to Tests panel |
| Ctrl+3 | Switch to Run panel |
| Ctrl+4 | Switch to History panel |
| Ctrl+5 | Switch to Deps panel |
| Ctrl+S | Save SKILL.md (when Editor active) |
| Ctrl+Enter | Run selected test case |
| Ctrl+Shift+Enter | Run all test cases |

Shortcuts are suppressed when a textarea/input has focus (except Ctrl+S which always saves when Editor panel is active).

---

## 10. Extraction Strategy: Pages to Panels

Each existing page maps to a workspace panel. The extraction pattern: move business logic (state, effects, API calls) into the workspace reducer/context, keep only rendering logic in the panel component.

### 10.1 SkillDetailPage (1068 lines) -> EditorPanel + TestsPanel

| Section | Destination |
|---------|-------------|
| Skill content viewer + improve | EditorPanel |
| Dependencies section | DepsPanel (wrapper) |
| Eval case CRUD (add/edit/delete) | TestsPanel + context actions |
| Assertion management (add/edit/delete/reorder) | AssertionBuilder |
| Inline benchmark results | TestCaseDetail (InlineRunResult) |
| Single-case SSE benchmark | Context `runBenchmark()` |
| Improve for case / Apply and rerun | Context `fixWithAI()` / `applyAndRerun()` |
| EvalCaseFormModal | panels/TestCaseFormModal.tsx |
| AssertionInput component | AssertionBuilder |

### 10.2 BenchmarkPage (647 lines) -> RunPanel

| Section | Destination |
|---------|-------------|
| SSE event processing | useSSEBridge hook + reducer |
| Run controls (run all, baseline, A/B) | RunControls |
| Per-case result cards | CaseResultCard |
| Case history panel | Removed (now in HistoryPanel) |
| Pass rate chart | RunSummary + GroupedBarChart |
| Overall result card | RunSummary |
| Progress log | Reused ProgressLog |

### 10.3 ComparisonPage (381 lines) -> RunPanel (A/B mode)

| Section | Destination |
|---------|-------------|
| Comparison event processing | useSSEBridge (comparison mode) |
| ScoreBar / ScoreRow components | ComparisonResultCard |
| OutputPanel (side-by-side) | ComparisonResultCard |
| Verdict display | RunSummary (verdict mode) |
| MetricPill helper | RunSummary |

### 10.4 HistoryPage (789 lines) -> HistoryPanel

| Section | Destination |
|---------|-------------|
| Tab bar (Timeline/Per-Eval/Statistics) | HistoryPanel (HistoryTabBar) |
| FilterBar | TimelineView (FilterBar subcomponent) |
| Timeline list + run selection | TimelineView (RunTimeline) |
| SingleRunDetail | TimelineView |
| CompareView | TimelineView |
| History fetch + filter logic | HistoryPanel local state |

**Note**: History data stays as panel-local state (not in the workspace context) because it involves paginated/filtered fetching that only matters when the History panel is active. Only regression detection results are promoted to shared context.

---

## 11. Assertion Health Computation

### useAssertionHealth Hook

Derives badge data from existing APIs (`/stats` and `/history`) -- no new backend endpoints (AC-US4-04).

**Rules**:
- **Flaky**: assertion pass rate between 30-70% across 3+ runs (from `stats.assertionStats`)
- **Non-discriminating**: assertion passes in both latest benchmark AND latest baseline run (compare from history where type=baseline)
- **Regression**: assertion passed in previous run but fails in latest (compare `latestBenchmark` vs second-most-recent from history)

---

## 12. Markdown Preview

The EditorPanel preview uses the existing `parseFrontmatter()` utility for frontmatter and renders the body as formatted `<pre>` text -- same display quality as the existing `SkillContentViewer`. Frontmatter fields render as structured key-value cards (AC-US2-03).

A full markdown renderer (remark/rehype) is out of scope for this increment. The MarkdownPreview component API is designed so internals can be upgraded later without changing consumers.

---

## 13. Sparkline Charts

TestCaseListItem shows a sparkline of recent pass-rate trend using inline SVG (no library). Data source: `api.getCaseHistory()` fetched on TestsPanel mount, cached in panel-local state.

The existing BenchmarkPage already has a nearly identical SVG sparkline implementation (lines 453-483) that will be extracted into the reusable `Sparkline` component.

---

## 14. Concurrent Run Protection

The workspace enforces one-at-a-time runs via the `isRunning` flag in workspace state. All run buttons check this flag. If clicked while running, a toast message appears: "Benchmark already running -- wait or cancel" (AC-US5-07).

The existing `useSSE` hook's `stop()` function is exposed through the context for cancellation.

---

## 15. Implementation Order

Tasks should be implemented in this dependency order:

1. **Backend**: PUT /content endpoint + api.ts client method
2. **Foundation**: workspaceTypes, workspaceReducer, SkillWorkspaceProvider, useSkillWorkspace hook
3. **Shell**: WorkspaceShell, LeftRail, WorkspaceHeader, CSS Grid layout
4. **Route**: Wire SkillWorkspace into App.tsx (keep old routes temporarily)
5. **EditorPanel**: Raw editor + preview + save + dirty indicator
6. **TestsPanel**: Case list + detail + assertion builder + inline results
7. **RunPanel**: Benchmark/baseline/comparison execution + SSE bridge + results
8. **HistoryPanel**: Timeline + per-eval + statistics sub-tabs
9. **DepsPanel**: Thin wrapper around McpDependencies
10. **Cross-panel flows**: Edit-test-iterate loop (Fix with AI -> editor, Apply and Rerun)
11. **Keyboard shortcuts**: useKeyboardShortcuts hook
12. **Assertion health**: Flaky/non-discriminating/regression badges
13. **Polish**: Dirty indicator in rail/header, iteration counter, celebration state, regression banner
14. **Cleanup**: Delete old page files, remove old routes from App.tsx

---

## 16. Risk Mitigation

| Risk | Mitigation |
|------|-----------|
| Large refactor breaks existing functionality | Old pages kept until new workspace is feature-complete; delete only in final task |
| Context re-renders cause performance issues | `useMemo` on expensive derived state; panels only read slices they need |
| SSE bridge complexity | Dedicated `useSSEBridge` hook isolates SSE -> dispatch mapping; tested independently |
| Drag-to-reorder assertions is flaky | Use HTML5 DnD API with `draggable` attribute; fallback to up/down buttons if unreliable |
| Markdown preview quality | Start with pre-formatted text (same as current viewer); upgrade to remark later if needed |
