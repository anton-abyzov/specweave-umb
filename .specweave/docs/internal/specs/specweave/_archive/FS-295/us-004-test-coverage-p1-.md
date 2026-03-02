---
id: US-004
feature: FS-295
title: "Test Coverage (P1)"
status: not_started
priority: P1
created: 2026-02-21
tldr: "**As a** developer
**I want** unit tests for the reorganization logic
**So that** the migration is reliable and edge cases are handled."
project: specweave
---

# US-004: Test Coverage (P1)

**Feature**: [FS-295](./FEATURE.md)

**As a** developer
**I want** unit tests for the reorganization logic
**So that** the migration is reliable and edge cases are handled

---

## Acceptance Criteria

- [ ] **AC-US4-01**: Unit tests cover: project detection from spec.md, dry-run plan generation, folder move operations, config update, idempotency
- [ ] **AC-US4-02**: Unit tests cover edge cases: no project field, cross-project specs, assets subfolder preservation, already-reorganized state
- [ ] **AC-US4-03**: Tests use Vitest + vi.mock() pattern
- [ ] **AC-US4-04**: Coverage for new reorganization module reaches 80%+

---

## Implementation

**Increment**: [0295-multi-repo-docs-restructuring](../../../../../increments/0295-multi-repo-docs-restructuring/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_
