---
id: US-004
feature: FS-531
title: Migrate Test Mocks to Shared Constants (P1)
status: completed
priority: P1
created: 2026-03-15T00:00:00.000Z
tldr: "**As a** SpecWeave developer."
project: specweave
external_tools:
  jira:
    key: SWE2E-215
  ado:
    id: 210
---

# US-004: Migrate Test Mocks to Shared Constants (P1)

**Feature**: [FS-531](./FEATURE.md)

**As a** SpecWeave developer
**I want** test files that mock npm commands to import command strings from `npm-constants.ts`
**So that** test mocks cannot silently drift from production code

---

## Acceptance Criteria

- [x] **AC-US4-01**: Given `installation-health-checker.test.ts`, when mock command strings are constructed, then they import and use constants from `npm-constants.ts`
- [x] **AC-US4-02**: Given `update.test.ts`, when mock command strings are constructed, then they import and use constants from `npm-constants.ts`
- [x] **AC-US4-03**: Given `update-robustness.test.ts`, when mock command strings are constructed, then they import and use constants from `npm-constants.ts`
- [x] **AC-US4-04**: Given all migrated test files, when the full test suite runs, then all tests pass

---

## Implementation

**Increment**: [0531-fix-test-mock-drift-prevention](../../../../../increments/0531-fix-test-mock-drift-prevention/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_
