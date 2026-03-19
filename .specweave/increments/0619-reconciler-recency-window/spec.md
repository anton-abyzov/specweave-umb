---
increment: 0619-reconciler-recency-window
title: 'GitHub reconciler: bulk fetch + recency window'
type: feature
priority: P1
status: completed
created: 2026-03-19T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: GitHub Reconciler Recency Window Optimization

## Overview

Replace per-issue `getIssue()` API calls with a single bulk search query, cap milestone fetching, and add a `--full` flag for deep reconciliation. Reduces API calls from ~70 to ~3 per typical run.

## User Stories

### US-001: Bulk Issue State Fetch (P1)
**Project**: specweave

**As a** SpecWeave user with many GitHub-synced increments
**I want** the reconciler to fetch all issue states in a single bulk query
**So that** it doesn't exhaust my GitHub rate limit with per-issue API calls

**Acceptance Criteria**:
- [x] **AC-US1-01**: `bulkFetchIssueStates()` method added to GitHubClientV2 that returns `Map<number, 'open' | 'closed'>` from a single `gh search issues` call
- [x] **AC-US1-02**: `reconcileIssue()` reads issue state from pre-fetched map instead of calling `getIssue()` per issue
- [x] **AC-US1-03**: If an issue is not found in the bulk map (edge case), falls back to individual `getIssue()` call
- [x] **AC-US1-04**: Bulk search is limited to 100 issues by default (configurable via `--full` for no limit)

### US-002: Milestone Reconciliation Cap (P1)
**Project**: specweave

**As a** SpecWeave user
**I want** milestone reconciliation capped at 20 most-recently-updated milestones
**So that** it doesn't paginate through hundreds of old milestones

**Acceptance Criteria**:
- [x] **AC-US2-01**: Milestone fetch uses `per_page=20&sort=updated&direction=desc` instead of `--paginate`
- [x] **AC-US2-02**: `--full` flag restores `--paginate` behavior for deep reconciliation

### US-003: Full Reconciliation Flag (P2)
**Project**: specweave

**As a** SpecWeave user doing periodic deep maintenance
**I want** a `--full` flag on `github-reconcile` that removes all caps
**So that** I can do a thorough quarterly reconciliation

**Acceptance Criteria**:
- [x] **AC-US3-01**: `full` option added to `ReconcileOptions` interface
- [x] **AC-US3-02**: CLI `github-reconcile --full` passes `full: true` to reconciler
- [x] **AC-US3-03**: When `full: true`, bulk search has no limit and milestones use `--paginate`

## Out of Scope

- Local state diff cache (future increment)
- GraphQL batch queries (future increment)
- ETag/conditional request support

## Dependencies

- Existing `GitHubClientV2` class and `listIssuesInTimeRange()` pattern
- Existing `gh` CLI authentication
