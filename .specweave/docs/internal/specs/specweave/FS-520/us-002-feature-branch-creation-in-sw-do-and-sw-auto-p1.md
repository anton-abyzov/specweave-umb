---
id: US-002
feature: FS-520
title: "Feature Branch Creation in sw:do and sw:auto (P1)"
status: completed
priority: P1
created: 2026-03-13T00:00:00.000Z
tldr: "**As a** developer starting increment work."
project: specweave
external:
  github:
    issue: 1563
    url: https://github.com/anton-abyzov/specweave/issues/1563
---

# US-002: Feature Branch Creation in sw:do and sw:auto (P1)

**Feature**: [FS-520](./FEATURE.md)

**As a** developer starting increment work
**I want** `sw:do` and `sw:auto` to automatically create a local feature branch when `pushStrategy` is `pr-based`
**So that** all my commits are isolated from the target branch

---

## Acceptance Criteria

- [x] **AC-US2-01**: Given `pushStrategy` is `"pr-based"` and the developer is on the target branch, when `sw:do` starts (Step 2.7), then a local branch named `{branchPrefix}{increment-id}` is created and checked out (e.g., `sw/0520-pr-based-increment-closure`)
- [x] **AC-US2-02**: Given `pushStrategy` is `"pr-based"` and the developer is already on a non-target branch, when `sw:do` starts, then the existing branch is used as-is without renaming
- [x] **AC-US2-03**: Given `pushStrategy` is `"pr-based"` and the feature branch already exists locally, when `sw:do` starts, then it checks out the existing branch instead of creating a new one
- [x] **AC-US2-04**: Given `pushStrategy` is `"direct"`, when `sw:do` starts, then no branch creation occurs and the existing branch is used unchanged
- [x] **AC-US2-05**: Given `pushStrategy` is `"pr-based"` and there are uncommitted changes in the working tree, when the branch is created, then the uncommitted changes carry over to the new branch (standard `git checkout -b` behavior)

---

## Implementation

**Increment**: [0520-pr-based-increment-closure](../../../../../increments/0520-pr-based-increment-closure/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-004**: Add Step 2.7 (Feature Branch Setup) to sw:do SKILL.md
- [x] **T-005**: Verify sw:auto inherits branch creation via sw:do delegation
