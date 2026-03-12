---
id: US-002
feature: FS-511
title: ADO Parent Work Item Linking (P1)
status: completed
priority: P1
created: 2026-03-12T00:00:00.000Z
tldr: "**As a** SpecWeave user syncing to ADO."
project: specweave
external:
  github:
    issue: 1553
    url: https://github.com/anton-abyzov/specweave/issues/1553
---

# US-002: ADO Parent Work Item Linking (P1)

**Feature**: [FS-511](./FEATURE.md)

**As a** SpecWeave user syncing to ADO
**I want** user story work items to be linked to their parent epic/feature work item
**So that** my ADO hierarchy reflects the SpecWeave spec structure

---

## Acceptance Criteria

- [x] **AC-US2-01**: `createIssue()` in `ado.ts` reads `feature.externalRef?.id` to obtain the parent work item ID
- [x] **AC-US2-02**: When a parent ID exists, `createIssue()` adds a `System.LinkTypes.Hierarchy-Reverse` relation to the PATCH operations pointing to the parent work item URL
- [x] **AC-US2-03**: When no parent ID exists (feature not yet synced), creation proceeds without parent link (no error)

---

## Implementation

**Increment**: [0511-fix-ado-jira-sync](../../../../../increments/0511-fix-ado-jira-sync/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_
