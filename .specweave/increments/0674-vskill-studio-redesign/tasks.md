---
increment: 0674-vskill-studio-redesign
title: vSkill Studio Redesign — Tasks
scope: Option B (Phases 1-4). Phase 5 (editor) deferred to 0675-skill-md-editor.
target_days: 9
status: active
---

# Tasks: vSkill Studio Redesign (Phases 1–4)

> **Scope = Option B (Phases 1-4). Phase 5 (editor) deferred to 0675-skill-md-editor.**
> Target codebase: `repositories/anton-abyzov/vskill/src/eval-ui/`
> Stack: Vite 6 + React 19 + Tailwind 4 + TypeScript 5.7 + Vitest 3 + Playwright

---

## Phase 1 — Theme Foundation

_Goal: both themes render correctly with warm-neutral tokens, FOUC prevented, serif/shimmer scope enforced, fonts loaded._

---

### T-001: Install font packages and configure Vite manual chunk
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01 | **Status**: [x] completed
**Phase**: 1 | **Estimated**: 1h | **Test Level**: unit
**Test Plan**:
  Given the package.json in `repositories/anton-abyzov/vskill/`
  When `npm install` runs
  Then `@fontsource-variable/source-serif-4`, `@fontsource-variable/inter-tight`, and `@fontsource-variable/jetbrains-mono` are resolvable imports; and `vite.config.ts` `manualChunks` routes them to a `fonts` chunk ≤ 70 KB gzipped (asserted via `vite build --reporter json`)
**Files**:
  - `repositories/anton-abyzov/vskill/package.json`
  - `repositories/anton-abyzov/vskill/src/eval-ui/vite.config.ts`
**Dependencies**: none
**Notes**: Use tilde-range `~4.2.1` for tailwindcss per ADR-0674-04. Three font imports land in `src/eval-ui/src/main.tsx` after this task.

---

### T-002: Rewrite globals.css with Tailwind 4 @theme token layers
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-06 | **Status**: [x] completed
**Phase**: 1 | **Estimated**: 3h | **Test Level**: unit
**Test Plan**:
  Given `globals.css` rewritten under `@theme` with the full light palette (--color-paper: #FBF8F3, --color-ink: #191919, all tokens from ADR-0674-01) and `[data-theme="dark"]` override with warm near-black values (#1A1814)
  When `@tailwindcss/vite` processes the file
  Then CSS custom properties `--color-paper`, `--color-surface`, `--color-ink`, `--color-ink-muted`, `--color-rule`, `--color-accent`, `--color-installed`, `--color-own`, `--color-focus` are defined in `:root` and overridden in `[data-theme="dark"]`; semantic Layer 2 tokens (`--bg-canvas`, `--text-primary`, `--border-default`, `--status-installed`, `--status-own`) resolve through to raw tokens; and no `@keyframes shimmer` or `.skeleton` class remains in the file
**Files**:
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/styles/globals.css`
**Dependencies**: T-001
**Notes**: Delete the existing `.skeleton` shimmer animation. Add `.placeholder` static class. Add `[data-contrast="more"]` overlay. Add reduced-motion global rule collapsing all durations to 0ms.

---

### T-003: Add FOUC-prevention inline script to index.html
**User Story**: US-002 | **Satisfies ACs**: AC-US2-04 | **Status**: [x] completed
**Phase**: 1 | **Estimated**: 0.5h | **Test Level**: e2e
**Test Plan**:
  Given `index.html` has the inline script that reads `localStorage.getItem("vskill-theme")` before React mounts
  When Playwright loads the page with `"vskill-theme"` set to `"dark"` in localStorage
  Then `document.documentElement.getAttribute("data-theme")` equals `"dark"` before the first React render frame (verified by intercepting the first paint via `page.evaluate`)
**Files**:
  - `repositories/anton-abyzov/vskill/src/eval-ui/index.html`
**Dependencies**: T-002
**Notes**: Also sets `data-contrast="more"` when `prefers-contrast: more` matches. Try/catch wraps the script for private-browsing localStorage restrictions.

---

### T-004: Implement ThemeProvider context and useTheme hook
**User Story**: US-002 | **Satisfies ACs**: AC-US2-03, AC-US2-04, AC-US2-05 | **Status**: [x] completed
**Phase**: 1 | **Estimated**: 2h | **Test Level**: unit
**Test Plan**:
  Given `ThemeProvider` wraps the component tree
  When `setTheme("dark")` is called
  Then `document.documentElement.dataset.theme` is set to `"dark"`, `localStorage.getItem("vskill-theme")` equals `"dark"`, and a subsequent `setTheme("auto")` with `prefers-color-scheme: dark` media query mocked to `true` resolves `resolvedTheme` to `"dark"`
**Files**:
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/theme/ThemeProvider.tsx`
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/theme/useTheme.ts`
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/__tests__/theme-provider.test.ts`
**Dependencies**: T-002, T-003
**Notes**: `auto` state listens via `matchMedia("(prefers-color-scheme: dark)").addEventListener("change", ...)`. Cross-tab sync via `window.addEventListener("storage", ...)`. No next-themes dependency — this is a Vite SPA.

---

### T-005: Import fonts in main.tsx and wrap app with ThemeProvider
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01 | **Status**: [x] completed
**Phase**: 1 | **Estimated**: 0.5h | **Test Level**: unit
**Test Plan**:
  Given `main.tsx` imports the three `@fontsource-variable/*` packages and wraps `<App>` with `<ThemeProvider>`
  When a Vitest component render occurs
  Then `useTheme()` does not throw and `document.fonts` (mocked) contains references to `Source Serif 4 Variable`, `Inter Tight Variable`, `JetBrains Mono Variable`
**Files**:
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/main.tsx`
**Dependencies**: T-001, T-004

---

### T-006: Write contrast verification tests (WCAG AA CI gate)
**User Story**: US-002 | **Satisfies ACs**: AC-US2-02 | **Status**: [x] completed
**Phase**: 1 | **Estimated**: 1.5h | **Test Level**: unit
**Test Plan**:
  Given `theme-contrast.test.ts` uses `wcag-contrast` to measure each semantic token pair
  When run against the light token values (#FBF8F3 paper, #191919 ink, #5A5651 ink-muted, etc.) and dark token values (#1A1814, #F2ECE1, #A59D8F, etc.)
  Then all body-text pairs ≥ 4.5:1, `--ink` on `--paper` ≥ 7:1 (both themes), `--ink-muted` on `--paper` ≥ 4.5:1, `--installed` ≥ 3:1, `--own` ≥ 3:1, `--focus` ≥ 3:1; test file exits 0 on correct tokens and exits non-zero when a token is manually set below threshold
**Files**:
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/__tests__/theme-contrast.test.ts`
**Dependencies**: T-002
**Notes**: Install `wcag-contrast` as devDependency. This test runs in CI and blocks merge on failure.

---

### T-007: Add ESLint rule vskill/no-raw-color and register it
**User Story**: US-002 | **Satisfies ACs**: AC-US2-06 | **Status**: [x] completed
**Phase**: 1 | **Estimated**: 1h | **Test Level**: unit
**Test Plan**:
  Given `eslint.config.js` registers the `vskill/no-raw-color` rule
  When ESLint runs against a component file containing `color: "#FF0000"` or `background: rgb(0,0,0)`
  Then ESLint reports an error on that line; when the same file uses `var(--text-primary)` or `bg-ink`, ESLint passes
**Files**:
  - `repositories/anton-abyzov/vskill/eslint.config.js`
  - `repositories/anton-abyzov/vskill/src/eval-ui/eslint-rules/no-raw-color.ts`
**Dependencies**: T-002

---

### T-008: Create CI scripts — check-no-shimmer, check-serif-scope
**User Story**: US-002, US-001 | **Satisfies ACs**: AC-US2-01, AC-US1-01 | **Status**: [x] completed
**Phase**: 1 | **Estimated**: 1h | **Test Level**: unit
**Test Plan**:
  Given `scripts/check-no-shimmer.ts` greps `src/eval-ui/src/**` for `shimmer` and `scripts/check-serif-scope.ts` greps workspace/editor paths for `--font-serif` usage
  When run against a file containing `animation: shimmer` or `font-family: var(--font-serif)` inside `src/eval-ui/src/pages/workspace/`
  Then each script exits with code 1 and prints the offending file path; when no violations exist, they exit 0
**Files**:
  - `repositories/anton-abyzov/vskill/scripts/check-no-shimmer.ts`
  - `repositories/anton-abyzov/vskill/scripts/check-serif-scope.ts`
  - `repositories/anton-abyzov/vskill/package.json` (add `lint:shimmer`, `lint:serif-scope` scripts)
**Dependencies**: T-002

---

## Phase 2 — Shell + Sidebar Split

_Goal: 3-row shell renders; OWN/INSTALLED sidebar split driven by `classifyOrigin` SSoT; selection indicator, collapse persistence, empty states._

---

### T-009: Rewrite StudioLayout with 3-row CSS grid shell
**User Story**: US-007 | **Satisfies ACs**: AC-US7-01, AC-US7-02, AC-US7-03, AC-US7-04 | **Status**: [x] completed
**Phase**: 2 | **Estimated**: 2h | **Test Level**: component
**Test Plan**:
  Given `StudioLayout.tsx` renders with `grid-template-rows: var(--top-rail-height) 1fr var(--status-bar-height)` and middle row uses `grid-template-columns: var(--sidebar-width) 1fr`
  When rendered at 1280px viewport width
  Then the sidebar column is 320px and main area fills 1fr; at 900px viewport, sidebar is 240px; below 768px, sidebar is not in the grid column (overlay mode)
**Files**:
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/components/StudioLayout.tsx`
**Dependencies**: T-002, T-005
**Notes**: Wrap with `<header>`, `<aside>`, `<main>`, `<footer role="contentinfo">` semantics per plan §7.

---

### T-010: Build TopRail component (logo, breadcrumb, quick actions)
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01 | **Status**: [x] completed
**Phase**: 2 | **Estimated**: 1.5h | **Test Level**: component
**Test Plan**:
  Given `TopRail` renders with a project name prop and a selected skill breadcrumb
  When rendered in both light and dark themes
  Then the logo, "Skill Studio" label in 600 mono, and breadcrumb `OWN › plugin › skill-name` are visible; the `⌘K` button has `aria-label` and is focusable; clicking `⌘K` emits the `onOpenPalette` callback
**Files**:
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/components/TopRail.tsx`
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/__tests__/TopRail.test.tsx`
**Dependencies**: T-009

---

### T-011: Build StatusBar component (project path, model, health, theme toggle)
**User Story**: US-002 | **Satisfies ACs**: AC-US2-03 | **Status**: [x] completed
**Phase**: 2 | **Estimated**: 1.5h | **Test Level**: component
**Test Plan**:
  Given `StatusBar` reads from `useTheme()` and `ConfigContext`
  When the theme toggle segment is clicked three times starting from `"light"`
  Then theme cycles `light → dark → auto → light` and `localStorage.getItem("vskill-theme")` reflects each intermediate state; the `aria-label` on the button reads `"Switch to dark theme"`, `"Switch to auto theme"`, `"Switch to light theme"` respectively
**Files**:
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/components/StatusBar.tsx`
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/__tests__/StatusBar.test.tsx`
**Dependencies**: T-004, T-009

---

### T-012: Build ProvenanceChip component (installed agent dir display chip)
**User Story**: US-001 | **Satisfies ACs**: AC-US1-12 | **Status**: [x] completed
**Phase**: 2 | **Estimated**: 0.5h | **Test Level**: component
**Test Plan**:
  Given `ProvenanceChip` receives `dir="/home/user/.claude/skills/foo"` and `root="/home/user"`
  When rendered
  Then displays the text `.claude` in `--type-meta` monospace style with `--text-faint` color and no background fill; tooltip shows the full dir on hover
**Files**:
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/components/sidebar/ProvenanceChip.tsx`
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/__tests__/ProvenanceChip.test.tsx`
**Dependencies**: T-002
**Notes**: Derives first path segment from `skill.dir` for display only — classification decision comes from `skill.origin` (ADR-0674-02). No `startsWith(".claude")` checks here.

---

### T-013: Build SkillRow component (36px row, provenance dot, selection state)
**User Story**: US-001 | **Satisfies ACs**: AC-US1-06, AC-US1-12, AC-US1-13 | **Status**: [x] completed
**Phase**: 2 | **Estimated**: 2h | **Test Level**: component
**Test Plan**:
  Given `SkillRow` receives `skill.origin="source"` and `isSelected=false`
  When rendered and then `isSelected` changes to `true`
  Then the row transitions to `background: var(--bg-selected)` and gains a `box-shadow: inset 2px 0 0 var(--border-selected)` within 180ms; the provenance dot for a source skill uses `--status-own` color; for an installed skill the dot uses `--status-installed`; `data-selected` attribute is set on the row element
**Files**:
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/components/sidebar/SkillRow.tsx`
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/__tests__/SkillRow.test.tsx`
**Dependencies**: T-012
**Notes**: Row height 36px. Inter Tight for names. JetBrains Mono for paths/chips. `updateAvailable` chip is accent-colored per AC-US1-13. No shimmer.

---

### T-014: Build PluginGroup component (plugin header + skill rows, alpha sort)
**User Story**: US-001 | **Satisfies ACs**: AC-US1-11 | **Status**: [x] completed
**Phase**: 2 | **Estimated**: 1h | **Test Level**: component
**Test Plan**:
  Given `PluginGroup` receives an array of skills all belonging to `plugin="obsidian-brain"` plus another `plugin="slack-messaging"`
  When rendered
  Then groups appear in alphabetical order by plugin name; each group header shows the plugin name in kicker caps with per-plugin count; `obsidian-brain` renders before `slack-messaging`
**Files**:
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/components/sidebar/PluginGroup.tsx`
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/__tests__/PluginGroup.test.tsx`
**Dependencies**: T-013

---

### T-015: Build SidebarSection component (OWN/INSTALLED header, collapse, localStorage)
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-04, AC-US1-05 | **Status**: [x] completed
**Phase**: 2 | **Estimated**: 2h | **Test Level**: component
**Test Plan**:
  Given `SidebarSection` with `origin="source"` is rendered with 5 source skills and collapsed state initially read from `localStorage.getItem("vskill-sidebar-own-collapsed")` (which is null, so defaults to false)
  When the section header is clicked
  Then the skill rows collapse (height 0), `localStorage.getItem("vskill-sidebar-own-collapsed")` is set to `"true"`, and clicking the header again re-expands and sets it back to `"false"`; an INSTALLED section uses `"vskill-sidebar-installed-collapsed"` key
**Files**:
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/components/sidebar/SidebarSection.tsx`
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/__tests__/SidebarSection.test.tsx`
**Dependencies**: T-014
**Notes**: Both sections default to expanded (AC-US1-04). Section header uses `<h2>` with `aria-level="2"`. Group below uses `role="group"` with `aria-labelledby` (AC-US8-04).

---

### T-016: Build SidebarSearch component (text input, / shortcut, fuzzy filter)
**User Story**: US-001, US-004 | **Satisfies ACs**: AC-US1-09, AC-US4-01, AC-US4-06 | **Status**: [x] completed
**Phase**: 2 | **Estimated**: 1.5h | **Test Level**: component
**Test Plan**:
  Given `SidebarSearch` is rendered with 10 skills (5 own, 5 installed) and fuse.js configured on `{skill, plugin, dir}`
  When the query `"obsidian"` is typed
  Then only skills whose name/plugin/dir matches `"obsidian"` are shown within their respective sections; the filtered count badge on each section updates to `(N of M)` format; after pressing `Escape` the query clears and all skills are visible again; debounce is 120ms (verified with timer mocking)
**Files**:
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/components/sidebar/SidebarSearch.tsx`
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/__tests__/SidebarSearch.test.tsx`
**Dependencies**: T-015
**Notes**: Fuzzy via `fuse.js` ^7. Match highlighting uses `<mark>` with `--accent-soft` bg. Results remain in their section (Installed matches stay in Installed). AC-US1-09 zero-match case: show "No matches in this section" micro-state, keep section visible.

---

### T-017: Build Sidebar root component (composites SidebarSection + search + empty states)
**User Story**: US-001 | **Satisfies ACs**: AC-US1-03, AC-US1-07, AC-US1-08, AC-US1-10 | **Status**: [x] completed
**Phase**: 2 | **Estimated**: 2h | **Test Level**: component
**Test Plan**:
  Given `Sidebar` receives a mixed array of skills with `origin: "source" | "installed"`, including one pair where `(plugin, skill)` is identical in both sections (duplicate scenario)
  When rendered
  Then own skills appear above the full-width divider, installed skills below; the duplicate skill appears in both sections, with the installed copy showing a `"synced from Own"` link; source section with zero skills shows "No skills yet." CTA copy; installed section with zero skills shows "No installed skills. Run `vskill install <plugin>` to add one." copy
**Files**:
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/components/Sidebar.tsx`
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/__tests__/Sidebar.test.tsx`
**Dependencies**: T-015, T-016
**Notes**: Origin classification consumed from `skill.origin` only — no path inspection in this component (ADR-0674-02). Duplicate detection cross-references `(plugin, skill)` pairs client-side after the split.

---

### T-018: Implement sidebar virtualization with react-virtuoso (threshold ≥200)
**User Story**: US-009 | **Satisfies ACs**: AC-US9-02 | **Status**: [x] completed
**Phase**: 2 | **Estimated**: 2h | **Test Level**: component
**Test Plan**:
  Given `Sidebar` receives 250 skills (150 own + 100 installed)
  When rendered
  Then only the visible rows are mounted in the DOM (verified by counting DOM nodes — should be far fewer than 250); scrolling to the bottom renders previously-unmounted rows; section headers remain sticky/visible during scroll
**Files**:
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/components/Sidebar.tsx`
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/components/sidebar/SidebarSection.tsx`
  - `repositories/anton-abyzov/vskill/package.json` (add `react-virtuoso`)
**Dependencies**: T-017
**Notes**: Threshold is skills.length >= 200 per scope brief (plan says > 60, spec says >= 500, use 200 as balanced). Each section virtualizes independently. Overscan 4.

---

### T-019: Implement ResizeHandle for sidebar width drag (240–480px, localStorage)
**User Story**: US-007 | **Satisfies ACs**: AC-US7-05 | **Status**: [x] completed
**Phase**: 2 | **Estimated**: 1.5h | **Test Level**: component
**Test Plan**:
  Given `ResizeHandle` is mounted between sidebar and workspace
  When pointer-down on the handle and dragged 50px to the right
  Then `--sidebar-width` CSS variable on the layout element updates to `370px` (original 320px + 50px); after mouseup, `localStorage.getItem("vskill-sidebar-width")` equals `"370"`; clamped: dragging beyond 480px stays at 480px, below 240px stays at 240px
**Files**:
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/components/ResizeHandle.tsx`
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/__tests__/ResizeHandle.test.tsx`
**Dependencies**: T-009
**Notes**: Uses pointer capture events. `cursor: col-resize`. No animation during drag (live update).

---

### T-020: Update App.tsx — wire new layout, delete deprecated components
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01 | **Status**: [x] completed
**Phase**: 2 | **Estimated**: 1h | **Test Level**: component
**Test Plan**:
  Given `App.tsx` wraps `<ThemeProvider>` → `<StudioLayout>` → `<TopRail>` + `<Sidebar>` + `<Workspace>` + `<StatusBar>`
  When rendered with mocked `StudioContext` providing mixed origin skills
  Then the OWN and INSTALLED section headers are present in the sidebar; `LeftPanel`, `SkillCard`, and `SkillGroupList` components are no longer referenced
**Files**:
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/App.tsx`
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/components/LeftPanel.tsx` (delete)
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/components/SkillCard.tsx` (delete)
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/components/SkillGroupList.tsx` (delete)
**Dependencies**: T-017, T-009, T-010, T-011

---

### T-021: Extend API and SkillInfo type with origin field guarantee
**User Story**: US-001 | **Satisfies ACs**: AC-US1-03 | **Status**: [x] completed
**Phase**: 2 | **Estimated**: 1h | **Test Level**: unit
**Test Plan**:
  Given `src/eval-server/api-routes.ts` `/api/skills` endpoint
  When a skill with a dir starting with `.claude/` relative to root is included
  Then the response JSON for that skill has `origin: "installed"`; a skill with a dir outside agent paths has `origin: "source"`; origin is derived from `classifyOrigin(skill.dir, root)` in `src/eval/skill-scanner.ts` and not recomputed in the route
**Files**:
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/types.ts`
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/api.ts`
  - `repositories/anton-abyzov/vskill/src/eval-server/api-routes.ts`
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/__tests__/api-origin.test.ts`
  - `repositories/anton-abyzov/vskill/src/eval-server/__tests__/api-skills.test.ts`
**Dependencies**: none (can run in parallel with Phase 2 UI tasks)
**Notes**: Endpoint is `/api/skills` (not `/api/v1/skills` — the v1 prefix belongs to the verified-skill.com platform proxy routes). Server-side behavior was already correct pre-task: `scanSkills()` → `classifyOrigin()` populates `origin` on every item. This task added (a) a defensive `s.origin ?? classifyOrigin(...)` fallback in the `/api/skills` handler, (b) a client-side `normalizeSkillInfo()` boundary validator that defaults missing/invalid origin to `"source"` with `console.warn` (graceful degradation), and (c) explicit server + client regression tests locking the contract. Downstream consumers may treat `SkillInfo.origin` as a guaranteed non-null `"source" | "installed"` literal.

---

### T-022: Playwright E2E — sidebar split renders with correct counts and collapse
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-04, AC-US1-05 | **Status**: [x] completed
**Phase**: 2 | **Estimated**: 1.5h | **Test Level**: e2e
**Test Plan**:
  Given the eval-server is started with a seeded workspace containing 3 source skills and 2 installed skills
  When Playwright opens the studio
  Then the OWN section header shows count 3 and INSTALLED shows count 2; clicking the OWN header collapses that section; reloading the page preserves the collapsed state; clicking again expands it
**Files**:
  - `repositories/anton-abyzov/vskill/src/eval-ui/e2e/sidebar-split.spec.ts`
**Dependencies**: T-017, T-020

---

### T-023: Add loading placeholder rows (no shimmer, static fill)
**User Story**: US-006, US-001 | **Satisfies ACs**: AC-US6-01, AC-US6-02, AC-US1-14 | **Status**: [x] completed
**Phase**: 2 | **Estimated**: 1h | **Test Level**: component
**Test Plan**:
  Given `Sidebar` receives `isLoading=true`
  When rendered
  Then six 36px placeholder rows with `--bg-hover` static fill are visible (3 per section); no `animation` or `@keyframes` are applied to them; section headers render with count `—`; the CI check-no-shimmer script passes on the component file
**Files**:
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/components/sidebar/SkeletonRow.tsx`
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/components/Sidebar.tsx` (integrate)
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/__tests__/Sidebar.loading.test.tsx`
**Dependencies**: T-017

---

### T-024: Add sidebar error state and SSE disconnect banner
**User Story**: US-006 | **Satisfies ACs**: AC-US6-03, AC-US6-06 | **Status**: [x] completed
**Phase**: 2 | **Estimated**: 1h | **Test Level**: component
**Test Plan**:
  Given `Sidebar` receives `error="Permission denied"` prop
  When rendered
  Then an error card is shown with the error message, a `<details>` disclosure with the full error, and a "Retry" button; when the SSE connection closes, a top-bar `<aside aria-live="assertive">` banner reads "Disconnected — reconnecting…"; when SSE reconnects, the banner disappears
**Files**:
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/components/Sidebar.tsx` (error state)
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/components/DisconnectBanner.tsx`
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/__tests__/DisconnectBanner.test.tsx`
**Dependencies**: T-017

---

## Phase 3 — Detail Panel

_Goal: every SkillInfo field surfaced; RightPanel card layout; progressive disclosure; empty and error states._

---

### T-025: Extend SkillInfo type and augment /api/skills with frontmatter fields
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-05, AC-US3-07 | **Status**: [x] completed
**Phase**: 3 | **Estimated**: 2h | **Test Level**: unit
**Test Plan**:
  Given `api-routes.ts` parses SKILL.md frontmatter (via the inline `parseSkillFrontmatter()` helper — no gray-matter dep added) for each skill
  When the `/api/skills` endpoint is called with a skill that has `description`, `version`, `tags`, `author` in its frontmatter and a known `lastModified` mtime
  Then the response includes those fields; `sizeBytes` is the sum of file sizes in the skill dir; `lastModified` is an ISO string; existing consumers that don't reference the new fields are unaffected
**Files**:
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/types.ts`
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/api.ts`
  - `repositories/anton-abyzov/vskill/src/eval-server/api-routes.ts`
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/__tests__/api-frontmatter.test.ts`
  - `repositories/anton-abyzov/vskill/src/eval-server/__tests__/api-skills.test.ts`
**Dependencies**: T-021
**Notes**: Endpoint is `/api/skills` (not `/api/v1/skills` — the v1 prefix is reserved for verified-skill.com platform proxy routes). All new SkillInfo fields use `T | null` (JSON-stable) rather than optional-undefined, so existing consumers see a consistent shape. Added: `description`, `version`, `category`, `author`, `license`, `homepage`, `tags[]`, `deps[]`, `mcpDeps[]`, `entryPoint`, `lastModified` (ISO 8601), `sizeBytes`, `sourceAgent` (installed-only, derived from `AGENTS_REGISTRY.localSkillsDir` first segment).

---

### T-026: Restyle DetailHeader with new typography scale and path chip
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-09 | **Status**: [x] completed
**Phase**: 3 | **Estimated**: 1.5h | **Test Level**: component
**Test Plan**:
  Given `DetailHeader` receives a skill with name, plugin, version, origin, certTier, and dir
  When rendered in light theme
  Then the skill name is displayed at `--type-heading-lg` (20px, Source Serif 4 500); plugin name is a breadcrumb prefix in `--type-meta`; origin badge uses dot-only style (`--status-own` or `--status-installed`) with no pill fill; path chip shows truncated dir with a copy-to-clipboard button; missing/null fields show `—` in `--text-faint`
**Files**:
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/components/DetailHeader.tsx`
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/__tests__/DetailHeader.test.tsx`
**Dependencies**: T-025, T-002

---

### T-027: Build MetadataTab — all frontmatter fields, filesystem group, benchmark group
**User Story**: US-003 | **Satisfies ACs**: AC-US3-02, AC-US3-05, AC-US3-06, AC-US3-09, AC-US3-10 | **Status**: [x] completed
**Phase**: 3 | **Estimated**: 2.5h | **Test Level**: component
**Test Plan**:
  Given `MetadataTab` receives a fully-populated `SkillInfo` including extended frontmatter (description, model, allowedTools, target-agents, tags, author) and filesystem stats (dir, byteSize, lastModified)
  When rendered at 1280px width
  Then: frontmatter definition list shows all keys including a "More fields" collapsible for unknown keys; filesystem group shows absolute dir, SKILL.md entry path, file count, byte size, lastModified as relative time with absolute on hover; benchmark group shows evalCount, assertionCount, benchmarkStatus dot, lastBenchmark; no field is silently omitted; long paths use tooltip for full value; `allowedTools` wraps to multiple chips
**Files**:
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/pages/workspace/MetadataTab.tsx`
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/__tests__/MetadataTab.test.tsx`
**Dependencies**: T-026

---

### T-028: Build MetadataTab — MCP dependencies section
**User Story**: US-003 | **Satisfies ACs**: AC-US3-03 | **Status**: [x] completed
**Phase**: 3 | **Estimated**: 1h | **Test Level**: component
**Test Plan**:
  Given `MetadataTab` receives a skill with 2 MCP dependencies (server, url, transport, matchedTools each populated)
  When the MCP Dependencies section renders
  Then each dependency shows server, url, transport, matchedTools, and a "Copy config snippet" button; when 0 MCP deps, the section shows "No MCP dependencies." on a single line
**Files**:
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/pages/workspace/MetadataTab.tsx` (extend)
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/__tests__/MetadataTab.mcp.test.tsx`
**Dependencies**: T-027

---

### T-029: Build MetadataTab — skill dependency chips (clickable, navigate or tooltip)
**User Story**: US-003 | **Satisfies ACs**: AC-US3-04 | **Status**: [x] completed
**Phase**: 3 | **Estimated**: 1h | **Test Level**: component
**Test Plan**:
  Given `MetadataTab` receives a skill with 2 skill dependencies — one that exists in the sidebar and one that does not
  When both dependency chips are rendered
  Then clicking the present dependency chip triggers `onSelectSkill(dep)` callback and the sidebar selection updates; clicking the absent dependency shows a tooltip "Not installed" rather than navigating; both chips are keyboard-focusable and activatable with Enter
**Files**:
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/pages/workspace/MetadataTab.tsx` (extend)
**Dependencies**: T-027

---

### T-030: Build MetadataTab — source agent row for installed skills
**User Story**: US-003 | **Satisfies ACs**: AC-US3-07 | **Status**: [x] completed
**Phase**: 3 | **Estimated**: 0.5h | **Test Level**: component
**Test Plan**:
  Given `MetadataTab` receives a skill with `origin: "installed"` and `dir` starting with `.claude/`
  When rendered
  Then a "Source agent" row appears showing `.claude/skills/...` with the agent display name from `AGENTS_REGISTRY` (e.g., "Claude Code"); source skills (`origin: "source"`) do not render the "Source agent" row
**Files**:
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/pages/workspace/MetadataTab.tsx` (extend)
**Dependencies**: T-027

---

### T-031: Wire MetadataTab and VersionHistoryPanel into RightPanel tab bar
**User Story**: US-003 | **Satisfies ACs**: AC-US3-08 | **Status**: [x] completed
**Phase**: 3 | **Estimated**: 1h | **Test Level**: component
**Test Plan**:
  Given `RightPanel` with a selected skill that has version history
  When the "Overview" tab is clicked, then the "Versions" tab is clicked
  Then Overview shows `MetadataTab`; Versions shows the existing `VersionHistoryPanel` with pinned-version highlighting; the tab bar uses hairline-divider + 2px underline on active (no pill tabs); tab labels are in `--type-heading-md` sans
**Files**:
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/components/TabBar.tsx` (restyle)
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/components/RightPanel.tsx` (integrate MetadataTab)
**Dependencies**: T-027

---

### T-032: Build SkillRowHoverCard (popover on 500ms hover, progressive disclosure)
**User Story**: US-003 | **Satisfies ACs**: AC-US3-02, AC-US3-09 | **Status**: [x] completed
**Phase**: 3 | **Estimated**: 1.5h | **Test Level**: component
**Test Plan**:
  Given `SkillRowHoverCard` wraps a `SkillRow` and receives a skill with description, version, tags, lastModified, evalCount
  When a pointer hovers on the row for 600ms (mocked via timer)
  Then a popover appears showing: 3-line clamped description, version (v1.0.0), up to 4 tags (overflow "+N"), "3 days ago" relative lastModified, eval count; closing happens immediately on pointer-leave; missing fields show `—` not empty string
**Files**:
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/components/sidebar/SkillRowHoverCard.tsx`
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/__tests__/SkillRowHoverCard.test.tsx`
**Dependencies**: T-013
**Notes**: Use native `popover` API with 30-line custom positioner fallback (no Radix — bundle budget).

---

### T-033: Add detail panel empty state and error state
**User Story**: US-006 | **Satisfies ACs**: AC-US6-04, AC-US6-05 | **Status**: [x] completed
**Phase**: 3 | **Estimated**: 1h | **Test Level**: component
**Test Plan**:
  Given `RightPanel` with no skill selected
  When rendered
  Then an `<EmptyState variant="no-selection">` displays with a Source Serif 4 headline and calm copy; when a skill is selected but its SKILL.md fails to load, an error state shows "Couldn't load SKILL.md for <skill>" with "Open in editor" and "Copy path" actions; an `ErrorBoundary` wraps the workspace root and prevents white-screen crashes
**Files**:
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/components/EmptyState.tsx` (restyle + extend)
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/components/RightPanel.tsx` (integrate)
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/__tests__/RightPanel.states.test.tsx`
**Dependencies**: T-031

---

### T-034: Playwright E2E — detail panel populates on skill selection
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-05 | **Status**: [x] completed
**Phase**: 3 | **Estimated**: 1h | **Test Level**: e2e
**Test Plan**:
  Given the studio is running with a seeded skill that has a populated SKILL.md frontmatter
  When Playwright clicks on that skill in the sidebar
  Then the detail panel header shows the skill name, plugin breadcrumb, origin badge, and path chip; the Metadata tab shows at least description and lastModified; `aria-live="polite"` region announces "Viewing <skill-name> (Own)"
**Files**:
  - `repositories/anton-abyzov/vskill/src/eval-ui/e2e/skill-detail-capture.spec.ts`
**Dependencies**: T-033

---

## Phase 4 — Polish, Keyboard, A11y

_Goal: every shortcut works; strings.ts central; voice CI gate; reduced-motion; axe-core; Playwright theme-persistence and keyboard E2E._

---

### T-035: Create central strings.ts module with all user-facing copy
**User Story**: US-010 | **Satisfies ACs**: AC-US10-01, AC-US10-02, AC-US10-03, AC-US10-04, AC-US10-05 | **Status**: [x] completed
**Phase**: 4 | **Estimated**: 1.5h | **Test Level**: unit
**Test Plan**:
  Given `strings.ts` exports a `strings` object containing sidebar, actions, errors, and loading copy
  When a Vitest test inspects every string value
  Then none contains "oops", "uh-oh", "awesome", "blazing-fast", an exclamation point at end of any value, or celebration emoji (🎉 ✨ 🚀 ✅); all empty-state strings follow "Short declarative sentence. Concrete next step." pattern; success toasts are ≤ 5 words
**Files**:
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/strings.ts`
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/__tests__/strings-voice.test.ts`
**Dependencies**: T-017, T-027

---

### T-036: Add CI voice-enforcement script for strings.ts
**User Story**: US-010 | **Satisfies ACs**: AC-US10-06 | **Status**: [x] completed
**Phase**: 4 | **Estimated**: 0.5h | **Test Level**: unit
**Test Plan**:
  Given `scripts/check-strings-voice.ts` runs regex patterns against `src/eval-ui/src/strings.ts`
  When any string contains `oops`, `uh-oh`, `awesome`, `blazing-fast`, a celebration emoji, or ends with `!!`
  Then the script exits with code 1 and prints the violating line; when strings.ts is clean, exits 0
**Files**:
  - `repositories/anton-abyzov/vskill/scripts/check-strings-voice.ts`
  - `repositories/anton-abyzov/vskill/package.json` (add `lint:strings` script)
**Dependencies**: T-035

---

### T-037: Implement useKeyboardShortcut hook (input-aware, single registry)
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-04, AC-US4-09 | **Status**: [x] completed
**Phase**: 4 | **Estimated**: 1.5h | **Test Level**: unit
**Test Plan**:
  Given `useKeyboardShortcut` registers handlers for `"/"`, `"j"`, `"k"`, `"?"`, `"Cmd+b"`, `"Cmd+Shift+d"`
  When `"/"` is pressed while `document.activeElement` is `<body>`
  Then the registered callback fires; when `"/"` is pressed while `document.activeElement` is an `<input>`, the callback does NOT fire; `Escape` key is handled correctly in stacked contexts (e.g., palette open → search open → nothing open)
**Files**:
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/hooks/useKeyboardShortcut.ts`
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/__tests__/useKeyboardShortcut.test.ts`
**Dependencies**: none

---

### T-038: Wire j/k/Enter navigation across sidebar sections
**User Story**: US-004 | **Satisfies ACs**: AC-US4-02 | **Status**: [x] completed
**Phase**: 4 | **Estimated**: 1h | **Test Level**: component
**Test Plan**:
  Given a sidebar with 3 own skills then 2 installed skills and the first own skill focused
  When `"j"` is pressed 4 times
  Then selection moves through all 5 skills in order (skipping the section header between them); pressing `"k"` moves backward; pressing `Enter` opens the selected skill in the detail panel
**Files**:
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/components/Sidebar.tsx` (integrate navigation)
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/__tests__/Sidebar.keyboard.test.tsx`
**Dependencies**: T-037, T-017

---

### T-039: Build CommandPalette component (lazy-loaded, ⌘K trigger)
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01 | **Status**: [x] completed
**Phase**: 4 | **Estimated**: 2h | **Test Level**: component
**Test Plan**:
  Given `CommandPalette` is loaded via `React.lazy` and mounted
  When `Cmd+K` is pressed from the studio
  Then the palette opens with an input focused; typing `"bench"` filters actions to show "Run benchmark"; pressing `Escape` closes the palette and focus returns to the element that had focus before; the palette uses `role="combobox"` + `role="listbox"` ARIA; focus is trapped inside while open
**Files**:
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/components/CommandPalette.tsx`
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/__tests__/CommandPalette.test.tsx`
**Dependencies**: T-037
**Notes**: Lazy-loaded so it's not in the initial bundle. Stub actions sufficient for this increment: select skill, run benchmark, switch theme, new skill.

---

### T-040: Build ShortcutModal (keyboard cheatsheet, ? trigger, focus trap)
**User Story**: US-004 | **Satisfies ACs**: AC-US4-05 | **Status**: [x] completed
**Phase**: 4 | **Estimated**: 1h | **Test Level**: component
**Test Plan**:
  Given `ShortcutModal` is mounted via `React.lazy`
  When `"?"` is pressed
  Then the modal opens listing all shortcuts grouped by Navigation / Actions / Theme; `role="dialog"` + `aria-modal="true"` are set; `Escape` closes it and focus returns to the triggering element; the modal is keyboard-navigable (Tab cycles through close button only)
**Files**:
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/components/ShortcutModal.tsx`
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/__tests__/ShortcutModal.test.tsx`
**Dependencies**: T-037

---

### T-041: Build ContextMenu component (right-click/long-press on skill row)
**User Story**: US-004 | **Satisfies ACs**: AC-US4-07 | **Status**: [x] completed
**Phase**: 4 | **Estimated**: 2h | **Test Level**: component
**Test Plan**:
  Given `ContextMenu` wraps a `SkillRow` with `origin="source"` and `updateAvailable=false`
  When the row is right-clicked
  Then a menu appears with: Open, Copy Path, Reveal in Editor, Edit, Duplicate, Run Benchmark; "Update" and "Uninstall" are absent; for an installed skill with `updateAvailable=true`, "Update" and "Uninstall" appear but "Edit" and "Duplicate" are absent; `role="menu"` + `role="menuitem"` are set; arrow keys navigate items; `Escape` closes and restores focus
**Files**:
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/components/ContextMenu.tsx`
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/__tests__/ContextMenu.test.tsx`
  - `repositories/anton-abyzov/vskill/src/eval-server/api-routes.ts` (add `reveal` endpoint)
**Dependencies**: T-013, T-037

---

### T-042: Add theme-transition CSS (150ms bg/color/border, no transition on focus)
**User Story**: US-002 | **Satisfies ACs**: AC-US2-08, AC-US2-09 | **Status**: [x] completed
**Phase**: 4 | **Estimated**: 0.5h | **Test Level**: component
**Test Plan**:
  Given `globals.css` has `:root { transition: background-color 150ms, color 150ms, border-color 150ms; }` and `input:focus, textarea:focus { transition: none; }` and `@media (prefers-reduced-motion: reduce)` collapses all durations to 0ms
  When Vitest renders a component and `data-theme` is changed from `"light"` to `"dark"`
  Then the computed transition on `body` is `"background-color 150ms"` (not zero); when `prefers-reduced-motion: reduce` is mocked, the computed transition is `"0ms"`
**Files**:
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/styles/globals.css`
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/__tests__/theme-transition.test.ts`
**Dependencies**: T-002

---

### T-043: Run token sweep on workspace pages — replace hardcoded colors
**User Story**: US-002 | **Satisfies ACs**: AC-US2-06, AC-US2-07 | **Status**: [x] completed
**Phase**: 4 | **Estimated**: 2h | **Test Level**: unit
**Test Plan**:
  Given ESLint rule `vskill/no-raw-color` is active
  When `eslint src/eval-ui/src/pages/workspace/**` is run after the sweep
  Then zero violations are reported; SVG icons in workspace components use `currentColor`; code block syntax theme is mapped to theme tokens (GitHub-light/dark equivalent)
**Files**:
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/pages/workspace/**/*.tsx` (modify as needed)
**Dependencies**: T-007

---

### T-044: Add aria-live region for skill selection announcements
**User Story**: US-008 | **Satisfies ACs**: AC-US8-05, AC-US8-07 | **Status**: [x] completed
**Phase**: 4 | **Estimated**: 0.5h | **Test Level**: component
**Test Plan**:
  Given an `aria-live="polite"` region is rendered in `StudioLayout`
  When a skill is selected
  Then the region's text content updates to `"Viewing <skill-name> (Own)"` or `"Viewing <skill-name> (Installed)"`; toasts for errors use `aria-live="assertive"` and toasts for success use `aria-live="polite"`
**Files**:
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/components/StudioLayout.tsx`
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/__tests__/a11y-live-regions.test.tsx`
**Dependencies**: T-020

---

### T-045: Implement focus-visible rings using --border-focus across interactive elements
**User Story**: US-008 | **Satisfies ACs**: AC-US8-03, AC-US8-06 | **Status**: [x] completed
**Phase**: 4 | **Estimated**: 1h | **Test Level**: component
**Test Plan**:
  Given a `SkillRow` and modal dialog rendered with keyboard focus
  When `:focus-visible` is triggered on the row via keyboard Tab
  Then a 2px `outline` in `var(--border-focus)` with 2px offset is visible; mouse click does NOT show the ring (`:focus-visible` not `:focus`); `[data-contrast="more"]` widens the ring to 3px; in the modal, Tab cycles through focusable elements and does not escape the modal
**Files**:
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/styles/globals.css` (focus-visible rule)
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/__tests__/focus-ring.test.tsx`
**Dependencies**: T-002

---

### T-046: Add high-contrast variant [data-contrast="more"] tokens and prefers-contrast detection
**User Story**: US-008 | **Satisfies ACs**: AC-US8-09 | **Status**: [x] completed
**Phase**: 4 | **Estimated**: 1h | **Test Level**: component
**Test Plan**:
  Given `globals.css` has `[data-contrast="more"]` selector that thickens `--color-rule` and widens focus rings to 3px
  When `matchMedia("(prefers-contrast: more)").matches` is `true` (mocked) and the FOUC script runs
  Then `document.documentElement.dataset.contrast` equals `"more"` before React mounts; a contrast test asserts all muted-text pairs exceed 4.5:1 in high-contrast mode
**Files**:
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/styles/globals.css` (already partially done in T-002, finalize here)
  - `repositories/anton-abyzov/vskill/src/eval-ui/index.html` (contrast detection in inline script — already partially done in T-003)
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/__tests__/high-contrast.test.ts`
**Dependencies**: T-003, T-002

---

### T-047: Axe-core a11y test in both themes (zero serious/critical violations)
**User Story**: US-008 | **Satisfies ACs**: AC-US8-01, AC-US8-02, AC-US8-04 | **Status**: [x] completed
**Phase**: 4 | **Estimated**: 1.5h | **Test Level**: component
**Test Plan**:
  Given the full studio layout rendered with a mocked skill list (3 own, 2 installed) and a selected skill
  When `axe.run()` is called against the root in light theme and again in dark theme
  Then zero violations of impact "serious" or "critical" are reported in either theme; section headers have `role="heading"` aria-level="2"; each section group has `role="group"` with `aria-labelledby`; all interactive elements have accessible names
**Files**:
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/__tests__/a11y.test.tsx`
**Dependencies**: T-044, T-045, T-020
**Notes**: Install `@axe-core/react` as devDependency if not present.

---

### T-048: Bundle size CI assertion (initial chunk ≤ 250KB gzipped, fonts chunk ≤ 70KB)
**User Story**: US-009 | **Satisfies ACs**: AC-US9-05 | **Status**: [x] completed
**Phase**: 4 | **Estimated**: 1h | **Test Level**: unit
**Test Plan**:
  Given `vite build` produces a stats JSON
  When a CI script parses the gzipped chunk sizes
  Then the initial JS chunk is ≤ 250 KB gzipped; the fonts chunk is ≤ 70 KB gzipped; CommandPalette and ShortcutModal are in separate lazy chunks each ≤ 150 KB; the script exits non-zero if any threshold is exceeded
**Files**:
  - `repositories/anton-abyzov/vskill/scripts/check-bundle-size.ts`
  - `repositories/anton-abyzov/vskill/package.json` (add `check:bundle` script)
**Dependencies**: T-001, T-039, T-040

---

### T-049: Playwright E2E — theme toggle persists across reload
**User Story**: US-002 | **Satisfies ACs**: AC-US2-03, AC-US2-04 | **Status**: [x] completed
**Phase**: 4 | **Estimated**: 1h | **Test Level**: e2e
**Test Plan**:
  Given the studio is open with default (auto) theme
  When the theme toggle in the status bar is clicked to switch to `"dark"`, then the page is reloaded
  Then `document.documentElement.dataset.theme` is `"dark"` immediately after reload (before React hydration, checked via early evaluate); the toggle shows the moon icon and aria-label reads "Switch to auto theme"
**Files**:
  - `repositories/anton-abyzov/vskill/src/eval-ui/e2e/theme-persistence.spec.ts`
**Dependencies**: T-011, T-003

---

### T-050: Playwright E2E — keyboard shortcuts (/, j/k, ?, Cmd+B, Cmd+Shift+D)
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02, AC-US4-05, AC-US4-09 | **Status**: [x] completed
**Phase**: 4 | **Estimated**: 1.5h | **Test Level**: e2e
**Test Plan**:
  Given the studio is loaded with 3 own skills and 2 installed skills
  When Playwright presses `"/"` from the body
  Then the sidebar search input is focused; pressing `"j"` twice moves selection to the third own skill; pressing `"?"` opens the keyboard cheatsheet modal; pressing `"Escape"` closes it; pressing `"Ctrl+B"` hides the sidebar; pressing `"Ctrl+B"` again shows it; pressing `"Ctrl+Shift+D"` toggles the theme
**Files**:
  - `repositories/anton-abyzov/vskill/src/eval-ui/e2e/keyboard-shortcuts.spec.ts`
**Dependencies**: T-037, T-038, T-039, T-040

---

### T-051: Performance marks verification (detail panel ≤120ms, search ≤80ms)
**User Story**: US-009 | **Satisfies ACs**: AC-US9-03, AC-US9-04, AC-US9-06 | **Status**: [x] completed
**Phase**: 4 | **Estimated**: 1h | **Test Level**: e2e
**Test Plan**:
  Given the studio is loaded (Playwright with throttled CPU 4x slowdown for mid-range laptop simulation)
  When a skill is selected via click
  Then `performance.measure("detail-panel-render")` shows ≤120ms; typing in search shows result list update within ≤80ms for a 100-skill dataset; switching theme with the toggle completes without any `performance.mark("long-task")` entries > 50ms
**Files**:
  - `repositories/anton-abyzov/vskill/src/eval-ui/e2e/performance.spec.ts`
**Dependencies**: T-034, T-016, T-011

---

### T-052: Build Toast notification system (queue, auto-dismiss, reduced-motion)
**User Story**: US-004 | **Satisfies ACs**: AC-US4-08 | **Status**: [x] completed
**Phase**: 4 | **Estimated**: 1.5h | **Test Level**: component
**Test Plan**:
  Given `ToastProvider` wraps the app and a `useToast()` hook fires a success toast
  When the toast renders
  Then it appears in the bottom-right corner; auto-dismisses after 4000ms (verified with fake timers); a second toast queues below the first; pressing `Escape` dismisses the topmost toast; with `prefers-reduced-motion: reduce` mocked, the enter/exit animation duration is 0ms
**Files**:
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/components/Toast.tsx`
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/hooks/useToast.ts`
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/__tests__/Toast.test.tsx`
**Dependencies**: T-044
**Notes**: Error toasts use `aria-live="assertive"`; success/info toasts use `aria-live="polite"` (per AC-US8-07, already on T-044). "Retry" action on rollback toasts wired in T-053.

---

### T-053: Implement optimistic UI with rollback toast for quick actions
**User Story**: US-004 | **Satisfies ACs**: AC-US4-10 | **Status**: [x] completed
**Phase**: 4 | **Estimated**: 1.5h | **Test Level**: component
**Test Plan**:
  Given a skill row's context-menu "Copy Path" action is invoked
  When the action fires
  Then the UI updates immediately (optimistic state); if the backend responds within 500ms with success, the optimistic state is confirmed silently; if the backend returns an error or times out at 500ms, a rollback toast appears with the error message and a "Retry" button that re-invokes the same action
**Files**:
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/hooks/useOptimisticAction.ts`
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/__tests__/useOptimisticAction.test.ts`
**Dependencies**: T-052, T-041
**Notes**: Covers all quick actions exposed via ContextMenu (T-041) and keyboard shortcuts (T-037). Rollback restores pre-action UI state via stored snapshot.

---

### T-054: Add aria-invalid and aria-describedby to form inputs with validation errors
**User Story**: US-008 | **Satisfies ACs**: AC-US8-08 | **Status**: [x] completed
**Phase**: 4 | **Estimated**: 0.5h | **Test Level**: component
**Test Plan**:
  Given a form input in the create-skill flow receives an empty required value and the form is submitted
  When the validation error fires
  Then the input element has `aria-invalid="true"` and `aria-describedby` pointing to the error message element's id; the error message element exists in the DOM with the matching id; clearing the input and entering a valid value removes `aria-invalid`
**Files**:
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/components/FormField.tsx` (create or modify)
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/__tests__/FormField.a11y.test.tsx`
**Dependencies**: T-047
**Notes**: Applies to any form input rendered in the studio create flow. If a shared `FormField` wrapper does not exist, create one and retrofit the create-skill form.

---

### T-055: Lighthouse CI FCP/TTI budget assertion (FCP ≤800ms, TTI ≤1500ms)
**User Story**: US-009 | **Satisfies ACs**: AC-US9-01 | **Status**: [x] completed
**Phase**: 4 | **Estimated**: 1h | **Test Level**: e2e
**Test Plan**:
  Given `vite preview` is serving the production build with a workspace of ≤100 skills
  When Lighthouse CI runs in a simulated mid-range laptop environment (CPU throttle 4×, network Fast 3G)
  Then FCP is reported ≤800ms and TTI ≤1500ms; the CI script exits non-zero if either threshold is exceeded; results are written to `scripts/lighthouse-report.json`
**Files**:
  - `repositories/anton-abyzov/vskill/scripts/check-lhci.ts`
  - `repositories/anton-abyzov/vskill/package.json` (add `check:lhci` script)
**Dependencies**: T-048, T-001
**Notes**: Uses `@lhci/cli` as devDependency. Complementary to T-051 (interaction perf) and T-048 (bundle size). Cold-load scenario only — no warm-cache measurement.

---

## Phase 5 UX regressions — UI-LINK-AGENT bundle

Phase 4 screenshots surfaced a cluster of clickability / discoverability
gaps in the redesigned detail panel and top rail. T-056..T-062 close those
gaps without altering the overall redesign palette or layout.

### T-056: Wrap HOMEPAGE value in external-link anchor with ↗ glyph
**User Story**: US-004 | **Satisfies ACs**: AC-US4-02 | **Status**: [x] completed
**Phase**: 5 | **Estimated**: 0.25h | **Test Level**: component
**Test Plan**:
  Given a skill with a populated `homepage` frontmatter value
  When MetadataTab renders the Frontmatter card
  Then the Homepage row contains an `<a href target="_blank" rel="noopener noreferrer">` wrapping the URL, suffixed by a ↗ glyph; underline only appears on hover (rest state has no underline); when homepage is null, the row falls back to the muted em-dash (no anchor emitted).
**Files**:
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/components/MetadataTab.tsx`
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/components/__tests__/MetadataTab.links.test.tsx`
**Dependencies**: T-027
**Notes**: Link color uses `var(--text-accent)` which resolves to `var(--color-accent-ink)` in light mode and the near-white accent-ink in dark mode — matches the design-token voice without raw hex.

---

### T-057: Make ENTRY POINT a clickable mono chip with copy-to-clipboard
**User Story**: US-004 | **Satisfies ACs**: AC-US4-02 | **Status**: [x] completed
**Phase**: 5 | **Estimated**: 0.5h | **Test Level**: component
**Test Plan**:
  Given a skill with `dir=/a/b/c/obsidian-brain` and `entryPoint=SKILL.md`
  When the user clicks the Entry-point chip in the MetadataTab Filesystem card
  Then `navigator.clipboard.writeText` is called with the absolute path `/a/b/c/obsidian-brain/SKILL.md`, a `studio:toast` CustomEvent is dispatched on `window` carrying `{ message: "Copied <abs-path>", severity: "info" }`, and the chip renders in mono typography with a hover-border affordance; when `entryPoint` is null, the chip falls back to `SKILL.md` per the convention used elsewhere.
**Files**:
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/components/MetadataTab.tsx`
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/components/__tests__/MetadataTab.links.test.tsx`
**Dependencies**: T-027, T-052
**Notes**: MetadataTab is invoked as a plain function (not JSX) from RightPanel, so the implementation avoids hooks — it dispatches a global CustomEvent and leaves the toast wiring to any listener in the provider tree. Opening the file in the browser is impractical (no filesystem:// protocol), so copy-to-clipboard is the contract.

---

### T-058: Apply overflow-wrap: anywhere to DIRECTORY path values
**User Story**: US-004 | **Satisfies ACs**: AC-US4-02 | **Status**: [x] completed
**Phase**: 5 | **Estimated**: 0.25h | **Test Level**: component
**Test Plan**:
  Given a MetadataTab rendering a very long filesystem path (≥80 chars without spaces) in the Directory row
  When the rendered cell is inspected
  Then the value `<span data-path-value="true">` carries `overflowWrap: "anywhere"` and `wordBreak: "break-word"`, so the browser breaks between characters rather than preserving mid-word cliffs like `repos\ns`; the surrounding display-grid row alignment stays intact (130px label column + 1fr value column).
**Files**:
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/components/MetadataTab.tsx`
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/components/__tests__/MetadataTab.links.test.tsx`
**Dependencies**: T-027
**Notes**: DetailHeader already uses a head+…+tail truncation (`truncatePath`) plus a `title` attribute with the full path, so no change was required there — only MetadataTab's Directory row needed the wrap fix.

---

### T-059: Make breadcrumb segments clickable + dispatch navigate-scope event
**User Story**: US-004 | **Satisfies ACs**: AC-US4-02 | **Status**: [x] completed
**Phase**: 5 | **Estimated**: 0.5h | **Test Level**: component
**Test Plan**:
  Given the TopRail breadcrumb "Skill Studio · vskill · OWN › google-workspace › gws"
  When the user clicks "OWN"
  Then a `studio:navigate-scope` CustomEvent is dispatched on `window` with `detail = { scope: "origin", origin: "source" }`; clicking the plugin segment fires the same event with `{ scope: "plugin", plugin: "google-workspace" }`; the final skill segment is rendered as a non-clickable `<span aria-current="page">` (it is the current view).
**Files**:
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/components/TopRail.tsx`
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/components/__tests__/TopRail.modelselector.test.tsx`
**Dependencies**: T-026, T-037
**Notes**: Sidebar consumption of these events (scroll to section + expand / filter by plugin) lives in Sidebar.tsx which is owned by polish-interactions. The click surface + event dispatch is complete; wiring the listener is a follow-up tracked in qa-findings.

---

### T-060: Wire Model Selector into TopRail + add useStudioPreferences helper
**User Story**: US-004 | **Satisfies ACs**: AC-US4-02 | **Status**: [x] completed
**Phase**: 5 | **Estimated**: 1h | **Test Level**: component + unit
**Test Plan**:
  Given the TopRail renders inside a ConfigProvider with a populated config
  When the top rail paints
  Then a `<span data-slot="model-selector">` wraps `<ModelSelector />` inside the right-side action cluster (`data-toprail-right="true"`), positioned BEFORE the ⌘K palette button; and when `readStudioPreferences()` is called with an empty localStorage it returns `{}`; writing `selectedModel` persists it under the `vskill.studio.prefs` key and a subsequent `writeStudioPreference("sidebarCollapsed", true)` does NOT clobber the prior value; both calls are no-ops under a failing localStorage (quota / private-mode) without throwing.
**Files**:
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/components/TopRail.tsx`
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/hooks/useStudioPreferences.ts` (NEW)
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/hooks/__tests__/useStudioPreferences.test.ts` (NEW)
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/components/__tests__/TopRail.modelselector.test.tsx` (NEW)
**Dependencies**: T-024 (TopRail shell), T-053 (ModelSelector pre-existed from earlier increment)
**Notes**: BLOCKING_ISSUE — the team-lead spec calls for persisting preferences to `.vskill/studio.json` via an eval-server endpoint so the selection survives across browsers. There is no `POST /api/prefs` endpoint today. `useStudioPreferences` ships localStorage-only; the write surface is shaped to be swapped to a fetch call without touching callers. ModelSelector itself already persists provider/model via `POST /api/config`, so the user-visible behaviour is unchanged — the preference helper is for future keys (sidebarCollapsed, lastActiveTab, etc.).

---

### T-061: Verify theme toggle is rendered + reachable
**User Story**: US-007 | **Satisfies ACs**: AC-US7-01 | **Status**: [x] completed
**Phase**: 5 | **Estimated**: 0.1h | **Test Level**: component
**Test Plan**:
  Given the StatusBar is rendered inside a ThemeProvider
  When the rendered tree is inspected
  Then exactly one element carries `data-testid="theme-toggle"` with an `aria-label` matching `/theme/i`, confirming the toggle is present in the footer chrome.
**Files**:
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/components/StatusBar.tsx` (verified — no change)
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/components/__tests__/TopRail.modelselector.test.tsx`
**Dependencies**: T-042
**Notes**: The toggle already lives in StatusBar (bottom chrome, right-most button). The TopRail additionally gains the model selector (T-060) but NOT a redundant theme toggle — the design constraint is "one toggle, one location". Task outcome: regression test added so the toggle cannot silently disappear.

---

### T-062: Empty-state em-dash tooltip affordance
**User Story**: US-004 | **Satisfies ACs**: AC-US4-02 | **Status**: [x] completed
**Phase**: 5 | **Estimated**: 0.25h | **Test Level**: component
**Test Plan**:
  Given a skill with several null frontmatter fields (`version`, `author`, `license`, `homepage`)
  When MetadataTab renders the Frontmatter card
  Then each em-dash `<span>` carries a `title` attribute matching `/SKILL\.md|frontmatter/i` — pointing the user at the exact action ("Add `author:` to the SKILL.md frontmatter to display a value here."). No modal, no link — just a native tooltip hint.
**Files**:
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/components/MetadataTab.tsx`
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/components/__tests__/MetadataTab.links.test.tsx`
**Dependencies**: T-027
**Notes**: Hint table (`FIELD_HINTS`) covers all scalar rows plus Entry-point, Last modified, and Last benchmark (which are filesystem-derived, not frontmatter — hint text explains that).

---

## Phase 5 UX regressions — QA-driven expansion (T-063..T-066)

qa-e2e-agent's `e2e/qa-findings.md` surfaced four more regressions beyond
the original UI-LINK-AGENT scope. Team-lead added these as T-063..T-066.

### T-063: Wire Versions tab switching in App.tsx
**User Story**: US-003 | **Satisfies ACs**: AC-US3-08 | **Status**: [x] completed
**Phase**: 5 | **Estimated**: 0.5h | **Test Level**: component
**Test Plan**:
  Given a selected skill and App.tsx lifting `activeDetailTab` state
  When the user clicks the "Versions" tab button
  Then `onDetailTabChange` fires with `"versions"`; the tab button's `aria-selected` flips to `true`; the Versions tabpanel renders `<VersionHistoryPanel>` inside a `<WorkspaceProvider>` (not the "Select a skill from the sidebar…" fallback), because App.tsx now forwards `allSkills` + `onSelectSkill` so RightPanel's `renderDetailShell` enters the integrated branch.
**Files**:
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/App.tsx`
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/components/RightPanel.tsx`
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/components/__tests__/App.versions-tab.test.tsx` (NEW)
**Dependencies**: T-031
**Notes**: Fixes qa-findings #1 and #12 simultaneously — the integrated `allSkills` / `onSelectSkill` bag is threaded through so skill-dep chips in Overview also work end-to-end in production (not just in the isolated test branch).

---

### T-064: Wire ContextMenu to SkillRow
**User Story**: US-004 | **Satisfies ACs**: AC-US4-07 | **Status**: [x] completed
**Phase**: 5 | **Estimated**: 1h | **Test Level**: unit + component
**Test Plan**:
  Given App.tsx holds a `contextMenuState: { open, x, y, skill }` anchor and passes `onContextMenu` through Sidebar → SectionList/PluginGroup → SkillRow
  When the user right-clicks a skill row
  Then `openContextMenuAt(event, skill)` updates the anchor with the cursor coords and the target skill; `<ContextMenu state={...} onAction={handleContextMenuAction}>` renders at the cursor; clicking the "Copy path" item invokes `handleContextMenuAction("copy-path", skill)` which calls `navigator.clipboard.writeText(skill.dir)` AND dispatches a `studio:toast` CustomEvent with `strings.toasts.pathCopied` as the message; unknown actions are silent no-ops; Escape closes the menu (existing ContextMenu contract).
**Files**:
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/hooks/useContextMenuState.ts` (NEW — pure helpers)
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/hooks/__tests__/useContextMenuState.test.ts` (NEW)
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/App.tsx` (state + mount ContextMenu)
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/components/Sidebar.tsx` (thread onContextMenu through SectionList)
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/components/PluginGroup.tsx` (thread to SkillRow)
**Dependencies**: T-041, T-052
**Notes**: Fixes qa-findings #2. The action router lives in a hook-free module (`useContextMenuState.ts`) so it is unit-testable without React; the ContextMenu component itself still owns cursor positioning, keyboard nav, and click-outside-to-close. Open / Reveal / Edit share the existing `strings.actions.editPlaceholder` copy because the full actions land with increment 0675.

---

### T-065: Copy-path action dispatches Toast
**User Story**: US-004 | **Satisfies ACs**: AC-US4-09 | **Status**: [x] completed
**Phase**: 5 | **Estimated**: 0.25h | **Test Level**: component
**Test Plan**:
  Given the DetailHeader copy button is clicked on a skill with `dir="/a/b/c/foo"`
  When the click handler completes
  Then `navigator.clipboard.writeText("/a/b/c/foo")` is invoked; a `studio:toast` CustomEvent is dispatched with `{ message: strings.toasts.pathCopied, severity: "info" }`; the inline "Copied" label still flips for 1.5s (unchanged UX); when the clipboard API throws, an error-severity toast with `strings.toasts.permissionDenied` is dispatched instead.
**Files**:
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/components/DetailHeader.tsx`
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/App.tsx` (listener bridges studio:toast → useToast)
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/components/__tests__/DetailHeader.copy.test.tsx` (NEW)
**Dependencies**: T-026, T-052
**Notes**: Fixes qa-findings #5. A global `studio:toast` CustomEvent listener in App.tsx is the single bridge from hook-free helpers (DetailHeader, MetadataTab entry-chip, context-menu router) to the `useToast()` API — this keeps the helpers test-mode-friendly. The canonical copy lives in `strings.toasts.pathCopied` — "Path copied." per the voice guide.

---

### T-066: Path chip interactivity (clickable chip)
**User Story**: US-003 | **Satisfies ACs**: AC-US3-04 | **Status**: [x] completed
**Phase**: 5 | **Estimated**: 0.25h | **Test Level**: component
**Test Plan**:
  Given the DetailHeader path chip renders with a bordered mono box (carryover from T-026)
  When the user clicks the chip itself (not the adjacent Copy button)
  Then the chip IS a `<button>` with `cursor: pointer`, a descriptive `aria-label` of the form "Copy path <dir> to clipboard", and its `onClick` runs the same `onCopyPath` handler as the Copy button — so clipboard is written, the "Copied" state flips, and the `studio:toast` CustomEvent fires.
**Files**:
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/components/DetailHeader.tsx`
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/components/__tests__/DetailHeader.copy.test.tsx`
**Dependencies**: T-065
**Notes**: Fixes qa-findings #7. The explicit Copy button is preserved as a discoverability affordance — users who prefer a labeled button still have one; users who reflexively click the chip get the expected behaviour.

---

## Deferred ACs (Phase 5 → 0675-skill-md-editor)

The following acceptance criteria from spec.md apply exclusively to the SKILL.md editor (US-005) which is deferred to increment 0675:

- AC-US5-01: Two-pane editor split (editor + preview, resizable, localStorage-persisted)
- AC-US5-02: Live preview with ≤150ms debounce, no flicker, sync scroll toggle
- AC-US5-03: YAML frontmatter parse errors highlighted in gutter with tooltip
- AC-US5-04: Schema validation (required: name, description; optional: model, allowedTools, target-agents); issues strip above editor
- AC-US5-05: allowedTools validated against known-tools allowlist; warnings for unknown tools
- AC-US5-06: Cmd/Ctrl+S saves via eval-server endpoint; dirty-state tracking; save failure toast
- AC-US5-07: Installed skill read-only banner with "Find source" action
- AC-US5-08: Unsaved changes confirm dialog on skill switch
- AC-US5-09: Preview uses existing Markdown/code renderer; theme-aware syntax highlighting
- AC-US5-10: External file-change detection via SSE; reload/keep-editing banner; no silent overwrites

These ACs will be the primary scope of increment 0675. The `E` keyboard shortcut wired in T-037 and T-038 shows a "Not available yet — edit in your file system" placeholder toast in this increment (AC-US4-03 partially satisfied; full editor behavior in 0675).
