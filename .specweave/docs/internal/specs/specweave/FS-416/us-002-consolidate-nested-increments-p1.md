---
id: US-002
feature: FS-416
title: "Consolidate Nested Increments (P1)"
status: completed
priority: P1
created: 2026-03-03T00:00:00.000Z
tldr: "**As a** SpecWeave user migrating to umbrella mode."
project: specweave
---

# US-002: Consolidate Nested Increments (P1)

**Feature**: [FS-416](./FEATURE.md)

**As a** SpecWeave user migrating to umbrella mode
**I want** a CLI command that moves orphaned increments and living docs from nested repo `.specweave/` directories to the umbrella root
**So that** the umbrella root is the single source of truth for all increments across repos

---

## Acceptance Criteria

- [x] **AC-US2-01**: Given the `--consolidate` flag is passed to `migrate-to-umbrella`, when the command runs, then it scans all `repositories/*/` paths for nested `.specweave/increments/` directories
- [x] **AC-US2-02**: Given an increment exists in a nested repo but not in the umbrella root, when `--consolidate --execute` runs, then the increment directory is moved to the umbrella root `.specweave/increments/`
- [x] **AC-US2-03**: Given an increment exists in both a nested repo and the umbrella root (duplicate), when `--consolidate --execute` runs, then the umbrella root version is kept and the nested copy is removed
- [x] **AC-US2-04**: Given living doc specs exist in a nested repo's `.specweave/docs/`, when `--consolidate --execute` runs, then they are moved to the umbrella root `.specweave/docs/`
- [x] **AC-US2-05**: Given `--consolidate` is run without `--execute`, when the command runs, then it prints a dry-run plan of all planned moves and deletions without making any changes

---

## Implementation

**Increment**: [0416-umbrella-sync-consolidation](../../../../../increments/0416-umbrella-sync-consolidation/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-006**: Add --consolidate flag to migrate-to-umbrella CLI
- [x] **T-007**: Implement consolidation engine
- [x] **T-009**: Integration tests covering all ACs
- [x] **T-010**: Run consolidation and enable distributed sync in umbrella config
