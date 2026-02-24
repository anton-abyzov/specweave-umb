---
id: US-002
feature: FS-342
title: DB-Only Data Layer
status: not-started
priority: P2
created: 2026-02-24
project: vskill-platform
---
# US-002: DB-Only Data Layer

**Feature**: [FS-342](./FEATURE.md)

developer
**I want** `getSkills()` to be a pure DB query with no in-memory merge
**So that** filtering, sorting, and pagination happen at the DB level

**ACs:**
- [x] AC-US2-01: `getSkills()` uses Prisma WHERE/ORDER BY/SKIP/TAKE — no seed-data.ts import
- [x] AC-US2-02: `getSkillByName()` is a single `db.skill.findUnique()` — no seed lookup
- [x] AC-US2-03: `getSkillCategories()` uses `db.skill.groupBy()` — no in-memory counting
- [x] AC-US2-04: New `getSkillCount(filters)` function uses `db.skill.count()` for pagination totals
- [x] AC-US2-05: `getTrendingSkills()` uses DB query with ORDER BY trendingScore7d DESC
- [x] AC-US2-06: `mapDbSkillToSkillData()` maps new fields: extensible, extensibilityTier, extensionPoints
- [x] AC-US2-07: Build-time fallback: if DB unreachable during `next build`, falls back to seed-data.ts

---

## Acceptance Criteria

- [ ] **AC-US002-01**: Pending specification

---

## Implementation

**Increment**: [0342-db-first-skill-architecture](../../../../../increments/0342-db-first-skill-architecture/spec.md)

