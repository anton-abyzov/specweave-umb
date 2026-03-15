---
id: US-003
feature: FS-531
title: Migrate Production Code to Shared Constants (P0)
status: completed
priority: P1
created: 2026-03-15T00:00:00.000Z
tldr: "**As a** SpecWeave developer."
project: specweave
external_tools:
  jira:
    key: SWE2E-214
  ado:
    id: 209
---

# US-003: Migrate Production Code to Shared Constants (P0)

**Feature**: [FS-531](./FEATURE.md)

**As a** SpecWeave developer
**I want** all production files that hardcode the npm registry URL to import from `npm-constants.ts`
**So that** future registry URL changes propagate automatically

---

## Acceptance Criteria

- [x] **AC-US3-01**: Given `src/core/doctor/checkers/installation-health-checker.ts`, when the npm install command is built, then it uses the imported constant instead of a hardcoded registry string
- [x] **AC-US3-02**: Given `src/cli/commands/update.ts`, when the npm update command is built, then it uses the imported constant
- [x] **AC-US3-03**: Given `src/utils/docs-preview/package-installer.ts`, when the npm install command is built, then it uses the imported constant
- [x] **AC-US3-04**: Given `src/core/fabric/discovery/npm-provider.ts`, when the registry URL is referenced, then it uses the imported constant
- [x] **AC-US3-05**: Given all 4 production files after migration, when the test suite runs, then all existing tests pass with no behavior change

---

## Implementation

**Increment**: [0531-fix-test-mock-drift-prevention](../../../../../increments/0531-fix-test-mock-drift-prevention/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-011**: Final completeness check and full suite regression
