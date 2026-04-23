# Tasks — 0682 Studio QA regressions

All tasks target `repositories/anton-abyzov/vskill/`. For each defect the **failing E2E spec is the acceptance test** — no selector or expectation rewrites allowed (except T-011, the breadcrumb reconciliation).

---

### T-001: Fix OWN/INSTALLED sidebar section collapse persistence (B1)
**User Story**: US-001 | **AC**: AC-US1-01 | **Status**: [ ] pending
**File(s)**: `src/eval-ui/src/components/SidebarSection.tsx` (+ companion test if missing)
**Test Plan**:
- **Given** the Studio is open at `/` with the OWN section expanded (`aria-expanded="true"`)
- **When** the user clicks the OWN section header to collapse it and reloads the page
- **Then** after reload, the OWN section button still has `aria-expanded="false"` (collapsed state persisted via `localStorage` key `vskill-sidebar-own-collapsed`)
- **Acceptance spec**: `e2e/qa-click-audit.spec.ts:174` "section collapse persistence [AC-US1-05]" AND `e2e/sidebar-split.spec.ts:47` "collapse state for OWN section persists across reload" — both must pass.

---

### T-002: Fix theme toggle from `data-theme="light"` branch (B2)
**User Story**: US-002 | **AC**: AC-US2-01, AC-US2-02 | **Status**: [ ] pending
**File(s)**: `src/eval-ui/src/App.tsx` (lines 123, 149, 153), `src/eval-ui/src/theme/ThemeProvider.tsx` (line 147), `src/eval-ui/src/components/StatusBar.tsx` (line 96)
**Test Plan**:
- **Given** the Studio is loaded with `document.documentElement.dataset.theme === "light"`
- **When** the user presses `Cmd+Shift+D` (macOS) / `Ctrl+Shift+D` (other) OR clicks the status-bar theme button
- **Then** `document.documentElement.dataset.theme === "dark"` within 150 ms AND `localStorage.getItem("vskill-theme")` reflects the new mode
- **And** the existing `theme-persistence.spec.ts:79` (dark → auto) still passes (no regression)
- **Acceptance specs**: `e2e/keyboard-shortcuts.spec.ts:100` AND `e2e/qa-click-audit.spec.ts:230` pass.

---

### T-003: j/k keyboard navigation sets `aria-selected` on a skill row (B3)
**User Story**: US-001 | **AC**: AC-US1-02 | **Status**: [ ] pending
**File(s)**: `src/eval-ui/src/hooks/useKeyboardShortcut.ts`, `src/eval-ui/src/components/Sidebar.tsx`, `src/eval-ui/src/components/SkillRow.tsx`
**Test Plan**:
- **Given** the Studio is open at `/` with one or more skill rows in the sidebar and body focus (no input focused)
- **When** the user presses `j`
- **Then** exactly one `[data-testid='skill-row']` in the sidebar has `aria-selected="true"` (select-first if none was previously selected)
- **And** pressing `j` again moves selection to the next row (or stays on last); `k` moves backward
- **Edge case**: with zero rows, the handler is a no-op (does not throw)
- **Acceptance spec**: `e2e/keyboard-shortcuts.spec.ts:47` "T-050 — `j`/`k` move selection in the sidebar".

---

### T-004: Cmd+B toggles skills-sidebar visibility (B4)
**User Story**: US-001 | **AC**: AC-US1-03 | **Status**: [ ] pending
**File(s)**: `src/eval-ui/src/components/StudioLayout.tsx` (state + conditional render), `src/eval-ui/src/App.tsx` or the shortcut registration site (keybinding)
**Test Plan**:
- **Given** the Studio is open at `/` with `aside[aria-label='Skills sidebar']` visible
- **When** the user presses `Cmd+B` (macOS) / `Ctrl+B` (other)
- **Then** the aside transitions to hidden (unmounted, `hidden` attribute, or `display: none` — any mechanism that makes `expect(aside).not.toBeVisible()` pass)
- **When** the user presses `Cmd+B` again
- **Then** the aside is visible again
- **Non-goal**: visibility state does NOT persist across reload.
- **Acceptance spec**: `e2e/keyboard-shortcuts.spec.ts:85` "T-050 — Cmd/Ctrl+B toggles sidebar visibility".

---

### T-005: Add Leaderboard panel to workspace LeftRail (B5)
**User Story**: US-003 | **AC**: AC-US3-01, AC-US3-02 | **Status**: [ ] pending
**File(s)**: `src/eval-ui/src/pages/workspace/LeftRail.tsx` (add entry + icon)
**Test Plan**:
- **Given** the Studio is open at a skill detail page and the workspace panel is active
- **When** the DOM is queried
- **Then** `text=Leaderboard` is visible in the LeftRail, inside the "Insights" panel group
- **And** clicking the Leaderboard entry sets `state.activePanel === "leaderboard"` and renders `LeaderboardPanel` (with its empty-state UI when no sweep data exists)
- **Acceptance specs**: `e2e/leaderboard.spec.ts:5` "leaderboard tab is visible in workspace" AND `e2e/leaderboard.spec.ts:13` "leaderboard panel shows empty state when no sweep data".

---

### T-006: TestsPanel filter tabs render unconditionally (B6)
**User Story**: US-003 | **AC**: AC-US3-03, AC-US3-04 | **Status**: [ ] pending
**File(s)**: `src/eval-ui/src/pages/workspace/TestsPanel.tsx` (remove `hasIntegrationTests && (...)` guard at ~line 383)
**Test Plan**:
- **Given** the Studio is open at a skill detail page, the Tests panel is active, and the skill has zero integration tests
- **When** the DOM is rendered
- **Then** `button:has-text("All")`, `button:has-text("Unit")`, and `button:has-text("Integration")` all exist in the DOM (Integration tab shows `(0)` count)
- **When** the user clicks "Unit"
- **Then** only unit-type test case rows are rendered in the list
- **Acceptance specs**: `e2e/tests-panel.spec.ts:5` AND `e2e/tests-panel.spec.ts:30`.

---

### T-007: Escape early-dismisses the `'e'`-placeholder toast (B8)
**User Story**: US-004 | **AC**: AC-US4-01 | **Status**: [ ] pending
**File(s)**: `src/eval-ui/src/components/ToastProvider.tsx` (add global Escape listener), possibly `src/eval-ui/src/hooks/useKeyboardShortcut.ts` (priority ordering)
**Test Plan**:
- **Given** the Studio is open at `/` with no toasts active, and the user presses `'e'` (triggering the placeholder toast)
- **When** the user then presses `Escape`
- **Then** the toast is removed from the DOM within 150 ms (toast count = 0)
- **Edge case**: if multiple toasts are stacked, Escape dismisses only the most-recent (LIFO); preserve the existing higher-priority Escape handlers (cheatsheet close, command-palette close, context-menu close) so those win when open.
- **Acceptance spec**: `e2e/qa-click-audit.spec.ts:385` "toast lifecycle [AC-US4-08]".

---

### T-008: Triage eval-ui page-load perf (1914 ms vs 1000 ms budget) (Perf-1)
**User Story**: US-005 | **AC**: AC-US5-01 | **Status**: [ ] pending
**File(s)**: investigation first; then either `e2e/eval-ui.spec.ts:168` (raise budget with comment) OR `src/eval-ui/src/main.tsx` + route code (lazy-load heavy imports — Monaco, Recharts, Mermaid candidates)
**Test Plan**:
- **Given** a warm dev server (pre-booted at least 30 s before the run)
- **When** Playwright navigates to `/` and measures time-to-`networkidle`
- **Then** the measurement is under **1200 ms** (new documented budget) OR under **1000 ms** (original budget, if lazy-load quick-win lands)
- **Investigation output**: a bullet list in the task closure log naming the 3 heaviest imports and whether each was lazy-loaded.

---

### T-009: Triage sidebar-search filter perf (313 ms vs 160 ms hard) (Perf-2)
**User Story**: US-005 | **AC**: AC-US5-02 | **Status**: [ ] pending
**File(s)**: `src/eval-ui/src/components/PluginGroup.tsx`, `src/eval-ui/src/components/SkillRow.tsx`, `src/eval-ui/src/components/SidebarSearch.tsx`
**Test Plan**:
- **Given** the Studio is open at `/` with at least one skill row rendered
- **When** the user types a character into the sidebar search input and Playwright measures the time until the filtered list is repainted
- **Then** the measurement is under **160 ms** (hard budget, blocker); the **80 ms** soft budget is aspirational
- **Quick wins to try first**: `React.memo` on `PluginGroup` + `SkillRow`, `useDeferredValue` on the search query, `useCallback` on the filter predicate.
- **Acceptance spec**: `e2e/performance-marks.spec.ts:74` hard-budget branch passes.

---

### T-010: Triage FCP under headless Chromium (null entry) (Perf-3)
**User Story**: US-005 | **AC**: AC-US5-03 | **Status**: [ ] pending
**File(s)**: `e2e/lighthouse-budget.spec.ts` (guard against null) — and optionally `src/eval-ui/src/main.tsx` (emit a paint marker via `PerformanceObserver`)
**Test Plan**:
- **Given** Playwright runs against headless Chromium where `performance.getEntriesByName('first-contentful-paint')` returns `[]`
- **When** `e2e/lighthouse-budget.spec.ts:31` executes
- **Then** the spec emits `test.skip(true, 'FCP not emitted by headless chromium in this env')` with a console log — does NOT fail
- **Alternative (preferred if tractable)**: add a `PerformanceObserver({ type: "paint" })` in `main.tsx` that stores `paint.startTime` on `window.__vskillPaint` and update the spec to read that marker as a fallback.

---

## Related spec updates

### T-011: Reconcile breadcrumb regression canary with T-059 interactive breadcrumbs (B7)
**File(s)**: `e2e/qa-click-audit.spec.ts:44` (the test "breadcrumb items are rendered but currently NOT interactive — regression tracked in qa-findings.md")
**Nature**: test-spec drift, not a source defect. Interactive breadcrumbs shipped intentionally in T-059 during 0674; the test was pinned to `linkCount === 0` as a canary and must now be updated.
**Action**: rewrite the assertion to either
- (a) `expect(linkCount).toBe(2)` with a comment referencing T-059 / 0674 as the source of the change, OR
- (b) **preferred**: switch to an aria-based assertion that asserts the breadcrumb nav has a labelled button for each segment (`Own`, `test-plugin`) and that the current segment (`test-skill`) is **not** interactive — more resilient to future breadcrumb changes.

Update `qa-findings.md` to reflect that the regression canary was closed in this increment.

**Status**: [ ] pending
