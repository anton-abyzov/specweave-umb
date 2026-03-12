---
id: US-003
feature: FS-488
title: "Tests Panel Scroll Containment"
status: completed
priority: P1
created: "2026-03-11T00:00:00.000Z"
tldr: "**As a** skill author."
project: vskill
---

# US-003: Tests Panel Scroll Containment

**Feature**: [FS-488](./FEATURE.md)

**As a** skill author
**I want** long prompt and expected-output content to be contained within a scrollable area
**So that** assertions and action buttons remain visible without excessive scrolling

---

## Acceptance Criteria

- [x] **AC-US3-01**: Given a prompt longer than 200px of rendered height, when the case detail is displayed, then the prompt section has `max-height` with `overflow-y: auto` and shows a scroll indicator
- [x] **AC-US3-02**: Given an expected-output section longer than 200px, when displayed, then it has the same scroll containment behavior as the prompt section

---

## Implementation

**Increment**: [0488-skill-studio-status-ux](../../../../../increments/0488-skill-studio-status-ux/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-004**: Add max-height and overflow-y to prompt and expected-output sections
