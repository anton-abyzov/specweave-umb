---
id: US-003
feature: FS-428
title: "Clear error messages"
status: completed
priority: P2
created: "2026-03-05T00:00:00.000Z"
tldr: "**As a** plugin user."
project: vskill
---

# US-003: Clear error messages

**Feature**: [FS-428](./FEATURE.md)

**As a** plugin user
**I want** actionable error messages when install fails
**So that** I know what went wrong and how to fix it

---

## Acceptance Criteria

- [x] **AC-US3-01**: Given a plugin name that does not exist in marketplace.json, when the user runs `vskill install`, then the error message lists all available plugin names from marketplace.json
- [x] **AC-US3-02**: Given a marketplace registration failure, when the error is displayed to the user, then captured stderr from the `claude` CLI is shown in dim text below the primary error message
- [x] **AC-US3-03**: Given any marketplace validation call, when `validateMarketplace()` is invoked, then it returns a structured object with `{ valid: boolean; errors: Array<{ code: string; message: string }> }` covering specific error reasons (missing manifest, empty plugin list, invalid JSON, unreachable source)

---

## Implementation

**Increment**: [0428-plugin-install-reliability](../../../../../increments/0428-plugin-install-reliability/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_
