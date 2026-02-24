---
id: US-003
feature: FS-342
title: Pre-Computed Platform Stats
status: not-started
priority: P2
created: 2026-02-24
project: vskill-platform
---
# US-003: Pre-Computed Platform Stats

**Feature**: [FS-342](./FEATURE.md)

homepage visitor
**I want** stats (total skills, stars, downloads, categories) to load instantly
**So that** the homepage doesn't recompute everything on each visit

**ACs:**
- [x] AC-US3-01: `computePlatformStats()` uses DB aggregate queries (COUNT, GROUP BY, SUM, raw SQL for deduped stars)
- [x] AC-US3-02: Stats stored in KV key `platform:stats` with 2h TTL
- [x] AC-US3-03: `getPlatformStats()` reads KV blob, falls back to live computation if missing
- [x] AC-US3-04: Homepage uses pre-computed stats — no `getSkills()` full-load
- [x] AC-US3-05: `/api/v1/stats` returns KV-cached stats — no in-memory iteration

---

## Acceptance Criteria

- [ ] **AC-US003-01**: Pending specification

---

## Implementation

**Increment**: [0342-db-first-skill-architecture](../../../../../increments/0342-db-first-skill-architecture/spec.md)

