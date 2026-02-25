---
status: completed
---
# FS-348: Consolidate GitHub Sync to Single Path

**Project**: specweave
**Status**: active
**Priority**: P1

## Problem

Three competing code paths create GitHub issues with different quality levels:
- **Path 1** (`ExternalIssueAutoCreator.createGitHubIssues`) — medium body, basic labels
- **Path 2** (`GitHubFeatureSync` + `UserStoryIssueBuilder`) — rich body with progress, ACs, tasks, status labels, comments, reopen/close logic
- **Path 3** (`SyncCoordinator.formatUserStoryBody`) — minimal body with no labels (e.g. issue #1279)

This creates inconsistent GitHub issues and duplicate sync logic across ~900 lines of code.

## Solution

Consolidate all GitHub sync operations to Path 2 (`GitHubFeatureSync`). Remove GitHub-specific code from `ExternalIssueAutoCreator` and `SyncCoordinator`. Extract AC checkbox sync to the GitHub plugin. Keep JIRA/ADO paths untouched.

---

## User Stories

### US-001: Remove GitHub from ExternalIssueAutoCreator (P1)

**As a** developer, **I want** GitHub issue creation routed through GitHubFeatureSync instead of ExternalIssueAutoCreator, **so that** all issues have consistent rich bodies and labels.

#### Acceptance Criteria

- [x] AC-US1-01: `ExternalIssueAutoCreator.autoCreateExternalIssue()` skips GitHub provider (delegates to LivingDocsSync chain which calls GitHubFeatureSync)
- [x] AC-US1-02: `LifecycleHookDispatcher.onIncrementPlanned()` no longer calls `autoCreateExternalIssue()` for GitHub; uses `LivingDocsSync.syncIncrement()` path instead
- [x] AC-US1-03: `StatusChangeSyncTrigger.autoCreateIfNeeded()` no longer calls `autoCreateExternalIssue()` for GitHub — LivingDocsSync at line 203 already handles it
- [x] AC-US1-04: JIRA and ADO auto-creation in ExternalIssueAutoCreator remains fully functional
- [x] AC-US1-05: Backward compat — if `auto_create_github_issue: true` but `sync_living_docs: false`, GitHub issues still get created via LivingDocsSync fallback

### US-002: Remove GitHub methods from SyncCoordinator (P1)

**As a** developer, **I want** GitHub-specific methods removed from SyncCoordinator, **so that** it becomes provider-agnostic for GitHub operations.

#### Acceptance Criteria

- [x] AC-US2-01: `createGitHubIssuesForUserStories()` method removed from SyncCoordinator
- [x] AC-US2-02: `formatUserStoryBody()` fallback removed from SyncCoordinator
- [x] AC-US2-03: `closeGitHubIssuesForUserStories()` method removed from SyncCoordinator
- [x] AC-US2-04: `syncIncrementClosure()` delegates GitHub closure to GitHubFeatureSync, keeps JIRA/ADO closure
- [x] AC-US2-05: `syncIncrementCompletion()` no longer calls `createGitHubIssuesForUserStories()` for GitHub
- [x] AC-US2-06: Helper methods (`detectDuplicateIssue`, `updateIssueIfPlaceholder`) removed or inlined where needed

### US-003: Extract AC Checkbox Sync to GitHub Plugin (P1)

**As a** developer, **I want** the AC checkbox regex sync extracted from SyncCoordinator into the GitHub plugin, **so that** GitHub-specific code lives in the GitHub plugin.

#### Acceptance Criteria

- [x] AC-US3-01: New `GitHubACCheckboxSync` class in `plugins/specweave-github/lib/github-ac-checkbox-sync.ts`
- [x] AC-US3-02: `syncACCheckboxesToGitHub()` and `parseACStatusFromSpec()` moved from SyncCoordinator to the new class
- [x] AC-US3-03: `update-ac-status.ts` hook updated to import from new location
- [x] AC-US3-04: `sync-progress.ts` CLI updated to import from new location
- [x] AC-US3-05: SyncCoordinator no longer has any `syncACCheckboxesToGitHub` or `parseACStatusFromSpec` methods

### US-004: Rewire LifecycleHookDispatcher for Single Path (P1)

**As a** developer, **I want** all lifecycle hooks to route GitHub sync through GitHubFeatureSync, **so that** the full lifecycle (create, update, close, reopen) uses one consistent path.

#### Acceptance Criteria

- [x] AC-US4-01: `onIncrementPlanned()` routes GitHub sync through `LivingDocsSync.syncIncrement()` only (not ExternalIssueAutoCreator)
- [x] AC-US4-02: `onTaskCompleted()` routes GitHub sync through `LivingDocsSync.syncIncrement()` only (not SyncCoordinator)
- [x] AC-US4-03: `onIncrementDone()` routes GitHub closure through `GitHubFeatureSync` (not SyncCoordinator), keeps JIRA/ADO via SyncCoordinator
- [x] AC-US4-04: Increment reopen (`completed → active`) triggers `LivingDocsSync.syncIncrement()` → `GitHubFeatureSync` which auto-reopens issues

### US-005: Update Tests (P2)

**As a** developer, **I want** tests updated to reflect the consolidated sync architecture, **so that** test suite passes and validates the new flow.

#### Acceptance Criteria

- [x] AC-US5-01: `sync-coordinator.test.ts` updated — removed GitHub method tests, added tests for non-GitHub closure delegation
- [x] AC-US5-02: `external-issue-auto-creator.test.ts` updated — GitHub provider skipped, JIRA/ADO still tested
- [x] AC-US5-03: `LifecycleHookDispatcher` tests updated for rewired hooks
- [x] AC-US5-04: All existing integration tests pass
