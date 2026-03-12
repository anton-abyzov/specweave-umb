---
id: US-003
feature: FS-498
title: "Visual De-emphasis of Installed Skills"
status: completed
priority: P1
created: 2026-03-11T00:00:00.000Z
tldr: "**As a** skill developer."
project: vskill
external:
  github:
    issue: 93
    url: https://github.com/anton-abyzov/vskill/issues/93
---

# US-003: Visual De-emphasis of Installed Skills

**Feature**: [FS-498](./FEATURE.md)

**As a** skill developer
**I want** installed skills to appear visually dimmed with a distinguishing icon
**So that** I can quickly scan past them and focus on my editable skills

---

## Acceptance Criteria

- [x] **AC-US3-01**: Given a skill card for an installed skill, when rendered in the sidebar, then the card text has opacity 0.7
- [x] **AC-US3-02**: Given a skill card for an installed skill, when rendered in the sidebar, then a lock SVG icon is displayed before the skill name
- [x] **AC-US3-03**: Given a skill card for a source skill, when rendered in the sidebar, then no lock icon is shown and text has opacity 1.0

---

## Implementation

**Increment**: [0498-studio-skill-origin-classification](../../../../../increments/0498-studio-skill-origin-classification/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-005**: Add lock icon and reduced-opacity styling to installed `SkillCard`
