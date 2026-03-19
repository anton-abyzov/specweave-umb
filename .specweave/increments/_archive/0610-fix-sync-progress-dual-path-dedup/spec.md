---
increment: 0610-fix-sync-progress-dual-path-dedup
title: Fix sync-progress dual-path duplication for JIRA/ADO
type: bug
priority: P0
status: completed
created: 2026-03-19T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 95
---

# Bug Fix: sync-progress dual-path duplication for JIRA/ADO

## Problem Statement

The `specweave sync-progress` command creates duplicate JIRA epics and ADO features due to a field name mismatch between Step 2 (LivingDocsSync backfill) and Step 4 (ExternalIssueAutoCreator dedup check). `backfillExternalLinks()` writes `epicKey`/`featureId` but `checkExistingIssue()` only checks `issueKey`/`workItemId`.

**Project**: specweave

## User Stories

### US-001: JIRA Dedup Field Name Fix (P0)
**Project**: specweave

**As a** SpecWeave user
**I want** sync-progress to recognize JIRA items created by living docs sync
**So that** duplicate JIRA epics are not created

**Acceptance Criteria**:
- [x] **AC-US1-01**: `checkExistingIssue('jira')` returns the epic key when `externalLinks.jira.epicKey` is present
- [x] **AC-US1-02**: `checkExistingIssue('jira')` continues to work when `externalLinks.jira.issueKey` is present (regression guard)

---

### US-002: ADO Dedup Field Name Fix (P0)
**Project**: specweave

**As a** SpecWeave user
**I want** sync-progress to recognize ADO items created by living docs sync
**So that** duplicate ADO features are not created

**Acceptance Criteria**:
- [x] **AC-US2-01**: `checkExistingIssue('ado')` returns the feature ID when `externalLinks.ado.featureId` is present
- [x] **AC-US2-02**: `checkExistingIssue('ado')` continues to work when `externalLinks.ado.workItemId` is present (regression guard)

## Out of Scope

- Refactoring the dual-path architecture (Step 2 + Step 4)
- Unifying field naming conventions across the codebase
- JIRA/ADO user story-level dedup (only feature/epic level)
