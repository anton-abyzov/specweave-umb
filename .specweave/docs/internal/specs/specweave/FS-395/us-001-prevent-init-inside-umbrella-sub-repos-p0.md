---
id: US-001
feature: FS-395
title: "Prevent Init Inside Umbrella Sub-Repos (P0)"
status: completed
priority: P1
created: 2026-03-01
tldr: "**As a** developer working in a multi-repo umbrella project."
project: specweave
---

# US-001: Prevent Init Inside Umbrella Sub-Repos (P0)

**Feature**: [FS-395](./FEATURE.md)

**As a** developer working in a multi-repo umbrella project
**I want** `specweave init` to refuse to initialize inside a sub-repository that belongs to an already-initialized umbrella
**So that** I don't create orphaned `.specweave/` folders that conflict with the umbrella's management

---

## Acceptance Criteria

- [x] **AC-US1-01**: When `specweave init` is run inside a directory that has a parent `.specweave/config.json` with umbrella indicators (repository.umbrellaRepo set, or sibling `repositories/` dir exists), init MUST refuse and show an error message explaining the umbrella relationship
- [x] **AC-US1-02**: The error message MUST suggest running init in the umbrella root or using `--force` to override
- [x] **AC-US1-03**: When `--force` flag is passed, the umbrella sub-repo check MUST be bypassed with a warning
- [x] **AC-US1-04**: The existing `detectNestedSpecweave()` parent-walking logic MUST be reused (no duplication)

---

## Implementation

**Increment**: [0395-init-location-guard-rails](../../../../../increments/0395-init-location-guard-rails/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-001**: Add detectUmbrellaParent() to path-utils.ts
- [x] **T-002**: Integrate umbrella guard into init.ts
- [x] **T-005**: Build, test, verify
