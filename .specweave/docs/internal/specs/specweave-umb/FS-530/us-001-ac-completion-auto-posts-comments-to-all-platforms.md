---
id: US-001
feature: FS-530
title: AC completion auto-posts comments to all platforms
status: completed
priority: P1
created: 2026-03-15
tldr: "**As a** SpecWeave user."
project: specweave-umb
external_tools:
  jira:
    key: SWE2E-228
  ado:
    id: 194
---

# US-001: AC completion auto-posts comments to all platforms

**Feature**: [FS-530](./FEATURE.md)

**As a** SpecWeave user
**I want** AC completion to automatically post progress comments to GitHub, JIRA, and ADO stories
**So that** stakeholders on any platform see real-time AC progress without manual updates

---

## Acceptance Criteria

- [x] **AC-US1-01**: Given a task marked complete in tasks.md, when the AC status hook fires, then a progress comment is posted to the linked GitHub issue showing which ACs are done
- [x] **AC-US1-02**: Given a task marked complete in tasks.md, when the AC status hook fires, then a progress comment is posted to the linked JIRA story showing AC completion percentage
- [x] **AC-US1-03**: Given a task marked complete in tasks.md, when the AC status hook fires, then a progress comment is posted to the linked ADO work item showing AC completion percentage

---

## Implementation

**Increment**: [0530-verify-full-sync-pipeline](../../../../../increments/0530-verify-full-sync-pipeline/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_
