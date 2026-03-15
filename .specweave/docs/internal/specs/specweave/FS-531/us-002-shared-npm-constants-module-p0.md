---
id: US-002
feature: FS-531
title: Shared npm Constants Module (P0)
status: completed
priority: P1
created: 2026-03-15T00:00:00.000Z
tldr: "**As a** SpecWeave developer."
project: specweave
external_tools:
  jira:
    key: SWE2E-213
  ado:
    id: 208
---

# US-002: Shared npm Constants Module (P0)

**Feature**: [FS-531](./FEATURE.md)

**As a** SpecWeave developer
**I want** a shared `src/constants/npm-constants.ts` module exporting the registry URL and command-building helpers
**So that** production code and test mocks reference a single source of truth

---

## Acceptance Criteria

- [x] **AC-US2-01**: Given the new module `src/constants/npm-constants.ts`, when imported, then it exports `NPM_REGISTRY_URL` with value `https://registry.npmjs.org`
- [x] **AC-US2-02**: Given the new module, when imported, then it exports a `npmRegistryFlag()` helper that returns `--registry https://registry.npmjs.org`
- [x] **AC-US2-03**: Given the module file, when inspected, then its structure follows the same pattern as `src/utils/pricing-constants.ts`

---

## Implementation

**Increment**: [0531-fix-test-mock-drift-prevention](../../../../../increments/0531-fix-test-mock-drift-prevention/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_
