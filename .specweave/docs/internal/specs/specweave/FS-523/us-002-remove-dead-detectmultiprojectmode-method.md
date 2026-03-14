---
id: US-002
feature: FS-523
title: "Remove Dead detectMultiProjectMode Method"
status: not_started
priority: P1
created: 2026-03-14
tldr: "**As a** SpecWeave maintainer."
project: specweave
---

# US-002: Remove Dead detectMultiProjectMode Method

**Feature**: [FS-523](./FEATURE.md)

**As a** SpecWeave maintainer
**I want** the unused `detectMultiProjectMode` private method removed from `living-docs-sync.ts`
**So that** the file is shorter and there is no confusion about which implementation is authoritative

---

## Acceptance Criteria

- [ ] **AC-US2-01**: Given the current codebase, when searching for `detectMultiProjectMode` in `living-docs-sync.ts`, then zero definitions or calls exist in that file
- [ ] **AC-US2-02**: Given the removal, when existing tests are run, then all tests pass with no regressions

---

## Implementation

**Increment**: [0523-living-docs-sync-cleanup](../../../../../increments/0523-living-docs-sync-cleanup/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [ ] **T-007**: Run full test suite and confirm all grep invariants
