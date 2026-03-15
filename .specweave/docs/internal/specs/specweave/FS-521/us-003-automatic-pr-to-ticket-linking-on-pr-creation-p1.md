---
id: US-003
feature: FS-521
title: Automatic PR-to-Ticket Linking on PR Creation (P1)
status: completed
priority: P1
created: 2026-03-13T00:00:00.000Z
tldr: "**As a** developer using pr-based push strategy."
project: specweave
external_tools:
  jira:
    key: SWE2E-252
  ado:
    id: 209
---

# US-003: Automatic PR-to-Ticket Linking on PR Creation (P1)

**Feature**: [FS-521](./FEATURE.md)

**As a** developer using pr-based push strategy
**I want** SpecWeave to automatically add remote links (JIRA) and hyperlinks (ADO) when a PR is created during increment closure
**So that** external tickets are bidirectionally linked to PRs without manual `specweave link-pr` invocation

---

## Acceptance Criteria

- [x] **AC-US3-01**: When pr-based closure creates a PR and the increment has JIRA external refs, `addRemoteLink` is called automatically for each JIRA issue
- [x] **AC-US3-02**: When pr-based closure creates a PR and the increment has ADO external refs, `addHyperlink` is called automatically for each ADO work item
- [x] **AC-US3-03**: Link failures are logged as warnings but do not block PR creation or increment closure

---

## Implementation

**Increment**: [0521-external-integration-smart-linking](../../../../../increments/0521-external-integration-smart-linking/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_
