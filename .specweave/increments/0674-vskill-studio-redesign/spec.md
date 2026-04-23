---
increment: 0674-vskill-studio-redesign
title: >-
  vSkill Studio Redesign — Developer-First UI with Installed/Own Split and
  Light+Dark Themes
type: feature
priority: P1
status: completed
created: 2026-04-22T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: vSkill Studio Redesign — Developer-First UI with Installed/Own Split and Light+Dark Themes

## Overview

Redesign the vSkill NPM Studio — the interactive SPA served by `npx vskill studio` — to be the fastest, sleekest, most information-dense skill workbench for developers. The redesign delivers four headline outcomes:

1. **Installed vs Own split (the central requirement)** — the left sidebar is reorganised into two visually distinct sections: **Installed** (skills living under `.claude/` and equivalent agent config dirs) and **Own** (skills the user authors in their source tree, outside any agent config dir). Provenance is communicated at a glance, not buried under a collapsed accordion.
2. **First-class light and dark themes** — both themes are equally polished. No "dark-mode only" treatment and no "light mode as afterthought." Theme is toggleable, persistent, and follows the OS preference on first load.
3. **Every skill detail captured** — a detail panel surfaces every piece of metadata a developer cares about (name, plugin, version, cert tier, provenance path, frontmatter, dependencies, entry point, last-modified, benchmark status, update availability) without clutter.
4. **Developer-first ergonomics** — keyboard-first navigation, instant fuzzy search, quick actions (install/uninstall/edit/open-in-editor/duplicate/copy-path), SKILL.md live preview with frontmatter validation, and sub-second interaction budgets.

## Code Location & Scope

**Target codebase:** `repositories/anton-abyzov/vskill/src/eval-ui/` — the Vite + React SPA served by `npx vskill studio`. Supporting API changes land in `repositories/anton-abyzov/vskill/src/eval-server/` as needed.

**Not in scope:** `repositories/anton-abyzov/vskill-platform/src/app/studio/page.tsx` is the marketing landing page and is **out of scope** for this redesign. It may be updated separately.

**Existing building blocks** (redesign, do not rebuild):
- `SkillInfo.origin: "source" | "installed"` already exists in `src/eval-ui/src/types.ts` and is populated by `classifyOrigin()` in `src/eval/skill-scanner.ts` (detects `.claude`, `.cursor`, `.specweave`, `.vscode`, `.idea`, `.zed`, `.devcontainer`, `.github`, `.agents`, `.agent`, and `plugins/cache/`). The redesign *uses* this classification and elevates it visually — no scanner rewrite.
- `StudioContext.tsx`, `ConfigContext.tsx`, `LeftPanel.tsx`, `SkillGroupList.tsx`, `SkillCard.tsx`, `RightPanel.tsx` exist. Treat them as the refactor surface.
- `src/eval-ui/src/styles/globals.css` holds dark-only CSS variables today — extend with a `[data-theme="light"]` token set and a theme provider.

## Personas

- **P1 — Skill Author** (primary): a developer authoring their own SKILL.md files and evals in a project tree. Lives in the **Own** section. Wants editor affordances, frontmatter validation, instant preview, keyboard shortcuts.
- **P2 — Skill Consumer**: a developer who installs third-party skills via `vskill install` / `claude plugin install`. Lives in the **Installed** section. Wants to read, test, and update — never edit in place.
- **P3 — Skill Reviewer**: a teammate inspecting a skill before approving it (security scan result, dependencies, eval pass rate). Needs the detail panel to be information-dense.

## User Stories

### US-001: Installed vs Own Sidebar Split (P1)
**Project**: vskill-platform

**As a** skill author working alongside installed third-party skills
**I want** the left sidebar to show Installed skills and my Own skills in two clearly separated sections with unmistakable visual distinction
**So that** I can instantly tell which files I can edit versus which are read-only consumed copies, and I never accidentally edit an installed skill

**Acceptance Criteria**:
- [x] **AC-US1-01**: Given the studio is loaded with at least one source skill and one installed skill, when the left sidebar renders, then two distinct sections are visible — "Own" above and "Installed" below — separated by a full-width horizontal divider of at least 1px using `var(--border-default)`.
- [x] **AC-US1-02**: Given both sections have content, when the sidebar renders, then each section header displays: (a) a section label in uppercase small-caps ("OWN" / "INSTALLED"), (b) an icon distinguishing provenance (e.g., folder icon for Own, lock/download icon for Installed), (c) a count badge showing the number of skills in that section, and (d) a section-scoped filter affordance.
- [x] **AC-US1-03**: Given a skill's `dir` path, when `classifyOrigin(dir, root)` returns `"installed"`, then it appears in the Installed section; when it returns `"source"`, it appears in the Own section. The classification rule — any skill whose path, relative to project root, has a first segment matching `.claude`, `.cursor`, `.specweave`, `.vscode`, `.idea`, `.zed`, `.devcontainer`, `.github`, `.agents`, `.agent`, or contains `plugins/cache/` — is the single source of truth and must match `src/eval/skill-scanner.ts#classifyOrigin`.
- [x] **AC-US1-04**: Given the Own section has skills, when it renders, then it is **expanded by default** (not collapsed). Given the Installed section has skills, when it renders, then it is **expanded by default** — the current pattern of collapsing Installed under a disclosure button is removed; both sections are equally first-class.
- [x] **AC-US1-05**: Given a user toggles a section header, when clicked, then that section collapses/expands and the state persists across reloads in `localStorage` (keys: `vskill-sidebar-own-collapsed`, `vskill-sidebar-installed-collapsed`, both default `false`).
- [x] **AC-US1-06**: Given a skill is in the Own section, when hovered or selected, then its card background uses a subtle accent tint (`var(--accent-muted)`) and shows an "editable" affordance (pencil icon or "Edit" quick action). Given a skill is in the Installed section, when hovered or selected, then its card shows a "read-only" affordance (lock icon or "Read-only" micro-label) — the visual language is different enough that a screenshot alone communicates provenance.
- [x] **AC-US1-07**: Given the Own section is empty (zero source skills), when rendered, then it shows an explicit empty state with CTA "+ New skill" wired to the existing create flow — not a hidden or missing section.
- [x] **AC-US1-08**: Given the Installed section is empty (zero installed skills), when rendered, then it shows an explicit empty state with microcopy "No installed skills. Run `vskill install <plugin>` or `claude plugin install <plugin>` to add one." and a copy-to-clipboard button for the snippet.
- [x] **AC-US1-09**: Given a search query is entered, when skills are filtered, then matches are shown within their respective section (Installed matches in Installed, Own matches in Own). When a section has zero matches for the query, it renders a "No matches in this section" micro-state and remains visible (not hidden) so the split is preserved.
- [x] **AC-US1-10**: Given a skill exists both as source (user is authoring it) **and** as installed (compiled copy in `.claude/`), when the sidebar renders, then it appears in **both** sections as separate cards — the Own card is marked primary; the Installed card displays a small "synced from Own" link that, when clicked, selects the Own card. No de-duplication is performed silently.
- [x] **AC-US1-11**: Given skills within a section, when rendered, they are grouped by `plugin` using the existing `PluginGroupHeader` component, with the plugin name and per-plugin count visible; groups are sorted alphabetically by plugin name.
- [x] **AC-US1-12**: Given a skill card, when rendered, it displays (within the sidebar): skill name, optional version pill, benchmark status dot (pass/fail/stale/missing), and — only for Installed — the source agent directory label (`.claude` / `.cursor` / etc.) as a 10px caption so the user sees provenance without opening the detail panel.
- [x] **AC-US1-13**: Given an Installed skill card has `updateAvailable === true`, when rendered, then it shows a subtle "Update" chip in the accent color; the chip is keyboard-focusable and triggers the update flow.
- [x] **AC-US1-14**: Given the user runs the studio in a workspace where scanning takes >150ms, when skills are loading, then each section shows 3 skeleton placeholders with a shimmer animation; skeletons appear within 16ms of the load starting (no flash of empty content).

---

### US-002: Light & Dark Themes with Persistence (P1)
**Project**: vskill-platform

**As a** developer who switches between bright offices and dim rooms
**I want** a polished light theme that is equal to the dark theme, a one-click toggle, persistence across sessions, and an honest default that follows my OS
**So that** the studio is comfortable to use at any time of day without eye strain

**Acceptance Criteria**:
- [x] **AC-US2-01**: Given `globals.css`, when the studio ships, then it defines **two complete token sets**: `:root` (dark, current) and `[data-theme="light"]` (new) — every token in dark has a counterpart in light: surfaces 0–4, borders (subtle/default/hover/active), text (primary/secondary/tertiary), accent (+hover, +muted), semantic colors (green/red/yellow/orange/purple + muted variants).
- [x] **AC-US2-02**: Given the light theme tokens, when measured, then all text-on-surface pairings meet WCAG 2.1 AA contrast: `--text-primary` on `--surface-0` ≥ 7:1 (AAA body), `--text-secondary` on `--surface-1` ≥ 4.5:1, `--text-tertiary` on `--surface-1` ≥ 3:1 (captions/pills only). The same contrast floors apply to dark theme.
- [x] **AC-US2-03**: Given the studio top bar, when rendered, then a theme toggle button (sun/moon icon) is present with `aria-label="Switch to {light|dark} theme"` and `role="button"`. Clicking it cycles `data-theme` on `<html>` between `dark` and `light`. A third "Auto" state follows `prefers-color-scheme`.
- [x] **AC-US2-04**: Given the user selects a theme, when the selection changes, then it persists to `localStorage` under key `vskill-theme` with value `"dark" | "light" | "auto"`. On next load, the stored value is applied before first paint (inline script in `index.html` or root layout) to prevent FOUC.
- [x] **AC-US2-05**: Given the stored theme is `"auto"` (default on first install), when the OS `prefers-color-scheme` changes, then the studio reacts via `matchMedia("(prefers-color-scheme: dark)").addEventListener("change", ...)` and updates `data-theme` in place with no reload.
- [x] **AC-US2-06**: Given any existing component uses hardcoded colors (hex, rgb, named colors), when the redesign lands, then those are replaced with CSS variables. Specifically: no `#xxxxxx`, no `rgb(...)`, no `rgba(...)` with hardcoded RGB values outside `globals.css`. ESLint rule or CI grep enforces this. (Acceptable exceptions: `rgba(0,0,0,*)` for shadows only.)
- [x] **AC-US2-07**: Given images, icons, and syntax highlighting, when the theme is switched, then they remain legible in both themes — SVG icons use `currentColor`, code blocks use a theme-aware syntax scheme (e.g., GitHub-light / GitHub-dark or equivalent mapped to tokens), charts (TrendChart, GroupedBarChart) use theme tokens for axes/grid.
- [x] **AC-US2-08**: Given the theme toggle is activated, when the transition occurs, then background, text, and borders transition with `transition: background-color 150ms, color 150ms, border-color 150ms` for visual polish. No transition is applied to components mid-interaction (e.g., focused input) — the transition uses `:root` scope and respects `prefers-reduced-motion: reduce`.
- [x] **AC-US2-09**: Given a user prefers reduced motion, when `prefers-reduced-motion: reduce` is set, then all fade/slide/scale animations in the studio are reduced to ≤100ms or removed, and theme transitions are instant.

---

### US-003: Skill Detail Panel — Exhaustive Metadata (P1)
**Project**: vskill-platform

**As a** skill author or reviewer
**I want** the right panel to show every relevant detail of the selected skill without hiding anything behind extra clicks
**So that** I can audit, debug, and iterate without context-switching to a file explorer or terminal

**Acceptance Criteria**:
- [x] **AC-US3-01**: Given a skill is selected, when the detail panel renders, then the header displays: skill name (H1), plugin name (breadcrumb-style prefix), origin badge ("Own" / "Installed"), current version, latest available version (if `updateAvailable`), pinned version (if present), cert tier pill, and a copy-path button that copies the absolute `dir` to clipboard.
- [x] **AC-US3-02**: Given a skill has a SKILL.md, when the "Overview" tab renders, then it shows the parsed frontmatter as a definition list: `name`, `description`, `model` (if set), `allowedTools`, `target-agents` (if set), plus any other frontmatter keys in a "More fields" collapsible row — no frontmatter key is silently dropped.
- [x] **AC-US3-03**: Given the skill has MCP dependencies (from `McpDependencies` parsing), when the Overview tab renders, then a "MCP Dependencies" section lists each dependency with `server`, `url`, `transport`, `matchedTools`, and a "Copy config snippet" button; if zero, the section shows a one-line "No MCP dependencies".
- [x] **AC-US3-04**: Given the skill has body-referenced or frontmatter-declared skill dependencies (`SkillDependencyInfo[]`), when the Overview tab renders, then they appear as clickable chips; clicking navigates to the referenced skill in the sidebar if present, or shows a "Not installed" tooltip if absent.
- [x] **AC-US3-05**: Given a skill, when the Overview tab renders, then a "Filesystem" group displays: absolute `dir` path, `entry point` (SKILL.md path), total file count, size on disk, and `last-modified` timestamp (relative + absolute on hover).
- [x] **AC-US3-06**: Given a skill, when the Overview tab renders, then a "Benchmark" group shows: `evalCount`, `assertionCount`, `benchmarkStatus` with colored dot (pass/fail/stale/pending/missing), `lastBenchmark` timestamp, and a "Run benchmark" primary action.
- [x] **AC-US3-07**: Given a skill is in the Installed section, when the detail panel renders, then a "Source agent" row shows the detected agent directory (`.claude/skills/...` or `.cursor/...` etc.) and the agent display name resolved from `AGENTS_REGISTRY`.
- [x] **AC-US3-08**: Given a skill has multiple versions in the version history store, when the detail panel renders, then a "Versions" tab shows the existing `VersionHistoryPanel` with pinned-version highlighting and cert-score comparison.
- [x] **AC-US3-09**: Given any metadata field is missing or null, when rendered, then a neutral "—" placeholder is shown with `var(--text-tertiary)` — never a raw `null`, `undefined`, or empty string.
- [x] **AC-US3-10**: Given the detail panel in either theme, when rendered on a screen ≥1280px wide, then no metadata is truncated silently — long paths use a tooltip showing the full value on hover; long arrays (e.g., allowedTools) wrap to multiple chips.

---

### US-004: Developer-Efficiency Workflows (P1)
**Project**: vskill-platform

**As a** developer using the studio dozens of times a day
**I want** keyboard shortcuts, instant search, and one-click quick actions
**So that** I stay in flow and the studio never feels slower than the terminal

**Acceptance Criteria**:
- [x] **AC-US4-01**: Given the studio is focused, when the user presses `Cmd/Ctrl+K` (or `/`), then the sidebar search input receives focus and selects its existing text; pressing `Escape` while focused clears the query and blurs.
- [x] **AC-US4-02**: Given the sidebar has skills, when the user presses `↑`/`↓`, then the selection moves between skill cards across both Own and Installed sections; `Enter` opens the selected skill in the detail panel. Section headers are skipped, not focusable as selections.
- [x] **AC-US4-03**: Given a skill is selected in the detail panel, when the user presses `E`, then the "Edit SKILL.md" action is invoked (opens the inline editor for Own skills; shows a read-only banner for Installed skills).
- [x] **AC-US4-04**: Given a skill is selected, when the user presses `R`, then "Run benchmark" is invoked; when the user presses `C`, then "Copy path" is invoked; when the user presses `D`, then "Duplicate skill" is invoked (source skills only); when the user presses `U`, then "Update" is invoked for Installed skills with `updateAvailable`.
- [x] **AC-US4-05**: Given the user presses `?` with the studio focused, when handled, then a keyboard-shortcut cheat sheet modal opens listing every shortcut, grouped by category (Navigation / Actions / Theme). The modal is dismissable with `Escape` and is keyboard-navigable.
- [x] **AC-US4-06**: Given search input contains a query, when the user types, then results update within 80ms for workspaces with ≤500 skills; fuzzy matching applies across `skill`, `plugin`, and the first paragraph of frontmatter `description`; results are ranked by match quality with exact-prefix matches first.
- [x] **AC-US4-07**: Given the user right-clicks (or long-presses on touch) a skill card, when the context menu opens, then it exposes: Open, Copy Path, Reveal in Editor (invokes OS-appropriate open command via existing server endpoint), Edit (Own only), Duplicate, Run Benchmark, Uninstall (Installed only), Delete (Own only, with confirm).
- [x] **AC-US4-08**: Given a toast/notification fires (success, error, info), when shown, then it appears in the bottom-right with a 4s auto-dismiss, is keyboard-dismissable with `Escape`, queues multiple toasts vertically, and respects reduced motion.
- [x] **AC-US4-09**: Given the studio window has focus and the user has the sidebar collapsed on narrow widths, when they press `Cmd/Ctrl+B`, then the sidebar toggles visibility.
- [x] **AC-US4-10**: Given all quick actions, when invoked, then an optimistic UI updates immediately; backend confirms within 500ms or a rollback toast fires with a "Retry" action.

---

### US-005: SKILL.md Editor, Preview, and Frontmatter Validation (P1) — DEFERRED TO 0675

> **Scope decision (2026-04-22)**: Option B selected for 0674. Phase 5 (SKILL.md editor) deferred in full to **0675-skill-md-editor** (reserved increment). ACs below are preserved for traceability and will be re-scoped there. They are **not** part of 0674 closure.

**Project**: vskill-platform

**As a** skill author iterating on SKILL.md
**I want** a focused editor with live preview and inline frontmatter validation
**So that** I catch schema mistakes before running an eval and see how my skill reads without leaving the studio

**Acceptance Criteria (DEFERRED → 0675)**:
> - **AC-US5-01** (DEFERRED → 0675): Given an Own skill is selected and the user clicks "Edit" (or presses `E`), when the editor opens, then it renders a two-pane split: left = monospace Markdown editor with syntax highlighting, right = rendered SKILL.md preview. The split is resizable with a draggable divider; position persists to `localStorage`.
> - **AC-US5-02** (DEFERRED → 0675): Given the editor is focused, when the user types, then the preview updates with ≤150ms debounce; no preview flicker; both panes scroll independently with a "sync scroll" toggle available.
> - **AC-US5-03** (DEFERRED → 0675): Given the user edits frontmatter, when the YAML parses cleanly, then a "Valid" indicator is shown; when the YAML is malformed, then the gutter highlights the offending line with a red marker and an error tooltip describing the parse error.
> - **AC-US5-04** (DEFERRED → 0675): Given the frontmatter parses, when validated against the SKILL.md schema (required: `name`, `description`; optional: `model`, `allowedTools`, `target-agents`), then missing required fields are flagged as errors and unknown fields as warnings — both surface in a compact issues strip above the editor.
> - **AC-US5-05** (DEFERRED → 0675): Given `allowedTools` is present, when validated, then each tool name is checked against a known-tools allowlist (Read, Write, Edit, Glob, Grep, Bash, WebFetch, WebSearch, and registered MCP tools); unknown tool names show a warning "Unknown tool — will be ignored at runtime."
> - **AC-US5-06** (DEFERRED → 0675): Given the user saves (Cmd/Ctrl+S), when the save succeeds, then a toast confirms "Saved <skill>" and the file on disk is written via the existing eval-server endpoint; when the save fails, the toast shows the error and the editor stays dirty.
> - **AC-US5-07** (DEFERRED → 0675): Given the user edits an **Installed** skill, when they attempt to type, then a banner appears: "Installed skills are read-only. Edit the source in your project, then re-install." with a "Find source" button that searches for a matching Own skill and selects it if found.
> - **AC-US5-08** (DEFERRED → 0675): Given an edit is in progress, when the user selects a different skill, then a confirm dialog warns "Discard unsaved changes?" with keyboard-accessible Discard / Cancel.
> - **AC-US5-09** (DEFERRED → 0675): Given the preview pane, when it renders, then it uses the same Markdown/code renderer used elsewhere in the studio (no new dependency), honors both themes, and renders code fences with theme-aware syntax highlighting.
> - **AC-US5-10** (DEFERRED → 0675): Given the file watcher detects an external change to the SKILL.md being edited, when detected, then a banner offers "File changed on disk — Reload / Keep editing"; no silent overwrites.

---

### US-006: Empty, Loading, and Error States (P1)
**Project**: vskill-platform

**As a** developer who has just installed the studio or whose workspace has issues
**I want** explicit, helpful states for every scenario
**So that** I never see a blank screen and always know what to do next

**Acceptance Criteria**:
- [x] **AC-US6-01**: Given a fresh workspace with zero skills (neither Own nor Installed), when the studio loads, then the main area shows a large empty state: headline "No skills yet", two CTA buttons — "Create a skill" (opens create flow) and "Install from registry" (copies `vskill install` command) — plus a link to the docs. The sidebar shows both section headers with count `(0)` and per-section empty microcopy.
- [x] **AC-US6-02**: Given initial skill scan is in progress, when rendering, then the sidebar shows 6 skeleton cards (3 per section) and the detail panel shows a full-panel skeleton; skeletons use the existing `.skeleton` class and respect theme tokens.
- [x] **AC-US6-03**: Given the scan fails (permission denied, path not found, server error), when detected, then the sidebar shows an error card with icon, short message, full error in a `<details>` disclosure, and a "Retry" button that re-invokes the scan. The console is NOT the only signal.
- [x] **AC-US6-04**: Given a skill fails to load its SKILL.md (corrupt file, missing frontmatter), when selected, then the detail panel renders an error state explaining which file failed, with a "Open in editor" action and a "Copy path" action — the rest of the sidebar remains usable.
- [x] **AC-US6-05**: Given a network error fetching model list or benchmark results, when a request fails, then the affected component shows an inline error with "Retry"; the studio never crashes to a white screen and `ErrorBoundary` wraps the root.
- [x] **AC-US6-06**: Given the studio is disconnected from the eval-server (SSE closed), when detected, then a persistent top-bar banner appears "Disconnected — reconnecting…" with a live connection indicator; on reconnect the banner auto-dismisses.

---

### US-007: Responsive Layout (P2)
**Project**: vskill-platform

**As a** developer on a laptop or external display
**I want** the studio to adapt to the width I have available
**So that** it's usable on a 13" laptop and shines on a 27" monitor

**Acceptance Criteria**:
- [x] **AC-US7-01**: Given a viewport width ≥1280px (desktop), when the studio renders, then the layout is `[sidebar 320px | divider | main 1fr]` with the detail panel using an inner 2-column layout when width permits (≥1600px).
- [x] **AC-US7-02**: Given a viewport width 768–1279px (tablet/narrow desktop), when the studio renders, then the sidebar narrows to 240px and the detail panel switches to a single-column inner layout.
- [x] **AC-US7-03**: Given a viewport width <768px, when the studio renders, then the sidebar is hidden behind an overlay drawer toggleable from the top bar (hamburger icon); the main area fills the viewport. This is degraded-mode only — mobile is not a primary target.
- [x] **AC-US7-04**: Given the user resizes the window, when the viewport crosses a breakpoint, then transitions are smooth and no content is clipped or reflowed with jank.
- [x] **AC-US7-05**: Given the sidebar is visible at ≥1280px, when the user drags the divider between sidebar and main, then the sidebar resizes within [240px, 480px]; the width persists to `localStorage`.

---

### US-008: Accessibility (WCAG 2.1 AA) (P1)
**Project**: vskill-platform

**As a** developer using a screen reader or keyboard-only input
**I want** the studio to be fully navigable and announce state changes
**So that** the studio is usable regardless of input modality

**Acceptance Criteria**:
- [x] **AC-US8-01**: Given the studio renders, when evaluated with axe-core in both themes, then zero serious or critical violations are reported.
- [x] **AC-US8-02**: Given every interactive element (button, link, input, section toggle, skill card, theme toggle), when rendered, then it has a discernible accessible name via text content, `aria-label`, or `aria-labelledby`.
- [x] **AC-US8-03**: Given the sidebar skill list, when navigated via keyboard, then focus is visible with a 2px outline in `var(--accent)` at 3:1 minimum contrast against the surrounding background, in both themes. `:focus-visible` is used so mouse clicks don't show the ring.
- [x] **AC-US8-04**: Given the section headers (Own / Installed), when rendered, then each uses `<h2>` (or has `role="heading"` + `aria-level="2"`) and each group below uses `role="group"` with `aria-labelledby` pointing to the header.
- [x] **AC-US8-05**: Given a skill is selected, when the detail panel updates, then an `aria-live="polite"` region announces "Viewing <skill-name> (<Own|Installed>)".
- [x] **AC-US8-06**: Given modals (keyboard cheatsheet, discard-changes confirm, context menu), when opened, then focus is trapped inside, `Escape` closes them, focus returns to the trigger on close, and `role="dialog"` + `aria-modal="true"` are set.
- [x] **AC-US8-07**: Given toasts/notifications, when fired, then they are announced via `aria-live="assertive"` for errors and `aria-live="polite"` for success/info.
- [x] **AC-US8-08**: Given form inputs in the editor or create flow, when a validation error fires, then `aria-invalid="true"` is set and the error message is associated via `aria-describedby`.
- [x] **AC-US8-09**: Given the theme toggle, when the user is on `prefers-contrast: more`, then the studio respects a high-contrast variant (tokens have a `[data-contrast="more"]` set with heavier borders and stronger contrast).

---

### US-009: Performance Budget (P1)
**Project**: vskill-platform

**As a** developer running the studio hundreds of times a day
**I want** the studio to feel instant at every interaction
**So that** it's always faster to open the studio than to `cat` a SKILL.md

**Acceptance Criteria**:
- [x] **AC-US9-01**: Given a cold load on a workspace with ≤100 skills, when the studio boots, then first paint (FCP) occurs within 800ms and time-to-interactive (TTI) within 1500ms on a mid-range laptop (measured via Vite preview + Lighthouse CI).
- [x] **AC-US9-02**: Given a workspace with ≥500 skills, when the sidebar renders, then skill cards are virtualised (react-virtuoso or equivalent — not full-list render); scroll FPS stays ≥50 on a mid-range laptop.
- [x] **AC-US9-03**: Given a skill is selected, when the detail panel renders, then the render-to-first-visible-content completes within 120ms (excluding network-backed operations like benchmark history fetch, which render their own skeletons).
- [x] **AC-US9-04**: Given the search input receives input, when a character is typed, then the result list updates within 80ms for ≤500 skills and within 180ms for up to 2000 skills — debounced at 50ms to avoid per-keystroke re-renders.
- [x] **AC-US9-05**: Given the JS bundle, when built, then the initial chunk is ≤250KB gzipped; heavy components (Markdown editor, charts, sweep leaderboard) are dynamically imported and not in the initial chunk.
- [x] **AC-US9-06**: Given the theme is switched, when the transition runs, then it completes in ≤200ms with no layout thrash (verified via Performance panel — no long tasks >50ms triggered by the switch).

---

### US-010: Copy Voice — Direct, Calm, Humane (P1)
**Project**: vskill-platform

**As a** developer using the studio in focus mode
**I want** every piece of user-facing copy to sound like a thoughtful collaborator, not a marketing bot
**So that** the studio feels like professional tooling, respects my attention, and doesn't slow me down with chatter

**Voice principles** (derived from Anthropic / Claude Labs guidance):
- Direct — say what happened and what to do next.
- Calm — no exclamation marks except inside user content; no "Oops!", no "Uh oh", no "Success!"
- Humane — second-person ("you"), plain verbs, no corporate passive voice.
- Brief — sentences under 18 words where possible; one idea per line.
- No emoji in product strings (user-generated content excepted). No celebration language.

**Acceptance Criteria**:
- [x] **AC-US10-01**: Given every empty state (sidebar sections, detail panel, search results, main area), when rendered, then copy follows the pattern "Short declarative sentence. Concrete next step." Example anchors: sidebar Own empty → "No skills yet. Add one from the marketplace or point Studio at a folder." Sidebar Installed empty → "No installed skills. Run `vskill install <plugin>` or `claude plugin install <plugin>` to add one." No variant uses "Oops", "Let's get started", "Welcome!", or any exclamation-punctuated phrase.
- [x] **AC-US10-02**: Given every error state (scan failure, save failure, network error, SSE disconnect, malformed SKILL.md), when rendered, then the copy names what failed, states the cause in plain language, and offers the remediation. No blame ("You entered an invalid…"), no shame ("Oops, something went wrong"), no emoji, no exclamation marks. Example anchor: save failure → "Couldn't save SKILL.md — the file changed on disk. Reload to see the new version, or keep editing to overwrite."
- [x] **AC-US10-03**: Given every loading/progress state (scanning workspace, running benchmark, saving, installing), when rendered, then the copy is declarative and present-tense, without filler phrases. Good: "Scanning workspace…", "Running benchmark on claude-sonnet-4.5…". Not allowed: "Please wait while we…", "Just a moment…", "Working hard on this…".
- [x] **AC-US10-04**: Given every success confirmation (save, install, benchmark complete, update applied), when surfaced as a toast, then it states the outcome in four words or fewer where possible and ends with a period, not an exclamation mark. Good: "Saved obsidian-brain.", "Installed 3 skills.", "Benchmark complete." Not allowed: "Success!", "Saved! 🎉", "Great job!".
- [x] **AC-US10-05**: Given all tooltips, button labels, and section headers, when written, then they use plain verbs and avoid marketing adjectives. Good: "Run benchmark", "Copy path", "Edit SKILL.md", "Switch theme". Not allowed: "Blazing-fast benchmark", "Magical edit mode", "Awesome theme switcher". Commands that reference shell commands (e.g., `vskill install`) are formatted as inline code, not prose.
- [x] **AC-US10-06**: Given every user-facing string in the redesign, when extracted to the central `strings.ts` module (per NFR-005), then each entry is reviewed against the voice principles. A single-file grep in CI forbids: `/\boops\b/i`, `/\buh[ -]oh\b/i`, `\bawesome\b/i`, `/\bblazing[- ]fast\b/i`, `/🎉|✨|🚀|✅/` in source strings, and any string ending in more than one `!`. Violations fail the build.

---

## Functional Requirements

### FR-001: Classification is Single-Source-of-Truth
The UI must not re-implement origin classification. It consumes `SkillInfo.origin` from the backend (populated by `classifyOrigin()` in `src/eval/skill-scanner.ts`). If the rule set changes (e.g., a new agent dir), it changes in `skill-scanner.ts` only; the UI picks it up for free.

### FR-002: Theme Tokens Are the Only Color Source
All colors in studio components must reference CSS custom properties defined in `globals.css`. No component may introduce a hardcoded color outside that file. A CI check greps `src/eval-ui/src/**/*.{ts,tsx}` for `#[0-9a-fA-F]{3,8}` and `rgba?\(` patterns; matches outside an allowlist (shadows, SVG fills that intentionally override) fail the build.

### FR-003: No Backend Rewrite
Scanner, eval-server, benchmark runner, skill-create routes, and the install pipeline are untouched by this increment. The redesign is UI-and-theme-first. If a new endpoint is needed (e.g., "reveal in editor"), it is a thin additive route, not a refactor.

### FR-004: Backward Compatibility
Existing hash-routes (`#/updates`, `#/sweep`, per-skill routes) continue to work. The URL shape is not broken. Users on prior versions returning to the studio see their preferences respected where present.

### FR-005: Keyboard-First
Every interactive action that has a mouse path must also have a keyboard path. The cheatsheet (AC-US4-05) is the canonical registry.

### FR-006: Component Reuse
Reuse `SkillCard`, `SkillSearch`, `ModelSelector`, `EmptyState`, `ErrorCard`, `VersionHistoryPanel`, `McpDependencies`, `TrendChart`, `GroupedBarChart`, `StudioLayout`, `LeftPanel`, `RightPanel`. The redesign refactors these in place; net-new components are limited to: `ThemeProvider`, `ThemeToggle`, `KeyboardShortcutCheatsheet`, `SidebarSectionHeader`, `ContextMenu`, and the split-pane editor-preview wrapper if absent.

## Non-Functional Requirements

### NFR-001: Performance Budget
See US-009. Hard-blocked by Lighthouse CI assertions.

### NFR-002: Accessibility
See US-008. Hard-blocked by axe-core zero-serious-violations assertion in both themes.

### NFR-003: Test Coverage
Unit: 90% line coverage for new/modified components. Integration: full coverage of Installed/Own split rendering, theme switching, keyboard shortcuts. E2E: Playwright spec covering "launch studio → see both sections populated → switch theme → select skill → edit → save → benchmark" end-to-end, run in both themes.

### NFR-004: Bundle Size
Initial gzipped chunk ≤250KB. Lazy-loaded chunks ≤150KB each.

### NFR-005: i18n Readiness
All user-visible strings are extracted to a single `strings.ts` module. No i18n framework is added in this increment, but the extraction means a future PR can plug in i18next without touching every component.

### NFR-006: Telemetry (Opt-in)
If the existing telemetry opt-in is enabled, the redesign emits: `studio.theme_changed`, `studio.section_collapsed`, `studio.shortcut_used`, `studio.skill_selected` with origin dimension. Zero telemetry when disabled (default).

### NFR-007: Visual Language (Informational — Architect Owns the Tokens)
Visual language derives from Anthropic / Claude Labs — warm-neutral palette, serif display + geometric sans body, calm restrained motion. Both light and dark themes are first-class; dark mode preserves warmth (warm near-black, not cool slate). Concretely this means: dark `--surface-0` trends toward a warm `#1a1816`-ish family rather than a cool `#0b0d11` slate; light `--surface-0` trends toward a warm off-white (`#faf9f7`-ish) rather than pure `#ffffff`; accents remain restrained and readable at small sizes; motion uses ≤300ms ease-out curves and respects `prefers-reduced-motion`. This NFR is guidance for the token layer — the architect owns the exact palette.

## Success Criteria

- **Visual clarity**: A user screenshot of the sidebar is sufficient to identify a skill's provenance — no hover required.
- **Theme parity**: A side-by-side screenshot of light and dark themes is judged "equally polished" by a design review; no "clearly an afterthought" token fails present.
- **Speed**: P95 of all in-app interactions (selection, search, theme switch) ≤200ms. Cold boot TTI ≤1500ms.
- **Keyboard**: Every documented shortcut works; the cheatsheet is complete; a user can complete "select → edit → save → benchmark" without touching the mouse.
- **Detail completeness**: For a selected skill, a reviewer can answer — without leaving the studio — "what version, what plugin, what path, what deps, what agent it's installed under, last benchmark status, update available?"
- **Zero regressions**: All existing eval-ui tests pass; no existing feature is removed.

## Out of Scope

- Rewriting `skill-scanner.ts`, `eval-server`, or the install/uninstall pipeline
- Adding a new backend, new auth, new payment, new analytics provider
- Mobile-native wrapper (the studio is a desktop-first web SPA)
- i18n translation (only extraction readiness — no locale files shipped)
- Redesigning the `vskill-platform/src/app/studio/page.tsx` marketing page
- Replacing the existing Markdown renderer or syntax highlighter with a new library
- Adding new AI features (improve, sweep, model-compare are untouched — their UIs only gain theme support)
- Windows-only testing (dev on macOS/Linux primary; Windows is best-effort)

## Dependencies

- `classifyOrigin()` in `src/eval/skill-scanner.ts` — exists, reused
- `AGENTS_REGISTRY` in `src/agents/agents-registry.ts` — exists, reused for agent display-name resolution in detail panel
- Existing eval-server endpoints for scan, SKILL.md read/write, benchmark, version history — existing
- Tailwind v4 + globals.css — existing, extended with light-theme token set
- Vite + React 18 SPA scaffold at `src/eval-ui/` — existing
- Playwright + Vitest — existing test stack

## Risks

| Risk | Probability | Impact | Severity | Mitigation |
|------|-------------|--------|----------|------------|
| Elevating Installed section breaks user expectation that their own skills come first | 0.4 | 3 | 1.2 | Own is rendered ABOVE Installed; empty-state guidance; release note covers change |
| Light theme tokens fail WCAG without careful tuning | 0.5 | 4 | 2.0 | Token palette designed against contrast matrix; CI contrast check blocks regressions |
| Large workspaces hit perf budget without virtualisation | 0.4 | 4 | 1.6 | Virtualised list from day 1; perf budget enforced in CI |
| Keyboard shortcut collisions with browser/OS | 0.3 | 3 | 0.9 | Use well-scoped combos (Cmd/Ctrl+K, `?`, single-letter actions only when not in input); cheatsheet is canonical |
| Existing tests coupled to current sidebar structure | 0.6 | 2 | 1.2 | Rewrite tests alongside the refactor; tests are part of each task |
| Hardcoded-color ESLint rule fights existing code | 0.5 | 2 | 1.0 | Whitelist legitimate exceptions; one-time cleanup pass as part of this increment |

## Edge Cases

- **Skill with identical name in both sections**: rendered in both (AC-US1-10); selection state is per-origin.
- **Skill whose `dir` is outside the project root** (e.g., symlink): `classifyOrigin` uses the relative path from root — treated as source if not under a known prefix.
- **User on `prefers-color-scheme: no-preference`**: treated as dark (the brand default).
- **Theme toggle pressed rapidly**: debounced — only the final state persists.
- **Zero skills on first load**: main area shows the master empty state (AC-US6-01); sidebar shows both headers with empty microcopy, not collapsed.
- **File on disk changes while editor is dirty**: reload banner offered, no silent overwrite (AC-US5-10).
- **Scanner returns a skill with `origin` field missing** (older backend): UI treats it as `"source"` and logs a dev-console warning — graceful degradation.
- **User's Markdown contains unclosed code fence**: preview renderer renders best-effort; a gutter warning shows the parse issue but doesn't block preview.
- **`allowedTools` includes an MCP tool not currently loaded**: warning (not error) surfaces in editor issues strip — runtime will ignore it.
