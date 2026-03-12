---
id: US-SPE-001
feature: FS-425
title: "Specweave Repo Sync Verification"
status: completed
priority: P2
created: 2026-03-04
tldr: "**As a** developer."
project: specweave
related_projects: [vskill, vskill-platform]
external:
  github:
    issue: 1489
    url: "https://github.com/anton-abyzov/specweave/issues/1489"
---

# US-SPE-001: Specweave Repo Sync Verification

**Feature**: [FS-425](./FEATURE.md)

**As a** developer
**I want** sync to route to the specweave child repo
**So that** GitHub issues go to anton-abyzov/specweave, JIRA to WTTC, ADO to SpecWeaveSync

---

## Acceptance Criteria

- [x] **AC-SPE-US1-01**: GitHub issue created in anton-abyzov/specweave (not specweave-umb)
- [x] **AC-SPE-US1-02**: JIRA ticket created in WTTC project (not SWE2E)
- [x] **AC-SPE-US1-03**: ADO work item created in SpecWeaveSync project

---

## Implementation

**Increment**: [0425-umbrella-sync-e2e-test](../../../../../increments/0425-umbrella-sync-e2e-test/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-001**: Verify resolver routes all three platforms for each child repo
- [x] **T-005**: Verify JIRA routing per child repo
- [x] **T-006**: Verify ADO routing per child repo
