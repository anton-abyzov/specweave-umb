# Plan: 0299 Reconciler Config Cache + Stale Issue Closure

## Architecture

### Config Caching Strategy

The simplest approach: add a `private configCache: any | null = null` field to `GitHubReconciler`. The `loadConfig()` method checks the cache first, reads from disk only if null, then stores the result.

**File**: `repositories/anton-abyzov/specweave/src/sync/github-reconciler.ts`

Changes:
1. Add `private configCache: any | null = null` field
2. Modify `loadConfig()` to check/populate cache
3. The existing fd61f51c fix (passing config to initClient) remains as-is

This is a minimal, low-risk change. The reconciler is short-lived (created per reconcile cycle), so the cache lifetime is naturally scoped to a single operation.

### Regression Test

**File**: `repositories/anton-abyzov/specweave/tests/unit/sync/github-reconciler.test.ts`

Add a test that:
1. Spies on `mockReadFile` call count for config.json path
2. Runs `reconcile()`
3. Asserts config.json was read exactly once

### Stale Issue Closure

Use `gh` CLI to close the 13 open issues with `status:complete` label plus issue #1223, with appropriate reconciliation comments.

**Issues to close**:
- FS-278: #1212, #1213, #1214 (3 issues)
- FS-271: #1199, #1200, #1201 (3 issues)
- FS-219: #1194, #1195, #1196, #1197, #1198 (5 issues)
- FS-265: #1192, #1193 (2 issues)
- Bug: #1223 (1 issue)

Total: 14 issues

## Risks

- **Low**: Config caching is scoped to the reconciler instance lifetime (one reconcile cycle)
- **Low**: Closing issues is idempotent; already-closed issues are no-ops
- **None**: The fd61f51c fix is already on develop and all 59 tests pass

## Dependencies

None -- the fix is already in place, this increment adds caching + cleanup.
