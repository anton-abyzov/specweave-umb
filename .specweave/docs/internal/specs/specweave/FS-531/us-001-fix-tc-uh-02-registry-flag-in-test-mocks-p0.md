---
id: US-001
feature: FS-531
title: Fix TC-UH-02 Registry Flag in Test Mocks (P0)
status: completed
priority: P1
created: 2026-03-15T00:00:00.000Z
tldr: "**As a** SpecWeave developer."
project: specweave
external_tools:
  jira:
    key: SWE2E-212
  ado:
    id: 194
---

# US-001: Fix TC-UH-02 Registry Flag in Test Mocks (P0)

**Feature**: [FS-531](./FEATURE.md)

**As a** SpecWeave developer
**I want** TC-UH-02 test mocks to include the `--registry https://registry.npmjs.org` flag
**So that** the test accurately validates the production npm install command

---

## Acceptance Criteria

- [x] **AC-US1-01**: Given the `installation-health-checker.test.ts` file, when TC-UH-02 constructs a mock npm install command, then the command string includes `--registry https://registry.npmjs.org`
- [x] **AC-US1-02**: Given the corrected TC-UH-02 test, when the test suite runs, then TC-UH-02 passes without modifying production behavior

---

## Implementation

**Increment**: [0531-fix-test-mock-drift-prevention](../../../../../increments/0531-fix-test-mock-drift-prevention/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_
