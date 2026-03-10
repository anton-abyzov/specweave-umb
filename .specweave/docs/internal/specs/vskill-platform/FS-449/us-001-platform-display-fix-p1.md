---
id: US-001
feature: FS-449
title: "Platform Display Fix (P1)"
status: completed
priority: P1
created: 2026-03-07T00:00:00.000Z
tldr: "**As a** skill marketplace user."
project: vskill-platform
related_projects: [vskill]
---

# US-001: Platform Display Fix (P1)

**Feature**: [FS-449](./FEATURE.md)

**As a** skill marketplace user
**I want** skill names to display as their short folder name with a separate publisher/repo label
**So that** I can quickly identify skills without seeing duplicated or garbled owner prefixes

---

## Acceptance Criteria

- [x] **AC-US1-01**: Given `SearchIndexEntry`, `SearchResult`, `TrendingSkillEntry`, and `SkillData` types, when the type definitions are inspected, then each includes `ownerSlug: string`, `repoSlug: string`, and `skillSlug: string` fields alongside the existing `name` field.
- [x] **AC-US1-02**: Given a search API response, when the search query endpoint (`/api/v1/skills/search`) returns results, then each result object includes populated `ownerSlug`, `repoSlug`, and `skillSlug` values sourced from the DB columns.
- [x] **AC-US1-03**: Given the search palette, when a user types a query and sees results, then each result label shows `skillSlug` as the primary name and `ownerSlug/repoSlug` as a secondary context (no owner duplication in the label).
- [x] **AC-US1-04**: Given the trending skills section on the homepage, when trending skills render, then each skill shows `skillSlug` as the primary name and `ownerSlug/repoSlug` as the faint publisher prefix (replacing the current `skill.author/skill.name` pattern).
- [x] **AC-US1-05**: Given the skills browse page, when `PublisherLink` receives skill data, then it receives `skillSlug` for the display name (not the full hierarchical `name`) and renders `author / skillSlug` without duplication.

---

## Implementation

**Increment**: [0449-fix-skill-display-names](../../../../../increments/0449-fix-skill-display-names/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-001**: Add slug fields to platform type definitions
- [x] **T-002**: Propagate slug fields through data mappers and search index builder
- [x] **T-003**: Fix SearchPalette to display skillSlug as primary name
- [x] **T-004**: Fix TrendingSkills to display skillSlug with ownerSlug prefix
- [x] **T-005**: Fix skills browse page to pass skillSlug to PublisherLink
- [x] **T-006**: Write backfill script for NULL slug fields and document index rebuild
