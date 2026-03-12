---
id: US-002
feature: FS-490
title: Consistent documentation
status: complete
priority: P1
created: 2026-03-11
project: specweave
---
# US-002: Consistent documentation

**Feature**: [FS-490](./FEATURE.md)

developer reading SpecWeave docs
**I want** all docs to agree that the first increment is `0001`
**So that** I am not confused by conflicting information

---

## Acceptance Criteria

- [x] **AC-US2-01**: `docs-site/docs/quick-start.md` no longer references `0001-project-setup` in the init output tree
- [x] **AC-US2-02**: `docs-site/docs/quick-start.md` shows the first user-created increment as `0001-*` (not `0002-*`)
- [x] **AC-US2-03**: `docs-site/docs/glossary/terms/greenfield.md` no longer uses `0001-project-setup-and-auth` as a system-reserved example
- [x] **AC-US2-04**: No doc file under `docs-site/` implies that init creates an increment

---

## Implementation

**Increment**: [0490-remove-init-increment-reservation](../../../../../increments/0490-remove-init-increment-reservation/spec.md)

