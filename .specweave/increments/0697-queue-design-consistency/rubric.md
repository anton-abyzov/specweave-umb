---
increment: 0697-queue-design-consistency
title: "Queue page design rollback to app design system"
generated: 2026-04-22
source: auto-generated
version: "1.0"
status: active
---

# Quality Contract: Queue page design rollback to app design system

## Functional Correctness

### R-001: Queue page background uses standard tokens [blocking]
- **Source**: AC-US1-01, AC-US2-01
- **Evaluator**: sw:grill
- **Verify**: Navigate from `/skills` to `/queue`; confirm no warm-paper tint — background, borders, card radius, and spacing rhythm are visually continuous with the rest of the site.
- **Threshold**: `getComputedStyle(document.documentElement).getPropertyValue('--queue-paper')` === `""` on loaded `/queue` page.
- **Result**: [ ] PENDING

### R-002: Queue hero title renders in Geist Sans [blocking]
- **Source**: AC-US1-02, AC-US4-01
- **Evaluator**: sw:grill
- **Verify**: The `/queue` hero `h1` computed `font-family` contains `geist-sans` (case-insensitive) and does NOT contain `Georgia`.
- **Threshold**: E2E assertion in `queue-design-consolidation.spec.ts` test block (b) passes green.
- **Result**: [ ] PENDING

### R-003: Queue filter bar matches /skills filter bar visually [blocking]
- **Source**: AC-US1-03, AC-US5-03
- **Evaluator**: sw:grill
- **Verify**: Filter-bar bounding box at 1280x720 light mode has `|deltaHeight| <= 4px` and `|deltaPaddingX| <= 4px` compared to `/skills` filter bar.
- **Threshold**: E2E assertion in `queue-design-consolidation.spec.ts` test block (c) passes green.
- **Result**: [ ] PENDING

### R-004: State badges render in semantic color families both themes [blocking]
- **Source**: AC-US1-04, AC-US3-02
- **Evaluator**: sw:grill
- **Verify**: Pending/Running/Succeeded/Failed/Paused/Rejected badges use `--status-*` intent colors in both light and dark mode; no warm-peach accent visible on any badge.
- **Threshold**: Browser devtools Accessibility panel shows all 5 semantic intents x 2 themes with no `--queue-accent` color applied; WCAG AA contrast (>=4.5:1 body, >=3:1 large/UI) confirmed.
- **Result**: [ ] PENDING

### R-005: globals.css contains zero --queue-* definitions [blocking]
- **Source**: AC-US2-01
- **Evaluator**: sw:grill
- **Verify**: Both light-theme block (originally lines 94-102) and dark-theme block (originally lines 191-199) are fully removed with no replacement rules.
- **Threshold**: `rg -n "--queue-" src/app/globals.css` returns exit code 1 (no matches).
- **Result**: [ ] PENDING

### R-006: All queue components reference only standard tokens [blocking]
- **Source**: AC-US2-02
- **Evaluator**: sw:grill
- **Verify**: Every file under `src/app/queue/**` uses only `--bg`, `--bg-subtle`, `--bg-hover`, `--text`, `--text-muted`, `--border`, `--status-*` families, plus `STATUS_VARS` helper.
- **Threshold**: `rg -n "--queue-" src/app/queue/` returns exit code 1 (no matches).
- **Result**: [ ] PENDING

### R-007: Repo-wide zero --queue-* hits [blocking]
- **Source**: AC-US2-03
- **Evaluator**: sw:grill
- **Verify**: No `--queue-*` CSS variable references remain anywhere in the `src/` tree.
- **Threshold**: `rg -n "--queue-" src/` from `vskill-platform` root returns exit code 1.
- **Result**: [ ] PENDING

### R-008: STATE_BADGES export unchanged and consumed by both routes [blocking]
- **Source**: AC-US2-04
- **Evaluator**: sw:grill
- **Verify**: `src/app/queue/shared/constants.ts` has zero diff in `git status`; both `/queue` and `/admin/queue` render state badges correctly without modification.
- **Threshold**: `git diff src/app/queue/shared/constants.ts` is empty; existing `STATE_BADGES`-dependent tests pass.
- **Result**: [ ] PENDING

### R-009: Theme switch produces standard dark/light values on /queue [blocking]
- **Source**: AC-US3-01
- **Evaluator**: sw:grill
- **Verify**: Toggling from light to dark mode on `/queue` transitions background, text, borders, and card surfaces to app-standard dark values — no isolated `--queue-*` palette persists.
- **Threshold**: Screenshots in `tests/e2e/evidence/queue-after/` for both themes show no warm-paper tint; `--queue-paper` resolves to `""` in both themes.
- **Result**: [ ] PENDING

### R-010: Sticky first-column separation remains visually distinct [blocking]
- **Source**: AC-US3-03
- **Evaluator**: sw:grill
- **Verify**: In `SubmissionTable` during horizontal scroll, the sticky `skillName` column is visually distinct from scrolled content using `var(--bg-subtle)` in both light and dark themes.
- **Threshold**: No `color-mix` expression remains in `SubmissionTable.tsx`; `rg -n "color-mix" src/app/queue/SubmissionTable.tsx` returns 0 hits; visual inspection at 768px width confirms separation.
- **Result**: [ ] PENDING

### R-011: Zero Georgia serif hits in queue source [blocking]
- **Source**: AC-US4-01
- **Evaluator**: sw:grill
- **Verify**: No `Georgia` font reference remains in any queue component file.
- **Threshold**: `rg -n "Georgia" src/app/queue/` returns exit code 1 (no matches).
- **Result**: [ ] PENDING

### R-012: Zero color-mix() hits in queue components [blocking]
- **Source**: AC-US4-02
- **Evaluator**: sw:grill
- **Verify**: No inline `color-mix()` call remains in any queue component file.
- **Threshold**: `rg -n "color-mix" src/app/queue/` returns exit code 1 (no matches).
- **Result**: [ ] PENDING

### R-013: Queue <main> uses flat var(--bg) background [blocking]
- **Source**: AC-US4-03
- **Evaluator**: sw:grill
- **Verify**: The `<main>` element of the queue page uses a flat `var(--bg)` background with no gradient or multi-stop expression.
- **Threshold**: `rg -n "linear-gradient\|radial-gradient" src/app/queue/QueuePageClient.tsx` returns 0 hits on `<main>` background rule.
- **Result**: [ ] PENDING

### R-014: Geist Mono restricted to correct element types only [blocking]
- **Source**: AC-US4-04
- **Evaluator**: sw:grill
- **Verify**: Mono appears ONLY on timestamp cells, submission IDs, repo slugs/URLs, numeric badges (score, `#N` position), and `.queue-kicker` eyebrows — not on headings, body text, labels, CTAs, or table-cell prose.
- **Threshold**: New Vitest assertion in `QueueStatusBar.test.tsx` passes: `getComputedStyle(container.firstChild).fontFamily` does NOT contain `geist-mono`. All remaining Mono-grep hits in queue files are on permitted element types.
- **Result**: [ ] PENDING

### R-015: StatCard renders with flat surface matching .role-card [blocking]
- **Source**: AC-US4-05
- **Evaluator**: sw:grill
- **Verify**: `StatCard` component uses `border-radius: 10px`, `box-shadow: 0 1px 4px rgba(0,0,0,0.06)`, `border: 1px solid var(--border)`, no `linear-gradient` background.
- **Threshold**: `rg -n "linear-gradient" src/app/queue/QueuePageComponents.tsx` returns 0 hits in StatCard definition; `data-testid="stat-card-*"` attributes unchanged.
- **Result**: [ ] PENDING

### R-016: QueueStatusBar micro-padding normalized [blocking]
- **Source**: AC-US4-06
- **Evaluator**: sw:grill
- **Verify**: `QueueStatusBar` outer wrapper uses padding `0.25rem 0.625rem` (4px/10px), not `0.32rem 0.62rem`.
- **Threshold**: `rg -n "0.32rem\|0.62rem" src/app/queue/QueueStatusBar.tsx` returns 0 hits.
- **Result**: [ ] PENDING

### R-017: New E2E consolidation spec exists and passes [blocking]
- **Source**: AC-US5-01, AC-US5-02, AC-US5-03
- **Evaluator**: sw:grill
- **Verify**: `tests/e2e/queue-design-consolidation.spec.ts` exists with three assertions and all pass green after implementation.
- **Threshold**: `npx playwright test tests/e2e/queue-design-consolidation.spec.ts` exits 0 with 3 passing tests.
- **Result**: [ ] PENDING

### R-018: All 6 existing Vitest queue specs pass unchanged [blocking]
- **Source**: AC-US5-04
- **Evaluator**: sw:grill
- **Verify**: All 6 spec files under `src/app/queue/__tests__/` pass without modification to test files.
- **Threshold**: `npx vitest run src/app/queue/__tests__/` exits 0 with 6 spec files and 0 failures.
- **Result**: [ ] PENDING

### R-019: All 9 existing Playwright queue specs pass unchanged [blocking]
- **Source**: AC-US5-05
- **Evaluator**: sw:grill
- **Verify**: All pre-existing queue E2E specs pass without modification — no `data-testid` renames, no DOM structure changes.
- **Threshold**: `npx playwright test tests/e2e/queue*.spec.ts` exits 0; 9 pre-existing spec files all pass (10 total including the new one).
- **Result**: [ ] PENDING

### R-020: Before/after screenshot evidence captured [blocking]
- **Source**: AC-US5-06
- **Evaluator**: sw:grill
- **Verify**: `tests/e2e/evidence/queue-before/` and `tests/e2e/evidence/queue-after/` each contain 18-24 PNGs covering the full matrix (light+dark x 1280/768/375 x 4 URL states).
- **Threshold**: Both directories non-empty; at minimum 12 files each (light+dark x 3 viewports x 2 URL states).
- **Result**: [ ] PENDING

---

## Infrastructure Criteria

### R-021: No incidental file edits outside increment scope [blocking]
- **Source**: FR-003, FR-005
- **Evaluator**: sw:grill
- **Verify**: `git status` shows only the 5 modified queue files + 1 new E2E spec + 2 evidence directories — no accidental edits to admin queue, API routes, shared constants, or other routes.
- **Threshold**: `git diff --name-only` matches exactly: `src/app/globals.css`, `src/app/queue/QueuePageClient.tsx`, `src/app/queue/QueuePageComponents.tsx`, `src/app/queue/SubmissionTable.tsx`, `src/app/queue/QueueStatusBar.tsx`, `tests/e2e/queue-design-consolidation.spec.ts` plus evidence directory PNGs.
- **Result**: [ ] PENDING

### R-022: Test coverage targets met [non-blocking]
- **Source**: spec.md Test Strategy
- **Evaluator**: sw:grill
- **Verify**: Unit coverage for queue components is >= 90% (per increment metadata); new Vitest assertion increases rather than decreases coverage.
- **Threshold**: `npx vitest run --coverage src/app/queue/` reports >= 90% line coverage.
- **Result**: [ ] PENDING

### R-023: /admin/queue renders identically after change [blocking]
- **Source**: FR-005, AC-US2-04
- **Evaluator**: sw:grill
- **Verify**: `/admin/queue` page renders without visual regression after `--queue-*` deletion from globals.css; uses its own `--admin-*` token namespace which is unaffected.
- **Threshold**: `src/app/admin/queue/page.tsx` has zero diff in `git status`; manual load of `/admin/queue` shows correct state badges and layout.
- **Result**: [ ] PENDING

---

## Review Notes

Customize criteria before implementation begins:
- **Severity**: Change `[blocking]` to `[non-blocking]` for criteria where failure should warn but not halt closure.
- **Add criteria**: Insert additional rubric rows for edge cases identified during implementation (e.g., specific viewport breakpoints, dark-mode contrast ratios per badge intent).
- **Remove criteria**: Remove R-022 if coverage tooling is not configured for this repo.
- **R-014 (Mono audit)**: This criterion requires a new Vitest assertion — confirm `QueueStatusBar.test.tsx` can render the component in a JSDOM environment before implementation.
- **R-020 (screenshots)**: These are reference artifacts, not CI-enforced baselines. The criterion passes if the directories are non-empty with reasonable file counts.
