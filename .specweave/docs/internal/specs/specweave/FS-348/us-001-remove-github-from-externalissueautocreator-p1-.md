---
id: US-001
feature: FS-348
title: Remove GitHub from ExternalIssueAutoCreator (P1)
status: completed
priority: P1
created: 2026-02-25
tldr: Remove GitHub from ExternalIssueAutoCreator (P1)
project: specweave
external:
  github:
    issue: 1355
    url: https://github.com/anton-abyzov/specweave/issues/1355
---

# US-001: Remove GitHub from ExternalIssueAutoCreator (P1)

**Feature**: [FS-348](./FEATURE.md)

---

## Acceptance Criteria

- [x] **AC-US1-01**: `ExternalIssueAutoCreator.autoCreateExternalIssue()` skips GitHub provider (delegates to LivingDocsSync chain which calls GitHubFeatureSync)
- [x] **AC-US1-02**: `LifecycleHookDispatcher.onIncrementPlanned()` no longer calls `autoCreateExternalIssue()` for GitHub; uses `LivingDocsSync.syncIncrement()` path instead
- [x] **AC-US1-03**: `StatusChangeSyncTrigger.autoCreateIfNeeded()` no longer calls `autoCreateExternalIssue()` for GitHub — LivingDocsSync at line 203 already handles it
- [x] **AC-US1-04**: JIRA and ADO auto-creation in ExternalIssueAutoCreator remains fully functional
- [x] **AC-US1-05**: Backward compat — if `auto_create_github_issue: true` but `sync_living_docs: false`, GitHub issues still get created via LivingDocsSync fallback

---

## Implementation

**Increment**: [0348-consolidate-github-sync-path](../../../../../increments/0348-consolidate-github-sync-path/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-005**: Rewire StatusChangeSyncTrigger
