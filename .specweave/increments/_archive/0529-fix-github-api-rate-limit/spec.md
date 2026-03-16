---
id: FS-529
title: Fix GitHub API Rate Limit Exhaustion
status: completed
priority: P1
project: specweave-umb
---

# FS-529: Fix GitHub API Rate Limit Exhaustion

## Overview

SpecWeave exhausts GitHub's 5000 req/hour API limit during normal sync operations. The reconciler scans ALL 529 increments (175 active + 372 archived + 12 abandoned), making individual `getIssue()` calls per user story — 350+ API calls per run. Combined with DuplicateDetector triple-scan and AC checkbox N+1, total reaches ~5000 calls/hour.

**Target**: 10x reduction — from ~5000 to <500 calls/hour.

## User Stories

### US-001: Scope reconciler to active increments only

**As a** SpecWeave user with 175+ features
**I want** the reconciler to only scan active increments
**So that** API calls scale with active work, not total history

#### Acceptance Criteria

- [x] **AC-US1-01**: Given 529 total increments (175 active, 354 archived/abandoned), when reconciler runs, then only active increments trigger GitHub API calls
- [x] **AC-US1-02**: Given a completed increment with all issues already closed, when reconciler runs, then no `getIssue()` calls are made for that increment
- [x] **AC-US1-03**: Given reconciler ran less than 5 minutes ago, when triggered again, then it returns immediately (debounced) unless force=true

### US-002: Eliminate redundant API calls in sync pipeline

**As a** SpecWeave user
**I want** sync operations to cache responses and batch requests
**So that** each sync session uses minimal API calls

#### Acceptance Criteria

- [x] **AC-US2-01**: Given multiple `getIssue()` calls for the same issue within 30 seconds, when the second call is made, then the cached response is returned without an API call
- [x] **AC-US2-02**: Given DuplicateDetector creating a new issue, when Phase 1 search finds no duplicates, then Phase 3 verification search is skipped (1 API call instead of 3)
- [x] **AC-US2-03**: Given a sync operation starting, when remaining rate limit is below 100, then the operation is skipped with a warning log
- [x] **AC-US2-04**: Given AC checkbox sync with 4 user stories, when syncing checkboxes, then issue data is fetched in 1 batch GraphQL call instead of 4 individual calls
