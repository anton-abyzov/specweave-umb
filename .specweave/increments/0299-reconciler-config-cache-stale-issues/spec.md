# 0299: Reconciler Double-LoadConfig Fix + Stale Issue Closure

## Overview

Fix the GitHubReconciler's double `loadConfig()` bug (issue #1223, already fixed on develop at fd61f51c), add config caching to the reconciler to prevent race conditions, and close the 13 GitHub issues that are marked `status:complete` in SpecWeave but remain open on GitHub (a direct symptom of the reconciler bug).

## Background

The `GitHubReconciler.reconcile()` method previously called `loadConfig()` twice in sequence: once to check permissions (line 85), and again inside `initClient()` (which had its own `loadConfig()` call). In test scenarios, the second `readFile` call consumed mock data meant for metadata, causing all reconciliation operations (close/reopen) to silently fail. In production, this caused unnecessary disk I/O and potential race conditions if config changed between reads.

The immediate fix (commit fd61f51c) passes the already-loaded config to `initClient(config)`. However, the loadConfig pattern across the sync pipeline still lacks caching -- each call re-reads from disk. This increment adds a simple per-instance config cache and closes the stale issues that accumulated while the reconciler was broken.

## User Stories

### US-001: Config Caching for GitHubReconciler
**Project**: specweave

**As a** SpecWeave user
**I want** the reconciler to cache its config after the first load
**So that** multiple calls within the same reconciliation cycle don't re-read from disk, preventing race conditions and improving performance

**Acceptance Criteria**:
- [ ] **AC-US1-01**: `GitHubReconciler.loadConfig()` caches the parsed config on first call and returns the cached value on subsequent calls
- [ ] **AC-US1-02**: The existing `reconcile()` flow passes config to `initClient()` (fd61f51c fix verified in place)
- [ ] **AC-US1-03**: All 59 existing github-reconciler tests pass
- [ ] **AC-US1-04**: New test confirms `loadConfig()` only reads from disk once even when called multiple times

### US-002: Close Stale GitHub Issues
**Project**: specweave

**As a** SpecWeave maintainer
**I want** the 13 stale open GitHub issues with `status:complete` label to be closed
**So that** the GitHub issue tracker accurately reflects the current state of completed increments

**Acceptance Criteria**:
- [ ] **AC-US2-01**: All open issues with `status:complete` label are closed with a reconciliation comment
- [ ] **AC-US2-02**: Bug issue #1223 is closed with a reference to the fix commit fd61f51c
- [ ] **AC-US2-03**: No issues that should remain open are accidentally closed

### US-003: Verify Double-LoadConfig Fix
**Project**: specweave

**As a** developer
**I want** the fd61f51c fix to be verified with a specific regression test
**So that** the double-loadConfig bug cannot reoccur without test failure

**Acceptance Criteria**:
- [ ] **AC-US3-01**: A dedicated regression test verifies that `reconcile()` calls `loadConfig()` exactly once (not twice)
- [ ] **AC-US3-02**: The test documents the bug scenario (mock data consumed by extra config read leaving stale data for metadata)
