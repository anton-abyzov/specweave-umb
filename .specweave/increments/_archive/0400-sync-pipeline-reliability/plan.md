# Plan: FS-400 Sync Pipeline Reliability

## Architecture

The sync pipeline has three trigger points that need fixing:

1. **Task completion** → `onTaskCompleted` (currently dead code)
2. **Status transitions** → `StatusChangeSyncTrigger` (missing `active → ready_for_review`)
3. **Increment closure** → `GitHubReconciler` (can't find milestone from split fields)

## Approach

### Phase 1: Wire up task-level sync (US-001)
- Add `onTaskCompleted()` call from `task-ac-sync-guard.sh` or from `MetadataManager` when task status changes
- Most pragmatic: have the shell hook call a new CLI command (e.g., `specweave sync-task`) that invokes `onTaskCompleted()`
- Add `active → ready_for_review` to `SYNC_WORTHY` transitions in `StatusChangeSyncTrigger`

### Phase 2: Unify metadata fields (US-003)
- Modify `GitHubFeatureSync.syncFeatureToGitHub()` to write both `externalLinks.github` and `github` fields
- Same for `syncToGitHub()` in LivingDocsSync
- Add a `normalizeMetadata()` function that copies `github` → `externalLinks.github` if the latter is empty

### Phase 3: Fix milestone lifecycle (US-002)
- `GitHubReconciler.closeCompletedIncrementIssues()` already has milestone-closing code — fix it to check both fields
- Add auto-recovery: if no sync data exists at closure time, run full sync first
- Add duplicate milestone detection before creation

### Phase 4: Surface errors (US-004)
- Replace silent catch-and-swallow in `LifecycleHookDispatcher` with structured error reporting
- Add sync status summary to `/sw:done` output

### Phase 5: Schema validation (US-005)
- Add validation to `MetadataManager.load()` with warnings for non-standard fields
- Map common mistakes (`createdAt` → `created`, `enhancement` → `feature`)

### Phase 6: Stale cleanup (US-006)
- Add `sync-reconcile` subcommand or integrate into `sync-progress --reconcile`
- Scan completed increments, close stale milestones, remove duplicate milestones

## Key Files

| File | Changes |
|------|---------|
| `src/core/hooks/LifecycleHookDispatcher.ts` | Wire `onTaskCompleted`, improve error reporting |
| `src/core/increment/status-change-sync-trigger.ts` | Add `active → ready_for_review` to SYNC_WORTHY |
| `plugins/specweave-github/lib/github-feature-sync.ts` | Write both metadata fields |
| `src/core/living-docs/living-docs-sync.ts` | Write both metadata fields |
| `src/sync/github-reconciler.ts` | Read from both fields, add auto-recovery |
| `src/core/increment/metadata-manager.ts` | Add schema validation, normalizeMetadata() |
| `plugins/specweave/hooks/v2/guards/task-ac-sync-guard.sh` | Trigger task-level sync |
| `src/cli/commands/sync-progress.ts` | Add --reconcile flag |
| `src/core/increment/status-commands.ts` | Add sync summary to /sw:done output |

## Risks

- **Sync spam**: Task-level sync on every edit could be noisy. Mitigated by existing `USSyncThrottle` (60s window).
- **Race condition**: `StatusChangeSyncTrigger` async + `LifecycleHookDispatcher` awaited could double-fire. Existing filesystem lock mitigates.
- **Backward compat**: Writing both fields is additive, not breaking.
