---
id: US-001
feature: FS-491
title: "Per-Task Review Gates in sw:do (P1)"
status: completed
priority: P1
created: 2026-03-11T00:00:00.000Z
tldr: "**As a** SpecWeave user executing tasks with sw:do."
project: specweave
external:
  github:
    issue: 1538
    url: https://github.com/anton-abyzov/specweave/issues/1538
---

# US-001: Per-Task Review Gates in sw:do (P1)

**Feature**: [FS-491](./FEATURE.md)

**As a** SpecWeave user executing tasks with sw:do
**I want** two lightweight review subagents (spec-compliance + code-quality) to run after each task completion
**So that** spec drift and code quality issues are caught immediately rather than accumulating until increment closure

---

## Acceptance Criteria

- [x] **AC-US1-01**: Given `quality.perTaskReview: true` in config.json, when sw:do completes a task (before marking [x]), then two subagent reviews run: (1) spec-compliance reviewer checking AC-by-AC alignment, (2) code-quality reviewer doing focused diff review
- [x] **AC-US1-02**: Given the spec-compliance reviewer finds a misalignment, when the review completes, then the implementer must fix the issue before proceeding to the next task
- [x] **AC-US1-03**: Given the code-quality reviewer finds issues, when the review completes, then the implementer must address findings before proceeding to the next task
- [x] **AC-US1-04**: Given `quality.perTaskReview` is absent or false in config.json, when sw:do runs, then per-task review gates are skipped entirely (backward compatible)
- [x] **AC-US1-05**: Given team-lead is active (detected via team-lead state), when sw:do runs, then per-task review gates are skipped (team-lead has its own review flow)

---

## Implementation

**Increment**: [0491-shift-quality-left-per-task-gates](../../../../../increments/0491-shift-quality-left-per-task-gates/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-001**: Add Fresh Verification Iron Law to sw:do Step 6
- [x] **T-002**: Add Per-Task Review Gate (Step 6.5) to sw:do
