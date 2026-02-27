# Plan: Consolidate GitHub Sync to Single Path

## Architecture Change

```
BEFORE (3 paths):
  onIncrementPlanned → ExternalIssueAutoCreator (Path 1) ← REMOVE
  onTaskCompleted    → SyncCoordinator.syncIncrementClosure (Path 3) ← REMOVE
  onIncrementDone    → SyncCoordinator.syncIncrementClosure (Path 3) ← REMOVE
  AC change          → SyncCoordinator.syncACCheckboxesToGitHub ← EXTRACT

AFTER (1 path):
  ALL lifecycle events → LivingDocsSync.syncIncrement() → GitHubFeatureSync (Path 2)
  AC checkbox updates  → GitHubACCheckboxSync (extracted to plugin)
  JIRA/ADO closure     → SyncCoordinator (untouched)
```

## Execution Order

Phase 1 (independent, parallel-safe):
- T-001: Extract AC checkbox sync to GitHub plugin
- T-002: Remove GitHub from ExternalIssueAutoCreator

Phase 2 (depends on Phase 1):
- T-003: Remove GitHub methods from SyncCoordinator
- T-004: Rewire LifecycleHookDispatcher
- T-005: Rewire StatusChangeSyncTrigger

Phase 3:
- T-006: Update tests
- T-007: Run full test suite
