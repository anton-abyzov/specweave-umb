---
id: US-VSK-001
feature: FS-425
title: "VSkill Repo Sync Verification"
status: not_started
priority: P2
created: 2026-03-04
tldr: "**As a** developer."
project: vskill
related_projects: [specweave, vskill-platform]
external:
  github:
    issue: 4
    url: https://github.com/anton-abyzov/vskill/issues/4
---

# US-VSK-001: VSkill Repo Sync Verification

**Feature**: [FS-425](./FEATURE.md)

**As a** developer
**I want** sync to route to the vskill child repo
**So that** GitHub issues go to anton-abyzov/vskill, JIRA to SWE2E, ADO to VSkillSync

---

## Acceptance Criteria

- [ ] **AC-VSK-US1-01**: GitHub issue created in anton-abyzov/vskill (not specweave-umb)
- [ ] **AC-VSK-US1-02**: JIRA ticket created in SWE2E project
- [ ] **AC-VSK-US1-03**: ADO work item created in VSkillSync project

---

## Implementation

**Increment**: [0425-umbrella-sync-e2e-test](../../../../../increments/0425-umbrella-sync-e2e-test/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-001**: Verify resolver routes all three platforms for each child repo
- [ ] **T-005**: Verify JIRA routing per child repo
- [ ] **T-006**: Verify ADO routing per child repo
