---
id: US-005
feature: FS-398
title: "Fix ADO Work Item Type and State Assumptions (P1)"
status: completed
priority: P0
created: 2026-03-02T00:00:00.000Z
tldr: "**As a** user with Agile/Scrum ADO process templates."
project: specweave
---

# US-005: Fix ADO Work Item Type and State Assumptions (P1)

**Feature**: [FS-398](./FEATURE.md)

**As a** user with Agile/Scrum ADO process templates
**I want** work item creation to use the correct type and state names
**So that** items aren't created as "Issue" when they should be "User Story"

---

## Acceptance Criteria

- [x] **AC-US5-01**: `providers/ado.ts` createIssue() detects process template or accepts configurable work item type (default: `User Story` for Agile/Scrum, `Issue` for Basic)
- [x] **AC-US5-02**: ADO closeIssue() uses configurable target state (`Closed` for Agile, `Done` for Scrum/Basic)
- [x] **AC-US5-03**: ADO reopenIssue() uses configurable reopen state (not hardcoded `Active`)

---

## Implementation

**Increment**: [0398-sync-integration-critical-fixes](../../../../../increments/0398-sync-integration-critical-fixes/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_
