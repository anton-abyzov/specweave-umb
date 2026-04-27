---
increment: 0788-studio-create-skill-redirect-fix
title: 'Studio: redirect to skill detail after Create Skill'
type: bug
priority: P1
status: completed
created: 2026-04-27T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Studio: redirect to skill detail after Create Skill

## Overview

When a user clicks **Create Skill** on the vskill Studio "+ New Skill" page (`#/create`), the create succeeds on the backend but the UI stays rendered on the form. The URL hash updates to `#/skills/<plugin>/<skill>` but no route handler exists for that pattern (the Studio uses ad-hoc hash routing — only `#/create` and `#/updates` are recognized). `state.selectedSkill` is never updated and `refreshSkills()` is never called, so the right panel falls through to an empty/stale state and the user perceives the flow as "stuck on the New Skill page".

The working pattern already shipped for the simpler `CreateSkillModal` flow (App.tsx:743-761) — `refreshSkills()` + `setTimeout(500ms, revealSkill(plugin, skill))` — must also be wired into `CreateSkillPage`. `revealSkill` (StudioContext.tsx:291-321) both updates context state and writes the hash, so the broken `react-router` `navigate(...)` call is dropped.

## User Stories

### US-001: New skill opens automatically after Create Skill click (P1)
**Project**: vskill

**As a** Skill Studio user creating a new skill via the "+ New Skill" page
**I want** the studio to switch to the new skill's detail view as soon as the create succeeds
**So that** I can immediately edit/inspect the skill I just created without navigating manually or refreshing

**Acceptance Criteria**:
- [x] **AC-US1-01**: After `POST /api/skills/create` returns 201, the studio invokes `refreshSkills()` so the new skill appears in `state.skills` (verified via spy in unit test).
- [x] **AC-US1-02**: Within 500 ms of a successful create, `revealSkill(plugin, skill)` is invoked with the exact `plugin` and `skill` values returned by the backend (verified via spy + `vi.advanceTimersByTime(500)`).
- [x] **AC-US1-03**: After the redirect, the URL hash equals `#/skills/<plugin>/<skill>` (set by `revealSkill`, not by react-router `navigate`).
- [x] **AC-US1-04**: After the redirect, `state.selectedSkill` matches `{ plugin, skill, origin: "source" }` and the right panel renders the skill's detail view (Overview tab) — not the create form, not an empty state.
- [x] **AC-US1-05**: The fix does not regress the existing 409 "skill-already-exists" recovery path (`useCreateSkill.ts:653-662`) — that branch also calls `onCreated`, so the redirect must work identically when a duplicate is recovered.

---

### US-002: Standalone-layout skills also redirect cleanly (P1)
**Project**: vskill

**As a** Skill Studio user creating a standalone skill (layout 3, `?mode=standalone`)
**I want** the same automatic redirect behavior as plugin-scoped skills
**So that** the create flow feels consistent across layouts

**Acceptance Criteria**:
- [x] **AC-US2-01**: When the backend returns `plugin: ""` (standalone layout), `revealSkill("", skill)` is invoked. The existing safe-guard in `revealSkill` (StudioContext.tsx:305-313) handles the empty-plugin matcher logic — no extra wiring needed in `CreateSkillPage`.
- [x] **AC-US2-02**: The unit test covers the standalone path (plugin === "") in addition to the plugin-scoped path, asserting that `revealSkill` is still called once with the empty plugin string.

## Functional Requirements

### FR-001: CreateSkillPage uses StudioContext for post-create state updates
`CreateSkillPage` MUST consume `useStudio()` to obtain `refreshSkills` and `revealSkill`. Its `useCreateSkill({ onCreated })` callback MUST call `refreshSkills(); setTimeout(() => revealSkill(plugin, skill), 500);` — exactly mirroring the established `CreateSkillModal` pattern in `App.tsx:743-761`.

### FR-002: react-router navigate is dropped from the create-success path
`navigate(\`/skills/${plugin}/${skill}\`)` MUST be removed from the `onCreated` callback. `revealSkill` already writes `window.location.hash`. If `useNavigate` becomes unused after this change, the import is dropped to avoid dead code.

### FR-003: No backend, no routing-architecture changes
This fix MUST NOT modify `useHashRoute.ts`, `App.tsx`'s route ternary, `useCreateSkill.ts`'s `handleCreate`, or backend `skill-create-routes.ts`. Scope is limited to the two files in §FR-001.

## Success Criteria

- Manual smoke: clicking Create Skill on `#/create` redirects within ~500 ms to the new skill's detail tab; the sidebar row is auto-revealed and scrolled into view.
- Unit test `CreateSkillPage.redirect.test.tsx` passes; existing `CreateSkillPage.*.test.tsx` and `useCreateSkill*.test.ts` suites stay green.
- No new console warnings or errors in a happy-path run.

## Out of Scope

- Adding a real `#/skills/<plugin>/<skill>` route handler in `useHashRoute.ts` (larger refactor; not needed because `revealSkill` already drives both state and hash).
- Changes to the backend response shape, `useCreateSkill.handleCreate`, or `CreateSkillModal`.
- Toast / telemetry / analytics changes.
- Cancel-button or back-button behavior on `CreateSkillPage` (not user-reported).
- E2E (Playwright) coverage — the unit test plus manual smoke is sufficient for a one-page wiring bug.

## Dependencies

- `StudioContext.revealSkill` (StudioContext.tsx:291-321) — unchanged; already-shipped helper.
- `StudioContext.refreshSkills` — unchanged; already exposed via `useStudio()`.
- `useCreateSkill.handleCreate` (useCreateSkill.ts:621-669) — unchanged; already calls `onCreated(result.plugin, result.skill)` on both success and 409-recovery paths.
