---
id: US-007
feature: FS-404
title: "Reorganization Detector Reliability"
status: completed
priority: P1
created: 2026-03-02
tldr: "**As a** user relying on JIRA issue reorganization detection,."
---

# US-007: Reorganization Detector Reliability

**Feature**: [FS-404](./FEATURE.md)

**As a** user relying on JIRA issue reorganization detection,
**I want** the detector to correctly identify real reparenting events and execute handlers,
**So that** my local hierarchy stays in sync with JIRA changes.

---

## Acceptance Criteria

- [x] **AC-US7-01**: REPARENTED event fires only when `parent` or Epic Link field actually changes
- [x] **AC-US7-02**: Reorganization handler executes real hierarchy update logic (not a stub)
- [x] **AC-US7-03**: False positive rate for REPARENTED events is zero for non-parent-changing updates

---

## Implementation

**Increment**: [0404-jira-sync-plugin-fixes](../../../../../increments/0404-jira-sync-plugin-fixes/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_
