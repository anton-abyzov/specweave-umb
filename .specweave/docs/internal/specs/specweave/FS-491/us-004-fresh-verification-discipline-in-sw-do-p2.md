---
id: US-004
feature: FS-491
title: "Fresh Verification Discipline in sw:do (P2)"
status: completed
priority: P1
created: "2026-03-11T00:00:00.000Z"
tldr: "**As a** SpecWeave user completing tasks via sw:do."
project: specweave
external:
  github:
    issue: 1541
    url: "https://github.com/anton-abyzov/specweave/issues/1541"
---

# US-004: Fresh Verification Discipline in sw:do (P2)

**Feature**: [FS-491](./FEATURE.md)

**As a** SpecWeave user completing tasks via sw:do
**I want** an iron law enforced: no task marked [x] without fresh verification evidence from running the task's test command
**So that** completion claims are always backed by proof, not assumptions

---

## Acceptance Criteria

- [x] **AC-US4-01**: Given a task has a `**Test**:` block with a Given/When/Then, when the task is about to be marked [x], then the test command must be run and output captured as evidence
- [x] **AC-US4-02**: Given a task has no `**Test**:` block, when the task is about to be marked [x], then the project-level test command is run as fallback verification
- [x] **AC-US4-03**: Given the verification command fails, when the implementer attempts to mark [x], then the task remains [ ] and the failure output is presented for fixing
- [x] **AC-US4-04**: The SKILL.md states the iron law explicitly: "NO COMPLETION CLAIMS WITHOUT FRESH VERIFICATION EVIDENCE"

---

## Implementation

**Increment**: [0491-shift-quality-left-per-task-gates](../../../../../increments/0491-shift-quality-left-per-task-gates/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-006**: Verify Iron Law Statement Completeness in sw:do
