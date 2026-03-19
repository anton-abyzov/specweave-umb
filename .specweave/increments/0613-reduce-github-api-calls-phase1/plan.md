---
increment: 0613-reduce-github-api-calls-phase1
type: architecture
---

# Architecture Plan: Reduce GitHub API Calls (Phase 1)

## Approach

Six surgical fixes to the existing sync-progress pipeline. No new architecture -- pure optimization of the current call flow.

## Current Flow (per US)

```
sync-progress command
  Step 5: GitHubACCheckboxSync         -> getIssue + updateBody + addComment  (3 calls)
  Step 6a: postACProgressComments      -> fetchLastComment + postComment + fetchBody + patchBody (4 calls)  <- DUPLICATE
  Step 6b: autoCloseCompletedUserStories -> viewState + comment + close + labelCheck + labelEdit (5 calls)
```

## Optimized Flow (per US)

```
sync-progress command
  Step 5: GitHubACCheckboxSync         -> getIssue + updateBody + addComment  (3 calls, comment only if changes)
  Step 6a: SKIPPED for GitHub          -> 0 calls (skipGitHubComments=true)
  Step 6b: autoClose (optimized)       -> close+label combined (2-3 calls, skip known-closed)
```

## Changes by File

### 1. src/cli/commands/sync-progress.ts
- After Step 5 succeeds, pass `skipGitHubComments: true` to syncACProgressToProviders

### 2. src/core/ac-progress-sync.ts
- Add `skipGitHubComments?: boolean` to the options
- In syncGitHubACProgress: when skipGitHubComments=true, skip postACProgressComments entirely, only run autoCloseCompletedUserStories

### 3. plugins/specweave/lib/integrations/github/github-us-auto-closer.ts
- Hoist ensureLabelExists before the per-US loop
- Add module-level label cache (Set keyed by repo+label)
- Combine `gh issue close` + `gh issue edit --add-label` into single `gh api` PATCH
- Check metadata.json stored status before gh issue view

### 4. plugins/specweave/lib/integrations/github/github-ac-checkbox-sync.ts
- Skip addComment when body === originalBody (no checkbox changes)

## Risk Assessment

- **Low risk**: All fixes are additive guards/skips. Fallback to existing behavior on failure.
- **No breaking changes**: Same API surface, same outcomes, fewer calls.
