---
id: US-001
feature: FS-523
title: Fix Cross-Reference Generation Using Unfiltered Groups
status: completed
priority: P1
created: 2026-03-14
tldr: "**As a** SpecWeave user with a multi-project workspace."
project: specweave
external:
  github:
    issue: 1565
    url: https://github.com/anton-abyzov/specweave/issues/1565
---

# US-001: Fix Cross-Reference Generation Using Unfiltered Groups

**Feature**: [FS-523](./FEATURE.md)

**As a** SpecWeave user with a multi-project workspace
**I want** FEATURE.md cross-references to only link to validated projects
**So that** I do not see broken or misleading links to filtered-out placeholder projects

---

## Acceptance Criteria

- [x] **AC-US1-01**: Given a multi-project sync where `validGroups` contains 2 of 4 original groups, when `generateCrossReferences()` is called, then only the 2 validated project keys are passed (not all 4)
- [x] **AC-US1-02**: Given a project that was filtered out by the validation logic (lines 262-282), when FEATURE.md is generated for another project, then no cross-reference link to the filtered project appears

---

## Implementation

**Increment**: [0523-living-docs-sync-cleanup](../../../../../increments/0523-living-docs-sync-cleanup/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-007**: Run full test suite and confirm all grep invariants
