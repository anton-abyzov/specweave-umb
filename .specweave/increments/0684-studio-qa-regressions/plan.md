# Plan — 0682 Studio QA regressions

## Strategy

Each defect is diagnosed from its `test-results/<slug>/error-context.md` page snapshot plus the relevant source file. Fixes are **local** — no cross-component refactors, no API changes, no new deps. Each task writes (or reuses) the failing E2E spec as its acceptance test, then modifies the source to make it pass.

---

## Component-by-component diagnosis

### B1 — Sidebar section collapse does not persist (AC-US1-01)
- **Source**: `src/eval-ui/src/components/SidebarSection.tsx` (160 lines)
- **Keys**: `vskill-sidebar-own-collapsed`, `vskill-sidebar-installed-collapsed` (already declared at lines 25, 33, 42–43).
- **Suspected root cause**: one of
  1. `useState` initial value reads from `localStorage` **but** the component re-initializes from a prop default on each mount (hydration overrides reload state).
  2. The `useEffect` writes back, but the initial render uses `defaultCollapsed` instead of reading the stored value.
  3. A parent (`Sidebar.tsx`) passes a controlled `collapsed` prop whose source doesn't hydrate from localStorage.
- **Evidence**: page snapshot shows `[expanded]` state immediately after reload even when the test collapsed it pre-reload.
- **Fix sketch**: ensure the `useState` initializer function reads `localStorage.getItem(key)` synchronously (lazy initializer) and that no `useEffect` subsequently overwrites it with a default. Add a unit test in `components/__tests__/SidebarSection.test.tsx` (if missing) for the hydration branch.
- **Acceptance**: `qa-click-audit.spec.ts:174` AND `sidebar-split.spec.ts:47` pass.

### B2 — Theme toggle broken on light→dark branch (AC-US2-01, AC-US2-02)
- **Sources**:
  - `src/eval-ui/src/App.tsx` (235 lines) — lines 123, 149, 153 define three `setTheme` call sites: one Cmd+Shift+D cycle (`light→dark→auto→light`), two toggle handlers (`light↔dark`).
  - `src/eval-ui/src/theme/ThemeProvider.tsx` (165 lines) — `setTheme` callback at line 147.
  - `src/eval-ui/src/components/StatusBar.tsx` — `setTheme(next)` at line 96.
- **Suspected root cause**: the existing `theme-persistence.spec.ts:79` passes for `dark→auto`, so `setTheme("auto")` + localStorage write work. The failure is that `setTheme("dark")` from an initial `mode === "light"` never mutates `data-theme`. Likely candidates:
  1. The `mode === "light" ? "dark" : ...` ternary at App.tsx:123 and StatusBar's `next` calculation disagree on the cycle order, so one branch produces the current mode as its `next` and no-ops.
  2. `ThemeProvider.setTheme` has an early-return when `mode === newMode` that triggers because `resolvedTheme` and `mode` are conflated.
- **Evidence**: the error-context snapshot shows `button "Switch to dark theme" ... "light"` (status-bar still labeled "Switch to dark theme" after the shortcut, confirming the mode didn't change).
- **Fix sketch**: trace `setTheme("dark")` end-to-end from `mode === "light"`. Verify the cycle math in App.tsx:123 (`light → dark`) and StatusBar:96 match, and that ThemeProvider.setTheme writes `document.documentElement.dataset.theme` synchronously for every incoming mode.
- **Acceptance**: `keyboard-shortcuts.spec.ts:100` AND `qa-click-audit.spec.ts:230` pass; `theme-persistence.spec.ts` still passes (no regression).

### B3 — j/k doesn't set aria-selected (AC-US1-02)
- **Sources**:
  - `src/eval-ui/src/hooks/useKeyboardShortcut.ts` (167 lines)
  - `src/eval-ui/src/components/Sidebar.tsx` (consumer — the `j`/`k` handler)
  - `src/eval-ui/src/components/SkillRow.tsx` (the row that needs `aria-selected`)
- **Suspected root cause**: j/k handler either (a) doesn't fire when no row is selected (missing "select first on no-selection" fallback), or (b) updates selection state but `SkillRow` doesn't read that state into `aria-selected`.
- **Evidence**: error-context snapshot shows `button "test-skill"` with no `aria-selected` attribute. Fixture has exactly one row so `j` should select it.
- **Fix sketch**: in the j/k handler, if `selectedIndex === null`, set it to `0`. Ensure `SkillRow` renders `aria-selected={isSelected}` and `data-testid="skill-row"` (the spec locator).
- **Acceptance**: `keyboard-shortcuts.spec.ts:47` passes.

### B4 — Cmd+B doesn't toggle sidebar (AC-US1-03)
- **Sources**:
  - `src/eval-ui/src/App.tsx` — keyboard registration site (App declares `setTheme` keybindings here; Cmd+B should be sibling).
  - `src/eval-ui/src/components/StudioLayout.tsx` — the layout that renders `<aside aria-label="Skills sidebar">`.
  - `src/eval-ui/src/components/ShortcutModal.tsx:53` already documents `⌘B` → `toggleSidebar`, so the label is wired but the **handler isn't**.
- **Suspected root cause**: keybinding declared in cheatsheet UI but no `useKeyboardShortcut` registration actually mutates a layout state. Need to add `sidebarHidden` state (lift to `StudioLayout` or `App`), gate `<aside>` rendering (or `display`/`aria-hidden`), and register a `mod+B` handler that toggles it.
- **Evidence**: error-context snapshot shows the aside fully rendered after Cmd+B; neither `display:none` nor unmount happened.
- **Fix sketch**: add local `const [sidebarHidden, setSidebarHidden] = useState(false)` in `StudioLayout.tsx`; register `useKeyboardShortcut({ key: "b", modifiers: ["mod"] }, () => setSidebarHidden(h => !h))`; conditionally render (or `hidden`-attr) the aside. Per spec decision (see non-goals): no reload persistence required.
- **Acceptance**: `keyboard-shortcuts.spec.ts:85` passes.

### B5 — Leaderboard tab missing from LeftRail (AC-US3-01, AC-US3-02)
- **Source**: `src/eval-ui/src/pages/workspace/LeftRail.tsx` — `PANEL_GROUPS` at lines 17–39 defines Build / Evaluate / Insights groups. Insights group currently has only History + Deps.
- **Upstream already wired**: `SkillWorkspace.tsx:16` imports `LeaderboardPanel`; `VALID_PANELS` at line 20 + 71 include `"leaderboard"`; line 144 renders `<LeaderboardPanel />` when `state.activePanel === "leaderboard"`. **Only the LeftRail entry is missing.**
- **Fix**: add `{ id: "leaderboard", label: "Leaderboard", shortcut: "7" }` to the Insights group. Add a `PanelIcon` case for `leaderboard` (a podium / bar-chart SVG).
- **Acceptance**: `leaderboard.spec.ts:5` AND `leaderboard.spec.ts:13` pass.

### B6 — TestsPanel filter tabs not rendered (AC-US3-03, AC-US3-04)
- **Source**: `src/eval-ui/src/pages/workspace/TestsPanel.tsx:383` (`hasIntegrationTests && (...)` wraps the filter-tab group).
- **Root cause**: the conditional guard hides the entire All/Unit/Integration tab group when no integration tests exist. The test fixture (`e2e/fixtures/test-plugin/skills/test-skill/evals/evals.json`) has only unit tests, so the group never renders.
- **Fix**: remove the `hasIntegrationTests &&` guard — render the tab group unconditionally with its count labels (line 297–299 already computes zero-count labels cleanly: `Integration (0)`).
- **Side-effect check**: confirm no layout regression with only unit tests; the counts at line 297–299 handle zero gracefully.
- **Acceptance**: `tests-panel.spec.ts:5` AND `tests-panel.spec.ts:30` pass.

### B7 — Breadcrumb test drift (spec update, not defect)
- **Source**: `e2e/qa-click-audit.spec.ts:44` asserts `linkCount === 0` as a regression canary. Snapshot shows 2 interactive breadcrumb anchors (correctly added in T-059 during 0674).
- **Fix**: update the spec expectation — either (a) assert count `=== 2` with a comment explaining T-059 shipped interactivity, or (b) switch to an aria-based assertion that validates the breadcrumb nav has labelled buttons for each segment. Preferred: (b) — more resilient to future changes.
- **Note**: this is documented at the bottom of `tasks.md` under "Related spec updates".

### B8 — Escape doesn't early-dismiss the 'e' toast (AC-US4-01)
- **Sources**:
  - `src/eval-ui/src/components/Toast.tsx` / `ToastProvider.tsx` — has `onDismiss` wiring
  - `src/eval-ui/src/hooks/useKeyboardShortcut.ts` — Escape registration order
  - Whoever fires the `'e'` placeholder toast (likely `App.tsx` or a top-level handler)
- **Suspected root cause**: multiple keybindings register for Escape (cheatsheet modal close, command-palette close, context-menu close). The toast-dismiss handler is either (a) registered last and shadowed by an earlier handler that calls `event.preventDefault()` / `event.stopPropagation()`, or (b) not registered at all — Toast's internal Escape listener is attached to a ref that isn't focused.
- **Fix sketch**: subscribe the ToastProvider to a global Escape handler that dismisses the most-recent toast (stack-popping). Ensure registration runs regardless of focused element. Preserve the priority order for modal/palette close handlers (they should still win when open).
- **Acceptance**: `qa-click-audit.spec.ts:385` passes.

---

## Performance triage

### Perf-1 — page load 1914 ms vs 1000 ms (AC-US5-01)
- **Context**: first navigation to `/` includes dev-server cold-boot + uncached Vite bundle. On warm CI this likely drops significantly.
- **Approach**:
  1. Record a Chrome performance trace locally with a warm server. Compare against headless run.
  2. If warm-vs-cold gap > 500 ms, raise the budget to `1200 ms` and add a comment in the spec explaining the measurement context (not a regression).
  3. If cold and warm both exceed 1500 ms, investigate heaviest imports (look for Monaco, Recharts, Mermaid — lazy-load candidates via dynamic `import()`).

### Perf-2 — search filter 313 ms vs 160 ms hard (AC-US5-02)
- **Target**: `src/eval-ui/src/components/PluginGroup.tsx`, `SkillRow.tsx`, `SidebarSearch.tsx`.
- **Likely wins**: wrap `PluginGroup` / `SkillRow` in `React.memo`; ensure filter predicate is stable (`useCallback`); use `useDeferredValue` on the search input. Fixtures have exactly one row so the fix must not break zero/one-row rendering.
- **Target**: hard budget ≤ 160 ms passes; soft 80 ms is a stretch goal.

### Perf-3 — FCP null under headless Chromium (AC-US5-03)
- **Target**: `e2e/lighthouse-budget.spec.ts:31`.
- **Fix**: guard the assertion — `test.skip(entries.length === 0, 'FCP not emitted by headless chromium in this env')` with a log line explaining. Alternatively (better long-term): wire a `PerformanceObserver({ type: "paint" })` in `main.tsx` that records into a custom window-exposed mark the spec can read.

---

## ADR

### ADR-0682-A — Sidebar collapse state is durable via localStorage, not URL / server
**Context**: B1 requires the OWN/INSTALLED collapse state to survive reloads.
**Options**:
1. **localStorage** (chosen) — already scaffolded; keys `vskill-sidebar-own-collapsed`, `vskill-sidebar-installed-collapsed`; scope per-origin.
2. URL query params — shareable but clutters URLs users never read.
3. Server-side preference — overkill for a local studio; no existing prefs endpoint.
**Decision**: Fix the existing localStorage path (fix the hydration bug). Do not introduce a new persistence mechanism. Falls back to in-memory when localStorage is unavailable (edge-case noted in spec).
**Consequences**: preference is per-browser-origin, not per-user. Acceptable for local-only Studio usage. No cross-device sync.

No other decisions warrant an ADR — every other fix is a straightforward correction to existing wiring.

---

## Execution order

1. B5 → lowest risk, single-file change; unblocks 2 specs immediately.
2. B6 → single-file guard removal; unblocks 2 specs.
3. B1 → single-component hydration fix; unblocks 2 specs.
4. B3 → hook/consumer aria-selected wiring.
5. B4 → new layout state + keybinding.
6. B8 → ToastProvider Escape subscription.
7. B2 → trace theme cycle math (most subtle — left for last so easy wins are already green).
8. Perf triage (AC-US5-01/02/03) in parallel once defects are green.
9. B7 → update the breadcrumb regression spec (spec-only change).

Full Playwright run after each task to catch regressions.
