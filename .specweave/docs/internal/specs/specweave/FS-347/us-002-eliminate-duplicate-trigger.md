---
id: US-002
feature: FS-347
title: "Eliminate Duplicate Trigger"
status: completed
priority: P1
created: 2026-02-25
tldr: "**As a** developer
**I want** `syncIncrementClosure()` to execute only once per increment completion
**So that** there are no redundant API calls to external tools."
---

# US-002: Eliminate Duplicate Trigger

**Feature**: [FS-347](./FEATURE.md)

**As a** developer
**I want** `syncIncrementClosure()` to execute only once per increment completion
**So that** there are no redundant API calls to external tools

---

## Acceptance Criteria

- [x] **AC-US2-01**: `LifecycleHookDispatcher.onIncrementDone()` skips `syncClosure()` when `StatusChangeSyncTrigger` handles it, OR a process-level/filesystem lock prevents the second execution
- [x] **AC-US2-02**: No regression — external issues still get closed when increment completes

---

## Implementation

**Increment**: [0347-fix-duplicate-sync-comments](../../../../../increments/0347-fix-duplicate-sync-comments/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_
