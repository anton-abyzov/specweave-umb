---
increment: 0704-studio-new-skill-reveal-and-api-empty-state
title: "Studio new-skill reveal + API empty-state"
type: hotfix
priority: P1
status: planned
created: 2026-04-24
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Studio new-skill reveal + API empty-state

## Overview

Two polish bugs surfaced when creating a new skill in Skill Studio:

1. After `+ New Skill` succeeds, the sidebar does **not** reveal the newly-created skill — ancestor sections (AUTHORING, NamedScopeSection, PluginTreeGroup) each hold independent collapsed state, and the sidebar never calls `scrollIntoView`. Users cannot see where their new skill landed in the nested tree.
2. `GET /api/skills/:plugin/:skill/evals` and `/benchmark/latest` return `404` when the data files don't yet exist. Every freshly-created skill produces red errors in the devtools Network tab + console, making the Studio feel broken even though UI consumers silently handle the 404.

Scope: `repositories/anton-abyzov/vskill/` only.

## User Stories

### US-001: Sidebar reveals newly-created skill (P1)
**Project**: vskill

**As a** Skill Studio author
**I want** the sidebar to expand parent folders and scroll to my newly-created skill
**So that** I can see where it landed in the nested tree without hunting for it.

**Acceptance Criteria**:
- [ ] **AC-US1-01**: When a new skill is created under AUTHORING > Project (standalone), the AUTHORING group and the Project NamedScopeSection both render expanded, and the new skill's row is scrolled into view.
- [ ] **AC-US1-02**: When a new skill is created under AUTHORING > Plugins > {plugin} (plugin-owned), the AUTHORING group, Plugins NamedScopeSection, and the matching PluginTreeGroup all render expanded, and the new skill's row is scrolled into view.
- [ ] **AC-US1-03**: The reveal-time expansion does NOT write to localStorage — after the reveal clears, the user's prior manual collapse preferences are preserved for the next page load.
- [ ] **AC-US1-04**: The newly-revealed skill is also selected (detail panel opens with its metadata), and the URL hash matches `#/skills/{plugin}/{skill}`.
- [ ] **AC-US1-05**: Regular row clicks (user navigating within the sidebar) do NOT force-expand ancestors — only explicit reveal triggers (creation, notification-bell) expand collapsed ancestors.

---

### US-002: API returns 200 sentinel for missing evals/benchmark (P1)
**Project**: vskill

**As a** Skill Studio author
**I want** the API to return `200` with a valid-empty body when my new skill has no evals or benchmark data yet
**So that** the Network tab + console stay clean and the Studio doesn't look broken for freshly-created skills.

**Acceptance Criteria**:
- [ ] **AC-US2-01**: `GET /api/skills/:plugin/:skill/evals` returns `200 { exists: false, evals: [] }` when `evals/evals.json` is missing (previously `404 { error: "No evals.json found" }`).
- [ ] **AC-US2-02**: `GET /api/skills/:plugin/:skill/evals` continues to return `200 { evals: [...] }` (the existing EvalsFile shape) when `evals/evals.json` exists and is valid.
- [ ] **AC-US2-03**: `GET /api/skills/:plugin/:skill/benchmark/latest` returns `200 null` when no benchmark exists (previously `404 { error: "No benchmark found" }`).
- [ ] **AC-US2-04**: `getLatestBenchmark` client function continues to return `null` on missing data — via the new 200 null body, not the dropped 404 branch.
- [ ] **AC-US2-05**: All existing SkillDetailPage / BenchmarkPage / HistoryPerEval / WorkspaceContext consumers continue to render correctly with the new response shapes — no regressions.
- [ ] **AC-US2-06**: The dev-tools Network tab shows no 4xx errors for these two endpoints on a freshly-created skill.

## Functional Requirements

### FR-001: `forceOpen` prop on collapsible sidebar sections
`NamedScopeSection` (inline in `Sidebar.tsx`) and `PluginTreeGroup` gain an optional `forceOpen?: boolean` prop. When true, the section renders as expanded regardless of its internal `collapsed` state. The prop does NOT mutate internal state or localStorage — override is purely render-time.

### FR-002: `revealSkill(plugin, skill)` on StudioContext
`StudioContext` exposes `revealSkill(plugin, skill)` and `clearReveal()`. `revealSkill` atomically dispatches both SELECT_SKILL (existing) and SET_REVEAL (new). `clearReveal` is called after the sidebar has scrolled the target row into view.

### FR-003: Sidebar reveal effect
Sidebar reads `state.revealSkillId`. When non-null, it (a) forces `authoringCollapsed = false`, (b) passes `forceOpen` to the owning NamedScopeSection + PluginTreeGroup, (c) after paint, calls `scrollIntoView({ behavior: "smooth", block: "nearest" })` on `[data-skill-id="{plugin}/{skill}"]`, then (d) calls `clearReveal()`.

### FR-004: App.tsx onCreated wires to revealSkill
The `onCreated` handler in `App.tsx` replaces its `selectSkill()` call with `revealSkill()`. The `setTimeout(..., 500)` that waits for `refreshSkills()` is preserved.

## Success Criteria

- Creating a new skill (standalone or plugin-owned) causes the sidebar to expand ancestors + scroll the new row into view within 500 ms of the skill appearing in state.
- No 404 responses appear in the devtools Network tab for freshly-created skills.
- User's manual collapse preferences persist across page loads.
- 100% of new code paths covered by vitest; no regressions in existing Sidebar / Benchmark / SkillDetail test suites.

## Out of Scope

- Reworking how evals/benchmark are persisted
- Auto-generating evals on skill creation (separate existing feature)
- Any change to installed / non-authored skill flows
- Adding reveal to any trigger other than `+ New Skill` (notification-bell, deep-links, etc. can reuse `revealSkill` later)
- Animation timing / motion-preference tuning

## Dependencies

- Existing `data-skill-id="{plugin}/{skill}"` attribute on SkillRow (already present at [SkillRow.tsx:78](repositories/anton-abyzov/vskill/src/eval-ui/src/components/SkillRow.tsx:78))
- Existing `selectSkill` dispatch in StudioContext (wrapped by new `revealSkill`)
- Existing `refreshSkills()` in `onCreated` handler (reveal fires after skill lands in state)
- Native `Element.prototype.scrollIntoView` (no polyfill needed for Chrome/Firefox/Safari)
