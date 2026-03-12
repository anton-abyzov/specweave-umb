---
id: US-004
feature: FS-452
title: "Rejection stage indicator (P2)"
status: completed
priority: P1
created: 2026-03-07T00:00:00.000Z
tldr: "**As a** platform visitor."
project: vskill-platform
---

# US-004: Rejection stage indicator (P2)

**Feature**: [FS-452](./FEATURE.md)

**As a** platform visitor
**I want** to see a visual indicator showing at which pipeline stage the skill was rejected
**So that** I can quickly assess the nature of the rejection (early structural failure vs. late security failure)

---

## Acceptance Criteria

- [x] **AC-US4-01**: A stage indicator shows a simplified pipeline (Submission > Structure > Security > Review) with the failure point highlighted
- [x] **AC-US4-02**: The stage indicator maps `rejectionTrigger` values to the correct pipeline stage
- [x] **AC-US4-03**: When `rejectionTrigger` is undefined, the stage indicator is hidden rather than showing an incorrect stage

---

## Implementation

**Increment**: [0452-rejected-skill-detail-view](../../../../../increments/0452-rejected-skill-detail-view/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_
