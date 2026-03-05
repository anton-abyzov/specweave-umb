---
increment: 0425-umbrella-sync-e2e-test
title: "Umbrella Sync E2E Verification"
status: active
priority: P2
type: experiment
created: 2026-03-04
---

# Umbrella Sync E2E Verification

## Problem Statement

Verify that umbrella sync routing correctly routes GitHub issues, JIRA tickets, and ADO work items to per-child-repo targets based on the **Project** field in each user story.

## Goals

- Verify all three platforms (GitHub, JIRA, ADO) route correctly per child repo
- Verify cross-cutting increments work (stories targeting different repos)
- Verify fallback to global when project doesn't match

## User Stories

### US-SPE-001: Specweave Repo Sync Verification
**Project**: specweave

**As a** developer
**I want** sync to route to the specweave child repo
**So that** GitHub issues go to anton-abyzov/specweave, JIRA to WTTC, ADO to SpecWeaveSync

**Acceptance Criteria**:
- [ ] **AC-SPE-US1-01**: GitHub issue created in anton-abyzov/specweave (not specweave-umb)
- [ ] **AC-SPE-US1-02**: JIRA ticket created in WTTC project (not SWE2E)
- [ ] **AC-SPE-US1-03**: ADO work item created in SpecWeaveSync project

### US-VSK-001: VSkill Repo Sync Verification
**Project**: vskill

**As a** developer
**I want** sync to route to the vskill child repo
**So that** GitHub issues go to anton-abyzov/vskill, JIRA to SWE2E, ADO to VSkillSync

**Acceptance Criteria**:
- [ ] **AC-VSK-US1-01**: GitHub issue created in anton-abyzov/vskill (not specweave-umb)
- [ ] **AC-VSK-US1-02**: JIRA ticket created in SWE2E project
- [ ] **AC-VSK-US1-03**: ADO work item created in VSkillSync project

### US-VPL-001: VSkill-Platform Repo Sync Verification
**Project**: vskill-platform

**As a** developer
**I want** sync to route to the vskill-platform child repo
**So that** GitHub issues go to anton-abyzov/vskill-platform, JIRA to SWE2E, ADO to VSkillPlatformSync

**Acceptance Criteria**:
- [ ] **AC-VPL-US1-01**: GitHub issue created in anton-abyzov/vskill-platform (not specweave-umb)
- [ ] **AC-VPL-US1-02**: JIRA ticket created in SWE2E project
- [ ] **AC-VPL-US1-03**: ADO work item created in VSkillPlatformSync project

## Out of Scope

- Actual feature implementation — this is a sync verification experiment
- Bidirectional sync testing (status updates from external tools back to SpecWeave)

## Technical Notes

This increment tests the full umbrella sync pipeline:
1. `resolveSyncTarget()` reads **Project** field from each US
2. Routes to matching `childRepos[].sync` config
3. GitHub, JIRA, and ADO each get per-repo targets
4. Fallback to global config when no child repo matches

## Success Metrics

- All three user stories create issues in the correct external targets
- No issues leak to the umbrella-level targets (specweave-umb repo, SWE2E project)
