---
id: US-001
feature: FS-532
title: Eliminate PreToolUse Edit Hook Errors (P1)
status: completed
priority: P2
created: 2026-03-15T00:00:00.000Z
tldr: "**As a** SpecWeave user."
project: specweave
external:
  github:
    issue: 1573
    url: https://github.com/anton-abyzov/specweave/issues/1573
external_tools:
  jira:
    key: SWE2E-225
  ado:
    id: 194
---

# US-001: Eliminate PreToolUse Edit Hook Errors (P1)

**Feature**: [FS-532](./FEATURE.md)

**As a** SpecWeave user
**I want** PreToolUse hooks to not crash on Edit operations
**So that** I don't see noisy "PreToolUse:Edit hook error" warnings on every edit

---

## Acceptance Criteria

- [x] **AC-US1-01**: `pre-tool-use.sh` uses `set +e` instead of `set -e`, matching all other hook scripts
- [x] **AC-US1-02**: Editing a `.specweave/increments/*/tasks.md` file produces no PreToolUse error warnings

---

## Implementation

**Increment**: [0532-fix-hook-timeout-errors](../../../../../increments/0532-fix-hook-timeout-errors/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-004**: Refresh plugin cache
