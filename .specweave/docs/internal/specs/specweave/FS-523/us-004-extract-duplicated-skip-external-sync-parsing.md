---
id: US-004
feature: FS-523
title: "Extract Duplicated SKIP_EXTERNAL_SYNC Parsing"
status: not_started
priority: P1
created: 2026-03-14
tldr: "**As a** SpecWeave maintainer."
project: specweave
---

# US-004: Extract Duplicated SKIP_EXTERNAL_SYNC Parsing

**Feature**: [FS-523](./FEATURE.md)

**As a** SpecWeave maintainer
**I want** the SKIP_EXTERNAL_SYNC env var parsing to exist in one place
**So that** future changes to the parsing logic only need one update

---

## Acceptance Criteria

- [ ] **AC-US4-01**: Given `living-docs-sync.ts`, when searching for the SKIP_EXTERNAL_SYNC parsing pattern (`['true', '1', 'yes'].includes`), then it appears exactly once (extracted to a single check near the top of `syncIncrement`)
- [ ] **AC-US4-02**: Given both the cross-project and single-project sync paths, when SKIP_EXTERNAL_SYNC is set to "true", then both paths skip external sync (behavior preserved)

---

## Implementation

**Increment**: [0523-living-docs-sync-cleanup](../../../../../increments/0523-living-docs-sync-cleanup/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [ ] **T-007**: Run full test suite and confirm all grep invariants
