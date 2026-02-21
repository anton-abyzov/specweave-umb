# Implementation Plan: Hook Lifecycle Wiring

## Overview

Create a `LifecycleHookDispatcher` that reads `config.json` hooks configuration and dispatches configured actions at lifecycle event points. Wire it into three existing callsites: increment creation, task completion, and increment completion.

## Architecture

### Current State (Problem)

```
config.json hooks: { post_increment_planning, post_task_completion, post_increment_done }
                       ^                           ^                        ^
                       |                           |                        |
                   NEVER READ                  NEVER READ                NEVER READ

createIncrementTemplates() --> no hook dispatch
completeIncrement() --> inline StatusChangeSyncTrigger (ignores hooks config)
task completion --> no hook dispatch
```

### Target State

```
config.json hooks: { post_increment_planning, post_task_completion, post_increment_done }
                       ^                           ^                        ^
                       |                           |                        |
              LifecycleHookDispatcher    LifecycleHookDispatcher    LifecycleHookDispatcher
              .onIncrementPlanned()      .onTaskCompleted()         .onIncrementDone()
                       ^                           ^                        ^
                       |                           |                        |
              createIncrementCommand()    (exposed entry point)     completeIncrement()
```

### Key Design Decision: No Duplication with StatusChangeSyncTrigger

`StatusChangeSyncTrigger` already handles:
- Auto-create issues on status change to ACTIVE
- Auto-close issues on status change to COMPLETED
- Living docs sync on status changes

The `LifecycleHookDispatcher` will:
- Handle `post_increment_planning` (NEW - not covered by StatusChangeSyncTrigger at all)
- Handle `post_task_completion` (NEW - not covered)
- Handle `post_increment_done` (COORDINATE with StatusChangeSyncTrigger to avoid double-sync)

For `post_increment_done`: `completeIncrement()` already calls `MetadataManager.updateStatus(COMPLETED)` which triggers `StatusChangeSyncTrigger`. The dispatcher will only handle `update_living_docs_first` ordering and any actions NOT already covered by the status change trigger.

### Components

1. **LifecycleHookDispatcher** (`src/core/hooks/LifecycleHookDispatcher.ts`)
   - Static class with three dispatch methods
   - Reads config via ConfigManager
   - Non-blocking, error-isolated

2. **Wiring in createIncrementCommand** (`src/cli/commands/create-increment.ts`)
   - Call `onIncrementPlanned()` after successful template creation

3. **Wiring in completeIncrement** (`src/core/increment/status-commands.ts`)
   - Call `onIncrementDone()` after status update succeeds

## Technology Stack

- **Language/Framework**: TypeScript, Node.js ESM
- **Testing**: Vitest with vi.hoisted() + vi.mock()
- **Dependencies**: ConfigManager, autoCreateExternalIssue, LivingDocsSync, SyncCoordinator (all existing)

## Implementation Phases

### Phase 1: LifecycleHookDispatcher
- Create the dispatcher with all three methods
- Unit tests with mocked config and services
- Test config edge cases (missing, partial, disabled)

### Phase 2: Wiring
- Wire into createIncrementCommand
- Wire into completeIncrement
- Expose onTaskCompleted as importable entry point

### Phase 3: Integration Verification
- Verify no duplicate syncs with StatusChangeSyncTrigger
- Verify backward compatibility when hooks config is absent
- Run existing test suite to confirm no regressions

## Testing Strategy

- Unit tests for LifecycleHookDispatcher (mock ConfigManager, mock sync services)
- Test each hook trigger independently
- Test config edge cases: missing hooks, partial config, all disabled, all enabled
- Test error isolation: sync failure doesn't propagate
- Existing tests must pass unchanged

## Technical Challenges

### Challenge 1: Avoiding duplicate sync on completion
**Solution**: The dispatcher checks what StatusChangeSyncTrigger already handles and only dispatches additional actions (like `update_living_docs_first` ordering). The key distinction: StatusChangeSyncTrigger fires on ANY status change to COMPLETED (including via updateStatus), while the dispatcher fires specifically from the `completeIncrement()` code path where hooks config should be respected.

### Challenge 2: Non-blocking dispatch in synchronous callers
**Solution**: Use the same pattern as MetadataManager.updateStatus -- fire-and-forget async IIFE with error catching. This ensures the calling code returns immediately.
