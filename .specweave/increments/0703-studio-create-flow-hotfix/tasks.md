---
increment: 0703-studio-create-flow-hotfix
status: ready_for_review
---

# Tasks: Skill Studio create flow hotfix

> Retrospective tasks.md. All code shipped in vskill 0.5.98. Every task is [x] completed.

## Task Notation

- `[x]`: Completed
- `[P]`: Parallelizable

---

## Phase 1: Prefill effect — US-001

### T-001: Write aiPrompt and description from URL on mount
**User Story**: US-001 | **AC**: AC-US1-01, AC-US1-02 | **Status**: [x] completed
**File**: `repositories/anton-abyzov/vskill/src/eval-ui/src/pages/CreateSkillPage.tsx`
**Test Plan**: Given `?description=Does+X` in URL → When CreateSkillPage mounts → Then `sk.setAiPrompt("Does X")` and `sk.setDescription("Does X")` are both called
**Test**: `repositories/anton-abyzov/vskill/src/eval-ui/src/pages/__tests__/CreateSkillPage.prefill.test.tsx` (case: "AC-US1-01: copies ?description=… into aiPrompt so Generate is enabled")

### T-002: Guard prefill — no-op when description param absent
**User Story**: US-001 | **AC**: AC-US1-03 | **Status**: [x] completed
**File**: `repositories/anton-abyzov/vskill/src/eval-ui/src/pages/CreateSkillPage.tsx`
**Test Plan**: Given URL with no `?description` → When CreateSkillPage mounts → Then `setAiPrompt` is never called
**Test**: `repositories/anton-abyzov/vskill/src/eval-ui/src/pages/__tests__/CreateSkillPage.prefill.test.tsx` (case: "AC-US1-03: leaves aiPrompt alone when no ?description param is present")

---

## Phase 2: Duplicate pre-check endpoint — US-002

### T-003: Add makeSkillExistsHandler factory with shared validation
**User Story**: US-002 | **AC**: AC-US2-04 | **Status**: [x] completed
**File**: `repositories/anton-abyzov/vskill/src/eval-server/authoring-routes.ts`
**Test Plan**: Given `GET /api/authoring/skill-exists` uses same `validateKebab` and `skillDir` resolution as POST → When called → Then validation divergence is structurally impossible
**Test**: `repositories/anton-abyzov/vskill/src/eval-server/__tests__/authoring-routes.test.ts` (describe: "0703 — GET /api/authoring/skill-exists")

### T-004: [P] GET skill-exists returns exists:false for fresh standalone name
**User Story**: US-002 | **AC**: AC-US2-01 | **Status**: [x] completed
**File**: `repositories/anton-abyzov/vskill/src/eval-server/authoring-routes.ts`
**Test Plan**: Given skill dir does not exist → When `GET ?mode=standalone&skillName=anton-greet` → Then `{ exists: false }` with 200
**Test**: `repositories/anton-abyzov/vskill/src/eval-server/__tests__/authoring-routes.test.ts` (case: "returns exists:false for a fresh standalone skill name")

### T-005: [P] GET skill-exists returns exists:true when skill dir present
**User Story**: US-002 | **AC**: AC-US2-01 | **Status**: [x] completed
**File**: `repositories/anton-abyzov/vskill/src/eval-server/authoring-routes.ts`
**Test Plan**: Given skill dir scaffolded on disk → When `GET ?mode=standalone&skillName=anton-greet` → Then `{ exists: true, path }` with 200
**Test**: `repositories/anton-abyzov/vskill/src/eval-server/__tests__/authoring-routes.test.ts` (case: "returns exists:true when the skill directory is already present")

### T-006: [P] GET skill-exists handles existing-plugin mode
**User Story**: US-002 | **AC**: AC-US2-01 | **Status**: [x] completed
**File**: `repositories/anton-abyzov/vskill/src/eval-server/authoring-routes.ts`
**Test Plan**: Given `mode=existing-plugin&pluginName=my-plugin&skillName=greeter` and plugin manifest present → When GET → Then 200 with correct path
**Test**: `repositories/anton-abyzov/vskill/src/eval-server/__tests__/authoring-routes.test.ts` (case: "returns 200 for existing-plugin mode when the plugin manifest exists")

### T-007: [P] GET skill-exists returns 404 for missing plugin
**User Story**: US-002 | **AC**: AC-US2-02 | **Status**: [x] completed
**File**: `repositories/anton-abyzov/vskill/src/eval-server/authoring-routes.ts`
**Test Plan**: Given `mode=existing-plugin&pluginName=ghost` and no manifest → When GET → Then 404 plugin-not-found
**Test**: `repositories/anton-abyzov/vskill/src/eval-server/__tests__/authoring-routes.test.ts` (case: "returns 404 plugin-not-found when existing-plugin mode targets a missing plugin")

### T-008: [P] GET skill-exists returns 400 for invalid skillName
**User Story**: US-002 | **AC**: AC-US2-02 | **Status**: [x] completed
**File**: `repositories/anton-abyzov/vskill/src/eval-server/authoring-routes.ts`
**Test Plan**: Given `skillName=BAD%20NAME` (not kebab) → When GET → Then 400 invalid-skill-name
**Test**: `repositories/anton-abyzov/vskill/src/eval-server/__tests__/authoring-routes.test.ts` (case: "returns 400 invalid-skill-name for non-kebab inputs")

### T-009: [P] GET skill-exists returns 400 for unknown mode
**User Story**: US-002 | **AC**: AC-US2-02 | **Status**: [x] completed
**File**: `repositories/anton-abyzov/vskill/src/eval-server/authoring-routes.ts`
**Test Plan**: Given `mode=bogus` → When GET → Then 400 invalid-mode
**Test**: `repositories/anton-abyzov/vskill/src/eval-server/__tests__/authoring-routes.test.ts` (case: "returns 400 invalid-mode for unknown mode")

### T-010: [P] CreateSkillModal awaits skill-exists before navigating
**User Story**: US-002 | **AC**: AC-US2-03 | **Status**: [x] completed
**File**: `repositories/anton-abyzov/vskill/src/eval-ui/src/components/CreateSkillModal.tsx`
**Test Plan**: Given skill-exists returns `{ exists: true }` → When "Generate with AI" clicked → Then inline error shown and `window.location.assign` never called
**Test**: `repositories/anton-abyzov/vskill/src/eval-ui/src/components/__tests__/CreateSkillModal.0703.test.tsx` (case: "AC-US2-04: shows error and does NOT navigate when skill already exists")

### T-011: [P] CreateSkillModal navigates on exists:false
**User Story**: US-002 | **AC**: AC-US2-03 | **Status**: [x] completed
**File**: `repositories/anton-abyzov/vskill/src/eval-ui/src/components/CreateSkillModal.tsx`
**Test Plan**: Given skill-exists returns `{ exists: false }` → When "Generate with AI" clicked → Then `window.location.assign` called with `/#/create?…`
**Test**: `repositories/anton-abyzov/vskill/src/eval-ui/src/components/__tests__/CreateSkillModal.0703.test.tsx` (case: "AC-US2-05: navigates to /#/create when the skill name is free")

---

## Phase 3: ModelRow layout fixes — US-003 & US-004

### T-012: Replace fixed height with minHeight on ModelRow
**User Story**: US-003 | **AC**: AC-US3-01, AC-US3-02 | **Status**: [x] completed
**File**: `repositories/anton-abyzov/vskill/src/eval-ui/src/components/ModelList.tsx`
**Test Plan**: Given three claude-cli model rows with resolvedModel set → When rendered → Then `row.style.height` is empty and `row.style.minHeight` matches `44px`
**Test**: `repositories/anton-abyzov/vskill/src/eval-ui/src/components/__tests__/ModelList.0703.test.tsx` (case: "uses minHeight, not fixed height, so rows with resolvedModel can grow")

### T-013: Add matchesResolvedAlias helper; render routing hint only on matched row
**User Story**: US-004 | **AC**: AC-US4-01, AC-US4-02 | **Status**: [x] completed
**File**: `repositories/anton-abyzov/vskill/src/eval-ui/src/components/ModelList.tsx`
**Test Plan**: Given resolvedModel "claude-opus-4-7[1m]" → When ModelList rendered → Then exactly 1 `[data-testid$="-resolved"]` element, on the opus row only
**Test**: `repositories/anton-abyzov/vskill/src/eval-ui/src/components/__tests__/ModelList.0703.test.tsx` (case: "only the 'opus' row shows 'routing to claude-opus-4-7[1m]'…")

### T-014: [P] matchesResolvedAlias is case-insensitive substring match
**User Story**: US-004 | **AC**: AC-US4-01 | **Status**: [x] completed
**File**: `repositories/anton-abyzov/vskill/src/eval-ui/src/components/ModelList.tsx`
**Test Plan**: Given resolvedModel "claude-sonnet-4-6" → When rendered → Then sonnet row has routing sub-line, opus row does not
**Test**: `repositories/anton-abyzov/vskill/src/eval-ui/src/components/__tests__/ModelList.0703.test.tsx` (case: "shows 'routing to' on the 'sonnet' row when resolvedModel contains sonnet")

### T-015: [P] No routing sub-line rendered when resolvedModel is null
**User Story**: US-004 | **AC**: AC-US4-03 | **Status**: [x] completed
**File**: `repositories/anton-abyzov/vskill/src/eval-ui/src/components/ModelList.tsx`
**Test Plan**: Given resolvedModel is null → When rendered → Then zero `[data-testid$="-resolved"]` elements exist
**Test**: `repositories/anton-abyzov/vskill/src/eval-ui/src/components/__tests__/ModelList.0703.test.tsx` (case: "renders no routing sub-line at all when resolvedModel is null")

---

## Phase 4: Hash-route takeover — US-005

### T-016: Wrap App in HashRouter and add useIsCreateRoute hook
**User Story**: US-005 | **AC**: AC-US5-01, AC-US5-02, AC-US5-03, AC-US5-04 | **Status**: [x] completed
**File**: `repositories/anton-abyzov/vskill/src/eval-ui/src/main.tsx`, `repositories/anton-abyzov/vskill/src/eval-ui/src/App.tsx`
**Test Plan**: Given `window.location.assign("/#/create?description=…")` → When hash changes → Then App renders CreateSkillPage under Suspense (verified via E2E in Claude_Preview)
**Test**: `e2e/0703-create-flow-hotfix.spec.ts` (scenario: "navigating to /#/create renders CreateSkillPage")

---

## Phase 5: Target Agents scoping — US-006

### T-017: Hide Target Agents section when activeAgent is claude-code
**User Story**: US-006 | **AC**: AC-US6-01, AC-US6-02 | **Status**: [x] completed
**File**: `repositories/anton-abyzov/vskill/src/eval-ui/src/pages/CreateSkillPage.tsx`
**Test Plan**: Given `localStorage["vskill.studio.prefs"].activeAgent = "claude-code"` → When CreateSkillPage renders → Then "Target Agents" header and Cursor/Codex CLI rows absent from DOM
**Test**: `repositories/anton-abyzov/vskill/src/eval-ui/src/pages/__tests__/CreateSkillPage.targetAgents.test.tsx` (case: "AC-US5-01: hides Cursor / Codex CLI / Copilot rows when activeAgent is claude-code")

### T-018: Show Target Agents section for non-claude-code scopes
**User Story**: US-006 | **AC**: AC-US6-03 | **Status**: [x] completed
**File**: `repositories/anton-abyzov/vskill/src/eval-ui/src/pages/CreateSkillPage.tsx`
**Test Plan**: Given `activeAgent = "cursor"` or preference unset (null) → When CreateSkillPage renders → Then "Target Agents" and universal agent rows present
**Test**: `repositories/anton-abyzov/vskill/src/eval-ui/src/pages/__tests__/CreateSkillPage.targetAgents.test.tsx` (cases: "AC-US5-02: shows all universal agents when activeAgent is NOT claude-code", "sanity: installed agents actually render without activeAgent preference")

---

## Completion Gate

- [x] All T-001..T-018 unit tests green under `npx vitest run` (18 new cases + 0701 regression suite 5/5)
- [x] Playwright E2E: `e2e/0703-create-flow-hotfix.spec.ts` 5/5 passed (verified via Claude_Preview)
- [x] `npx tsc --noEmit` clean in eval-ui + eval-server
- [x] No regressions vs main (pre-existing TopRail breadcrumb + picker-tooltip failures unchanged)
- [x] vskill npm release cut after merge (0.5.98)
