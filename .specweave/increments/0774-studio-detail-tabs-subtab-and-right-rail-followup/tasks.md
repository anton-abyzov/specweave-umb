---
increment: 0774-studio-detail-tabs-subtab-and-right-rail-followup
tasks_version: 1
---

# Tasks: Studio detail page — SubTabBar + Overview right-rail

## Legend
- `[ ]` pending | `[x]` completed | `[-]` skipped

---

## PART A — SubTabBar component (US-001 prerequisite)

### T-001: GREEN — create `SubTabBar` component
**User Story**: US-001, US-002 | **Satisfies ACs**: AC-US1-01, AC-US2-01 | **Status**: [x] completed
**Test Plan**: Given an array of 3 sub-tab descriptors and `active="history"` → When `SubTabBar` is called as a pure function → Then 3 buttons render with `role="tab"`, the second has `aria-selected={true}`, others false; clicking a button fires `onChange(id)`
**Files**: `src/eval-ui/src/components/SubTabBar.tsx` (new)

---

### T-002: RED — `SubTabBar` element-tree test
**User Story**: US-001, US-002 | **Satisfies ACs**: AC-US1-01, AC-US2-01 | **Status**: [x] completed
**Test Plan**: Given `SubTabBar({tabs: [...3], active: "history"})` returned tree → When `findAll(role="tab")` runs → Then `tabs.length === 3` and the active tab has `aria-selected: true`
**Files**: `src/eval-ui/src/components/__tests__/SubTabBar.test.tsx` (new)

---

## PART C — SkillOverview right-rail (US-003)

### T-003: GREEN — extract `SkillOverviewRightRail` component (Setup + Credentials sections)
**User Story**: US-003 | **Satisfies ACs**: AC-US3-02 | **Status**: [x] completed
**Test Plan**: Given a plugin/skill prop pair → When `SkillOverviewRightRail` mounts → Then two sections render with `data-testid="overview-rightrail-setup"` (containing `<McpDependencies>`) and `data-testid="overview-rightrail-credentials"` (containing `<CredentialManager>`)
**Files**: `src/eval-ui/src/components/SkillOverviewRightRail.tsx` (new)

---

### T-004: GREEN — wrap `SkillOverview` content in CSS grid + mount right-rail
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-03 | **Status**: [x] completed
**Test Plan**: Given `SkillOverview` rendered → When inspecting the outer container → Then `display: "grid"` and `gridTemplateColumns: "minmax(0, 1fr) 280px"` (or media-query fallback to `"1fr"` for mobile); `SkillOverviewRightRail` element exists in the tree
**Files**: `src/eval-ui/src/components/SkillOverview.tsx`

---

### T-005: REFACTOR — preserve DepsPanel deep-link back-compat
**User Story**: US-003 | **Satisfies ACs**: AC-US3-04 | **Status**: [x] completed
**Test Plan**: Given `?panel=deps` URL on consumer skill → When RightPanel renders → Then `DepsPanel` still mounts (back-compat preserved by 0769 `CONSUMER_BACKCOMPAT_TABS`); no test-only change needed beyond confirming
**Files**: (verification only — no code change)

---

## PART B — RightPanel sub-tab wiring + F-004 safeActive (US-001, US-002, US-004)

### T-006: GREEN — add `SUB_TAB_DESCRIPTORS` + `readInitialSub` + `defaultSubFor` helpers
**User Story**: US-001, US-002 | **Satisfies ACs**: AC-US1-04, AC-US2-01 | **Status**: [x] completed
**Test Plan**: Given `readInitialSub("run", "?panel=run&sub=history")` → returns `"history"`; given unknown sub `"foo"` → returns `"run"` (default for run); given non-sub-bearing tab `"versions"` → returns `""`
**Files**: `src/eval-ui/src/components/RightPanel.tsx` (helpers), `src/eval-ui/src/components/__tests__/RightPanel.subtab-helpers.test.ts` (new — pure helper tests)

---

### T-007: GREEN — `IntegratedDetailShell` reads/writes `?sub=` URL param
**User Story**: US-001, US-002 | **Satisfies ACs**: AC-US1-03, AC-US2-03 | **Status**: [x] completed
**Test Plan**: Given the URL-sync effect → When `active === "run"` and `sub === "history"` → Then URL = `?panel=run&sub=history`; when active changes to `"versions"` → Then `?sub=` is dropped
**Files**: `src/eval-ui/src/components/RightPanel.tsx`

---

### T-008: GREEN — `WorkspacePanel` dispatches on `(active, sub)`
**User Story**: US-001, US-002 | **Satisfies ACs**: AC-US1-02, AC-US2-02 | **Status**: [x] completed
**Test Plan**: Given `(run, history)` → mounts `HistoryPanel`; given `(run, models)` → mounts `LeaderboardPanel`; given `(run, run)` → mounts `RunPanel`; given `(activation, history)` or `(activation, run)` → mounts `ActivationPanel` (history surfaced via the panel's existing in-panel history list)
**Files**: `src/eval-ui/src/components/RightPanel.tsx`

---

### T-009: GREEN — render `SubTabBar` below top-level tab bar when descriptors exist
**User Story**: US-001, US-002 | **Satisfies ACs**: AC-US1-01, AC-US2-01 | **Status**: [x] completed
**Test Plan**: Given source skill with `safeActive === "run"` → SubTabBar with 3 tabs renders below top-level bar; with `safeActive === "activation"` → SubTabBar with 2 tabs; with `safeActive === "versions"` → no SubTabBar
**Files**: `src/eval-ui/src/components/RightPanel.tsx`

---

### T-010: GREEN — F-004 fix: pass `safeActive` to `WorkspaceTabSync` + `WorkspacePanel`
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02 | **Status**: [x] completed
**Test Plan**: Given consumer skill with `activeDetailTab="editor"` → After `applyPersonaRedirect` `safeActive==="overview"` → Both `WorkspaceTabSync` and `WorkspacePanel` receive `"overview"` (not `"editor"`); for source skill with `activeDetailTab="editor"` → `safeActive==="editor"`, no behavior change
**Files**: `src/eval-ui/src/components/RightPanel.tsx`

---

### T-011: GREEN — extend `RightPanel.flatTabs.test.tsx` with sub-tab assertions
**User Story**: US-001, US-002 | **Satisfies ACs**: AC-US1-01, AC-US2-01 | **Status**: [x] completed
**Test Plan**: Source skill on `run` tab → SubTabBar element exists with 3 sub-tabs; source skill on `activation` tab → SubTabBar with 2 sub-tabs; source skill on `versions` → no SubTabBar; consumer skill on `activation` → SubTabBar with 2 sub-tabs
**Files**: `src/eval-ui/src/components/__tests__/RightPanel.flatTabs.test.tsx`

---

## VERIFICATION (US-005)

### T-012: tsc + targeted tests + full build
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01, AC-US5-02, AC-US5-03, AC-US5-04 | **Status**: [x] completed
**Test Plan**: `npx tsc --noEmit` clean; targeted vitest passes (SubTabBar, RightPanel.subtab-helpers, RightPanel.flatTabs, SkillOverview); `npm run build` clean; `npm run build:eval-ui` clean
**Files**: build verification only
