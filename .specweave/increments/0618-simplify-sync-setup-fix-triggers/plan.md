---
increment: 0618-simplify-sync-setup-fix-triggers
---

# Architecture: Simplify sync-setup + fix quadruple triggers

## Approach

**Part A (Triggers)**: Convert 3 of 4 sync triggers from direct sync to event queue. `stop-sync.sh` already has the queue model — make it the single sync owner.

**Part B (Setup)**: Detect single vs multi from `childRepos.length`. Single = 3 questions. Multi = per-repo targets.

## Key Files

| File | Change |
|------|--------|
| `src/core/sync/event-queue.ts` (NEW) | `queueSyncEvent()` utility |
| `src/core/hooks/LifecycleHookDispatcher.ts` | Queue instead of direct sync |
| `src/core/increment/status-change-sync-trigger.ts` | Queue instead of direct sync |
| `hooks/v2/dispatchers/post-tool-use.sh` | Queue to pending.jsonl |
| `src/cli/helpers/issue-tracker/index.ts` | Simplified wizard flow |
| `src/cli/commands/sync-setup.ts` | `--quick` flag |

## Design Decision: sync.mode

`"queued"` (default): All hook-triggered syncs write to queue. `stop-sync.sh` processes at session end.
`"immediate"`: Legacy direct sync behavior for users who need real-time.
Exception: `specweave complete` always does direct sync (explicit user action).
