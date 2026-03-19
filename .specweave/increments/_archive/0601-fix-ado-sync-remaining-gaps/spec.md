---
increment: 0601-fix-ado-sync-remaining-gaps
title: Fix Remaining ADO Sync Gaps
type: bug
priority: P1
status: completed
created: 2026-03-19T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Bug Fix: Remaining ADO Sync Gaps

## Overview

Post-brainstorm fixes for ADO sync. P0: `sync-progress.ts` writes Feature ID as Story ID on every progress-sync. P1: No API-level dedup for ADO (GitHub has `searchIssueByTitle`, ADO doesn't). P1: `updateIssue()` silently swallows errors.

## User Stories

### US-001: Remove ADO Metadata Corruption in sync-progress (P0)
**Project**: specweave

**As a** SpecWeave user
**I want** `/sw:progress-sync` to not corrupt my ADO metadata
**So that** user stories maintain correct work item IDs

**Acceptance Criteria**:
- [x] **AC-US1-01**: The ADO auto-mapping block in `sync-progress.ts` that writes Feature ID as Story IDs is removed
- [x] **AC-US1-02**: A warning is logged when unmapped ADO stories are detected instead of auto-mapping them

---

### US-002: ADO Layer 3 API-Level Dedup (P1)
**Project**: specweave

**As a** SpecWeave user
**I want** ADO sync to search for existing work items before creating new ones
**So that** metadata loss doesn't produce duplicate work items

**Acceptance Criteria**:
- [x] **AC-US2-01**: `AdoWorkItemFilter` supports a `title` field for WIQL queries
- [x] **AC-US2-02**: `AdoClient` has a `searchWorkItemByTitle()` method that queries by exact title + specweave tag
- [x] **AC-US2-03**: `createAdoIssues()` searches for existing Feature/Epic by title before creating
- [x] **AC-US2-04**: When an existing work item is found, it is reused (metadata updated, creation skipped)

---

### US-003: Fix Silent Update Failures in ADO Provider (P1)
**Project**: specweave

**As a** SpecWeave developer
**I want** `updateIssue()` in the ADO provider to throw on failure
**So that** callers know when updates fail

**Acceptance Criteria**:
- [x] **AC-US3-01**: `providers/ado.ts` `updateIssue()` checks `response.ok` and throws on failure
- [x] **AC-US3-02**: Unit test verifies `updateIssue()` throws on non-ok response

## Out of Scope

- JIRA auto-mapping fix (different mechanism, lower risk)
- Creation locking / TOCTOU race fix (P2, deferred)
- Retry/backoff for transient failures
