---
increment: 0731-studio-find-slick-ui
title: "Studio Find — Slick Search → Select → Install"
type: feature
priority: P1
status: planned
created: 2026-04-25
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Studio Find — Slick Search → Select → Install

## Overview

Increments 0716/0717/0718 shipped a working `/studio/find` page (search → result cards → clipboard install) but never wired a discoverable nav entry-point into Studio chrome — users currently have to know the URL. The shipped FindClient also lacks a select → version → install flow (no detail view, no version selector); install is a single button per result card.

The verified-skill.com platform already owns the polished primitives needed: a 612-line ⌘K SearchPalette (debounced search, SWR cache, infinite scroll, trending fallback, keyboard nav, tier/taint badges); a refined skill detail page at `/skills/[owner]/[repo]/[skill]` with TrustBadge, TierBadge, RepoHealthBadge, RepoLink, scan badges, TerminalBlock install, and a versions sub-route. Studio runs in the same Next.js app and consumes the same CSS tokens, so these patterns drop in without re-skinning.

This increment makes the Studio Find experience discoverable and complete: a "Find skills" nav button + ⌘K shortcut anywhere in `/studio/*`, an in-Studio skill detail route with a version selector, a one-click install panel using `TerminalBlock`, a Studio home CTA card, and continued visibility for the existing Submit-Find banner. No new aesthetic — adopt the platform's existing visual language for cohesion.

## Out of Scope

- Redesigning the verified-skill.com SearchPalette (adopted as-is)
- New aesthetic / theme tokens (existing platform CSS vars only)
- Editing skill data, scan results, or registry behavior
- E2E search performance tuning (covered by parallel 0715)
- Rich version diff/changelog viewer (link to existing `/skills/.../versions/compare` instead)

## User Stories

### US-001: "Find skills" nav button + ⌘K shortcut in Studio chrome (P1)
**Project**: vskill-platform

**As a** Studio user browsing any `/studio/*` page
**I want** a discoverable "Find skills" button in the Studio top bar plus a global ⌘K (Mac) / Ctrl+K (Win/Linux) shortcut
**So that** I can open the search palette from anywhere in Studio without knowing or typing the `/studio/find` URL

**Acceptance Criteria**:
- [ ] **AC-US1-01**: `FindNavButton` renders in the `studio-nav-extras` container, immediately to the left of `SubmitNavButton`, with the same flex layout and height (matches existing button style: `padding 0.375rem 0.75rem`, `borderRadius 6`, mono font, 14×14 search-icon SVG).
- [ ] **AC-US1-02**: Click → opens the SearchPalette overlay by dispatching the existing custom `openSearch` event (same contract used on verified-skill.com).
- [ ] **AC-US1-03**: ⌘K (Mac) / Ctrl+K (Win/Linux) anywhere under `/studio/*` opens the palette. A shortcut-hint badge (`⌘K`) renders inside the button on the right edge.
- [ ] **AC-US1-04**: Button has `data-testid="studio-find-nav-button"` for E2E hooks and ARIA label `"Find verified skills — opens search (⌘K)"`.
- [ ] **AC-US1-05**: Reduced-motion is respected — no shortcut-hint pulse animation when the user prefers reduced motion (`prefers-reduced-motion: reduce`).

---

### US-002: SearchPalette mounted in Studio with same-origin search (P1)
**Project**: vskill-platform

**As a** Studio user
**I want** the same ⌘K palette experience that verified-skill.com offers, but driven by Studio's same-origin search endpoint
**So that** I get debounced search, trending fallback, keyboard nav, and trust signals without leaving Studio or hitting cross-origin rate limits

**Acceptance Criteria**:
- [ ] **AC-US2-01**: A new thin wrapper `StudioSearchPalette.tsx` reuses verified-skill.com's `SearchPalette` (or extracted shared core). Same UX: 150ms debounce, SWR 60s cache, trending preload, infinite scroll via IntersectionObserver, keyboard nav (↑ ↓ Enter Esc), MiniTierBadge + taint warning per row.
- [ ] **AC-US2-02**: Fetches results from same-origin `/api/v1/studio/search` (shipped in 0716 — preserves rate-limit insulation and studio-specific telemetry). Trending fetch from existing `/api/v1/stats`.
- [ ] **AC-US2-03**: Selecting a result (Enter or click) navigates to `/studio/find/[owner]/[repo]/[skill]` (new in-Studio detail route from US-003) and closes the palette.
- [ ] **AC-US2-04**: Mounted once in `studio/layout.tsx` so it is available on every Studio page (home, find, skill detail).
- [ ] **AC-US2-05**: Telemetry: fire-and-forget `POST /api/v1/studio/telemetry/search-select` with `{ skillName, q, ts }` on result selection. Mirrors the `install-copy` pattern from 0716; failures must not block navigation.
- [ ] **AC-US2-06**: Blocked / tainted skills surface threat signals inline in palette rows, reusing `MiniTierBadge` `BLOCKED` / `TAINTED` styling.

---

### US-003: In-Studio skill detail view with version selector (P1)
**Project**: vskill-platform

**As a** Studio user who selected a skill from the palette
**I want** to see the skill's trust signals, scan results, and last 5 versions without leaving Studio, then copy a versioned install command in one click
**So that** I can vet and install a specific version with the same fidelity as verified-skill.com, inside the Studio shell

**Acceptance Criteria**:
- [ ] **AC-US3-01**: New route `app/studio/find/[owner]/[repo]/[skill]/page.tsx` renders a server component that reads the skill via the same `getSkillByName` data function used by `/skills/[owner]/[repo]/[skill]/page.tsx`. No DB schema changes.
- [ ] **AC-US3-02**: Layout reuses platform components: `TrustBadge`, `TierBadge`, `PublisherLink`, `RepoLink`, `RepoHealthBadge`, `TaintWarning`, `SectionDivider`. Same hero (display name, publisher, tier badge, GitHub stars), same description, same scan-results row.
- [ ] **AC-US3-03**: Versions section lists the last 5 versions (newest first) via `getSkillVersions`. Each version is a clickable row showing `v1.2.3 · 2026-04-12 · author@email` with a "Selected" indicator on the active one. Default selection: latest published version. A "see all" link points to `/skills/[owner]/[repo]/[skill]/versions` (full platform version history).
- [ ] **AC-US3-04**: Install panel uses `TerminalBlock` (black bg, mono): shows `vskill install <publisher>/<skill>` by default; when a non-latest version is selected, shows `vskill install <publisher>/<skill>@<version>`. A Copy button sits on the right side of the block. Skill identifier is sanitized with the regex `^[a-zA-Z0-9._@/-]+$` (same rule as 0717 AC-US3-01).
- [ ] **AC-US3-05**: Click Copy → clipboard write + toast "Run `vskill install ...` in your terminal" (same toast pattern as the existing `InstallButton`: 3.5s auto-dismiss, fallback path when `navigator.clipboard` is unavailable).
- [ ] **AC-US3-06**: Telemetry `POST /api/v1/studio/telemetry/install-copy` with `{ skillName, version, q: "", ts }`. The endpoint payload accepts an optional `version` field — backward compatible with the 0716 contract.
- [ ] **AC-US3-07**: When `isBlocked === true`, the install panel is replaced by a "This skill is blocked" panel (mirrors AC-US3-04 of 0717).
- [ ] **AC-US3-08**: A "← Back to results" link at the top returns to `/studio/find?q=<lastQuery>` when the prior query is recoverable from `document.referrer` or sessionStorage; otherwise to `/studio/find`.
- [ ] **AC-US3-09**: Keyboard tab order is: back link → versions list → copy button. Version rows are real `<button>` elements; Enter activates them.

---

### US-004: Studio home CTA card for Find (P2)
**Project**: vskill-platform

**As a** first-time Studio user landing on `/studio`
**I want** a prominent CTA card that surfaces the new Find experience above the existing 4-card feature grid
**So that** I discover ⌘K search without needing to scan the nav bar

**Acceptance Criteria**:
- [ ] **AC-US4-01**: A feature-card-style block on `/studio` above the existing 4-card grid with title "Find verified skills", short copy "Search the registry. Trust signals inline. Install in one click.", and a primary CTA button "Search skills (⌘K)" that dispatches the `openSearch` event.
- [ ] **AC-US4-02**: Card matches existing home card aesthetic (colored border/bg via CSS vars, pill badge, mono font) with a distinct accent color (e.g. `--accent-cyan`) so it does not collide with the 4 existing feature cards.
- [ ] **AC-US4-03**: On mobile (≤375px) the card stacks above the hero CopyButton block. No layout reflow at SSR (no client-only height changes that cause CLS).

---

### US-005: Submit-Find banner stays visible across Find surfaces (P2)
**Project**: vskill-platform

**As a** Studio user who cannot find the skill they need
**I want** the existing Submit-Find banner to remain reachable from the Find page and the new skill detail page
**So that** I can submit my own skill via the existing deep-link flow without losing context

**Acceptance Criteria**:
- [ ] **AC-US5-01**: The `SubmitFindBanner` shipped in 0718 still renders below the empty-state on `/studio/find`. No regression in placement, copy, or deep-link behavior.
- [ ] **AC-US5-02**: On the new skill detail page, a "Don't see what you need? Submit your skill →" link appears in the footer of the install panel and uses the existing `useSubmitDeepLink` hook to construct the deep link.

---

## Functional Requirements

### FR-001: Accessibility — WCAG 2.1 AA
All new UI must satisfy WCAG 2.1 AA: visible focus states on every interactive element, non-color-only state indicators (icon + text for "Selected", "Blocked", "Tainted"), text contrast ≥ 4.5:1 for body and ≥ 3:1 for large text, palette overlay traps focus while open and restores focus to the invoking element on close.

### FR-002: Keyboard navigation
Every flow must be completable without a mouse: ⌘K / Ctrl+K opens the palette; ↑ ↓ moves selection; Enter activates; Esc closes. On the detail page, Tab order is back → versions list → copy. Version rows are buttons (not divs with click handlers). The home CTA button is reachable via Tab and activates with Enter / Space.

### FR-003: Reduced-motion
`prefers-reduced-motion: reduce` disables non-essential animations: the ⌘K hint pulse (AC-US1-05), any palette open/close transitions beyond a static fade, and toast slide-ins. Functional state changes still convey through static styles.

### FR-004: Telemetry — fire-and-forget
All telemetry POSTs (`/api/v1/studio/telemetry/search-select`, `/api/v1/studio/telemetry/install-copy`) are fire-and-forget: invoked with `keepalive: true` (or equivalent), not awaited, and any failure (network, 4xx, 5xx) MUST NOT block UI navigation, copy, or palette behavior. Endpoints respond 200 on POST and 405 on GET / other verbs.

### FR-005: Dark / light mode parity
All new components render correctly in both dark and light themes by consuming existing CSS vars (`var(--bg-subtle)`, `var(--tier-verified)`, `var(--font-geist-mono)`, etc.). No hard-coded `#000` or `#fff` outside of `TerminalBlock`. Verified by manual visual smoke in both modes.

## Performance Budgets

- **Palette open**: from `openSearch` dispatch (button click or ⌘K) to first paint of the palette overlay < 100ms on a warm route.
- **Debounced search**: 150ms debounce window from last keystroke to fetch dispatch (matches verified-skill.com behavior); first results visible < 350ms p95 on a cache-warm same-origin endpoint.
- **Detail-page TTFB**: < 500ms p95 with cache-warm `getSkillByName` (server-component path, no client waterfall).

## Risk Register

| ID | Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| R-01 | SearchPalette extraction breaks existing platform `/skills` usage | Medium | High | Prefer minimum-diff path: add `searchUrl` + `onSelect` props with defaults that preserve current platform behavior. Cover both consumers with unit tests before refactor. |
| R-02 | Version data shape mismatch — `getSkillVersions` returns fewer/extra fields than the detail UI needs | Medium | Medium | Type-check the `getSkillVersions` return contract once at the page boundary; render gracefully when `author` or `publishedAt` is missing (show `—`). Add an integration test for the "missing fields" case. |
| R-03 | Telemetry endpoint flooding from rapid palette interactions or scripted clients | Low | Medium | Fire-and-forget with `keepalive: true`; route applies the same lightweight throttle as `install-copy` from 0716 (per-IP, per-skill window). No retry on failure. |

## Success Criteria

- "Find skills" nav button is visibly discoverable in Studio chrome on first visit (no URL knowledge required).
- ⌘K (Mac) / Ctrl+K (Win/Linux) opens the palette on every page under `/studio/*`.
- The install command shown on the detail page is copyable for any of the last 5 versions and matches `vskill install <publisher>/<skill>[@<version>]` exactly.
- No regression on the existing `/studio/find` page (FindClient list, ResultCard, InstallButton, SubmitFindBanner all behave as shipped in 0717/0718).

## Dependencies

- **0716** — `/api/v1/studio/search` (same-origin proxy with `publisher`, `offset/total`) and `/api/v1/studio/telemetry/install-copy`. Reused as-is; this increment extends the install-copy payload with an optional `version` field.
- **0717** — `/studio/find` page with `FindClient`, `ResultCard`, `InstallButton` (clipboard + toast + telemetry). Reused; result-card click target updates to navigate to the new detail route.
- **0718** — `SubmitNavButton`, `SubmitFindBanner`, `useSubmitDeepLink` hook. Reused unchanged; the new `FindNavButton` mounts immediately to the left of `SubmitNavButton`.
- **Platform components** (verified-skill.com side, same Next.js app): `SearchPalette.tsx`, `TrustBadge`, `TierBadge`, `PublisherLink`, `RepoLink`, `RepoHealthBadge`, `TaintWarning`, `SectionDivider`, `TerminalBlock`, and the `getSkillByName` / `getSkillVersions` data functions from `@/lib/data`.
