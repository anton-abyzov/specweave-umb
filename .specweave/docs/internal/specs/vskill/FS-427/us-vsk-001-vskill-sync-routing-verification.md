---
id: US-VSK-001
feature: FS-427
title: VSkill Sync Routing Verification
status: not_started
priority: P1
created: 2026-03-05
tldr: "**As a** developer."
project: vskill
related_projects:
  - specweave
  - vskill-platform
external:
  github:
    issue: 5
    url: https://github.com/anton-abyzov/vskill/issues/5
---

# US-VSK-001: VSkill Sync Routing Verification

**Feature**: [FS-427](./FEATURE.md)

**As a** developer
**I want** sync to route to vskill repo
**So that** GitHub issues appear in anton-abyzov/vskill

---

## Acceptance Criteria

- [ ] **AC-VSK-US1-01**: GitHub milestone created in vskill repo
- [ ] **AC-VSK-US1-02**: GitHub issue created with [FS-427][US-VSK-001] title

---

## Implementation

**Increment**: [0427-umbrella-sync-lifecycle-test](../../../../../increments/0427-umbrella-sync-lifecycle-test/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [ ] **T-001**: Verify sync-progress routes to all three repos
- [ ] **T-002**: Verify GitHub issues created per child repo
