---
id: US-003
feature: FS-497
title: "Apply AI Fix integration (P1)"
status: completed
priority: P1
created: "2026-03-11T00:00:00.000Z"
tldr: "**As a** skill author."
project: vskill
---

# US-003: Apply AI Fix integration (P1)

**Feature**: [FS-497](./FEATURE.md)

**As a** skill author
**I want** to click "Apply AI Fix" and have the system improve my skill
**So that** I don't have to manually figure out how to fix weaknesses

---

## Acceptance Criteria

- [x] **AC-US3-01**: "Apply AI Fix" navigates to workspace editor with comparison context as notes
- [x] **AC-US3-02**: Reuses existing /improve endpoint — zero duplication of improve infrastructure

---

## Implementation

**Increment**: [0497-comparison-action-items](../../../../../increments/0497-comparison-action-items/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-006**: Add action_items phase to ProgressLog spinner
- [x] **T-007**: Fix 404 console noise on benchmark/latest
- [x] **T-008**: Run tests — all 1076 pass, TypeScript clean
