# Implementation Plan: Studio detail page — SubTabBar + Overview right-rail

## Architecture overview

### Part A — SubTabBar component (new)

`src/eval-ui/src/components/SubTabBar.tsx` — descriptor-driven secondary tab bar. Mirrors the top-level tab bar pattern in `RightPanel.tsx` (data-testid wiring, role="tab", aria-selected, 2px underline) but at smaller scale (12px font, 6px-8px padding) so it visually nests as a sub-bar.

```ts
interface SubTabDescriptor {
  id: string;
  label: string;
}

interface Props {
  tabs: SubTabDescriptor[];
  active: string;
  onChange: (id: string) => void;
}
```

### Part B — RightPanel sub-tab wiring + safeActive fix

`src/eval-ui/src/components/RightPanel.tsx`:

1. New constant `SUB_TAB_DESCRIPTORS: Partial<Record<DetailTab, SubTabDescriptor[]>>`:
   - `run` → `[{id: "run", label: "Run"}, {id: "history", label: "History"}, {id: "models", label: "Models"}]`
   - `activation` → `[{id: "run", label: "Run"}, {id: "history", label: "History"}]`

2. New helpers:
   - `readInitialSub(active)` — reads `?sub=` from URL, validates against the active tab's descriptors, falls back to the first descriptor.
   - `defaultSubFor(active)` — returns `"run"` if descriptors exist, else `null`.

3. `IntegratedDetailShell`:
   - Add `[sub, setSub]` state initialized via `readInitialSub(initialActive)`.
   - The URL-sync effect now reads `(active, sub)` and writes both params atomically.
   - When `active` changes, reset `sub` to `defaultSubFor(newActive)`.
   - When sub-tab changes for the active tab, just update `?sub=`.

4. `WorkspacePanel` signature: `({ active, sub })`. Dispatch logic:
   - `(run, history)` → `<HistoryPanel />`
   - `(run, models)` → `<LeaderboardPanel />`
   - `(run, run)` (default) → `<RunPanel />`
   - `(activation, history)` → `<ActivationPanel showOnlyHistory />` (or full `ActivationPanel` if no clean extraction)
   - `(activation, run)` (default) → `<ActivationPanel />`
   - All other top-level tabs ignore `sub`.

5. **F-004 fix**: `WorkspaceTabSync` + `WorkspacePanel` receive `safeActive` (post-redirect) instead of pre-redirect `active`.

6. SubTabBar renders below the top-level tab bar when `SUB_TAB_DESCRIPTORS[safeActive]` is defined.

### Part C — SkillOverview right-rail

`src/eval-ui/src/components/SkillOverview.tsx`:

1. Outer wrapper switches from vertical-flex to CSS grid:
   ```css
   display: grid;
   grid-template-columns: 1fr;          /* < 900px (mobile fallback) */
   grid-template-columns: minmax(0, 1fr) 280px; /* >= 900px via @media */
   gap: 16px;
   ```

2. New `SkillOverviewRightRail.tsx`:
   - `<section data-testid="overview-rightrail-setup">` — wraps `<McpDependencies plugin skill />`. Section heading "Setup".
   - `<section data-testid="overview-rightrail-credentials">` — wraps `<CredentialManager plugin skill />`. Section heading "Credentials".
   - Both sections render even when empty (their internal empty states already handle "No deps detected" / "No credentials configured").

3. Existing `SkillOverview` content (header + PublishStatusRow + metric grid) stays in the main column.

4. Below 900px the grid collapses to a single column — the right-rail naturally falls under the metric grid via grid-template-columns: 1fr media-query.

## File ownership

| File | Change | LOC delta |
|---|---|---|
| `src/eval-ui/src/components/SubTabBar.tsx` | NEW | +60 |
| `src/eval-ui/src/components/RightPanel.tsx` | MODIFIED — sub-tab wiring + safeActive fix | +50 |
| `src/eval-ui/src/components/SkillOverview.tsx` | MODIFIED — wrap in grid + mount RightRail | +15 |
| `src/eval-ui/src/components/SkillOverviewRightRail.tsx` | NEW | +40 |
| `src/eval-ui/src/components/__tests__/SubTabBar.test.tsx` | NEW — pure-fn tests for descriptors + URL helpers | +50 |
| `src/eval-ui/src/components/__tests__/RightPanel.flatTabs.test.tsx` | MODIFIED — assertions for sub-tabs | +30 |

## Test strategy

### Pure-function tests (no DOM, no React renderer needed)

Two helpers in `RightPanel.tsx` are pure:
- `readInitialSub(active: DetailTab, search: string): string`
- `defaultSubFor(active: DetailTab): string | null`

Test by calling them with synthetic `?panel=run&sub=history` strings.

### Element-tree tests (existing pure-function-call pattern)

`RightPanel.flatTabs.test.tsx` already calls `RightPanel({ selectedSkillInfo, activeDetailTab })` and walks the React element tree. Extend it:
- For source-origin skill with `activeDetailTab: "run"`: assert SubTabBar element exists with 3 children.
- For consumer skill with `activeDetailTab: "activation"`: assert SubTabBar element exists with 2 children.
- For `activeDetailTab: "versions"`: assert NO SubTabBar element.

### Build verification

`npx tsc --noEmit` + `npm run build` + `npm run build:eval-ui` must all be green. Failure is blocking.

## Migration order

1. Part A (SubTabBar component, no consumers) — lowest risk.
2. Part C (SkillOverview right-rail) — independent of Part B.
3. Part B (RightPanel wiring + safeActive) — wires Part A in; keeps DepsPanel deep-link working for back-compat.
4. Verification (tsc + tests + build).

## Risk register

- **R-1 URL sync race**: dual `useEffect` writes to `?panel=` + `?sub=` could race. Mitigation: single effect that reads `(active, sub)` and writes both atomically.
- **R-2 ActivationPanel history extraction**: ActivationPanel embeds its own history list. If extraction is non-trivial, fall back to mounting full ActivationPanel for both sub-modes (history shows up inside it as today). Acceptable simplification — AC-US2-02 is already permissive about extraction.
- **R-3 Right-rail fetches**: fetches kick on Overview mount. If breaking the existing fetch contract surfaces flakes, the right-rail can be lazy-mounted behind an IntersectionObserver. Defer optimization unless flakes appear.
- **R-4 Width breakpoint**: 900px is one author judgment. Acceptable for v1; can be tuned if user feedback diverges.

## References

- Increment 0769 (immediate predecessor): T-021/T-022 deferred → US-001/US-002 here. T-025 deferred → US-003 here. F-004 → US-004 here.
- `HistoryPanel.tsx` (605 lines), `LeaderboardPanel.tsx` (526 lines), `ActivationPanel.tsx` (586 lines), `RunPanel.tsx` (644 lines) — existing standalone panels, no rewrites needed.
- `DepsPanel.tsx` (47 lines) — kept as-is for `?panel=deps` deep-link back-compat.
- `McpDependencies.tsx`, `CredentialManager.tsx` — existing components, reused inside `SkillOverviewRightRail`.
