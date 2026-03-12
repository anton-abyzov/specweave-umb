---
id: US-002
feature: FS-498
title: "Sidebar Split into Source and Installed Sections"
status: completed
priority: P1
created: 2026-03-11T00:00:00.000Z
tldr: "**As a** skill developer."
project: vskill
external:
  github:
    issue: 92
    url: https://github.com/anton-abyzov/vskill/issues/92
---

# US-002: Sidebar Split into Source and Installed Sections

**Feature**: [FS-498](./FEATURE.md)

**As a** skill developer
**I want** the studio sidebar to display "Your Skills" at the top and "Installed" below
**So that** I can immediately identify which skills I should be editing

---

## Acceptance Criteria

- [x] **AC-US2-01**: Given the sidebar loads skills, when skills have mixed origins, then source skills appear under a "Your Skills" section header and installed skills appear under an "Installed" section header
- [x] **AC-US2-02**: Given all skills are source skills, when the sidebar renders, then only the "Your Skills" section is shown (no empty "Installed" section)
- [x] **AC-US2-03**: Given all skills are installed skills, when the sidebar renders, then only the "Installed" section is shown (no empty "Your Skills" section)
- [x] **AC-US2-04**: Given the search filter is active, when filtering skills, then the origin-based grouping is preserved within filtered results

---

## Implementation

**Increment**: [0498-studio-skill-origin-classification](../../../../../increments/0498-studio-skill-origin-classification/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-003**: Update frontend types and `StudioContext` to propagate `origin`
- [x] **T-004**: Split `SkillGroupList` into "Your Skills" and "Installed" sections
