---
id: US-004
feature: FS-511
title: ADO Metadata Fallback for Closure (P2)
status: completed
priority: P1
created: 2026-03-12T00:00:00.000Z
tldr: "**As a** SpecWeave user closing an increment with ADO sync."
project: specweave
external:
  github:
    issue: 1555
    url: https://github.com/anton-abyzov/specweave/issues/1555
---

# US-004: ADO Metadata Fallback for Closure (P2)

**Feature**: [FS-511](./FEATURE.md)

**As a** SpecWeave user closing an increment with ADO sync
**I want** ADO work item ID resolution to check metadata.json as a fallback
**So that** work items created by the auto-creator are properly closed

---

## Acceptance Criteria

- [x] **AC-US4-01**: `closeAdoWorkItemsForUserStories()` in `sync-coordinator.ts` implements the same 3-layer resolution as the JIRA closure path: `usFile.external_tools?.ado?.id` -> `usFile.external_id` -> `metadata.ado.work_item_id`
- [x] **AC-US4-02**: metadata.json is read once per closure call (not per user story) and cached locally

---

## Implementation

**Increment**: [0511-fix-ado-jira-sync](../../../../../increments/0511-fix-ado-jira-sync/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_
