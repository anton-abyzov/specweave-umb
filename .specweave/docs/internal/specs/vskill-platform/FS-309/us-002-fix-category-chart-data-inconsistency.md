---
id: US-002
feature: FS-309
title: Fix Category Chart Data Inconsistency
status: complete
priority: P1
created: 2026-02-22
project: vskill-platform
external:
  github:
    issue: 1259
    url: https://github.com/anton-abyzov/specweave/issues/1259
---
# US-002: Fix Category Chart Data Inconsistency

**Feature**: [FS-309](./FEATURE.md)

visitor viewing the "Skills by Category" chart
**I want** the chart to reflect the total number of skills in the registry
**So that** the chart counts match the total skills number shown in the hero

---

## Acceptance Criteria

- [x] **AC-US2-01**: `getSkillCategories()` returns counts from seed + Prisma DB (not seed-only when DB is available)
- [x] **AC-US2-02**: Category chart sum equals the total skills count shown in the hero section
- [x] **AC-US2-03**: When Prisma is unavailable, fallback behavior (seed + KV) still works correctly
- [x] **AC-US2-04**: Existing tests pass and new tests cover the DB-merged category counts

---

## Implementation

**Increment**: [0309-homepage-improvements](../../../../../increments/0309-homepage-improvements/spec.md)

