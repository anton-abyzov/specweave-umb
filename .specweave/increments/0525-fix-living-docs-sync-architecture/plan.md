# Architecture Plan: Fix Living Docs Sync Architecture

## Overview

Bug fix to eliminate zombie background sync processes, remove triple-sync redundancy, and make `specweave complete` resilient to external drift. No new architecture -- simplifying existing over-engineered flow.

## Problem Analysis

### Current Sync Flow (Broken)

```
completeIncrement()
  |
  +-- 1. Pre-completion sync (lines 306-319 in status-commands.ts)
  |      LivingDocsSync.syncIncrement()            <-- SYNC #1
  |
  +-- 2. MetadataManager.updateStatus(COMPLETED)
  |
  +-- 3. LifecycleHookDispatcher.onIncrementDone()
  |      LivingDocsSync.syncIncrement()            <-- SYNC #2
  |
  +-- 4. GitHubReconciler.closeCompletedIncrementIssues()
  |
  +-- PostToolUse hook (close-completed-issues.sh)
         specweave sync-living-docs & disown        <-- SYNC #3 (ZOMBIE)
```

Three syncs per completion. The hook's `& disown` creates zombie processes with no timeout, no PID tracking, and leaked lock files.

### External Drift Blocker

`completion-validator.ts` lines 153-156: drift > 168 hours pushes an error, making `isValid = false`, which causes `completeIncrement()` to return false (line 293-294). This blocks completion for a non-fatal condition.

## Design Decisions

### DD-1: Remove Pre-Completion Sync from completeIncrement()

**File**: `status-commands.ts` lines 306-319

Remove the entire pre-completion sync block. The `onIncrementDone()` hook already performs living docs sync (step 1 in `LifecycleHookDispatcher.onIncrementDone`). The pre-sync was added as a "catch up" mechanism but creates redundancy.

**Rationale**: `onIncrementDone()` is the designated single sync point per ADR-0185. The pre-sync creates a race condition where stale data from sync #1 can conflict with sync #2.

### DD-2: Convert Drift >168h from Error to Warning

**File**: `completion-validator.ts` lines 142-177

Change the drift > 168 hours block (lines 153-162) from `errors.push(...)` to `warnings.push(...)`. External drift is informational -- it should never block completion.

**Before**:
```
if (hoursSince > 168) {
  errors.push(...)  // BLOCKS completion
}
```

**After**:
```
if (hoursSince > 168) {
  warnings.push(...)  // WARNS but allows completion
}
```

**Rationale**: External tool staleness is not a quality problem with the increment itself. Blocking completion forces users to sync manually before closing, which creates the frustration loop that led to the `& disown` workaround.

### DD-3: Wire autoSyncOnCompletion into onIncrementDone

**File**: `LifecycleHookDispatcher.ts`, `onIncrementDone()` method

The `autoSyncOnCompletion` flag exists in `config.sync.settings` (see `src/sync/config.ts` line 27) and is already checked by `SyncCoordinator` (line 443, 596). But `LifecycleHookDispatcher.onIncrementDone()` does NOT check it -- it only checks `doneConfig.sync_living_docs` from hooks config.

Add a config check at the top of `onIncrementDone()`:

```typescript
// Check global autoSyncOnCompletion flag
const config = await configManager.read();
const autoSync = config.sync?.settings?.autoSyncOnCompletion ?? true;
if (!autoSync) {
  // Skip all sync, return empty result
  return result;
}
```

This provides the global opt-out mechanism (AC-US3-01).

### DD-4: Add skipLivingDocsSync to IncrementMetadata

**File**: `increment-metadata.ts`, `IncrementMetadataV2` interface

Add optional field:

```typescript
/** Skip living docs sync for this increment (v1.0.xxx+) */
skipLivingDocsSync?: boolean;
```

Then in `onIncrementDone()`, after the global check, add per-increment check:

```typescript
// Check per-increment skip flag
const metadata = MetadataManager.read(incrementId);
if (metadata.skipLivingDocsSync === true) {
  return result;
}
```

### DD-5: Remove Background Sync from Hook

**File**: `.claude/hooks/close-completed-issues.sh`

Remove Section 2 entirely (lines 48-73). The `& disown` pattern is the root cause of zombie processes. With DD-1 removing pre-sync and keeping `onIncrementDone()` as the sole sync point, the hook no longer needs to trigger sync at all.

Keep Section 1 (GitHub issue closure via `gh` CLI) but fix it to source GITHUB_TOKEN from `.env`:

```bash
# Source GITHUB_TOKEN from .env if available
if [[ -f "$PROJECT_ROOT/.env" ]]; then
  GITHUB_TOKEN=$(grep -E '^GITHUB_TOKEN=' "$PROJECT_ROOT/.env" | cut -d= -f2- | tr -d '"'"'")
  [[ -n "$GITHUB_TOKEN" ]] && export GH_TOKEN="$GITHUB_TOKEN"
fi
```

### DD-6: Stale Lock File Cleanup

**File**: `.claude/hooks/close-completed-issues.sh`

Add at hook entry (before Section 1):

```bash
# Clean stale sync lock files (>60 min old)
find "$PROJECT_ROOT/.specweave/state/" -name "sync-*.lock" -mmin +60 -delete 2>/dev/null
```

This handles leaked lock files from killed zombie processes.

### DD-7: Stderr Logging for Silent Mode Failures

**File**: `status-commands.ts`, `completeIncrement()` function

The `log()` helper suppresses output when `silent = true`. But transition failures (lines 274-275) should always write to stderr for diagnostics:

```typescript
// Change from:
log(chalk.red(`...`));
// To:
if (silent) process.stderr.write(`[completeIncrement] Transition failure: ...\n`);
else log(chalk.red(`...`));
```

## Component Boundaries

```
specweave CLI (repositories/anton-abyzov/specweave/)
  |
  +-- src/core/increment/status-commands.ts
  |     completeIncrement(): Remove pre-sync (DD-1), stderr logging (DD-7)
  |
  +-- src/core/increment/completion-validator.ts
  |     validateCompletion(): Drift warning instead of error (DD-2)
  |
  +-- src/core/hooks/LifecycleHookDispatcher.ts
  |     onIncrementDone(): Wire autoSyncOnCompletion + skipLivingDocsSync (DD-3, DD-4)
  |
  +-- src/core/types/increment-metadata.ts
        IncrementMetadataV2: Add skipLivingDocsSync field (DD-4)

specweave-umb (umbrella repo)
  |
  +-- .claude/hooks/close-completed-issues.sh
        Remove Section 2, fix .env sourcing, add lock cleanup (DD-5, DD-6)
```

## Data Flow (After Fix)

```
completeIncrement()
  |
  +-- 1. Quality gate validation (drift is WARNING only)
  |
  +-- 2. MetadataManager.updateStatus(COMPLETED)
  |
  +-- 3. LifecycleHookDispatcher.onIncrementDone()
  |      Check autoSyncOnCompletion (global skip?)
  |      Check skipLivingDocsSync (per-increment skip?)
  |      LivingDocsSync.syncIncrement()            <-- SINGLE SYNC
  |      SyncCoordinator.syncIncrementClosure()
  |      drainRetryQueue()
  |
  +-- 4. GitHubReconciler.closeCompletedIncrementIssues()
  |
  +-- PostToolUse hook
         Clean stale locks
         Close GitHub issues via gh CLI (with GH_TOKEN from .env)
         NO background sync
```

## Risk Mitigation

| Risk | Mitigation |
|------|-----------|
| Removing pre-sync misses increments created without planning sync | `onIncrementDone()` already handles this case -- it syncs living docs regardless of prior state |
| Per-increment skip flag not read by other sync paths | Only `onIncrementDone()` needs to check it -- task-level sync and planning-time sync are separate concerns (out of scope) |
| Hook .env sourcing fails on non-standard layouts | Graceful fallback -- if `.env` missing or no GITHUB_TOKEN, gh CLI falls back to its own auth |

## Testing Strategy

- Unit tests for `completion-validator.ts` drift warning behavior
- Unit tests for `LifecycleHookDispatcher.onIncrementDone()` skip logic (both flags)
- Integration test verifying single sync call per completion
- Shell script validation for hook changes (no `&` or `disown` in sync paths)

## No ADR Needed

This is a simplification of existing architecture, not a new architectural decision. The changes align with ADR-0185 (Unified Living Docs Sync Architecture) which already designates `onIncrementDone()` as the primary sync trigger. We are removing deviations from that ADR, not creating new patterns.

## Domain Skill Delegation

No domain skills needed. This is a targeted bug fix across TypeScript (specweave CLI) and shell (hook script). The changes are surgical edits to existing files, not new component development. Proceed directly to task planning.
