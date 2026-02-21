---
id: US-001
feature: FS-292
title: Clean Skill Slug Generation
status: complete
priority: P1
created: 2026-02-21
project: vskill-platform
---
# US-001: Clean Skill Slug Generation

**Feature**: [FS-292](./FEATURE.md)

platform user browsing the skill registry
**I want** skills to be named by their clean skill name (e.g. `sw-frontend`) rather than org/repo-prefixed slugs (e.g. `anton-abyzov-specweave-sw-frontend`)
**So that** skill names are concise, human-readable, and consistent with community norms (skills.sh)

---

## Acceptance Criteria

- [x] **AC-US1-01**: `makeSlug()` returns the clean base name only (no org/repo prefix) for newly published skills
- [x] **AC-US1-02**: Collision handling: if two skills from different repos share the same base name, a disambiguating suffix is added (e.g. `sw-frontend-2` or `owner-sw-frontend`)
- [x] **AC-US1-03**: `getPublishedSkill()` correctly resolves skills by their new clean slugs
- [x] **AC-US1-04**: Published index uses clean slugs for dedup and lookup

---

## Implementation

**Increment**: [0292-skill-naming-strip-prefix](../../../../../increments/0292-skill-naming-strip-prefix/spec.md)

