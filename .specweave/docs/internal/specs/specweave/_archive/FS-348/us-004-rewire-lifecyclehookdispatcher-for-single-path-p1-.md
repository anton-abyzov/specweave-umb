---
id: US-004
feature: FS-348
title: "Rewire LifecycleHookDispatcher for Single Path (P1)"
status: completed
priority: P1
created: 2026-02-25
tldr: "Rewire LifecycleHookDispatcher for Single Path (P1)"
project: specweave
---

# US-004: Rewire LifecycleHookDispatcher for Single Path (P1)

**Feature**: [FS-348](./FEATURE.md)

---

## Acceptance Criteria

- [x] **AC-US4-01**: `onIncrementPlanned()` routes GitHub sync through `LivingDocsSync.syncIncrement()` only (not ExternalIssueAutoCreator)
- [x] **AC-US4-02**: `onTaskCompleted()` routes GitHub sync through `LivingDocsSync.syncIncrement()` only (not SyncCoordinator)
- [x] **AC-US4-03**: `onIncrementDone()` routes GitHub closure through `GitHubFeatureSync` (not SyncCoordinator), keeps JIRA/ADO via SyncCoordinator
- [x] **AC-US4-04**: Increment reopen (`completed → active`) triggers `LivingDocsSync.syncIncrement()` → `GitHubFeatureSync` which auto-reopens issues

---

## Implementation

**Increment**: [0348-consolidate-github-sync-path](../../../../../increments/0348-consolidate-github-sync-path/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_
