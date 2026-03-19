---
increment: 0609-fix-github-api-rate-limit
title: Fix GitHub API Rate Limit Exhaustion
type: bug
priority: P1
status: completed
created: 2026-03-19T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Fix GitHub API Rate Limit Exhaustion

## Overview

GitHub sync exhausts the 5000/hr API rate limit during increment closures due to redundant API calls in `updateUserStoryIssue()`, missing rate limit awareness, and unnecessary writes when nothing changed. This fix eliminates redundant fetches, adds rate limit pre-checks, and skips unchanged writes to reduce API calls by ~50%.

## User Stories

### US-001: Eliminate Redundant Issue Fetches (P1)
**Project**: specweave

**As a** SpecWeave user closing increments
**I want** GitHub sync to cache issue data within a single sync operation
**So that** the same issue is not fetched 3-4 times per user story

**Acceptance Criteria**:
- [x] **AC-US1-01**: `updateUserStoryIssue()` fetches issue data once and passes it to `updateStatusLabels()` instead of re-fetching
- [x] **AC-US1-02**: `updateStatusLabels()` accepts cached issue data as a parameter and does not call `getIssue()` internally when data is provided
- [x] **AC-US1-03**: The second `getIssue()` call in `updateStatusLabels()` is removed; the first fetch result is reused
- [x] **AC-US1-04**: `getLastComment()` result is fetched once and shared between `updateUserStoryIssue()` and `updateStatusLabels()`

---

### US-002: Rate Limit Pre-Check (P1)
**Project**: specweave

**As a** SpecWeave user
**I want** GitHub sync to check remaining API budget before starting
**So that** sync degrades gracefully instead of hitting 403 errors mid-operation

**Acceptance Criteria**:
- [x] **AC-US2-01**: `syncFeatureToGitHub()` calls `checkRateLimit()` before acquiring the sync lock
- [x] **AC-US2-02**: When remaining API calls < 200, sync logs a warning and returns early with a retriable status
- [x] **AC-US2-03**: The retry queue captures skipped syncs for later execution

---

### US-003: Skip-If-Unchanged Guards (P2)
**Project**: specweave

**As a** SpecWeave user
**I want** GitHub sync to skip label and comment updates when nothing has changed
**So that** unnecessary API calls are eliminated during re-syncs

**Acceptance Criteria**:
- [x] **AC-US3-01**: `updateStatusLabels()` compares current labels with desired labels and skips API calls if they match
- [x] **AC-US3-02**: `postProgressCommentIfChanged()` uses `this.client.getLastComment()` instead of direct `gh api` call
- [x] **AC-US3-03**: When body, labels, and progress are all unchanged, zero write API calls are made for that user story

---

### US-004: DuplicateDetector Optimization (P2)
**Project**: specweave

**As a** SpecWeave user
**I want** the DuplicateDetector to skip Phase 3 verification when reusing an existing issue
**So that** the identical search query is not executed twice unnecessarily

**Acceptance Criteria**:
- [x] **AC-US4-01**: When `createWithProtection()` finds an existing issue in Phase 1 and reuses it (no new issue created), Phase 3 verification is skipped
- [x] **AC-US4-02**: When a new issue IS created, Phase 3 verification still runs (safety check for race conditions)

## Out of Scope

- GraphQL batch migration (deferred — too high risk for this fix)
- Dual-trigger deduplication (already properly handled with 4 layers)
- Reconciler optimization (already well-optimized with debounce + pre-flight)

## Dependencies

- Existing `checkRateLimit()` in `github-client-v2.ts`
- Existing retry queue infrastructure in `sync-retry.ts`
