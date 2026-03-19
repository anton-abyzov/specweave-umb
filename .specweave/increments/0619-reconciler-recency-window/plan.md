# Implementation Plan: GitHub Reconciler Recency Window

## Overview

Replace per-issue API calls with bulk search, cap milestones, add --full flag. 3 files modified.

## Architecture

1. Add `bulkFetchIssueStates()` to `GitHubClientV2` — single `gh search issues` call
2. In `reconcile()`: call bulk fetch once, pass map to `reconcileIssue()`
3. `reconcileIssue()` reads from map; fallback to `getIssue()` if not found
4. Milestone fetch: replace `--paginate` with `per_page=20&sort=updated&direction=desc`
5. `--full` flag: no search limit, paginate milestones

## Files to Modify

1. `plugins/specweave/lib/integrations/github/github-client-v2.ts` — add `bulkFetchIssueStates()`
2. `src/sync/github-reconciler.ts` — pre-fetch, map lookup, milestone cap, --full
3. CLI command file for github-reconcile — wire --full flag
