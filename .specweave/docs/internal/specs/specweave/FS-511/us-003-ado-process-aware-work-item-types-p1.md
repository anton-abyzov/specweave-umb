---
id: US-003
feature: FS-511
title: ADO Process-Aware Work Item Types (P1)
status: completed
priority: P1
created: 2026-03-12T00:00:00.000Z
tldr: "**As a** SpecWeave user with an ADO Basic process project."
project: specweave
external:
  github:
    issue: 1554
    url: https://github.com/anton-abyzov/specweave/issues/1554
---

# US-003: ADO Process-Aware Work Item Types (P1)

**Feature**: [FS-511](./FEATURE.md)

**As a** SpecWeave user with an ADO Basic process project
**I want** user stories to be created as Issue work items (not User Story)
**So that** work item creation does not fail with a 400 error on Basic projects

---

## Acceptance Criteria

- [x] **AC-US3-01**: `createIssue()` in `ado.ts` uses the cached template from `detectProcessTemplate()` to resolve the correct work item type for user stories (Basic=Issue, Agile=User Story, Scrum=Product Backlog Item, CMMI=Requirement)
- [x] **AC-US3-02**: If template detection fails, fallback to `this.config.workItemType || 'User Story'` (no regression)
- [x] **AC-US3-03**: The existing `detectHierarchy()` method is aligned with the new cached template data (no duplicate detection calls)

---

## Implementation

**Increment**: [0511-fix-ado-jira-sync](../../../../../increments/0511-fix-ado-jira-sync/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_
