---
id: US-003
feature: FS-306
title: Migrate getSkills() to Prisma-Primary
status: active
priority: P1
created: 2026-02-21
project: specweave
external:
  github:
    issue: 1249
    url: "https://github.com/anton-abyzov/specweave/issues/1249"
---
# US-003: Migrate getSkills() to Prisma-Primary

**Feature**: [FS-306](./FEATURE.md)

platform operator
**I want** the skills listing page to read from Prisma as the primary source
**So that** the marketplace is resilient to KV blob corruption and can leverage SQL filtering/sorting

---

## Acceptance Criteria

- [x] **AC-US3-01**: New function `getPublishedSkillsFromDb()` in `data.ts` queries `Skill` table with support for category, certTier, author, search, sorting, pagination, and extensibility filtering
- [x] **AC-US3-02**: `getSkills()` reads from Prisma if available, falls back to seed+KV if Prisma fails (e.g., at build time when no DATABASE_URL)
- [x] **AC-US3-03**: `getSkillByName()` checks Prisma before KV; returns Prisma data if found
- [x] **AC-US3-04**: `getSkillCount()` and `getSkillCategories()` also query Prisma when available
- [x] **AC-US3-05**: Seed data is still merged (not duplicated): skills that exist in seed AND Prisma use the seed data (seed is canonical for those 118 skills)
- [ ] **AC-US3-06**: Performance: Prisma query for paginated listing completes in <200ms (existing indexes on category, certTier, trendingScore7d)
- [ ] **AC-US3-07**: Unit tests mock Prisma client to verify fallback path, merge logic, and filter support

---

## Implementation

**Increment**: [0306-fix-marketplace-skill-loss](../../../../../increments/0306-fix-marketplace-skill-loss/spec.md)

