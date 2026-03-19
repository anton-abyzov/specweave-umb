---
increment: 0597-fix-ado-parent-child-linking
title: Fix ADO Sync Parent-Child Linking Bug
type: bug
priority: P1
status: completed
created: 2026-03-19T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Bug Fix: ADO Sync Parent-Child Linking

## Overview

ADO sync creates user stories linked to wrong parent epics from unrelated increments. `linkWorkItems()` silently swallows API failures, and a metadata fallback corrupts story work item IDs with Feature IDs, causing permanent cross-linking.

**Evidence**: Epic #1448 (FS-591) has zero children. Story #194 parented under Epic #191 (FS-480, wrong). Story #208 parented under Epic #206 (FS-482, wrong).

## User Stories

### US-001: Reliable ADO Parent-Child Linking (P1)
**Project**: specweave

**As a** SpecWeave user syncing to Azure DevOps
**I want** user stories to be correctly linked to their parent Feature/Epic
**So that** my ADO work item hierarchy accurately reflects my increment structure

**Acceptance Criteria**:
- [x] **AC-US1-01**: `linkWorkItems()` throws an error when the ADO API returns a non-409 failure status
- [x] **AC-US1-02**: `linkWorkItems()` treats HTTP 409 (duplicate link) as idempotent success
- [x] **AC-US1-03**: `createWorkItem()` propagates linking failures to callers when parentId is specified
- [x] **AC-US1-04**: Unit tests verify parent-child linking behavior in `ado-client.ts`

---

### US-002: Correct ADO Metadata Storage (P1)
**Project**: specweave

**As a** SpecWeave user
**I want** metadata.json to never record a Feature's work item ID as a Story's work item ID
**So that** subsequent syncs don't link stories to wrong parents

**Acceptance Criteria**:
- [x] **AC-US2-01**: When a story has no entry in `storyItemMap`, its metadata is skipped (not filled with Feature ID)
- [x] **AC-US2-02**: A warning is logged when story metadata is skipped due to missing sync data

---

### US-003: ADO Provider Parent Linking Tests (P2)
**Project**: specweave

**As a** SpecWeave developer
**I want** unit tests that verify ADO provider parent-child linking
**So that** regressions in the linking logic are caught before release

**Acceptance Criteria**:
- [x] **AC-US3-01**: Test verifies `createIssue` includes `Hierarchy-Reverse` relation when `feature.externalRef` is set
- [x] **AC-US3-02**: Test verifies `createIssue` omits relation when `feature.externalRef` is not set
- [x] **AC-US3-03**: Test verifies the ADO URL format in the parent link is correct

## Out of Scope

- Fixing existing corrupted ADO links (requires manual cleanup)
- JIRA parent linking changes (different mechanism, works correctly)
- Changes to the SyncEngine orchestration layer
