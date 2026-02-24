---
id: US-004
feature: FS-355
title: Cron Observability & Independence
status: complete
priority: P1
created: 2026-02-24
project: vskill-platform
---
# US-004: Cron Observability & Independence

**Feature**: [FS-355](./FEATURE.md)

platform operator
**I want** stats refresh to run independently and with timing logs
**So that** I can diagnose cron failures and ensure stats refresh isn't blocked by other tasks

---

## Acceptance Criteria

- [x] **AC-US4-01**: `refreshPlatformStats` runs in its own `ctx.waitUntil` block, independent of the sequential cron chain
- [x] **AC-US4-02**: Enrichment and stats-refresh steps have timing logs in the cron handler
- [x] **AC-US4-03**: KV `put()` calls remove `expirationTtl` — data persists indefinitely, staleness tracked via `updatedAt`

---

## Implementation

**Increment**: [0355-fix-homepage-zero-stats](../../../../../increments/0355-fix-homepage-zero-stats/spec.md)

