---
increment: 0465-skill-builder-redesign
title: "Skill Builder Redesign: Unified Workspace"
status: completed
total_tasks: 40
completed_tasks: 40
by_user_story:
  US-001: [T-001, T-002, T-003, T-004, T-005]
  US-002: [T-006, T-007, T-008, T-009]
  US-003: [T-010, T-011, T-012, T-013, T-014, T-015]
  US-004: [T-016, T-017]
  US-005: [T-018, T-019, T-020, T-021]
  US-006: [T-022, T-023, T-024]
  US-007: [T-025, T-026, T-027]
  US-008: [T-028, T-029, T-030, T-031]
  INFRA:  [T-032, T-033, T-034, T-035, T-036, T-037, T-038, T-039, T-040]
---

# Tasks: Skill Builder Redesign -- Unified Workspace

> Implementation order follows plan.md section 15. Old pages are deleted only in T-037 after workspace is feature-complete.

---

## User Story: US-008 - Centralized State Management (P0)

> Built first -- all panels depend on it.

**Linked ACs**: AC-US8-01, AC-US8-02, AC-US8-03, AC-US8-04
**Tasks**: 4 total, 0 completed

### T-028: Define workspace types and interfaces

**User Story**: US-008 | **Satisfies ACs**: AC-US8-01 | **Status**: [x] completed

**Test Plan**:
- **Given** the workspace types file exists
- **When** TypeScript compiles the project
- **Then** all interfaces compile without errors and exported types are importable by panel components

**Test Cases**:
1. **Unit**: `src/pages/workspace/__tests__/workspaceTypes.test.ts`
   - testWorkspaceStateShape(): WorkspaceState has all required fields (skillContent, evals, inlineResults, activePanel, selectedCaseId, isDirty, isRunning, iterationCount, regressions)
   - testPanelIdUnion(): PanelId union includes editor|tests|run|history|deps
   - **Coverage Target**: 90%

**Implementation**:
1. Create `src/pages/workspace/workspaceTypes.ts`
2. Define `PanelId`, `WorkspaceState`, `WorkspaceAction`, `WorkspaceContextValue`, `InlineResult`, `RegressionInfo`, `RunMode` types matching plan.md section 3.1-3.3
3. Export all types

---

### T-029: Implement workspaceReducer

**User Story**: US-008 | **Satisfies ACs**: AC-US8-01, AC-US8-02 | **Status**: [x] completed

**Test Plan**:
- **Given** a workspace action is dispatched
- **When** the reducer processes it
- **Then** the returned state is a new object with the correct field updates and no mutation of prior state

**Test Cases**:
1. **Unit**: `src/pages/workspace/__tests__/workspaceReducer.test.ts`
   - testSetPanel(): dispatching SET_PANEL updates activePanel
   - testSetContent(): dispatching SET_CONTENT updates skillContent and sets isDirty=true
   - testContentSaved(): dispatching CONTENT_SAVED sets savedContent=skillContent, isDirty=false
   - testRunStart(): dispatching RUN_START sets isRunning=true, runMode, runScope
   - testRunComplete(): dispatching RUN_COMPLETE sets isRunning=false, updates latestBenchmark and inlineResults
   - testOpenImprove(): dispatching OPEN_IMPROVE sets improveTarget and switches activePanel to "editor"
   - testSelectCase(): dispatching SELECT_CASE sets selectedCaseId
   - testNoMutation(): state reference changes on every action
   - **Coverage Target**: 95%

**Implementation**:
1. Create `src/pages/workspace/workspaceReducer.ts`
2. Implement reducer function handling all actions in plan.md section 3.2
3. Derive `isDirty` as `skillContent !== savedContent` in reducer
4. Export `workspaceReducer` and `initialWorkspaceState`

---

### T-030: Implement SkillWorkspaceProvider and useSkillWorkspace hook

**User Story**: US-008 | **Satisfies ACs**: AC-US8-01, AC-US8-02, AC-US8-03, AC-US8-04 | **Status**: [x] completed

**Test Plan**:
- **Given** SkillWorkspaceProvider wraps a component tree
- **When** a child calls useSkillWorkspace()
- **Then** it receives state and action dispatchers; calling saveContent dispatches CONTENT_SAVED; calling fixWithAI dispatches OPEN_IMPROVE + SET_PANEL:"editor"

**Test Cases**:
1. **Unit**: `src/pages/workspace/__tests__/SkillWorkspaceProvider.test.tsx`
   - testContextAvailable(): useSkillWorkspace() returns non-null context inside provider
   - testThrowsOutsideProvider(): useSkillWorkspace() throws descriptive error outside provider
   - testSaveContent(): saveContent() calls PUT /api/skills/.../content and dispatches CONTENT_SAVED
   - testFixWithAI(): fixWithAI(1, "a1") dispatches OPEN_IMPROVE and SET_PANEL:"editor"
   - testRunBenchmarkRejectedWhenRunning(): runBenchmark() called while isRunning=true returns without dispatching RUN_START
   - testRunBenchmarkSwitchesToRun(): runBenchmark() dispatches SET_PANEL:"run" and sets scope
   - **Coverage Target**: 90%

**Implementation**:
1. Create `src/pages/workspace/SkillWorkspaceProvider.tsx`
2. Create `src/pages/workspace/useSkillWorkspace.ts`
3. Use React Context + useReducer
4. Implement async action creators: saveContent, runBenchmark, runBaseline, runComparison, saveEvals, fixWithAI, applyAndRerun, stopRun
5. On mount: fetch skillContent, evals, latestBenchmark, stats in parallel; dispatch LOADED
6. Expose context value matching `WorkspaceContextValue` interface

---

### T-031: Implement useURLSync hook

**User Story**: US-008 | **Satisfies ACs**: AC-US1-04 | **Status**: [x] completed

**Test Plan**:
- **Given** activePanel changes in workspace state
- **When** useURLSync() effect fires
- **Then** ?panel= query param updates to match; on initial mount the panel from URL is read and dispatched as SET_PANEL

**Test Cases**:
1. **Unit**: `src/pages/workspace/hooks/__tests__/useURLSync.test.ts`
   - testSyncsActivePanelToURL(): panel change updates searchParams
   - testReadsInitialPanelFromURL(): ?panel=history on mount dispatches SET_PANEL:"history"
   - testDefaultsToEditorForInvalidParam(): ?panel=garbage defaults to "editor"
   - testSyncsCaseIdToURL(): selectedCaseId change updates ?case= param
   - **Coverage Target**: 90%

**Implementation**:
1. Create `src/pages/workspace/hooks/useURLSync.ts`
2. Use `useSearchParams` from react-router-dom
3. Sync activePanel + selectedCaseId to URL params in useEffect
4. Read initial values on mount and dispatch

---

## User Story: US-001 - Unified Workspace Shell (P0)

**Linked ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05
**Tasks**: 5 total, 0 completed

### T-001: Implement WorkspaceShell CSS Grid layout

**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02 | **Status**: [x] completed

**Test Plan**:
- **Given** the WorkspaceShell renders
- **When** inspecting the DOM
- **Then** a CSS Grid container with 2 columns (48px, 1fr) and 2 rows (auto, 1fr) exists; the rail occupies the left column spanning both rows

**Test Cases**:
1. **Unit**: `src/pages/workspace/__tests__/WorkspaceShell.test.tsx`
   - testRendersGridContainer(): root element has CSS Grid with correct template columns
   - testRailSpansFullHeight(): LeftRail receives correct grid placement
   - testPanelAreaRenders(): active panel content renders in column 2 row 2
   - testAnimateFadeInOnPanelSwitch(): key={activePanel} on panel container triggers remount
   - **Coverage Target**: 90%

**Implementation**:
1. Create `src/pages/workspace/WorkspaceShell.tsx`
2. Implement CSS Grid layout from plan.md section 7.1
3. Add workspace grid CSS classes to `src/styles/globals.css` (see T-038)
4. Apply `animate-fade-in` class on `key={activePanel}` panel container

---

### T-002: Implement LeftRail navigation component

**User Story**: US-001 | **Satisfies ACs**: AC-US1-02, AC-US2-05 | **Status**: [x] completed

**Test Plan**:
- **Given** the LeftRail renders with activePanel="tests"
- **When** inspecting the 5 icon buttons
- **Then** the Tests button has the active visual state; clicking Editor button dispatches SET_PANEL:"editor"; dirty dot appears on Editor button when isDirty=true

**Test Cases**:
1. **Unit**: `src/pages/workspace/__tests__/LeftRail.test.tsx`
   - testRendersFiveButtons(): exactly 5 icon buttons (Editor, Tests, Run, History, Deps)
   - testActiveButtonHighlighted(): active panel button has aria-current="page"
   - testClickDispatchesSetPanel(): clicking each button dispatches correct SET_PANEL action
   - testDirtyIndicator(): dirty dot visible on Editor button when isDirty=true
   - testRailWidth(): container has 48px width
   - **Coverage Target**: 90%

**Implementation**:
1. Create `src/pages/workspace/LeftRail.tsx`
2. Read activePanel and isDirty from useSkillWorkspace context
3. Define panel config array: [{id, icon, label}] for all 5 panels
4. Render 5 icon buttons with aria-label and aria-current
5. Show dirty dot overlay on Editor icon when isDirty=true

---

### T-003: Implement WorkspaceHeader

**User Story**: US-001 | **Satisfies ACs**: AC-US1-03, AC-US2-05, AC-US6-06 | **Status**: [x] completed

**Test Plan**:
- **Given** the WorkspaceHeader renders with a loaded workspace state
- **When** inspecting the header content
- **Then** breadcrumb shows "pluginName > skillName", pass rate badge is visible, dirty indicator appears when isDirty=true, regression alert banner shows when regressions exist

**Test Cases**:
1. **Unit**: `src/pages/workspace/__tests__/WorkspaceHeader.test.tsx`
   - testBreadcrumb(): renders "plugin > skill" with correct values from context
   - testPassRateBadge(): shows correct pass count and total from latestBenchmark
   - testModelInfo(): shows active model name from workspace state
   - testDirtyIndicator(): asterisk/dot visible when isDirty=true, hidden when false
   - testRegressionBanner(): alert banner visible with count and link when regressions.length > 0
   - testBannerLinkNavigatesToHistory(): clicking banner link dispatches SET_PANEL:"history"
   - **Coverage Target**: 90%

**Implementation**:
1. Create `src/pages/workspace/WorkspaceHeader.tsx`
2. Read plugin, skill, isDirty, latestBenchmark, regressions from useSkillWorkspace
3. Render breadcrumb, pass rate summary badge, active model info
4. Render dirty indicator when isDirty
5. Render regression alert banner when regressions.length > 0

---

### T-004: Implement SkillWorkspace route and wire into App.tsx

**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-04 | **Status**: [x] completed

**Test Plan**:
- **Given** the user navigates to /skills/myplugin/myskill
- **When** the route renders
- **Then** SkillWorkspace mounts with SkillWorkspaceProvider wrapping WorkspaceShell; ?panel=history in URL activates the History panel

**Test Cases**:
1. **Unit**: `src/pages/workspace/__tests__/SkillWorkspace.test.tsx`
   - testMountsProvider(): SkillWorkspaceProvider is ancestor of WorkspaceShell
   - testDefaultPanel(): no ?panel param defaults to "editor"
   - testURLPanelDeepLink(): ?panel=history renders HistoryPanel
   - testExtractsRouteParams(): plugin and skill from URL params reach provider
   - **Coverage Target**: 85%

**Implementation**:
1. Create `src/pages/workspace/SkillWorkspace.tsx`
2. Extract plugin/skill from useParams
3. Wrap with SkillWorkspaceProvider, render WorkspaceShell inside
4. Modify `src/App.tsx`: add route `/skills/:plugin/:skill` -> SkillWorkspace (keep old routes temporarily)
5. Mount useURLSync inside SkillWorkspace

---

### T-005: Implement useKeyboardShortcuts hook

**User Story**: US-001 | **Satisfies ACs**: AC-US1-05, AC-US2-04 | **Status**: [x] completed

**Test Plan**:
- **Given** WorkspaceShell is mounted and useKeyboardShortcuts is registered
- **When** the user presses Ctrl+1
- **Then** SET_PANEL:"editor" is dispatched; Ctrl+S calls saveContent() when Editor panel active; shortcuts suppressed when non-editor input has focus

**Test Cases**:
1. **Unit**: `src/pages/workspace/hooks/__tests__/useKeyboardShortcuts.test.ts`
   - testCtrl1SwitchesToEditor(): keydown Ctrl+1 dispatches SET_PANEL:"editor"
   - testCtrl2SwitchesToTests(): keydown Ctrl+2 dispatches SET_PANEL:"tests"
   - testCtrl3Through5(): panels run/history/deps covered
   - testCtrlSSavesContent(): Ctrl+S calls saveContent when activePanel="editor"
   - testCtrlEnterRunsSelected(): Ctrl+Enter calls runBenchmark with selectedCaseId
   - testCtrlShiftEnterRunsAll(): Ctrl+Shift+Enter calls runBenchmark for all cases
   - testSuppressedInNonEditorInput(): shortcut not fired when non-editor input has focus
   - **Coverage Target**: 90%

**Implementation**:
1. Create `src/pages/workspace/hooks/useKeyboardShortcuts.ts`
2. Register keydown listener on window in useEffect; clean up on unmount
3. Suppression: skip if `document.activeElement` is input/textarea (except Ctrl+S when Editor panel active)
4. Use useSkillWorkspace for dispatch and action creators
5. Register hook inside WorkspaceShell

---

## User Story: US-002 - SKILL.md Editor with Live Preview (P1)

**Linked ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04, AC-US2-05, AC-US2-06
**Tasks**: 4 total, 0 completed

### T-006: Implement EditorPanel shell with view mode switching

**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02 | **Status**: [x] completed

**Test Plan**:
- **Given** the EditorPanel renders
- **When** the view mode is "side-by-side"
- **Then** both textarea and preview pane are visible; switching to "raw" hides the preview; switching to "preview" hides the textarea

**Test Cases**:
1. **Unit**: `src/pages/workspace/panels/__tests__/EditorPanel.test.tsx`
   - testSideBySideLayout(): both panes visible in default split view
   - testRawOnlyMode(): only textarea visible, preview hidden
   - testPreviewOnlyMode(): only preview visible, textarea hidden
   - testViewModeToggles(): clicking mode buttons changes layout
   - testTextareaContainsSkillContent(): textarea value equals skillContent from context
   - **Coverage Target**: 90%

**Implementation**:
1. Create `src/pages/workspace/panels/EditorPanel.tsx`
2. Create `src/pages/workspace/panels/EditorToolbar.tsx` with Raw/Preview/Side-by-side toggle buttons
3. Read skillContent from useSkillWorkspace; textarea onChange dispatches SET_CONTENT
4. CSS Grid split layout per plan.md section 7.2

---

### T-007: Implement MarkdownPreview and FrontmatterCards

**User Story**: US-002 | **Satisfies ACs**: AC-US2-03 | **Status**: [x] completed

**Test Plan**:
- **Given** SKILL.md content with frontmatter
- **When** MarkdownPreview renders
- **Then** frontmatter fields display as key-value cards (not raw YAML); the body renders as formatted pre text

**Test Cases**:
1. **Unit**: `src/pages/workspace/panels/__tests__/MarkdownPreview.test.tsx`
   - testFrontmatterRenderedAsCards(): YAML frontmatter keys/values appear as structured cards (not raw YAML)
   - testBodyAsFormattedText(): markdown body rendered inside pre element
   - testNoRawYAMLVisible(): raw YAML delimiters (---) not visible in preview output
   - testEmptyContent(): renders without error for empty string
   - **Coverage Target**: 90%

**Implementation**:
1. Create `src/pages/workspace/panels/MarkdownPreview.tsx`
2. Create `src/pages/workspace/panels/FrontmatterCards.tsx`
3. Use existing `parseFrontmatter()` utility from `src/utils/`
4. FrontmatterCards renders key-value dl/dt/dd structure
5. Body rendered in `<pre>` element matching SkillContentViewer quality

---

### T-008: Implement editor save flow and dirty indicator

**User Story**: US-002 | **Satisfies ACs**: AC-US2-04, AC-US2-05 | **Status**: [x] completed

**Test Plan**:
- **Given** the editor textarea has unsaved changes
- **When** the user presses Ctrl+S
- **Then** saveContent() is called, PUT /api/skills/:plugin/:skill/content receives the new content, and isDirty becomes false

**Test Cases**:
1. **Unit**: `src/pages/workspace/panels/__tests__/EditorSave.test.tsx`
   - testDirtyStateOnEdit(): changing textarea value sets isDirty=true in state
   - testSaveCallsAPI(): saveContent() triggers PUT /content with correct body
   - testSaveClearsDirtyState(): isDirty=false after successful save
   - testDirtyIndicatorInHeader(): WorkspaceHeader shows indicator when isDirty=true
   - testDirtyIndicatorInRail(): LeftRail Editor button shows dot when isDirty=true
   - **Coverage Target**: 90%

**Implementation**:
1. Dirty state tracked in workspaceReducer via SET_CONTENT / CONTENT_SAVED (T-029)
2. Verify EditorPanel textarea onChange dispatches SET_CONTENT
3. Ctrl+S already wired in useKeyboardShortcuts (T-005) to call saveContent
4. WorkspaceHeader and LeftRail read isDirty and render indicators (T-002, T-003)
5. Write integration smoke test confirming the full save data flow

---

### T-009: Integrate SkillImprovePanel into EditorPanel

**User Story**: US-002 | **Satisfies ACs**: AC-US2-06, AC-US7-01 | **Status**: [x] completed

**Test Plan**:
- **Given** the EditorPanel is active
- **When** clicking "Improve with AI"
- **Then** SkillImprovePanel (existing component) renders inline; when improveTarget is pre-set via fixWithAI(), the panel opens with eval_id already populated

**Test Cases**:
1. **Unit**: `src/pages/workspace/panels/__tests__/EditorPanel.improve.test.tsx`
   - testImprovePanelHiddenByDefault(): SkillImprovePanel not visible initially
   - testImprovePanelOpensOnClick(): clicking "Improve with AI" shows SkillImprovePanel
   - testImproveTargetPrePopulated(): when improveTarget set in context, panel opens with evalId
   - testApplyOutputToTextarea(): applying improvement output updates textarea via SET_CONTENT
   - **Coverage Target**: 85%

**Implementation**:
1. Extend `EditorPanel.tsx` to conditionally render SkillImprovePanel when improveVisible=true
2. Read improveTarget from useSkillWorkspace context; pass evalId to SkillImprovePanel
3. Wire SkillImprovePanel apply callback to dispatch SET_CONTENT
4. Add "Improve with AI" button to EditorToolbar

---

## User Story: US-003 - Test Case Management Panel (P0)

**Linked ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04, AC-US3-05, AC-US3-06, AC-US3-07, AC-US3-08
**Tasks**: 6 total, 0 completed

### T-010: Implement TestsPanel list+detail layout with TestCaseList

**User Story**: US-003 | **Satisfies ACs**: AC-US3-01 | **Status**: [x] completed

**Test Plan**:
- **Given** TestsPanel renders with 3 test cases
- **When** inspecting the layout
- **Then** left sub-panel (280px) shows 3 case rows with status pills and sparklines; clicking a row dispatches SELECT_CASE

**Test Cases**:
1. **Unit**: `src/pages/workspace/panels/__tests__/TestsPanel.test.tsx`
   - testListSubPanelWidth(): TestCaseList container has 280px fixed width
   - testRendersAllCases(): all evals from context appear in list
   - testStatusPills(): pass/fail/pending pills derived from inlineResults
   - testClickSelectsCase(): clicking a row dispatches SELECT_CASE with that case id
   - testSparklineVisible(): Sparkline SVG component rendered per case
   - **Coverage Target**: 90%

**Implementation**:
1. Create `src/pages/workspace/panels/TestsPanel.tsx` with CSS Grid `280px 1fr`
2. Create `src/pages/workspace/panels/TestCaseList.tsx`
3. Create `src/pages/workspace/panels/TestCaseListItem.tsx` with status pill and Sparkline
4. Create `src/pages/workspace/panels/Sparkline.tsx` using inline SVG (extract from BenchmarkPage lines 453-483)
5. Read evals and inlineResults from useSkillWorkspace

---

### T-011: Implement TestCaseDetail with editable fields and inline run results

**User Story**: US-003 | **Satisfies ACs**: AC-US3-02, AC-US3-04 | **Status**: [x] completed

**Test Plan**:
- **Given** a test case is selected
- **When** viewing the right sub-panel
- **Then** prompt and expected output textareas are editable and pre-filled; last run results show per-assertion pass/fail with reasoning text

**Test Cases**:
1. **Unit**: `src/pages/workspace/panels/__tests__/TestCaseDetail.test.tsx`
   - testPromptEditable(): prompt textarea is editable and pre-filled with case prompt
   - testExpectedOutputEditable(): expectedOutput textarea pre-filled
   - testSaveOnBlur(): leaving textarea triggers saveEvals with updated case
   - testInlineRunResults(): when inlineResult exists, assertion results show pass/fail and reasoning
   - testNoResultsState(): shows "No runs yet" placeholder when inlineResult is null
   - **Coverage Target**: 90%

**Implementation**:
1. Create `src/pages/workspace/panels/TestCaseDetail.tsx`
2. Read selectedCaseId from context; find matching eval from evals
3. Render prompt and expectedOutput textareas; onBlur calls saveEvals
4. Create `InlineRunResult` sub-component showing per-assertion pass/fail + reasoning text

---

### T-012: Implement AssertionBuilder with CRUD and drag reorder

**User Story**: US-003 | **Satisfies ACs**: AC-US3-03 | **Status**: [x] completed

**Test Plan**:
- **Given** a test case has 2 assertions
- **When** the AssertionBuilder renders
- **Then** both assertions are listed with edit/delete controls; dragging a row reorders it; clicking "+" adds a new assertion

**Test Cases**:
1. **Unit**: `src/pages/workspace/panels/__tests__/AssertionBuilder.test.tsx`
   - testRendersAllAssertions(): all assertions in the selected case are listed
   - testAddAssertion(): clicking "+" adds a new empty assertion row
   - testEditAssertion(): editing assertion text updates via saveEvals
   - testDeleteAssertion(): clicking delete removes the assertion
   - testDragReorder(): HTML5 drag events reorder assertion list (dragstart/dragover/drop)
   - testFallbackUpDownButtons(): up/down buttons available as fallback to drag
   - **Coverage Target**: 85%

**Implementation**:
1. Create `src/pages/workspace/panels/AssertionBuilder.tsx`
2. Implement add/edit/delete operations calling saveEvals from context
3. Implement HTML5 DnD reorder with `draggable` attribute
4. Add up/down button fallback for each assertion row

---

### T-013: Implement single-case run and A/B Compare from TestsPanel

**User Story**: US-003 | **Satisfies ACs**: AC-US3-05, AC-US3-06 | **Status**: [x] completed

**Test Plan**:
- **Given** a test case is selected in TestsPanel
- **When** clicking its "Run" button
- **Then** runBenchmark([selectedCaseId]) fires and activePanel switches to "run" scoped to that case; clicking "A/B Compare" calls runComparison for that case

**Test Cases**:
1. **Unit**: `src/pages/workspace/panels/__tests__/TestCaseDetail.run.test.tsx`
   - testRunButtonCallsRunBenchmark(): Run button calls runBenchmark with case id
   - testRunSwitchesPanel(): activePanel becomes "run" after clicking Run
   - testABCompareCallsRunComparison(): "A/B Compare" calls runComparison for case id
   - testRunButtonDisabledWhileRunning(): Run button disabled when isRunning=true
   - **Coverage Target**: 90%

**Implementation**:
1. Add "Run" and "A/B Compare" buttons to TestCaseDetail
2. Wire Run button to `runBenchmark([selectedCaseId])` from useSkillWorkspace
3. Wire A/B Compare to `runComparison()` scoped to selected case
4. Disable buttons when isRunning is true

---

### T-014: Implement add test case form

**User Story**: US-003 | **Satisfies ACs**: AC-US3-07 | **Status**: [x] completed

**Test Plan**:
- **Given** the Tests panel is active
- **When** clicking "+ Add Test Case"
- **Then** a form appears for entering prompt, expected output, and assertions; submitting creates the new case via saveEvals and selects it

**Test Cases**:
1. **Unit**: `src/pages/workspace/panels/__tests__/TestCaseForm.test.tsx`
   - testFormAppearsOnAddClick(): form visible after clicking "+ Add Test Case"
   - testFormFieldsEmpty(): prompt and expectedOutput start empty
   - testSubmitCreatesCase(): submitting calls saveEvals with new case appended
   - testCancelHidesForm(): cancel button hides form without saving
   - testNewCaseSelected(): newly created case becomes selectedCaseId
   - **Coverage Target**: 90%

**Implementation**:
1. Create `src/pages/workspace/panels/TestCaseFormModal.tsx`
2. Add "+ Add Test Case" button above TestCaseList
3. On submit: call saveEvals with new eval appended, dispatch SELECT_CASE for new id

---

### T-015: Implement "Suggest Assertions" AI feature

**User Story**: US-003 | **Satisfies ACs**: AC-US3-08 | **Status**: [x] completed

**Test Plan**:
- **Given** a test case has prompt and expected output
- **When** clicking "Suggest Assertions"
- **Then** AI-generated assertions are returned and displayed; each suggestion has Accept/Reject controls; accepted suggestions are appended via saveEvals

**Test Cases**:
1. **Unit**: `src/pages/workspace/panels/__tests__/SuggestAssertions.test.tsx`
   - testSuggestCallsAPI(): clicking "Suggest Assertions" calls the suggest endpoint
   - testSuggestionsRendered(): returned assertions display with Accept/Reject buttons
   - testAcceptAddsAssertion(): clicking Accept appends assertion via saveEvals
   - testRejectHidesSuggestion(): clicking Reject removes that suggestion from UI
   - testLoadingState(): loading indicator shown while API call is in-flight
   - **Coverage Target**: 85%

**Implementation**:
1. Add "Suggest Assertions" button to TestCaseDetail (visible when prompt + expectedOutput non-empty)
2. Call suggest API endpoint (add to api.ts if not present)
3. Render suggestions list below AssertionBuilder with per-suggestion Accept/Reject
4. On Accept: call saveEvals to persist

---

## User Story: US-004 - Assertion Health and Quality Indicators (P1)

**Linked ACs**: AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-04
**Tasks**: 2 total, 0 completed

### T-016: Implement useAssertionHealth hook

**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-04 | **Status**: [x] completed

**Test Plan**:
- **Given** stats and history data are available
- **When** useAssertionHealth() is called
- **Then** it returns a map of assertionId to health flags derived from existing /stats and /history APIs only (no new endpoints)

**Test Cases**:
1. **Unit**: `src/pages/workspace/hooks/__tests__/useAssertionHealth.test.ts`
   - testFlakyDetection(): assertion with 40% pass rate across 4 runs gets Flaky badge
   - testNotFlakyBelow3Runs(): assertion with 40% pass rate but only 2 runs gets no badge
   - testNonDiscriminatingDetection(): assertion passing in both benchmark and baseline gets Non-discriminating badge
   - testRegressionDetection(): assertion passing in run N-1 but failing in run N gets Regression marker
   - testNoNewEndpointsUsed(): hook only reads from /stats and /history (AC-US4-04)
   - testEmptyForNoData(): returns empty map when no history data
   - **Coverage Target**: 90%

**Implementation**:
1. Create `src/pages/workspace/hooks/useAssertionHealth.ts`
2. Read from latestBenchmark and stats/history already in workspace state
3. Flaky: `assertionStats.passRate` between 0.3-0.7 AND runCount >= 3
4. Non-discriminating: passes in latest benchmark AND latest baseline history entry
5. Regression: passed in second-most-recent run, fails in most-recent

---

### T-017: Implement AssertionHealthBadge component

**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02, AC-US4-03 | **Status**: [x] completed

**Test Plan**:
- **Given** an assertion has health data
- **When** AssertionHealthBadge renders
- **Then** yellow "Flaky" badge, gray "Non-discriminating" badge, or red downward arrow for regression; nothing for healthy assertions

**Test Cases**:
1. **Unit**: `src/pages/workspace/panels/__tests__/AssertionHealthBadge.test.tsx`
   - testFlakyBadge(): health={flaky:true} renders yellow "Flaky" badge
   - testNonDiscriminatingBadge(): health={nonDiscriminating:true} renders gray badge
   - testRegressionMarker(): health={regression:true} renders red downward arrow
   - testNoBadgeForHealthy(): health={} renders nothing
   - testMultipleBadges(): can show regression + flaky simultaneously
   - **Coverage Target**: 90%

**Implementation**:
1. Create `src/pages/workspace/panels/AssertionHealthBadge.tsx`
2. Render badge spans with colors using CSS variables (yellow, gray, red)
3. Integrate into AssertionBuilder rows by passing health data from useAssertionHealth

---

## User Story: US-005 - Benchmark Execution Panel (P1)

**Linked ACs**: AC-US5-01, AC-US5-02, AC-US5-03, AC-US5-04, AC-US5-05, AC-US5-06, AC-US5-07
**Tasks**: 4 total, 0 completed

### T-018: Implement RunPanel shell with controls and scope selector

**User Story**: US-005 | **Satisfies ACs**: AC-US5-01, AC-US5-02, AC-US5-07 | **Status**: [x] completed

**Test Plan**:
- **Given** the Run panel is active
- **When** viewing the controls bar
- **Then** "Run All", "Run Baseline", and "Run A/B Comparison" buttons are visible; scope selector shows current scope; clicking Run while isRunning=true shows rejection message

**Test Cases**:
1. **Unit**: `src/pages/workspace/panels/__tests__/RunPanel.test.tsx`
   - testRunAllButtonVisible(): "Run All" button exists
   - testRunBaselineButtonVisible(): "Run Baseline" button exists
   - testRunABButtonVisible(): "Run A/B Comparison" button exists
   - testScopePrefilledFromContext(): when runScope=caseId, "Selected case only" is pre-selected
   - testRejectMessageWhenRunning(): clicking Run while isRunning=true shows "Benchmark already running -- wait or cancel"
   - testAllButtonsDisabledWhileRunning(): buttons disabled when isRunning=true
   - **Coverage Target**: 90%

**Implementation**:
1. Create `src/pages/workspace/panels/RunPanel.tsx`
2. Create `src/pages/workspace/panels/RunControls.tsx`
3. Read isRunning, runScope from useSkillWorkspace context
4. Implement rejection message toast/banner for concurrent run attempt
5. Scope selector: radio/select between "All cases" and "Selected case only"

---

### T-019: Implement useSSEBridge hook for streaming results

**User Story**: US-005 | **Satisfies ACs**: AC-US5-03, AC-US5-04, AC-US5-06 | **Status**: [x] completed

**Test Plan**:
- **Given** a benchmark run is started
- **When** SSE events arrive from the server
- **Then** each event dispatches RUN_EVENT; on completion RUN_COMPLETE is dispatched with final results and inlineResults update in shared state

**Test Cases**:
1. **Unit**: `src/pages/workspace/hooks/__tests__/useSSEBridge.test.ts`
   - testSSEEventDispatched(): each incoming SSE event dispatches RUN_EVENT
   - testCompletionDispatched(): "done" SSE event dispatches RUN_COMPLETE
   - testInlineResultsUpdated(): after RUN_COMPLETE, inlineResults updated for each case
   - testSSEStopOnUnmount(): SSE connection closed when hook unmounts
   - testBridgeForComparisonMode(): comparison mode SSE events handled correctly
   - **Coverage Target**: 90%

**Implementation**:
1. Create `src/pages/workspace/hooks/useSSEBridge.ts`
2. Wrap existing `useSSE` hook from `src/sse.ts`
3. Map SSE events to workspace dispatch actions
4. Handle benchmark, baseline, and comparison SSE event shapes
5. On completion: build InlineResult map and dispatch SET_INLINE_RESULT per case

---

### T-020: Implement RunPanel streaming result display

**User Story**: US-005 | **Satisfies ACs**: AC-US5-03, AC-US5-04, AC-US5-05 | **Status**: [x] completed

**Test Plan**:
- **Given** a benchmark run is in progress
- **When** SSE events stream in
- **Then** per-case CaseResultCards animate in with fade-in; progress bar shows "2/5 cases"; on completion a pass rate summary card and GroupedBarChart render

**Test Cases**:
1. **Unit**: `src/pages/workspace/panels/__tests__/RunPanel.streaming.test.tsx`
   - testProgressBar(): progress bar shows correct fraction during run
   - testCaseResultCardAnimatesIn(): new case result has animate-fade-in class
   - testGroupedBarChartRendersOnComplete(): GroupedBarChart appears after RUN_COMPLETE
   - testRunSummaryShowsPassRate(): overall pass rate percentage displayed
   - testComparisonCards(): A/B mode renders ComparisonResultCard instead of CaseResultCard
   - **Coverage Target**: 90%

**Implementation**:
1. Create `src/pages/workspace/panels/CaseResultCard.tsx`
2. Create `src/pages/workspace/panels/ComparisonResultCard.tsx` (extract ScoreBar/ScoreRow from ComparisonPage)
3. Create `src/pages/workspace/panels/RunSummary.tsx`
4. Create `src/pages/workspace/panels/RunProgress.tsx` (progress bar)
5. Compose into RunPanel; reuse existing GroupedBarChart and ProgressLog components

---

### T-021: Wire RunPanel results back to Tests panel via shared state

**User Story**: US-005 | **Satisfies ACs**: AC-US5-06 | **Status**: [x] completed

**Test Plan**:
- **Given** a run completes from the Run panel
- **When** the user switches to the Tests panel
- **Then** each test case list item shows the updated pass/fail status pill without a page reload

**Test Cases**:
1. **Integration**: `src/pages/workspace/__tests__/CrossPanel.test.tsx`
   - testInlineResultsSharedAfterRun(): run completion updates inlineResults in context; TestCaseListItem reads updated status
   - testTestsPanelStatusPillUpdates(): switching to Tests panel after run shows correct pills
   - **Coverage Target**: 85%

**Implementation**:
1. Verify reducer RUN_COMPLETE action updates `inlineResults` map keyed by evalId
2. Verify TestCaseListItem reads inlineResults from context to derive status pill color
3. Integration test confirms the cross-panel data flow end-to-end

---

## User Story: US-006 - History and Regression Detection Panel (P1)

**Linked ACs**: AC-US6-01, AC-US6-02, AC-US6-03, AC-US6-04, AC-US6-05, AC-US6-06, AC-US6-07
**Tasks**: 3 total, 0 completed

### T-022: Implement HistoryPanel with tab bar and TimelineView

**User Story**: US-006 | **Satisfies ACs**: AC-US6-01, AC-US6-02, AC-US6-03 | **Status**: [x] completed

**Test Plan**:
- **Given** the History panel is active
- **When** viewing the Timeline tab
- **Then** historical runs list with model, type, date, pass rate; filter controls for model/type/date; selecting 2 runs enables "Compare" button

**Test Cases**:
1. **Unit**: `src/pages/workspace/panels/__tests__/HistoryPanel.test.tsx`
   - testThreeTabsRendered(): Timeline, Per-Eval, Statistics tabs visible
   - testTimelineListRendered(): runs list with model/type/date/passRate per row
   - testFilterByModel(): selecting model filter narrows list to matching runs
   - testFilterByType(): type filter (benchmark/comparison/baseline) works
   - testCompareButtonEnablesOnTwo(): "Compare" button disabled with fewer than 2 selections, enabled with exactly 2
   - testCompareViewRendered(): selecting 2 runs and clicking Compare shows diff view
   - **Coverage Target**: 90%

**Implementation**:
1. Create `src/pages/workspace/panels/HistoryPanel.tsx`
2. Create `src/pages/workspace/panels/TimelineView.tsx` with FilterBar, RunTimeline, SingleRunDetail, CompareView
3. History data fetched in panel-local state (not workspace context per plan.md section 10.4)
4. Wire 2-run selection and Compare flow

---

### T-023: Implement Per-Eval heatmap tab

**User Story**: US-006 | **Satisfies ACs**: AC-US6-04, AC-US6-05 | **Status**: [x] completed

**Test Plan**:
- **Given** the Per-Eval tab is active
- **When** viewing the heatmap
- **Then** rows=assertions, columns=runs (most recent rightmost), cells green/red; clicking a cell opens detail overlay with output text and reasoning

**Test Cases**:
1. **Unit**: `src/pages/workspace/panels/__tests__/HistoryPerEvalTab.test.tsx`
   - testReusesExistingComponent(): HistoryPerEval existing component is rendered inside the tab
   - testCellClickOpensOverlay(): clicking a cell renders detail overlay with output and reasoning
   - testMostRecentOnRight(): column order is chronological, most recent last (rightmost)
   - **Coverage Target**: 85%

**Implementation**:
1. Add Per-Eval tab to HistoryPanel rendering existing `HistoryPerEval` component from `src/components/`
2. Wire cell-click to detail overlay (check if HistoryPerEval already supports it; add if not)

---

### T-024: Implement Statistics tab and regression detection

**User Story**: US-006 | **Satisfies ACs**: AC-US6-06, AC-US6-07 | **Status**: [x] completed

**Test Plan**:
- **Given** the Statistics tab is active
- **When** viewing the content
- **Then** existing StatsPanel and TrendChart render; when regressions are detected and dispatched to context, WorkspaceHeader shows regression banner with count and History link

**Test Cases**:
1. **Unit**: `src/pages/workspace/panels/__tests__/HistoryStats.test.tsx`
   - testStatsPanelReused(): StatsPanel existing component renders in Statistics tab
   - testTrendChartReused(): TrendChart existing component renders in Statistics tab
   - testRegressionBannerInHeader(): when SET_REGRESSIONS dispatched, WorkspaceHeader shows banner
   - testBannerLinkNavigatesToHistory(): clicking banner link dispatches SET_PANEL:"history"
   - **Coverage Target**: 85%

**Implementation**:
1. Add Statistics tab rendering existing StatsPanel and TrendChart
2. After history load in HistoryPanel, compute regressions; dispatch SET_REGRESSIONS to workspace context
3. WorkspaceHeader reads regressions and renders banner (already wired in T-003)

---

## User Story: US-007 - Edit-Test-Iterate Tight Loop (P0)

**Linked ACs**: AC-US7-01, AC-US7-02, AC-US7-03, AC-US7-04
**Tasks**: 3 total, 0 completed

### T-025: Implement "Fix with AI" cross-panel flow

**User Story**: US-007 | **Satisfies ACs**: AC-US7-01 | **Status**: [x] completed

**Test Plan**:
- **Given** a test case has a failed assertion
- **When** clicking "Fix with AI" on that assertion
- **Then** activePanel switches to "editor", SkillImprovePanel opens, and it is pre-populated with the failing assertion's eval_id and failure details

**Test Cases**:
1. **Integration**: `src/pages/workspace/__tests__/FixWithAI.test.tsx`
   - testFixWithAIDispatchesOpenImprove(): clicking Fix with AI dispatches OPEN_IMPROVE with correct evalId
   - testActivePanelSwitchesToEditor(): after dispatch, activePanel becomes "editor"
   - testImprovePanelPrePopulated(): EditorPanel reads improveTarget from context and opens SkillImprovePanel with evalId
   - **Coverage Target**: 90%

**Implementation**:
1. Add "Fix with AI" button to InlineRunResult (in TestCaseDetail) for each failed assertion
2. Button calls `fixWithAI(evalId, assertionId)` from useSkillWorkspace
3. SkillWorkspaceProvider.fixWithAI dispatches OPEN_IMPROVE + SET_PANEL:"editor"
4. EditorPanel reads improveTarget from context and opens SkillImprovePanel (T-009)

---

### T-026: Implement "Apply & Rerun" flow with iteration counter

**User Story**: US-007 | **Satisfies ACs**: AC-US7-02, AC-US7-03 | **Status**: [x] completed

**Test Plan**:
- **Given** an AI improvement has been generated in SkillImprovePanel
- **When** clicking "Apply & Rerun"
- **Then** improved content saves to disk, the failing test case immediately re-runs via SSE, and the iteration counter increments

**Test Cases**:
1. **Integration**: `src/pages/workspace/__tests__/ApplyAndRerun.test.tsx`
   - testApplyAndRerunSavesContent(): calls PUT /content with improved content
   - testApplyAndRerunTriggersRun(): after save, runBenchmark fires for the target case
   - testIterationCounterIncrements(): iterationCount in state increments after each Apply & Rerun
   - testIterationDisplayed(): WorkspaceHeader shows "Iteration N: X/Y passing"
   - **Coverage Target**: 90%

**Implementation**:
1. Extend `applyAndRerun(content, evalId)` in SkillWorkspaceProvider: save content then call runBenchmark([evalId])
2. Dispatch INCREMENT_ITERATION after each applyAndRerun
3. Wire SkillImprovePanel "Apply" button to `applyAndRerun` from context
4. Display iteration counter in WorkspaceHeader

---

### T-027: Implement all-passing celebration state

**User Story**: US-007 | **Satisfies ACs**: AC-US7-04 | **Status**: [x] completed

**Test Plan**:
- **Given** a run completes with all assertions passing for all test cases
- **When** viewing the workspace
- **Then** a celebration state renders with a "Run Final A/B Comparison" call-to-action button

**Test Cases**:
1. **Unit**: `src/pages/workspace/__tests__/CelebrationState.test.tsx`
   - testCelebrationAppearsOnAllPass(): when all inlineResults are pass and iterationCount > 0, celebration component renders
   - testCelebrationHiddenWithFailures(): any failed assertion hides celebration
   - testFinalABButton(): celebration shows "Run Final A/B Comparison" button
   - testFinalABButtonCallsRunComparison(): clicking button calls runComparison()
   - **Coverage Target**: 90%

**Implementation**:
1. Derive `allPassing` boolean from inlineResults in WorkspaceShell or SkillWorkspace
2. Render celebration banner when allPassing=true and iterationCount > 0
3. Include "Run Final A/B Comparison" button calling runComparison from context

---

## Infrastructure Tasks

### T-032: Add PUT /api/skills/:plugin/:skill/content backend endpoint

**User Story**: INFRA | **Satisfies ACs**: AC-US2-04 (FR-001) | **Status**: [x] completed

**Test Plan**:
- **Given** a PUT request to /api/skills/:plugin/:skill/content with `{ content: "..." }`
- **When** the handler processes it
- **Then** SKILL.md is written to disk for the given plugin/skill and `{ ok: true }` is returned

**Test Cases**:
1. **Unit**: `src/eval-server/__tests__/content-endpoint.test.ts`
   - testPUTWritesFile(): PUT /content writes content to correct SKILL.md path
   - testReturnsOkTrue(): response body is { ok: true }
   - testLastWriteWins(): two sequential PUTs result in last content on disk
   - testInvalidPlugin(): 404 for unknown plugin/skill
   - **Coverage Target**: 90%

**Implementation**:
1. Add PUT route to `src/eval-server/api-routes.ts` in existing `registerRoutes`
2. Use same path resolution as existing skill endpoints
3. Write content to `SKILL.md` with `fs.writeFile`
4. Add `saveSkillContent(plugin, skill, content)` method to `src/eval-ui/src/api.ts`

---

### T-033: Implement DepsPanel (thin wrapper around McpDependencies)

**User Story**: INFRA | **Satisfies ACs**: AC-US1-02 (5th panel) | **Status**: [x] completed

**Test Plan**:
- **Given** the Deps panel is active
- **When** DepsPanel renders
- **Then** existing McpDependencies component renders with correct plugin/skill props from context

**Test Cases**:
1. **Unit**: `src/pages/workspace/panels/__tests__/DepsPanel.test.tsx`
   - testMcpDependenciesRendered(): McpDependencies component is mounted
   - testCorrectPropsForwarded(): plugin and skill from context passed to McpDependencies
   - **Coverage Target**: 85%

**Implementation**:
1. Create `src/pages/workspace/panels/DepsPanel.tsx`
2. Read plugin, skill from useSkillWorkspace
3. Render `<McpDependencies plugin={plugin} skill={skill} />`

---

### T-034: Implement panel lazy loading on first activation

**User Story**: INFRA | **Satisfies ACs**: AC-US8-01 (performance) | **Status**: [x] completed

**Test Plan**:
- **Given** the workspace mounts on the editor panel
- **When** inspecting network calls on mount
- **Then** HistoryPanel does not fetch history data until first activated; RunPanel does not initialize SSE until Run panel is activated

**Test Cases**:
1. **Unit**: `src/pages/workspace/__tests__/LazyPanel.test.tsx`
   - testHistoryNotFetchedOnMount(): history API not called on workspace mount
   - testHistoryFetchedOnFirstActivation(): switching to History panel triggers history fetch
   - testSecondActivationNoRefetch(): switching away and back to History does not re-fetch
   - **Coverage Target**: 85%

**Implementation**:
1. Use `hasActivated` panel-local state pattern in HistoryPanel and RunPanel
2. Each panel fetches supplemental data on first render only
3. Workspace mount only fetches: skillContent, evals, latestBenchmark, stats (plan.md 3.4)

---

### T-035: Wire all panels into WorkspaceShell conditional render

**User Story**: INFRA | **Satisfies ACs**: AC-US1-01 (all panels accessible) | **Status**: [x] completed

**Test Plan**:
- **Given** the workspace is rendered with activePanel set to each PanelId
- **When** each panel is activated
- **Then** exactly one panel renders at a time; the correct component renders for each panel id

**Test Cases**:
1. **Unit**: `src/pages/workspace/__tests__/WorkspaceShell.panels.test.tsx`
   - testEditorPanelActive(): activePanel="editor" renders EditorPanel
   - testTestsPanelActive(): activePanel="tests" renders TestsPanel
   - testRunPanelActive(): activePanel="run" renders RunPanel
   - testHistoryPanelActive(): activePanel="history" renders HistoryPanel
   - testDepsPanelActive(): activePanel="deps" renders DepsPanel
   - testOnlyOnePanelVisible(): only one panel in DOM at a time
   - **Coverage Target**: 90%

**Implementation**:
1. Update WorkspaceShell.tsx panel area to conditionally render based on activePanel
2. Use object map or switch: `{ editor: EditorPanel, tests: TestsPanel, ... }[activePanel]`
3. Wrap in `<div key={activePanel} className="animate-fade-in">`

---

### T-036: End-to-end smoke test: full workspace flow

**User Story**: INFRA | **Satisfies ACs**: All (smoke coverage) | **Status**: [x] completed

**Test Plan**:
- **Given** the workspace loads for a skill with 2 test cases
- **When** the user completes an edit-test-iterate cycle (edit -> run -> see results -> fix with AI -> apply & rerun)
- **Then** all panel transitions work, results update cross-panel, and no page navigations occur

**Test Cases**:
1. **Integration**: `src/pages/workspace/__tests__/WorkspaceSmoke.test.tsx`
   - testWorkspaceLoads(): workspace renders without errors on mount
   - testPanelSwitching(): switching all 5 panels works without unmounting provider
   - testEditAndSave(): typing in editor + Ctrl+S saves via PUT /content
   - testRunAndSeeResults(): triggering run shows progress bar and result cards
   - testCrossPanelResults(): after run, Tests panel shows updated status pills
   - testKeyboardShortcuts(): Ctrl+1 through Ctrl+5 switch panels
   - **Coverage Target**: 80%

**Implementation**:
1. Create integration test with mocked API (vi.mock or MSW)
2. Mock SSE to emit synthetic events
3. Test full user journey end-to-end

---

### T-037: Remove old routes and delete legacy page files

**User Story**: INFRA | **Satisfies ACs**: AC-US1-01 (FR-002) | **Status**: [x] completed

**Test Plan**:
- **Given** workspace is feature-complete (T-001 through T-035 done)
- **When** old routes are removed from App.tsx
- **Then** /benchmark, /compare, /history routes no longer exist; project compiles without errors from deleted files

**Test Cases**:
1. **Unit**: `src/pages/workspace/__tests__/RouteCleanup.test.tsx`
   - testOldRoutesRemoved(): App.tsx route config no longer contains BenchmarkPage, ComparisonPage, HistoryPage imports
   - testSkillDetailPageRemoved(): SkillDetailPage route replaced by SkillWorkspace
   - testNoBuildErrors(): `npm run build` exits 0 with no dangling import errors
   - **Coverage Target**: 80%

**Implementation**:
1. Remove from App.tsx: BenchmarkPage, ComparisonPage, HistoryPage, SkillDetailPage routes and imports
2. Delete: `SkillDetailPage.tsx`, `BenchmarkPage.tsx`, `ComparisonPage.tsx`, `HistoryPage.tsx`
3. Run `npm run build` to confirm no dangling imports
4. Add redirect from old benchmark/compare/history URLs to workspace with correct ?panel= if needed

---

### T-038: Add CSS globals for workspace layout

**User Story**: INFRA | **Satisfies ACs**: AC-US1-01, AC-US1-02 (visual layout) | **Status**: [x] completed

**Test Plan**:
- **Given** the workspace renders in a 1024px+ viewport
- **When** inspecting computed styles
- **Then** CSS Grid layout matches plan.md section 7.1; workspace fills full viewport height; no horizontal overflow

**Test Cases**:
1. **Unit**: `src/pages/workspace/__tests__/WorkspaceLayout.test.tsx`
   - testGridTemplateColumns(): workspace-shell has 48px 1fr column template
   - testRailFullHeight(): rail spans both grid rows
   - testPanelAreaScrollable(): panel area has overflow:auto
   - **Coverage Target**: 80%

**Implementation**:
1. Add CSS classes to `src/styles/globals.css`: `.workspace-shell`, `.workspace-rail`, `.workspace-header`, `.workspace-panel`
2. Follow exact CSS from plan.md section 7.1
3. Ensure `height: 100%` propagates from root to workspace container

---

### T-039: Accessibility and aria attributes for workspace navigation

**User Story**: INFRA | **Satisfies ACs**: AC-US1-02 (accessible navigation) | **Status**: [x] completed

**Test Plan**:
- **Given** the workspace renders
- **When** a screen reader navigates
- **Then** left rail buttons have aria-label; active panel button has aria-current="page"; panel area has role="region" with aria-label

**Test Cases**:
1. **Unit**: `src/pages/workspace/__tests__/WorkspaceA11y.test.tsx`
   - testRailButtonAriaLabels(): all 5 rail buttons have descriptive aria-label attributes
   - testActiveButtonAriaCurrent(): active panel button has aria-current="page"
   - testPanelRegionRole(): panel area has role="region" or role="main"
   - testKeyboardFocusOrder(): tab order reaches all interactive elements
   - **Coverage Target**: 85%

**Implementation**:
1. Add aria-label to each LeftRail button (e.g., "Editor panel")
2. Set aria-current="page" on active rail button
3. Add role="region" aria-label to panel container div
4. Verify tab order in LeftRail and WorkspaceHeader

---

### T-040: Final validation -- run full test suite and build

**User Story**: INFRA | **Satisfies ACs**: All (regression guard) | **Status**: [x] completed

**Test Plan**:
- **Given** all implementation tasks T-001 through T-039 are complete
- **When** running the full test suite
- **Then** all tests pass, coverage targets met, and `npm run build` succeeds

**Test Cases**:
1. **Suite**: `npx vitest run --coverage` in `repositories/anton-abyzov/vskill/src/eval-ui/`
   - All new tests pass
   - Coverage >= 90% for new workspace files
   - No pre-existing tests broken
2. **Build**: `npm run build` exits 0
3. **Manual smoke**: Workspace loads, all 5 panels render, keyboard shortcuts work

**Implementation**:
1. Run `npx vitest run` in eval-ui directory
2. Fix any failing tests
3. Run `npm run build` to verify production build
4. Check coverage report against per-file targets
