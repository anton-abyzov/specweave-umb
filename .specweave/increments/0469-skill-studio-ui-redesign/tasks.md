# Tasks: Skill Studio UI Redesign

## Phase 1: Foundation (Types + State)

### T-001: Extend type system for activation panel
**References**: AC-US1-01
**Status**: [x] Completed
- Added `"activation"` to `PanelId` union type
- Added activation state fields to `WorkspaceState`
- Added 6 activation actions to `WorkspaceAction` union
- Added `runActivationTest` to `WorkspaceContextValue`

### T-002: Add activation reducer cases
**References**: AC-US1-01
**Status**: [x] Completed
- Added default activation state to `initialWorkspaceState`
- Added reducer cases: SET_ACTIVATION_PROMPTS, ACTIVATION_START, ACTIVATION_RESULT, ACTIVATION_DONE, ACTIVATION_ERROR, ACTIVATION_RESET

### T-003: Wire SSE activation in WorkspaceContext
**References**: AC-US1-01
**Status**: [x] Completed
- Added useSSE instance for activation stream
- Created `runActivationTest(prompts)` callback
- Wired SSE events to dispatch actions
- Added "activation" to URL sync panel list

## Phase 2: Grouped Panel Rail

### T-004: Redesign LeftRail with grouped panels
**References**: AC-US1-02
**Status**: [x] Completed
- Replaced flat PANELS array with 3 groups: Build, Evaluate, Insights
- Added group separator lines and 8px uppercase labels
- Added activation icon (target/bullseye)
- Added `isActivationRunning` prop for status dot

## Phase 3: Activation Panel

### T-005: Create ActivationPanel component
**References**: AC-US1-01
**Status**: [x] Completed
- Ported from standalone ActivationTestPage.tsx
- Removed skill selector (uses workspace context)
- Kept ResultRow, MetricCard, ConfusionCell helpers
- Full panel width layout

## Phase 4: Workspace Wiring

### T-006: Wire ActivationPanel into SkillWorkspace
**References**: AC-US1-01, AC-US1-02
**Status**: [x] Completed
- Imported ActivationPanel
- Added rendering condition for activation panel
- Updated keyboard shortcuts from Ctrl+1-5 to Ctrl+1-6
- Passed isActivationRunning to LeftRail

## Phase 5: Navigation Cleanup

### T-007: Remove standalone activation route from App.tsx
**References**: AC-US1-03
**Status**: [x] Completed
- Removed "Activation Test" from NAV_ITEMS (3→2 items)
- Removed /activation route
- Removed ActivationTestPage import and IconActivation

## Phase 6: Run Panel Mode Badges

### T-008: Add mode badges to RunPanel
**References**: AC-US1-04
**Status**: [x] Completed
- Added MODE_BADGE config for Skill/Baseline/Compare with color coding
- Shows badge pill next to case name when running or complete
- Skill=accent blue, Baseline=gray, Compare=purple

## Phase 7: Verification

### T-009: Build and test verification
**Status**: [x] Completed
- `npm run build:eval-ui` — builds without errors (477ms)
- `npx vitest run` — all 921 tests pass
- No E2E test changes needed
