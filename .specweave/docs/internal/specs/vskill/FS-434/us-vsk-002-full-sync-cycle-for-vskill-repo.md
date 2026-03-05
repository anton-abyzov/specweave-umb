---
id: US-VSK-002
feature: FS-434
title: "Full Sync Cycle for VSkill Repo"
status: completed
priority: P2
created: 2026-03-05
tldr: "**As a** developer."
project: vskill
related_projects: [specweave, vskill-platform]
external:
  github:
    issue: 7
    url: https://github.com/anton-abyzov/vskill/issues/7
---

# US-VSK-002: Full Sync Cycle for VSkill Repo

**Feature**: [FS-434](./FEATURE.md)

**As a** developer
**I want** the full sync cycle to work end-to-end for vskill
**So that** vskill issues are tracked across all platforms

---

## Acceptance Criteria

- [x] **AC-VSK-US2-01**: GitHub issue created in anton-abyzov/vskill
- [x] **AC-VSK-US2-02**: JIRA ticket created in SWE2E project

---

## Implementation

**Increment**: [0434-full-sync-cycle-test](../../../../../increments/0434-full-sync-cycle-test/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-001**: Sync to GitHub for all child repos
- [x] **T-002**: Sync to JIRA for all child repos
- [x] **T-005**: Verify close flow transitions external items
