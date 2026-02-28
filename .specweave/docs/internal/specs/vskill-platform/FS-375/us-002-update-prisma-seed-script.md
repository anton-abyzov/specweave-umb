---
id: US-002
feature: FS-375
title: Update Prisma seed script
status: complete
priority: P1
created: 2026-02-28
project: vskill-platform
---
# US-002: Update Prisma seed script

**Feature**: [FS-375](./FEATURE.md)

platform developer
**I want** the Prisma seed script updated to only seed admins, blocklist, and agent compat data
**So that** running `prisma db seed` no longer inserts fake skills into the database

---

## Acceptance Criteria

- [x] **AC-US2-01**: `prisma/seed.ts` no longer imports `skills` from the data file
- [x] **AC-US2-02**: `prisma/seed.ts` imports `agents` from `../src/lib/agent-data`
- [x] **AC-US2-03**: The skill upsert loop and skill version creation are removed from seed.ts
- [x] **AC-US2-04**: The `SKILL_NAME_RENAMES` migration map is removed (no longer needed)
- [x] **AC-US2-05**: Admin seeding and blocklist seeding continue to work unchanged
- [x] **AC-US2-06**: Agent compat records can still be seeded against existing DB skills (not fake ones)

---

## Implementation

**Increment**: [0375-remove-fake-seed-data](../../../../../increments/0375-remove-fake-seed-data/spec.md)

