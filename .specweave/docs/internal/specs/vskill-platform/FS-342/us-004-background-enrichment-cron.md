---
id: US-004
feature: FS-342
title: Background Enrichment Cron
status: not-started
priority: P2
created: 2026-02-24
project: vskill-platform
---
# US-004: Background Enrichment Cron

**Feature**: [FS-342](./FEATURE.md)

platform operator
**I want** skill metrics (GitHub stars, npm downloads) updated automatically
**So that** the DB has fresh data and trending scores reflect reality

**ACs:**
- [x] AC-US4-01: Enrichment batch job selects 20 oldest-refreshed skills, fetches GitHub + npm metrics, writes to DB
- [x] AC-US4-02: Trending scores recomputed based on actual star/download data
- [x] AC-US4-03: Stats refresh runs after enrichment, updates KV blob
- [x] AC-US4-04: Integrated into existing hourly cron handler

---

## Acceptance Criteria

- [ ] **AC-US004-01**: Pending specification

---

## Implementation

**Increment**: [0342-db-first-skill-architecture](../../../../../increments/0342-db-first-skill-architecture/spec.md)

