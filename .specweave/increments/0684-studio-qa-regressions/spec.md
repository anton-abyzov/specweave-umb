---
status: completed
---
# Increment 0682 — Studio QA regressions (post-0674)

## Context

Playwright executed the full shipped-0674 studio spec suite for the first time on 2026-04-23. Specs were authored during 0674 but never run end-to-end; the first verifier pass surfaced **7 real UI defects, 1 test-drift case, and 3 perf-budget failures** across 56 tests (38 pass / 15 fail / 3 `test.fixme`).

This increment is a **hotfix** — it patches the shipped-regression list verified against `http://localhost:3077` with the auto-booted `node dist/index.js eval serve --root e2e/fixtures` webServer. Every defect has a failing Playwright spec that serves as the acceptance test; closure requires each spec to pass without modification (except B7 — see "Related spec updates" in `tasks.md`).

**Source-of-truth artifacts** (authored by the playwright-verifier):
- `repositories/anton-abyzov/vskill/e2e/playwright-verification-report.md` — full triage report
- `repositories/anton-abyzov/vskill/e2e/playwright-run-log-1776928243.txt` — raw run log
- `repositories/anton-abyzov/vskill/test-results/<slug>/error-context.md` — per-failure page snapshots

**Target path**: `repositories/anton-abyzov/vskill/` (source-only — no test rewrites except B7 reconciliation).

---

## User Stories

### US-001 — Sidebar state & navigation reliability
**As a** Studio power user
**I want** the sidebar's section-collapse state, j/k keyboard selection, and Cmd+B visibility toggle to work reliably across reloads and sessions
**So that** I can trust my UI preferences survive and keyboard-driven navigation behaves like every other editor I use

**Acceptance Criteria**:
- [x] **AC-US1-01** OWN/INSTALLED sidebar section collapse state persists across browser reload.
  - **Failing spec**: `e2e/qa-click-audit.spec.ts:174` "section collapse persistence [AC-US1-05]" AND `e2e/sidebar-split.spec.ts:47` "collapse state for OWN section persists across reload".
  - **Expected**: After user clicks OWN header (collapsing the section) and reloads the page, `aria-expanded="false"` on the OWN section button.
  - **Observed**: `aria-expanded="true"` after reload (state reset).
- [x] **AC-US1-02** Pressing `j` on the body (no input focused) sets `aria-selected="true"` on a skill row in the sidebar.
  - **Failing spec**: `e2e/keyboard-shortcuts.spec.ts:47` "T-050 — `j`/`k` move selection in the sidebar".
  - **Expected**: `[data-testid='skill-row'][aria-selected='true']` becomes visible within 500 ms of the first `j` press (select-first-row semantics when no row is currently selected).
  - **Observed**: no row is ever marked selected.
- [x] **AC-US1-03** `Cmd+B` (macOS) / `Ctrl+B` (other) hides the skills sidebar; pressing the shortcut again reveals it.
  - **Failing spec**: `e2e/keyboard-shortcuts.spec.ts:85` "T-050 — Cmd/Ctrl+B toggles sidebar visibility".
  - **Expected**: `aside[aria-label='Skills sidebar']` transitions from visible → hidden → visible across successive Cmd+B presses.
  - **Observed**: the aside stays visible after every press.

---

### US-002 — Theme toggle reliability (light→dark path)
**As a** Studio user starting in light mode
**I want** both the `Cmd+Shift+D` shortcut and the status-bar theme button to flip `data-theme` to `dark` (and persist it)
**So that** the theme toggle works identically regardless of my current theme

**Acceptance Criteria**:
- [x] **AC-US2-01** `Cmd+Shift+D` pressed while `data-theme="light"` flips `data-theme` to `dark` and persists the new mode to `localStorage`.
  - **Failing spec**: `e2e/keyboard-shortcuts.spec.ts:100` "T-050 — Cmd/Ctrl+Shift+D toggles the theme".
  - **Note**: The reverse path (dark → auto) already **passes** via `theme-persistence.spec.ts:79`. The regression is specific to the light → dark branch, which implicates the cycle logic in `App.tsx` handlers (lines 123, 149, 153) or in `ThemeProvider.setTheme`.
- [x] **AC-US2-02** Clicking the status-bar theme button while `data-theme="light"` flips `data-theme` to `dark` and writes the new mode to `localStorage`.
  - **Failing spec**: `e2e/qa-click-audit.spec.ts:230` "theme toggle [AC-US2-03, AC-US2-04]" — same cycle branch as AC-US2-01.

---

### US-003 — Workspace panel completeness (Leaderboard + TestsPanel filters)
**As a** Studio user inspecting a skill
**I want** the Leaderboard tab to appear in the left rail and the TestsPanel filter tabs (All / Unit / Integration) to render consistently
**So that** I can access the backend data that already exists and filter tests without hunting for missing UI

**Acceptance Criteria**:
- [x] **AC-US3-01** The workspace left rail shows a "Leaderboard" panel entry when a skill is selected.
  - **Failing spec**: `e2e/leaderboard.spec.ts:5` "leaderboard tab is visible in workspace".
  - **Expected**: `text=Leaderboard` is visible in the DOM. Backend `/api/skills/:p/:s/leaderboard` already works (test #27 passes), and `SkillWorkspace.tsx` already routes `state.activePanel === "leaderboard"` to `LeaderboardPanel` — but `LeftRail.PANEL_GROUPS` omits the entry.
- [x] **AC-US3-02** Clicking the Leaderboard tab renders `LeaderboardPanel` with its empty state when there is no sweep data.
  - **Failing spec**: `e2e/leaderboard.spec.ts:13` "leaderboard panel shows empty state when no sweep data".
- [x] **AC-US3-03** The TestsPanel renders the `All / Unit / Integration` filter-tab group unconditionally when a skill is selected and the Tests panel is active (even with zero integration tests).
  - **Failing spec**: `e2e/tests-panel.spec.ts:5` "TestsPanel filter tabs render (All / Unit / Integration)".
  - **Observed**: the tab group is hidden when `hasIntegrationTests === false` (see `TestsPanel.tsx:383` — the wrapping guard).
  - **Expected**: all three tab buttons exist in the DOM with their counts (including zero).
- [x] **AC-US3-04** Switching between the All / Unit / Integration filter tabs changes the rendered case list.
  - **Failing spec**: `e2e/tests-panel.spec.ts:30` "filter tabs filter the test case list".

---

### US-004 — Keyboard-driven toast dismissal
**As a** Studio user who fires a toast via a keybinding (e.g. `e`)
**I want** pressing `Escape` to dismiss that toast immediately
**So that** I can recover my keyboard focus without waiting for auto-dismiss

**Acceptance Criteria**:
- [x] **AC-US4-01** Pressing `Escape` while the `'e'`-placeholder toast is active removes the toast from the DOM within 150 ms.
  - **Failing spec**: `e2e/qa-click-audit.spec.ts:385` "toast lifecycle [AC-US4-08]".
  - **Expected**: toast count = 0 after Escape.
  - **Observed**: toast count = 1 (Escape is swallowed by an earlier-registered handler, or the Toast `onDismiss` path is never reached from the Escape handler).
  - **Edge case**: if multiple toasts are active, Escape dismisses the most-recent one; subsequent presses dismiss older toasts one at a time.

---

### US-005 — Perf budget triage (eval-ui load, search-filter, FCP)
**As a** release engineer
**I want** the three perf-budget failures triaged — each either reduced to within budget or reclassified (with a documented rationale) as environment-variance noise
**So that** the `/lighthouse-budget`, `/performance-marks`, and page-load gates don't block CI with meaningless fails

**Acceptance Criteria**:
- [x] **AC-US5-01** The eval-ui `/` page load either passes the 1000 ms budget **or** the budget is raised to a justified new value with a comment in the spec citing the measurement context (cold dev-server boot included).
  - **Failing spec**: `e2e/eval-ui.spec.ts:168` "page loads in under 1 second" — observed 1914 ms.
- [x] **AC-US5-02** Typing a character into the sidebar search updates the filtered result list within the **hard** 160 ms budget.
  - **Failing spec**: `e2e/performance-marks.spec.ts:74` "typing in search updates results within 80 ms" — observed 313 ms (2× the hard ceiling).
  - **Target**: hard ≤ 160 ms (blocker); soft ≤ 80 ms (aspirational).
- [x] **AC-US5-03** The FCP smoke-budget spec emits a deterministic pass/skip rather than fatal-failing on a missing entry under headless Chromium.
  - **Failing spec**: `e2e/lighthouse-budget.spec.ts:31` "FCP reported within the smoke budget" — browser returns `null`.
  - **Acceptable outcomes**: (a) spec skips with a logged reason when `performance.getEntriesByName('first-contentful-paint').length === 0`, **or** (b) the app emits a paint marker via `PerformanceObserver` before the assertion runs.

---

## Definition of Done

- All 13 ACs checked off (metadata records defect↔task↔AC mapping).
- Every referenced failing spec passes without selector/expectation rewrites (except B7 — see `tasks.md` "Related spec updates").
- Full Playwright suite runs with **0 failures** and **0 new test.fixme** (the existing 3 remain).
- No unit/integration regressions (`npx vitest run` green).
- `/sw:code-reviewer` + `/simplify` + `/sw:grill` pass.

## Non-Goals

- No feature work. No redesigns. No refactors beyond what's needed to fix the listed defects.
- Performance work is **triage-scoped** — only quick wins are in scope; deeper perf overhauls belong in a separate increment.
- The 3 `test.fixme` cases in `qa-click-audit.spec.ts` stay skipped — they are tracked elsewhere.
- Cmd+B sidebar-hidden state does **not** need to persist across reload (per-session toggle is sufficient).
