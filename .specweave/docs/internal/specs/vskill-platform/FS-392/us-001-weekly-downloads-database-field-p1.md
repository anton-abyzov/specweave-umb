---
id: US-001
feature: FS-392
title: "Weekly Downloads Database Field (P1)"
status: completed
priority: P1
created: 2026-03-01T00:00:00.000Z
tldr: "**As a** platform operator."
project: vskill-platform
---

# US-001: Weekly Downloads Database Field (P1)

**Feature**: [FS-392](./FEATURE.md)

**As a** platform operator
**I want** a dedicated `npmDownloadsWeekly` integer field on the Skill model
**So that** weekly download counts are stored separately from monthly without affecting the trending formula

---

## Acceptance Criteria

- [x] **AC-US1-01**: Prisma schema has `npmDownloadsWeekly Int @default(0)` on the `Skill` model alongside existing `npmDownloads`
- [x] **AC-US1-02**: A Prisma migration adds the column with default 0 (no data loss on existing rows)
- [x] **AC-US1-03**: `MetricsSnapshot` model includes `npmDownloadsWeekly Int @default(0)` for historical tracking
- [x] **AC-US1-04**: `SkillData` type in `src/lib/types.ts` includes `npmDownloadsWeekly: number`

---

## Implementation

**Increment**: [0392-npm-weekly-downloads](../../../../../increments/0392-npm-weekly-downloads/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-001**: Add npmDownloadsWeekly to Prisma schema and run migration
- [x] **T-002**: Add npmDownloadsWeekly to SkillData type and data layer mapping
