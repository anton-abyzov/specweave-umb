---
increment: 0621-reduce-github-api-calls-phase2
title: Reduce GitHub API calls in sync-living-docs
type: feature
priority: P1
status: completed
created: 2026-03-19T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Reduce GitHub API Calls — Cross-Process Rate Limit Coordination

## Overview

Multiple processes (reconciler, sync-progress, status-change triggers, dashboard "Sync Now") share the same GitHub token with NO cross-process coordination, causing 4000+ API calls in minutes. Fix by adding a shared rate-limit state file, global reconciler lock, persistent label cache, and skip redundant API calls for already-linked issues.

Brainstorm source: 3-agent analysis confirmed dashboard server itself makes 0 GitHub calls — the triggered sync commands are the problem. 8 prior increments fixed symptoms; this fixes the root cause (cross-process coordination).

## User Stories

### US-001: Shared Rate-Limit State File (P1)
**Project**: specweave

**As a** SpecWeave user running multiple Claude sessions
**I want** all processes to share a rate-limit budget via a state file
**So that** concurrent sessions don't independently exhaust the GitHub rate limit

**Acceptance Criteria**:
- [x] **AC-US1-01**: New module `src/sync/github-rate-limit-budget.ts` reads/writes `.specweave/state/github-rate-limit.json` with `{remaining, limit, resetAt, lastChecked}`
- [x] **AC-US1-02**: Every GitHub API call in `GitHubClientV2` checks the shared budget before executing — skip with warning if `remaining < 200`
- [x] **AC-US1-03**: After each API call, decrement `remaining` in the state file (atomic read-modify-write)
- [x] **AC-US1-04**: Periodically validate budget against actual rate limit via `gh api rate_limit` (every 50 calls or 5 minutes, whichever first)

### US-002: Global Reconciler Lock (P1)
**Project**: specweave

**As a** SpecWeave user with multiple Claude sessions starting simultaneously
**I want** only one reconciler to run at a time across all processes
**So that** 5 concurrent sessions don't each burn 120+ API calls

**Acceptance Criteria**:
- [x] **AC-US2-01**: File-based lock at `.specweave/state/reconciler.lock` with PID and timestamp
- [x] **AC-US2-02**: If lock exists and is < 5 min old, reconciler skips with info message
- [x] **AC-US2-03**: Stale locks (> 5 min or PID not running) are automatically cleaned up

### US-003: Persistent Label Cache (P1)
**Project**: specweave

**As a** SpecWeave user
**I want** label existence cached to disk across CLI invocations
**So that** every sync doesn't re-create 8-12 labels

**Acceptance Criteria**:
- [x] **AC-US3-01**: Label cache persisted to `.specweave/state/github-label-cache.json`
- [x] **AC-US3-02**: On CLI start, labels are loaded from disk (not re-fetched from GitHub)
- [x] **AC-US3-03**: New labels are written to disk immediately after successful creation

### US-004: Skip Redundant API Calls for Linked Issues (P2)
**Project**: specweave

**As a** SpecWeave user syncing existing increments
**I want** the sync to skip duplicate detection for issues already linked in metadata
**So that** repeat syncs use ~6 calls instead of ~22

**Acceptance Criteria**:
- [x] **AC-US4-01**: When metadata.json has issue number for a user story, skip `DuplicateDetector.createWithProtection()` and update directly
- [x] **AC-US4-02**: Skip `getIssue()` before `editIssue()` when only updating body (direct edit)

## Out of Scope

- GraphQL migration (future Phase 3)
- GitHub App auth (future)
- Dashboard client changes (dashboard makes 0 GitHub calls)
