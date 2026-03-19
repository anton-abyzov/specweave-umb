---
id: US-002
feature: FS-626
title: Add Variable Capture Patterns (P1)
status: completed
priority: P1
created: 2026-03-19T00:00:00.000Z
tldr: "**As a** developer following the skill's instructions."
project: vskill
external_tools:
  jira:
    key: SWE2E-738
  ado:
    id: 1577
---

# US-002: Add Variable Capture Patterns (P1)

**Feature**: [FS-626](./FEATURE.md)

**As a** developer following the skill's instructions
**I want** `$BUILD_ID` and `$VERSION_ID` to be captured before use
**So that** subsequent commands using these variables actually work

---

## Acceptance Criteria

- [x] **AC-US2-01**: `$BUILD_ID` capture pattern added using `jq -r '.id'` after build list/latest
- [x] **AC-US2-02**: `$VERSION_ID` capture pattern added after version create/list
- [x] **AC-US2-03**: Submit mode captures `$VERSION_ID` before using it

---

## Implementation

**Increment**: [0626-fix-appstore-skill-md](../../../../../increments/0626-fix-appstore-skill-md/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_
