---
id: US-001
feature: FS-527
title: Verify JIRA native AC checkboxes
status: completed
priority: P2
created: 2026-03-15
tldr: "**As a** SpecWeave user."
project: specweave-umb
external_tools:
  github:
    issue: 78
    url: https://github.com/anton-abyzov/specweave-umb/issues/78
  jira:
    key: SWE2E-209
  ado:
    id: 194
external:
  github:
    issue: 78
    url: https://github.com/anton-abyzov/specweave-umb/issues/78
---

# US-001: Verify JIRA native AC checkboxes

**Feature**: [FS-527](./FEATURE.md)

**As a** SpecWeave user
**I want** acceptance criteria in JIRA story descriptions to render as native tickable checkboxes
**So that** I can track AC progress directly inside the JIRA issue without leaving the tool

---

## Acceptance Criteria

- [x] **AC-US1-01**: Given a feature synced to JIRA, when the story description is viewed, then each AC appears as a native JIRA checkbox (ADF taskItem) not plain bullet text
- [x] **AC-US1-02**: Given an AC is marked [x] in spec.md, when the AC status hook fires, then the corresponding JIRA story description checkbox is flipped to DONE automatically
- [x] **AC-US1-03**: Given the JIRA story description, when Priority and Status fields are rendered, then they appear on separate lines (not fused as "Priority: P1Status: done")

---

## Implementation

**Increment**: [0527-test-ac-checkbox-sync](../../../../../increments/0527-test-ac-checkbox-sync/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_
