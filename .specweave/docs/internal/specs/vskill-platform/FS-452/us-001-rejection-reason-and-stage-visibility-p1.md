---
id: US-001
feature: FS-452
title: "Rejection reason and stage visibility (P1)"
status: completed
priority: P1
created: 2026-03-07T00:00:00.000Z
tldr: "**As a** skill author."
project: vskill-platform
---

# US-001: Rejection reason and stage visibility (P1)

**Feature**: [FS-452](./FEATURE.md)

**As a** skill author
**I want** to see the specific rejection reason, trigger stage, and timestamp on the rejected skill page
**So that** I understand exactly why my skill was rejected and at which point in the pipeline it failed

---

## Acceptance Criteria

- [x] **AC-US1-01**: The rejected skill detail page displays the `rejectionReason` from the state event metadata, or a sensible default message if none exists
- [x] **AC-US1-02**: The `rejectionTrigger` (e.g. "tier1_scan", "framework_plugin", "manual_review") is displayed as a labeled row
- [x] **AC-US1-03**: The submission date (`createdAt`) and rejection date (`updatedAt`) are both displayed in human-readable format
- [x] **AC-US1-04**: The page renders correctly when `rejectionReason` and `rejectionTrigger` are both undefined (graceful fallback)

---

## Implementation

**Increment**: [0452-rejected-skill-detail-view](../../../../../increments/0452-rejected-skill-detail-view/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_
