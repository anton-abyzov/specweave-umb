---
increment: 0741-vskill-cli-studio-find-palette
title: vskill CLI Studio Find Palette
type: feature
priority: P1
status: completed
created: 2026-04-26T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: vskill CLI Studio Find Palette

## Overview

The online Studio at `verified-skill.com/studio` ships a polished search palette via increments 0716/0717/0731 — `Find skills` button, ⌘K shortcut, in-Studio detail view with version selector, and one-click install. Confirmed live (curl returns the markup).

The local `vskill studio` CLI is a **different surface**: `eval-server.ts` (Node http) static-serves a Vite-built bundle from `vskill/dist/eval-ui` (source: `vskill/src/eval-ui/`). Grep across `src/eval-ui/src/**` returns zero find/search UI — users have no in-CLI way to discover skills they don't already have installed locally. They must either know the URL `verified-skill.com/studio/find` or open `vskill install <name>` blind.

This gap was missed because 0731's spec targeted `vskill-platform/src/app/studio/*` (Next.js app routes), not the eval-ui Vite bundle baked into the vskill npm package. This increment ports the same UX into the eval-ui surface and extends `eval-server`'s `platform-proxy` to forward the search/telemetry endpoints to upstream. The browser must call ONLY localhost eval-server — never `verified-skill.com` directly (architecture rule from `project_studio_cors_free_architecture` memory).

## Out of Scope

- Redesign of the palette aesthetic (reuse the source SearchPalette CSS / eval-ui CSS variable tokens unchanged)
- Changes to vskill-platform server-side endpoints (already shipped in 0716/0731)
- Auto-install / one-click install execution (still copy-to-clipboard; the user runs the command in their terminal)
- Changes to ⌘K (CommandPalette) or ⌘P (ProjectCommandPalette) behavior — this increment only adds a new ⌘⇧K binding
- Marketplace browse / category filters beyond what the source SearchPalette already supports

## User Stories

### US-001: ⌘⇧K opens Find-skills palette from anywhere in eval-ui
**Project**: vskill

**As a** vskill studio user
**I want** to press ⌘⇧K (Mac) or Ctrl+Shift+K (Win/Linux) anywhere in eval-ui
**So that** I can search the verified-skill registry without leaving the local Studio

**Acceptance Criteria**:
- [x] **AC-US1-01**: A new `FindSkillsPalette.tsx` component is mounted at App root via `React.lazy`, mirroring the existing `CommandPalette` and `ProjectCommandPalette` lazy-load pattern in `vskill/src/eval-ui/src/App.tsx:49`.
- [x] **AC-US1-02**: A global `keydown` listener in `App.tsx` registers `⌘⇧K` (Mac, `metaKey + shiftKey + KeyK`) and `Ctrl+Shift+K` (Win/Linux, `ctrlKey + shiftKey + KeyK`) — pressing the combo toggles the palette open. Existing ⌘K (CommandPalette) and ⌘P (ProjectCommandPalette) bindings continue to work unchanged.
- [x] **AC-US1-03**: The palette also opens in response to a `window.openFindSkills` `CustomEvent` (mirror of platform's `openSearch` contract; renamed to avoid collision with the existing CommandPalette listener which already binds `openSearch`).
- [x] **AC-US1-04**: `Esc` closes the palette and returns focus to the invoking element (button or last-focused element before the keyboard shortcut).
- [x] **AC-US1-05**: When `prefers-reduced-motion: reduce` is set, palette open/close animations collapse to a static fade only.

---

### US-002: "Find skills" button in TopRail with shortcut hint
**Project**: vskill

**As a** vskill studio user who doesn't know the keyboard shortcut
**I want** a discoverable "Find skills" button in the top bar
**So that** I can find the search feature visually without memorising shortcuts

**Acceptance Criteria**:
- [x] **AC-US2-01**: A new `FindSkillsNavButton` component mounts in TopRail (the header area rendered around `App.tsx:503`), positioned to the left of the existing `+ New Skill` button. It matches the existing button style: same height, padding, font, and CSS-variable tokens.
- [x] **AC-US2-02**: Clicking the button dispatches `window.dispatchEvent(new CustomEvent("openFindSkills"))` — the palette opens via the listener from AC-US1-03.
- [x] **AC-US2-03**: A shortcut-hint badge renders inside the button on the right edge: `⌘⇧K` on Mac, `Ctrl+Shift+K` on Win/Linux. Platform detection mirrors `vskill-platform/src/app/studio/components/FindNavButton.tsx:48-53` (SSR-safe `navigator.platform` probe).
- [x] **AC-US2-04**: The button has `data-testid="find-skills-nav-button"` for E2E hooks and ARIA label `"Find verified skills — opens search (⌘⇧K)"` (or the Win/Linux equivalent).
- [x] **AC-US2-05**: Under `prefers-reduced-motion: reduce`, the shortcut-hint badge does not pulse or animate.

---

### US-003: Search palette UX — debounce, trending, infinite scroll, keyboard nav
**Project**: vskill

**As a** vskill studio user inside the open palette
**I want** the same fast, polished search UX as `verified-skill.com/studio` — debounced search, trending results when empty, infinite scroll, keyboard navigation, and inline trust badges
**So that** finding the right skill is fast and high-confidence

**Acceptance Criteria**:
- [x] **AC-US3-01**: A new `SearchPaletteCore.tsx` is created at `vskill/src/eval-ui/src/components/FindSkillsPalette/SearchPaletteCore.tsx` as a near-verbatim port of `vskill-platform/src/app/components/SearchPalette.tsx` (680 LOC). Replace `useRouter` from `next/navigation` with an `onNavigate(href: string)` callback prop. Replace `@/lib/sanitize-html` and `@/lib/skill-url` imports with copies in `vskill/src/eval-ui/src/lib/`.
- [x] **AC-US3-02**: When the query is empty or 1 character, the palette fetches `/api/v1/stats` (proxied through eval-server) and renders the `trendingSkills` list. Response envelope: `{ trendingSkills: [...] }`.
- [x] **AC-US3-03**: For queries of 2+ characters, the palette debounces 150ms after the last keystroke, then fetches `/api/v1/studio/search?q=<query>&limit=20&offset=0` (proxied). Response envelope: `{ results, total, pagination: { hasMore } }`.
- [x] **AC-US3-04**: Results are cached SWR-style for 60 seconds in an in-memory `Map` + ref (preserve the source pattern from `SearchPalette.tsx:219-220`). An `AbortController` cancels in-flight fetches when the query changes.
- [x] **AC-US3-05**: An `IntersectionObserver` sentinel at the bottom of the result list triggers the next-page fetch when `hasMore` is true. New pages append to the existing list (no reset). Hard cap at 10 pages (200 results); after the cap, render a "See all on verified-skill.com" link instead.
- [x] **AC-US3-06**: Keyboard navigation: ↑ / ↓ moves selection, Enter activates, Esc closes. The "type-to-search-from-anywhere" behavior (printable character pressed outside an input opens the palette pre-filled with that character) from the source SearchPalette is preserved.
- [x] **AC-US3-07**: Each result row renders a `MiniTierBadge` and inline `BLOCKED` / `TAINTED` warnings — port the `MiniTierBadge.tsx` component from `vskill-platform/src/app/components/`.

---

### US-004: In-eval-ui skill detail view with version selector + install copy
**Project**: vskill

**As a** vskill studio user who selected a result in the palette
**I want** an in-Studio detail view that shows trust signals, the last 5 versions, and a one-click copyable install command
**So that** I can vet and install a specific version without context-switching to the browser

**Acceptance Criteria**:
- [x] **AC-US4-01**: Selecting a result (Enter or click) opens a new in-eval-ui detail panel — `SkillDetailPanel.tsx` mounted at App root via `React.lazy`. No router change required (eval-ui is single-page, hash-routed).
- [x] **AC-US4-02**: The detail panel fetches `/api/v1/skills/[owner]/[repo]/[skill]` (proxied) for skill metadata and `/api/v1/skills/[owner]/[repo]/[skill]/versions` (proxied) for the version list. Both endpoints already exist on platform — covered by the existing `/api/v1/skills/*` proxy glob.
- [x] **AC-US4-03**: The panel renders these ported components: `TrustBadge`, `TierBadge`, `RepoLink`, `RepoHealthBadge`, `TaintWarning`, `SectionDivider`, `TerminalBlock`. All copied from `vskill-platform/src/app/components/`. Per Explore subagent verification, these are pure React with no Next.js dependencies (replace only `next/link` with `<a>` in `RepoLink`).
- [x] **AC-US4-04**: The Versions section shows the last 5 versions, newest first. Each row is a `<button>` displaying `vX.Y.Z · YYYY-MM-DD · author@email` with a "Selected" indicator on the active row. The default selection is the latest published version. A "see all versions →" link points to `https://verified-skill.com/skills/[owner]/[repo]/[skill]/versions` (opens in a new browser tab).
- [x] **AC-US4-05**: The Install panel uses `TerminalBlock` (black background, mono font) and shows `vskill install <publisher>/<skill>` for the latest version, or `vskill install <publisher>/<skill>@<version>` when a non-latest version is selected. A Copy button writes the command to the clipboard via `navigator.clipboard.writeText` (with `document.execCommand('copy')` fallback for browsers without the Clipboard API). On copy, a toast is dispatched via the existing `ToastProvider`: `Run vskill install ... in your terminal` (3.5s auto-dismiss).
- [x] **AC-US4-06**: The skill identifier is sanitized with the regex `^[a-zA-Z0-9._@/-]+$` before being injected into the install command. Mismatching identifiers render an error state instead of the install panel. Matches the 0717 contract.
- [x] **AC-US4-07**: When `isBlocked === true` on the skill metadata, the install panel is replaced by a "This skill is blocked" panel (mirrors AC-US3-04 of 0717). The Versions section is still rendered for transparency.
- [x] **AC-US4-08**: A "← Back to results" link at the top closes the panel and re-opens the palette pre-filled with the previous query, restored from `sessionStorage` (key `find-skills:last-query`).
- [x] **AC-US4-09**: Keyboard tab order: back link → version list → copy button. Version rows are real `<button>` elements; Enter activates them. Esc closes the panel and returns to the palette.

---

### US-005: Extend eval-server platform-proxy to forward studio + stats endpoints
**Project**: vskill

**As an** eval-ui browser process
**I want** new path prefixes (`/api/v1/studio/search`, `/api/v1/studio/telemetry/`, `/api/v1/stats`) to be forwarded by `eval-server` to the upstream platform
**So that** the palette and detail view never make cross-origin calls and the CORS-free architecture rule is preserved

**Acceptance Criteria**:
- [x] **AC-US5-01**: `vskill/src/eval-server/platform-proxy.ts` `shouldProxyToPlatform()` (currently at line 84, matching only `/api/v1/skills/*`) is extended to also match `/api/v1/studio/search`, `/api/v1/studio/telemetry/`, and `/api/v1/stats`. The existing `/api/v1/skills/*` match is preserved unchanged.
- [x] **AC-US5-02**: `getPlatformBaseUrl()` already defaults to `https://verified-skill.com` and is overridable via the `VSKILL_PLATFORM_URL` env var. No code change required — this AC documents the confirmed default and adds a regression test asserting that an unset env still resolves to the production URL.
- [x] **AC-US5-03**: Telemetry POSTs (`/api/v1/studio/telemetry/search-select`, `/api/v1/studio/telemetry/install-copy`) are forwarded with body intact (the existing `proxyToPlatform()` already streams `req.pipe(upstreamReq)`). The eval-ui caller MUST invoke them fire-and-forget with `keepalive: true`; failures (4xx, 5xx, network) MUST NOT block UI navigation, copy, or palette behavior.
- [x] **AC-US5-04**: New Vitest cases in `vskill/src/eval-server/platform-proxy.test.ts` cover the new prefixes (positive: each is matched; negative: `/api/skills` without `/v1/` is NOT matched because eval-server owns it; negative: `/api/v1/foo` is NOT matched).
- [x] **AC-US5-05**: `/api/v1/skills/[owner]/[repo]/[skill]` and `.../versions` are already covered by the existing `/api/v1/skills/*` glob. Add a single confirming test case rather than new code.

---

## Functional Requirements

### FR-001: Accessibility — WCAG 2.1 AA
Every new interactive element has a visible focus state, non-color-only state indicators (icon + text for "Selected", "Blocked", "Tainted"), text contrast ≥ 4.5:1 body / ≥ 3:1 large. The palette overlay and detail panel both trap focus while open and restore focus to the invoking element on close.

### FR-002: Keyboard-completable
Every flow MUST work without a mouse. ⌘⇧K opens the palette; ↑ ↓ moves selection; Enter activates a result; Esc closes any overlay. On the detail panel, Tab order is back → version list → copy. Version rows are real `<button>` elements (not divs with click handlers).

### FR-003: Reduced motion
`prefers-reduced-motion: reduce` disables non-essential animations: the shortcut-hint pulse (AC-US2-05), palette open/close transitions beyond a static fade (AC-US1-05), and toast slide-ins. Functional state changes still convey through static styles.

### FR-004: Telemetry — fire-and-forget
All telemetry POSTs (`/api/v1/studio/telemetry/search-select`, `/api/v1/studio/telemetry/install-copy`) are invoked with `keepalive: true`, are not awaited, and any failure (network, 4xx, 5xx) MUST NOT block UI navigation, copy, or palette behavior. No `console.error` in production.

### FR-005: Theme parity
All new components render correctly in both light and dark themes by consuming existing eval-ui CSS variable tokens (`--bg-canvas`, `--text-primary`, `--border-default`, `--font-geist-mono`, etc. from `vskill/src/eval-ui/src/styles/globals.css`). No hard-coded `#000` or `#fff` outside `TerminalBlock`.

### FR-006: Bundle-size budget
The `dist/eval-ui` build delta from this increment MUST be < 50KB gzip. Enforce via a post-build size check (existing CI hook or new check). `FindSkillsPalette` and `SkillDetailPanel` MUST be lazy-loaded (`React.lazy` + `Suspense`) so they do not bloat the initial bundle.

## Performance Budgets

- **Palette open**: from `openFindSkills` event (button click or ⌘⇧K) to first paint of the palette overlay < 100ms warm.
- **Debounced search**: 150ms debounce window from last keystroke to fetch dispatch (matches the source SearchPalette behavior); first results visible < 350ms p95 on cache-warm proxy hit.
- **Detail panel TTFB**: < 600ms p95 on cache-warm proxy hit (slightly looser than the platform native path because of the proxy hop).

## Risk Register

| ID | Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| R-01 | Porting SearchPalette.tsx (680 LOC) introduces subtle behavior drift from the platform version | Medium | Medium | Keep the port a near-verbatim copy. Diff with the source after each refactor. Cover the same scenarios the platform unit tests cover. |
| R-02 | ⌘⇧K conflicts with browser DevTools shortcut on some browsers (Chrome on some platforms binds ⌘⇧K to Inspect Element history) | Medium | Low | Validate empirically during implementation. If confirmed, fall back to ⌘⌥K (Alt+K) and update the badge. Document in the spec footnote. |
| R-03 | Bundle-size regression in `dist/eval-ui` from porting 8+ components | Medium | Low | Lazy-load `FindSkillsPalette` and `SkillDetailPanel`. Verify post-build `dist/eval-ui` size delta < 50KB gzip via FR-006 check. |
| R-04 | Two parallel features (0670 + 0741) breach focus discipline | Low | Medium | This increment only plans now; implementation does not start until 0670 closes. WIP cap (max 2 features) respected. |
| R-05 | Detail-page version list is empty for skills without published versions | Low | Low | Render a "No published versions yet" empty state. Install command falls back to `vskill install <publisher>/<skill>` (latest implied). |

## Success Criteria

- "Find skills" button is visibly discoverable in the eval-ui TopRail on first launch (no URL or shortcut knowledge required).
- ⌘⇧K (Mac) / Ctrl+Shift+K (Win/Linux) opens the palette from any view in `vskill studio`.
- Search results stream in within 350ms p95 on a warm cache; trending list renders for empty queries.
- Selecting a result opens an in-eval-ui detail panel within 600ms TTFB; the install command is copyable for any of the last 5 versions and matches `vskill install <publisher>/<skill>[@<version>]` exactly.
- Existing ⌘K (CommandPalette) and ⌘P (ProjectCommandPalette) bindings continue to work without regression.
- `dist/eval-ui` bundle-size delta < 50KB gzip.

## Dependencies

- **Upstream platform endpoints (already shipped)**: `/api/v1/skills/search`, `/api/v1/studio/search`, `/api/v1/stats`, `/api/v1/studio/telemetry/[kind]`, `/api/v1/skills/[owner]/[repo]/[skill]`, `/api/v1/skills/[owner]/[repo]/[skill]/versions`. No platform changes needed.
- **eval-ui existing patterns**: `CommandPalette` (lazy-load reference), `ProjectCommandPalette` (overlay + ⌘P binding pattern), `ToastProvider` (toast dispatch), `StudioContext` (state), CSS variable tokens in `globals.css`.
- **eval-server**: `platform-proxy.ts` extension only — `eval-server.ts` integration point at line 132-135 already invokes the proxy guard.
- **Related but not blocking**: 0716 (search API + telemetry), 0717 (find UI on platform), 0731 (slick UI on platform). All shipped on `vskill-platform`. This increment is the eval-ui counterpart and can ship independently of any further platform work.
