---
id: US-001
feature: FS-342
title: Schema Migration & DB Seed
status: not-started
priority: P2
created: 2026-02-24
project: vskill-platform
---
# US-001: Schema Migration & DB Seed

**Feature**: [FS-342](./FEATURE.md)

platform operator
**I want** all 118 seed skills stored in the Prisma DB with full data
**So that** the DB is the single source of truth for all skills

**ACs:**
- [x] AC-US1-01: Prisma schema has new columns: extensible, extensibilityTier, extensionPoints, source
- [x] AC-US1-02: DB indexes added for githubStars DESC, trustScore DESC, createdAt DESC, author
- [x] AC-US1-03: Idempotent seed script upserts all 118 skills into DB with full data (stars, downloads, trending, cert info)
- [x] AC-US1-04: After seed, `SELECT COUNT(*) FROM "Skill"` returns ~133 (118 seed + existing community)
- [x] AC-US1-05: search_vector trigger populates tsvector for all seeded skills (full-text searchable)

---

## Acceptance Criteria

- [ ] **AC-US001-01**: Pending specification

---

## Implementation

**Increment**: [0342-db-first-skill-architecture](../../../../../increments/0342-db-first-skill-architecture/spec.md)

