---
id: US-002
feature: FS-400
title: "Milestone lifecycle is fully automated"
status: completed
priority: P1
created: 2026-03-02
tldr: "**As a** developer."
---

# US-002: Milestone lifecycle is fully automated

**Feature**: [FS-400](./FEATURE.md)

**As a** developer
**I want** GitHub milestones to be created on increment planning and closed on increment completion
**So that** milestones accurately reflect increment status without manual intervention

---

## Acceptance Criteria

- [x] **AC-US2-01**: `GitHubReconciler.closeCompletedIncrementIssues()` reads milestone numbers from BOTH `externalLinks.github.milestone` AND `github.milestone` fields
- [x] **AC-US2-02**: When `/sw:done` runs and `externalLinks` is empty but `github` field has data, the reconciler still finds and closes the milestone
- [x] **AC-US2-03**: When `/sw:done` runs and neither field has a milestone, a full sync is triggered BEFORE attempting closure (auto-recovery)
- [x] **AC-US2-04**: Duplicate milestone detection — before creating a new milestone, check if one with the same title already exists

---

## Implementation

**Increment**: [0400-sync-pipeline-reliability](../../../../../increments/0400-sync-pipeline-reliability/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_
