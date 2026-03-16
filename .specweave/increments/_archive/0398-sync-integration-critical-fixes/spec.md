---
increment: 0398-sync-integration-critical-fixes
title: Critical Sync Integration Bug Fixes
feature_id: FS-398
type: bug
priority: P0
status: completed
created: 2026-03-02T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# FS-398: Critical Sync Integration Bug Fixes

## Overview

Comprehensive audit of the sync subsystem (`src/sync/`, providers, reconcilers, coordinator, auto-creator) has revealed 30+ bugs across critical, high, and medium severity tiers. These range from stub code in production paths and data-destroying reconciliation logic to hardcoded branch names, missing pagination, and profile resolution inconsistencies.

**Affected files**: `sync-coordinator.ts`, `external-item-sync-service.ts`, `external-issue-auto-creator.ts`, `github-reconciler.ts`, `providers/github.ts`, `providers/jira.ts`, `providers/ado.ts`, `config.ts`, `status-mapper.ts`

## User Stories

### US-001: Fix Production Stub Code and Mock Data (P0)
**Project**: specweave

**As a** developer using SpecWeave sync
**I want** all sync code paths to execute real logic
**So that** external tool sync actually works end-to-end

**Acceptance Criteria**:
- [x] **AC-US1-01**: `sync-coordinator.ts` loadCompletionData() parses real task titles from tasks.md instead of using "Add mock data for demo" stub (line 838)
- [x] **AC-US1-02**: `external-item-sync-service.ts` commentOnlySync() posts comments to actual external APIs instead of just logging "TODO: Integrate with external tool APIs" (line 283-284)
- [x] **AC-US1-03**: `external-item-sync-service.ts` fullSync() implements real update logic instead of "TODO: Implement full sync logic" stub (line 346-350)

### US-002: Fix GitHub Reconciler Profile Resolution Bypass (P0)
**Project**: specweave

**As a** user with profile-based sync configuration
**I want** the GitHub reconciler to respect profile configs
**So that** reconciliation works for users who configured sync via profiles

**Acceptance Criteria**:
- [x] **AC-US2-01**: `github-reconciler.ts` line 94 uses `isProviderEnabled(config, 'github')` instead of `config.sync?.github?.enabled ?? false` which bypasses profile-based detection
- [x] **AC-US2-02**: All three reconcilers (GitHub, JIRA, ADO) use consistent provider detection via `isProviderEnabled()`

### US-003: Fix Hardcoded Branch Names in Issue Bodies (P1)
**Project**: specweave

**As a** user with a non-standard default branch
**I want** issue body links to use my actual default branch
**So that** links in GitHub/JIRA/ADO issues resolve correctly

**Acceptance Criteria**:
- [x] **AC-US3-01**: `external-issue-auto-creator.ts` buildGitHubIssueBody() and buildFeatureLevelIssueBody() detect default branch instead of hardcoding `develop` (lines 781, 811-812)
- [x] **AC-US3-02**: Default branch detection uses git or config, with fallback to `main`

### US-004: Fix Pagination Gaps in Pull Operations (P1)
**Project**: specweave

**As a** user with many external issues
**I want** sync pull operations to retrieve all relevant items
**So that** no issues are missed during sync

**Acceptance Criteria**:
- [x] **AC-US4-01**: GitHub provider `pullChanges()` handles pagination via Link header beyond the first 50 results
- [x] **AC-US4-02**: JIRA provider `pullChanges()` handles pagination via `startAt` beyond `maxResults: 50`
- [x] **AC-US4-03**: ADO provider `pullChanges()` handles WIQL results beyond the first 50 IDs via batching

### US-005: Fix ADO Work Item Type and State Assumptions (P1)
**Project**: specweave

**As a** user with Agile/Scrum ADO process templates
**I want** work item creation to use the correct type and state names
**So that** items aren't created as "Issue" when they should be "User Story"

**Acceptance Criteria**:
- [x] **AC-US5-01**: `providers/ado.ts` createIssue() detects process template or accepts configurable work item type (default: `User Story` for Agile/Scrum, `Issue` for Basic)
- [x] **AC-US5-02**: ADO closeIssue() uses configurable target state (`Closed` for Agile, `Done` for Scrum/Basic)
- [x] **AC-US5-03**: ADO reopenIssue() uses configurable reopen state (not hardcoded `Active`)

### US-006: Fix JIRA Epic Description Using Wiki Markup in ADF Context (P2)
**Project**: specweave

**As a** user with JIRA Cloud
**I want** JIRA descriptions to render correctly
**So that** auto-created epics look professional

**Acceptance Criteria**:
- [x] **AC-US6-01**: `external-issue-auto-creator.ts` buildJiraEpicDescription() uses plain text or ADF format instead of wiki markup (`h2.`, `h3.`, `*bold*`) since the createIssue API wraps content in ADF

### US-007: Fix Missing Error Handling in Provider API Responses (P1)
**Project**: specweave

**As a** developer debugging sync failures
**I want** all provider API calls to check response status
**So that** errors surface clearly instead of crashing on JSON parse

**Acceptance Criteria**:
- [x] **AC-US7-01**: JIRA provider `transitionIssue()` checks response.ok before parsing JSON (line 335-336)
- [x] **AC-US7-02**: JIRA provider `detectHierarchy()` checks response.ok before parsing (line 233)
- [x] **AC-US7-03**: ADO provider `pullChanges()` checks WIQL response.ok and batch GET response.ok before parsing (lines 186, 193-196)
- [x] **AC-US7-04**: GitHub provider `applyLabels()` PUT request checks response.ok (line 187)
- [x] **AC-US7-05**: GitHub provider `ensureLabelExists()` distinguishes 422 (already exists) from real errors instead of blanket catch (line 273-275)

### US-008: Fix Reconciler Data Safety Gaps (P2)
**Project**: specweave

**As a** user managing increment lifecycle
**I want** reconciliation to be safe for all status transitions
**So that** issues don't get incorrectly reopened or left in wrong state

**Acceptance Criteria**:
- [x] **AC-US8-01**: Reconcilers treat `paused` status as "should be open" (missing from shouldBeOpen list in github-reconciler.ts line 153)
- [x] **AC-US8-02**: Reconcilers log a warning for unknown/missing status instead of silently skipping

### US-009: Fix JIRA Idempotency Check Comparing Different Formats (P0)
**Project**: specweave

**As a** user with JIRA sync enabled
**I want** duplicate comment prevention to work correctly
**So that** JIRA issues don't get flooded with duplicate comments on every sync

**Acceptance Criteria**:
- [x] **AC-US9-01**: `sync-coordinator.ts` JIRA idempotency check at line 700 handles the fact that `lastComment.body` returns an ADF object while `completionComment` is a plain text string — comparison must normalize formats

### US-010: Fix Config Schema Inconsistencies (P2)
**Project**: specweave

**As a** user configuring sync
**I want** config properties to be consistent between types and runtime code
**So that** configuration works as documented

**Acceptance Criteria**:
- [x] **AC-US10-01**: `config.ts` PartialSyncConfig interface includes `profiles` field to match actual config.json shape
- [x] **AC-US10-02**: StatusMapper.canUpdateExternal() defaults align with SyncCoordinator behavior (currently StatusMapper returns `false`, Coordinator falls back to `permissions.canUpsert`)
- [x] **AC-US10-03**: validateSyncConfigConsistency() validates profile-based configs, not just legacy format

### US-011: Fix GitHub Issue Search Title Format Mismatch (P0)
**Project**: specweave

**As a** user with auto-create enabled
**I want** duplicate detection to work with the current issue title format
**So that** issues aren't duplicated when auto-create runs

**Acceptance Criteria**:
- [x] **AC-US11-01**: `external-issue-auto-creator.ts` createGitHubIssues() searches using current title format `US-XXX:` instead of legacy `[FS-XXX]` prefix which no longer matches (line 497-498)

### US-012: Fix ADO getAdoPat Sync vs Async Mismatch (P1)
**Project**: specweave

**As a** developer
**I want** the ADO PAT provider to be called consistently
**So that** PAT retrieval doesn't fail silently

**Acceptance Criteria**:
- [x] **AC-US12-01**: `sync-coordinator.ts` ADO sync path at line 769 calls `getAdoPat()` consistently (currently missing `await` while line 247 uses `await`)

## Priority Tiers

### Critical (P0 — data loss / broken core flow)
- **US-001**: Stub code in production sync paths — comments never posted, mock task data
- **US-002**: Profile-based GitHub config silently ignored by reconciler
- **US-009**: JIRA duplicate comment prevention always fails (format mismatch)
- **US-011**: Issue auto-create duplicate detection broken (title format mismatch)

### High (P1 — significant user impact)
- **US-003**: Hardcoded `develop` branch breaks issue body links for non-develop repos
- **US-004**: Pagination gaps — only first 50 items synced, rest silently lost
- **US-005**: Wrong ADO work item type for Agile/Scrum process templates
- **US-007**: Missing response.ok checks crash on non-200 API responses
- **US-012**: Sync/async PAT retrieval mismatch

### Medium (P2 — quality / robustness)
- **US-006**: Wiki markup in ADF context produces garbled JIRA descriptions
- **US-008**: Missing `paused` status in reconciler open-state list
- **US-010**: Config type/runtime inconsistencies

## Success Criteria

- All critical (P0) bugs fixed with regression tests
- All high (P1) bugs fixed with regression tests
- Medium (P2) bugs fixed where possible
- All existing sync tests continue to pass
- No new test failures introduced

## Out of Scope

- Rewriting the sync engine architecture (addressed by separate ADR)
- Adding new sync providers (e.g., Linear, Notion)
- Changing the sync configuration schema structure (only fixing inconsistencies)
- Performance optimization of sync operations

## Dependencies

- Access to specweave repo at `repositories/anton-abyzov/specweave/`
- Existing test infrastructure (Vitest)
- No external service dependencies (all tests use mocks)
