---
id: US-006
feature: FS-404
title: "Safe Conflict Resolution"
status: completed
priority: P1
created: 2026-03-02
tldr: "**As a** user syncing bidirectionally with JIRA,."
---

# US-006: Safe Conflict Resolution

**Feature**: [FS-404](./FEATURE.md)

**As a** user syncing bidirectionally with JIRA,
**I want** conflicts to be surfaced for manual resolution (not silently auto-resolved),
**So that** I don't lose local changes without knowing.

---

## Acceptance Criteria

- [x] **AC-US6-01**: Conflicts are detected and reported to the user with both local and remote values
- [x] **AC-US6-02**: Default resolution strategy is configurable (`remote-wins`, `local-wins`, `manual`)
- [x] **AC-US6-03**: Silent auto-resolve is removed; `manual` is the default strategy
- [x] **AC-US6-04**: Conflict report is written to a file when conflicts are detected

---

## Implementation

**Increment**: [0404-jira-sync-plugin-fixes](../../../../../increments/0404-jira-sync-plugin-fixes/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_
