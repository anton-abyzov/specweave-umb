---
increment: 0403-ado-sync-plugin-fixes
title: ADO Sync Plugin Critical Fixes
feature_id: FS-403
type: bugfix
priority: P0
status: completed
created: 2026-03-02T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 95
---

# FS-403: ADO Sync Plugin Critical Fixes

## Overview

Grill report audit of `repositories/anton-abyzov/specweave/plugins/specweave-ado/` revealed 16 bugs ranging from permanently broken auto-sync to silent data loss. Three critical issues make ADO sync non-functional for most real-world scenarios: the post-task-completion hook reads a stale field path, batch fetches fail above 200 items due to missing pagination, and cross-project WIQL queries silently truncate results.

**Affected plugin**: `plugins/specweave-ado/`

**Key files**: `hooks/post-task-completion.sh`, `ado-client-v2.ts`, `ado-hierarchical-sync.ts`, `ado-profile-resolver.ts`, `ado-spec-sync.ts`, `conflict-resolver.ts`, `per-us-sync.ts`, `ado-duplicate-detector.ts`, `enhanced-ado-sync.js`

## User Stories

### US-001: Fix Broken Auto-Sync Hook and Batch Pagination (CRITICAL)

**As a** developer using ADO auto-sync
**I want** the post-task-completion hook and batch fetch to work correctly
**So that** task completions propagate to ADO and large queries succeed

**Acceptance Criteria**:
- [x] **AC-US1-01**: `post-task-completion.sh` reads work item ID from `.external_sync.ado.workItemId` instead of the stale `.ado.item` path
- [x] **AC-US1-02**: `ado-client-v2.ts` batch fetch paginates when result count exceeds 200, collecting all pages before returning
- [x] **AC-US1-03**: `ado-hierarchical-sync.ts` FILTERED strategy uses the org-level WIQL endpoint for cross-project queries, not the project-scoped endpoint

### US-002: Fix Profile Resolution and URL Construction (HIGH)

**As a** developer with profile-based ADO configuration
**I want** consistent profile resolution and correct URL generation
**So that** sync operations target the right ADO endpoints

**Acceptance Criteria**:
- [x] **AC-US2-01**: `ado-profile-resolver.ts` and `commands/sync.md` use the same field name for the active/default profile (resolve `activeProfile` vs `defaultProfile` mismatch)
- [x] **AC-US2-02**: `ado-spec-sync.ts` URL construction uses the computed `workItemType` instead of hardcoded `$Feature`
- [x] **AC-US2-03**: `ado-client-v2.ts` `testConnection()` builds the correct URL in single-project mode (currently always 404s)
- [x] **AC-US2-04**: Org-specific PAT pattern `AZURE_DEVOPS_PAT_MYORG` documented in SKILL.md is implemented in code

### US-003: Fix Process Template Assumptions (HIGH)

**As a** team using Scrum or CMMI process templates
**I want** the plugin to respect my process template's work item types and states
**So that** sync works beyond the Agile template

**Acceptance Criteria**:
- [x] **AC-US3-01**: `conflict-resolver.ts` state resolution is process-template-aware (not hardcoded to Agile states)
- [x] **AC-US3-02**: `per-us-sync.ts` uses the configured work item type instead of hardcoded `'User Story'` (Scrum uses PBI, CMMI uses Requirement)
- [x] **AC-US3-03**: `ado-client-v2.ts` area path construction does not double-prepend the project name when it is already included

### US-004: Fix HTTP Reliability and Request Safety (HIGH)

**As a** user running sync against Azure DevOps
**I want** HTTP requests to have timeouts and safe query construction
**So that** sync does not hang indefinitely or produce corrupt queries

**Acceptance Criteria**:
- [x] **AC-US4-01**: `ado-hierarchical-sync.ts` HTTP requests have a configurable timeout (default 30s) so they cannot hang indefinitely
- [x] **AC-US4-02**: `ado-hierarchical-sync.ts` `addTimeRangeFilter` regex does not corrupt existing WIQL WHERE clauses

### US-005: Fix Data Integrity and Idempotency Issues (MEDIUM)

**As a** user relying on duplicate detection and conditional updates
**I want** accurate detection results and non-destructive updates
**So that** sync does not silently lose data or report false success

**Acceptance Criteria**:
- [x] **AC-US5-01**: `ado-hierarchical-sync.ts` applies container-specific filters per container, not just the first container's filters globally
- [x] **AC-US5-02**: `ado-duplicate-detector.ts` verification failure returns `success: false` (currently returns `success: true`)
- [x] **AC-US5-03**: `ado-spec-sync.ts` `updateAdoFeature` performs conditional updates (only writes title/description if changed, preserving ADO-side edits)
- [x] **AC-US5-04**: `enhanced-ado-sync.js` task URL uses the actual repository name instead of hardcoded `repo` string
- [x] **AC-US5-05**: `ado-hierarchical-sync.ts` `addTimeRangeFilter` regex handles existing WHERE clauses without corruption (overlaps with AC-US4-02; test both paths)
