---
id: US-002
feature: FS-390
title: "Test coverage for GitHub source registration (P1)"
status: completed
priority: P1
created: 2026-02-28
tldr: "**As a** maintainer."
project: vskill
---

# US-002: Test coverage for GitHub source registration (P1)

**Feature**: [FS-390](./FEATURE.md)

**As a** maintainer
**I want** tests to verify the correct marketplace source is registered
**So that** regressions are caught before release

---

## Acceptance Criteria

- [x] **AC-US2-01**: `claude-cli.test.ts` tests for `registerMarketplace()` include a case with GitHub `owner/repo` format input
- [x] **AC-US2-02**: `add.test.ts` marketplace integration tests assert that `registerMarketplace` is called with `owner/repo` (not a temp dir path) when installing from a GitHub marketplace repo
- [x] **AC-US2-03**: Existing `registerMarketplace` tests for local paths and paths-with-spaces continue to pass (no regression)

---

## Implementation

**Increment**: [0390-fix-marketplace-source-registration](../../../../../increments/0390-fix-marketplace-source-registration/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-001**: RED - Write tests asserting GitHub source registration
- [x] **T-004**: Final verification
