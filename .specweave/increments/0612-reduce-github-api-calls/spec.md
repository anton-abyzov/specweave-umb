---
increment: 0612-reduce-github-api-calls
title: Reduce GitHub API call volume in sync-progress (Phase 1)
type: feature
priority: P1
status: completed
created: 2026-03-19T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Reduce GitHub API call volume in sync-progress (Phase 1)

## Problem Statement

The `sync-progress` command makes ~150 GitHub API calls per 7-user-story increment (10-18 per US), hitting the 5000/hour rate limit after just 2 increments. This blocks workflows and wastes developer time.

**Project**: specweave

## User Stories

### US-001: Session-Level Caching (P0)
**Project**: specweave

**As a** SpecWeave user
**I want** labels and milestones to be cached per sync session
**So that** redundant API calls are eliminated on repeated operations

**Acceptance Criteria**:
- [x] **AC-US1-01**: Labels are created once per repo per session — subsequent issues skip `gh label create`
- [x] **AC-US1-02**: Milestone lookup is cached per session — subsequent user stories reuse the cached milestone number
- [x] **AC-US1-03**: Caches are scoped per `owner/repo` to prevent cross-repo contamination

---

### US-002: Reduce Redundant Searches and Fetches (P0)
**Project**: specweave

**As a** SpecWeave user
**I want** redundant API searches and sequential fetches to be eliminated
**So that** each user story sync uses the minimum necessary API calls

**Acceptance Criteria**:
- [x] **AC-US2-01**: DuplicateDetector Phase 3 verification is disabled by default (opt-in via `SPECWEAVE_VERIFY_DUPLICATES=1`)
- [x] **AC-US2-02**: `getIssue()` and `getLastComment()` are merged into a single GraphQL query in `updateUserStoryIssue`
- [x] **AC-US2-03**: `createEpicIssue()` accepts a `skipDuplicateCheck` option, and DuplicateDetector passes it to skip the redundant search
- [x] **AC-US2-04**: AC checkbox sync and AC progress sync share fetched issue state instead of fetching independently

## Out of Scope

- Full GraphQL engine rewrite (Phase 3 item)
- Persistent file-backed cache (Phase 2 item)
- GitHub App authentication changes
- JIRA/ADO sync optimizations (separate increment)

## Red Lines

1. Never cache DuplicateDetector Phase 1 search results
2. Never remove the LockManager sync lock
3. Never break `gh auth login` compatibility
