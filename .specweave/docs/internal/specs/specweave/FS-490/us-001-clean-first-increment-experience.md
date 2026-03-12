---
id: US-001
feature: FS-490
title: Clean first increment experience
status: complete
priority: P1
created: 2026-03-11
project: specweave
---
# US-001: Clean first increment experience

**Feature**: [FS-490](./FEATURE.md)

new SpecWeave user
**I want** my first increment to be numbered `0001`
**So that** there are no confusing phantom increments in my project

---

## Acceptance Criteria

- [x] **AC-US1-01**: Running `specweave init` does not create any folder under `.specweave/increments/`
- [x] **AC-US1-02**: After init, `IncrementNumberManager.getNextIncrementNumber()` returns `"0001"`
- [x] **AC-US1-03**: The quick-start guide shows the first user increment as `0001-click-counter` (not `0002`)

---

## Implementation

**Increment**: [0490-remove-init-increment-reservation](../../../../../increments/0490-remove-init-increment-reservation/spec.md)

