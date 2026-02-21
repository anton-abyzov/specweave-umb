---
id: US-005
feature: FS-219
title: Test Coverage
status: complete
priority: P1
created: 2026-02-21
project: specweave
external:
  github:
    issue: 1198
    url: "https://github.com/anton-abyzov/specweave/issues/1198"
---
# US-005: Test Coverage

**Feature**: [FS-219](./FEATURE.md)

developer
**I want** unit tests for the migration logic
**So that** the migration is reliable and edge cases are handled

---

## Acceptance Criteria

- [x] **AC-US5-01**: Unit tests cover: single-repo detection, dry-run plan generation, config.json path updates, backup creation, rollback
- [x] **AC-US5-02**: Unit tests cover edge cases: uncommitted changes, missing config.json, already-umbrella project, invalid org/repo extraction
- [x] **AC-US5-03**: Tests use the existing Vitest + vi.mock() pattern
- [x] **AC-US5-04**: Coverage for the new migration module reaches 80%+

---

## Implementation

**Increment**: [0219-multi-repo-migrate](../../../../../increments/0219-multi-repo-migrate/spec.md)

