---
id: US-005
feature: FS-498
title: "Info Banner Explaining Origin Distinction"
status: completed
priority: P1
created: 2026-03-11T00:00:00.000Z
tldr: "**As a** skill developer."
project: vskill
external:
  github:
    issue: 95
    url: https://github.com/anton-abyzov/vskill/issues/95
---

# US-005: Info Banner Explaining Origin Distinction

**Feature**: [FS-498](./FEATURE.md)

**As a** skill developer
**I want** an informational banner in the sidebar explaining the Your Skills vs Installed distinction
**So that** I understand why some skills are separated and what the grouping means

---

## Acceptance Criteria

- [x] **AC-US5-01**: Given the sidebar contains both source and installed skills, when the sidebar renders, then an info banner is displayed above or between the two sections explaining the distinction
- [x] **AC-US5-02**: Given the user dismisses the info banner, when the sidebar re-renders in the same session, then the banner remains hidden
- [x] **AC-US5-03**: Given the info banner is shown, when the user reads it, then it explains that "Your Skills" are editable source skills and "Installed" are copies consumed by AI agents

---

## Implementation

**Increment**: [0498-studio-skill-origin-classification](../../../../../increments/0498-studio-skill-origin-classification/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-010**: Create `InfoBanner` component and integrate into `SkillGroupList`
