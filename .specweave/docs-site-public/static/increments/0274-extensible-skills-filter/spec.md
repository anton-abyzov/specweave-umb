---
increment: 0274-extensible-skills-filter
title: "Extensible Skills Filter -- Full-Stack UX"
type: feature
priority: P1
status: completed
created: 2026-02-21
structure: user-stories
test_mode: test-after
coverage_target: 80
---

# Feature: Extensible Skills Filter -- Full-Stack UX

## Overview

Add extensible skill filtering to the catalog page with EXT badge on cards, toggle filter in filter bar, and extension point types visible in metrics when filter active.

## User Stories

### US-001: EXT Badge on Skill Cards (P1)
**Project**: vskill-platform

**As a** developer browsing the skills catalog
**I want** to see an "EXT" badge on extensible skill cards
**So that** I can immediately identify which skills support extension points without clicking into each one

**Acceptance Criteria**:
- [x] **AC-US1-01**: Each skill card in the catalog list shows a teal "EXT" pill badge next to the skill name/author line when `skill.extensible === true`
- [x] **AC-US1-02**: The EXT badge uses teal accent color (#0D9488) consistent with the extensible pill on the detail page
- [x] **AC-US1-03**: The EXT badge is always visible regardless of filter state (not conditional on the extensible filter being active)
- [x] **AC-US1-04**: Skills without `extensible: true` do not show the badge

---

### US-002: Extensible Toggle Filter (P1)
**Project**: vskill-platform

**As a** developer looking specifically for extensible skills
**I want** a toggle button in the filter bar that filters the catalog to only extensible skills
**So that** I can quickly find skills I can customize for my project

**Acceptance Criteria**:
- [x] **AC-US2-01**: A teal-accented "Extensible N" toggle button appears in the Sort+Tier row (after the Tier filter group), where N is the count of extensible skills matching current category/tier/search filters
- [x] **AC-US2-02**: Clicking the toggle adds `?ext=true` to the URL and filters results to only skills with `extensible === true`
- [x] **AC-US2-03**: Clicking again removes the `?ext=true` parameter and shows all skills
- [x] **AC-US2-04**: The toggle uses teal accent (#0D9488) for its active state background, consistent with extensible branding
- [x] **AC-US2-05**: The count (N) updates correctly when combined with other filters (category, tier, search)
- [x] **AC-US2-06**: The `SkillFilters` type in `types.ts` includes an `extensible?: boolean` field
- [x] **AC-US2-07**: The `getSkills()` function in `data.ts` filters by `extensible` when the filter is provided
- [x] **AC-US2-08**: The `/api/v1/skills` route accepts an `extensible=true` query param and passes it to `getSkills()`

---

### US-003: Extension Point Types in Metrics Row (P2)
**Project**: vskill-platform

**As a** developer browsing extensible skills
**I want** to see the extension point types (e.g., "config", "template", "hook", "plugin") in the metrics row of each card when the extensible filter is active
**So that** I can understand what kind of customization each skill supports without opening the detail page

**Acceptance Criteria**:
- [x] **AC-US3-01**: When `?ext=true` is active, each extensible skill card's metrics row appends the unique extension point types as teal-colored text (e.g., "config template hook")
- [x] **AC-US3-02**: Extension point types are derived from `skill.extensionPoints[].type` and de-duplicated
- [x] **AC-US3-03**: When the extensible filter is NOT active, extension point types are NOT shown in the metrics row
- [x] **AC-US3-04**: Extension point types use the teal color (#0D9488) to visually distinguish them from other metrics

## Functional Requirements

### FR-001: Backend -- SkillFilters extensible field
The `SkillFilters` interface in `src/lib/types.ts` gains an optional `extensible?: boolean` field. When true, `getSkills()` filters to only skills where `extensible === true`.

### FR-002: Backend -- API route extensible param
The `/api/v1/skills` route accepts `extensible=true` query param, validates it as a boolean string, and passes `extensible: true` to `getSkills()`.

### FR-003: Frontend -- EXT pill badge component
A small inline teal pill ("EXT") rendered on each skill card row for extensible skills. Uses monospace font, uppercase, same color family as the detail page extensible pill.

### FR-004: Frontend -- Toggle button in filter bar
A toggle button in the Sort+Tier row. Active state has teal background; inactive state has standard border. Shows count of extensible skills matching current filters.

### FR-005: Frontend -- Extension point types in metrics
When `ext=true` filter is active, the metrics row of each extensible card appends de-duplicated extension point type labels in teal.

## Success Criteria

- Users can filter to extensible-only skills in one click
- EXT badge visible on all extensible skill cards across all filter states
- Extension point type info reduces clicks-to-understand by showing types inline
- No visual regression on existing catalog UI when extensible filter is inactive

## Out of Scope

- Full-text search by extension point type
- Extension point filtering by specific type (e.g., "only config" type)
- Client-side interactive components (all server-rendered)
- New database schema changes (data layer uses existing `extensible` and `extensionPoints` fields)

## Dependencies

- Existing `extensible` and `extensionPoints` fields on `SkillData` interface (already present)
- Existing seed data with extensible skills (already present)
- Existing teal color branding for extensible features on the detail page (already present)
