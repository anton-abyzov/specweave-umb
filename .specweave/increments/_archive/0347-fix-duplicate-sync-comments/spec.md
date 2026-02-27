---
status: completed
---
# 0347 - Fix Duplicate Completion Comments on External Tools

## Problem

When `/sw:done` completes an increment, two independent code paths both call `SyncCoordinator.syncIncrementClosure()`:

1. **`StatusChangeSyncTrigger`** — fire-and-forget async IIFE from `MetadataManager.updateStatus()` (metadata-manager.ts:487)
2. **`LifecycleHookDispatcher.onIncrementDone()`** — awaited from `completeIncrement()` (status-commands.ts:301)

Both create separate `SyncCoordinator` instances with no shared state, so each independently posts the "User Story Complete" comment. The existing `state === 'closed'` guard is susceptible to race conditions — both calls see the issue as OPEN before either completes.

**JIRA already has dedup** (sync-coordinator.ts:1375) via `getLastComment()` comparison. GitHub and ADO do not.

## User Stories

### US-001: Idempotent Completion Comments

**As a** developer using SpecWeave with GitHub/JIRA/ADO sync
**I want** completion comments to be posted exactly once per user story
**So that** my issue threads are clean and professional

#### Acceptance Criteria

- [x] AC-US1-01: GitHub completion comments use `getLastComment()` dedup before posting (mirrors JIRA pattern)
- [x] AC-US1-02: ADO client has a `getLastComment()` method for idempotency checks
- [x] AC-US1-03: ADO completion comments use `getLastComment()` dedup before posting
- [x] AC-US1-04: `syncIncrementClosure()` uses a filesystem lock per increment to prevent concurrent execution
- [x] AC-US1-05: Existing JIRA dedup continues to work unchanged
- [x] AC-US1-06: Unit tests cover dedup logic for GitHub and ADO paths

### US-002: Eliminate Duplicate Trigger

**As a** developer
**I want** `syncIncrementClosure()` to execute only once per increment completion
**So that** there are no redundant API calls to external tools

#### Acceptance Criteria

- [x] AC-US2-01: `LifecycleHookDispatcher.onIncrementDone()` skips `syncClosure()` when `StatusChangeSyncTrigger` handles it, OR a process-level/filesystem lock prevents the second execution
- [x] AC-US2-02: No regression — external issues still get closed when increment completes

## Technical Context

### Call Chain (Current — Broken)

```
completeIncrement()
  ├── MetadataManager.updateStatus(COMPLETED)
  │     └── (async IIFE, not awaited) StatusChangeSyncTrigger
  │           └── SyncCoordinator.syncIncrementClosure() ← CALL 1
  │                 └── closeGitHubIssuesForUserStories()
  │                       └── client.closeIssue(n, comment) ← COMMENT #1
  │
  └── LifecycleHookDispatcher.onIncrementDone()
        └── syncClosure()
              └── SyncCoordinator.syncIncrementClosure() ← CALL 2
                    └── closeGitHubIssuesForUserStories()
                          └── client.closeIssue(n, comment) ← COMMENT #2
```

### Key Files

| File | Role |
|------|------|
| `src/sync/sync-coordinator.ts` | Main fix — add dedup to GitHub (line ~612) and ADO (line ~1472) |
| `src/integrations/ado/ado-client.ts` | Add `getLastComment()` method |
| `plugins/specweave-github/lib/github-client-v2.ts` | `getLastComment()` already exists (line 606) |
| `src/core/increment/status-commands.ts` | Trigger source (line 294, 301) |
| `src/core/hooks/LifecycleHookDispatcher.ts` | Second trigger (line 171-181) |
| `src/sync/format-preservation-sync.ts` | Reference: existing dedup pattern with lock + getLastComment |

### Existing Dedup Patterns to Mirror

**JIRA** (sync-coordinator.ts:1373-1379):
```typescript
const lastComment = await jiraClient.getLastComment(jiraKey);
if (lastComment && lastComment.body === completionComment) {
  this.logger.log(`  ⏭️  Skipping duplicate comment (already posted to ${jiraKey})`);
  return;
}
```

**GitHub progress comments** (format-preservation-sync.ts:170):
```typescript
const lastComment = await client.getLastComment(issueNumber);
if (lastComment && lastComment.body === comment) {
  this.logger.log(`  ⏭️  Skipping duplicate comment (already posted)`);
  return;
}
```
