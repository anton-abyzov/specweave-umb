---
id: US-006
feature: FS-400
title: "Stale milestone cleanup command"
status: completed
priority: P1
created: 2026-03-02
tldr: "**As a** developer."
---

# US-006: Stale milestone cleanup command

**Feature**: [FS-400](./FEATURE.md)

**As a** developer
**I want** a command to reconcile stale GitHub milestones
**So that** milestones for completed increments are closed without manual `gh api` calls

---

## Acceptance Criteria

- [x] **AC-US6-01**: `specweave sync-reconcile` (or added to existing `sync-progress`) scans all completed increments and closes any open milestones whose issues are all closed
- [x] **AC-US6-02**: Duplicate milestones (same FS-XXX title, different milestone numbers) are detected — the empty one is closed
- [x] **AC-US6-03**: The command outputs a summary of actions taken (N milestones closed, N duplicates resolved)

---

## Implementation

**Increment**: [0400-sync-pipeline-reliability](../../../../../increments/0400-sync-pipeline-reliability/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_
