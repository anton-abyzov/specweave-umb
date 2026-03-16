---
increment: 0434-full-sync-cycle-test
title: "Full Sync Cycle E2E Test"
status: active
priority: P2
type: experiment
created: 2026-03-05
---

# Full Sync Cycle E2E Test

## Problem Statement

Verify the complete synchronization lifecycle: create an internal increment, sync to GitHub/JIRA/ADO, verify progress comments with AC status, and test the full close flow.

## Goals

- Verify internal increment creation syncs to all 3 external platforms
- Verify progress comments are posted to GitHub/JIRA/ADO with AC checkboxes
- Verify close synchronization transitions external items to completed state

## User Stories

### US-SPE-002: Full Sync Cycle for Specweave Repo
**Project**: specweave

**As a** developer
**I want** the full sync cycle to work end-to-end for specweave
**So that** GitHub issues, JIRA tickets, and ADO work items stay synchronized

**Acceptance Criteria**:
- [x] **AC-SPE-US2-01**: GitHub issue created in anton-abyzov/specweave with correct title and labels
- [x] **AC-SPE-US2-02**: JIRA ticket created in WTTC project with AC checkboxes
- [x] **AC-SPE-US2-03**: ADO work item created in SpecWeaveSync with correct type

### US-VSK-002: Full Sync Cycle for VSkill Repo
**Project**: vskill

**As a** developer
**I want** the full sync cycle to work end-to-end for vskill
**So that** vskill issues are tracked across all platforms

**Acceptance Criteria**:
- [x] **AC-VSK-US2-01**: GitHub issue created in anton-abyzov/vskill
- [x] **AC-VSK-US2-02**: JIRA ticket created in SWE2E project

### US-VPL-002: Full Sync Cycle for VSkill-Platform Repo
**Project**: vskill-platform

**As a** developer
**I want** the full sync cycle to work end-to-end for vskill-platform
**So that** vskill-platform issues are tracked across all platforms

**Acceptance Criteria**:
- [x] **AC-VPL-US2-01**: GitHub issue created in anton-abyzov/vskill-platform
- [x] **AC-VPL-US2-02**: JIRA ticket created in SWE2E project

## Out of Scope

- Bidirectional sync testing (status updates from external tools back)
- ADO for vskill/vskill-platform (VSkillSync/VSkillPlatformSync projects don't exist)

## Technical Notes

Tests the v1.0.384 sync pipeline with fixes:
- Compound US-ID parsing (v1.0.373)
- Cross-repo -R flag targeting (v1.0.380)
- .env token parsing fix (v1.0.381)
- ADO Basic process type detection (v1.0.382)

## Success Metrics

- All user stories create issues in the correct external targets
- Progress comments reflect AC status
- Close flow transitions GitHub issues to closed state
