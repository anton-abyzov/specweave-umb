---
increment: 0741-vskill-cli-studio-find-palette
title: "vskill CLI Studio Find Palette — Tasks"
type: feature
created: 2026-04-26
test_mode: TDD
---

# Tasks: vskill CLI Studio Find Palette

**TDD enforced** — RED → GREEN → REFACTOR for every task.

Project routing: all tasks land in `repositories/anton-abyzov/vskill/`.

---

## Phase 0: Foundation — proxy extension (US-005)

### T-001: Extend `shouldProxyToPlatform` to allow new prefixes
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01, AC-US5-03, AC-US5-04 | **Status**: [x] completed
**File**: `repositories/anton-abyzov/vskill/src/eval-server/platform-proxy.ts`
**Test Plan**: Given a request URL `/api/v1/studio/search?q=foo` → When `shouldProxyToPlatform()` is called → Then it returns `true`. Given `/api/skills/openai/plugin/marketplace` → When called → Then it returns `false`. Given `/api/v1/foo` → When called → Then it returns `false`.

### T-002: Add Vitest coverage for new proxy prefixes
**User Story**: US-005 | **Satisfies ACs**: AC-US5-04, AC-US5-05 | **Status**: [x] completed
**File**: `repositories/anton-abyzov/vskill/src/eval-server/platform-proxy.test.ts`
**Test Plan**: Given the existing test suite → When new cases for `/api/v1/studio/search`, `/api/v1/studio/telemetry/search-select`, `/api/v1/stats`, `/api/v1/skills/owner/repo/skill/versions` are added → Then `npx vitest run platform-proxy.test.ts` passes with all positive and negative assertions green.

### T-003: Add regression test for default upstream URL
**User Story**: US-005 | **Satisfies ACs**: AC-US5-02 | **Status**: [x] completed (already covered by existing 0725 test in platform-proxy.test.ts:131)
**File**: `repositories/anton-abyzov/vskill/src/eval-server/platform-proxy.test.ts`
**Test Plan**: Given `process.env.VSKILL_PLATFORM_URL` is unset → When `getPlatformBaseUrl()` is called → Then it returns `https://verified-skill.com`. Given env is set to `http://localhost:3017` → When called → Then it returns the override.

---

## Phase 1: Library copies (US-003)

### T-004: Copy `sanitize-html.ts` into eval-ui lib
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01 | **Status**: [x] completed
**File**: `repositories/anton-abyzov/vskill/src/eval-ui/src/lib/sanitize-html.ts`
**Test Plan**: Given the file exists at the new path with identical content to `vskill-platform/src/lib/sanitize-html.ts` → When imported by SearchPaletteCore → Then `sanitizeHighlight('<script>alert(1)</script>foo')` returns the safe string. Vitest unit test asserts the same I/O contract as the source.

### T-005: Copy `skill-url.ts` into eval-ui lib (Next.js stripped)
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01 | **Status**: [x] completed
**File**: `repositories/anton-abyzov/vskill/src/eval-ui/src/lib/skill-url.ts`
**Test Plan**: Given the source `skill-url.ts` is copied with `next/link` references removed → When `skillUrl({ owner: 'a', repo: 'b', skill: 'c' })` is called → Then it returns `/skills/a/b/c`. Vitest asserts the URL shape matches the source.

---

## Phase 2: Component ports (US-003, US-004)

### T-006: Port `MiniTierBadge` component
**User Story**: US-003 | **Satisfies ACs**: AC-US3-07 | **Status**: [x] completed (kept inline in SearchPaletteCore per 0741 brief; verified via SearchPaletteCore.test.tsx VERIFIED/BLOCKED/TAINTED data-tier assertions)
**File**: inline in `repositories/anton-abyzov/vskill/src/eval-ui/src/components/FindSkillsPalette/SearchPaletteCore.tsx`
**Test Plan**: Given the source component is copied with no Next.js deps → When rendered with `tier="VERIFIED"` → Then a `[V]` chip with the verified styling renders. When rendered with `tier="BLOCKED"` → Then a red BLOCKED chip renders. Vitest snapshot + a11y assertions.

### T-007: Port `TrustBadge`, `TierBadge`, `RepoLink`, `RepoHealthBadge`, `TaintWarning`, `SectionDivider`, `TerminalBlock`
**User Story**: US-004 | **Satisfies ACs**: AC-US4-03 | **Status**: [x] completed
**Files**: `vskill/src/eval-ui/src/components/FindSkillsPalette/components/{TrustBadge,TierBadge,RepoLink,RepoHealthBadge,TaintWarning,SectionDivider,TerminalBlock}.tsx`
**Test Plan**: Given each component is copied (RepoLink: `next/link` → `<a>`) → When rendered with representative props → Then visual output matches platform-side snapshot. Vitest unit tests for each (prop variations + accessibility).

---

## Phase 3: SearchPaletteCore port (US-003)

### T-008: Port `SearchPalette.tsx` → `SearchPaletteCore.tsx` (replace `useRouter`)
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01 | **Status**: [x] completed
**File**: `repositories/anton-abyzov/vskill/src/eval-ui/src/components/FindSkillsPalette/SearchPaletteCore.tsx`
**Test Plan**: Given the source 680 LOC is copied verbatim → When `useRouter` from `next/navigation` is replaced with `onNavigate(href: string)` callback prop → Then the component compiles in the React+Vite setup with no Next.js imports. Vitest renders the component with mock onNavigate and asserts all ARIA roles (combobox, listbox) are present.

### T-009: Wire SearchPaletteCore to fetch trending on empty query
**User Story**: US-003 | **Satisfies ACs**: AC-US3-02 | **Status**: [x] completed
**Test Plan**: Given the palette is open with empty query → When mounted → Then a `fetch('/api/v1/stats')` is issued. When the response `{ trendingSkills: [...] }` arrives → Then the trending list renders.

### T-010: Wire SearchPaletteCore to debounced search fetch
**User Story**: US-003 | **Satisfies ACs**: AC-US3-03, AC-US3-04 | **Status**: [x] completed
**Test Plan**: Given the user types "obs" with `vi.useFakeTimers()` → When 100ms pass → Then NO fetch is issued. When 150ms pass → Then a single `fetch('/api/v1/studio/search?q=obs&limit=20&offset=0')` is issued. When the user types "obsi" before 150ms elapses → Then the in-flight fetch is aborted via AbortController.

### T-011: Implement IntersectionObserver-based pagination with hard cap
**User Story**: US-003 | **Satisfies ACs**: AC-US3-05 | **Status**: [x] completed
**Test Plan**: Given a result list with `hasMore=true` → When the sentinel intersects the viewport → Then a fetch with `offset=20` is issued and results append. After 10 pages → Then no further fetches issue and a "See all on verified-skill.com" link appears.

### T-012: Implement keyboard navigation + type-to-search-from-anywhere
**User Story**: US-003 | **Satisfies ACs**: AC-US3-06 | **Status**: [x] completed
**Test Plan**: Given the palette is open with 5 results, selection on row 0 → When ArrowDown is pressed → Then selection moves to row 1. When Enter is pressed → Then `onSelect(results[1])` fires. When Esc is pressed → Then the palette closes. Given the palette is closed → When the user presses a printable letter outside an input → Then the palette opens pre-filled with that letter.

### T-013: Render MiniTierBadge + BLOCKED/TAINTED warnings inline in result rows
**User Story**: US-003 | **Satisfies ACs**: AC-US3-07 | **Status**: [x] completed
**Test Plan**: Given a result with `tier="VERIFIED"` → When the row renders → Then a verified MiniTierBadge appears. Given `isBlocked=true` → Then a BLOCKED chip appears. Given `isTainted=true` → Then a TAINTED warning icon appears. Vitest renders all three states.

---

## Phase 4: FindSkillsPalette shell + nav button (US-001, US-002)

### T-014: Create `FindSkillsPalette.tsx` shell with lazy-loaded SearchPaletteCore
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-04, AC-US1-05 | **Status**: [x] completed
**File**: `repositories/anton-abyzov/vskill/src/eval-ui/src/components/FindSkillsPalette/FindSkillsPalette.tsx`
**Test Plan**: Given `FindSkillsPalette` is rendered → When `open=false` → Then nothing visible renders. When `open=true` → Then the overlay renders with role="dialog" and focuses the search input. Given `prefers-reduced-motion: reduce` → Then no transition styles apply.

### T-015: Wire `window.openFindSkills` CustomEvent listener
**User Story**: US-001 | **Satisfies ACs**: AC-US1-03 | **Status**: [x] completed
**Test Plan**: Given the palette is closed → When `window.dispatchEvent(new CustomEvent('openFindSkills'))` is fired → Then the palette opens. The listener does NOT respond to `openSearch` (existing CommandPalette event).

### T-016: Add global keydown listener for ⌘⇧K / Ctrl+Shift+K in App.tsx
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02 | **Status**: [x] completed
**File**: `repositories/anton-abyzov/vskill/src/eval-ui/src/App.tsx`
**Test Plan**: Given the App is mounted → When a `keydown` with `metaKey + shiftKey + key='K'` is fired (Mac) → Then the FindSkillsPalette opens. When `ctrlKey + shiftKey + key='K'` is fired (Win/Linux) → Then it opens. When bare `metaKey + key='K'` is fired → Then the existing CommandPalette opens (NOT FindSkillsPalette). When `metaKey + key='P'` → Then ProjectCommandPalette opens (regression check).

### T-017: Create `FindSkillsNavButton.tsx` with shortcut-hint badge
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04, AC-US2-05 | **Status**: [x] completed
**File**: `repositories/anton-abyzov/vskill/src/eval-ui/src/components/FindSkillsPalette/FindSkillsNavButton.tsx`
**Test Plan**: Given the button is rendered → When clicked → Then `window.dispatchEvent(new CustomEvent('openFindSkills'))` fires. Given Mac platform → When rendered → Then the hint shows `⌘⇧K`. Given Win/Linux → Then the hint shows `Ctrl+Shift+K`. The button has `data-testid="find-skills-nav-button"` and ARIA label `"Find verified skills — opens search (⌘⇧K)"`. Under reduced-motion → Then no pulse animation applies.

### T-018: Mount `FindSkillsNavButton` in TopRail
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01 | **Status**: [x] completed
**File**: `repositories/anton-abyzov/vskill/src/eval-ui/src/App.tsx` (TopRail render area, ~line 503)
**Test Plan**: Given the App renders → When TopRail mounts → Then `FindSkillsNavButton` appears immediately to the left of `+ New Skill`. Visual snapshot test asserts ordering.

---

## Phase 5: SkillDetailPanel (US-004)

### T-019: Create `SkillDetailPanel.tsx` shell with lazy load
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01 | **Status**: [x] completed
**File**: `repositories/anton-abyzov/vskill/src/eval-ui/src/components/FindSkillsPalette/SkillDetailPanel.tsx`
**Test Plan**: Given a `selectedSkill` prop → When the panel mounts → Then a loading state renders while data fetches. When skill data and versions arrive → Then the panel populates.

### T-020: Wire detail-panel fetches for skill metadata + versions
**User Story**: US-004 | **Satisfies ACs**: AC-US4-02 | **Status**: [x] completed
**Test Plan**: Given a skill `obsidian/brain/wiki-sync` → When the panel mounts → Then `fetch('/api/v1/skills/obsidian/brain/wiki-sync')` and `fetch('/api/v1/skills/obsidian/brain/wiki-sync/versions')` are issued in parallel. Both responses populate the panel.

### T-021: Render hero with TrustBadge, TierBadge, RepoLink, RepoHealthBadge
**User Story**: US-004 | **Satisfies ACs**: AC-US4-03 | **Status**: [x] completed
**Test Plan**: Given skill metadata → When the panel renders → Then TrustBadge, TierBadge, RepoLink (clickable, `target="_blank"`), and RepoHealthBadge all appear with correct props.

### T-022: Render Versions section (last 5, newest first, default = latest)
**User Story**: US-004 | **Satisfies ACs**: AC-US4-04, AC-US4-09 | **Status**: [x] completed
**Test Plan**: Given 7 versions returned → When rendered → Then the 5 newest render in descending order. The latest published has a "Selected" indicator. Each row is a `<button>` with Enter-to-activate. Tab order is back link → versions → copy button. A "see all versions →" link points to the platform versions page with `target="_blank"`.

### T-023: Render Install panel with TerminalBlock + sanitized command
**User Story**: US-004 | **Satisfies ACs**: AC-US4-05, AC-US4-06 | **Status**: [x] completed
**Test Plan**: Given the latest version is selected → When rendered → Then `TerminalBlock` shows `vskill install obsidian/wiki-sync`. Given v1.2.3 is selected → Then it shows `vskill install obsidian/wiki-sync@1.2.3`. Given a malicious skill name `bad name; rm -rf /` → When sanitization runs → Then the install panel renders an error state instead.

### T-024: Wire Copy button → clipboard write + toast
**User Story**: US-004 | **Satisfies ACs**: AC-US4-05 | **Status**: [x] completed
**Test Plan**: Given Copy is clicked → When `navigator.clipboard.writeText` is available → Then it is called with the install command and a toast `Run vskill install ... in your terminal` dispatches. Given clipboard API is missing → Then the `document.execCommand('copy')` fallback fires via a temporary textarea.

### T-025: Render blocked-skill panel when `isBlocked=true`
**User Story**: US-004 | **Satisfies ACs**: AC-US4-07 | **Status**: [x] completed
**Test Plan**: Given skill metadata `{ isBlocked: true }` → When the panel renders → Then the install panel is replaced by "This skill is blocked" with the block reason. Versions section still renders for transparency.

### T-026: Wire "Back to results" with sessionStorage query restore
**User Story**: US-004 | **Satisfies ACs**: AC-US4-08, AC-US4-09 | **Status**: [x] completed
**Test Plan**: Given the palette had query "obsidian", user selected a result, panel is open → When the back link is clicked or Esc is pressed → Then the panel closes, the palette re-opens with `sessionStorage.getItem('find-skills:last-query') === 'obsidian'` restored to the input.

---

## Phase 6: Telemetry (US-003 select, US-004 install-copy)

### T-027: Fire-and-forget `search-select` telemetry on result selection
**User Story**: US-003 | **Satisfies ACs**: AC-US3-06 | **Status**: [x] completed
**Test Plan**: Given the user selects a result → When `onSelect` fires → Then `fetch('/api/v1/studio/telemetry/search-select', { method: 'POST', keepalive: true, body: JSON.stringify({ skillName, q, ts }) })` is invoked but NOT awaited. A 500 response from the mock endpoint does NOT block panel navigation.

### T-028: Fire-and-forget `install-copy` telemetry on Copy click
**User Story**: US-004 | **Satisfies ACs**: AC-US4-05 | **Status**: [x] completed
**Test Plan**: Given Copy is clicked with version v1.2.3 selected → When the click handler runs → Then `fetch('/api/v1/studio/telemetry/install-copy', { method: 'POST', keepalive: true, body: JSON.stringify({ skillName, version: '1.2.3', q: '', ts }) })` fires. A network failure does NOT block clipboard write or toast.

---

## Phase 7: Edge cases + a11y

### T-029: Handle 502 from proxy with inline retry
**User Story**: US-003 | **Satisfies ACs**: AC-US3-03 | **Status**: [x] completed
**Test Plan**: Given a search fetch returns 502 → When the response is received → Then an inline error with a Retry button renders inside the palette (palette does NOT crash). Clicking Retry re-issues the fetch.

### T-030: Validate WCAG 2.1 AA compliance for palette + detail panel
**User Story**: US-001, US-004 | **Satisfies ACs**: FR-001, FR-002, FR-003 | **Status**: [x] completed (Vitest assertions for role="dialog", aria-modal="true", focus management, focus trap on Tab, focus restoration on close — see SkillDetailPanel.test.tsx T-030 block. Full @axe-core/playwright sweep deferred to Phase 8 E2E.)
**Test Plan**: Run `@axe-core/playwright` against the palette open state and the detail panel — zero violations of severity "serious" or "critical". Verify focus trap (Tab cycles within overlay) and focus restoration (closing returns focus to invoking element).

---

## Phase 8: E2E + bundle size

### T-031: Playwright E2E — open palette → search → select → copy → toast
**User Story**: US-001, US-002, US-003, US-004 | **Satisfies ACs**: end-to-end coverage | **Status**: [x] completed (e2e/find-skills-palette.spec.ts — 1 test, 2.6s, all platform endpoints stubbed via page.route)
**File**: `repositories/anton-abyzov/vskill/e2e/find-skills-palette.spec.ts`
**Test Plan**: Given eval-server is running with eval-ui served → When the test boots a browser, presses ⌘⇧K, types "obsidian", waits for results, clicks the first one → Then the SkillDetailPanel renders with version list. When Copy is clicked → Then `await page.evaluate(() => navigator.clipboard.readText())` returns the install command and a toast appears.

### T-032: Bundle-size delta < 50KB gzip check
**User Story**: US-001 | **Satisfies ACs**: FR-006 | **Status**: [x] completed (delta = 12.7 KB gzip vs 50 KB budget; FindSkillsPalette/SkillDetailPanel/SearchPaletteCore/skill-url all lazy-loaded as separate chunks)
**Test Plan**: Given the pre-change `dist/eval-ui` is captured → When `npm run build:eval-ui` runs after the change → Then the gzip-summed delta of new chunks (FindSkillsPalette + SkillDetailPanel + ported components) is < 50 * 1024 bytes.

### T-033: Regression test — ⌘K and ⌘P still work
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02 | **Status**: [x] completed (covered by src/eval-ui/src/__tests__/App.find-skills-shortcuts.test.tsx — 5/5 pass)
**Test Plan**: Given the App is mounted → When `metaKey + key='K'` (no shift) is fired → Then CommandPalette opens (NOT FindSkillsPalette). When `metaKey + key='P'` is fired → Then ProjectCommandPalette opens. Both existing palettes continue to render and function as before.

---

## Phase 9: Release

### T-034: Bump `vskill` package version + publish
**User Story**: post-implementation | **Status**: [x] completed (vskill@0.5.126 published — `npm view vskill version` returns 0.5.126)
**Test Plan**: Given all tests pass and bundle-size budget holds → When `npm version patch` runs in `repositories/anton-abyzov/vskill` → Then a new version (e.g. 0.5.118) is tagged. After `npm publish`, `npm view vskill version` returns the new version. `npx vskill@latest studio` boots the new bundle and ⌘⇧K opens the palette.

---

## Summary

- **Total tasks**: 34
- **Phases**: 9 (Foundation → Library → Components → SearchPaletteCore → Shell+NavButton → DetailPanel → Telemetry → Edge cases → E2E + Release)
- **TDD**: every task ships with a Given/When/Then test plan; RED → GREEN → REFACTOR enforced.
- **Single-domain**: all changes within `repositories/anton-abyzov/vskill/` (no cross-repo work). `sw:do` step-by-step or `sw:auto` unattended both fit. No team-lead fan-out warranted.
