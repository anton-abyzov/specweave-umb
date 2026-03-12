---
id: US-004
feature: FS-470
title: "New Skill Creation Button and Flow"
status: completed
priority: P1
created: "2026-03-10T00:00:00.000Z"
tldr: "**As a** skill author."
project: vskill
external:
  github:
    issue: 62
    url: "https://github.com/anton-abyzov/vskill/issues/62"
---

# US-004: New Skill Creation Button and Flow

**Feature**: [FS-470](./FEATURE.md)

**As a** skill author
**I want** a prominent "New Skill" button in the skill list panel
**So that** I can create a new skill without navigating to a separate page

---

## Acceptance Criteria

- [x] **AC-US4-01**: A "New Skill" button is rendered at the top of the skill list panel (below the search input), styled with `var(--accent)` background and a plus icon
- [x] **AC-US4-02**: Clicking "New Skill" renders the existing `CreateSkillPage` content in the right detail panel instead of navigating to a separate route
- [x] **AC-US4-03**: After successful skill creation, the skill list refreshes and the newly created skill is automatically selected
- [x] **AC-US4-04**: While the creation form is active, the "New Skill" button in the list panel shows an active state

---

## Implementation

**Increment**: [0470-skill-studio-full-redesign](../../../../../increments/0470-skill-studio-full-redesign/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-016**: Create `CreateSkillInline.tsx` adapting `CreateSkillPage`
- [x] **T-017**: Add "New Skill" button to `LeftPanel` with active state
