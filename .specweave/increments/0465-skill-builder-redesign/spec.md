---
increment: 0465-skill-builder-redesign
title: "Skill Builder Redesign: Unified Workspace"
type: feature
priority: P1
status: planned
created: 2026-03-09
structure: user-stories
test_mode: TDD
coverage_target: 90
supersedes: [0463-skill-builder-ui-redesign, 0464-skill-builder-create-flow]
---

# Feature: Skill Builder Redesign: Unified Workspace

## Problem Statement

The eval-ui currently has 4 disconnected pages (SkillDetailPage 1068 lines, BenchmarkPage 647, ComparisonPage 381, HistoryPage 789) that force skill developers to navigate between separate routes to edit, test, run benchmarks, and review history. This fragmented workflow breaks the tight edit-test-iterate loop that is critical for skill quality. State is not shared between pages, so running a benchmark requires navigating away from the test case list, losing context.

## Goals

- Collapse 4 separate pages into a single SkillWorkspace route with panel-based navigation
- Make test cases the central organizing unit with inline run results and assertion health
- Enable a seamless edit-test-iterate loop where failed assertions guide improvements
- Provide shared state management so cross-panel interactions work without page navigations
- Add SKILL.md editor with live preview for in-place content editing

## Design Decisions (from Interview)

- **State persistence**: Ephemeral (no localStorage). Active panel persisted in URL query params only
- **File save conflicts**: Last-write-wins. Single-user local dev tool, no conflict detection
- **Left rail**: Always 48px icon-only. Minimum viewport 1024px. No responsive breakpoints
- **Panel transitions**: Instant swap with subtle fade-in (existing `animate-fade-in` pattern)
- **Keyboard shortcuts**: Ctrl+1-5 panel switching, Ctrl+S save, Ctrl+Enter run selected, Ctrl+Shift+Enter run all
- **Test case scale**: Simple scrollable list. Real-world 2-15 cases max. No virtualization
- **Concurrent runs**: One at a time. Reject with message if already running
- **Dirty editor on panel switch**: Silently preserve dirty state. Dirty indicator stays visible. No warning dialog

## User Stories

### US-001: Unified Workspace Shell (P0)
**Project**: vskill

**As a** skill developer
**I want** a single workspace page with a left rail navigation
**So that** I can switch between editing, testing, running, and viewing history without page navigations

**Acceptance Criteria**:
- [ ] **AC-US1-01**: Given a skill exists, when navigating to /skills/:plugin/:skill, then a SkillWorkspace route renders replacing the 4 separate pages (SkillDetailPage, BenchmarkPage, ComparisonPage, HistoryPage)
- [ ] **AC-US1-02**: Given the workspace is open, when viewing the left rail, then 5 icon buttons (Editor, Tests, Run, History, Deps) are visible in a 48px-wide rail and clicking each switches the active panel
- [ ] **AC-US1-03**: Given the workspace is open, when viewing the WorkspaceHeader, then it shows breadcrumb (plugin > skill), pass rate summary badge, total assertion count, and active model info
- [ ] **AC-US1-04**: Given a panel is active, when the URL is shared or refreshed, then the query param ?panel=tests|editor|run|history|deps deep-links to that specific panel
- [ ] **AC-US1-05**: Given the workspace is open, when pressing Ctrl+1 through Ctrl+5, then the corresponding panel activates (1=Editor, 2=Tests, 3=Run, 4=History, 5=Deps)

---

### US-002: SKILL.md Editor with Live Preview (P1)
**Project**: vskill

**As a** skill developer
**I want** to edit my SKILL.md in a raw editor with a live preview
**So that** I can see changes in real-time without leaving the workspace

**Acceptance Criteria**:
- [ ] **AC-US2-01**: Given the Editor panel is active, when viewing the editor, then a split view shows a raw textarea on the left and rendered markdown preview on the right
- [ ] **AC-US2-02**: Given the Editor panel is active, when clicking view mode toggles, then the layout switches between Raw-only, Preview-only, and Side-by-Side modes
- [ ] **AC-US2-03**: Given SKILL.md has frontmatter, when viewing the preview pane, then frontmatter fields are displayed as structured key-value cards (not raw YAML)
- [ ] **AC-US2-04**: Given the editor has changes, when pressing Ctrl+S, then content saves to disk via PUT /api/skills/:plugin/:skill/content and the dirty indicator clears
- [ ] **AC-US2-05**: Given the editor content differs from the last saved version, when viewing the workspace, then a dirty indicator (dot or asterisk) appears next to the Editor icon in the rail and in the WorkspaceHeader
- [ ] **AC-US2-06**: Given the Editor panel is active, when clicking "Improve with AI", then the existing SkillImprovePanel opens inline with the editor and its output can be applied to the textarea

---

### US-003: Test Case Management Panel (P0)
**Project**: vskill

**As a** skill developer
**I want** test cases to be the central organizing unit with a list+detail layout
**So that** I can manage, edit, and run individual test cases efficiently

**Acceptance Criteria**:
- [ ] **AC-US3-01**: Given the Tests panel is active, when viewing the layout, then a left sub-panel (280px) shows a scrollable list of test cases with status pills (pass/fail/pending) and sparkline charts showing recent pass-rate trend
- [ ] **AC-US3-02**: Given a test case is selected in the list, when viewing the right sub-panel, then it shows the selected case's editable prompt textarea and expected output textarea
- [ ] **AC-US3-03**: Given a test case is selected, when viewing its assertions section, then an inline assertion builder allows add, edit, delete, and drag-to-reorder operations on assertions
- [ ] **AC-US3-04**: Given a test case has been run, when viewing its detail, then last run results appear inline showing each assertion's pass/fail status with reasoning text
- [ ] **AC-US3-05**: Given a test case is selected, when clicking its "Run" button, then a single-case benchmark triggers via SSE and the workspace switches to the Run panel scoped to that case
- [ ] **AC-US3-06**: Given a test case is selected, when clicking "A/B Compare", then a skill-vs-baseline comparison runs for that single case
- [ ] **AC-US3-07**: Given the Tests panel is active, when clicking "+ Add Test Case", then a form appears for entering prompt, expected output, and assertions for a new case
- [ ] **AC-US3-08**: Given a test case has a prompt and expected output, when clicking "Suggest Assertions", then AI-generated assertions are proposed and can be accepted/rejected individually

---

### US-004: Assertion Health and Quality Indicators (P1)
**Project**: vskill

**As a** skill developer
**I want** to see quality indicators on my assertions
**So that** I can identify flaky, non-discriminating, and regressed assertions

**Acceptance Criteria**:
- [ ] **AC-US4-01**: Given an assertion has a 30-70% pass rate across 3+ runs, when viewing it in the Tests panel, then a yellow "Flaky" badge appears next to it
- [ ] **AC-US4-02**: Given an assertion passes on both skill and baseline runs, when viewing it in the Tests panel, then a gray "Non-discriminating" badge appears next to it
- [ ] **AC-US4-03**: Given an assertion was passing in the previous run but fails in the latest run, when viewing it in the Tests panel, then a red downward arrow regression marker appears next to it
- [ ] **AC-US4-04**: Given quality badges are displayed, when inspecting the data source, then badge data is derived from the existing /api/skills/:plugin/:skill/stats and history APIs (no new backend endpoints)

---

### US-005: Benchmark Execution Panel (P1)
**Project**: vskill

**As a** skill developer
**I want** a unified run panel that supports benchmark, baseline, and A/B comparison modes with SSE streaming
**So that** I can execute and monitor all types of evaluation runs from one place

**Acceptance Criteria**:
- [ ] **AC-US5-01**: Given the Run panel is active, when viewing the controls bar, then "Run All", "Run Baseline", and "Run A/B Comparison" buttons are visible
- [ ] **AC-US5-02**: Given the Run panel is active, when a scope selector is present, then the user can choose between "All cases" and "Selected case only" (pre-filled when navigated from Tests panel)
- [ ] **AC-US5-03**: Given a run is in progress, when SSE events stream in, then per-case result cards animate in with fade-in showing pass/fail status and assertion details
- [ ] **AC-US5-04**: Given a run is in progress, when viewing the panel, then a progress bar shows completion count (e.g., "2/5 cases")
- [ ] **AC-US5-05**: Given a run completes, when viewing the panel, then an overall pass rate card and GroupedBarChart render showing results summary
- [ ] **AC-US5-06**: Given a run completes, when switching to the Tests panel, then inline results for each case are updated from the shared workspace state
- [ ] **AC-US5-07**: Given a run is in progress, when clicking another "Run" button, then the action is rejected with message "Benchmark already running -- wait or cancel"

---

### US-006: History and Regression Detection Panel (P1)
**Project**: vskill

**As a** skill developer
**I want** to view run history with regression detection
**So that** I can track improvements and catch regressions over time

**Acceptance Criteria**:
- [ ] **AC-US6-01**: Given the History panel is active, when viewing the layout, then three sub-tabs are available: Timeline, Per-Eval, and Statistics
- [ ] **AC-US6-02**: Given the Timeline tab is active, when viewing the list, then historical runs display with model, type (benchmark/comparison/baseline), date, and pass rate; filterable by model, type, and date range
- [ ] **AC-US6-03**: Given the Timeline tab is active, when selecting 2 runs via checkboxes, then a "Compare" button enables and clicking it shows a side-by-side regression/improvement diff
- [ ] **AC-US6-04**: Given the Per-Eval tab is active, when viewing the grid, then an assertion-level heatmap renders with rows=assertions, columns=runs (most recent on right), cells colored green (pass) or red (fail)
- [ ] **AC-US6-05**: Given the heatmap is displayed, when clicking any cell, then a detail overlay shows that run's full output text and the assertion's reasoning
- [ ] **AC-US6-06**: Given regressions are detected (assertions that were passing but now fail), when viewing the WorkspaceHeader, then a regression alert banner is visible with count and link to History panel
- [ ] **AC-US6-07**: Given the Statistics tab is active, when viewing the content, then it reuses the existing StatsPanel and TrendChart components

---

### US-007: Edit-Test-Iterate Tight Loop (P0)
**Project**: vskill

**As a** skill developer
**I want** the edit-test-iterate workflow to be seamless
**So that** failed assertions guide me directly to improvements without manual context switching

**Acceptance Criteria**:
- [ ] **AC-US7-01**: Given a test case has a failed assertion, when clicking "Fix with AI" on that assertion, then the workspace switches to the Editor panel with the SkillImprovePanel open and pre-populated with the failing assertion context (eval_id and failure details)
- [ ] **AC-US7-02**: Given an AI improvement has been generated, when clicking "Apply & Rerun", then the improved SKILL.md content is saved to disk and the failing test case immediately re-runs via SSE
- [ ] **AC-US7-03**: Given multiple iterations have occurred, when viewing the Run panel or WorkspaceHeader, then an iteration counter shows progress (e.g., "Iteration 3: 4/5 passing")
- [ ] **AC-US7-04**: Given all assertions pass for all test cases, when viewing the workspace, then a celebration state renders with a "Run Final A/B Comparison" call-to-action button

---

### US-008: Centralized State Management (P0)
**Project**: vskill

**As a** developer
**I want** shared workspace state via a single hook
**So that** cross-panel interactions work seamlessly without prop drilling or duplicated fetches

**Acceptance Criteria**:
- [ ] **AC-US8-01**: Given the workspace is mounted, when useSkillWorkspace() is called, then it returns shared state including: skillContent, evals, inlineResults, activePanel, selectedCaseId, isDirty, isRunning, iterationCount, and regressions
- [ ] **AC-US8-02**: Given the Editor saves content, when the save completes, then the shared skillContent updates and isDirty resets to false; given a Run completes, then shared inlineResults update for all panels
- [ ] **AC-US8-03**: Given a test case "Run" button is clicked in the Tests panel, when the action fires, then activePanel switches to "run" and scope is set to the selected case ID
- [ ] **AC-US8-04**: Given "Fix with AI" is clicked on a failed assertion, when the action fires, then activePanel switches to "editor" and the improve panel opens with the target eval_id pre-set

## Functional Requirements

### FR-001: New Backend Endpoint
PUT /api/skills/:plugin/:skill/content -- Accepts `{ content: string }` body, writes SKILL.md to disk, returns `{ ok: true }`. Last-write-wins semantics. No conflict detection.

### FR-002: Route Restructuring
- Remove routes: /skills/:plugin/:skill/benchmark, /skills/:plugin/:skill/compare, /skills/:plugin/:skill/history
- Add route: /skills/:plugin/:skill with ?panel= query param
- Preserve: /, /create, /activation routes unchanged

### FR-003: Component Reuse
Existing components to reuse without modification where possible:
- GroupedBarChart, StatsPanel, TrendChart, SkillImprovePanel, McpDependencies, ProgressLog, ModelCompareModal, SkillContentViewer
- SSE hook (useSSE) reused as-is for benchmark streaming

### FR-004: Keyboard Shortcuts
- Ctrl+1 through Ctrl+5: Switch panels (Editor, Tests, Run, History, Deps)
- Ctrl+S: Save SKILL.md (when Editor panel active)
- Ctrl+Enter: Run selected test case
- Ctrl+Shift+Enter: Run all test cases

## Out of Scope

- Responsive/mobile design (min 1024px, dev tool on large monitors)
- Multi-user collaboration or conflict detection
- localStorage persistence of editor state
- Test case virtualization (not needed for 2-15 cases)
- SkillListPage, CreateSkillPage, or ActivationTestPage changes
- Backend changes beyond the single PUT /content endpoint
- Authentication or authorization

## Dependencies

- Existing eval-server REST API (all current endpoints remain stable)
- Existing SSE streaming infrastructure for benchmarks
- Existing component library (GroupedBarChart, StatsPanel, TrendChart, etc.)
- react-router-dom for routing and URL query params

## Success Metrics

- All 4 separate pages consolidated into 1 workspace route
- Zero page navigations required for edit-test-iterate cycle
- Existing functionality fully preserved (no regression in benchmark, comparison, history features)
- All existing components reused (no unnecessary rewrites)
- Max file size stays under 500 lines per component (vs current 1068-line SkillDetailPage)

## Technical Notes

- Tech stack: React 18, TypeScript, Vite, CSS variables + Tailwind (no external UI framework)
- The useSkillWorkspace hook should use React Context to avoid prop drilling
- Panel components should lazy-load only their data on first activation (not all panels at mount)
- Sparkline charts in test case list can use simple inline SVG (no charting library needed)
- Assertion drag-reorder can use HTML5 Drag and Drop API (no library needed)
