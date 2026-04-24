---
increment: 0703-studio-create-flow-hotfix
title: Skill Studio create flow hotfix
type: hotfix
priority: P0
status: completed
created: 2026-04-24T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
retrospective: true
---

# Feature: Skill Studio create flow hotfix

## Overview

The Skill Studio "+ New Skill → Generate with AI" flow was broken by six compounding bugs that manifested as a single user-visible symptom: "nothing happens" after choosing Generate with AI. This increment retrospectively documents the six shipped fixes, the tests that lock them in, and the code paths that were touched.

**Project**: vskill (Skill Studio UI + eval server at `repositories/anton-abyzov/vskill/`)
**Type**: hotfix, P0
**Status**: Shipped — code already in the working tree; this spec exists for closure + audit trail.

## Root Causes (shipped fixes)

| # | Symptom | Root cause | Fix |
|---|---------|------------|-----|
| 1 | Generate button stays disabled after choosing a prefilled prompt | Prefill effect wrote to `sk.description` but not `sk.aiPrompt`; Generate is gated on `aiPrompt` | `CreateSkillPage` mount-only effect now calls `sk.setAiPrompt(prefill.description)` |
| 2 | Duplicate skill name silently clobbers on navigation | Generate-with-AI branch bypassed the POST 409 path | New `GET /api/authoring/skill-exists` + modal pre-check; blocks `window.location.assign` on `exists:true` |
| 3 | ModelRow third line overlaps the next row in ⌘K picker | 0701 added a third line but kept fixed `height: 44px` | `height` → `minHeight`; safe because virtualization only kicks in at ≥80 items |
| 4 | "routing to claude-opus-4-7[1m]" shown on Sonnet row | `resolvedModel` is Claude Code's default; vskill always passes `--model <alias>` | Helper `matchesResolvedAlias(modelId, resolvedModel)` — only the matching row renders the sub-line |
| 5 | `/#/create` is a null route — "nothing happens" | Commit 2796fd1 (2026-03-10) removed `<Routes>` from `App.tsx`; modal's `window.location.assign` went nowhere | Wrap `<App/>` in `<HashRouter>` in `main.tsx`; add `useIsCreateRoute()` in `App.tsx` that renders `<CreateSkillPage/>` under `<Suspense>` |
| 6 | Cursor/Codex CLI/Amp/Cline surfaced as Target Agents when scope is Claude Code | Target Agents picker ignored the active scope | Read `getStudioPreference<string\|null>("activeAgent", null)`; hide section when `activeAgentId === "claude-code"` |

## User Stories

### US-001: Prefill populates the Generate button's source of truth (P0)
**Project**: vskill

**As a** user who just typed a description into the "+ New Skill → Generate with AI" modal
**I want** the CreateSkillPage to arrive with the Generate button already enabled
**So that** I do not have to retype or re-paste the prompt before the AI can run

**Acceptance Criteria**:
- [x] **AC-US1-01**: When `?description=X` is present in the URL, CreateSkillPage's mount-only prefill effect sets BOTH `sk.description` AND `sk.aiPrompt` to `X`
- [x] **AC-US1-02**: When `?description` is missing or empty, `sk.aiPrompt` stays empty and the Generate button remains disabled
- [x] **AC-US1-03**: The prefill effect runs only on mount — subsequent URL changes do not re-overwrite user edits

**Test anchors**: `CreateSkillPage.prefill.test.tsx` (3 cases)

---

### US-002: Duplicate skill name is caught before navigation (P0)
**Project**: vskill

**As a** user who picks a skill name that already exists on disk
**I want** the modal to tell me immediately and block navigation
**So that** I do not silently clobber an existing skill or land on a broken generator page

**Acceptance Criteria**:
- [x] **AC-US2-01**: `GET /api/authoring/skill-exists?mode=&skillName=&pluginName=` returns `{ exists: true, path }` when the skill exists (where `path` is the resolved skill directory), `{ exists: false }` otherwise, for both `standalone` and `existing-plugin` modes
- [x] **AC-US2-02**: The endpoint returns `400` for invalid `skillName` or invalid `mode`, and `404` when the referenced plugin does not exist
- [x] **AC-US2-03**: `CreateSkillModal` awaits the skill-exists check before calling `window.location.assign(...)` and surfaces `"Skill 'X' already exists at <path>"` on `exists:true`, suppressing navigation
- [x] **AC-US2-04**: Endpoint shares validation and resolved-`path` derivation with the existing POST handler via the `makeSkillExistsHandler` factory (no duplicated logic)

**Test anchors**: `authoring-routes.test.ts` (+6 cases), `CreateSkillModal.0703.test.tsx` (2 cases)

---

### US-003: ModelRow no longer overlaps into the next row (P1)
**Project**: vskill

**As a** user opening the ⌘K model picker in Skill Studio
**I want** every row's text to stay within its own row
**So that** the picker is readable and clickable on the intended row

**Acceptance Criteria**:
- [x] **AC-US3-01**: `ModelRow` uses `minHeight: ROW_HEIGHT` instead of a fixed `height`, allowing the optional third "routing to..." line to expand without overlap
- [x] **AC-US3-02**: The change does not regress virtualization — `useVirtualList` still only activates at ≥80 items and claude-cli's 3-model catalogue renders normally

**Test anchors**: `ModelList.0703.test.tsx` (overlap cases)

---

### US-004: Routing hint appears only on the resolved model's row (P1)
**Project**: vskill

**As a** user inspecting the ⌘K model picker
**I want** the "routing to <alias>" sub-line to appear only on the row that is actually being invoked
**So that** I build a correct mental model of which CLI alias vskill will pass via `--model`

**Acceptance Criteria**:
- [x] **AC-US4-01**: `matchesResolvedAlias(modelId, resolvedModel)` returns true iff `resolvedModel.toLowerCase().includes(modelId.toLowerCase())`
- [x] **AC-US4-02**: Only the row where `matchesResolvedAlias` is true renders the "routing to <resolvedModel>" sub-line; other rows render with two lines
- [x] **AC-US4-03**: When `resolvedModel` is empty/null, no row renders the sub-line

**Test anchors**: `ModelList.0703.test.tsx` (alias-match cases)

---

### US-005: The `/#/create` route is alive again (P0)
**Project**: vskill

**As a** user who clicks "Generate with AI" in the CreateSkillModal
**I want** the browser to land on the generator page (not a blank screen)
**So that** the modal's prefill flow actually delivers me to CreateSkillPage

**Acceptance Criteria**:
- [x] **AC-US5-01**: `main.tsx` wraps `<App/>` in `<HashRouter>`
- [x] **AC-US5-02**: `App.tsx` exposes a `useIsCreateRoute()` hook that reads `window.location.hash` and subscribes to `hashchange` (sufficient for hash-only routing — spec amended 2026-04-25 per 0703 closure code-review F-001 to match shipped implementation; `popstate` was originally specified but hashchange alone correctly handles back/forward navigation for hash-route apps)
- [x] **AC-US5-03**: When the hash starts with `#/create`, `App` renders `<CreateSkillPage/>` under `<Suspense>`; otherwise it renders the default dashboard tree
- [x] **AC-US5-04**: Navigating from the modal via `window.location.assign("/#/create?description=...")` transitions the UI to CreateSkillPage without a full reload

**Test anchors**: manual E2E via Claude_Preview (routing is integration-level; unit coverage would require a full JSDOM router fixture — tracked as out of scope).

---

### US-006: Target Agents respect the active agent scope (P1)
**Project**: vskill

**As a** user with Claude Code set as the active agent scope
**I want** the Target Agents picker to be hidden
**So that** I do not see Cursor/Codex CLI/Amp/Cline as valid opt-in targets for a Claude Code skill

**Acceptance Criteria**:
- [x] **AC-US6-01**: `CreateSkillPage` reads `getStudioPreference<string|null>("activeAgent", null)` on render
- [x] **AC-US6-02**: Computed `showTargetAgents = activeAgentId !== "claude-code"` gates the entire Target Agents section — it is removed from the DOM, not merely disabled
- [x] **AC-US6-03**: For non-claude-code scopes (including `null`/unset), the section renders as before

**Test anchors**: `CreateSkillPage.targetAgents.test.tsx` (3 cases)

---

## Functional Requirements

### FR-001: Shared validation for skill-exists GET and skills POST
The `GET /api/authoring/skill-exists` endpoint MUST share its `skillName` regex, `mode` enum, and resolved-`path` (skill-directory) derivation with the existing `POST /api/authoring/skills` handler via a `makeSkillExistsHandler` factory. Divergence between the two paths would reintroduce the class of bug this hotfix is closing.

### FR-002: Prefill is mount-only
The URL-driven prefill effect in `CreateSkillPage` MUST run only on mount. Re-running on URL changes would overwrite the user's in-progress edits.

### FR-003: Resolved-alias sub-line is scoped
The "routing to <resolvedModel>" sub-line in `ModelRow` MUST render on at most one row per render — the row whose `modelId` matches `resolvedModel` via case-insensitive substring containment.

## Success Criteria

- All 18 new unit tests green; 0701 regression suite (5 tests) still green.
- `npx tsc --noEmit` clean.
- Manual E2E via Claude_Preview confirms: (a) model picker free of visual overlap, (b) Opus row shows "routing to claude-opus-4-7[1m]" while Sonnet/Haiku do not, (c) Generate-with-AI modal → CreateSkillPage lands with prefilled prompt + enabled Generate button, (d) duplicate-name pre-check blocks navigation with the expected error, (e) Target Agents section hidden under the Claude Code scope.
- No net-new failures compared to main baseline (5 pre-existing failures in TopRail breadcrumb + picker-tooltip are out of scope).

## Out of Scope

- A proper `<Routes>/<Route>` tree restoration — the hash-escape-hatch pattern is sufficient for today's single sub-route. A broader router refactor belongs to its own increment.
- Eliminating the pre-existing main-branch failures (TopRail breadcrumb + picker-tooltip).
- Any changes to the Claude Code CLI itself, the model catalogue source, or `resolvedModel` computation.
- Re-adding universal agents for non-claude-code scopes — behaviour for those scopes is unchanged.

## Dependencies

- Shipped 0701 (Studio provider pricing & model identity) — introduced the third ModelRow line that triggered overflow (FIX-3) and the `resolvedModel` field consumed by FIX-4.
- Existing `POST /api/authoring/skills` handler — FIX-2's `GET` endpoint shares validation + resolved-`path` derivation via `makeSkillExistsHandler`.
- `useCreateSkill` store — FIX-1 writes through `sk.setAiPrompt`.
- `getStudioPreference` utility — FIX-6 reads `activeAgent`.

## Files Touched

- `repositories/anton-abyzov/vskill/src/eval-ui/src/main.tsx` (FIX-5)
- `repositories/anton-abyzov/vskill/src/eval-ui/src/App.tsx` (FIX-5)
- `repositories/anton-abyzov/vskill/src/eval-ui/src/pages/CreateSkillPage.tsx` (FIX-1, FIX-6)
- `repositories/anton-abyzov/vskill/src/eval-ui/src/components/CreateSkillModal.tsx` (FIX-2)
- `repositories/anton-abyzov/vskill/src/eval-ui/src/components/ModelList.tsx` (FIX-3, FIX-4)
- `repositories/anton-abyzov/vskill/src/eval-server/authoring-routes.ts` (FIX-2)

## Test Inventory

- `CreateSkillPage.prefill.test.tsx` — 3 cases (AC-US1-01..03)
- `CreateSkillPage.targetAgents.test.tsx` — 3 cases (AC-US6-01..03)
- `CreateSkillModal.0703.test.tsx` — 2 cases (AC-US2-03, window.location stubbed via `Object.defineProperty`)
- `ModelList.0703.test.tsx` — 4 cases (AC-US3-01..02, AC-US4-01..03)
- `authoring-routes.test.ts` — +6 cases (AC-US2-01..04: exists:true/false × {standalone, existing-plugin}; 404 plugin-not-found; 400 invalid-skill-name; 400 invalid-mode)

Total: **18 new unit tests**, all green. 0701 regression suite (5 tests) still passes.
