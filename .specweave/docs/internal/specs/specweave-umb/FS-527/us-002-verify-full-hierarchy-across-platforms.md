---
id: US-002
feature: FS-527
title: Verify full hierarchy across platforms
status: completed
priority: P2
created: 2026-03-15
tldr: "**As a** SpecWeave user."
project: specweave-umb
external:
  github:
    issue: 79
    url: https://github.com/anton-abyzov/specweave-umb/issues/79
external_tools:
  jira:
    key: SWE2E-210
  ado:
    id: 208
---

# US-002: Verify full hierarchy across platforms

**Feature**: [FS-527](./FEATURE.md)

**As a** SpecWeave user
**I want** the feature hierarchy (Epic → Story in JIRA, Feature → Issue in ADO, Milestone → Issue in GitHub) to be correct
**So that** work items are navigable and properly nested in all three platforms

---

## Acceptance Criteria

- [x] **AC-US2-01**: Given a feature synced to JIRA, when the Epic is viewed, then the linked Story appears as a child work item under it
- [x] **AC-US2-02**: Given a feature synced to ADO, when the Epic is viewed, then the linked Issue appears as a child work item under it
- [x] **AC-US2-03**: Given a feature synced to GitHub, when the Milestone is viewed, then the linked Issue is associated with the correct milestone

---

## Implementation

**Increment**: [0527-test-ac-checkbox-sync](../../../../../increments/0527-test-ac-checkbox-sync/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_
