---
increment: 0801-studio-scope-breadcrumb-fix
title: "Studio header breadcrumb shows correct scope (PROJECT/PERSONAL/PLUGIN)"
---

# Tasks

## T-001: Extend `SelectedSkill` with optional `source` field
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-05 | **Status**: [x] completed
**File**: `repositories/anton-abyzov/vskill/src/eval-ui/src/StudioContext.tsx`
**Test Plan**:
- Given the `SelectedSkill` interface
- When TypeScript compiles
- Then it must accept an optional `source: "project" | "personal" | "plugin"` field without breaking existing test mocks that omit it.

## T-002: TDD RED — TopRail breadcrumb tests for 3-way source
**User Story**: US-001, US-003 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-05, AC-US3-01, AC-US3-02, AC-US3-03 | **Status**: [x] completed
**File**: `repositories/anton-abyzov/vskill/src/eval-ui/src/components/__tests__/TopRail.test.tsx`
**Test Plan**:
- Given a `SelectedSkill` with `source: "project"`
- When TopRail renders
- Then text contains "Project"

- Given a `SelectedSkill` with `source: "personal"` (NEW)
- When TopRail renders
- Then text contains "Personal"

- Given a `SelectedSkill` with `source: "plugin"` (NEW)
- When TopRail renders
- Then text contains "Plugins"

- Given a legacy `SelectedSkill` with `origin: "installed"` and no `source` (NEW)
- When TopRail renders
- Then text contains "Personal" (conservative fallback)

Run: `npx vitest run src/eval-ui/src/components/__tests__/TopRail.test.tsx` — must FAIL (red).

## T-003: TDD GREEN — Update TopRail to derive label from `source` with origin fallback
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05 | **Status**: [x] completed
**File**: `repositories/anton-abyzov/vskill/src/eval-ui/src/components/TopRail.tsx`
**Test Plan**:
- Given the failing tests from T-002
- When TopRail's `originLabel` derivation is replaced with `scopeLabel(selected)` reading `selected.source ?? fallbackFromOrigin(selected.origin)`
- Then all T-002 tests pass and the existing `Skills` (authoring) test still passes for legacy `source: "source"` semantics if any test relies on it.

Run: `npx vitest run src/eval-ui/src/components/__tests__/TopRail.test.tsx` — must PASS (green).

## T-004: Propagate `source` through `selectSkill` and `revealSkill` + write 3-segment hash
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01 | **Status**: [x] completed
**File**: `repositories/anton-abyzov/vskill/src/eval-ui/src/StudioContext.tsx`
**Test Plan**:
- Given a user clicks a skill row with `source: "personal"`
- When `selectSkill` writes to `window.location.hash`
- Then the hash equals `#/skills/personal/{plugin}/{skill}`.

- Given the SkillInfo passed to `revealSkill` has `source: "plugin"`
- When `revealSkill` writes the hash
- Then the hash equals `#/skills/plugin/{plugin}/{skill}`.

## T-005: Update `loadSkills` hash parser to accept 3-segment AND legacy 2-segment forms
**User Story**: US-002 | **Satisfies ACs**: AC-US2-02, AC-US2-03, AC-US2-04 | **Status**: [x] completed
**File**: `repositories/anton-abyzov/vskill/src/eval-ui/src/StudioContext.tsx`
**Test Plan**:
- Given a hash `#/skills/personal/claude-code/excalidraw-diagram-generator`
- When `loadSkills` runs
- Then it dispatches `SELECT_SKILL` with `{plugin: "claude-code", skill: "excalidraw-diagram-generator", source: "personal", origin: <found.origin>}`.

- Given a legacy hash `#/skills/claude-code/excalidraw-diagram-generator` (no source segment)
- When `loadSkills` runs
- Then it falls back to first-match-by-(plugin,skill) and dispatches with `source: <found.source>` derived from skill data.

- Given a malformed hash `#/skills/foo/bar/baz` where "foo" is not a valid SkillSource
- When `loadSkills` runs
- Then it falls through to legacy lookup, treating "foo" as plugin and "bar" as skill (3rd segment ignored).

## T-006: Update sidebar onSelect callback (`App.tsx`) to forward `source`
**User Story**: US-001, US-002 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US2-01 | **Status**: [x] completed
**File**: `repositories/anton-abyzov/vskill/src/eval-ui/src/App.tsx` (line 583-588)
**Test Plan**:
- Given Sidebar passes a full `SkillInfo` object to `onSelect`
- When `onSelect` calls `selectSkill`
- Then the call includes `source: s.source` alongside the existing `plugin/skill/origin` fields.

## T-007: Update RightPanel + UpdateBell `selectSkill` callsites to pass `source`
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01 | **Status**: [x] completed
**Files**: `src/eval-ui/src/components/RightPanel.tsx`, `src/eval-ui/src/components/UpdateBell.tsx`
**Test Plan**:
- Given an UpdateBell row click with skill `source: "personal"`
- When the underlying `selectSkill` fires
- Then the call includes the correct `source` (or omits it for the legacy-fallback path which still works via `origin`).

## T-008: Add StudioContext hash-parser test for 3-segment + legacy form
**User Story**: US-002 | **Satisfies ACs**: AC-US2-02, AC-US2-03 | **Status**: [x] completed
**File**: `repositories/anton-abyzov/vskill/src/eval-ui/src/__tests__/StudioContext.first-load.test.tsx`
**Test Plan**:
- Pre-seed `window.location.hash` to the new 3-segment form. Render `<StudioProvider>`. Assert the `selectedSkill` matches the hash, with `source` populated.
- Pre-seed `window.location.hash` to the legacy 2-segment form. Assert the same skill is selected, with `source` derived from the found skill's data.

## T-009: Build the eval-ui bundle and run unit suite
**User Story**: All | **Satisfies ACs**: All | **Status**: [x] completed
**Test Plan**:
- Run `cd repositories/anton-abyzov/vskill && npx vitest run src/eval-ui` — all tests pass.
- Run `cd repositories/anton-abyzov/vskill && npm run build:eval-ui` — bundle builds without TS errors.

## T-010: Manual verification — restart Studio and confirm crumb in browser for all 3 scopes
**User Story**: US-001, US-002 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US2-01, AC-US2-02 | **Status**: [x] completed
**Test Plan**:
- Restart `vskill studio` (kills cached bundle).
- Click a PROJECT-scope skill → header shows "PROJECT".
- Click a PERSONAL-scope skill → header shows "PERSONAL".
- Click a PLUGIN-scope skill → header shows "PLUGINS".
- Reload the page on the PERSONAL skill — crumb persists.
- Take a screenshot for each scope as evidence.
