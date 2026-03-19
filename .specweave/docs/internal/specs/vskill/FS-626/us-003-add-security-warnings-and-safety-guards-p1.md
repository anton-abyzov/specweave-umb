---
id: US-003
feature: FS-626
title: Add Security Warnings and Safety Guards (P1)
status: completed
priority: P1
created: 2026-03-19T00:00:00.000Z
tldr: "**As a** developer deploying to the App Store."
project: vskill
external_tools:
  jira:
    key: SWE2E-739
  ado:
    id: 1578
---

# US-003: Add Security Warnings and Safety Guards (P1)

**Feature**: [FS-626](./FEATURE.md)

**As a** developer deploying to the App Store
**I want** security warnings for sensitive operations
**So that** I don't accidentally leak credentials or make irreversible changes

---

## Acceptance Criteria

- [x] **AC-US3-01**: `--confirm` flag added to all destructive operations (submit, revoke, expire, phased-release complete)
- [x] **AC-US3-02**: Certificate revocation blast radius warning added
- [x] **AC-US3-03**: Phased release COMPLETE irreversibility warning added
- [x] **AC-US3-04**: .p8 key security warnings (chmod 600, .gitignore, shell history)
- [x] **AC-US3-05**: `ASC_DEBUG=api` CI security warning added
- [x] **AC-US3-06**: API key role guidance recommends App Manager minimum
- [x] **AC-US3-07**: App Privacy declaration requirement warning added
- [x] **AC-US3-08**: Export compliance note added

---

## Implementation

**Increment**: [0626-fix-appstore-skill-md](../../../../../increments/0626-fix-appstore-skill-md/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_
