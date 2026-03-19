---
increment: 0599-fix-triple-sync-complete
---

# Architecture Plan

## Approach

Minimal fix: Replace the redundant `LivingDocsSync.syncIncrement()` call in `GitHubReconciler.closeCompletedIncrementIssues()` with an early return. The lifecycle hook already handles the full sync before the reconciler runs.

## Key Decision

Early return vs. removing the entire block: Early return is safer — if the lifecycle hook fails and metadata has no GitHub data, the reconciler silently returns instead of attempting a redundant sync that would also likely fail. Users can run `/sw:progress-sync` manually to recover.
