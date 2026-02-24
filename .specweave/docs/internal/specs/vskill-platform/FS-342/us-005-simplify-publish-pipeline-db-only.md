---
id: US-005
feature: FS-342
title: Simplify Publish Pipeline (DB-Only)
status: not-started
priority: P2
created: 2026-02-24
project: vskill-platform
---
# US-005: Simplify Publish Pipeline (DB-Only)

**Feature**: [FS-342](./FEATURE.md)

developer
**I want** `publishSkill()` to write only to Prisma (no KV dual-write)
**So that** there's no split-brain between KV and DB

**ACs:**
- [x] AC-US5-01: `publishSkill()` removes KV `skill:{slug}` write and `addToPublishedIndex()` call
- [x] AC-US5-02: Dead KV skill functions removed: getPublishedSkill, getPublishedSkillsList, enumeratePublishedSkills, addToPublishedIndex
- [x] AC-US5-03: `_publishedCache` in data.ts removed
- [x] AC-US5-04: SUBMISSIONS_KV retained for submission lifecycle (sub/scan/hist keys)

---

## Acceptance Criteria

- [ ] **AC-US005-01**: Pending specification

---

## Implementation

**Increment**: [0342-db-first-skill-architecture](../../../../../increments/0342-db-first-skill-architecture/spec.md)

