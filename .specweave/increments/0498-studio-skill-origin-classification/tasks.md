---
increment: 0498-studio-skill-origin-classification
title: "Studio Skill Origin Classification (Consumed vs Editable)"
total_tasks: 12
completed_tasks: 0
by_user_story:
  US-001: [T-001, T-002]
  US-002: [T-003, T-004]
  US-003: [T-005]
  US-004: [T-006, T-007, T-008, T-009]
  US-005: [T-010]
  cross-cutting: [T-011, T-012]
---

# Tasks: Studio Skill Origin Classification (Consumed vs Editable)

## User Story: US-001 - Origin Classification in Scanner

**Linked ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05
**Tasks**: 2 total, 0 completed

---

### T-001: Implement `classifyOrigin` function and add `origin` to `SkillInfo`

**User Story**: US-001
**Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04
**Status**: [x] completed

**Test Plan**:
- **Given** a skill whose directory relative to root starts with `.claude/`
- **When** `classifyOrigin(dir, root)` is called
- **Then** it returns `"installed"`

- **Given** a skill under `.specweave/`, `.vscode/`, `.idea/`, `.zed/`, `.devcontainer/`, `.github/`, `.agents/`, or `.agent/`
- **When** `classifyOrigin(dir, root)` is called
- **Then** it returns `"installed"`

- **Given** a skill whose relative path contains `plugins/cache/` anywhere in it
- **When** `classifyOrigin(dir, root)` is called
- **Then** it returns `"installed"`

- **Given** a skill at `skills/my-skill` or `marketing/skills/smp` (no agent or cache prefix)
- **When** `classifyOrigin(dir, root)` is called
- **Then** it returns `"source"`

- **Given** `root === dir` (Layout 4 self-layout, empty relative path)
- **When** `classifyOrigin(dir, root)` is called
- **Then** it returns `"source"`

**Test Cases**:
1. **Unit**: `repositories/anton-abyzov/vskill/src/eval/skill-scanner.test.ts`
   - `classifyOrigin_claudeSkillsDir_returnsInstalled()`: rel path `.claude/skills/foo` → `"installed"`
   - `classifyOrigin_cursorSkillsDir_returnsInstalled()`: rel path `.cursor/skills/bar` → `"installed"`
   - `classifyOrigin_ampSkillsDir_returnsInstalled()`: rel path `.amp/skills/x` → `"installed"`
   - `classifyOrigin_specweaveDir_returnsInstalled()`: rel path `.specweave/plugins/something` → `"installed"`
   - `classifyOrigin_vscodeDir_returnsInstalled()`: rel path `.vscode/skills/baz` → `"installed"`
   - `classifyOrigin_pluginsCacheAnywhere_returnsInstalled()`: rel path `some/path/plugins/cache/specweave/skills/foo` → `"installed"`
   - `classifyOrigin_standardNested_returnsSource()`: rel path `plugins/marketing/skills/smp` (no `cache/`) → `"source"`
   - `classifyOrigin_rootLayout_returnsSource()`: rel path `skills/my-skill` → `"source"`
   - `classifyOrigin_emptyRelPath_returnsSource()`: root === dir edge case → `"source"`
   - `classifyOrigin_agentRegistryPrefixes_allReturnInstalled()`: every `localSkillsDir` top-level segment from `AGENTS_REGISTRY` classifies as installed
   - **Coverage Target**: 95%

**Implementation**:
1. In `src/eval/skill-scanner.ts`, import `AGENTS_REGISTRY` from `../agents/agents-registry.js`
2. Add `SkillOrigin = "source" | "installed"` type and `origin: SkillOrigin` to `SkillInfo` interface
3. Build a `Set<string>` of agent directory prefixes once at module level: `localSkillsDir.split('/')[0] + '/'` for each agent entry, deduplicated
4. Add hardcoded extras to the set: `.specweave/`, `.vscode/`, `.idea/`, `.zed/`, `.devcontainer/`, `.github/`, `.agents/`, `.agent/`
5. Implement `classifyOrigin(dir: string, root: string): SkillOrigin`:
   - `relPath = path.relative(root, dir).split(path.sep).join('/')` (normalize separators)
   - Empty relPath → return `"source"`
   - `relPath.includes('plugins/cache/')` → return `"installed"`
   - Any prefix in set where `relPath.startsWith(prefix)` → return `"installed"`
   - Default → return `"source"`
6. Write unit tests (RED), run to confirm failure, then implement (GREEN)
7. `npx tsc --noEmit` to verify no TypeScript errors

---

### T-002: Wire `origin` into all `skills.push()` call sites in `scanSkills`

**User Story**: US-001
**Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05
**Status**: [x] completed

**Test Plan**:
- **Given** a temp filesystem fixture with `.claude/skills/foo/SKILL.md` and `src/skills/bar/SKILL.md`
- **When** `scanSkills(root)` is called
- **Then** foo has `origin: "installed"` and bar has `origin: "source"`

- **Given** the same skill name exists in both a source dir and an installed dir
- **When** `scanSkills(root)` is called
- **Then** both appear with distinct correct `origin` values

- **Given** `scanSkills` runs over any fixture
- **When** results are inspected
- **Then** every `SkillInfo` object has a defined `origin` field (no undefined)

**Test Cases**:
1. **Integration**: `repositories/anton-abyzov/vskill/src/eval/skill-scanner.test.ts` (extends existing)
   - `scanSkills_sourceSkill_hasOriginSource()`: fixture with plain source layout → `origin === "source"`
   - `scanSkills_installedSkill_hasOriginInstalled()`: fixture with `.claude/skills/X/SKILL.md` → `origin === "installed"`
   - `scanSkills_mixedLayout_bothOriginsPresent()`: fixture with both → correct origins on each
   - `scanSkills_noSkillMissingOrigin()`: every result has `origin` defined
   - **Coverage Target**: 90%

**Implementation**:
1. Locate every `skills.push({...})` call site in `scanSkills` and its helper functions
2. Add `origin: classifyOrigin(skillDir, root)` to each push object
3. Ensure `root` is threaded through all helpers that construct `SkillInfo` objects
4. Run `npx tsc --noEmit` to confirm no type errors
5. Write integration tests (RED), implement, run tests (GREEN)

---

## User Story: US-002 - Sidebar Split into Source and Installed Sections

**Linked ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04
**Tasks**: 2 total, 0 completed

---

### T-003: Update frontend types and `StudioContext` to propagate `origin`

**User Story**: US-002
**Satisfies ACs**: AC-US2-01, AC-US2-04
**Status**: [x] completed

**Test Plan**:
- **Given** the API returns a skill with `origin: "installed"`
- **When** the user clicks on that skill in the sidebar
- **Then** `selectedSkill.origin` is `"installed"` in the context

- **Given** the user clicks on a skill with `origin: "source"`
- **When** `StudioContext` updates
- **Then** `selectedSkill.origin` is `"source"`

**Test Cases**:
1. **Unit**: `repositories/anton-abyzov/vskill/src/eval-ui/src/StudioContext.test.tsx`
   - `selectSkill_installedOrigin_propagatesCorrectly()`: selecting installed skill → `selectedSkill.origin === "installed"`
   - `selectSkill_sourceOrigin_propagatesCorrectly()`: selecting source skill → `selectedSkill.origin === "source"`
   - **Coverage Target**: 90%

**Implementation**:
1. In `src/eval-ui/src/types.ts`: add `origin: "source" | "installed"` to `SkillInfo` interface
2. In `src/eval-ui/src/StudioContext.tsx`: add `origin: "source" | "installed"` to `SelectedSkill` type
3. Update `selectSkill` action to include `origin: skill.origin` from the `SkillInfo` object
4. Run `npx tsc --noEmit` to confirm no type errors
5. Write/run unit tests

---

### T-004: Split `SkillGroupList` into "Your Skills" and "Installed" sections

**User Story**: US-002
**Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04
**Status**: [x] completed

**Test Plan**:
- **Given** skills with mixed origins in the sidebar
- **When** `SkillGroupList` renders
- **Then** "Your Skills" section header and "Installed" section header both appear with the correct skills under each

- **Given** all skills have `origin: "source"`
- **When** `SkillGroupList` renders
- **Then** only the "Your Skills" section header appears; no "Installed" header in the DOM

- **Given** all skills have `origin: "installed"`
- **When** `SkillGroupList` renders
- **Then** only the "Installed" section header appears; no "Your Skills" header in the DOM

- **Given** a search filter string is active
- **When** `SkillGroupList` filters results
- **Then** origin-based grouping is preserved within the filtered results

**Test Cases**:
1. **Unit**: `repositories/anton-abyzov/vskill/src/eval-ui/src/components/SkillGroupList.test.tsx`
   - `SkillGroupList_mixedOrigins_showsBothSections()`: both `"Your Skills"` and `"Installed"` headings in DOM
   - `SkillGroupList_allSource_showsOnlyYourSkills()`: "Installed" heading absent
   - `SkillGroupList_allInstalled_showsOnlyInstalled()`: "Your Skills" heading absent
   - `SkillGroupList_searchPreservesGrouping()`: filtered results still split by origin
   - **Coverage Target**: 90%

**Implementation**:
1. In `SkillGroupList.tsx`, partition filtered skills: `sourceSkills = skills.filter(s => s.origin === "source")` and `installedSkills = skills.filter(s => s.origin === "installed")`
2. Within each partition, keep existing plugin-based sub-grouping logic
3. Render `<section data-testid="section-your-skills">` with "Your Skills" header only if `sourceSkills.length > 0`
4. Render `<section data-testid="section-installed">` with "Installed" header only if `installedSkills.length > 0`
5. Write tests (RED), implement (GREEN)

---

## User Story: US-003 - Visual De-emphasis of Installed Skills

**Linked ACs**: AC-US3-01, AC-US3-02, AC-US3-03
**Tasks**: 1 total, 0 completed

---

### T-005: Add lock icon and reduced-opacity styling to installed `SkillCard`

**User Story**: US-003
**Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03
**Status**: [x] completed

**Test Plan**:
- **Given** a `SkillCard` rendered with `skill.origin === "installed"`
- **When** the component renders
- **Then** a lock SVG icon appears next to the skill name and text uses reduced opacity

- **Given** a `SkillCard` rendered with `skill.origin === "source"`
- **When** the component renders
- **Then** no lock icon is shown and full opacity text is applied

**Test Cases**:
1. **Unit**: `repositories/anton-abyzov/vskill/src/eval-ui/src/components/SkillCard.test.tsx`
   - `SkillCard_installedSkill_showsLockIcon()`: element with `data-testid="lock-icon"` present
   - `SkillCard_installedSkill_hasReducedOpacity()`: card text element has opacity/dim class
   - `SkillCard_sourceSkill_noLockIcon()`: no `data-testid="lock-icon"` in DOM
   - `SkillCard_sourceSkill_noReducedOpacity()`: no opacity reduction applied
   - **Coverage Target**: 90%

**Implementation**:
1. In `SkillCard.tsx`, read `skill.origin` from the `SkillInfo` prop (already present after T-003)
2. When `origin === "installed"`: add Tailwind `opacity-55` (or equivalent) to text wrappers; render inline lock SVG with `data-testid="lock-icon"` next to skill name
3. When `origin === "source"`: no icon, existing styles unchanged
4. Write tests (RED), implement (GREEN)

---

## User Story: US-004 - Read-Only Mode for Installed Skills

**Linked ACs**: AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-04
**Tasks**: 4 total, 0 completed

---

### T-006: Thread `origin` into `WorkspaceProvider` and expose `isReadOnly`

**User Story**: US-004
**Satisfies ACs**: AC-US4-01, AC-US4-04
**Status**: [x] completed

**Test Plan**:
- **Given** `WorkspaceProvider` receives `origin: "installed"`
- **When** a consumer reads the workspace context
- **Then** `isReadOnly` is `true`

- **Given** `WorkspaceProvider` receives `origin: "source"`
- **When** a consumer reads the workspace context
- **Then** `isReadOnly` is `false`

- **Given** `isReadOnly` is `true`
- **When** `saveContent` or `runAll` is called on the context
- **Then** the call is a no-op (write/run is blocked)

**Test Cases**:
1. **Unit**: `repositories/anton-abyzov/vskill/src/eval-ui/src/pages/workspace/WorkspaceContext.test.tsx`
   - `WorkspaceProvider_installedOrigin_isReadOnlyTrue()`: context `isReadOnly === true`
   - `WorkspaceProvider_sourceOrigin_isReadOnlyFalse()`: context `isReadOnly === false`
   - `WorkspaceProvider_saveContent_noopWhenReadOnly()`: `saveContent()` called when installed → no side effects
   - `WorkspaceProvider_runAll_noopWhenReadOnly()`: `runAll()` called when installed → no side effects
   - **Coverage Target**: 90%

**Implementation**:
1. Add `origin: "source" | "installed"` prop to `WorkspaceProvider` in `WorkspaceContext.tsx` (and `workspaceTypes.ts` if types are separate)
2. Derive `isReadOnly = origin === "installed"` and expose it on the context value
3. Guard `saveContent`, `saveEvals`, `runCase`, `runAll`, `submitAiEdit`, `generateEvals` with `if (isReadOnly) return`
4. In `RightPanel.tsx` (or wherever `WorkspaceProvider` is instantiated), pass `origin={selectedSkill.origin}`
5. `npx tsc --noEmit` to confirm types

---

### T-007: Disable run buttons in `RunPanel` for installed skills

**User Story**: US-004
**Satisfies ACs**: AC-US4-02
**Status**: [x] completed

**Test Plan**:
- **Given** an installed skill is selected and `RunPanel` renders
- **When** the panel is displayed
- **Then** "Run All" and all per-case "Run" buttons have the `disabled` attribute and show tooltip "Cannot benchmark installed skills"

- **Given** a source skill is selected
- **When** `RunPanel` renders
- **Then** all run buttons are enabled (no `disabled` attribute)

**Test Cases**:
1. **Unit**: `repositories/anton-abyzov/vskill/src/eval-ui/src/pages/workspace/RunPanel.test.tsx`
   - `RunPanel_installedSkill_runAllDisabled()`: "Run All" button has `disabled`
   - `RunPanel_installedSkill_perCaseRunDisabled()`: each per-case "Run" button has `disabled`
   - `RunPanel_sourceSkill_runAllEnabled()`: "Run All" button not disabled
   - **Coverage Target**: 85%

**Implementation**:
1. In `RunPanel.tsx`, consume `isReadOnly` from `WorkspaceContext`
2. Apply `disabled={isReadOnly}` to the "Run All" button
3. Apply `disabled={isReadOnly}` to each per-case run button
4. Add `title="Cannot benchmark installed skills"` to disabled state

---

### T-008: Disable editing controls in `EditorPanel` for installed skills

**User Story**: US-004
**Satisfies ACs**: AC-US4-01, AC-US4-03
**Status**: [x] completed

**Test Plan**:
- **Given** an installed skill is selected and `EditorPanel` renders
- **When** the panel is displayed
- **Then** the textarea has the `readOnly` attribute, the AI Edit button is absent, and the Save button is absent

- **Given** a source skill is selected
- **When** `EditorPanel` renders
- **Then** textarea is editable, AI Edit button is present, Save button is present

**Test Cases**:
1. **Unit**: `repositories/anton-abyzov/vskill/src/eval-ui/src/pages/workspace/EditorPanel.test.tsx`
   - `EditorPanel_installedSkill_textareaReadOnly()`: textarea has `readOnly` attribute
   - `EditorPanel_installedSkill_aiEditButtonHidden()`: AI Edit button not in DOM
   - `EditorPanel_installedSkill_saveButtonHidden()`: Save button not in DOM
   - `EditorPanel_sourceSkill_allControlsPresent()`: both buttons in DOM, textarea editable
   - **Coverage Target**: 85%

**Implementation**:
1. In `EditorPanel.tsx`, consume `isReadOnly` from `WorkspaceContext`
2. Add `readOnly={isReadOnly}` to the textarea element
3. Conditionally render AI Edit button: `{!isReadOnly && <AIEditButton />}`
4. Conditionally render Save button: `{!isReadOnly && <SaveButton />}`

---

### T-009: Disable eval controls in `TestsPanel` and add "Read-only" badge to `DetailHeader`

**User Story**: US-004
**Satisfies ACs**: AC-US4-01, AC-US4-03, AC-US4-04
**Status**: [x] completed

**Test Plan**:
- **Given** an installed skill is selected and `TestsPanel` renders
- **When** the panel is displayed
- **Then** the "Add eval" button is absent and per-eval edit/delete controls are absent

- **Given** an installed skill is selected and `DetailHeader` renders
- **When** the header is displayed
- **Then** a "Read-only" pill badge with a lock icon appears in the header

- **Given** a source skill is selected
- **When** `TestsPanel` and `DetailHeader` render
- **Then** all editing controls are present and no "Read-only" badge appears

**Test Cases**:
1. **Unit**: `repositories/anton-abyzov/vskill/src/eval-ui/src/pages/workspace/TestsPanel.test.tsx`
   - `TestsPanel_installedSkill_addEvalHidden()`: "Add eval" button not in DOM
   - `TestsPanel_installedSkill_editDeleteControlsHidden()`: no edit/delete buttons on evals
   - `TestsPanel_sourceSkill_addEvalPresent()`: "Add eval" button in DOM
2. **Unit**: `repositories/anton-abyzov/vskill/src/eval-ui/src/components/DetailHeader.test.tsx`
   - `DetailHeader_installedSkill_showsReadOnlyBadge()`: text "Read-only" present in DOM
   - `DetailHeader_sourceSkill_noReadOnlyBadge()`: no "Read-only" text
   - **Coverage Target**: 85%

**Implementation**:
1. In `TestsPanel.tsx`, consume `isReadOnly` from `WorkspaceContext`; hide "Add eval" button and per-eval edit/delete controls when `isReadOnly`
2. In `DetailHeader.tsx`, accept `origin` prop (or consume from context); when `"installed"`, render a pill: lock SVG + "Read-only" text with surface-3 background styling
3. Eval list content remains visible in read-only mode (only controls are hidden)

---

## User Story: US-005 - Info Banner Explaining Origin Distinction

**Linked ACs**: AC-US5-01, AC-US5-02, AC-US5-03
**Tasks**: 1 total, 0 completed

---

### T-010: Create `InfoBanner` component and integrate into `SkillGroupList`

**User Story**: US-005
**Satisfies ACs**: AC-US5-01, AC-US5-02, AC-US5-03
**Status**: [x] completed

**Test Plan**:
- **Given** the sidebar has both source and installed skills
- **When** `SkillGroupList` renders
- **Then** the `InfoBanner` appears between the two sections explaining "Your Skills" and "Installed"

- **Given** the user clicks the dismiss button on the `InfoBanner`
- **When** the sidebar re-renders within the same browser session
- **Then** the `InfoBanner` is not shown (sessionStorage key persists the dismissal)

- **Given** only source skills are present (no installed skills)
- **When** `SkillGroupList` renders
- **Then** `InfoBanner` is not shown

- **Given** the banner is visible
- **When** the user reads it
- **Then** it mentions "Your Skills are editable source skills" and "Installed skills are copies consumed by AI agents"

**Test Cases**:
1. **Unit**: `repositories/anton-abyzov/vskill/src/eval-ui/src/components/InfoBanner.test.tsx`
   - `InfoBanner_bothSectionsPresent_isVisible()`: banner renders when `hasSource && hasInstalled`
   - `InfoBanner_onlySource_isHidden()`: banner not rendered when no installed skills
   - `InfoBanner_dismissSetsSessionStorage()`: clicking dismiss sets `sessionStorage.getItem('vskill-origin-banner-dismissed')`
   - `InfoBanner_dismissedState_bannerHidden()`: pre-setting the sessionStorage key hides banner on render
   - `InfoBanner_textContent_explainsDistinction()`: banner text includes "Your Skills" and "Installed"
   - **Coverage Target**: 90%

**Implementation**:
1. Create `src/eval-ui/src/components/InfoBanner.tsx`
2. On mount, check `sessionStorage.getItem('vskill-origin-banner-dismissed')`; if truthy, render `null`
3. Render dismissable banner: "Your Skills are editable source skills you develop. Installed skills are copies consumed by AI agents."
4. Dismiss button: `sessionStorage.setItem('vskill-origin-banner-dismissed', '1')` + hide via state
5. In `SkillGroupList.tsx` (built in T-004), render `<InfoBanner />` between the two sections only when both `sourceSkills.length > 0` and `installedSkills.length > 0`
6. Write tests (RED), implement (GREEN)

---

## Cross-Cutting

**Tasks**: 2 total, 0 completed

---

### T-011: End-to-end type-check and regression verification

**User Story**: cross-cutting
**Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05, AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04, AC-US3-01, AC-US3-02, AC-US3-03, AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-04, AC-US5-01, AC-US5-02, AC-US5-03
**Status**: [x] completed

**Test Plan**:
- **Given** all tasks T-001 through T-010 are complete
- **When** the full Vitest suite runs
- **Then** 0 test failures and 0 TypeScript errors

**Test Cases**:
1. **Regression**: full suite
   - `npx vitest run` in `repositories/anton-abyzov/vskill/` → 0 failures
   - `npx tsc --noEmit` in both root and `src/eval-ui/` → 0 errors
   - **Coverage Target**: all previously passing tests still pass

**Implementation**:
1. Run `npx tsc --noEmit` from `repositories/anton-abyzov/vskill/`
2. Run `npx tsc --noEmit` from `repositories/anton-abyzov/vskill/src/eval-ui/`
3. Run `npx vitest run` from `repositories/anton-abyzov/vskill/`
4. Fix any remaining TypeScript errors or test failures before marking complete

---

### T-012: Manual verification of studio UI

**User Story**: cross-cutting
**Satisfies ACs**: AC-US2-01, AC-US3-01, AC-US3-02, AC-US4-01, AC-US4-02, AC-US5-01
**Status**: [x] completed

**Test Plan**:
- **Given** `npx vskill studio` is run in a project with both source skills and skills under `.claude/skills/`
- **When** the studio UI loads in the browser
- **Then** the sidebar shows "Your Skills" and "Installed" sections, installed cards are visually dimmed with lock icons, selecting an installed skill shows "Read-only" badge, run buttons are disabled, and the info banner is displayed

**Test Cases**:
1. **Manual**: user verification
   - Sidebar shows "Your Skills" section with source skills
   - Sidebar shows "Installed" section with `.claude/skills/` entries
   - Installed skill cards have lock icon and reduced opacity
   - Selecting an installed skill: "Read-only" badge in `DetailHeader`
   - `RunPanel` run buttons are disabled with tooltip
   - `EditorPanel` textarea is read-only, AI Edit / Save hidden
   - `TestsPanel` add/edit/delete controls hidden
   - Info banner appears and dismisses on click
   - **Coverage Target**: 100% of AC scenarios confirmed

**Implementation**:
1. Build the eval-ui: `cd repositories/anton-abyzov/vskill/src/eval-ui && npm run build`
2. Run `npx vskill studio` in a project directory that has both source skills and `.claude/skills/` entries
3. Walk through each verification point above
4. Request user confirmation before marking complete
