---
id: US-002
feature: FS-348
title: "Remove GitHub methods from SyncCoordinator (P1)"
status: completed
priority: P1
created: 2026-02-25
tldr: "Remove GitHub methods from SyncCoordinator (P1)"
project: specweave
---

# US-002: Remove GitHub methods from SyncCoordinator (P1)

**Feature**: [FS-348](./FEATURE.md)

---

## Acceptance Criteria

- [x] **AC-US2-01**: `createGitHubIssuesForUserStories()` method removed from SyncCoordinator
- [x] **AC-US2-02**: `formatUserStoryBody()` fallback removed from SyncCoordinator
- [x] **AC-US2-03**: `closeGitHubIssuesForUserStories()` method removed from SyncCoordinator
- [x] **AC-US2-04**: `syncIncrementClosure()` delegates GitHub closure to GitHubFeatureSync, keeps JIRA/ADO closure
- [x] **AC-US2-05**: `syncIncrementCompletion()` no longer calls `createGitHubIssuesForUserStories()` for GitHub
- [x] **AC-US2-06**: Helper methods (`detectDuplicateIssue`, `updateIssueIfPlaceholder`) removed or inlined where needed

---

## Implementation

**Increment**: [0348-consolidate-github-sync-path](../../../../../increments/0348-consolidate-github-sync-path/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_
