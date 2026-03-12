---
id: US-008
feature: FS-398
title: "Fix Reconciler Data Safety Gaps (P2)"
status: completed
priority: P0
created: "2026-03-02T00:00:00.000Z"
tldr: "**As a** user managing increment lifecycle."
project: specweave
---

# US-008: Fix Reconciler Data Safety Gaps (P2)

**Feature**: [FS-398](./FEATURE.md)

**As a** user managing increment lifecycle
**I want** reconciliation to be safe for all status transitions
**So that** issues don't get incorrectly reopened or left in wrong state

---

## Acceptance Criteria

- [x] **AC-US8-01**: Reconcilers treat `paused` status as "should be open" (missing from shouldBeOpen list in github-reconciler.ts line 153)
- [x] **AC-US8-02**: Reconcilers log a warning for unknown/missing status instead of silently skipping

---

## Implementation

**Increment**: [0398-sync-integration-critical-fixes](../../../../../increments/0398-sync-integration-critical-fixes/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_
