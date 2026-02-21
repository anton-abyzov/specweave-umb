---
id: US-004
feature: FS-286
title: "Range and Comma Toggle Syntax (P1)"
status: completed
priority: P1
created: 2026-02-21T00:00:00.000Z
tldr: "**As a** CLI user with many discovered skills
**I want** to toggle multiple items using ranges (1-3) and comma-separated lists (1,3,5)
**So that** I can efficiently select/deselect groups without toggling one by one."
project: vskill
---

# US-004: Range and Comma Toggle Syntax (P1)

**Feature**: [FS-286](./FEATURE.md)

**As a** CLI user with many discovered skills
**I want** to toggle multiple items using ranges (1-3) and comma-separated lists (1,3,5)
**So that** I can efficiently select/deselect groups without toggling one by one

---

## Acceptance Criteria

- [x] **AC-US4-01**: Input "1-3" toggles items 1, 2, and 3
- [x] **AC-US4-02**: Input "1,3,5" toggles items 1, 3, and 5
- [x] **AC-US4-03**: Input "1-3,5,7-9" toggles items 1, 2, 3, 5, 7, 8, 9 (mixed syntax)
- [x] **AC-US4-04**: Invalid ranges (e.g., "5-2", "0", "999") are silently ignored (no crash)
- [x] **AC-US4-05**: Ranges work in both skill selection and agent selection checkbox lists

---

## Implementation

**Increment**: [0286-vskill-install-ux](../../../../../increments/0286-vskill-install-ux/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_
