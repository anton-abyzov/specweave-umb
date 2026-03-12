---
id: US-002
feature: FS-470
title: "Scrollable Skill List with Search and Filter"
status: completed
priority: P1
created: "2026-03-10T00:00:00.000Z"
tldr: "**As a** skill author looking for a specific skill."
project: vskill
external:
  github:
    issue: 60
    url: "https://github.com/anton-abyzov/vskill/issues/60"
---

# US-002: Scrollable Skill List with Search and Filter

**Feature**: [FS-470](./FEATURE.md)

**As a** skill author looking for a specific skill
**I want** an inline search input and plugin group filter in the skill list panel
**So that** I can quickly find skills without scrolling through the entire list

---

## Acceptance Criteria

- [x] **AC-US2-01**: An inline search input at the top of the left panel filters skills by name with 200ms debounce, performed client-side against the already-loaded skill list (local skill counts are small, no server-side search needed)
- [x] **AC-US2-02**: Skills are grouped by plugin name with a group header showing the plugin name and skill count, matching the current `SkillListPage` grouping pattern
- [x] **AC-US2-03**: Each skill card shows: skill name, eval count, assertion count, benchmark status pill (Passing/Failing/Pending/No evals with color coding from existing `STATUS_CONFIG`), and last benchmark date
- [x] **AC-US2-04**: A total skill count is displayed below the search input (e.g., "12 skills across 3 plugins")
- [x] **AC-US2-05**: Empty search results show "No skills match your search" with a clear button

---

## Implementation

**Increment**: [0470-skill-studio-full-redesign](../../../../../increments/0470-skill-studio-full-redesign/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-009**: Create `SkillSearch.tsx` with 200ms debounce
- [x] **T-010**: Create `SkillCard.tsx` and `SkillGroupHeader` components
- [x] **T-011**: Create `SkillGroupList.tsx` and wire StudioContext filtering
