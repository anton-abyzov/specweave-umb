---
id: US-002
feature: FS-532
title: Eliminate PostToolUse Edit Hook Timeout Errors (P1)
status: completed
priority: P2
created: 2026-03-15T00:00:00.000Z
tldr: "**As a** SpecWeave user."
project: specweave
external:
  github:
    issue: 1574
    url: https://github.com/anton-abyzov/specweave/issues/1574
external_tools:
  jira:
    key: SWE2E-226
  ado:
    id: 208
---

# US-002: Eliminate PostToolUse Edit Hook Timeout Errors (P1)

**Feature**: [FS-532](./FEATURE.md)

**As a** SpecWeave user
**I want** PostToolUse hooks to complete within their timeout budget
**So that** I don't see "PostToolUse:Edit hook error" warnings on every edit

---

## Acceptance Criteria

- [x] **AC-US2-01**: `fail-fast-wrapper.sh` has a 15s timeout override for `post-tool-use.sh`
- [x] **AC-US2-02**: `task-ac-sync-guard.sh` runs in background (non-blocking) instead of synchronously
- [x] **AC-US2-03**: Editing a `.specweave/increments/*/tasks.md` file produces no PostToolUse timeout warnings
- [x] **AC-US2-04**: AC sync from tasks.md to spec.md still works correctly after backgrounding

---

## Implementation

**Increment**: [0532-fix-hook-timeout-errors](../../../../../increments/0532-fix-hook-timeout-errors/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_
