---
id: US-001
feature: FS-492
title: "No-args init uses CWD explicitly (P1)"
status: completed
priority: P1
created: 2026-03-11T00:00:00.000Z
tldr: "**As a** developer."
project: specweave
external:
  github:
    issue: 1544
    url: https://github.com/anton-abyzov/specweave/issues/1544
---

# US-001: No-args init uses CWD explicitly (P1)

**Feature**: [FS-492](./FEATURE.md)

**As a** developer
**I want** `specweave init` with no arguments to explicitly initialize SpecWeave in my current directory
**So that** the behavior is predictable and I don't need to remember to pass `.`

---

## Acceptance Criteria

- [x] **AC-US1-01**: Running `specweave init` (no args) in a project directory creates `.specweave/` in CWD, identical to `specweave init .`
- [x] **AC-US1-02**: Running `specweave init` in the home directory is blocked with the existing safety error
- [x] **AC-US1-03**: If the CWD directory name does not match the project name pattern (`/^[a-z0-9-]+$/`), the user is prompted for a config name (existing behavior preserved)
- [x] **AC-US1-04**: Running `specweave init my-project` still creates a `my-project/` subdirectory with `.specweave/` inside it (no regression)
- [x] **AC-US1-05**: The `undefined` and `'.'` code paths in `initCommand` are unified into a single branch with a comment explaining the intent

---

## Implementation

**Increment**: [0492-init-project-resolution-redesign](../../../../../increments/0492-init-project-resolution-redesign/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-008**: Run existing test suite and verify no regressions
