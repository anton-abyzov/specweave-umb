---
id: US-008
feature: FS-470
title: "Empty States and Error Handling"
status: completed
priority: P1
created: "2026-03-10T00:00:00.000Z"
tldr: "**As a** skill author launching the Studio with no skills or encountering errors."
project: vskill
external:
  github:
    issue: 66
    url: "https://github.com/anton-abyzov/vskill/issues/66"
---

# US-008: Empty States and Error Handling

**Feature**: [FS-470](./FEATURE.md)

**As a** skill author launching the Studio with no skills or encountering errors
**I want** meaningful empty states and error messages
**So that** I understand how to use the interface and what went wrong

---

## Acceptance Criteria

- [x] **AC-US8-01**: When no skill is selected, the right panel shows a centered empty state with the generated illustration and "Select a skill to view details" text in muted color
- [x] **AC-US8-02**: When `scanSkills()` returns zero skills, the left panel shows the existing empty state design ("No skills found" with root path hint and "Create Your First Skill" button)
- [x] **AC-US8-03**: When skill data fails to load (API error), the detail panel shows the error message with a retry button, styled with `var(--red-muted)` background
- [x] **AC-US8-04**: When the search filter returns no matches, the skill list shows "No skills match your search" with a "Clear search" link

---

## Implementation

**Increment**: [0470-skill-studio-full-redesign](../../../../../increments/0470-skill-studio-full-redesign/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-022**: Create `EmptyState.tsx` for all empty/error conditions
