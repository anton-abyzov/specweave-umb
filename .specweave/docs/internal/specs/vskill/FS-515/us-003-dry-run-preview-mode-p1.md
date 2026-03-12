---
id: US-003
feature: FS-515
title: "Dry-run preview mode (P1)"
status: completed
priority: P1
created: 2026-03-12T00:00:00.000Z
tldr: "**As a** developer."
project: vskill
---

# US-003: Dry-run preview mode (P1)

**Feature**: [FS-515](./FEATURE.md)

**As a** developer
**I want** a `--dry-run` flag to preview what would change without actually writing the file
**So that** I can verify before committing

---

## Acceptance Criteria

- [x] **AC-US3-01**: Given there are pending additions and updates, when the user runs `vskill marketplace sync --dry-run`, then the summary table is printed but marketplace.json is not modified on disk
- [x] **AC-US3-02**: Given `--dry-run` is active, when the command completes, then the output includes a line indicating no files were written (e.g., "dry run -- no changes written")

---

## Implementation

**Increment**: [0515-vskill-marketplace-sync](../../../../../increments/0515-vskill-marketplace-sync/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-003**: Write failing tests for `marketplaceCommand()` (TDD RED)
- [x] **T-004**: Implement `src/commands/marketplace.ts` and register command in `src/index.ts` (TDD GREEN)
- [x] **T-005**: TDD REFACTOR -- full suite, build, smoke test
