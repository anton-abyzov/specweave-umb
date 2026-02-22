---
increment: 0271-fix-external-sync-pipeline
title: "Fix External Sync Pipeline"
type: bug
priority: P1
status: in-progress
created: 2026-02-21
structure: user-stories
test_mode: test-after
coverage_target: 80
---

# Feature: Fix External Sync Pipeline

## Overview

GitHub issues are not being created since FS-238 due to three root causes in the external sync pipeline: (1) `loadUserStoriesForIncrement()` in SyncCoordinator returns empty when the living docs folder is missing, with no fallback to `deriveFeatureId()` or direct spec.md parsing; (2) multiple silent catch blocks in `checkExistingIssue()` and `checkExistingGitHubIssue()` swallow errors, hiding the real failure reason; (3) issue existence checks don't inspect the `externalLinks` metadata format (only the legacy `github.issue` format), causing duplicate creation attempts that fail on API.

## User Stories

### US-001: Fix loadUserStoriesForIncrement fallback (P1)
**Project**: specweave

**As a** developer using SpecWeave sync
**I want** the sync coordinator to find user stories even when living docs folders are missing
**So that** GitHub issues are created reliably for all increments

**Acceptance Criteria**:
- [x] **AC-US1-01**: `loadUserStoriesForIncrement()` uses `deriveFeatureId()` as fallback when featureId is not in spec.md frontmatter or metadata.json
- [x] **AC-US1-02**: When living docs folder is missing, falls back to parsing user stories directly from spec.md (same as `ExternalIssueAutoCreator.parseUserStories()`)
- [x] **AC-US1-03**: Logs a warning when falling back, so developers know living docs sync should be run

---

### US-002: Surface suppressed errors (P1)
**Project**: specweave

**As a** developer debugging sync failures
**I want** error details to be logged instead of silently swallowed
**So that** I can diagnose why GitHub issues are not being created

**Acceptance Criteria**:
- [x] **AC-US2-01**: `ExternalIssueAutoCreator.checkExistingIssue()` logs a warning on JSON parse errors instead of silent catch
- [x] **AC-US2-02**: `sync-progress.ts checkExistingGitHubIssue()` logs a warning on errors instead of silent catch
- [x] **AC-US2-03**: `sync-progress.ts detectActiveIncrement()` logs a debug message on errors instead of silent catch

---

### US-003: Fix externalLinks format checking (P2)
**Project**: specweave

**As a** developer using SpecWeave sync
**I want** existing issue checks to recognize all metadata formats
**So that** duplicate issues are not created

**Acceptance Criteria**:
- [x] **AC-US3-01**: `ExternalIssueAutoCreator.checkExistingIssue()` also checks `externalLinks.github` format
- [x] **AC-US3-02**: `sync-progress.ts checkExistingGitHubIssue()` also checks `externalLinks.github` format

## Functional Requirements

### FR-001: Fallback chain for loadUserStoriesForIncrement
When featureId is not in spec.md frontmatter or metadata.json, use `deriveFeatureId(incrementId)` as fallback. When living docs folder doesn't exist, parse user stories directly from spec.md body using regex (same approach as ExternalIssueAutoCreator).

### FR-002: Error logging in catch blocks
Replace all `catch { return null/false; }` with `catch (error) { logger.warn(...); return null/false; }`.

### FR-003: externalLinks format support
Add checks for `metadata.externalLinks.github.issues[US-XXX].issueNumber` and `metadata.externalLinks.github.issueNumber` in both issue existence checks.

## Success Criteria

- All 3 sync operations (GitHub, JIRA, ADO) no longer show as "failed" due to these bugs
- Error logs provide actionable diagnostics when sync fails
- No duplicate issues created due to format mismatch

## Out of Scope

- Fixing JIRA/ADO API credential issues
- Changing the overall sync architecture
- Adding new sync providers

## Dependencies

- specweave CLI codebase at `repositories/anton-abyzov/specweave/`
