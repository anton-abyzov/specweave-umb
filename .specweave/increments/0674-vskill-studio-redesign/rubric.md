---
increment: 0674-vskill-studio-redesign
title: Quality Contract Rubric — vSkill Studio Redesign (Phases 1–4)
scope: Option B (Phases 1-4). Phase 5 ACs deferred to 0675.
generated: 2026-04-22
---

# Rubric: vSkill Studio Redesign (Phases 1–4)

> All criteria start as `[ ] PENDING`. Update to `[x] PASS` or `[-] FAIL` during closure review.
> Blocking criteria must pass before `sw:done` can close the increment.

---

## Functional Correctness — US-001 (Installed/Own Split)

### R-001: OWN and INSTALLED sections are visually distinct [blocking]
- **Source**: AC-US1-01
- **Evaluator**: sw:grill
- **Verify**: Studio renders two sidebar sections separated by a full-width 1px divider; "OWN" appears above, "INSTALLED" below
- **Threshold**: Both section headers and the divider visible in a screenshot without hover
- **Result**: [ ] PENDING

### R-002: Section headers show label, icon, count, and filter affordance [blocking]
- **Source**: AC-US1-02
- **Evaluator**: sw:grill
- **Verify**: Each header shows uppercase kicker label, provenance icon, count badge, and section-scoped filter button
- **Threshold**: All four elements present in both sections
- **Result**: [ ] PENDING

### R-003: classifyOrigin SSoT drives sidebar placement [blocking]
- **Source**: AC-US1-03
- **Evaluator**: sw:grill
- **Verify**: Frontend reads `skill.origin` from API; no path inspection logic in Sidebar or SidebarSection; installed skills appear in INSTALLED, source skills in OWN
- **Threshold**: Code review confirms no `.startsWith(".claude")` or path-based classification in frontend; E2E seeds confirm correct placement
- **Result**: [ ] PENDING

### R-004: Both sections expanded by default [blocking]
- **Source**: AC-US1-04
- **Evaluator**: sw:grill
- **Verify**: On first load with no localStorage state, both OWN and INSTALLED sections render with skills visible (not collapsed)
- **Threshold**: Playwright E2E with cleared storage confirms both expanded
- **Result**: [ ] PENDING

### R-005: Collapse/expand state persists to localStorage [blocking]
- **Source**: AC-US1-05
- **Evaluator**: sw:grill
- **Verify**: Toggling a section header persists state under `vskill-sidebar-own-collapsed` / `vskill-sidebar-installed-collapsed`; reload restores state
- **Threshold**: Playwright reload test passes
- **Result**: [ ] PENDING

### R-006: OWN/INSTALLED rows have distinct hover and selection affordances [blocking]
- **Source**: AC-US1-06
- **Evaluator**: sw:grill
- **Verify**: OWN rows show pencil icon on hover; INSTALLED rows show lock/read-only label; selection uses 1px left border in --accent + --accent-wash tint
- **Threshold**: Visual difference between Own and Installed selected rows is clear in screenshot
- **Result**: [ ] PENDING

### R-007: OWN empty state shows "+ New skill" CTA [blocking]
- **Source**: AC-US1-07
- **Evaluator**: sw:grill
- **Verify**: When zero source skills, OWN section shows copy and CTA rather than hidden/collapsed section
- **Threshold**: Component test with empty source list confirms CTA is rendered and callable
- **Result**: [ ] PENDING

### R-008: INSTALLED empty state shows vskill install snippet [blocking]
- **Source**: AC-US1-08
- **Evaluator**: sw:grill
- **Verify**: When zero installed skills, INSTALLED section shows copy with `vskill install <plugin>` snippet and copy-to-clipboard button
- **Threshold**: Component test confirms text and button presence
- **Result**: [ ] PENDING

### R-009: Search filters within sections, preserves split [blocking]
- **Source**: AC-US1-09
- **Evaluator**: sw:grill
- **Verify**: Search results remain in their origin section; zero-match section shows "No matches in this section" micro-state and remains visible
- **Threshold**: Component test with query that matches only own skills confirms installed section is still visible with micro-state
- **Result**: [ ] PENDING

### R-010: Duplicate-in-both skill shows in both sections [blocking]
- **Source**: AC-US1-10
- **Evaluator**: sw:grill
- **Verify**: A skill with same (plugin, skill) in both own and installed appears in both sections; installed copy shows "synced from Own" link
- **Threshold**: Component test with duplicate fixture confirms two rows and link
- **Result**: [ ] PENDING

### R-011: Skills grouped by plugin within sections, alpha sorted [blocking]
- **Source**: AC-US1-11
- **Evaluator**: sw:grill
- **Verify**: PluginGroup renders within each section; plugins are sorted alphabetically; group header shows plugin name and per-plugin count
- **Threshold**: Component test with 3 plugins confirms alphabetical order
- **Result**: [ ] PENDING

### R-012: Skill row shows name, version pill, benchmark dot, provenance chip [blocking]
- **Source**: AC-US1-12
- **Evaluator**: sw:grill
- **Verify**: Each SkillRow renders name (Inter Tight), optional version pill, benchmark status dot, and — for installed only — agent dir provenance chip in JetBrains Mono
- **Threshold**: SkillRow component test covers all four elements for source and installed variants
- **Result**: [ ] PENDING

### R-013: updateAvailable chip is rendered and keyboard-focusable [blocking]
- **Source**: AC-US1-13
- **Evaluator**: sw:grill
- **Verify**: Installed skills with `updateAvailable: true` show an "Update" chip in --accent; chip has tabIndex and fires update callback on Enter
- **Threshold**: Component test confirms chip presence, color, and keyboard activation
- **Result**: [ ] PENDING

### R-014: Loading state shows static placeholder rows, no shimmer [blocking]
- **Source**: AC-US1-14
- **Evaluator**: sw:grill
- **Verify**: During loading, 3 placeholder rows per section with --bg-hover static fill are shown; no `animation` or `@keyframes shimmer` in DOM; CI check-no-shimmer script passes
- **Threshold**: check-no-shimmer script exits 0; DOM inspection in test confirms no animation
- **Result**: [ ] PENDING

---

## Functional Correctness — US-002 (Light/Dark Themes)

### R-015: Two complete token sets defined in globals.css [blocking]
- **Source**: AC-US2-01
- **Evaluator**: sw:grill
- **Verify**: globals.css under @theme defines all light tokens and [data-theme="dark"] overrides all of them; every raw token in light has a dark counterpart; semantic Layer 2 tokens point at raw
- **Threshold**: Manual audit of globals.css confirms all tokens from ADR-0674-01 are present
- **Result**: [ ] PENDING

### R-016: All text-on-surface contrast pairs meet WCAG AA [blocking]
- **Source**: AC-US2-02
- **Evaluator**: sw:grill
- **Verify**: theme-contrast.test.ts passes in CI; --ink on --paper ≥ 7:1 both themes; --ink-muted ≥ 4.5:1; --installed and --own ≥ 3:1; --focus ≥ 3:1
- **Threshold**: All Vitest contrast assertions pass; no violations
- **Result**: [ ] PENDING

### R-017: Theme toggle is present, cycles 3 states, has correct aria-label [blocking]
- **Source**: AC-US2-03
- **Evaluator**: sw:grill
- **Verify**: StatusBar has a theme toggle button that cycles light → dark → auto; aria-label updates per state; role="button" or native button element
- **Threshold**: Component test covers all three aria-label values
- **Result**: [ ] PENDING

### R-018: Theme persists to localStorage and prevents FOUC [blocking]
- **Source**: AC-US2-04
- **Evaluator**: sw:grill
- **Verify**: setTheme() writes to localStorage; inline script in index.html reads it before React mounts; Playwright E2E confirms data-theme is correct before hydration
- **Threshold**: E2E theme-persistence.spec.ts passes
- **Result**: [ ] PENDING

### R-019: Auto theme responds to OS prefers-color-scheme changes [blocking]
- **Source**: AC-US2-05
- **Evaluator**: sw:grill
- **Verify**: ThemeProvider listens to matchMedia("prefers-color-scheme") change event; changing OS preference in auto mode updates data-theme without reload
- **Threshold**: Unit test mocks matchMedia change event and verifies resolvedTheme updates
- **Result**: [ ] PENDING

### R-020: No hardcoded hex/rgb in component source files [blocking]
- **Source**: AC-US2-06
- **Evaluator**: sw:grill
- **Verify**: ESLint vskill/no-raw-color rule passes on all src/eval-ui/src/**; token sweep cleans workspace pages
- **Threshold**: eslint exits 0 on full codebase scan
- **Result**: [ ] PENDING

### R-021: SVG icons use currentColor; charts use theme tokens [blocking]
- **Source**: AC-US2-07
- **Evaluator**: sw:grill
- **Verify**: Lucide icons render with currentColor fill/stroke; TrendChart and GroupedBarChart reference --text-muted, --border-default etc. for axes/grid
- **Threshold**: Code review confirms no hardcoded colors in icon or chart components
- **Result**: [ ] PENDING

### R-022: Theme transition uses 150ms and skips focused inputs [blocking]
- **Source**: AC-US2-08
- **Evaluator**: sw:grill
- **Verify**: :root transition rule applies background-color 150ms, color 150ms, border-color 150ms; input:focus overrides to transition: none
- **Threshold**: CSS inspection test confirms computed transition values
- **Result**: [ ] PENDING

### R-023: prefers-reduced-motion collapses all animation durations [blocking]
- **Source**: AC-US2-09
- **Evaluator**: sw:grill
- **Verify**: globals.css @media (prefers-reduced-motion: reduce) sets animation: none !important and transition-duration: 0ms !important
- **Threshold**: Unit test mocks reduced-motion and confirms 0ms computed transition
- **Result**: [ ] PENDING

---

## Functional Correctness — US-003 (Detail Panel)

### R-024: Detail panel header shows all required fields [blocking]
- **Source**: AC-US3-01
- **Evaluator**: sw:grill
- **Verify**: DetailHeader renders skill name (Source Serif 4), plugin breadcrumb, origin badge (dot only, no fill), version, updateAvailable notice, certTier, copy-path button
- **Threshold**: Component test with fully-populated skill confirms all elements
- **Result**: [ ] PENDING

### R-025: Frontmatter definition list shows all keys including "More fields" [blocking]
- **Source**: AC-US3-02
- **Evaluator**: sw:grill
- **Verify**: MetadataTab shows name, description, model, allowedTools, target-agents from frontmatter; unknown keys appear in "More fields" collapsible; no key is silently dropped
- **Threshold**: Component test with extended frontmatter fixture confirms all keys present
- **Result**: [ ] PENDING

### R-026: MCP dependencies section is accurate [blocking]
- **Source**: AC-US3-03
- **Evaluator**: sw:grill
- **Verify**: MCP deps section shows server/url/transport/matchedTools per dep with copy snippet button; zero deps shows one-line "No MCP dependencies."
- **Threshold**: Component tests for both populated and empty MCP dep states
- **Result**: [ ] PENDING

### R-027: Skill dependency chips navigate or show "Not installed" [blocking]
- **Source**: AC-US3-04
- **Evaluator**: sw:grill
- **Verify**: Clicking a present dependency chip selects the skill in the sidebar; absent dep shows "Not installed" tooltip
- **Threshold**: Component test covers both cases with mocked sidebar state
- **Result**: [ ] PENDING

### R-028: Filesystem group shows dir, entry, size, lastModified [blocking]
- **Source**: AC-US3-05
- **Evaluator**: sw:grill
- **Verify**: Filesystem section shows absolute dir, SKILL.md entry path, file count, byteSize, lastModified relative + absolute on hover
- **Threshold**: Component test with mocked filesystem data confirms all fields
- **Result**: [ ] PENDING

### R-029: Benchmark group shows status, counts, and run action [blocking]
- **Source**: AC-US3-06
- **Evaluator**: sw:grill
- **Verify**: Benchmark section shows evalCount, assertionCount, benchmarkStatus dot (colored per status), lastBenchmark timestamp, and "Run benchmark" button
- **Threshold**: Component test covers pass/fail/stale/missing benchmarkStatus values
- **Result**: [ ] PENDING

### R-030: Source agent row shown for installed skills only [blocking]
- **Source**: AC-US3-07
- **Evaluator**: sw:grill
- **Verify**: Installed skills show "Source agent" row with dir and agent display name from AGENTS_REGISTRY; own skills do not show this row
- **Threshold**: Component test for both origins confirms presence/absence
- **Result**: [ ] PENDING

### R-031: VersionHistoryPanel accessible from Versions tab [blocking]
- **Source**: AC-US3-08
- **Evaluator**: sw:grill
- **Verify**: Versions tab in RightPanel renders existing VersionHistoryPanel; tab switching does not lose selection; tab bar uses underline indicator not pill tabs
- **Threshold**: Component test confirms tab rendering and content switching
- **Result**: [ ] PENDING

### R-032: Missing fields show neutral placeholder [blocking]
- **Source**: AC-US3-09
- **Evaluator**: sw:grill
- **Verify**: Null/undefined skill fields render as "—" in --text-faint; no raw "null", "undefined", or empty string visible
- **Threshold**: Component test with all-null optional fields confirms placeholder rendering
- **Result**: [ ] PENDING

### R-033: Long paths use tooltip; long arrays wrap chips [blocking]
- **Source**: AC-US3-10
- **Evaluator**: sw:grill
- **Verify**: Dir paths that exceed container width truncate with ellipsis and show full value in tooltip on hover; allowedTools with > 5 entries wraps to multiple lines of chips
- **Threshold**: Component test at 1280px confirms tooltip trigger for long path; chip wrap for large arrays
- **Result**: [ ] PENDING

---

## Functional Correctness — US-004 (Developer Efficiency)

### R-034: / and Cmd+K focus search; Escape clears and blurs [blocking]
- **Source**: AC-US4-01
- **Evaluator**: sw:grill
- **Verify**: Pressing "/" focuses sidebar search; Cmd+K opens command palette; Escape in search clears and blurs; Escape in palette closes it
- **Threshold**: Playwright keyboard-shortcuts.spec.ts passes
- **Result**: [ ] PENDING

### R-035: j/k navigate across sections, Enter opens skill [blocking]
- **Source**: AC-US4-02
- **Evaluator**: sw:grill
- **Verify**: j/↓ moves selection forward across both sections skipping headers; k/↑ moves backward; Enter opens the focused skill in detail panel
- **Threshold**: Component test with 5 skills in 2 sections confirms traversal order
- **Result**: [ ] PENDING

### R-036: E key invokes Edit action (own = editor placeholder, installed = read-only notice) [blocking]
- **Source**: AC-US4-03
- **Evaluator**: sw:grill
- **Verify**: Pressing E with an own skill selected shows "edit" action (placeholder toast in this increment); with installed skill shows read-only toast "Installed skills are read-only."
- **Threshold**: E2E or component test confirms different behaviors per origin
- **Result**: [ ] PENDING

### R-037: R/C/D/U shortcuts invoke correct actions [blocking]
- **Source**: AC-US4-04
- **Evaluator**: sw:grill
- **Verify**: R invokes run benchmark; C copies path with "Path copied." toast; D duplicates own skill; U triggers update on installed with updateAvailable=true
- **Threshold**: Component tests for each shortcut confirm callback invocation
- **Result**: [ ] PENDING

### R-038: ? opens keyboard cheatsheet modal with correct content and a11y [blocking]
- **Source**: AC-US4-05
- **Evaluator**: sw:grill
- **Verify**: ? key opens ShortcutModal; modal lists all shortcuts in Navigation/Actions/Theme groups; role="dialog" aria-modal="true"; Escape closes and returns focus; Tab cycles through modal only
- **Threshold**: Component test + Playwright E2E confirm open, content, close behavior
- **Result**: [ ] PENDING

### R-039: Search updates within 80ms for ≤500 skills [blocking]
- **Source**: AC-US4-06
- **Evaluator**: sw:grill
- **Verify**: Typing in SidebarSearch with 500-skill fixture shows results within 80ms (measured via performance.mark); fuzzy matching covers skill name, plugin, dir; exact-prefix matches rank first
- **Threshold**: Performance test or benchmarked unit test confirms ≤80ms at 500 skills
- **Result**: [ ] PENDING

### R-040: Context menu exposes correct actions per origin [blocking]
- **Source**: AC-US4-07
- **Evaluator**: sw:grill
- **Verify**: Right-click on own skill shows Open/CopyPath/Reveal/Edit/Duplicate/RunBenchmark; on installed+updateAvailable shows Open/CopyPath/Reveal/RunBenchmark/Update/Uninstall; keyboard navigation works in menu
- **Threshold**: Component test for both origin variants and updateAvailable states
- **Result**: [ ] PENDING

### R-041: Toasts appear in bottom-right, auto-dismiss 4s, queue vertically [blocking]
- **Source**: AC-US4-08
- **Evaluator**: sw:grill
- **Verify**: Toast fires on path copy, benchmark start etc.; appears bottom-right; dismissed after 4s or via Escape; multiple toasts stack vertically; aria-live="polite" for success, "assertive" for error
- **Threshold**: Component test covers single and multiple toast scenarios
- **Result**: [ ] PENDING

### R-042: Cmd+B toggles sidebar visibility [blocking]
- **Source**: AC-US4-09
- **Evaluator**: sw:grill
- **Verify**: Cmd+B (or Ctrl+B) hides sidebar; pressing again shows it; Playwright keyboard-shortcuts.spec.ts covers this
- **Threshold**: E2E passes
- **Result**: [ ] PENDING

---

## Functional Correctness — US-006 (Empty/Error States)

### R-043: Fresh workspace shows master empty state with both CTAs [blocking]
- **Source**: AC-US6-01
- **Evaluator**: sw:grill
- **Verify**: Studio with zero skills shows headline "No skills yet", "Create a skill" and "Install from registry" buttons, and docs link; sidebar shows both section headers with count (0) and per-section empty microcopy
- **Threshold**: Component test with empty skills array confirms all elements
- **Result**: [ ] PENDING

### R-044: Scan failure shows error card with retry [blocking]
- **Source**: AC-US6-03
- **Evaluator**: sw:grill
- **Verify**: API error response triggers error card in sidebar with icon, short message, full error in <details>, and Retry button; no white screen
- **Threshold**: Component test with mocked API error confirms error card
- **Result**: [ ] PENDING

### R-045: SKILL.md load failure shows error state in detail panel [blocking]
- **Source**: AC-US6-04
- **Evaluator**: sw:grill
- **Verify**: Selecting a skill whose SKILL.md fails shows error state with file name, "Open in editor" action, "Copy path" action; sidebar remains usable
- **Threshold**: Component test with mocked SKILL.md load error
- **Result**: [ ] PENDING

### R-046: Network errors show inline retry; ErrorBoundary prevents white screen [blocking]
- **Source**: AC-US6-05
- **Evaluator**: sw:grill
- **Verify**: Failed model-list or benchmark fetch shows inline error with Retry button; ErrorBoundary wraps workspace root; throwing inside workspace does not crash the sidebar
- **Threshold**: Component test with thrown error inside workspace confirms ErrorBoundary catches it
- **Result**: [ ] PENDING

### R-047: SSE disconnect banner shows and auto-dismisses on reconnect [blocking]
- **Source**: AC-US6-06
- **Evaluator**: sw:grill
- **Verify**: SSE close event triggers "Disconnected — reconnecting…" banner with live indicator; banner disappears when SSE reconnects
- **Threshold**: Component test mocking SSE events confirms banner lifecycle
- **Result**: [ ] PENDING

---

## Functional Correctness — US-007 (Responsive Layout)

### R-048: Desktop layout 1280px+ uses correct column widths [blocking]
- **Source**: AC-US7-01
- **Evaluator**: sw:grill
- **Verify**: At 1280px, sidebar is 320px and main fills 1fr; at ≥1600px, detail panel can use 2-column inner layout
- **Threshold**: Component test at mocked 1280px and 1600px viewports confirms grid dimensions
- **Result**: [ ] PENDING

### R-049: Tablet layout 768–1279px narrows sidebar to 240px [blocking]
- **Source**: AC-US7-02
- **Evaluator**: sw:grill
- **Verify**: At 900px viewport, sidebar is 240px; detail panel switches to single-column inner layout
- **Threshold**: Component test at 900px confirms sidebar width
- **Result**: [ ] PENDING

### R-050: Mobile <768px sidebar is drawer [blocking]
- **Source**: AC-US7-03
- **Evaluator**: sw:grill
- **Verify**: At 600px viewport, sidebar is hidden; hamburger button visible; clicking hamburger opens full-height overlay drawer; main area fills viewport
- **Threshold**: Component test at 600px confirms sidebar is not in grid flow
- **Result**: [ ] PENDING

### R-051: Sidebar drag resize persists to localStorage [blocking]
- **Source**: AC-US7-05
- **Evaluator**: sw:grill
- **Verify**: Dragging ResizeHandle adjusts --sidebar-width within [240px, 480px]; width persists to localStorage "vskill-sidebar-width" on mouseup
- **Threshold**: ResizeHandle component test confirms clamping and localStorage write
- **Result**: [ ] PENDING

---

## Functional Correctness — US-008 (Accessibility)

### R-052: Zero axe-core serious/critical violations in both themes [blocking]
- **Source**: AC-US8-01
- **Evaluator**: sw:grill
- **Verify**: a11y.test.tsx runs axe.run() against full layout in light and dark; violations of impact "serious" or "critical" = 0
- **Threshold**: Test passes with zero violations in both theme renders
- **Result**: [ ] PENDING

### R-053: All interactive elements have accessible names [blocking]
- **Source**: AC-US8-02
- **Evaluator**: sw:grill
- **Verify**: Every button, link, input, section toggle, skill card, theme toggle has aria-label, aria-labelledby, or text content discernible to AT
- **Threshold**: axe-core "button-name" and "label" rules pass; manual spot-check of 5 elements
- **Result**: [ ] PENDING

### R-054: Focus-visible rings are 2px --border-focus, ≥3:1 contrast [blocking]
- **Source**: AC-US8-03
- **Evaluator**: sw:grill
- **Verify**: :focus-visible shows 2px outline in var(--border-focus); mouse click does not show ring; [data-contrast="more"] widens to 3px; focus ring contrast ≥ 3:1
- **Threshold**: focus-ring.test.tsx passes; --focus color verified against surrounding background
- **Result**: [ ] PENDING

### R-055: Section headers and groups have correct ARIA structure [blocking]
- **Source**: AC-US8-04
- **Evaluator**: sw:grill
- **Verify**: OWN and INSTALLED headers use role="heading" aria-level="2"; skill lists below use role="group" with aria-labelledby pointing to the section header
- **Threshold**: DOM inspection in a11y test confirms heading roles and group labeling
- **Result**: [ ] PENDING

### R-056: aria-live regions announce selection and errors [blocking]
- **Source**: AC-US8-05, AC-US8-07
- **Evaluator**: sw:grill
- **Verify**: Selecting a skill updates aria-live="polite" region with "Viewing <name> (Own/Installed)"; error toasts use aria-live="assertive"; success toasts use aria-live="polite"
- **Threshold**: a11y-live-regions.test.tsx passes
- **Result**: [ ] PENDING

### R-057: Modals trap focus and restore on close [blocking]
- **Source**: AC-US8-06
- **Evaluator**: sw:grill
- **Verify**: ShortcutModal, CommandPalette, ContextMenu trap Tab focus inside; Escape closes and focus returns to trigger; role="dialog" aria-modal="true" on modal containers
- **Threshold**: Component tests for each modal confirm focus trap and restore
- **Result**: [ ] PENDING

### R-058: High-contrast variant activated via prefers-contrast [blocking]
- **Source**: AC-US8-09
- **Evaluator**: sw:grill
- **Verify**: When prefers-contrast: more, data-contrast="more" is set on <html>; [data-contrast="more"] tokens thicken rule borders and widen focus rings; contrast re-verified
- **Threshold**: high-contrast.test.ts passes
- **Result**: [ ] PENDING

---

## Functional Correctness — US-009 (Performance Budget)

### R-059: FCP ≤ 800ms, TTI ≤ 1500ms [blocking]
- **Source**: AC-US9-01
- **Evaluator**: sw:grill
- **Verify**: Lighthouse CI (vite preview mode) reports FCP ≤ 800ms and TTI ≤ 1500ms for a workspace with ≤100 skills
- **Threshold**: Lighthouse performance score passes configured thresholds
- **Result**: [ ] PENDING

### R-060: Sidebar virtualizes for ≥200 skills, scroll ≥50fps [blocking]
- **Source**: AC-US9-02
- **Evaluator**: sw:grill
- **Verify**: With 250 skills, DOM contains far fewer than 250 row nodes; react-virtuoso renders; Chrome perf panel shows scroll FPS ≥ 50
- **Threshold**: Component DOM node count test + performance.spec.ts passes
- **Result**: [ ] PENDING

### R-061: Initial bundle ≤ 250KB gzipped [blocking]
- **Source**: AC-US9-05
- **Evaluator**: sw:grill
- **Verify**: check-bundle-size.ts reports initial chunk ≤ 250KB gzipped; fonts chunk ≤ 70KB; lazy chunks (CommandPalette, ShortcutModal) each ≤ 150KB
- **Threshold**: check:bundle script exits 0
- **Result**: [ ] PENDING

---

## Functional Correctness — US-010 (Copy Voice)

### R-062: All empty states follow "declarative sentence. Concrete next step." pattern [blocking]
- **Source**: AC-US10-01
- **Evaluator**: sw:grill
- **Verify**: Own empty → "No skills yet. Add one from the marketplace or point Studio at a folder."; Installed empty → "No installed skills. Run `vskill install <plugin>`..."; no "Oops", "Let's get started", or "Welcome!" copy anywhere
- **Threshold**: strings-voice.test.ts passes; manual audit of 5 empty states
- **Result**: [ ] PENDING

### R-063: Error states name failure, cause, and remediation [blocking]
- **Source**: AC-US10-02
- **Evaluator**: sw:grill
- **Verify**: Error copy names what failed in plain language and offers remediation; no blame language, no "Oops", no emoji, no exclamation marks
- **Threshold**: strings-voice.test.ts passes; manual audit of 3 error strings
- **Result**: [ ] PENDING

### R-064: Loading states are declarative and present-tense [blocking]
- **Source**: AC-US10-03
- **Evaluator**: sw:grill
- **Verify**: Loading copy uses "Scanning workspace…" not "Please wait…"; no filler phrases
- **Threshold**: strings.ts contains no "Please wait", "Just a moment", or "Working hard"
- **Result**: [ ] PENDING

### R-065: Success toasts ≤4 words, end with period [blocking]
- **Source**: AC-US10-04
- **Evaluator**: sw:grill
- **Verify**: Success strings are "Saved obsidian-brain.", "Installed 3 skills.", "Benchmark complete." — ≤5 words, period-terminated, no "Success!", no emoji
- **Threshold**: strings-voice.test.ts word-count assertion passes for all action strings
- **Result**: [ ] PENDING

### R-066: CI voice gate blocks banned patterns in strings.ts [blocking]
- **Source**: AC-US10-06
- **Evaluator**: sw:grill
- **Verify**: check-strings-voice.ts script exits non-zero when any banned pattern is present; exits 0 on clean strings.ts; lint:strings wired in CI
- **Threshold**: Script self-test (introduce banned word, confirm exit 1; remove it, confirm exit 0)
- **Result**: [ ] PENDING

---

## Infrastructure Criteria

### R-067: Test coverage ≥90% line for new/modified components [blocking]
- **Source**: NFR-003
- **Evaluator**: sw:grill
- **Verify**: Vitest --coverage report shows ≥90% line coverage for all new components (ThemeProvider, Sidebar, SidebarSection, SkillRow, ProvenanceChip, PluginGroup, SidebarSearch, MetadataTab, StatusBar, TopRail, ResizeHandle, ContextMenu, CommandPalette, ShortcutModal, strings.ts)
- **Threshold**: Coverage report passes 90% threshold; no new file below 80%
- **Result**: [ ] PENDING

### R-068: CI scripts all pass (shimmer, serif-scope, voice, bundle, contrast) [blocking]
- **Source**: NFR-001, NFR-004
- **Evaluator**: sw:grill
- **Verify**: check-no-shimmer.ts, check-serif-scope.ts, check-strings-voice.ts, check-bundle-size.ts, and theme-contrast.test.ts all exit 0 in CI
- **Threshold**: All scripts pass in a clean build
- **Result**: [ ] PENDING

### R-069: No deprecated components referenced (LeftPanel, SkillCard, SkillGroupList deleted) [blocking]
- **Source**: FR-006
- **Evaluator**: sw:grill
- **Verify**: LeftPanel.tsx, SkillCard.tsx, SkillGroupList.tsx are deleted; no remaining import references them in any file
- **Threshold**: `grep -r "LeftPanel\|SkillCard\|SkillGroupList" src/eval-ui/src/` returns no matches
- **Result**: [ ] PENDING

### R-070: Existing eval-ui tests pass with no regressions [blocking]
- **Source**: NFR-003
- **Evaluator**: sw:grill
- **Verify**: Full Vitest run shows no newly failing tests; existing test files for benchmark, sweep, model-compare, version-history pass unchanged
- **Threshold**: vitest run exits 0 with all pre-existing tests green
- **Result**: [ ] PENDING

### R-071: Playwright E2E suite passes end-to-end [blocking]
- **Source**: NFR-003
- **Evaluator**: sw:grill
- **Verify**: sidebar-split.spec.ts, skill-detail-capture.spec.ts, keyboard-shortcuts.spec.ts, theme-persistence.spec.ts, performance.spec.ts all pass in Playwright CI run
- **Threshold**: npx playwright test exits 0 with all specs green
- **Result**: [ ] PENDING

---

> **Review note**: rubric.md has been generated. Review and customize criteria before implementation begins.
> You may change severity (add `[blocking]` / `[non-blocking]`), add project-specific criteria, or remove criteria that do not apply to your environment.
