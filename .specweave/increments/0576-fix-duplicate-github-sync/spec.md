---
increment: 0576-fix-duplicate-github-sync
title: Fix duplicate GitHub sync during specweave complete
type: bug
priority: P1
status: completed
created: 2026-03-18T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Fix duplicate GitHub sync during specweave complete

## Overview

During `specweave complete`, GitHub sync executes twice per completion. `LifecycleHookDispatcher.onIncrementDone()` Step 1 calls `LivingDocsSync.syncIncrement()` which chains through `syncToExternalTools()` → `syncToGitHub()` → `syncFeatureToGitHub()`. Then Step 2 calls `syncFeatureToGitHub()` again directly via `syncGitHubProject()`. This wastes ~22 GitHub API calls per completion and pushes users toward GitHub's 5000 requests/hour rate limit. Fix: remove the redundant `syncGitHubProject()` from Step 2.

## User Stories

### US-001: Eliminate redundant GitHub API calls during completion (P1)
**Project**: specweave

**As a** SpecWeave user with GitHub sync enabled,
**I want** increment completion to sync to GitHub exactly once,
**So that** I don't waste API calls and risk hitting GitHub's rate limit.

**Acceptance Criteria**:
- [x] **AC-US1-01**: `onIncrementDone()` does NOT call `syncFeatureToGitHub()` directly — GitHub sync only happens through the `LivingDocsSync` chain
- [x] **AC-US1-02**: The `syncGitHubProject` function and its `Promise.all` entry are removed from `LifecycleHookDispatcher.onIncrementDone()`
- [x] **AC-US1-03**: The `shouldSyncGitHubProject` flag is removed since it is no longer referenced
- [x] **AC-US1-04**: Step 2 comment is updated to reflect that only closure sync runs (not "direct GitHub sync in parallel")
- [x] **AC-US1-05**: Unit test verifies that `syncFeatureToGitHub` is called exactly once when both living docs sync and GitHub project sync are enabled
- [x] **AC-US1-06**: Existing closure sync via `SyncCoordinator` (JIRA/ADO) continues to work unchanged

## Functional Requirements

### FR-001: Remove redundant syncGitHubProject from onIncrementDone
Remove the `syncGitHubProject()` async function (lines 266-283), its `shouldSyncGitHubProject` flag (line 219), and its entry in the `Promise.all` call (line 305). Simplify `Promise.all([syncClosure()])` to `await syncClosure()` since only one function remains.

### FR-002: Update Step 2 comment
Update the comment at line 265 from "run closure and direct GitHub sync in parallel" to reflect that only closure sync runs at this stage.

## Success Criteria

- GitHub API calls per completion reduced by ~50% (from ~22 to ~11)
- No regression in JIRA/ADO closure sync behavior
- No regression in living docs sync or its GitHub sync chain

## Out of Scope

- Refactoring the sync lock mechanism in `GitHubFeatureSync`
- Reducing API calls within a single sync cycle
- Changes to `LivingDocsSync` internals

## Dependencies

- `LivingDocsSync.syncIncrement()` must continue chaining to `syncToExternalTools()` → `syncToGitHub()`

## Technical Notes

- **File**: `src/core/hooks/LifecycleHookDispatcher.ts`
- **Test file**: `tests/unit/core/hooks/lifecycle-hook-dispatcher.test.ts`
- The `syncClosure()` function (JIRA/ADO) must remain — only `syncGitHubProject()` is removed
