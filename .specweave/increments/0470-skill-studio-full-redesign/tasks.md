---
increment: 0470-skill-studio-full-redesign
by_user_story:
  US-001: [T-004, T-005, T-006, T-007, T-008]
  US-002: [T-009, T-010, T-011]
  US-003: [T-012, T-013, T-014, T-015]
  US-004: [T-016, T-017]
  US-005: [T-001, T-002, T-003]
  US-006: [T-018, T-019]
  US-007: [T-020, T-021]
  US-008: [T-022]
---

# Tasks: Skill Studio Full Redesign

## Phase 1: Foundation (US-005 + Infrastructure)

**Goal**: Establish the CLI entry point, server MIME fix, state management, and remove react-router-dom.

---

## User Story: US-005 - `vskill studio` CLI Command

**Linked ACs**: AC-US5-01, AC-US5-02, AC-US5-03, AC-US5-04, AC-US5-05
**Tasks**: 3 total, 3 completed

---

### T-001: Add `vskill studio` top-level CLI command

**User Story**: US-005
**Satisfies ACs**: AC-US5-01, AC-US5-02, AC-US5-03, AC-US5-04, AC-US5-05
**Status**: [x] completed

**Test Plan**:
- **Given** the vskill CLI is installed and `src/index.ts` is compiled
- **When** `vskill studio --root ./my-project --port 3099` is invoked
- **Then** the server starts on port 3099, the startup banner says "Skill Studio", and `vskill eval serve` still works unchanged

**Test Cases**:
1. **Unit**: `src/commands/eval/__tests__/studio-command.test.ts`
   - `testStudioCommandRegistered()`: Verify `studio` command exists in Commander program with correct description
   - `testStudioCommandAcceptsRootAndPort()`: Verify `--root` and `--port` options are registered
   - `testStudioCommandDelegatesToRunEvalServe()`: Mock `runEvalServe` and verify it is called with parsed args
   - `testEvalServeUnchanged()`: Verify `vskill eval serve` still resolves to `runEvalServe`
   - **Coverage Target**: 90%

**Implementation**:
1. Open `repositories/anton-abyzov/vskill/src/index.ts`
2. Before `program.parse()`, add:
   ```typescript
   program
     .command("studio")
     .description("Launch the Skill Studio UI for local skill development")
     .option("--root <path>", "Root directory (default: current dir)")
     .option("--port <number>", "Port for Skill Studio server")
     .action(async (opts) => {
       const { runEvalServe } = await import("./commands/eval/serve.js");
       const root = opts.root ? resolve(opts.root) : resolve(".");
       const port = opts.port ? parseInt(opts.port, 10) : null;
       await runEvalServe(root, port);
     });
   ```
3. Verify `vskill eval serve` action is unchanged (no modification to existing command)

---

### T-002: Add WebP MIME type to eval server

**User Story**: US-005 (infrastructure for US-007)
**Satisfies ACs**: AC-US7-02
**Status**: [x] completed

**Test Plan**:
- **Given** a `.webp` file exists in `src/eval-ui/public/images/icons/`
- **When** the browser requests `/images/icons/plugin.webp` from the eval server
- **Then** the server responds with `Content-Type: image/webp` and 200 status

**Test Cases**:
1. **Unit**: `src/eval-server/__tests__/mime-types.test.ts`
   - `testWebpMimeTypeReturned()`: Verify `MIME_TYPES['.webp']` equals `'image/webp'`
   - **Coverage Target**: 85%

**Implementation**:
1. Open `repositories/anton-abyzov/vskill/src/eval-server/eval-server.ts`
2. Find the `MIME_TYPES` object
3. Add `.webp: "image/webp"` entry

---

### T-003: Create `StudioContext.tsx` and `useMediaQuery` hook

**User Story**: US-005 (infrastructure for all layout stories)
**Satisfies ACs**: AC-US1-01, AC-US6-01, AC-US6-02, AC-US6-03
**Status**: [x] completed

**Test Plan**:
- **Given** the `StudioProvider` wraps the app
- **When** `selectSkill({ plugin: "foo", skill: "bar" })` is dispatched
- **Then** `useStudio().selectedSkill` returns `{ plugin: "foo", skill: "bar" }`

- **Given** viewport width is 500px
- **When** `useMediaQuery("(max-width: 767px)")` is called
- **Then** the hook returns `true`

**Test Cases**:
1. **Unit**: `src/eval-ui/src/__tests__/StudioContext.test.tsx`
   - `testSelectSkill()`: selectSkill updates selectedSkill state
   - `testClearSelection()`: clearSelection resets selectedSkill to null
   - `testSetMode()`: setMode toggles between "browse" and "create"
   - `testSetSearch()`: setSearch updates searchQuery
   - `testRefreshSkills()`: refreshSkills triggers API call and updates skills list
   - `testInitialState()`: selectedSkill is null, mode is "browse", searchQuery is ""
   - **Coverage Target**: 92%

2. **Unit**: `src/eval-ui/src/__tests__/useMediaQuery.test.ts`
   - `testMatchesNarrowViewport()`: returns true when matchMedia matches
   - `testNoMatchWideViewport()`: returns false when matchMedia does not match
   - `testUpdatesOnResize()`: dispatches change event, hook re-evaluates
   - **Coverage Target**: 90%

**Implementation**:
1. Create `repositories/anton-abyzov/vskill/src/eval-ui/src/StudioContext.tsx`:
   - Define `StudioState` interface with: `selectedSkill`, `mode`, `searchQuery`, `skills`, `skillsLoading`, `skillsError`, `isMobile`, `mobileView`
   - Implement `studioReducer` with actions: `SELECT_SKILL`, `CLEAR_SELECTION`, `SET_MODE`, `SET_SEARCH`, `SET_SKILLS`, `SET_SKILLS_ERROR`, `SET_MOBILE_VIEW`
   - Export `StudioProvider` (wraps `useReducer`) with `api.getSkills()` fetch on mount
   - Export `useStudio()` hook with guard
   - `refreshSkills` action calls `api.getSkills()` and dispatches `SET_SKILLS`

2. Create `repositories/anton-abyzov/vskill/src/eval-ui/src/hooks/useMediaQuery.ts`:
   - Accept `query: string`
   - Use `window.matchMedia(query)` with `addEventListener("change", ...)` cleanup

3. Remove `react-router-dom` from `src/eval-ui/package.json` dependencies
4. Update `src/eval-ui/src/main.tsx` to remove `HashRouter` wrapper

---

## Phase 2: Layout Shell (US-001)

**Goal**: Build the CSS Grid split-pane layout replacing the sidebar+page-route architecture.

---

## User Story: US-001 - Master-Detail Split-Pane Layout

**Linked ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05
**Tasks**: 5 total, 5 completed

---

### T-004: Create `StudioLayout.tsx` CSS Grid shell

**User Story**: US-001
**Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04
**Status**: [x] completed

**Test Plan**:
- **Given** `StudioLayout` is rendered
- **When** inspecting the DOM
- **Then** the root element has `grid-template-columns: 280px 1px 1fr`, left and right panels each have `overflow-y: auto`, and the divider element uses `var(--border-subtle)` background

**Test Cases**:
1. **Component**: `src/eval-ui/src/__tests__/StudioLayout.test.tsx`
   - `testGridTemplateColumns()`: Render StudioLayout, assert root style has `280px 1px 1fr`
   - `testPanelScrollContainers()`: Left and right panels have `overflow-y: auto`
   - `testDividerColor()`: Divider div has background `var(--border-subtle)`
   - `testFullViewportHeight()`: Root has `h-screen` or equivalent height style
   - **Coverage Target**: 88%

**Implementation**:
1. Create `repositories/anton-abyzov/vskill/src/eval-ui/src/components/StudioLayout.tsx`:
   ```tsx
   export function StudioLayout({ left, right }: { left: React.ReactNode; right: React.ReactNode }) {
     return (
       <div style={{ display: "grid", gridTemplateColumns: "280px 1px 1fr", height: "100vh" }}>
         <div style={{ overflowY: "auto", background: "var(--surface-1)" }}>{left}</div>
         <div style={{ background: "var(--border-subtle)" }} />
         <div style={{ overflowY: "auto", background: "var(--surface-0)" }}>{right}</div>
       </div>
     );
   }
   ```
2. Add responsive overrides to `globals.css` (768-1024px: `240px 1px 1fr`; <768px: single column)

---

### T-005: Create `LeftPanel.tsx` container

**User Story**: US-001
**Satisfies ACs**: AC-US1-05
**Status**: [x] completed

**Test Plan**:
- **Given** `LeftPanel` is rendered with a mock `StudioContext`
- **When** the panel mounts
- **Then** the header shows "Skill Studio" brand text, project name from `/api/config`, and the `ModelSelector` component

**Test Cases**:
1. **Component**: `src/eval-ui/src/__tests__/LeftPanel.test.tsx`
   - `testBrandTextVisible()`: "Skill Studio" text is rendered
   - `testProjectNameFromContext()`: Project name from StudioContext appears below brand
   - `testModelSelectorRendered()`: ModelSelector component is mounted
   - **Coverage Target**: 85%

**Implementation**:
1. Create `repositories/anton-abyzov/vskill/src/eval-ui/src/components/LeftPanel.tsx`
2. Compose: `StudioHeader` (brand + project name + ModelSelector) + `SkillSearch` + `NewSkillButton` + `SkillGroupList`
3. `StudioHeader` reads `projectName` from `StudioContext` (loaded by `StudioProvider` via `/api/config`)

---

### T-006: Create `RightPanel.tsx` container

**User Story**: US-001
**Satisfies ACs**: AC-US1-01, AC-US1-02
**Status**: [x] completed

**Test Plan**:
- **Given** `StudioContext.selectedSkill` is null and `mode` is "browse"
- **When** `RightPanel` renders
- **Then** `EmptyState` component with "Select a skill to view details" is shown

- **Given** `StudioContext.mode` is "create"
- **When** `RightPanel` renders
- **Then** `CreateSkillInline` is shown

- **Given** `StudioContext.selectedSkill` is set to a valid skill
- **When** `RightPanel` renders
- **Then** `WorkspaceProvider` with `DetailHeader` + `TabBar` is shown

**Test Cases**:
1. **Component**: `src/eval-ui/src/__tests__/RightPanel.test.tsx`
   - `testEmptyStateWhenNoSelection()`: EmptyState renders when selectedSkill is null
   - `testCreateFormWhenModeIsCreate()`: CreateSkillInline renders when mode is "create"
   - `testWorkspaceWhenSkillSelected()`: WorkspaceProvider renders when selectedSkill is set
   - `testWorkspaceKeyChangesOnSkillSwitch()`: key prop equals `${plugin}/${skill}` causing remount
   - **Coverage Target**: 90%

**Implementation**:
1. Create `repositories/anton-abyzov/vskill/src/eval-ui/src/components/RightPanel.tsx`
2. Read `selectedSkill`, `mode` from `useStudio()`
3. Render branches: null → `EmptyState`, "create" → `CreateSkillInline`, skill → `WorkspaceProvider key={plugin/skill}`

---

### T-007: Rewrite `App.tsx` as `StudioProvider` + `StudioLayout` shell

**User Story**: US-001
**Satisfies ACs**: AC-US1-01, AC-US1-04
**Status**: [x] completed

**Test Plan**:
- **Given** the application loads
- **When** the root DOM is inspected
- **Then** no `<nav>` sidebar exists, no `<Routes>` wrapper exists, and a CSS grid with `280px 1px 1fr` columns is the root layout

**Test Cases**:
1. **Integration**: `src/eval-ui/src/__tests__/App.test.tsx`
   - `testNoSidebarNav()`: No `<nav>` element in rendered tree
   - `testNoHashRouter()`: No `BrowserRouter` or `HashRouter` in tree
   - `testSplitPaneLayout()`: Root div has grid layout with correct columns
   - `testStudioProviderWraps()`: `useStudio()` works without throwing inside App tree
   - **Coverage Target**: 88%

**Implementation**:
1. Rewrite `repositories/anton-abyzov/vskill/src/eval-ui/src/App.tsx`:
   ```tsx
   export function App() {
     return (
       <StudioProvider>
         <StudioLayout
           left={<LeftPanel />}
           right={<RightPanel />}
         />
       </StudioProvider>
     );
   }
   ```
2. Remove all imports: `react-router-dom`, `Routes`, `Route`, `Link`, `useLocation`, `NAV_ITEMS`

---

### T-008: Add responsive CSS breakpoints to `globals.css`

**User Story**: US-001 / US-006
**Satisfies ACs**: AC-US1-04, AC-US6-01, AC-US6-04
**Status**: [x] completed

**Test Plan**:
- **Given** the stylesheet is loaded
- **When** viewport is between 768px and 1024px
- **Then** the `.studio-grid` grid-template-columns resolves to `240px 1px 1fr`

- **Given** viewport is below 768px
- **When** `StudioLayout` is inspected
- **Then** only one column is shown (single-column layout)

**Test Cases**:
1. **Unit (CSS)**: Manual visual verification at each breakpoint
   - Verify 280px column at >1024px
   - Verify 240px column at 768-1024px
   - Verify single-column at <768px
   - **Coverage Target**: N/A (visual)

**Implementation**:
1. Add `.studio-grid` class to `StudioLayout.tsx` root div
2. In `globals.css` add:
   ```css
   @media (max-width: 1024px) and (min-width: 768px) {
     .studio-grid { grid-template-columns: 240px 1px 1fr; }
   }
   @media (max-width: 767px) {
     .studio-grid { grid-template-columns: 1fr; }
   }
   ```

---

## Phase 3: Skill List (US-002 + US-008 partial)

**Goal**: Build the scrollable, searchable, grouped skill list in the left panel.

---

## User Story: US-002 - Scrollable Skill List with Search and Filter

**Linked ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04, AC-US2-05
**Tasks**: 3 total, 3 completed

---

### T-009: Create `SkillSearch.tsx` with 200ms debounce

**User Story**: US-002
**Satisfies ACs**: AC-US2-01, AC-US2-04, AC-US2-05
**Status**: [x] completed

**Test Plan**:
- **Given** the search input is rendered
- **When** the user types "foo"
- **Then** `StudioContext.setSearch` is NOT called immediately but IS called after 200ms

- **Given** search returns no results
- **When** the empty results state is shown
- **Then** "No skills match your search" text and a "Clear search" button are visible; clicking "Clear search" resets the query

**Test Cases**:
1. **Unit**: `src/eval-ui/src/__tests__/SkillSearch.test.tsx`
   - `testDebouncedSearch()`: Fake timers — type, assert setSearch not called at 0ms, advance 200ms, assert called
   - `testSummaryCount()`: Shows "12 skills across 3 plugins" when 12 skills across 3 plugins
   - `testClearButtonResetsQuery()`: Clear button calls setSearch("") and clears input
   - **Coverage Target**: 90%

**Implementation**:
1. Create `repositories/anton-abyzov/vskill/src/eval-ui/src/components/SkillSearch.tsx`
2. Controlled input with local `inputValue` state
3. `useEffect` with `setTimeout(200)` calling `studioContext.setSearch(inputValue)` on change; clear on re-render
4. Show total skill count summary: reads from `useStudio().skills`

---

### T-010: Create `SkillCard.tsx` and `SkillGroupHeader` components

**User Story**: US-002
**Satisfies ACs**: AC-US2-02, AC-US2-03, AC-US3-02
**Status**: [x] completed

**Test Plan**:
- **Given** a `SkillCard` is rendered with `benchmarkStatus: "pass"` and `isSelected: true`
- **When** the DOM is inspected
- **Then** the card has a left border with `var(--accent)` color and `var(--surface-2)` background; status pill shows "Passing" with green color

- **Given** a `SkillGroupHeader` with plugin "core" and 3 skills
- **When** rendered
- **Then** "core" text is visible alongside "(3)" count and an icon slot

**Test Cases**:
1. **Component**: `src/eval-ui/src/__tests__/SkillCard.test.tsx`
   - `testSelectedCardHighlight()`: selected card has accent left border and elevated background
   - `testStatusPillColors()`: pass=green, fail=red, pending=yellow, missing=muted
   - `testCardShowsEvalCount()`: eval count and assertion count displayed
   - `testCardShowsLastBenchmarkDate()`: last benchmark date shown when available
   - `testCardClickCallsSelectSkill()`: clicking card dispatches selectSkill action
   - **Coverage Target**: 92%

2. **Component**: `src/eval-ui/src/__tests__/SkillGroupHeader.test.tsx`
   - `testPluginNameRendered()`: plugin name text visible
   - `testSkillCountDisplayed()`: skill count shown
   - `testIconFallback()`: when no icon, renders `IconSkills` SVG
   - **Coverage Target**: 88%

**Implementation**:
1. Create `repositories/anton-abyzov/vskill/src/eval-ui/src/components/SkillCard.tsx`:
   - Props: `skill: SkillInfo`, `isSelected: boolean`, `onSelect: () => void`
   - Selected state: `borderLeft: "2px solid var(--accent)"`, `background: "var(--surface-2)"`
   - Reuse `STATUS_CONFIG` from former `SkillListPage` (extract to `src/types.ts` or inline)
   - `<button>` instead of `<Link>`, calls `onSelect`

2. Create `repositories/anton-abyzov/vskill/src/eval-ui/src/components/SkillGroupHeader.tsx`:
   - Props: `plugin: string`, `count: number`, `iconUrl?: string`
   - Render icon at 16x16 if `iconUrl` exists, else fallback to `IconSkills` SVG

---

### T-011: Create `SkillGroupList.tsx` and wire StudioContext filtering

**User Story**: US-002
**Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-05
**Status**: [x] completed

**Test Plan**:
- **Given** `StudioContext.searchQuery` is "route" and skills include ["router", "validator"]
- **When** `SkillGroupList` renders
- **Then** only "router" card is shown; "validator" is not in the DOM

- **Given** all skills are filtered out
- **When** `SkillGroupList` renders
- **Then** "No skills match your search" message appears

**Test Cases**:
1. **Integration**: `src/eval-ui/src/__tests__/SkillGroupList.test.tsx`
   - `testFiltersSkillsBySearchQuery()`: Only matching skills rendered
   - `testHidesEmptyGroups()`: Plugin group header hidden when all its skills filtered out
   - `testShowsNoResultsMessage()`: Shows empty results message when 0 matches
   - `testSelectSkillOnCardClick()`: Clicking card updates `selectedSkill` in context
   - **Coverage Target**: 90%

**Implementation**:
1. Create `repositories/anton-abyzov/vskill/src/eval-ui/src/components/SkillGroupList.tsx`
2. Read `skills`, `searchQuery`, `selectedSkill` from `useStudio()`
3. Compute `filteredSkills = useMemo(() => skills.filter(s => s.skill.toLowerCase().includes(debouncedQuery.toLowerCase())), [skills, debouncedQuery])`
4. Group by plugin, hide groups with 0 results
5. Render `SkillGroupHeader` + `SkillCard` per group

---

## Phase 4: Detail Panel (US-003 + US-008 partial)

**Goal**: Build the right panel with tabbed workspace replacing the LeftRail architecture.

---

## User Story: US-003 - Inline Skill Detail with Tabbed Panels

**Linked ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04, AC-US3-05
**Tasks**: 4 total, 4 completed

---

### T-012: Create `TabBar.tsx` horizontal tab bar replacing LeftRail

**User Story**: US-003
**Satisfies ACs**: AC-US3-04, AC-US3-05
**Status**: [x] completed

**Test Plan**:
- **Given** `TabBar` is rendered with `activePanel: "editor"`
- **When** the DOM is inspected
- **Then** the Editor tab has a bottom 2px accent border; all 6 tabs are visible with text + icon

- **Given** `isDirty: true`
- **When** the Editor tab renders
- **Then** an activity dot is visible on the Editor tab

- **Given** user presses Ctrl+3
- **When** the keyboard handler fires
- **Then** `onPanelChange("run")` is called

**Test Cases**:
1. **Component**: `src/eval-ui/src/__tests__/TabBar.test.tsx`
   - `testActiveTabHasAccentBorder()`: active tab has `borderBottom: "2px solid var(--accent)"`
   - `testAllSixTabsRendered()`: 6 tabs visible: editor, tests, run, activation, history, deps
   - `testDirtyDotOnEditorTab()`: isDirty=true shows yellow dot on Editor tab
   - `testRunningDotOnRunTab()`: isRunning=true shows accent dot on Run tab
   - `testActivationDotOnActivationTab()`: isActivationRunning=true shows dot
   - `testRegressionDotOnHistoryTab()`: hasRegressions=true shows red dot on History tab
   - `testCtrl1To6ShortcutsWork()`: Keyboard Ctrl+1..6 fire correct onPanelChange calls
   - **Coverage Target**: 92%

**Implementation**:
1. Create `repositories/anton-abyzov/vskill/src/eval-ui/src/components/TabBar.tsx`
2. Reuse `PANEL_GROUPS` structure from `LeftRail.tsx` — extract to shared constant
3. Horizontal layout: `display: flex`, full-width row with group separators
4. Active tab style: `borderBottom: "2px solid var(--accent)"`, `color: "var(--text-primary)"`
5. Preserve `handleKeyDown` for Ctrl+1..6 using `useEffect` on document

---

### T-013: Create `DetailHeader.tsx` extracting logic from `WorkspaceHeader`

**User Story**: US-003
**Satisfies ACs**: AC-US3-03
**Status**: [x] completed

**Test Plan**:
- **Given** `DetailHeader` is rendered with a skill that has `passRate: 0.85`, `benchmarkStatus: "pass"`
- **When** the header renders
- **Then** breadcrumb shows "pluginName / skillName", pass rate shows "85%", status pill shows "Passing"

**Test Cases**:
1. **Component**: `src/eval-ui/src/__tests__/DetailHeader.test.tsx`
   - `testBreadcrumbFormat()`: Renders "plugin / skill" text
   - `testPassRateDisplay()`: Pass rate percentage displayed correctly
   - `testStatusPillColor()`: Status pill uses correct color from STATUS_CONFIG
   - `testCaseAndAssertionCounts()`: eval count and assertion count shown
   - **Coverage Target**: 90%

**Implementation**:
1. Create `repositories/anton-abyzov/vskill/src/eval-ui/src/components/DetailHeader.tsx`
2. Extract data logic from `WorkspaceHeader` (breadcrumb, status pill, pass rate, counts)
3. Remove `<Link to="/">Skills</Link>` — replace with static `<span>` (list always visible)
4. Accept props from `WorkspaceContext` via `useWorkspace()`

---

### T-014: Modify `WorkspaceContext.tsx` to remove `useSearchParams` dependency

**User Story**: US-003
**Satisfies ACs**: AC-US3-05
**Status**: [x] completed

**Test Plan**:
- **Given** `WorkspaceProvider` is mounted without a `HashRouter` wrapper
- **When** it renders
- **Then** no error is thrown; `useSearchParams` is not imported

- **Given** `WorkspaceProvider` renders with a skill and `activePanel` changes
- **When** the panel changes to "tests"
- **Then** the `activePanel` state updates (local only, no URL sync)

**Test Cases**:
1. **Unit**: `src/eval-ui/src/__tests__/WorkspaceContext.test.tsx`
   - `testNoSearchParamsImport()`: Source file does not import `useSearchParams`
   - `testActivePanelStateUpdates()`: Dispatching SET_PANEL updates state.activePanel
   - `testMountsWithoutRouter()`: WorkspaceProvider renders without Router wrapper
   - **Coverage Target**: 88%

**Implementation**:
1. Edit `repositories/anton-abyzov/vskill/src/eval-ui/src/pages/workspace/WorkspaceContext.tsx`:
   - Remove `import { useSearchParams } from "react-router-dom"` (line 2)
   - Remove `const [searchParams, setSearchParams] = useSearchParams()` (line 26)
   - Remove the `useEffect` that reads panel from URL (lines 125-131)
   - Remove the `useEffect` that writes panel to URL (lines 133-142)

---

### T-015: Modify `SkillWorkspace.tsx` to accept props instead of `useParams`

**User Story**: US-003
**Satisfies ACs**: AC-US3-01, AC-US3-05
**Status**: [x] completed

**Test Plan**:
- **Given** `SkillWorkspace` is rendered with props `{ plugin: "core", skill: "router" }`
- **When** it mounts
- **Then** `WorkspaceProvider` receives `plugin="core"` and `skill="router"`; no `useParams` is called

**Test Cases**:
1. **Component**: `src/eval-ui/src/__tests__/SkillWorkspace.test.tsx`
   - `testAcceptsPropsNotParams()`: renders correctly with plugin/skill as props
   - `testWorkspaceProviderReceivesProps()`: WorkspaceProvider plugin/skill match props
   - `testNoUseParamsCall()`: Source file does not import `useParams`
   - **Coverage Target**: 88%

**Implementation**:
1. Edit `repositories/anton-abyzov/vskill/src/eval-ui/src/pages/workspace/SkillWorkspace.tsx`:
   - Change signature from reading `useParams()` to accepting `{ plugin: string; skill: string }` props
   - Remove `useParams` import
   - Wire `WorkspaceProvider plugin={plugin} skill={skill}`
   - Replace `LeftRail` with `TabBar` in the workspace layout
   - Replace `WorkspaceHeader` with `DetailHeader`

---

## Phase 5: Skill Creation Inline (US-004)

**Goal**: Adapt CreateSkillPage to work inline in the right panel without router navigation.

---

## User Story: US-004 - New Skill Creation Button and Flow

**Linked ACs**: AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-04
**Tasks**: 2 total, 2 completed

---

### T-016: Create `CreateSkillInline.tsx` adapting `CreateSkillPage`

**User Story**: US-004
**Satisfies ACs**: AC-US4-02, AC-US4-03
**Status**: [x] completed

**Test Plan**:
- **Given** `CreateSkillInline` is rendered with an `onCreated` callback
- **When** the form is submitted with valid plugin/skill names
- **Then** `api.createSkill()` is called; on success, `onCreated(plugin, skill)` fires

- **Given** skill creation succeeds
- **When** `onCreated` fires
- **Then** `StudioContext.refreshSkills()` and `selectSkill({ plugin, skill })` are called; mode resets to "browse"

**Test Cases**:
1. **Component**: `src/eval-ui/src/__tests__/CreateSkillInline.test.tsx`
   - `testFormSubmitCallsApiCreate()`: Filling form and submitting calls `api.createSkill`
   - `testOnCreatedCallbackFires()`: Mock api success, assert onCreated called with correct args
   - `testNoUseNavigate()`: Source file does not import `useNavigate`
   - `testValidationErrors()`: Empty plugin/skill names show validation errors
   - **Coverage Target**: 90%

**Implementation**:
1. Create `repositories/anton-abyzov/vskill/src/eval-ui/src/components/CreateSkillInline.tsx`
2. Copy form logic from `CreateSkillPage.tsx`
3. Replace `useNavigate()` redirect with `onCreated(plugin, skill)` callback prop
4. Remove all `react-router-dom` imports

---

### T-017: Add "New Skill" button to `LeftPanel` with active state

**User Story**: US-004
**Satisfies ACs**: AC-US4-01, AC-US4-04
**Status**: [x] completed

**Test Plan**:
- **Given** the left panel is rendered and `mode` is "browse"
- **When** the "New Skill" button is inspected
- **Then** the button has `var(--accent)` background and a plus icon

- **Given** `mode` is "create"
- **When** the button renders
- **Then** the button shows an active/pressed visual state (slightly different background or ring)

**Test Cases**:
1. **Component**: `src/eval-ui/src/__tests__/LeftPanel.test.tsx` (additional cases)
   - `testNewSkillButtonVisible()`: Button rendered with "New Skill" label
   - `testNewSkillButtonAccentBackground()`: Background color is var(--accent)
   - `testNewSkillButtonActiveState()`: When mode="create", button shows active style
   - `testNewSkillButtonClickSetsMode()`: Clicking dispatches setMode("create")
   - **Coverage Target**: 88%

**Implementation**:
1. Add "New Skill" button to `LeftPanel.tsx` below search input
2. Read `mode` from `useStudio()`; when `mode === "create"` apply active style (e.g., opacity 0.85 + ring)
3. `onClick` calls `studioCtx.setMode("create")`

---

## Phase 6: Responsive Layout (US-006)

**Goal**: Single-column layout on narrow viewports with mobile view toggle.

---

## User Story: US-006 - Responsive Layout

**Linked ACs**: AC-US6-01, AC-US6-02, AC-US6-03, AC-US6-04
**Tasks**: 2 total, 2 completed

---

### T-018: Implement mobile view toggle in `StudioContext` and `RightPanel`

**User Story**: US-006
**Satisfies ACs**: AC-US6-01, AC-US6-02, AC-US6-03
**Status**: [x] completed

**Test Plan**:
- **Given** `useMediaQuery("(max-width: 767px)")` returns true
- **When** a `SkillCard` is clicked
- **Then** `mobileView` transitions from "list" to "detail" and the right panel is shown full-width with a back button

- **Given** `mobileView` is "detail" on mobile
- **When** the back button is clicked
- **Then** `mobileView` resets to "list" and the search query is preserved

**Test Cases**:
1. **Integration**: `src/eval-ui/src/__tests__/ResponsiveLayout.test.tsx`
   - `testMobileDefaultShowsList()`: mobileView="list" shows left panel, hides right panel
   - `testSkillSelectSwitchesToDetail()`: selecting skill on mobile sets mobileView="detail"
   - `testBackButtonRestoresList()`: clicking back sets mobileView="list"
   - `testSearchQueryPreservedOnBack()`: searchQuery unchanged after back navigation
   - **Coverage Target**: 88%

**Implementation**:
1. `StudioContext` already has `mobileView` and `isMobile` (from T-003)
2. In `StudioLayout.tsx`: when `isMobile` is true, hide the inactive panel via CSS `display: none` or conditional render
3. In `RightPanel.tsx`: when `isMobile && mobileView === "detail"`, render a back button at top that calls `setMobileView("list")`
4. `selectSkill` action in StudioContext: if `isMobile`, also set `mobileView: "detail"`

---

### T-019: CSS media query single-column layout finalization

**User Story**: US-006
**Satisfies ACs**: AC-US6-01, AC-US6-04
**Status**: [x] completed

**Test Plan**:
- **Given** the page is loaded at 600px viewport width
- **When** `StudioLayout` renders
- **Then** the grid has a single column (no divider, no right panel visible by default)

**Test Cases**:
1. **Visual**: Manual verification at 600px and 900px breakpoints
   - 600px: single column, left panel fills width
   - 900px: two-column with 240px left panel
   - 1100px: two-column with 280px left panel

**Implementation**:
1. Ensure `globals.css` responsive rules (from T-008) are correctly scoped to `.studio-grid`
2. At `<768px`: `grid-template-columns: 1fr` with divider hidden (`display: none`)
3. Verify `overflow-y: auto` persists at all breakpoints

---

## Phase 7: Category Icons (US-007)

**Goal**: One-time Nano Banana Pro icon generation for plugin groups and empty state.

---

## User Story: US-007 - Category Icon Generation via Nano Banana Pro

**Linked ACs**: AC-US7-01, AC-US7-02, AC-US7-03, AC-US7-04, AC-US7-05
**Tasks**: 2 total, 2 completed

---

### T-020: Create `scripts/generate-studio-icons.ts` generation script

**User Story**: US-007
**Satisfies ACs**: AC-US7-01, AC-US7-02, AC-US7-05
**Status**: [x] completed

**Test Plan**:
- **Given** the script runs with a valid Nano Banana Pro API key
- **When** invoked for plugin name "core"
- **Then** a POST request is made to Nano Banana Pro with `responseModalities: ["TEXT", "IMAGE"]`, and the result is saved as `src/eval-ui/public/images/icons/core.webp` at 32x32px

- **Given** the empty-state illustration generation runs
- **When** the script completes
- **Then** `src/eval-ui/public/images/empty-studio.webp` exists at 128x128px

**Test Cases**:
1. **Unit**: `scripts/__tests__/generate-studio-icons.test.ts`
   - `testApiRequestFormat()`: Mock fetch, assert POST to correct Nano Banana endpoint with correct model and prompt
   - `testOutputPathForPlugin()`: Output path matches `icons/{pluginName}.webp`
   - `testEmptyStateIllustrationPath()`: Empty state saved to `empty-studio.webp`
   - **Coverage Target**: 85%

**Implementation**:
1. Create `repositories/anton-abyzov/vskill/scripts/generate-studio-icons.ts`
2. Use native `fetch` to call `POST https://generativelanguage.googleapis.com/v1beta/models/gemini-3-pro-image-preview:generateContent`
3. Read `GOOGLE_API_KEY` from env (VertexAI key: `AIzaSyCdr7OdR7WJ2ofivHKKfv__1sQ4YJKnnrg` stored in `.env`, never hardcoded)
4. Prompt template: `"Minimalist line-art icon representing {pluginName}, white lines on transparent background, 32x32 pixels, single subject, no text"`
5. Extract base64 image data from response, write as WebP to output path
6. Create `src/eval-ui/public/images/icons/` directory if not exists
7. Generate empty-state illustration: 128x128, theme-neutral minimalist illustration

---

### T-021: Wire plugin icons in `SkillGroupHeader` with fallback

**User Story**: US-007
**Satisfies ACs**: AC-US7-03, AC-US7-04
**Status**: [x] completed

**Test Plan**:
- **Given** a generated icon exists at `/images/icons/core.webp`
- **When** `SkillGroupHeader` for plugin "core" renders
- **Then** an `<img>` with `src="/images/icons/core.webp"` and `width="16" height="16"` is rendered

- **Given** no icon exists for plugin "unknown-plugin"
- **When** `SkillGroupHeader` renders for that plugin
- **Then** the `IconSkills` SVG fallback is rendered at 16x16

**Test Cases**:
1. **Component**: `src/eval-ui/src/__tests__/SkillGroupHeader.test.tsx` (additional)
   - `testIconImgRenderedWhenUrlProvided()`: img element with correct src and dimensions
   - `testSvgFallbackWhenNoIcon()`: IconSkills SVG shown when iconUrl is undefined
   - `testOnErrorFallback()`: onError handler switches to SVG fallback if img fails to load
   - **Coverage Target**: 88%

**Implementation**:
1. Update `SkillGroupHeader.tsx` (created in T-010):
   - Try to load icon at `/images/icons/${plugin}.webp`
   - Use `<img>` with `onError` handler that sets fallback state
   - Fallback renders `IconSkills` SVG
2. Pass `iconUrl` from `SkillGroupList` based on known plugin names

---

## Phase 8: Empty States and Error Handling (US-008)

**Goal**: Complete empty states for all UI conditions.

---

## User Story: US-008 - Empty States and Error Handling

**Linked ACs**: AC-US8-01, AC-US8-02, AC-US8-03, AC-US8-04
**Tasks**: 1 total, 1 completed

---

### T-022: Create `EmptyState.tsx` for all empty/error conditions

**User Story**: US-008
**Satisfies ACs**: AC-US8-01, AC-US8-02, AC-US8-03, AC-US8-04
**Status**: [x] completed

**Test Plan**:
- **Given** no skill is selected and mode is "browse"
- **When** `EmptyState` renders with `variant="no-selection"`
- **Then** the generated illustration `empty-studio.webp` is shown (with fallback SVG) and "Select a skill to view details" text in `var(--text-tertiary)` color

- **Given** `scanSkills()` returns zero skills
- **When** `EmptyState` renders with `variant="no-skills"`
- **Then** "No skills found" + root path hint + "Create Your First Skill" button with accent styling

- **Given** skill data fails to load with error "Network error"
- **When** `EmptyState` renders with `variant="error"` and `message="Network error"`
- **Then** error message displays in `var(--red-muted)` background with a "Retry" button

- **Given** search query returns zero matches
- **When** `EmptyState` renders with `variant="no-results"`
- **Then** "No skills match your search" text and a "Clear search" link are shown

**Test Cases**:
1. **Component**: `src/eval-ui/src/__tests__/EmptyState.test.tsx`
   - `testNoSelectionVariant()`: Illustration + "Select a skill" text + muted color
   - `testNoSkillsVariant()`: "No skills found" + hint text + "Create Your First Skill" button
   - `testErrorVariant()`: Error message in red-muted background + retry button visible
   - `testNoResultsVariant()`: "No skills match your search" + "Clear search" link
   - `testCreateFirstSkillButtonCallsSetMode()`: "Create Your First Skill" calls setMode("create")
   - `testRetryButtonCallsRefreshSkills()`: Retry button calls refreshSkills()
   - `testClearSearchCallsSetSearch()`: "Clear search" calls setSearch("")
   - **Coverage Target**: 92%

**Implementation**:
1. Create `repositories/anton-abyzov/vskill/src/eval-ui/src/components/EmptyState.tsx`
2. Accept `variant: "no-selection" | "no-skills" | "error" | "no-results"` and optional `message: string`, `onRetry: () => void`
3. `no-selection`: `<img src="/images/empty-studio.webp" />` with `onError` SVG fallback; centered layout; muted text
4. `no-skills`: existing empty state design from `SkillListPage` (box icon, hint, create button)
5. `error`: `var(--red-muted)` background, error message, retry button
6. `no-results`: search-miss text, "Clear search" link that calls `setSearch("")`

---

## Coverage Summary

| Test File | Type | Target |
|-----------|------|--------|
| `StudioContext.test.tsx` | Unit | 92% |
| `useMediaQuery.test.ts` | Unit | 90% |
| `StudioLayout.test.tsx` | Component | 88% |
| `LeftPanel.test.tsx` | Component | 88% |
| `RightPanel.test.tsx` | Component | 90% |
| `App.test.tsx` | Integration | 88% |
| `SkillSearch.test.tsx` | Unit | 90% |
| `SkillCard.test.tsx` | Component | 92% |
| `SkillGroupHeader.test.tsx` | Component | 88% |
| `SkillGroupList.test.tsx` | Integration | 90% |
| `TabBar.test.tsx` | Component | 92% |
| `DetailHeader.test.tsx` | Component | 90% |
| `WorkspaceContext.test.tsx` | Unit | 88% |
| `SkillWorkspace.test.tsx` | Component | 88% |
| `CreateSkillInline.test.tsx` | Component | 90% |
| `ResponsiveLayout.test.tsx` | Integration | 88% |
| `EmptyState.test.tsx` | Component | 92% |
| `studio-command.test.ts` | Unit | 90% |
| `mime-types.test.ts` | Unit | 85% |
| `generate-studio-icons.test.ts` | Unit | 85% |
| **Overall** | | **90%** |

## AC Coverage Matrix

| AC-ID | Covered By |
|-------|-----------|
| AC-US1-01 | T-003, T-004, T-007 |
| AC-US1-02 | T-004, T-006 |
| AC-US1-03 | T-004 |
| AC-US1-04 | T-004, T-007, T-008 |
| AC-US1-05 | T-005 |
| AC-US2-01 | T-009, T-011 |
| AC-US2-02 | T-010, T-011 |
| AC-US2-03 | T-010 |
| AC-US2-04 | T-009 |
| AC-US2-05 | T-009, T-011 |
| AC-US3-01 | T-006, T-015 |
| AC-US3-02 | T-010 |
| AC-US3-03 | T-013 |
| AC-US3-04 | T-012 |
| AC-US3-05 | T-012, T-014, T-015 |
| AC-US4-01 | T-017 |
| AC-US4-02 | T-016 |
| AC-US4-03 | T-016 |
| AC-US4-04 | T-017 |
| AC-US5-01 | T-001 |
| AC-US5-02 | T-001 |
| AC-US5-03 | T-001 |
| AC-US5-04 | T-001 |
| AC-US5-05 | T-001 |
| AC-US6-01 | T-008, T-018, T-019 |
| AC-US6-02 | T-018 |
| AC-US6-03 | T-018 |
| AC-US6-04 | T-008, T-019 |
| AC-US7-01 | T-020 |
| AC-US7-02 | T-002, T-020 |
| AC-US7-03 | T-021 |
| AC-US7-04 | T-021 |
| AC-US7-05 | T-020 |
| AC-US8-01 | T-022 |
| AC-US8-02 | T-022 |
| AC-US8-03 | T-022 |
| AC-US8-04 | T-009, T-022 |
