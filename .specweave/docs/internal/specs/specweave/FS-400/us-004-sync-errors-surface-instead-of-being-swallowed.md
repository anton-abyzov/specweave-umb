---
id: US-004
feature: FS-400
title: "Sync errors surface instead of being swallowed"
status: completed
priority: P1
created: 2026-03-02
tldr: "**As a** developer."
---

# US-004: Sync errors surface instead of being swallowed

**Feature**: [FS-400](./FEATURE.md)

**As a** developer
**I want** sync failures to be reported visibly
**So that** I know when GitHub sync failed and can take action

---

## Acceptance Criteria

- [x] **AC-US4-01**: `LifecycleHookDispatcher` logs sync failures as warnings (not just stderr) and includes them in the command output
- [x] **AC-US4-02**: `/sw:done` reports sync status in its summary output (e.g., "GitHub: 3 issues closed, milestone closed" or "GitHub sync failed: <reason>")
- [x] **AC-US4-03**: Sync failures do NOT block `/sw:done` from completing (non-fatal), but the failure is clearly communicated

---

## Implementation

**Increment**: [0400-sync-pipeline-reliability](../../../../../increments/0400-sync-pipeline-reliability/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_
