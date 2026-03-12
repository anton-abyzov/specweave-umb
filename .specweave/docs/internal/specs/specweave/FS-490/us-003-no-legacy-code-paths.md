---
id: US-003
feature: FS-490
title: No legacy code paths
status: complete
priority: P2
created: 2026-03-11
project: specweave
---
# US-003: No legacy code paths

**Feature**: [FS-490](./FEATURE.md)

SpecWeave maintainer
**I want** to confirm there is no residual code that creates a `0001-project-setup` increment during init
**So that** the behavior matches the documentation

---

## Acceptance Criteria

- [x] **AC-US3-01**: No source file under `src/` contains logic to create an increment folder during the init command
- [x] **AC-US3-02**: The `createDirectoryStructure` function only creates core directories (increments/, cache/, state/, etc.) without any seed increment
- [x] **AC-US3-03**: Existing unit tests for init do not assert the existence of `0001-project-setup`

---

## Implementation

**Increment**: [0490-remove-init-increment-reservation](../../../../../increments/0490-remove-init-increment-reservation/spec.md)

