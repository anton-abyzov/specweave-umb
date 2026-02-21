---
id: US-003
feature: FS-296
title: Accurate Category Counts Including KV Skills
status: complete
priority: P2
created: 2026-02-21
project: vskill-platform
---
# US-003: Accurate Category Counts Including KV Skills

**Feature**: [FS-296](./FEATURE.md)

user viewing the "Skills by Category" chart on the homepage
**I want** the category counts to include community-published skills from KV
**So that** the development category count reflects the actual number of skills

---

## Acceptance Criteria

- [x] **AC-US3-01**: `getSkillCategories()` merges published KV skills into category counts (using each skill's category, defaulting to "development")
- [x] **AC-US3-02**: Seed-data skills that overlap with KV-published slugs are not double-counted
- [x] **AC-US3-03**: When KV is unavailable (build time), the function falls back gracefully to seed-data-only counts

---

## Implementation

**Increment**: [0296-strip-prefix-rollout-fixes](../../../../../increments/0296-strip-prefix-rollout-fixes/spec.md)

