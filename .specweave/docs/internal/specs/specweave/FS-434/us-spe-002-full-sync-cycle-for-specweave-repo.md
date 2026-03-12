---
id: US-SPE-002
feature: FS-434
title: "Full Sync Cycle for Specweave Repo"
status: completed
priority: P2
created: 2026-03-05
tldr: "**As a** developer."
project: specweave
related_projects: [vskill, vskill-platform]
external:
  github:
    issue: 1496
    url: "https://github.com/anton-abyzov/specweave/issues/1496"
---

# US-SPE-002: Full Sync Cycle for Specweave Repo

**Feature**: [FS-434](./FEATURE.md)

**As a** developer
**I want** the full sync cycle to work end-to-end for specweave
**So that** GitHub issues, JIRA tickets, and ADO work items stay synchronized

---

## Acceptance Criteria

- [x] **AC-SPE-US2-01**: GitHub issue created in anton-abyzov/specweave with correct title and labels
- [x] **AC-SPE-US2-02**: JIRA ticket created in WTTC project with AC checkboxes
- [x] **AC-SPE-US2-03**: ADO work item created in SpecWeaveSync with correct type

---

## Implementation

**Increment**: [0434-full-sync-cycle-test](../../../../../increments/0434-full-sync-cycle-test/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-001**: Sync to GitHub for all child repos
- [x] **T-002**: Sync to JIRA for all child repos
- [x] **T-005**: Verify close flow transitions external items
