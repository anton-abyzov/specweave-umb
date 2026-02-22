# Architecture Plan: Auto-Close External Issues on status:complete Sync

## Overview

GitHub issues (and JIRA/ADO equivalents) get `status:complete` labels applied by progress-sync but remain in OPEN state. The label sync and issue closure are decoupled -- labels are managed by `updateStatusLabels()` while closure only happens in `updateUserStoryIssue()` or during increment closure via `syncIncrementClosure()`. This fix makes closure happen at the point where `status:complete` is determined.

## Architecture

### Current Flow (Bug)

```
Feature Sync Path:
  updateUserStoryIssue()  -> closes issue if overallComplete ---------> WORKS
  updateStatusLabels()    -> applies status:complete label            -> DOES NOT CLOSE

Progress-Sync CLI Path:
  syncACCheckboxesToGitHub() -> updates checkboxes only              -> DOES NOT CLOSE
  (never invokes ac-progress-sync providers for JIRA/ADO)            -> JIRA/ADO NOT TRANSITIONED

Result: Issues get status:complete label but remain OPEN
```

### Fixed Flow

```
Feature Sync Path:
  updateUserStoryIssue()  -> closes issue if overallComplete ---------> WORKS (unchanged)
  updateStatusLabels()    -> applies status:complete label + CLOSES  -> FIXED (additive)

Progress-Sync CLI Path:
  syncACCheckboxesToGitHub() -> updates checkboxes                   -> unchanged
  syncACProgressToProviders() -> closes GitHub + transitions JIRA/ADO -> FIXED (new call)

Result: Issues with status:complete are also CLOSED
```

## Changes

### Change 1: `updateStatusLabels()` -- Add issue close after label

**File**: `plugins/specweave-github/lib/github-feature-sync.ts`

The `updateStatusLabels()` method (lines 965-1058) already has `issueData` fetched at line 978 and knows the `completion.overallComplete` state. After applying `status:complete` label, add:

```typescript
// After Step 2 (adding status:complete label), close the issue if still OPEN
if (newStatusLabel === 'status:complete' && issueData.state.toLowerCase() !== 'closed') {
  const completionComment = this.calculator.buildCompletionComment(completion);
  await execFileNoThrow('gh', [
    'issue', 'close',
    issueNumber.toString(),
    '--comment', completionComment,
  ], { env: this.getGhEnv() });
  console.log(`      closed issue #${issueNumber} (status:complete)`);
}
```

**Key considerations**:
- `issueData` is already fetched -- no extra API call needed
- `completion` is already passed as a parameter -- reuse it for the comment
- The `calculator.buildCompletionComment()` is the same format used by `updateUserStoryIssue()` -- consistent UX
- If `updateUserStoryIssue()` already closed the issue, `issueData.state` will be 'closed' and this is a no-op
- Need to expand the `completion` parameter type to include fields needed by `buildCompletionComment()`

### Change 2: Progress-Sync CLI -- Wire in `syncACProgressToProviders()`

**File**: `src/cli/commands/sync-progress.ts`

In Step 5/5 (lines 206-245), after `syncCoordinator.syncACCheckboxesToGitHub()`, add a call to `syncACProgressToProviders()` from `ac-progress-sync.ts`. This function already handles:
- **GitHub**: Posts AC progress comments + auto-closes complete user stories via `autoCloseCompletedUserStories()`
- **JIRA**: Posts comments + transitions to Done via `JiraStatusSync.updateStatus()`
- **ADO**: Posts comments + transitions to Closed via `AdoStatusSync.updateStatus()`

The `syncACProgressToProviders()` needs:
- `incrementId` -- already available
- `affectedUSIds` -- parse from spec.md using `parseAllUserStoryIds()` (already exported)
- `specPath` -- derivable from increment path
- `config` -- build from config.json sync settings and metadata.json external links

### Change 3: Tests

**File**: New test `tests/unit/plugins/github/github-feature-sync-auto-close.test.ts`

Test that `updateStatusLabels()`:
1. Closes OPEN issue when `overallComplete=true`
2. Skips close on already CLOSED issue
3. Does not close when `overallComplete=false` (status:active)
4. Posts completion comment before closing

**File**: Extend `tests/unit/core/ac-progress-sync.test.ts`

Verify JIRA/ADO transitions fire during `syncACProgressToProviders()` when all ACs complete.

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Double-close (feature sync + label sync) | Low | Negligible | Both paths check `state !== 'closed'` before closing |
| Duplicate comments | Low | Low | `updateUserStoryIssue()` runs first, `updateStatusLabels()` checks state |
| gh CLI failure on close | Low | Medium | Non-blocking: wrapped in try/catch, logged as warning |
| JIRA/ADO transition failure | Low | Medium | Non-blocking: `syncACProgressToProviders()` isolates errors per provider |

## Files to Modify

1. `plugins/specweave-github/lib/github-feature-sync.ts` -- `updateStatusLabels()` method (~15 lines added)
2. `src/cli/commands/sync-progress.ts` -- Add `syncACProgressToProviders()` call (~30 lines added)
3. `tests/unit/plugins/github/github-feature-sync-auto-close.test.ts` -- New test file
4. `tests/unit/core/ac-progress-sync.test.ts` -- Extend existing tests

## Testing Strategy

- **TDD**: Write failing tests first, then implement the fix
- **Unit tests**: Mock `gh` CLI calls and `getIssue()` to verify close behavior
- **Integration tests**: Existing `tests/integration/external-tools/github/` cover the feature-sync flow; extend to verify label+close atomicity
