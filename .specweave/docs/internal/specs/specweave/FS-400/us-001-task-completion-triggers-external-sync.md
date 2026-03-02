---
id: US-001
feature: FS-400
title: "Task completion triggers external sync"
status: completed
priority: P1
created: 2026-03-02
tldr: "**As a** developer using SpecWeave."
---

# US-001: Task completion triggers external sync

**Feature**: [FS-400](./FEATURE.md)

**As a** developer using SpecWeave
**I want** task completions to automatically sync progress to GitHub
**So that** GitHub issues reflect real-time AC checkbox progress without manual `/sw:progress-sync`

---

## Acceptance Criteria

- [x] **AC-US1-01**: When a task is marked complete (via Edit to tasks.md), the shell hook or MetadataManager calls `LifecycleHookDispatcher.onTaskCompleted()` within 5 seconds
- [x] **AC-US1-02**: `onTaskCompleted()` triggers `LivingDocsSync.syncIncrement()` when `post_task_completion.sync_tasks_md: true`
- [x] **AC-US1-03**: GitHub issue AC checkboxes update automatically after each task completion (not just on `/sw:done`)
- [x] **AC-US1-04**: The `active → ready_for_review` status transition is added to `StatusChangeSyncTrigger.isSyncWorthy()` list

---

## Implementation

**Increment**: [0400-sync-pipeline-reliability](../../../../../increments/0400-sync-pipeline-reliability/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_
