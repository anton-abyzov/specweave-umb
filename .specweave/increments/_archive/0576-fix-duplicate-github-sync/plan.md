# Implementation Plan: Fix duplicate GitHub sync during specweave complete

## Overview

Remove the redundant `syncGitHubProject()` call (STEP 2) from `LifecycleHookDispatcher.onIncrementDone()`. The `LivingDocsSync.syncIncrement()` call in STEP 1 already chains to GitHub via `syncToExternalTools()` -> `syncToGitHub()` -> `GitHubFeatureSync`. The direct `syncGitHubProject()` in STEP 2 duplicates this, causing double API calls per completion.

## Root Cause

In `LifecycleHookDispatcher.onIncrementDone()` (`src/core/hooks/LifecycleHookDispatcher.ts`):

- **STEP 1** (lines 231-263): `LivingDocsSync.syncIncrement()` syncs living docs AND chains to GitHub via `syncToExternalTools()` -> `syncToGitHub()`.
- **STEP 2** (lines 265-283): `syncGitHubProject()` calls `syncFeatureToGitHub()` directly -- the same endpoint STEP 1 already reached.

The `sync_to_github_project` config flag and the `syncGitHubProject` async function are dead code paths now that STEP 1 handles GitHub sync.

## Fix

1. **Remove** the `syncGitHubProject` async function (lines 266-283) from `onIncrementDone()`.
2. **Remove** the `shouldSyncGitHubProject` flag (line 219) -- no longer used.
3. **Remove** `syncGitHubProject()` from the `Promise.all` on line 305 -- only `syncClosure()` remains (can be called directly instead of `Promise.all`).
4. **Update** the STEP 2 comment to reflect that only JIRA/ADO closure runs here.
5. **Update tests**: Remove TC-017 (sync_to_github_project=true dispatches), TC-018 (sync_to_github_project=false skips), TC-020 (feature ID resolution). Update TC-019 to no longer reference GitHub project sync failure. Remove `mockSyncFeatureToGitHub` and `mockResolveFeatureId` from test mocks if no longer used.

## Files Changed

| File | Change |
|------|--------|
| `src/core/hooks/LifecycleHookDispatcher.ts` | Remove `syncGitHubProject` function, `shouldSyncGitHubProject` flag, update `Promise.all` |
| `tests/unit/core/hooks/lifecycle-hook-dispatcher.test.ts` | Remove tests for `sync_to_github_project`, clean up unused mocks |

## No ADR Needed

This is a straightforward removal of a duplicate code path. No architectural decisions are being made -- we are consolidating to the existing single sync path via `LivingDocsSync`.

## Testing Strategy

- Existing tests for STEP 1 (`sync_living_docs=true`) already cover the GitHub sync path via LivingDocsSync.
- Verify removed tests (TC-017, TC-018, TC-020) are no longer needed since the code path is gone.
- Run full test suite to confirm no regressions.
