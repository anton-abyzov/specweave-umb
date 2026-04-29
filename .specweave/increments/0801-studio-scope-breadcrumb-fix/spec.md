---
increment: 0801-studio-scope-breadcrumb-fix
title: Studio header breadcrumb shows correct scope (PROJECT/PERSONAL/PLUGIN)
type: bug
priority: P1
status: completed
created: 2026-04-29T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Studio header breadcrumb shows correct scope (PROJECT/PERSONAL/PLUGIN)

## Overview

The Skill Studio header breadcrumb currently shows `PROJECT > {agent} > {skill}` for every selected skill, even when the skill is in PERSONAL or PLUGIN scope as shown in the sidebar. The label is computed from the binary `origin` field (`source` | `installed`) rather than the 3-way `source` field (`project` | `personal` | `plugin`) that the sidebar uses. This makes the header lie about where the skill lives — a symlinked personal skill (e.g. `~/.agents/skills/excalidraw-diagram-generator`) renders as `PROJECT` while the sidebar correctly groups it under `PERSONAL > CLAUDE-CODE`.

## Bug Reproduction

1. Open Skill Studio (`vskill studio` → http://localhost:3113/?tab=edit).
2. Expand `AVAILABLE > PERSONAL > CLAUDE-CODE` in the sidebar.
3. Click any skill (e.g. `excalidraw-diagram-generator`).
4. Observe: header shows `specweave-umb ▼  PROJECT › claude-code › excalidraw-diagram-generator`.
5. Expected: header shows `specweave-umb ▼  PERSONAL › claude-code › excalidraw-diagram-generator`.

## Root Cause

| File | Line | Issue |
|---|---|---|
| `StudioContext.tsx` | 14-18 | `SelectedSkill` only carries `origin: "source" \| "installed"` — drops the rich `source: "project" \| "personal" \| "plugin"` already present on `SkillInfo`. |
| `StudioContext.tsx` | 271 | `loadSkills` hash restorer extracts `found.origin` only — discards `found.source`. |
| `StudioContext.tsx` | 282 | `selectSkill` writes a 2-segment hash (`#/skills/{plugin}/{skill}`) — scope is unrecoverable on reload. |
| `TopRail.tsx` | 64-68 | `originLabel` uses `origin === "installed" ? "Project" : "Skills"` — installed-personal collapses to "Project". |

## User Stories

### US-001: Header breadcrumb reflects sidebar scope (P1)
**Project**: vskill

**As a** Studio user browsing skills across project, personal, and plugin scopes,
**I want** the header breadcrumb's first segment to match the sidebar group I selected from
**So that** I can trust the breadcrumb as ground truth and never wonder whether I'm editing a project skill or a personal one.

**Acceptance Criteria**:
- [x] **AC-US1-01**: Selecting a skill from `AVAILABLE > PROJECT` renders the first crumb as `PROJECT`.
- [x] **AC-US1-02**: Selecting a skill from `AVAILABLE > PERSONAL` renders the first crumb as `PERSONAL`.
- [x] **AC-US1-03**: Selecting a skill from `AVAILABLE > PLUGIN` renders the first crumb as `PLUGIN`.
- [x] **AC-US1-04**: Crumb color matches the scope (project=existing `--status-installed`, personal=neutral, plugin=accent), preserving the existing visual differentiation.
- [x] **AC-US1-05**: When a skill object is missing the `source` field (legacy fixtures, older bundles), the crumb falls back to deriving from `origin` (installed → `PERSONAL`, source → `PROJECT`) so no NPE / blank crumb is rendered.

### US-002: Deep links survive reload with correct scope (P1)
**Project**: vskill

**As a** Studio user who bookmarks or shares a skill URL,
**I want** the URL hash to encode which scope the skill was selected in
**So that** reloading the page restores the same crumb, even when the same skill name exists in two scopes.

**Acceptance Criteria**:
- [x] **AC-US2-01**: Clicking a skill writes `#/skills/{source}/{agent}/{skill}` to `window.location.hash` (3 segments after `/skills/`).
- [x] **AC-US2-02**: On page load, the new 3-segment hash is parsed and the matching skill (filtered by `source` AND `plugin` AND `skill`) is selected.
- [x] **AC-US2-03**: A legacy 2-segment hash (`#/skills/{plugin}/{skill}`) still selects the first matching skill; the breadcrumb derives `source` from the matched skill's data so the crumb is still correct.
- [x] **AC-US2-04**: A hash with an unrecognized source value (e.g. `#/skills/foo/bar/baz`) is ignored — falls back to the no-selection state instead of crashing.

### US-003: Existing tests stay green or are updated to reflect new contract (P2)
**Project**: vskill

**As a** developer maintaining the Studio test suite,
**I want** the breadcrumb-related unit tests to exercise the new 3-way contract
**So that** the bug cannot regress and future scope additions follow a clear pattern.

**Acceptance Criteria**:
- [x] **AC-US3-01**: The existing `TopRail.test.tsx` test "renders breadcrumb Project when an installed skill is selected" is updated to assert the new contract: a SelectedSkill with `source: "project"` renders "Project"; a SelectedSkill with `source: "personal"` renders "Personal".
- [x] **AC-US3-02**: A new test asserts plugin-scope renders "Plugins".
- [x] **AC-US3-03**: A new test asserts the legacy fallback (no `source`, only `origin: "installed"`) renders "Personal" (the conservative interpretation since installed-without-source is most likely a personal-tier symlink).
- [x] **AC-US3-04**: All other unit tests that mock `SelectedSkill` continue to pass (the new `source` field is optional in the type to avoid breaking ~25 test mocks).

## Out of Scope

- Making breadcrumb segments clickable to filter the sidebar (they already are, via existing `dispatchNavigateScope`).
- Renaming the legacy `origin` field — kept for back-compat with the 25+ files that read it.
- Server-side changes — `SkillInfo.source` is already populated by the scanner.

## Success Metrics

- Zero false PROJECT/PERSONAL labels in the breadcrumb during manual smoke (3 scopes × 2 skills each).
- Vitest unit suite green (`npx vitest run`).
- Studio dev server reload preserves the selected skill at the right scope.
