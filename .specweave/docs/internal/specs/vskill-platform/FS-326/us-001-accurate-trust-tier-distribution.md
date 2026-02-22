---
id: US-001
feature: FS-326
title: Accurate Trust Tier Distribution
status: complete
priority: P1
created: 2026-02-22
project: vskill-platform
---
# US-001: Accurate Trust Tier Distribution

**Feature**: [FS-326](./FEATURE.md)

Trust Center visitor
**I want** tier distribution cards to show correct counts from both seed and database skills
**So that** I can trust the security posture metrics displayed on the page

---

## Acceptance Criteria

- [x] **AC-US1-01**: Stats API computes `totalSkills` as merged count of seed skills + Prisma-only skills (no double counting of skills that exist in both)
- [x] **AC-US1-02**: Seed-only skills (not in Prisma) without a `trustTier` value count as T1 (Unscanned)
- [x] **AC-US1-03**: Prisma skills with `certTier=SCANNED` map to T2 (Scanned)
- [x] **AC-US1-04**: Prisma skills with `certTier=VERIFIED` map to T3 (Verified)
- [x] **AC-US1-05**: Prisma skills with `certTier=CERTIFIED` map to T4 (Certified)
- [x] **AC-US1-06**: Active blocklist entries (from `blocklistEntry` table where `isActive=true`) contribute to T0 count
- [x] **AC-US1-07**: Seed skills that already have `trustTier` set (e.g., "T4") use their existing value, not re-derive from certTier
- [x] **AC-US1-08**: The five tier cards (T0-T4) display updated counts immediately after API returns

---

## Implementation

**Increment**: [0326-trust-center-fixes](../../../../../increments/0326-trust-center-fixes/spec.md)

