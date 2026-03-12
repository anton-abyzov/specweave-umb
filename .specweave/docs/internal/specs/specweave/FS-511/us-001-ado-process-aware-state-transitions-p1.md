---
id: US-001
feature: FS-511
title: ADO Process-Aware State Transitions (P1)
status: completed
priority: P1
created: 2026-03-12T00:00:00.000Z
tldr: "**As a** SpecWeave user with an ADO Basic process project."
project: specweave
external:
  github:
    issue: 1552
    url: https://github.com/anton-abyzov/specweave/issues/1552
---

# US-001: ADO Process-Aware State Transitions (P1)

**Feature**: [FS-511](./FEATURE.md)

**As a** SpecWeave user with an ADO Basic process project
**I want** increment closure to transition work items to the correct terminal state (Done, not Closed)
**So that** my ADO board accurately reflects completed work

---

## Acceptance Criteria

- [x] **AC-US1-01**: `closeIssue()` in `ado.ts` calls `detectProcessTemplate()` (lazy-cached) to resolve the correct terminal state per process template (Basic=Done, Agile=Closed, Scrum=Done, CMMI=Closed)
- [x] **AC-US1-02**: A `private cachedTemplate?: AdoProcessTemplateInfo` field caches the result of `detectProcessTemplate()` after first call; subsequent calls reuse it
- [x] **AC-US1-03**: If `detectProcessTemplate()` fails, fallback to `this.config.closedState || 'Closed'` (no regression from current behavior)
- [x] **AC-US1-04**: `mapStatusToAdo()` uses the cached template to resolve `completed` and `done` to the correct terminal state instead of hardcoding `'Closed'`
- [x] **AC-US1-05**: `reopenIssue()` uses the cached template to resolve the correct active state (Basic=Doing, Agile=Active, Scrum=Committed, CMMI=Active) with fallback to `this.config.activeState || 'Active'`

---

## Implementation

**Increment**: [0511-fix-ado-jira-sync](../../../../../increments/0511-fix-ado-jira-sync/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_
