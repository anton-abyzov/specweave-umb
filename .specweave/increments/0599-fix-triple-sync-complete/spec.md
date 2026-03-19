---
increment: 0599-fix-triple-sync-complete
title: Fix triple-sync bug in specweave complete
type: bug
priority: P1
status: completed
created: 2026-03-19T00:00:00.000Z
structure: user-stories
---

# Bug Fix: Triple-sync in specweave complete

## Overview

`specweave complete` triggers 3 independent sync pipelines that all hit GitHub/JIRA/ADO, exhausting the 5000 req/hr GitHub API rate limit in minutes. The GitHubReconciler's auto-recovery fallback re-runs `LivingDocsSync.syncIncrement()` even though `LifecycleHookDispatcher.onIncrementDone()` already ran it.

## User Stories

### US-001: Deduplicate sync on increment completion (P1)
**Project**: specweave

**As a** SpecWeave user completing an increment
**I want** external tool sync to run exactly once during `specweave complete`
**So that** GitHub API rate limits are not exhausted by redundant calls

**Acceptance Criteria**:
- [x] **AC-US1-01**: `GitHubReconciler.closeCompletedIncrementIssues()` does NOT call `LivingDocsSync.syncIncrement()` when metadata has no GitHub sync data
- [x] **AC-US1-02**: If metadata has GitHub sync data, reconciler still closes issues normally
- [x] **AC-US1-03**: Comment in `status-commands.ts` accurately describes the reconciler's role
- [x] **AC-US1-04**: Existing tests pass after the change
- [x] **AC-US1-05**: `StatusChangeSyncTrigger` records throttle BEFORE sync (not after) to prevent reentrancy
- [x] **AC-US1-06**: `LivingDocsSync.syncIncrement()` has a static reentrancy guard preventing concurrent syncs for the same increment

## Out of Scope

- Adding rate limit tracking or backoff logic
- Increasing the throttle window (5s → 30s) — addressed by reentrancy guard instead
