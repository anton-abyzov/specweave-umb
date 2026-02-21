---
increment: 0313-post-closure-sync-pipeline
type: architecture
---

# Architecture Plan: Fix post-closure sync pipeline

## Overview

The post-closure sync pipeline has a critical architectural problem: the `/sw:done` skill directly edits `metadata.json` to set status to `completed` (Step 8 in SKILL.md), bypassing the `completeIncrement()` function in `status-commands.ts`. This means `LifecycleHookDispatcher.onIncrementDone()` never fires from the skill path, so living docs sync, GitHub issue closure, and GitHub Project sync silently fail.

This plan unifies the completion path, creates the missing `sw:sync-docs` skill, wires the dispatcher, and adds the missing `sync_to_github_project` handler.

## Problem Analysis

### Dual-Path Architecture (Root Cause)

There are currently TWO independent code paths that close an increment:

1. **CLI path** (`specweave complete <id>` -> `completeIncrement()` in `status-commands.ts`):
   - Calls `MetadataManager.updateStatus(incrementId, IncrementStatus.COMPLETED)`
   - Fires `LifecycleHookDispatcher.onIncrementDone()` (fire-and-forget via void async IIFE)
   - Used by auto mode stop hook

2. **Skill path** (`/sw:done` -> LLM directly edits metadata.json):
   - Step 8 says "Update metadata.json status to completed, set completion date"
   - The LLM uses `Edit()` to change the JSON file directly
   - `LifecycleHookDispatcher.onIncrementDone()` NEVER fires
   - Living docs sync, GitHub issue closure, and GitHub Project sync silently fail

### Missing Components

1. **`sw:sync-docs` skill**: Referenced in `/sw:done` Step 10 but does not exist.

2. **`sync_to_github_project` handler**: Declared in `HookConfiguration` type and present in default config, but `LifecycleHookDispatcher.onIncrementDone()` only handles `sync_living_docs` and `close_github_issue`.

## Architecture

### Change 1: Unify completion path via CLI

**File**: `plugins/specweave/skills/done/SKILL.md`

Modify Step 8 to instruct the LLM to run `specweave complete <id> --skip-validation --silent` CLI command instead of directly editing metadata.json. The `--skip-validation` flag is safe here because `/sw:done` already ran Gate 0 + PM validation in Steps 6-7.

### Change 2: Make hook dispatch awaited

**File**: `src/core/increment/status-commands.ts`

Replace the fire-and-forget void IIFE with an awaited call plus error reporting. This ensures hooks complete before CLI exits and the user gets feedback.

### Change 3: Add sync_to_github_project handler

**File**: `src/core/hooks/LifecycleHookDispatcher.ts`

Add handling for the `sync_to_github_project` flag in `onIncrementDone()`. The handler resolves the feature ID from metadata.json or spec.md frontmatter, then invokes the GitHub feature sync via dynamic import. The GitHub plugin may not be installed, so import failure is caught and logged.

### Change 4: Create sw:sync-docs skill

**File**: `plugins/specweave/skills/sync-docs/SKILL.md` (new file)

A skill that wraps `LivingDocsSync.syncIncrement()`. Accepts increment ID, supports "review" mode for dry-run validation.

## File Changes Summary

| File | Change | Risk |
|------|--------|------|
| `plugins/specweave/skills/done/SKILL.md` | Modify Step 8 to use CLI | Low |
| `src/core/increment/status-commands.ts` | Await hooks instead of fire-and-forget | Low |
| `src/core/hooks/LifecycleHookDispatcher.ts` | Add sync_to_github_project handler + feature ID resolver | Medium |
| `plugins/specweave/skills/sync-docs/SKILL.md` | New skill file | Low |
| `tests/unit/core/hooks/lifecycle-hook-dispatcher.test.ts` | Add tests for new handler | Low |

## Architecture Diagram

```
/sw:done (SKILL)
  |
  v
Gate 0 + PM Validation (Steps 6-7)
  |
  v
specweave complete <id> --skip-validation --silent  <-- UNIFIED PATH
  |
  v
completeIncrement()  (status-commands.ts)
  |
  +-- MetadataManager.updateStatus(COMPLETED)
  |
  +-- await LifecycleHookDispatcher.onIncrementDone()  <-- NOW AWAITED
       |
       +-- sync_living_docs --> LivingDocsSync.syncIncrement()
       +-- sync_to_github_project --> resolveFeatureId() + GitHubFeatureSync (NEW)
       +-- close_github_issue --> SyncCoordinator.syncIncrementClosure()
```

## Implementation Phases

### Phase 1: Tests first (TDD RED)
Write failing tests for:
- sync_to_github_project handler dispatch
- Awaited hook dispatch pattern in completeIncrement

### Phase 2: Core changes (TDD GREEN)
- Implement sync_to_github_project handler
- Change fire-and-forget to await
- Update done skill Step 8

### Phase 3: Skill creation
- Create sw:sync-docs SKILL.md

## Technical Challenges

### Challenge 1: GitHub plugin may not be installed
**Solution**: Dynamic import with try/catch. Handler logs warning and continues.

### Challenge 2: Feature ID resolution
**Solution**: Read metadata.json `feature_id` first, fall back to spec.md frontmatter parsing, fall back to FS-{increment-number} convention.

### Challenge 3: TDD mode active
**Solution**: Write tests RED first per TDD protocol, then implement GREEN.
