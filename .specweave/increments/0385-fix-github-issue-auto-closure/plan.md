# Plan: Fix GitHub Issue Auto-Closure

## Architecture
Add direct metadata-based fallback to `completeIncrement()` that bypasses the broken LivingDocsSync chain.

## Changes
1. `github-reconciler.ts`: Add `closeCompletedIncrementIssues()` static method
2. `status-commands.ts`: Wire fallback call after LifecycleHookDispatcher
3. Tests: New test file for the closure method
