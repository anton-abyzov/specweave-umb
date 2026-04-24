# Implementation Plan: Queue page design rollback to app design system

**Increment**: 0697-queue-design-consistency
**Target repo**: `repositories/anton-abyzov/vskill-platform/`
**Type**: refactor (cosmetic / design-system consolidation)
**Priority**: P2 (UX consistency)
**Source of truth**: approved plan `/Users/antonabyzov/.claude/plans/tranquil-hopping-shannon.md` (read by architect before drafting)

---

## Overview

The `/queue` page on verified-skill.com drifted visually from the rest of the vskill-platform during the 0657 dark-theme-semantic-tokens migration. It was given its own isolated warm-paper palette (`--queue-paper`, `--queue-surface`, `--queue-ink`, `--queue-muted`, `--queue-rule`, `--queue-accent`, `--queue-shadow`), a Georgia serif title, heavy Geist Mono body typography, and inline `color-mix()` gradients — while every sibling route (`/`, `/skills`, `/studio`, `/docs`) uses the canonical app tokens (`--bg`, `--text`, `--text-muted`, `--border`, `--bg-hover`, `--bg-subtle`, `--status-*`) with Geist Sans for prose and Geist Mono only for code/IDs/timestamps.

This increment is a **CSS-variable de-aliasing pass** that rolls the queue page back onto the shared design system. It is strictly cosmetic: no logic, no API shape, no data-access, no component boundary changes. The separate "hanging" symptom on `/queue` (data-layer: ~2.8 M duplicate rows in prod) is tracked in **0673 Steps 5-7** and is explicitly **out of scope** for this increment.

Architecturally the change is local to five files in the `src/app/queue/` tree plus two blocks in `src/app/globals.css`. No new helpers, no new abstractions, no component extraction — the existing `STATUS_VARS` (`src/lib/status-intent.ts`) and `STATE_BADGES` (`src/app/queue/shared/constants.ts`) are already semantic and are reused unchanged.

---

## Architecture

### Approach: CSS-variable de-aliasing (not a redesign)

The 11 `--queue-*` tokens currently defined in `globals.css` are a **duplicate, alias layer** over the already-existing canonical tokens. The design pattern is:

```
Current (drifted):  components → var(--queue-paper) →  #FBF8F3 (duplicate light) / #171411 (duplicate dark)
Target   (aligned):  components → var(--bg)         →  canonical light/dark background
```

De-aliasing means: delete the `--queue-*` definitions, rewrite the 4 consuming component files to reference the canonical tokens directly, and delete the Georgia serif / mono-everywhere typography overrides. No structural refactor, no new components, no new CSS classes.

**Why this is not an architecture decision**: the architectural choice (three-layer token system: raw → semantic → component) was already made in the 0657 migration. This increment is a **drift correction** — the queue page bypassed the semantic layer with a private raw-token cluster. Rolling it back restores conformance with the decision that's already in force.

**Consequence**: no new ADR. This is an amendment of the 0657 migration's implementation. See the "ADR decision" section below.

### Component responsibility boundaries (5 modified files)

| File | Responsibility | Scope of change |
|---|---|---|
| `src/app/globals.css` | Canonical token definitions (Layer 1 + Layer 2). | **Delete** two `--queue-*` blocks (light 94-102, dark 191-199). No replacement rules added. |
| `src/app/queue/QueuePageClient.tsx` | Top-level client shell: hero, filter bar, inline `<style>`, SSR handoff. | Rewrite inline `<style>` string — drop `--queue-*`, `color-mix(...queue-paper)`, `Georgia`, queue shadow/accent. Flatten `<main>` background to `var(--bg)`. Retitle `.queue-title` to Geist Sans, size/weight matching `.hero-h1`. Inputs, pills, surface cards → reuse `.doc-card` / `.category-pill` patterns. |
| `src/app/queue/QueuePageComponents.tsx` | `QueueSkeleton`, `StatCard`, `ReasonPill`, `ExecutionLogPanel`. | Replace `--queue-*` with `--text` / `--text-muted` / `--border` / `--bg` / `--bg-subtle`. Drop `fontFamily: mono` wrappers; keep Mono only on numeric values inside `StatCard`. Flatten `StatCard` gradient to a flat surface that matches `.role-card`. |
| `src/app/queue/SubmissionTable.tsx` | Virtualized submissions table, sticky `skillName` column, row flash. | `--queue-ink` → `--text`, `--queue-rule` → `--border`. Sticky-cell `color-mix(white, queue-paper)` → `var(--bg-subtle)` (preserves subtle scroll-separation). Highlight-row `color-mix(queue-accent, white)` → `var(--bg-hover)` (or `--status-info-bg` if a hue is required for the flash animation). Retain Geist Mono on score / queue-position `#N` badges + timestamp cells. |
| `src/app/queue/QueueStatusBar.tsx` | Health / paused pill strip + filter counts. | Remove outer `fontFamily: mono` wrapper. `--queue-muted` → `--text-muted`, `--queue-rule` → `--border`. Normalize micro-padding `0.32rem 0.62rem` → `0.25rem 0.625rem` (matches the app's 4/10 px baseline). Existing `STATUS_VARS[intent]` pills unchanged (already semantic). |

### Unchanged files (already correct or out of scope)

| File | Reason unchanged |
|---|---|
| `src/app/queue/page.tsx` | Server component; no styling, just data fetch + client boundary. |
| `src/app/queue/shared/constants.ts` | `STATE_BADGES` composes `STATUS_VARS[intent]` + labels — already semantic. No hardcoded hex. |
| `src/app/queue/shared/components/StateBadge.tsx` | Consumes `STATE_BADGES`; renders via canonical `--status-*`. No drift. |
| `src/app/admin/queue/page.tsx` | Uses its own `--admin-*` token family; not part of this consolidation. |
| `src/lib/status-intent.ts` | `STATUS_VARS` is the helper we reuse. Read-only. |

### Inline style vs CSS class convention

Follow the existing pattern already established in `globals.css`:

- **Global CSS classes** (`.doc-card`, `.role-card`, `.category-pill`, `.hero-h1`) for repeatable surface patterns and typography. The queue components should reuse these classes rather than reinvent equivalents.
- **Inline `style={{ ... }}`** allowed only for dynamic per-instance values (row highlight flash, sticky column positioning) and short-lived animations.
- **Inline `<style jsx>` / `<style>` string** inside `QueuePageClient.tsx` is pre-existing; keep the file layout, just replace token references. Do NOT introduce CSS-in-JS runtimes or CSS modules — stay consistent with the rest of the file's current approach.

### Token mapping (fixed per approved plan — do not re-litigate)

| Current `--queue-*` | Target canonical token | Usage context |
|---|---|---|
| `--queue-paper` | `--bg` (primary) or `--bg-subtle` (alt panels) | Body backgrounds |
| `--queue-surface` | `--bg` | Panel backgrounds |
| `--queue-surface-strong` | `--bg-hover` | Hover/emphasized surfaces |
| `--queue-ink` | `--text` | Primary text |
| `--queue-muted` | `--text-muted` | Supporting text |
| `--queue-rule` | `--border` | 1 px dividers, inputs |
| `--queue-accent` + `--queue-accent-ink` | **dropped**; use `--status-info-*` only when a hue is required (row flash) | Brand warm-peach removed |
| `--queue-shadow` | `0 1px 4px rgba(0,0,0,0.06)` | Card elevation matching `.doc-card` |

---

## Data Model

**Not applicable.** This increment does not touch database schema, Prisma models, API payloads, component state, or client-side cache. Visual layer only.

---

## API Contracts

**Not applicable.** No API routes added, removed, or modified. All existing `/api/queue/*` endpoints, their request/response shapes, and caching behavior remain identical.

---

## Technology Stack

- **Framework**: Next.js 15 App Router (client components only — `"use client"` files). No server-component changes.
- **Styling**:
  - CSS variables defined in `src/app/globals.css` (Layer 1 raw + Layer 2 semantic).
  - Tailwind utility classes where already in use (no new utilities introduced).
  - Inline `style={{}}` for dynamic per-instance values (row highlight, sticky offsets).
  - Inline `<style>` blocks in `QueuePageClient.tsx` for page-scoped CSS (pre-existing pattern).
- **Typography**:
  - **Geist Sans** — all running text, H1 / H2 / H3, labels, CTAs, table header prose, filter labels, counts, help copy, kicker text.
  - **Geist Mono** — restricted to: timestamps (`getElapsed`), submission IDs, URLs / repo slugs, numeric badges (score, queue position `#N`), `.queue-kicker` eyebrow labels. Nothing else.
- **Testing**:
  - **Vitest** — existing unit tests under `src/app/queue/__tests__/` plus one new font-family assertion.
  - **Playwright** — one new E2E spec (`tests/e2e/queue-design-consolidation.spec.ts`) plus the 9 existing queue E2E specs (unchanged).

**Architecture Decisions (implementation-level, not ADR-grade)**:

1. **Reuse `STATUS_VARS` instead of a new helper.** Alternative considered and rejected per approved plan: a new `src/lib/submission-state-styles.ts` wrapper. Rejected because `STATUS_VARS` is already a 5-intent semantic helper used across the app; introducing a second wrapper would multiply indirection without benefit.
2. **Drop the warm-peach accent rather than port it.** Alternative considered: move `--queue-accent` into a global `--brand-accent` token usable across the site. Rejected because no other page uses a brand accent on primary chrome; adding a global one would spread the drift, not contain it. If a hue is needed for the row-flash animation, reuse `--status-info-*` (already defined for both themes).
3. **Keep the inline `<style>` block in `QueuePageClient.tsx`.** Alternative considered: extract to a CSS Module or a dedicated `.css` file. Rejected — stays consistent with the file's current structure and avoids a refactor-within-a-refactor that would inflate the diff.
4. **Preserve sticky-cell separation via `--bg-subtle`.** Alternative considered: flat `--bg` with no visual differentiation. Rejected because `SubmissionTable` relies on visual separation of the sticky `skillName` column during horizontal scroll; `--bg-subtle` provides the needed subtle offset without reintroducing a custom token.

---

## Implementation Phases

The approved plan specifies 6 phases containing 12 tasks in strict TDD order. Each phase below explains WHY and HOW for the implementation agents.

### Phase 1 — RED: Discovery tests + baseline evidence (Tasks 1-2)

**Why**: TDD gate. Before changing any code, assert the current drift and capture before-state visual evidence. This phase fails on current code — that failure is the proof the tests are sensitive enough to detect the fix.

**How**:
- **Task 1** — Add `tests/e2e/queue-design-consolidation.spec.ts` with three assertions:
  1. `getComputedStyle(document.documentElement).getPropertyValue('--queue-paper')` returns empty string (confirms no `--queue-*` tokens leak to `:root`).
  2. Hero `h1` element's computed `font-family` contains `geist-sans`, NOT `Georgia`.
  3. Screenshot stability of filter-bar against `/skills` filter-bar dimensions (pixel-tolerance assertion on bounding box).
- **Task 2** — Capture "before" screenshots into `tests/e2e/evidence/queue-before/`. Matrix: light+dark × 1280/768/375 × four URL variants (`/queue`, `/queue?filter=rejected`, `/queue?q=d`, `/queue?filter=rejected&reason=security`). These are reference artifacts, not baseline snapshots — they live on disk for manual comparison and are not asserted against.

### Phase 2 — (skipped by design): no new helper required

The approved plan explicitly skips any "build a new helper" phase. `STATUS_VARS` already exists and is sufficient. This gap in phase numbering is intentional and mirrors the approved plan.

### Phase 3 — GREEN: per-component token swap (Tasks 3-7)

**Why**: Small, mechanical, file-by-file edits minimize conflict surface when multiple agents work in parallel (see Execution strategy below).

**How**:
- **Task 3 (globals-agent owns)** — Delete `--queue-*` block at `globals.css` lines 94-102 (light) and lines 191-199 (dark). No replacement CSS rules added. Verify `rg -n "--queue-" src/app/globals.css` returns 0.
- **Task 4** — `QueueStatusBar.tsx`: token swaps, remove outer mono-wrapper, normalize padding to `0.25rem 0.625rem`. Keep `STATUS_VARS[intent]` pills untouched — they're already correct.
- **Task 5** — `SubmissionTable.tsx`: token swaps; sticky cell uses `var(--bg-subtle)`; highlight row uses `var(--bg-hover)` (or `--status-info-bg` if animation hue is needed). Preserve all `data-testid` values.
- **Task 6** — `QueuePageComponents.tsx`: `StatCard` loses its gradient (now flat, matches `.role-card`); `ReasonPill`, `ExecutionLogPanel`, skeletons get token swaps. Remove `fontFamily: mono` from wrappers; keep it on numeric values inside `StatCard`.
- **Task 7** — `QueuePageClient.tsx`: rewrite the inline `<style>` string to drop every `--queue-*` ref, the `color-mix()` expressions using queue paper, the Georgia title font, the `queue-shadow` and `queue-accent` class rules. Flatten the `<main>` to `background: var(--bg)`. Retitle the hero to Geist Sans matching `.hero-h1`. Cards match `.doc-card`; inputs match the standard app input chrome.

### Phase 4 — Typography pass (Task 8)

**Why**: The typography drift (Mono on everything) is the most visible symptom. It needs one dedicated sweep to catch instances the token-swap tasks miss.

**How**:
- Grep `fontFamily.*mono|font-family.*mono|Geist Mono` across the four queue component files.
- **Keep Mono on**: timestamp outputs from `getElapsed`, submission IDs, URL / repo slug rendering, numeric badges (score, queue position `#N`), `.queue-kicker` eyebrow label.
- **Remove Mono from**: all headings (H1/H2/H3), body text, form labels, filter counts, CTAs, table-cell prose, tooltip copy, modal copy.
- Verify with a targeted Vitest assertion (below): outer container of `QueueStatusBar` must NOT render with a `geist-mono` family.

### Phase 5 — Regression + visual verification (Tasks 9-10)

**Why**: Confirm no behavioral regression and capture comparable after-state evidence.

**How**:
- **Task 9** — Run `npx vitest run src/app/queue/__tests__/` (6 spec files). All must pass with zero behavior changes. Run Phase 1 E2E — must now GREEN.
- **Task 10** — Capture "after" screenshots into `tests/e2e/evidence/queue-after/` (same matrix as Phase 1). Side-by-side with `/skills` and `/docs` — typography and chrome rhythm must match.

### Phase 6 — Cleanup / verification gates (Tasks 11-12)

**Why**: Lock the drift from recurring. Any remaining `--queue-*` or `Georgia` reference is a regression.

**How**:
- **Task 11** — `rg "--queue-" src/` must return 0 hits. If grep hits anything, the task is not done.
- **Task 12** — `rg "Georgia" src/app/queue/` must return 0 hits. Delete any now-orphaned inline `<style>` rules, dead `color-mix` expressions that referenced dropped tokens, and unused imports.

---

## Testing Strategy

| Layer | Tests | Status |
|---|---|---|
| **Unit (Vitest)** | `src/app/queue/__tests__/QueueStatusBar.test.tsx`, `SubmissionTable.test.tsx`, `page.test.tsx`, and 3 others — all green with no behavior change. | Pre-existing + 1 new font-family assertion added. |
| **Unit addition** | Assert `getComputedStyle(container).fontFamily` on the outer wrapper rendered by `QueueStatusBar` does NOT contain `geist-mono`. | New. |
| **E2E (Playwright)** | New `tests/e2e/queue-design-consolidation.spec.ts` — 3 assertions (`--queue-paper` empty, font-family Sans, filter-bar stability). | New (1 file). |
| **E2E existing** | `queue.spec.ts`, `queue-pagination.spec.ts`, `queue-stat-card-stability.spec.ts`, `queue-submit-visibility.spec.ts`, `queue-duplicates.spec.ts`, `queue-cold-load.spec.ts`, plus 3 others — untouched; target `data-testid` / text, not styles. | Must stay green. |
| **Manual (gated)** | Light + dark × 1280 / 768 / 375 × `/queue`, `/queue?filter=rejected`, `/queue?q=d`, `/queue?filter=rejected&reason=security`. Browser devtools Accessibility panel → state-badge WCAG AA. Side-by-side with `/skills` in adjacent tab. | Required before `/sw:done`. |

**Visual evidence directories** (created during testing, checked into repo for traceability):
- `tests/e2e/evidence/queue-before/` — captured in Phase 1 Task 2.
- `tests/e2e/evidence/queue-after/` — captured in Phase 5 Task 10.

**Coverage targets** (inherited from project config): unit 95%, integration 90%, e2e 100% of AC scenarios. This refactor does not decrease any of these.

---

## Technical Challenges

### Challenge 1: Brand-accent loss

**Risk**: The warm-peach `--queue-accent` is being dropped. Product may feel the queue page looks too neutral after the rollback.

**Mitigation**: If product wants a hue on queue primary chrome, use `--status-info-*` (exists in both themes, WCAG-verified) for the row-flash animation only — do NOT reintroduce a private brand accent. Everything else goes neutral. Flag this to product during the Phase 5 manual-verification gate; do not re-add the accent pre-emptively.

### Challenge 2: Sticky-cell separation

**Risk**: `SubmissionTable` sticky `skillName` column currently uses `color-mix(white 84%, queue-paper 16%)` to stand out during horizontal scroll. Switching to flat `var(--bg)` would lose the separation cue.

**Mitigation**: Map sticky cell to `var(--bg-subtle)` rather than `var(--bg)`. Light theme: `#FAFAFA` on `#FFFFFF` — subtle but visible. Dark theme: `#161B22` on `#0D1117` — same subtle lift. Verify in Phase 5 manual matrix (both themes, all 3 viewport widths).

### Challenge 3: Dark-mode state-badge contrast

**Risk**: Dark-mode state badges use `var(--status-danger-text) = #F87171` on `var(--status-danger-bg) = rgba(248,113,113,0.12)`. Any accidental accent change could push below WCAG AA (4.5:1).

**Mitigation**: No intentional change to `--status-*` tokens in this increment. After Phase 3 completes, re-run the browser Accessibility panel audit (part of Phase 5 manual) on all 5 badge intents × 2 themes. Document contrast ratios in the PR description. If the audit finds a regression (it shouldn't — tokens are untouched), halt and triage.

### Challenge 4: `data-testid` preservation

**Risk**: Existing E2E specs query `[data-testid="queue-status-bar"]`, `[data-testid="stat-card-*"]`, etc. Style-only refactors often accidentally rename attributes.

**Mitigation**: Enforce "style-only" guardrail: tasks 3-7 may change CSS classes, inline styles, and font families, but MUST NOT rename, remove, or add `data-testid` attributes, DOM structure, or React component exports. Code review step checks the diff for any `data-testid` delta — if present, requires explicit justification.

### Challenge 5: 0673 data dependency for staging E2E

**Risk**: The staging `/queue` endpoint still has ~2.8 M duplicate rows from the 0673-tracked bug. Page render time there can exceed 30 s during peak, which would false-red the new E2E spec.

**Mitigation**: Document a 30 s Playwright action timeout for the new spec. If staging is mid-cleanup (0673 Step 5 in flight), wait for 0673 to pass its own gates before running 0697 E2E in staging. Local dev and preview environments have clean data and are unaffected.

### Challenge 6: Cross-browser computed `font-family` string

**Risk**: Phase 1's E2E assertion `font-family contains "geist-sans"` depends on how Chromium reports the CSS `font-family` stack. Firefox and WebKit may report the resolved family name differently (`Geist`, `"Geist Sans"`, quoted vs unquoted).

**Mitigation**: Use a case-insensitive regex match `/geist[\s_-]*sans/i` rather than exact string equality. Run the Playwright spec against all three engines in CI (Chromium, Firefox, WebKit) during the `/sw:done` gate.

---

## File Manifest

**Create (1 file)**:
- `tests/e2e/queue-design-consolidation.spec.ts` — 3-assertion Playwright spec.

**Modify (5 files)**:
- `src/app/globals.css` — delete two `--queue-*` blocks (lines 94-102 light, 191-199 dark); no replacement rules.
- `src/app/queue/QueuePageClient.tsx` — rewrite inline `<style>` string; drop `--queue-*` refs, `color-mix()`, Georgia, queue shadow/accent; flatten main to `var(--bg)`; hero title to Geist Sans (`.hero-h1` pattern).
- `src/app/queue/QueuePageComponents.tsx` — token swaps in `QueueSkeleton`, `StatCard`, `ReasonPill`, `ExecutionLogPanel`; drop wrapper-level Mono; flatten `StatCard` gradient.
- `src/app/queue/QueueStatusBar.tsx` — remove Mono wrapper; token swaps; normalize micro-padding to `0.25rem 0.625rem`.
- `src/app/queue/SubmissionTable.tsx` — token swaps; sticky cell → `var(--bg-subtle)`; highlight row → `var(--bg-hover)` or `--status-info-bg`.

**Reuse without modification (4 files)**:
- `src/lib/status-intent.ts` — `STATUS_VARS` read-only.
- `src/app/queue/shared/constants.ts` — `STATE_BADGES` already semantic.
- `src/app/queue/shared/components/StateBadge.tsx` — already consumes semantic tokens.
- `src/app/admin/queue/page.tsx` — uses separate `--admin-*` token family; out of scope.

**Delete (0 files)**: none.

---

## Risk Register

Transcribed from the approved plan. Likelihood × Impact × Mitigation per risk.

| # | Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| R1 | Brand-accent loss — product requests return of warm peach | Medium | Low (reversible) | Use `--status-info-*` for row-flash if a hue is demanded; don't reintroduce `--queue-accent`. Flag at Phase 5 manual gate. |
| R2 | Sticky-cell separation weakens in horizontal scroll | Medium | Low | Map sticky cell to `--bg-subtle` (not `--bg`); verify light+dark × all viewports in Phase 5. |
| R3 | Dark-mode state-badge WCAG regression | Low | High (a11y) | No `--status-*` changes in scope; re-run Accessibility audit at Phase 5; halt if regression found. |
| R4 | `data-testid` accidentally renamed | Low | High (test suite breaks) | Code-review guardrail: style-only refactor, no DOM / testid deltas. |
| R5 | `--queue-*` JS string references missed | Very low | Medium | Already `rg`-verified zero JS refs exist outside CSS and inline style objects; task 11 re-checks post-merge. |
| R6 | Staging E2E flakes on 0673 data condition | Medium (while 0673 open) | Medium (false red) | 30 s action timeout; coordinate with 0673 prod-cleanup timing; fall back to preview-deploy URL for validation. |
| R7 | Cross-browser `font-family` string mismatch | Low | Medium | Case-insensitive regex `/geist[\s_-]*sans/i`; run Chromium + Firefox + WebKit in CI. |

---

## Dependencies

**Blocked by**: nothing. This increment can begin immediately.

**Blocks**: nothing. Independent from 0673 (prod data cleanup) — ships on its own track.

**External**:
- Deployed preview URL (existing CI infrastructure — Cloudflare Pages or Vercel preview) required for Phase 5 manual matrix and final E2E screenshot run.
- Playwright infrastructure already present in repo (per existing 9 queue E2E specs).

**Internal references (no code dependency, only context)**:
- 0657-dark-theme-semantic-tokens — originating migration where the `--queue-*` drift was introduced.
- 0657E-dark-theme-followup — follow-up increment; does not touch queue.
- 0673-queue-reliability (Steps 5-7) — data-layer cleanup for the ~2.8 M duplicate rows causing the "hanging" symptom; independent.

---

## Success Criteria

Mirrors the approved plan's verification checklist. `/sw:done` will not close the increment until every box is checked.

- [ ] `rg -n "--queue-" src/` returns 0 hits.
- [ ] `rg -n "Georgia" src/app/queue/` returns 0 hits.
- [ ] In browser devtools on `/queue`: `getComputedStyle(document.documentElement).getPropertyValue('--queue-paper')` === `""`.
- [ ] Hero `h1` computed `font-family` contains `geist-sans` (case-insensitive), NOT `Georgia`.
- [ ] Queue surface cards render with `border-radius: 10px` (matches `.doc-card`), not `24px`.
- [ ] All 6 `src/app/queue/__tests__/*.test.tsx` specs pass unchanged.
- [ ] All 10 `tests/e2e/queue*.spec.ts` specs pass (9 existing untouched + 1 new consolidation spec).
- [ ] Light + dark × 1280 / 768 / 375 screenshots visually match `/skills` and `/docs` typography + chrome rhythm.
- [ ] State badges render with semantic colors in both themes (WCAG AA verified via devtools).
- [ ] `/admin/queue` renders unchanged (no regression from unchanged `STATE_BADGES` import).
- [ ] `git status` on `repositories/anton-abyzov/vskill-platform/` shows only the 5 modified files + 1 new test file + evidence directories (no incidental edits).

---

## ADR Decision

**Do we need a new ADR?** **No.**

**Rationale**: This increment is not an architectural choice — it is a **drift correction** that re-aligns the `/queue` page with decisions already captured during the 0657 dark-theme-semantic-tokens migration. The three-layer token pattern (raw tokens → semantic tokens → component consumption) is already in force and documented by the 0657 implementation; no competing design was considered here.

**Existing ADRs consulted** (in `.specweave/docs/internal/architecture/adr/`):
- `0674-01-warm-neutral-theme-tokens.md` — applies to `vskill-studio` (the `src/eval-ui/` SPA), not `vskill-platform`. Not load-bearing for this increment.
- `0674-04-tailwind-4-theme-layer.md` — same scope (`vskill-studio`). Not applicable.
- No dedicated ADR exists for the 0657 vskill-platform dark-theme migration; the decisions live in `.specweave/increments/0657-dark-theme-semantic-tokens/plan.md`.

**Amendment note**: this plan (0697) functions as a follow-up enforcement pass for the 0657 migration on the queue surface specifically. If the team later decides to formalize the platform-side design system into an ADR (recommended independent of this increment), reference both 0657 and 0697 as its implementation history.

**Action for implementation agents**: do NOT create a new ADR file. If a reviewer requests one during `/sw:done`, point them at this section.

---

## Execution Strategy

Per the approved plan, after `/sw:increment` completes the spec / plan / tasks, spawn a team-lead team:

- **globals-agent** — owns `src/app/globals.css` (Task 3).
- **queue-components-agent** — owns the 4 component files (Tasks 4-7 + Task 8 typography pass).
- **e2e-agent** — owns `tests/e2e/queue-design-consolidation.spec.ts` + before/after screenshot directories (Tasks 1-2 + 9-10).

Verification team (same pattern as 0673 Track A): test-runner + code-reviewer. Commit and push per umbrella convention (see CLAUDE.md "Git Rules").
