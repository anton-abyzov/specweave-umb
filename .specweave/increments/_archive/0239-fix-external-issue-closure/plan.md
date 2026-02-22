# Plan: Fix External Issue Closure

## Root Cause

3 chained bugs prevent GitHub issue closure on `/sw:done`:

1. **Wrong method**: `status-change-sync-trigger.ts:273` calls `syncIncrementCompletion()` (no-op for closure) instead of `syncIncrementClosure()` (actually closes issues)
2. **setTimeout fire-and-forget**: The sync runs in `setTimeout(..., 0)` — process may exit before callback fires
3. **DONE skill closes ONE issue**: Step 9C only targets `metadata.github.issue` (single number), not all per-US issues

## Changes

### Change 1: Fix method call (status-change-sync-trigger.ts)
- Line 273: `syncIncrementCompletion()` → `syncIncrementClosure()`
- Line 275-278: Update result handling to use `closedIssues` from closure result

### Change 2: Make completion sync blocking (status-change-sync-trigger.ts)
- Lines 185-219: For COMPLETED transitions, await sync directly instead of setTimeout

### Change 3: Update DONE skill (done/SKILL.md)
- Step 9C: Close ALL per-US issues via search pattern, report results

### Change 4: Close orphaned issues
- Use `gh issue close` for all 20 orphaned issues
