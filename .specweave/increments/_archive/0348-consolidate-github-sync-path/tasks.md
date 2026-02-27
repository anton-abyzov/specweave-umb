# Tasks: 0348-consolidate-github-sync-path

### T-001: Extract AC checkbox sync to GitHub plugin
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02 | **Status**: [x] completed
**Test**: Given SyncCoordinator has `syncACCheckboxesToGitHub()` → When extracted to `plugins/specweave-github/lib/github-ac-checkbox-sync.ts` → Then new class works identically with same interface

### T-002: Remove GitHub from ExternalIssueAutoCreator
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-04 | **Status**: [x] completed
**Test**: Given `autoCreateExternalIssue()` detects GitHub provider → When called → Then it skips GitHub creation (LivingDocsSync chain handles it) and JIRA/ADO still work

### T-003: Remove GitHub methods from SyncCoordinator
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-05, AC-US2-06 | **Status**: [x] completed
**Test**: Given SyncCoordinator → When GitHub methods removed → Then `syncIncrementCompletion()` skips GitHub, `syncIncrementClosure()` delegates GitHub to GitHubFeatureSync, JIRA/ADO closure untouched

### T-004: Rewire LifecycleHookDispatcher
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02, AC-US4-03 | **Status**: [x] completed
**Test**: Given `onIncrementPlanned()` → When `auto_create_github_issue: true` → Then routes through `LivingDocsSync.syncIncrement()` not ExternalIssueAutoCreator

### T-005: Rewire StatusChangeSyncTrigger
**User Story**: US-001, US-002 | **Satisfies ACs**: AC-US1-03, AC-US2-04 | **Status**: [x] completed
**Test**: Given `autoCreateIfNeeded()` → When called → Then skips GitHub (LivingDocsSync at line 203 already handles it). Given `autoCloseExternalIssues()` → When called → Then delegates GitHub to GitHubFeatureSync

### T-006: Update callers of AC checkbox sync
**User Story**: US-003 | **Satisfies ACs**: AC-US3-03, AC-US3-04, AC-US3-05 | **Status**: [x] completed
**Test**: Given `update-ac-status.ts` and `sync-progress.ts` → When they call AC checkbox sync → Then they import from `GitHubACCheckboxSync` not SyncCoordinator

### T-007: Update tests
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01, AC-US5-02, AC-US5-03, AC-US5-04 | **Status**: [x] completed
**Test**: Given all tests → When run → Then pass with updated imports and removed GitHub-specific SyncCoordinator tests
