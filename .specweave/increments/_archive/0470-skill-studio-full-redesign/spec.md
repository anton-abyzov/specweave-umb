---
increment: 0470-skill-studio-full-redesign
title: Skill Studio Full Redesign
type: feature
priority: P1
status: completed
created: 2026-03-10T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Skill Studio Full Redesign

## Problem Statement

The local Skill Studio UI (React eval UI served by `vskill eval serve`) uses a sidebar navigation with separate page routes for each concern (Home, Create, Benchmark, Comparison, History). Selecting a skill navigates to an entirely separate workspace page with an icon-based LeftRail panel switcher. This multi-page navigation model is slow, loses context, and makes it hard to compare or quickly browse between skills. The UI needs a unified master-detail layout where the skill list is always visible and selecting a skill shows its details inline without full-page navigation.

## Goals

- Replace sidebar nav + page-based routing with a master-detail split-pane layout
- Provide instant skill switching without page transitions
- Consolidate the 6 workspace panels (Editor, Tests, Run, Activation, History, Deps) into a tabbed detail view
- Add search and filtering to the skill list
- Introduce `vskill studio` as a new CLI entry point
- Generate category icons and illustrations via Nano Banana Pro
- Achieve a world-class dark-theme design using existing CSS variable system

## User Stories

### US-001: Master-Detail Split-Pane Layout
**Project**: vskill
**As a** skill author using the local Skill Studio
**I want** a side-by-side layout with a skill list on the left and skill details on the right
**So that** I can browse and switch between skills without losing context or triggering full-page navigations

**Acceptance Criteria**:
- [x] **AC-US1-01**: The root route renders a split-pane layout with a left panel (280px fixed width) and a right panel (flex: 1), replacing the current sidebar nav + SkillListPage + separate SkillWorkspace page routes
- [x] **AC-US1-02**: Both panels scroll independently with `overflow-y: auto` and fill the full viewport height
- [x] **AC-US1-03**: A 1px vertical border separates the two panels using `var(--border-subtle)` color
- [x] **AC-US1-04**: The layout uses the existing design system (Tailwind v4 + CSS variables: `--surface-0..4`, `--text-*`, `--accent`, etc.)
- [x] **AC-US1-05**: The left panel header displays the "Skill Studio" brand with project name (from `/api/config`) and a model selector (existing `ModelSelector` component)

---

### US-002: Scrollable Skill List with Search and Filter
**Project**: vskill
**As a** skill author looking for a specific skill
**I want** an inline search input and plugin group filter in the skill list panel
**So that** I can quickly find skills without scrolling through the entire list

**Acceptance Criteria**:
- [x] **AC-US2-01**: An inline search input at the top of the left panel filters skills by name with 200ms debounce, performed client-side against the already-loaded skill list (local skill counts are small, no server-side search needed)
- [x] **AC-US2-02**: Skills are grouped by plugin name with a group header showing the plugin name and skill count, matching the current `SkillListPage` grouping pattern
- [x] **AC-US2-03**: Each skill card shows: skill name, eval count, assertion count, benchmark status pill (Passing/Failing/Pending/No evals with color coding from existing `STATUS_CONFIG`), and last benchmark date
- [x] **AC-US2-04**: A total skill count is displayed below the search input (e.g., "12 skills across 3 plugins")
- [x] **AC-US2-05**: Empty search results show "No skills match your search" with a clear button

---

### US-003: Inline Skill Detail with Tabbed Panels
**Project**: vskill
**As a** skill author evaluating and editing a skill
**I want** the right panel to show skill details organized in tabs matching the current workspace panels
**So that** I can edit, test, run evals, check activation, view history, and inspect dependencies without navigating away

**Acceptance Criteria**:
- [x] **AC-US3-01**: Clicking a skill card in the left panel selects it and renders its detail in the right panel without a page navigation or hash change
- [x] **AC-US3-02**: The selected skill card is highlighted with a left accent border (`var(--accent)`) and slightly elevated background (`var(--surface-2)`)
- [x] **AC-US3-03**: The detail panel header shows a breadcrumb (plugin / skill), benchmark status pill, pass rate, and case/assertion counts (reusing current `WorkspaceHeader` data logic)
- [x] **AC-US3-04**: Six tabs are rendered below the header: Editor, Tests, Run, Activation, History, Deps -- matching the current LeftRail panel groups (Build, Evaluate, Insights)
- [x] **AC-US3-05**: Each tab renders the corresponding existing panel component (`EditorPanel`, `TestsPanel`, `RunPanel`, `ActivationPanel`, `HistoryPanel`, `DepsPanel`) wrapped in the existing `WorkspaceProvider` context

---

### US-004: New Skill Creation Button and Flow
**Project**: vskill
**As a** skill author
**I want** a prominent "New Skill" button in the skill list panel
**So that** I can create a new skill without navigating to a separate page

**Acceptance Criteria**:
- [x] **AC-US4-01**: A "New Skill" button is rendered at the top of the skill list panel (below the search input), styled with `var(--accent)` background and a plus icon
- [x] **AC-US4-02**: Clicking "New Skill" renders the existing `CreateSkillPage` content in the right detail panel instead of navigating to a separate route
- [x] **AC-US4-03**: After successful skill creation, the skill list refreshes and the newly created skill is automatically selected
- [x] **AC-US4-04**: While the creation form is active, the "New Skill" button in the list panel shows an active state

---

### US-005: `vskill studio` CLI Command
**Project**: vskill
**As a** skill author
**I want** to run `vskill studio` to launch the Skill Studio UI
**So that** I have a discoverable, memorable entry point separate from the `eval serve` subcommand

**Acceptance Criteria**:
- [x] **AC-US5-01**: A new top-level `studio` command is registered in `src/index.ts` via Commander, with the description "Launch the Skill Studio UI for local skill development"
- [x] **AC-US5-02**: `vskill studio` accepts the same `--root <path>` and `--port <number>` options as `vskill eval serve`
- [x] **AC-US5-03**: `vskill studio` delegates to the existing `runEvalServe()` function, reusing all port selection logic (hash-based deterministic port 3077-3177, conflict detection, auto-kill)
- [x] **AC-US5-04**: `vskill eval serve` continues to work as before (not removed, not changed)
- [x] **AC-US5-05**: The terminal output when launching via `vskill studio` says "Skill Studio" instead of "Eval UI" in the startup banner

---

### US-006: Responsive Layout
**Project**: vskill
**As a** skill author using the Studio on a smaller screen or narrow window
**I want** the layout to adapt gracefully
**So that** the UI remains usable at various viewport widths

**Acceptance Criteria**:
- [x] **AC-US6-01**: Below 768px viewport width, the split-pane collapses to a single-column layout showing only the skill list
- [x] **AC-US6-02**: On narrow viewports, tapping a skill shows the detail panel as a full-width overlay with a back button to return to the list
- [x] **AC-US6-03**: The back button preserves the current search/filter state
- [x] **AC-US6-04**: The left panel width (280px) can be reduced to 240px at viewport widths between 768px and 1024px

---

### US-007: Category Icon Generation via Nano Banana Pro
**Project**: vskill
**As a** skill author browsing the skill list
**I want** each plugin group to have a distinctive generated icon
**So that** I can visually distinguish plugin groups at a glance

**Acceptance Criteria**:
- [x] **AC-US7-01**: A one-time generation script uses the Nano Banana Pro model (`gemini-3-pro-image-preview`) to create plugin group icons in a consistent minimalist line-art style on transparent background
- [x] **AC-US7-02**: Generated icons are stored as static assets (WebP, 32x32px) in `src/eval-ui/public/images/icons/` and served by the eval server's static file handler
- [x] **AC-US7-03**: Each plugin group header renders its icon at 16x16 display size to the left of the plugin name
- [x] **AC-US7-04**: A fallback SVG icon (the existing box/package icon from `IconSkills`) is shown when a plugin-specific icon is not available
- [x] **AC-US7-05**: One empty-state illustration is generated and stored at `src/eval-ui/public/images/empty-studio.webp` (128x128, theme-neutral) for use in empty states

---

### US-008: Empty States and Error Handling
**Project**: vskill
**As a** skill author launching the Studio with no skills or encountering errors
**I want** meaningful empty states and error messages
**So that** I understand how to use the interface and what went wrong

**Acceptance Criteria**:
- [x] **AC-US8-01**: When no skill is selected, the right panel shows a centered empty state with the generated illustration and "Select a skill to view details" text in muted color
- [x] **AC-US8-02**: When `scanSkills()` returns zero skills, the left panel shows the existing empty state design ("No skills found" with root path hint and "Create Your First Skill" button)
- [x] **AC-US8-03**: When skill data fails to load (API error), the detail panel shows the error message with a retry button, styled with `var(--red-muted)` background
- [x] **AC-US8-04**: When the search filter returns no matches, the skill list shows "No skills match your search" with a "Clear search" link

## Out of Scope

- Drag-and-drop panel resizing (split-pane width is fixed)
- Keyboard shortcuts for list navigation (existing Ctrl+1..6 panel shortcuts within workspace are preserved)
- Light theme (the eval UI is dark-theme only via CSS variables)
- Changes to the eval server API routes (no new endpoints)
- Changes to the existing workspace panel components themselves (EditorPanel, TestsPanel, RunPanel, etc.) -- they are reused as-is
- Removal of old page routes (the HashRouter routes for `/create` and `/skills/:plugin/:skill` can remain as fallbacks during transition)
- Real-time skill file watching / hot reload of skill list
- Mobile-native optimizations beyond basic responsive layout

## Technical Notes

### Architecture
- **Target code**: `src/eval-ui/` (React 19 + Vite 6 + Tailwind v4)
- **Server**: `src/eval-server/` (custom Node.js HTTP server)
- **State**: Existing `useReducer` in `WorkspaceContext` for per-skill workspace state; new lightweight state for selected skill and search filter
- **Routing**: Current `HashRouter` with `Routes` in `App.tsx`. The redesign replaces route-based navigation with component-level state (selected skill ID). The `WorkspaceProvider` is instantiated per selected skill
- **Skill discovery**: `scanSkills(root)` from `src/eval/skill-scanner.ts` discovers skills across 4 project layouts

### Dependencies
- Existing API routes: `/api/skills`, `/api/skills/:plugin/:skill`, `/api/skills/:plugin/:skill/evals`, `/api/skills/:plugin/:skill/benchmark/latest`, `/api/config`
- Existing components: `ModelSelector`, `EditorPanel`, `TestsPanel`, `RunPanel`, `ActivationPanel`, `HistoryPanel`, `DepsPanel`, `WorkspaceProvider`, `WorkspaceHeader`
- Existing design tokens in `globals.css` (`--surface-*`, `--text-*`, `--accent`, `--border-*`, etc.)
- Nano Banana Pro API (`gemini-3-pro-image-preview`) via VertexAI key for icon generation
- Commander.js for CLI command registration

### Constraints
- Must not break `vskill eval serve` behavior
- Must work with all 4 project layouts supported by `scanSkills()`
- Multiple instances from different folders must work simultaneously (existing hash-based port logic)
- Generated icons are a one-time build step, not runtime generation

## Success Metrics

- Switching between skills in the list feels instant (no page transition, no loading spinner for already-loaded skills)
- The `vskill studio` command launches the UI and prints the correct "Skill Studio" banner
- All 6 workspace panels (Editor, Tests, Run, Activation, History, Deps) function correctly within the tabbed detail view
- Search filtering responds within 200ms of keystroke
- The UI gracefully handles 0 skills, 1 skill, and 50+ skills without layout breakage
