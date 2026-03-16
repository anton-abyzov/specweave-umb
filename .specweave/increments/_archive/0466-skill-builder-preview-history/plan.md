# Architecture Plan: Skill Builder MD Preview & Per-Case History

## Overview

Two independent features sharing a utility-extraction prerequisite: (1) render SKILL.md body as formatted HTML in the EditorPanel preview pane, (2) embed per-case execution history directly inside TestsPanel's CaseDetail view. Both require extracting shared utilities from HistoryPerEval.tsx into a common module.

## Architecture Decisions

### AD-1: Custom renderMarkdown as pure function

**Decision**: Port `renderMarkdown()` from `vskill-platform/EvalCaseCard.tsx` into `src/eval-ui/src/utils/renderMarkdown.ts` as a pure `string -> string` function. Extend with table support and link `target="_blank"` attributes.

**Rationale**: The spec explicitly forbids adding external markdown libraries (react-markdown, remark, etc.). The existing implementation in vskill-platform already handles headers, bold, italic, code blocks, inline code, lists, and links via chained regex replacements. This is a local dev tool with no XSS risk, so `dangerouslySetInnerHTML` is acceptable.

**Extension points beyond the port**:
- Table rendering: detect pipe-delimited rows, emit `<table>` with `<thead>`/`<tbody>`
- Links: add `target="_blank" rel="noopener noreferrer"` to generated `<a>` tags
- Style tokens: use CSS custom properties (`var(--text-primary)`, `var(--surface-2)`) consistent with eval-ui's design system rather than vskill-platform's hard-coded rgba values

### AD-2: Shared history utilities module

**Decision**: Extract `passRateColor`, `shortDate`, `fmtDuration`, and `MiniTrend` from `HistoryPerEval.tsx` into `src/eval-ui/src/utils/historyUtils.tsx`. HistoryPerEval and the new CaseHistorySection both import from this shared module.

**Rationale**: These four utilities are needed in both HistoryPerEval (full history panel) and CaseDetail (inline history in TestsPanel). Duplication would cause visual inconsistency if either copy drifts. The `.tsx` extension is required because `MiniTrend` returns JSX.

**Export list**:
- `passRateColor(rate: number): string` -- pure function
- `shortDate(iso: string): string` -- pure function
- `fmtDuration(ms: number | undefined): string` -- pure function
- `MiniTrend({ entries }: { entries: CaseHistoryEntry[] }): JSX.Element | null` -- React component

### AD-3: CaseHistorySection as a local component within TestsPanel

**Decision**: Add `CaseHistorySection` as a local function component inside `TestsPanel.tsx` (not a separate file). It is rendered at the bottom of `CaseDetail`, below the existing `OutputSection`.

**Rationale**: The component is tightly coupled to `CaseDetail`'s layout and props. It uses `useWorkspace()` to get `plugin`/`skill` for the API call and `dispatch` for panel switching. Keeping it in-file follows the existing pattern where `CaseDetail`, `AssertionRow`, `Section`, `StatusPill`, `MiniSparkline`, `OutputSection`, and `NewCaseForm` are all local to `TestsPanel.tsx`.

**Behavior**:
- Collapsible section (collapsed by default), matching `OutputSection`'s chevron pattern
- On expand: calls `api.getCaseHistory(plugin, skill, evalId)`, limits display to 10 entries
- Loading state: spinner (existing `.spinner` class)
- Empty state: "No history for this case" text
- Each entry shows: timestamp, model, run type badge, pass rate, duration, tokens, per-assertion pass/fail with reasoning
- "View full history" link at bottom: `dispatch({ type: "SET_PANEL", panel: "history" })`
- Caches fetched history in local state keyed by evalId to avoid refetching on collapse/expand

## Component Boundaries

```
src/eval-ui/src/
  utils/
    renderMarkdown.ts        [NEW]  pure fn, string -> string
    historyUtils.tsx          [NEW]  extracted from HistoryPerEval
    __tests__/
      renderMarkdown.test.ts  [NEW]  TDD: covers all markdown features
      historyUtils.test.tsx   [NEW]  TDD: covers pure fns + MiniTrend rendering
  pages/workspace/
    EditorPanel.tsx           [MOD]  import renderMarkdown, replace <pre> body with dangerouslySetInnerHTML div
    TestsPanel.tsx            [MOD]  add CaseHistorySection below OutputSection in CaseDetail
  components/
    HistoryPerEval.tsx        [MOD]  remove local passRateColor/shortDate/fmtDuration/MiniTrend, import from utils
```

## Data Flow

### Markdown Preview (EditorPanel)

```
skillContent (string from WorkspaceState)
  |
  parseFrontmatter()  -->  { metadata, body }
  |
  body  -->  renderMarkdown(body)  -->  HTML string
  |
  <div dangerouslySetInnerHTML={{ __html: html }} />
```

No new state, no new API calls. The preview updates reactively on every `SET_CONTENT` dispatch since `skillContent` is already in the render path.

### Per-Case History (TestsPanel CaseDetail)

```
CaseDetail receives evalCase.id
  |
  CaseHistorySection (collapsed by default)
  |
  [user clicks expand]
  |
  api.getCaseHistory(plugin, skill, evalCase.id)
  |           ^--- from useWorkspace()
  |
  CaseHistoryEntry[]  (limit display to 10)
  |
  Render using: shortDate, passRateColor, fmtDuration, MiniTrend
  |
  "View full history"  -->  dispatch({ type: "SET_PANEL", panel: "history" })
```

History is fetched lazily on first expand and cached in a `useState<Record<number, CaseHistoryEntry[]>>` local to `CaseHistorySection`. This matches the caching pattern already used in `HistoryPerEval.tsx`.

## Implementation Strategy

### Phase 1: Utility extraction and creation (US-004, US-001)

1. **Extract historyUtils.tsx** -- Move 4 items from HistoryPerEval, update HistoryPerEval imports. Run existing tests to confirm no regression.
2. **Create renderMarkdown.ts** -- Port from vskill-platform, add table support and link attributes. Write comprehensive tests first (TDD red phase).

### Phase 2: Feature integration (US-002, US-003)

3. **EditorPanel markdown preview** -- Replace `<pre>{body}</pre>` with `<div dangerouslySetInnerHTML>`. Add prose styling for proper markdown rendering.
4. **CaseHistorySection in TestsPanel** -- Add collapsible section below OutputSection, wire up API fetch, render history entries with shared utilities.

### Ordering rationale

US-004 (extraction) and US-001 (renderMarkdown) are pure infrastructure with no UI dependencies, so they come first and can be fully tested in isolation. US-002 and US-003 depend on these utilities.

## Markdown Preview CSS Strategy

The `renderMarkdown()` function outputs HTML with inline styles (matching the vskill-platform approach). For the EditorPanel preview, the wrapping `<div>` sets base prose styling:

```
font-size: 13px;
line-height: 1.7;
color: var(--text-secondary);
```

The renderMarkdown function's inline styles handle element-specific formatting (headers, code blocks, list indentation). No new CSS file is needed -- the inline style approach keeps everything self-contained.

## Styling Adaptation (vskill-platform -> eval-ui)

The ported `renderMarkdown` must adapt style tokens:

| vskill-platform token | eval-ui equivalent |
|---|---|
| `var(--card-text)` | `var(--text-primary)` |
| `rgba(255,255,255,0.05)` | `var(--surface-2)` |
| `rgba(255,255,255,0.06)` | `var(--surface-3)` |

These substitutions ensure the rendered markdown matches the eval-ui dark theme.

## Testing Strategy (TDD)

All tests written before implementation (TDD red phase).

### renderMarkdown.test.ts
- Headers h1-h3 produce correct HTML with appropriate styles
- Bold/italic produce `<strong>`/`<em>`
- Inline code produces styled `<code>`
- Fenced code blocks produce `<pre><code>` with preserved whitespace
- Unordered/ordered lists produce indented divs
- Links produce `<a target="_blank" rel="noopener noreferrer">`
- Tables produce `<table>` with `<thead>`/`<tbody>`
- Empty/undefined input returns empty string
- Mixed content renders all elements correctly

### historyUtils.test.tsx
- `passRateColor`: returns green/yellow/red at thresholds (0.8, 0.5)
- `shortDate`: formats ISO string to "Mon DD, HH:MM"
- `fmtDuration`: formats ms to "Xs" or "Xms", handles undefined
- `MiniTrend`: renders null for <2 entries, renders SVG polyline for 2+ entries

### Integration verification
- EditorPanel: manual verification that preview renders markdown (deferred to manual QA gate)
- CaseHistorySection: manual verification of expand/collapse, API integration, panel switch link

## Risk Assessment

| Risk | Mitigation |
|---|---|
| renderMarkdown regex edge cases (nested bold/italic) | Spec explicitly scopes out full markdown compliance. Test common patterns only. |
| Table regex complexity | Tables require detecting header separator row. Keep regex simple: split by newline, check for separator, emit table HTML. |
| HistoryPerEval visual regression after extraction | Extraction is purely mechanical (move + re-import). No logic changes. |
| CaseHistorySection re-renders on every CaseDetail mount | Cache history in local state keyed by evalId. Only fetch on first expand per case. |

## No New Dependencies

Zero new npm packages. `renderMarkdown` is pure regex string processing. All UI uses existing Tailwind classes, CSS custom properties, and inline SVG patterns already established in the codebase.
