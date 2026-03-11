---
id: US-001
feature: FS-488
title: "Correct Empty-Assertions Case Status"
status: completed
priority: P1
created: 2026-03-11T00:00:00.000Z
tldr: "**As a** skill author."
project: vskill
---

# US-001: Correct Empty-Assertions Case Status

**Feature**: [FS-488](./FEATURE.md)

**As a** skill author
**I want** a test case with zero assertions to report `status: "fail"` (not "pass")
**So that** the sidebar badge never falsely displays "Passing" for untested cases

---

## Acceptance Criteria

- [x] **AC-US1-01**: Given a test case with an empty assertions array, when `runSingleCaseSSE` computes the case status, then `status` is `"fail"` and `pass_rate` is `0`
- [x] **AC-US1-02**: Given a test case with one or more assertions all passing, when the case status is computed, then `status` is `"pass"` (no regression to existing behavior)

---

## Implementation

**Increment**: [0488-skill-studio-status-ux](../../../../../increments/0488-skill-studio-status-ux/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-001**: Guard empty assertions in benchmark-runner.ts
