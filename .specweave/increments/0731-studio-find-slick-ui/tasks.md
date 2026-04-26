---
increment: 0731-studio-find-slick-ui
title: "Studio Find — Slick Search → Select → Install"
type: tasks
created: 2026-04-25
test_mode: TDD
tdd_enforcement: strict
---

# Tasks: Studio Find — Slick Search → Select → Install

## Overview

This increment makes the Studio Find experience discoverable and complete. It wires a "Find skills" nav button + ⌘K shortcut into Studio chrome, mounts a `StudioSearchPalette` wrapper that reuses the platform's `SearchPalette` (via backward-compatible props, per ADR 0731-01), adds a new in-Studio skill detail route (`/studio/find/[owner]/[repo]/[skill]`) with a `VersionPicker` (ARIA radiogroup), an `InstallPanel` (clipboard + toast + telemetry), and surfaces the Submit-Find banner on the detail page. Three prereq tasks (layout collision gate, workspace-fingerprint helper, `BlockedSkillView` lift) must complete before any consumer component. The `SearchPalette` refactor runs next as the primary regression gate (existing 713-LOC/59-case suite must pass unchanged). All tasks run TDD-strict: write failing test first, confirm RED, implement, confirm GREEN.

---

## Task List

### T-001: [GREEN] Gate root layout — confirm SearchPalette does NOT mount on /studio/* routes
**User Story**: US-002 | **Satisfies ACs**: AC-US2-04 | **Status**: [x] completed
**Test Plan (RED)**:
- Given the root `layout.tsx` and `studio/layout.tsx` both exist
- When rendering any `/studio/*` route
- Then the platform `SearchPalette` (in root layout) is NOT rendered — assert `<SearchPalette />` import is absent from root layout or is gated via `usePathname().startsWith("/studio")` check
**Test files**: `src/app/__tests__/layout.collision.test.tsx`
**Implementation files**: `src/app/layout.tsx` (gate if needed — no-op if already absent)
**Acceptance**: Playwright confirms no double-palette on `/studio` (only one `[role="dialog"]` from SearchPalette is present after ⌘K).

---

### T-002: [GREEN] Use authFetch (no new helper needed) — recon-collapsed
**User Story**: US-002, US-003 | **Satisfies ACs**: AC-US2-05, AC-US3-06 | **Status**: [x] completed
**Recon outcome**: `@/lib/auth-fetch` (`authFetch`) already auto-attaches `X-Workspace-Fingerprint` header — confirmed in `InstallButton.tsx` (0723). No new helper needed.
**Acceptance (carries to consumers)**: T-009 `StudioSearchPalette` and T-016 `InstallPanel` MUST use `authFetch` instead of raw `fetch` for telemetry POSTs. Telemetry test cases assert `authFetch` was called (not raw fetch).

---

### T-003: [GREEN] Lift BlockedSkillView to shared component
**User Story**: US-003 | **Satisfies ACs**: AC-US3-07 | **Status**: [x] completed
**Test Plan (RED)**:
- Given `BlockedSkillView` and `BlockedRow` are currently defined inside `src/app/skills/[owner]/[repo]/[skill]/page.tsx`
- When writing `src/app/components/__tests__/BlockedSkillView.test.tsx` importing from `@/app/components/BlockedSkillView`
- Then the import fails (RED — component not yet extracted)
**Test files**: `src/app/components/__tests__/BlockedSkillView.test.tsx`
**Implementation files**: `src/app/components/BlockedSkillView.tsx` (new — lifted from platform page), `src/app/skills/[owner]/[repo]/[skill]/page.tsx` (remove definition, add import)
**Acceptance**: `BlockedSkillView.test.tsx` passes; existing platform page renders BLOCKED state identically (no visual regression).

---

### T-004: [GREEN] SearchPalette — export SearchResult type and add searchUrl prop
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02 | **Status**: [x] completed
**Test Plan (RED)**:
- Given the new test file `SearchPalette.props.test.tsx` asserts `searchUrl` is forwarded to `fetch`
- When `SearchPalette` is rendered with `searchUrl="/api/v1/studio/search"` and a query is typed
- Then `fetch` is called with URL containing `/api/v1/studio/search` (not `/api/v1/skills/search`) — for debounced fetch, SWR revalidate, and handleLoadMore sites
**Test files**: `src/app/components/__tests__/SearchPalette.props.test.tsx`
**Implementation files**: `src/app/components/SearchPalette.tsx`
**Acceptance**: New test passes; entire existing `SearchPalette.test.tsx` (59 cases) passes without any edits.

---

### T-005: [GREEN] SearchPalette — add selectHref prop and store sourceResult on allItems
**User Story**: US-002 | **Satisfies ACs**: AC-US2-03 | **Status**: [x] completed
**Test Plan (RED)**:
- Given `SearchPalette.props.test.tsx` (extend) asserts `selectHref` is called and its return value is used in `router.push`
- When `selectHref={(r) => "/studio/find/" + r.name}` is passed and user selects a result
- Then `router.push` is called with the `selectHref` return value, not the default `skillUrl(r.name)`
**Test files**: `src/app/components/__tests__/SearchPalette.props.test.tsx` (extend)
**Implementation files**: `src/app/components/SearchPalette.tsx`
**Acceptance**: Test passes; default platform behavior (no `selectHref` prop) verified unchanged by existing suite.

---

### T-006: [GREEN] SearchPalette — add onSelect prop, fire before router.push
**User Story**: US-002 | **Satisfies ACs**: AC-US2-05, AC-US2-06 | **Status**: [x] completed
**Test Plan (RED)**:
- Given `SearchPalette.props.test.tsx` (extend) asserts `onSelect` fires exactly once per skill selection with `(result, query)`
- When a skill result row is selected via keyboard Enter
- Then `onSelect` is called with the correct `SearchResult` object and the current query string; `onSelect` is NOT called for category/action items; existing platform mount (no `onSelect` prop) test passes unchanged
**Test files**: `src/app/components/__tests__/SearchPalette.props.test.tsx` (extend)
**Implementation files**: `src/app/components/SearchPalette.tsx`
**Acceptance**: Full `SearchPalette.props.test.tsx` suite green; full existing `SearchPalette.test.tsx` (59 cases) green; `SearchResult` type is exported at module scope.

---

### T-007: [GREEN] FindNavButton component — renders, ARIA, testid
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-04 | **Status**: [x] completed
**Test Plan (RED)**:
- Given `FindNavButton.test.tsx` imports from `@/app/studio/components/FindNavButton` (file does not exist yet)
- When rendered
- Then component has `data-testid="studio-find-nav-button"`, `aria-label="Find verified skills — opens search (⌘K)"`, renders a search icon SVG, and text "Find skills"
**Test files**: `src/app/studio/components/__tests__/FindNavButton.test.tsx`
**Implementation files**: `src/app/studio/components/FindNavButton.tsx` (new)
**Acceptance**: All render/ARIA assertions pass.

---

### T-008: [GREEN] FindNavButton — click dispatches openSearch, ⌘K hint, reduced-motion
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02, AC-US1-03, AC-US1-05 | **Status**: [x] completed
**Test Plan (RED)**:
- Given `FindNavButton.test.tsx` (extend T-007) with `window.dispatchEvent` spy
- When button is clicked
- Then `window.dispatchEvent` is called with a `CustomEvent("openSearch")`; ⌘K shortcut hint `<kbd>` is rendered; when `prefers-reduced-motion: reduce` is active, no animation class/attribute is applied; `FindNavButton` does NOT register its own keydown listener (SearchPalette owns ⌘K globally)
**Test files**: `src/app/studio/components/__tests__/FindNavButton.test.tsx` (extend)
**Implementation files**: `src/app/studio/components/FindNavButton.tsx`
**Acceptance**: Click-dispatch test passes; reduced-motion test passes (mock `window.matchMedia`); no `keydown` addEventListener call in component.

---

### T-009: [GREEN] StudioSearchPalette wrapper — correct props, telemetry POST on select
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04, AC-US2-05 | **Status**: [x] completed
**Test Plan (RED)**:
- Given `StudioSearchPalette.test.tsx` mocks `SearchPalette` and `fetch`
- When a skill result is selected
- Then `SearchPalette` received `searchUrl="/api/v1/studio/search"`; `selectHref` returns a `/studio/find/...` path; `onSelect` fires `fetch` to `/api/v1/studio/telemetry/search-select` with `{ skillName, q, ts }` payload; `X-Workspace-Fingerprint` header is set; `keepalive: true`; fetch failure does NOT throw or block navigation
**Test files**: `src/app/studio/components/__tests__/StudioSearchPalette.test.tsx`
**Implementation files**: `src/app/studio/components/StudioSearchPalette.tsx` (new)
**Acceptance**: All assertions green; telemetry failure path tested (fetch throws → no unhandled rejection).

---

### T-010: [GREEN] Wire FindNavButton + StudioSearchPalette into studio/layout.tsx
**User Story**: US-001, US-002 | **Satisfies ACs**: AC-US1-01, AC-US2-04 | **Status**: [x] completed
**Test Plan (RED)**:
- Given the studio layout test (`src/app/studio/__tests__/layout.test.tsx`) asserts both components are present
- When the test renders `studio/layout.tsx`
- Then `FindNavButton` renders before `SubmitNavButton` in `studio-nav-extras`; `StudioSearchPalette` renders as a sibling of `{children}`
**Test files**: `src/app/studio/__tests__/layout.test.tsx`
**Implementation files**: `src/app/studio/layout.tsx`
**Acceptance**: Layout test green; no duplicate SearchPalette rendered (T-001 gate already passed).

---

### T-011: [GREEN] Telemetry route — add search-select kind + extend install-copy with version field
**User Story**: US-002, US-003 | **Satisfies ACs**: AC-US2-05, AC-US3-06 | **Status**: [x] completed
**Test Plan (RED)**:
- Given the existing `route.test.ts` for `[kind]/route.ts`
- When new test cases POST to `search-select` kind with valid/invalid/missing-fingerprint/rate-limited payloads
- Then 200 OK for valid; 400 for invalid payload; 403 for workspace mismatch; 429 for rate-limited; existing `install-copy` with `version` field returns 200; old install-copy payload (no `version`) still returns 200
**Test files**: `src/app/api/v1/studio/telemetry/[kind]/__tests__/route.test.ts` (extend existing)
**Implementation files**: `src/app/api/v1/studio/telemetry/[kind]/route.ts`
**Acceptance**: All new cases green; all existing cases remain green; lockdown self-bypass tests untouched.

---

### T-012: [GREEN] Studio detail page — server component, data fetch, hero, metadata
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02 | **Status**: [x] completed
**Test Plan (RED)**:
- Given `page.test.tsx` mocks `getSkillByName` and `getSkillVersions`
- When the page renders with a valid skill slug
- Then hero renders with `TrustBadge`, `TierBadge`, `PublisherLink`, `RepoLink`, `RepoHealthBadge`; metadata title contains "Studio Preview"; `revalidate = 3600` is exported; 404 is returned when `getSkillByName` returns null
**Test files**: `src/app/studio/find/[owner]/[repo]/[skill]/__tests__/page.test.tsx`
**Implementation files**: `src/app/studio/find/[owner]/[repo]/[skill]/page.tsx` (new)
**Acceptance**: Hero and metadata assertions pass; 404 path passes; `TaintWarning` renders when `isTainted`; `BlockedSkillView` renders when `isBlocked` (imports shared component from T-003).

---

### T-013: [GREEN] VersionPicker — radiogroup ARIA, keyboard nav, controlled selection
**User Story**: US-003 | **Satisfies ACs**: AC-US3-03, AC-US3-09 | **Status**: [x] completed
**Test Plan (RED)**:
- Given `VersionPicker.test.tsx` renders with 5 mock versions
- When rendered
- Then `role="radiogroup"` container is present; each row is `role="radio"`; only selected row has `tabIndex={0}`; ↑/↓ arrow keys move focus + selection; Enter activates the focused row; `onSelect` fires with the version string
**Test files**: `src/app/studio/find/[owner]/[repo]/[skill]/__tests__/VersionPicker.test.tsx`
**Implementation files**: `src/app/studio/find/[owner]/[repo]/[skill]/VersionPicker.tsx` (new)
**Acceptance**: All ARIA, keyboard, and callback assertions pass; "Selected" indicator rendered on active row (icon + text, not color-only per WCAG); reduced-motion: no transition styles applied.

---

### T-014: [GREEN] InstallPanel — latest vs versioned install command derivation, sanitize
**User Story**: US-003 | **Satisfies ACs**: AC-US3-04 | **Status**: [x] completed
**Test Plan (RED)**:
- Given `InstallPanel.test.tsx` renders with `skillName="anton/vskill/demo"`, `defaultVersion="1.2.0"`, 3 mock versions
- When latest version (1.2.0) is selected
- Then `TerminalBlock` shows `vskill install anton/vskill/demo` (no @version); when older version selected via `VersionPicker`, shows `vskill install anton/vskill/demo@1.1.0`; sanitize regex `/^[a-zA-Z0-9._@/-]+$/` blocks a skillName containing `$` — copy button hidden
**Test files**: `src/app/studio/find/[owner]/[repo]/[skill]/__tests__/InstallPanel.test.tsx`
**Implementation files**: `src/app/studio/find/[owner]/[repo]/[skill]/InstallPanel.tsx` (new)
**Acceptance**: Command derivation tests pass; regex sanitization test passes; `VersionPicker` renders above `TerminalBlock` in DOM order.

---

### T-015: [GREEN] InstallPanel — clipboard copy + toast (success + fallback paths)
**User Story**: US-003 | **Satisfies ACs**: AC-US3-05 | **Status**: [x] completed
**Test Plan (RED)**:
- Given `InstallPanel.test.tsx` (extend T-014)
- When Copy button is clicked and `navigator.clipboard.writeText` resolves
- Then toast appears with message `Run \`vskill install ...\` in your terminal`, `role="status"`, `aria-live="polite"`, auto-dismissed after 3.5 s; when `navigator.clipboard` is undefined, fallback path (hidden textarea + `execCommand`) is used and toast still appears
**Test files**: `src/app/studio/find/[owner]/[repo]/[skill]/__tests__/InstallPanel.test.tsx` (extend)
**Implementation files**: `src/app/studio/find/[owner]/[repo]/[skill]/InstallPanel.tsx`
**Acceptance**: Both clipboard paths tested; toast auto-dismiss tested with fake timers; copy button has `aria-label="Copy install command to clipboard"`.

---

### T-016: [GREEN] InstallPanel — telemetry POST on copy, version field omitted for latest
**User Story**: US-003 | **Satisfies ACs**: AC-US3-06 | **Status**: [x] completed
**Test Plan (RED)**:
- Given `InstallPanel.test.tsx` (extend) mocks `fetch`
- When Copy is clicked with latest version selected
- Then `fetch` called to `/api/v1/studio/telemetry/install-copy` with body `{ skillName, q: "", ts }` — `version` field is ABSENT; when non-latest version is selected and Copy clicked, body includes `version: "1.1.0"`; `X-Workspace-Fingerprint` header is set; `keepalive: true`; fetch failure does NOT block toast or navigation
**Test files**: `src/app/studio/find/[owner]/[repo]/[skill]/__tests__/InstallPanel.test.tsx` (extend)
**Implementation files**: `src/app/studio/find/[owner]/[repo]/[skill]/InstallPanel.tsx`
**Acceptance**: All telemetry shape assertions pass; failure path tested (no unhandled rejection).

---

### T-017: [GREEN] InstallPanel — blocked path replaces install panel
**User Story**: US-003 | **Satisfies ACs**: AC-US3-07 | **Status**: [x] completed
**Test Plan (RED)**:
- Given `InstallPanel.test.tsx` (extend) rendered with `isBlocked={true}`
- When component renders
- Then `BlockedSkillView` is rendered; no `VersionPicker`, no `TerminalBlock`, no Copy button is present in the DOM
**Test files**: `src/app/studio/find/[owner]/[repo]/[skill]/__tests__/InstallPanel.test.tsx` (extend)
**Implementation files**: `src/app/studio/find/[owner]/[repo]/[skill]/InstallPanel.tsx`
**Acceptance**: Blocked assertions pass; `BlockedSkillView` imported from `@/app/components/BlockedSkillView` (T-003 output).

---

### T-018: [GREEN] Detail page — back link and submit-find footer link
**User Story**: US-003, US-005 | **Satisfies ACs**: AC-US3-08, AC-US5-02 | **Status**: [x] completed
**Test Plan (RED)**:
- Given `page.test.tsx` (extend T-012)
- When detail page renders with `?from=vskill` query param
- Then "← Back to results" link href is `/studio/find?q=vskill`; when no `?from` param, href is `/studio/find`; "Don't see what you need? Submit your skill →" link is present in install panel footer, constructed via `useSubmitDeepLink` hook
**Test files**: `src/app/studio/find/[owner]/[repo]/[skill]/__tests__/page.test.tsx` (extend), `src/app/studio/find/[owner]/[repo]/[skill]/__tests__/InstallPanel.test.tsx` (extend)
**Implementation files**: `src/app/studio/find/[owner]/[repo]/[skill]/page.tsx`, `src/app/studio/find/[owner]/[repo]/[skill]/InstallPanel.tsx`
**Acceptance**: Back-link href tests pass for both cases; submit-find link uses existing `useSubmitDeepLink` hook unchanged.

---

### T-019: [GREEN] Detail page — versions section (last 5, graceful missing fields, "see all" link)
**User Story**: US-003 | **Satisfies ACs**: AC-US3-03 | **Status**: [x] completed
**Test Plan (RED)**:
- Given `page.test.tsx` (extend) with 7 mock versions from `getSkillVersions`
- When page renders
- Then only 5 versions are shown (newest first); a "see all" link points to `/skills/{owner}/{repo}/{skill}/versions`; each row shows `v{version} · {date} · {author}` format; missing `author` or `publishedAt` renders `—` (graceful field handling)
**Test files**: `src/app/studio/find/[owner]/[repo]/[skill]/__tests__/page.test.tsx` (extend)
**Implementation files**: `src/app/studio/find/[owner]/[repo]/[skill]/page.tsx`
**Acceptance**: Version slice (5 of 7) test passes; graceful missing-field test passes; "see all" link present with correct href.

---

### T-020: [GREEN] FindClient — wire result card body click to navigate to detail route
**User Story**: US-002 | **Satisfies ACs**: AC-US2-03 | **Status**: [x] completed
**Test Plan (RED)**:
- Given `FindClient.test.tsx` (extend existing) renders a result card
- When the card body is clicked (not the Install button)
- Then navigation to `/studio/find/{owner}/{repo}/{skill}` occurs; clicking the Install button still triggers copy (no regression on existing behavior)
**Test files**: `src/app/studio/find/__tests__/FindClient.test.tsx` (extend existing)
**Implementation files**: `src/app/studio/find/FindClient.tsx`
**Acceptance**: Card body click → navigate test passes; existing Install button tests still pass (R-08 mitigation verified).

---

### T-021: [GREEN] Studio home CTA card — renders above feature grid, dispatches openSearch
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02 | **Status**: [x] completed
**Test Plan (RED)**:
- Given `src/app/studio/__tests__/page.test.tsx` (extend existing)
- When studio home page renders
- Then "Find verified skills" CTA card is present above the 4-card feature grid; has title "Find verified skills", copy "Search the registry. Trust signals inline. Install in one click.", CTA button "Search skills (⌘K)"; clicking CTA dispatches `openSearch` event; card uses `--accent-cyan` (or equivalent distinct accent) so it does not collide with existing feature cards
**Test files**: `src/app/studio/__tests__/page.test.tsx` (extend existing)
**Implementation files**: `src/app/studio/page.tsx`
**Acceptance**: All render assertions pass; click-dispatch assertion passes.

---

### T-022: [GREEN] Studio home CTA card — mobile stacking, no CLS
**User Story**: US-004 | **Satisfies ACs**: AC-US4-03 | **Status**: [x] completed
**Test Plan (RED)**:
- Given `page.test.tsx` (extend) checks DOM order and that the card has no client-only layout side-effects
- When rendered
- Then CTA card is positioned above hero CopyButton block via flex order; no `useEffect` layout mutations in card component (card is SSR-safe); CTA button is the only interactive element (thin `"use client"` island if needed)
**Test files**: `src/app/studio/__tests__/page.test.tsx` (extend)
**Implementation files**: `src/app/studio/page.tsx`
**Acceptance**: DOM order test passes; no CLS-inducing client-only layout changes.

---

### T-023: [GREEN] SubmitFindBanner regression — still renders on /studio/find empty state
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01 | **Status**: [x] completed
**Test Plan (RED)**:
- Given the existing `FindClient.test.tsx` (extend)
- When `/studio/find` renders with empty results
- Then `SubmitFindBanner` renders below empty-state; placement, copy, and deep-link behavior are unchanged from 0718
**Test files**: `src/app/studio/find/__tests__/FindClient.test.tsx` (extend existing)
**Implementation files**: No implementation change expected — regression guard; fix `FindClient.tsx` if test fails after T-020 edits
**Acceptance**: Existing banner tests pass; banner behavior unchanged after T-020 edits to `FindClient.tsx`.

---

### T-024: [GREEN] CSS var audit — no hard-coded colors in new components
**User Story**: US-001, US-002, US-003, US-004 | **Satisfies ACs**: AC-US1-01, AC-US2-01, AC-US3-02, AC-US4-02 | **Status**: [x] completed
**Test Plan (RED)**:
- Given a grep scan of all new `.tsx` files introduced in this increment
- When scanning for hard-coded color values (`#[0-9a-fA-F]{3,6}`, `rgb(`, `hsl(`) outside of `TerminalBlock`
- Then zero violations found; all colors reference `var(--...)` CSS tokens
**Test files**: `scripts/check-no-hardcoded-colors.sh` (or inline vitest snapshot test asserting grep returns 0 results)
**Implementation files**: All new component files — fix any violations found during this task
**Acceptance**: Grep returns zero violations outside `TerminalBlock`; confirmed by manual dark/light visual smoke in E2E T-029.

---

### T-025: [GREEN] E2E — golden path (mouse): Studio home → palette → detail → copy
**User Story**: US-001, US-002, US-003, US-004, US-005 | **Satisfies ACs**: AC-US1-02, AC-US2-01, AC-US2-03, AC-US3-04, AC-US3-05, AC-US4-01 | **Status**: [x] completed
**Test Plan (RED)**:
- Given `tests/e2e/studio-find-slick.spec.ts` (new) is written first against TODO selectors — test fails because components don't exist yet (RED)
- When all prior tasks complete and test runs
- Then: visit `/studio` → see Find CTA card → click "Search skills (⌘K)" → palette opens → type "vskill" → results appear → click first row → land on `/studio/find/.../...` → see version list → click older version → install command updates to include `@<version>` → click Copy → toast appears → clipboard contains correct command
**Test files**: `tests/e2e/studio-find-slick.spec.ts` (new)
**Implementation files**: None (consumes all prior tasks)
**Acceptance**: Scenario passes on Playwright chromium 1280×720.

---

### T-026: [GREEN] E2E — keyboard-only path: ⌘K → navigate → version → copy
**User Story**: US-001, US-002, US-003 | **Satisfies ACs**: AC-US1-03, AC-US2-01, AC-US3-09 | **Status**: [x] completed
**Test Plan (RED)**:
- Given `tests/e2e/studio-find-slick.spec.ts` (extend T-025)
- When keyboard scenario runs
- Then: `/studio` → press ⌘K → palette opens with focus on input → type "vskill" → ↓ → Enter → land on detail → Tab → first version radio focused → ↓ to second → Enter selects second version → Tab → copy button focused → Enter → toast appears; entire flow completable without mouse
**Test files**: `tests/e2e/studio-find-slick.spec.ts` (extend)
**Implementation files**: None
**Acceptance**: Keyboard scenario passes; focus management at each step verified.

---

### T-027: [GREEN] E2E — back navigation and blocked skill path
**User Story**: US-003, US-005 | **Satisfies ACs**: AC-US3-07, AC-US3-08, AC-US5-01 | **Status**: [x] completed
**Test Plan (RED)**:
- Given `tests/e2e/studio-find-slick.spec.ts` (extend)
- When back navigation scenario: select skill from palette with query "vskill" → land on detail → click "← Back to results" → assert URL is `/studio/find?q=vskill`
- When blocked skill scenario: navigate directly to `/studio/find/<blocked-owner>/<blocked-repo>/<blocked-skill>` → assert BLOCKED panel renders, no Copy button present
**Test files**: `tests/e2e/studio-find-slick.spec.ts` (extend)
**Implementation files**: None
**Acceptance**: Back-nav scenario passes; blocked-skill scenario passes.

---

### T-028: [GREEN] E2E — telemetry assertions (search-select + install-copy payload shapes)
**User Story**: US-002, US-003 | **Satisfies ACs**: AC-US2-05, AC-US3-06 | **Status**: [x] completed
**Test Plan (RED)**:
- Given `tests/e2e/studio-find-slick.spec.ts` (extend) with Playwright `page.route()` interception
- When skill selected from palette → intercept POST to `/api/v1/studio/telemetry/search-select` → assert body has `{ skillName, q, ts }` and `X-Workspace-Fingerprint` header is non-empty
- When Copy clicked for non-latest version → intercept POST to `/api/v1/studio/telemetry/install-copy` → assert body has `{ skillName, version: "1.1.0", q: "", ts }` and header present; for latest version → `version` field absent from payload
**Test files**: `tests/e2e/studio-find-slick.spec.ts` (extend)
**Implementation files**: None
**Acceptance**: All payload shape and header assertions pass.

---

### T-029: [GREEN] E2E — dark/light mode + mobile viewport smoke
**User Story**: US-001, US-002, US-003, US-004 | **Satisfies ACs**: AC-US1-05, AC-US4-03 | **Status**: [x] completed
**Test Plan (RED)**:
- Given `tests/e2e/studio-find-slick.spec.ts` (extend) with multi-project Playwright config
- When running in dark mode at 1280×720, light mode at 1280×720, and mobile (375×812)
- Then palette opens without layout breaks in all viewports/themes; CTA card stacks correctly on mobile; no console errors about missing CSS vars; no layout reflow (CLS) on mobile
**Test files**: `tests/e2e/studio-find-slick.spec.ts` (extend — `--project=chromium` multi-config)
**Implementation files**: None
**Acceptance**: All 3 smoke scenarios pass; zero console errors.

---

## Test Files Index

| Test File | New/Extend | AC Coverage |
|---|---|---|
| `src/app/__tests__/layout.collision.test.tsx` | NEW | AC-US2-04 |
| `src/app/studio/lib/__tests__/workspace-fingerprint.test.ts` | NEW | AC-US2-05, AC-US3-06 |
| `src/app/components/__tests__/BlockedSkillView.test.tsx` | NEW | AC-US3-07 |
| `src/app/components/__tests__/SearchPalette.props.test.tsx` | NEW | AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-05 |
| `src/app/components/__tests__/SearchPalette.test.tsx` | EXISTING (must stay green) | Regression gate — all 59 cases |
| `src/app/studio/components/__tests__/FindNavButton.test.tsx` | NEW | AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05 |
| `src/app/studio/components/__tests__/StudioSearchPalette.test.tsx` | NEW | AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04, AC-US2-05, AC-US2-06 |
| `src/app/studio/__tests__/layout.test.tsx` | NEW | AC-US1-01, AC-US2-04 |
| `src/app/api/v1/studio/telemetry/[kind]/__tests__/route.test.ts` | EXTEND | AC-US2-05, AC-US3-06 |
| `src/app/studio/find/[owner]/[repo]/[skill]/__tests__/page.test.tsx` | NEW | AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-07, AC-US3-08 |
| `src/app/studio/find/[owner]/[repo]/[skill]/__tests__/VersionPicker.test.tsx` | NEW | AC-US3-03, AC-US3-09 |
| `src/app/studio/find/[owner]/[repo]/[skill]/__tests__/InstallPanel.test.tsx` | NEW | AC-US3-04, AC-US3-05, AC-US3-06, AC-US3-07, AC-US3-08 |
| `src/app/studio/find/__tests__/FindClient.test.tsx` | EXTEND | AC-US2-03, AC-US5-01 |
| `src/app/studio/__tests__/page.test.tsx` | EXTEND | AC-US4-01, AC-US4-02, AC-US4-03 |
| `tests/e2e/studio-find-slick.spec.ts` | NEW | AC-US1-02, AC-US1-03, AC-US2-01, AC-US2-03, AC-US2-05, AC-US3-04, AC-US3-05, AC-US3-06, AC-US3-07, AC-US3-08, AC-US3-09, AC-US4-01, AC-US5-01 |

---

## Coverage Targets

| Scope | Target | Notes |
|---|---|---|
| Unit — new files | ≥95% line + branch | All new `.tsx` / `.ts` files in this increment |
| Integration | ≥90% | Telemetry route, server-component page tests |
| E2E — critical-path ACs | 100% | All 5 scenarios in `studio-find-slick.spec.ts` |
| `SearchPalette.tsx` net coverage | Must not drop | Existing 59-case suite is the primary regression gate |

---

## Execution Order Notes

Tasks must be executed in dependency order. Prereqs (T-001 through T-003) are independent and can run in parallel.

```
T-001 (layout collision gate)
  └─→ T-010 (wire layout — needs gate result)

T-002 (workspace-fingerprint helper)
  └─→ T-009 (StudioSearchPalette uses helper)
  └─→ T-016 (InstallPanel telemetry uses helper)

T-003 (BlockedSkillView lift)
  └─→ T-012 (detail page imports BlockedSkillView)
  └─→ T-017 (InstallPanel blocked path imports BlockedSkillView)

T-004 → T-005 → T-006  (SearchPalette refactor — sequential, each builds on prior)
  └─→ T-009 (StudioSearchPalette wraps refactored SearchPalette)

T-007 → T-008  (FindNavButton — render then behavior)
  └─→ T-010 (layout mounts FindNavButton)

T-009 (StudioSearchPalette)
  └─→ T-010 (layout mounts StudioSearchPalette)

T-010 (layout integration)
  └─→ T-025, T-026, T-029 (E2E exercises full layout)

T-011 (telemetry route extension)
  └─→ T-016 (InstallPanel posts to extended route)
  └─→ T-028 (E2E asserts telemetry shapes)

T-012 (detail page skeleton)
  └─→ T-013 (VersionPicker — page composes it)
  └─→ T-014 (InstallPanel — page composes it)
  └─→ T-018 (back link + footer on page)
  └─→ T-019 (versions section on page)

T-013 → T-014 → T-015 → T-016 → T-017 → T-018 → T-019
  (InstallPanel refinements — sequential, each adds behavior)

T-020 (FindClient card click)  — independent after T-012 route exists

T-021 → T-022  (CTA card — sequential)

T-023 (banner regression) — independent, run after T-020

T-024 (CSS audit) — run after all component tasks complete

T-025 → T-026 → T-027 → T-028 → T-029  (E2E — sequential within spec file)
```

**Parallel opportunities**:
- T-001 + T-002 + T-003 — run in parallel (independent prereqs).
- T-004/T-005/T-006 (SearchPalette refactor) and T-007/T-008 (FindNavButton) and T-011 (telemetry route) — can all overlap once prereqs complete.
- T-020, T-021/T-022, T-023 — can run in parallel once T-010 and T-012 are done.
- T-024 — runs last among unit tasks, before E2E phase.
