---
increment: 0697-queue-design-consistency
title: "Queue page design rollback to app design system"
type: refactor
status: planned
generated: 2026-04-22
---

# Tasks: Queue page design rollback to app design system

Target repo: `repositories/anton-abyzov/vskill-platform/`

---

## Phase 1 — RED: Discovery tests + baseline evidence

### T-001: RED — Write queue-design-consolidation E2E spec (fails on current code)
**User Story**: US-005 | **AC**: AC-US5-01, AC-US5-02, AC-US5-03 | **Status**: [x] completed
**Test Plan**: Given the current `/queue` page still has `--queue-paper` defined and a Georgia serif hero title → When the new Playwright spec runs against the running app → Then all three assertions FAIL (confirming test sensitivity before any code changes land).
**Files**:
- `/Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/vskill-platform/tests/e2e/queue-design-consolidation.spec.ts`
**Notes**: Phase 1 — RED. Create the new spec with three `test()` blocks: (a) evaluate `getComputedStyle(document.documentElement).getPropertyValue('--queue-paper')` on `/queue` and assert it equals `""`; (b) evaluate computed `font-family` on the hero `h1` and assert it matches `/geist[\s_-]*sans/i` and does NOT match `/Georgia/i`; (c) capture bounding boxes of `.queue-filter-bar` and the `/skills` filter bar (or equivalent selectors) at 1280x720 light mode and assert `|deltaHeight| <= 4` and `|deltaPaddingX| <= 4` px. Run spec — expected outcome: ALL THREE FAIL against current code. Do not fix code in this task. The failure IS the red-phase deliverable.

---

### T-002: RED — Capture "before" screenshot evidence
**User Story**: US-005 | **AC**: AC-US5-06 | **Status**: [x] completed
**Test Plan**: Given the queue page still renders with its current warm-paper palette → When a Playwright script captures screenshots at the full matrix → Then `tests/e2e/evidence/queue-before/` contains 18-24 PNG files named `{theme}-{viewport}-{url-slug}.png`.
**Files**:
- `/Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/vskill-platform/tests/e2e/evidence/queue-before/` (directory + files)
**Notes**: Phase 1 — RED (baseline). Matrix: light + dark x 1280 / 768 / 375 x `/queue`, `/queue?filter=rejected`, `/queue?q=d`, `/queue?filter=rejected&reason=security`. Use a standalone Playwright script or a `test.describe` block with `page.screenshot({ path: ... })`. These are reference artifacts, NOT pixel-diff baselines — do not register with `expect(page).toHaveScreenshot()`. Create the `tests/e2e/evidence/queue-before/` directory and commit the PNGs with the task. Run BEFORE any code changes (dependency: complete after T-001 spec file exists, but before T-003+).

---

## Phase 3 — GREEN: Per-component token swap

### T-003: GREEN — Delete --queue-* blocks from globals.css
**User Story**: US-002 | **AC**: AC-US2-01, AC-US2-03 | **Status**: [x] completed
**Test Plan**: Given `globals.css` currently defines `--queue-paper` through `--queue-shadow` in both light (lines 94-102) and dark (lines 191-199) theme blocks → When the two blocks are deleted with no replacement rules → Then `rg -n "--queue-" src/app/globals.css` returns 0 hits.
**Files**:
- `/Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/vskill-platform/src/app/globals.css`
**Notes**: Phase 3 — GREEN (globals-agent owns). Delete the light-theme block at lines 94-102 (`--queue-paper`, `--queue-surface`, `--queue-surface-strong`, `--queue-ink`, `--queue-muted`, `--queue-rule`, `--queue-accent`, `--queue-accent-ink`, `--queue-shadow`) and the mirror dark-theme block at lines 191-199. Do NOT add any replacement CSS. Verify with `rg` before marking complete. This task breaks the app visually until T-004 through T-007 provide component-level replacements.

---

### T-004: GREEN — Migrate QueueStatusBar.tsx to standard tokens
**User Story**: US-002, US-003 | **AC**: AC-US2-02, AC-US3-01, AC-US4-06 | **Status**: [x] completed
**Test Plan**: Given `QueueStatusBar.tsx` uses `--queue-muted`, `--queue-rule`, `color-mix(...queue-paper...)`, `fontFamily: mono` wrapper, and `padding: 0.32rem 0.62rem` → When all queue-specific tokens and the mono wrapper are replaced → Then (a) `rg -n "--queue-" src/app/queue/QueueStatusBar.tsx` returns 0 hits; (b) the outer wrapper div does NOT have an inline `fontFamily` containing `mono`; (c) padding is `0.25rem 0.625rem`.
**Files**:
- `/Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/vskill-platform/src/app/queue/QueueStatusBar.tsx`
**Notes**: Phase 3 — GREEN. Token map: `--queue-muted` → `--text-muted`, `--queue-rule` → `--border`, `color-mix(...var(--queue-paper)...)` → `var(--bg-subtle)`. Remove the outer `fontFamily: mono` wrapper (the `STATUS_VARS[intent]` pills inside are already correct — leave them). Normalize micro-padding `0.32rem 0.62rem` → `0.25rem 0.625rem` (4px / 10px app baseline). Preserve `data-testid="queue-status-bar"`. Keep `STATUS_VARS` import — still needed for pill colors.

---

### T-005: GREEN — Migrate SubmissionTable.tsx to standard tokens
**User Story**: US-002, US-003, US-004 | **AC**: AC-US2-02, AC-US3-03, AC-US4-02, AC-US4-04 | **Status**: [x] completed
**Test Plan**: Given `SubmissionTable.tsx` uses `--queue-ink`, `--queue-rule`, `color-mix(white, queue-paper)` on the sticky cell, and `color-mix(queue-accent, white)` for the row flash → When all queue tokens are replaced → Then (a) `rg -n "--queue-" src/app/queue/SubmissionTable.tsx` returns 0 hits; (b) `rg -n "color-mix" src/app/queue/SubmissionTable.tsx` returns 0 hits; (c) all `data-testid` attributes are unchanged.
**Files**:
- `/Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/vskill-platform/src/app/queue/SubmissionTable.tsx`
**Notes**: Phase 3 — GREEN. Token map: `--queue-ink` → `--text`, `--queue-rule` → `--border`, sticky-cell `color-mix(white 84%, --queue-paper 16%)` → `var(--bg-subtle)`, highlight-row `color-mix(queue-accent, white)` → `var(--bg-hover)` (or `var(--status-info-bg)` if animation hue is needed). Retain Geist Mono ONLY on: score cells, queue-position `#N` badges, timestamp cells (output of `getElapsed`), submission ID spans, URL/repo slug spans. Preserve every `data-testid` attribute exactly — no renames, no additions, no removals. Flash animation may still exist, just without the peach hue.

---

### T-006: GREEN — Migrate QueuePageComponents.tsx to standard tokens
**User Story**: US-002, US-004 | **AC**: AC-US2-02, AC-US2-04, AC-US4-05 | **Status**: [x] completed
**Test Plan**: Given `QueuePageComponents.tsx` defines `QueueSkeleton`, `QueueTableSkeleton`, `StatCard`, `ReasonPill`, and `ExecutionLogPanel` using `--queue-*` tokens, gradients, and wrapper-level `fontFamily: mono` → When all queue tokens and wrapper mono are replaced → Then (a) `rg -n "--queue-" src/app/queue/QueuePageComponents.tsx` returns 0 hits; (b) `StatCard` renders with a flat background matching `.role-card` (no `linear-gradient`); (c) `data-testid="stat-card-*"` attributes are unchanged.
**Files**:
- `/Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/vskill-platform/src/app/queue/QueuePageComponents.tsx`
**Notes**: Phase 3 — GREEN. `StatCard`: drop gradient wrapper, replace with `background: var(--bg)`, `border: 1px solid var(--border)`, `border-radius: 10px`, `box-shadow: 0 1px 4px rgba(0,0,0,0.06)` — matches `.role-card`. Drop wrapper-level `fontFamily: mono`; keep Mono ONLY on the numeric value span inside `StatCard`. `ReasonPill` + `ExecutionLogPanel`: `--queue-*` → standard tokens per plan token map. `QueueSkeleton` / `QueueTableSkeleton`: replace shimmer `--queue-surface` / `--queue-paper` with `--bg-subtle`. Preserve all `data-testid="stat-card-*"` attributes.

---

### T-007: GREEN — Rewrite QueuePageClient.tsx inline style block
**User Story**: US-001, US-002, US-004 | **AC**: AC-US1-01, AC-US1-02, AC-US2-05, AC-US4-01, AC-US4-03 | **Status**: [x] completed
**Test Plan**: Given `QueuePageClient.tsx` has an inline `<style>` block containing `Georgia`, `--queue-*` references, `color-mix()` gradient on `<main>`, and queue-specific shadow/accent class rules → When the block is rewritten → Then (a) `rg -n "Georgia" src/app/queue/QueuePageClient.tsx` returns 0 hits; (b) `rg -n "--queue-" src/app/queue/QueuePageClient.tsx` returns 0 hits; (c) the `<main>` element uses `background: var(--bg)` (flat, no gradient); (d) `.queue-title` renders in Geist Sans matching `.hero-h1` pattern.
**Files**:
- `/Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/vskill-platform/src/app/queue/QueuePageClient.tsx`
**Notes**: Phase 3 — GREEN (queue-components-agent owns). Rewrite the inline `<style>` string in place — do NOT extract to a CSS module or separate file (keep existing file layout). `.queue-title` → Geist Sans, size/weight matching `.hero-h1` (e.g., `font-family: var(--font-geist-sans)`, `font-size: clamp(2rem, 5vw, 3rem)`, `font-weight: 700`). `.queue-kicker` → keep Mono (eyebrow label). `.queue-lede` / `.queue-aside-copy` → Geist Sans. `.queue-surface-card` → matches `.doc-card` (`border-radius: 10px`, `box-shadow: 0 1px 4px rgba(0,0,0,0.06)`, `border: 1px solid var(--border)`). `.queue-meta-pill` → matches `.category-pill`. `.queue-search-input` → standard app input chrome. Error banner: `--status-warning-bg` / `--status-danger-bg`. Shortcuts hint: `--border` + `--bg-subtle`. `<main>` background: flat `var(--bg)`. Drop all `color-mix()` expressions referencing dropped tokens. Drop `--queue-shadow`, `--queue-accent` class rules.

---

## Phase 4 — Typography audit

### T-008: REFACTOR — Mono typography audit across all four queue component files
**User Story**: US-004 | **AC**: AC-US2-05, AC-US4-04 | **Status**: [x] completed
**Test Plan**: Given tasks T-004 through T-007 have landed → When `rg -n "fontFamily.*mono|font-family.*mono|geist-mono|Geist Mono" src/app/queue/` runs across all four component files → Then every remaining hit is ONLY on: `getElapsed` timestamp output spans, submission ID spans, URL/repo slug spans, numeric badge spans (score, `#N` queue position), `.queue-kicker` eyebrow label.
**Files**:
- `/Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/vskill-platform/src/app/queue/QueuePageClient.tsx`
- `/Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/vskill-platform/src/app/queue/QueuePageComponents.tsx`
- `/Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/vskill-platform/src/app/queue/SubmissionTable.tsx`
- `/Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/vskill-platform/src/app/queue/QueueStatusBar.tsx`
**Notes**: Phase 4 — REFACTOR. Sweep task that catches anything T-004..T-007 may have missed. Remove Mono from: headings (H1/H2/H3), body text, form labels, filter counts, CTAs, table-cell prose, tooltip copy, modal copy. Also add the new Vitest font-family assertion in `src/app/queue/__tests__/QueueStatusBar.test.tsx` (or a new `__tests__/typography.test.tsx`): render `QueueStatusBar` in a test container and assert `getComputedStyle(container.firstChild).fontFamily` does NOT contain `geist-mono` (case-insensitive). Plan ref: Phase 4 typography pass.

---

## Phase 5 — Regression + visual verification

### T-009: VERIFY — Run all existing Vitest queue specs (must pass unchanged)
**User Story**: US-005 | **AC**: AC-US5-04 | **Status**: [x] completed
**Test Plan**: Given the five queue component files have been modified in T-003..T-008 → When `npx vitest run src/app/queue/__tests__/` runs → Then all 6 spec files pass with 0 failures and 0 skips; then `npx vitest run` globally returns 0 failures.
**Files**:
- `/Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/vskill-platform/src/app/queue/__tests__/` (run existing files, do not modify)
**Notes**: Phase 5 — VERIFY. Run from `repositories/anton-abyzov/vskill-platform/` directory. If any spec fails, the failing spec reveals a behavior regression introduced during T-003..T-008 — DO NOT modify the test; fix the component. The new font-family assertion added in T-008 must also pass. If global vitest run shows pre-existing unrelated failures, document them but do not block this task.

---

### T-010: VERIFY — Run new E2E consolidation spec (must now pass GREEN)
**User Story**: US-005 | **AC**: AC-US5-01, AC-US5-02, AC-US5-03, AC-US5-05 | **Status**: [x] completed
**Test Plan**: Given T-003..T-008 have all completed → When `npx playwright test tests/e2e/queue-design-consolidation.spec.ts` runs → Then all three assertions pass (GREEN); then `npx playwright test tests/e2e/queue*.spec.ts` runs and all 9 pre-existing specs pass unchanged.
**Files**:
- `/Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/vskill-platform/tests/e2e/queue-design-consolidation.spec.ts`
**Notes**: Phase 5 — VERIFY. Run from `repositories/anton-abyzov/vskill-platform/`. This is the RED→GREEN transition proof: the spec written in T-001 must now be GREEN. If any assertion still fails, return to the appropriate GREEN task to complete the token swap. For the font-family assertion, use case-insensitive regex `/geist[\s_-]*sans/i` to avoid cross-browser string format differences (plan ref: Challenge 6, R7). If staging has 0673 data issues (>30 s load), run against localhost or a preview URL with clean fixture data (plan ref: Challenge 5, R6).

---

### T-011: VERIFY — Capture "after" screenshots and manual side-by-side compare
**User Story**: US-001, US-003 | **AC**: AC-US1-03, AC-US3-02, AC-US5-06 | **Status**: [x] completed
**Test Plan**: Given T-003..T-010 are complete and the page renders correctly → When after-screenshots are captured at the same matrix as T-002 → Then `tests/e2e/evidence/queue-after/` contains 18-24 PNGs; side-by-side with `/skills` at 1280 light shows matching chrome rhythm, typography, and card radius; browser devtools Accessibility panel confirms WCAG AA on all 5 state-badge intents x 2 themes.
**Files**:
- `/Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/vskill-platform/tests/e2e/evidence/queue-after/` (directory + files)
**Notes**: Phase 5 — VERIFY (manual gate). Same matrix as T-002: light + dark x 1280 / 768 / 375 x `/queue`, `/queue?filter=rejected`, `/queue?q=d`, `/queue?filter=rejected&reason=security`. Side-by-side check: open `/queue` and `/skills` in adjacent tabs at 1280 light mode; typography (Geist Sans body, matching hero weight/size), card border-radius (10px), border tone (`--border`), and spacing rhythm must match visually. WCAG AA check: browser devtools Accessibility panel. Verify contrast ratios >=4.5:1 for body text, >=3:1 for large text/UI components, for Pending/Running/Succeeded/Failed/Paused/Rejected badge variants in both themes. Plan ref: Phase 5 manual verification, Challenge 3.

---

## Phase 6 — Cleanup + CI verification

### T-012: CLEANUP — Final rg sweep: zero --queue-* and Georgia hits
**User Story**: US-002, US-004 | **AC**: AC-US2-03, AC-US4-01, AC-US4-02 | **Status**: [x] completed
**Test Plan**: Given all GREEN and REFACTOR tasks are complete → When `rg -n "--queue-" src/` runs from the vskill-platform root → Then exit code 1 (no matches); When `rg -n "Georgia" src/app/queue/` runs → Then exit code 1 (no matches); When `rg -n "color-mix" src/app/queue/` runs → Then exit code 1 (no matches).
**Files**:
- `/Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/vskill-platform/src/app/globals.css`
- `/Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/vskill-platform/src/app/queue/QueuePageClient.tsx`
- `/Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/vskill-platform/src/app/queue/QueuePageComponents.tsx`
- `/Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/vskill-platform/src/app/queue/SubmissionTable.tsx`
- `/Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/vskill-platform/src/app/queue/QueueStatusBar.tsx`
**Notes**: Phase 6 — CLEANUP. Run the three `rg` commands in sequence. If any returns hits, return to the relevant task. Also remove: now-orphaned inline `<style>` rules that only referenced dropped tokens, dead `color-mix()` expressions referencing `--queue-*`, and unused CSS variable references in the four queue component files. Verify `git status` shows only the 5 modified files + 1 new test file + 2 evidence directories — no incidental edits. Plan ref: Phase 6, cleanup gates.

---

### T-013: VERIFY — Confirm /admin/queue renders unchanged
**User Story**: US-002 | **AC**: AC-US2-04 | **Status**: [x] completed
**Test Plan**: Given T-003 deleted `--queue-*` from globals.css and all queue component files have been updated → When `/admin/queue` is loaded in a browser → Then it renders identically to before the increment (uses its own `--admin-*` tokens; `STATE_BADGES` from the unchanged `src/app/queue/shared/constants.ts` renders correctly).
**Files**:
- `/Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/vskill-platform/src/app/admin/queue/page.tsx` (read-only — must be unchanged)
- `/Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/vskill-platform/src/app/queue/shared/constants.ts` (read-only — must be unchanged)
**Notes**: Phase 6 — VERIFY. Regression check, not a code change. Verify: (a) `src/app/admin/queue/page.tsx` has zero diff in `git status`; (b) `src/app/queue/shared/constants.ts` has zero diff in `git status`; (c) `STATE_BADGES` export renders the correct semantic badge colors on the admin page. If `--admin-*` tokens are accidentally affected, audit globals.css diff to confirm only `--queue-*` blocks were removed. Plan ref: FR-005, unchanged-files table.

---

### T-014: REFACTOR — Accessibility audit on state badges (optional / time-permitting)
**User Story**: US-001, US-003 | **AC**: AC-US1-04, AC-US3-02 | **Status**: [x] completed
**Test Plan**: Given T-011 has completed the manual screenshot matrix → When browser devtools Accessibility panel is used on `/queue` for each of the 5 badge intents x 2 themes → Then contrast ratios are documented and all meet WCAG AA (>=4.5:1 body text, >=3:1 large text/UI components).
**Files**:
- No file changes required — documentation only in PR description
**Notes**: Phase 6 — REFACTOR (optional). Systematically capture the contrast ratio for each badge variant (Pending=neutral, Running=info, Succeeded=success, Failed=danger, Paused=warning, Rejected=danger) in light mode AND dark mode. Document ratios in a PR comment. If any ratio is below AA threshold AND caused by this increment (not pre-existing), halt and triage before closure. If pre-existing, open a follow-up increment and proceed. Plan ref: Challenge 3, R3.

---

## AC Coverage Matrix

| AC | Task(s) |
|---|---|
| AC-US1-01 | T-007 |
| AC-US1-02 | T-007 |
| AC-US1-03 | T-011 |
| AC-US1-04 | T-014 |
| AC-US2-01 | T-003 |
| AC-US2-02 | T-004, T-005, T-006, T-007 |
| AC-US2-03 | T-003, T-012 |
| AC-US2-04 | T-013 |
| AC-US2-05 | T-007, T-008 |
| AC-US3-01 | T-004 |
| AC-US3-02 | T-011, T-014 |
| AC-US3-03 | T-005 |
| AC-US4-01 | T-012 |
| AC-US4-02 | T-005, T-012 |
| AC-US4-03 | T-007 |
| AC-US4-04 | T-008 |
| AC-US4-05 | T-006 |
| AC-US4-06 | T-004 |
| AC-US5-01 | T-001, T-010 |
| AC-US5-02 | T-001, T-010 |
| AC-US5-03 | T-001, T-010 |
| AC-US5-04 | T-009 |
| AC-US5-05 | T-010 |
| AC-US5-06 | T-002, T-011 |
