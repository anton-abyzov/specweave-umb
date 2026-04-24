---
increment: 0697-queue-design-consistency
title: "Queue page design rollback to app design system"
type: refactor
priority: P2
status: planned
created: 2026-04-24
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Queue page design rollback to app design system

## Overview

The `/queue` page on verified-skill.com (vskill-platform) has drifted visually from every other page on the site. During the 0657 dark-theme-semantic-tokens migration, it was given an isolated warm-paper palette (`--queue-paper`, `--queue-surface`, `--queue-ink`, `--queue-muted`, `--queue-rule`, `--queue-accent`), a Georgia serif title, Geist Mono body text, and inline `color-mix()` / gradients — while the rest of the app (`/`, `/skills`, `/studio`, `/docs`) uses standard tokens (`--bg`, `--text`, `--border`, `--status-*`) with Geist Sans body and Geist Mono reserved for code, timestamps, and IDs.

This increment rolls the queue page back onto the same design system as the rest of the app. It is a cosmetic / token-consolidation refactor. No logic, API, data, or behavior is touched. Every existing data-testid, DOM structure, and semantic state-badge color is preserved so that all existing unit and E2E tests continue to pass unchanged.

**Reference plan**: `/Users/antonabyzov/.claude/plans/tranquil-hopping-shannon.md`
**Target repo**: `repositories/anton-abyzov/vskill-platform`
**Increment scope**: 5 files modified + 1 new E2E spec + before/after screenshot evidence.

---

## User Stories

### US-001: Visual consistency for visitors on /queue (P1)
**Project**: vskill-platform

**As a** visitor browsing verified-skill.com
**I want** the `/queue` page to look and feel like every other page on the site
**So that** the product feels coherent and professional, and nothing jumps out as "half-finished" or left over from a prior redesign.

**Acceptance Criteria**:
- [ ] **AC-US1-01**: When I navigate from `/skills` to `/queue` in the same session, the page chrome (background color, border style, card radius, spacing rhythm) is visually continuous — no warm-paper tint, no serif title, no all-Mono body copy.
- [ ] **AC-US1-02**: The `/queue` hero title renders in the same typeface and weight family as the `/skills` and `/docs` hero titles (Geist Sans, matching the existing `.hero-h1` pattern), not in Georgia serif.
- [ ] **AC-US1-03**: The `/queue` filter bar matches the `/skills` filter bar in border-radius, padding, and font-family within a visual-diff tolerance suitable for a side-by-side screenshot comparison captured at 1280×720 light mode.
- [ ] **AC-US1-04**: State badges on `/queue` (Pending, Running, Succeeded, Failed, Paused, Rejected, etc.) still render in their semantically correct color families (success/warning/danger/info/neutral) in both light and dark mode.

---

### US-002: Design tokens unified across the app (P1)
**Project**: vskill-platform

**As a** UX / design engineer maintaining the vskill-platform design system
**I want** queue components to consume the app's standard design tokens (`--bg`, `--bg-subtle`, `--bg-hover`, `--text`, `--text-muted`, `--border`, `--status-*`) instead of an isolated `--queue-*` palette
**So that** future theme tweaks propagate automatically to the queue page and we do not carry two parallel token systems.

**Acceptance Criteria**:
- [ ] **AC-US2-01**: `src/app/globals.css` contains zero `--queue-*` CSS variable definitions after the change. Specifically, the light-theme block (currently lines 94-102) and the dark-theme block (currently lines 191-199) are fully removed with no replacement rules.
- [ ] **AC-US2-02**: Every file under `src/app/queue/**` references only the app's standard tokens: `--bg`, `--bg-subtle`, `--bg-hover`, `--text`, `--text-muted`, `--border`, `--status-info-*`, `--status-success-*`, `--status-warning-*`, `--status-danger-*`, `--status-neutral-*`, plus the existing `STATUS_VARS` helper.
- [ ] **AC-US2-03**: Running `rg -n "--queue-" src/` from the `vskill-platform` repo root returns 0 hits after the change.
- [ ] **AC-US2-04**: The `STATE_BADGES` export at `src/app/queue/shared/constants.ts` is kept as-is (it already composes `STATUS_VARS[intent]` semantically) and continues to be consumed by both `/queue` and `/admin/queue` without modification.

---

### US-003: Theme switching feels consistent on /queue (P2)
**Project**: vskill-platform

**As a** user who switches between light and dark mode
**I want** the `/queue` page to respond to the theme switch with the same typography, spacing, and chrome as the other pages
**So that** the switch feels coherent across the entire site and no page appears to have a "stuck" palette from a prior era.

**Acceptance Criteria**:
- [ ] **AC-US3-01**: When the app theme switches from light to dark (and vice versa), the `/queue` background, text, borders, and card surfaces transition to the corresponding app-standard dark/light values — not to isolated `--queue-*` values.
- [ ] **AC-US3-02**: State badges on `/queue` (Pending, Running, Succeeded, Failed, Paused, Rejected) meet WCAG AA contrast (≥4.5:1 for body text, ≥3:1 for large text or UI components) against their background tint in both light and dark mode, verified in browser devtools Accessibility panel.
- [ ] **AC-US3-03**: Sticky first-column separation on horizontal scroll in `SubmissionTable` remains visually distinct in both themes using `var(--bg-subtle)` instead of the prior `color-mix(white 84%, --queue-paper 16%)` expression.

---

### US-004: Queue-specific styling cruft removed (P2)
**Project**: vskill-platform

**As a** developer maintaining the vskill-platform codebase
**I want** queue-specific styling cruft — warm-peach accent, Georgia serif, micro-padding, inline `color-mix()` expressions, gradient backgrounds — removed
**So that** the queue page is easier to maintain, aligns with future design updates, and stops accumulating one-off styles that only apply to a single route.

**Acceptance Criteria**:
- [ ] **AC-US4-01**: Running `rg -n "Georgia" src/app/queue/` returns 0 hits after the change.
- [ ] **AC-US4-02**: Running `rg -n "color-mix" src/app/queue/` returns 0 hits after the change (no inline `color-mix()` calls remain in queue components).
- [ ] **AC-US4-03**: The main `<main>` element of the queue page uses a flat `var(--bg)` background, not a gradient or multi-stop expression.
- [ ] **AC-US4-04**: Geist Mono is retained ONLY on: timestamp cells (`getElapsed` output), submission IDs, repo slugs / URLs, numeric badges (score, queue position `#N`), and `.queue-kicker` eyebrow text. It is removed from: headings, body text, labels, table-cell prose, and CTAs.
- [ ] **AC-US4-05**: `StatCard` (`QueuePageComponents.tsx`) renders with a flat surface matching the existing `.role-card` pattern — no gradient, no warm accent, standard `--border` and `--bg`.
- [ ] **AC-US4-06**: `QueueStatusBar` micro-padding is normalized from `0.32rem 0.62rem` to the app baseline `0.25rem 0.625rem` (4px / 10px), matching the rhythm used by other status chips.

---

### US-005: Regression guard against reintroduction (P2)
**Project**: vskill-platform

**As an** operator running pre-release E2E suites
**I want** automated visual/semantic regression coverage that asserts no `--queue-*` CSS variables resolve and the queue hero title uses Geist Sans
**So that** accidental reintroduction of the drift during future design work is caught by CI instead of discovered after deploy.

**Acceptance Criteria**:
- [ ] **AC-US5-01**: A new Playwright spec at `tests/e2e/queue-design-consolidation.spec.ts` exists and asserts: `getComputedStyle(document.documentElement).getPropertyValue('--queue-paper')` resolves to the empty string on `/queue`.
- [ ] **AC-US5-02**: The same spec asserts that the queue hero `h1` computed `font-family` contains `geist-sans` (case-insensitive) and does NOT contain `Georgia`.
- [ ] **AC-US5-03**: The same spec asserts that the queue filter-bar bounding box (border-radius, padding) is within an agreed visual-diff tolerance of the `/skills` filter-bar when both are captured at 1280×720 in light mode.
- [ ] **AC-US5-04**: All 6 existing Vitest specs under `src/app/queue/__tests__/` (including `QueueStatusBar.test.tsx`, `SubmissionTable.test.tsx`, `page.test.tsx`, and 3 others) pass without modification after the rollback — behavior is unchanged.
- [ ] **AC-US5-05**: All 9 existing Playwright specs matching `tests/e2e/queue*.spec.ts` (`queue.spec.ts`, `queue-pagination.spec.ts`, `queue-stat-card-stability.spec.ts`, `queue-submit-visibility.spec.ts`, `queue-duplicates.spec.ts`, `queue-cold-load.spec.ts`, and 3 others) pass unchanged — no `data-testid` renames, no DOM structure changes.
- [ ] **AC-US5-06**: Before/after screenshot evidence is captured under `tests/e2e/evidence/queue-before/` and `tests/e2e/evidence/queue-after/` covering light + dark × 1280 / 768 / 375 × 3-4 URL states (`/queue`, `/queue?filter=rejected`, `/queue?q=d`, `/queue?filter=rejected&reason=security`).

---

## Functional Requirements

### FR-001: Standard token palette only
Queue page components MUST consume only the app's standard design tokens: `--bg`, `--bg-subtle`, `--bg-hover`, `--text`, `--text-muted`, `--border`, and the `--status-*` families. No isolated `--queue-*` tokens, no hardcoded hex colors for semantic state, no inline `color-mix()` calls.

### FR-002: Typography matches the app
Queue page typography MUST match the app's typographic system: Geist Sans for body, headings, labels, and CTAs; Geist Mono reserved for timestamps, IDs, URLs / repo slugs, numeric badges, and eyebrow kickers. The hero title MUST use Geist Sans and match the existing `.hero-h1` pattern — not Georgia serif.

### FR-003: Behavior parity
The queue page MUST behave identically after the change: filtering, pagination, sorting, state-badge semantics, row selection, status bar health indicators, execution log expansion, and every user-visible interaction must be unchanged. All existing `data-testid` attributes MUST be preserved (specifically `queue-status-bar` and every `stat-card-*`).

### FR-004: Regression E2E guard
A new Playwright spec MUST exist that would fail if `--queue-*` variables are reintroduced, if the hero title reverts to Georgia serif, or if the filter-bar chrome drifts significantly from the `/skills` baseline.

### FR-005: /admin/queue isolation
The `/admin/queue` page MUST be unchanged and unaffected. It uses its own `--admin-*` token namespace and consumes the shared `STATE_BADGES` export, which is kept as-is.

---

## Test Strategy

### Unit tests (Vitest)
- **Scope**: All 6 existing specs under `src/app/queue/__tests__/` pass unchanged (logic/DOM untouched).
- **New assertion**: One test added asserting that `getComputedStyle(container).fontFamily` on the `QueueStatusBar` outer wrapper does NOT contain `geist-mono` (proving the mono-wrapper was removed while keeping mono on inner numeric spans).
- **Target coverage**: 90% (per increment metadata).

### E2E tests (Playwright)
- **New spec**: `tests/e2e/queue-design-consolidation.spec.ts` with three assertions:
  1. `--queue-paper` resolves to empty string on `/queue`.
  2. Hero `h1` computed `font-family` contains `geist-sans`, not `Georgia`.
  3. Filter-bar dimensions within tolerance of `/skills` filter-bar.
- **Existing specs preserved green**: All 9 `tests/e2e/queue*.spec.ts` files (`queue.spec.ts`, `queue-pagination.spec.ts`, `queue-stat-card-stability.spec.ts`, `queue-submit-visibility.spec.ts`, `queue-duplicates.spec.ts`, `queue-cold-load.spec.ts`, plus 3 others) target text content and `data-testid`, not styles — must remain green without modification.
- **TDD order**: The new consolidation spec is written FIRST (Phase 1 RED), fails on current code, then drives the GREEN implementation across the 5 modified files.

### Manual verification
- **Matrix**: Light mode + dark mode × viewports 1280×720, 768×1024, 375×667 × URL states `/queue`, `/queue?filter=rejected`, `/queue?q=d`, `/queue?filter=rejected&reason=security`.
- **Side-by-side check**: Open `/queue` and `/skills` in adjacent tabs at 1280 light; typography, chrome rhythm, card radius, border tone must match.
- **Accessibility check**: Browser devtools → Accessibility panel. Verify state badges (success / warning / danger / info / neutral) meet WCAG AA contrast against their background tint in both themes.

### Visual regression evidence
- **Before**: `tests/e2e/evidence/queue-before/` captured before any code changes land (light+dark × 3 viewports × 3-4 URL states ≈ 18-24 PNGs). Reference artifacts, not baselines for pixel-diff.
- **After**: `tests/e2e/evidence/queue-after/` captured post-rollback, same matrix. Used for PR review and future audit.

---

## Edge Cases

1. **Sticky first-column separation on horizontal scroll.** `SubmissionTable` currently achieves visual separation of the sticky `skillName` column using `color-mix(white 84%, --queue-paper 16%)`. After the rollback, this switches to `var(--bg-subtle)`. The separation will be subtler but remains visually distinct; verify in both themes at narrow viewports where horizontal scroll is expected.
2. **Dark-mode badge contrast after accent removal.** `--queue-accent` (warm peach) is dropped outright. Re-verify that `danger` badge text (`#F87171`) on its `rgba(248,113,113,0.12)` background, and the other four state intents, still meet WCAG AA in dark mode after the surrounding chrome loses its warm tint.
3. **data-testid preservation.** Existing E2E specs rely on `[data-testid="queue-status-bar"]` and every `[data-testid="stat-card-*"]`. No testid may be renamed, removed, or restructured during the rollback.
4. **Row-highlight animation.** Current code uses `color-mix(queue-accent, white)` for the row-flash highlight. Replace with `var(--bg-hover)`; confirm the flash is still visible in both themes but no longer peach.
5. **JS references to `--queue-*` tokens.** Verified via `rg` that there are ZERO JavaScript string references to any `--queue-*` token outside CSS declarations and inline `style={{}}` blocks. Safe to delete the CSS definitions without leaving dangling runtime references.
6. **Staging hang on /queue (0673 data issue).** The queue page currently hangs in prod due to 2.8M duplicate submission rows. This is a DATA problem tracked in 0673 and is NOT in scope here. Staging E2E must complete inside the default 30s Playwright timeout; if `/queue` hangs during test runs, run against a smaller fixture data set rather than attempting to fix the data issue in this increment.

---

## Non-Goals (Out of Scope)

- **Queue hang / 2.8M duplicate rows in prod.** This is a data-layer problem being addressed in increment 0673 Steps 5-7. Not touched here.
- **Any behavior or logic change.** No filtering logic, pagination, sort, API, or state-machine change. Purely a visual / token refactor.
- **Any API route change.** `src/app/api/v1/submissions/**` is untouched.
- **Any change to `/admin/queue` styling.** It uses its own `--admin-*` token namespace and is explicitly preserved.
- **New design-system abstractions.** No new helper libraries, no new CSS architecture, no new wrapper components. The change reuses existing `STATUS_VARS`, `STATE_BADGES`, `.doc-card`, `.role-card`, `.category-pill`, `.hero-h1` patterns.
- **Typography rework on other pages.** Only queue-page files change.
- **Visual pixel-diff baselining as a CI gate.** Before/after screenshots are reference artifacts for PR review, not enforced pixel baselines in CI.

---

## Success Criteria

- Running `rg -n "--queue-" src/` from `vskill-platform` root returns 0 hits.
- Running `rg -n "Georgia" src/app/queue/` returns 0 hits.
- `getComputedStyle(document.documentElement).getPropertyValue('--queue-paper')` is the empty string on a loaded `/queue` page.
- Hero `h1` computed `font-family` contains `geist-sans` and does not contain `Georgia`.
- All 6 `src/app/queue/__tests__/*.test.tsx` specs green without modification.
- All 9 existing `tests/e2e/queue*.spec.ts` specs green without modification.
- The new `tests/e2e/queue-design-consolidation.spec.ts` spec is green.
- State badges meet WCAG AA contrast in both themes across all 5 semantic intents.
- `/admin/queue` renders identically to before the increment (no visual regression from the shared `STATE_BADGES` import).
- Side-by-side screenshots of `/queue` vs `/skills` at 1280 light mode show matching chrome rhythm, typography, and card radius.

---

## Dependencies

- **Existing app design tokens** in `src/app/globals.css` (`--bg`, `--bg-subtle`, `--bg-hover`, `--text`, `--text-muted`, `--border`, `--status-*`) — already defined and stable.
- **`STATUS_VARS` helper** at `src/lib/status-intent.ts` — already returns `var(--status-*-*)` CSS variable references, no change needed.
- **`STATE_BADGES` export** at `src/app/queue/shared/constants.ts` — already semantic, kept as-is.
- **Existing CSS class patterns** `.doc-card`, `.role-card`, `.category-pill`, `.hero-h1` in `globals.css` — reused directly, no new classes introduced.
- **Playwright E2E infrastructure** already in place under `tests/e2e/`.
- **Vitest setup** already in place under `src/app/queue/__tests__/`.

No new external dependencies, no new packages, no new tooling.
