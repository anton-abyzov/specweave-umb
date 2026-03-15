---
id: US-002
feature: FS-521
title: Branch Naming with External Ticket Keys (P1)
status: completed
priority: P1
created: 2026-03-13T00:00:00.000Z
tldr: "**As a** developer working with JIRA or ADO."
project: specweave
external_tools:
  jira:
    key: SWE2E-250
  ado:
    id: 208
---

# US-002: Branch Naming with External Ticket Keys (P1)

**Feature**: [FS-521](./FEATURE.md)

**As a** developer working with JIRA or ADO
**I want** increment branches to include the external ticket key (e.g., `PROJ-123/sw/0521-smart-linking`)
**So that** JIRA/ADO smart commits and CI integrations can auto-link branches to tickets

---

## Acceptance Criteria

- [x] **AC-US2-01**: When `cicd.git.includeExternalKey` is true and an increment has an external ticket, the branch name includes the ticket key as a prefix (format: `{ticketKey}/{branchPrefix}{incrementId}`)
- [x] **AC-US2-02**: When no external ticket exists or the setting is disabled, branch naming falls back to the existing `{branchPrefix}{incrementId}` format
- [x] **AC-US2-03**: JIRA keys use the format `PROJ-123` and ADO keys use the format `AB#123` in branch names

---

## Implementation

**Increment**: [0521-external-integration-smart-linking](../../../../../increments/0521-external-integration-smart-linking/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_
