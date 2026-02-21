---
id: US-002
feature: FS-292
title: KV Data Migration
status: complete
priority: P1
created: 2026-02-21
project: vskill-platform
---
# US-002: KV Data Migration

**Feature**: [FS-292](./FEATURE.md)

platform operator
**I want** existing KV records with old org-prefixed slugs to be migrated to clean slugs
**So that** previously published skills are accessible under their new clean names

---

## Acceptance Criteria

- [x] **AC-US2-01**: A migration function reads all entries from `skills:published-index`, re-keys each skill record from old slug to new slug
- [x] **AC-US2-02**: The published-index is rewritten with clean slugs
- [x] **AC-US2-03**: Old KV keys (`skill:{old-slug}`) are deleted after migration
- [x] **AC-US2-04**: Migration is idempotent -- running it twice produces the same result
- [x] **AC-US2-05**: Migration handles collisions (two old records mapping to the same new slug) by keeping the most recent one

---

## Implementation

**Increment**: [0292-skill-naming-strip-prefix](../../../../../increments/0292-skill-naming-strip-prefix/spec.md)

