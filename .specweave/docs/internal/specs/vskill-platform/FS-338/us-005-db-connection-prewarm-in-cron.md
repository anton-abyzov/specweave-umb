---
id: US-005
feature: FS-338
title: DB Connection Prewarm in Cron
status: not-started
priority: P2
created: 2026-02-23
project: vskill-platform
---
# US-005: DB Connection Prewarm in Cron

**Feature**: [FS-338](./FEATURE.md)

platform operator
**I want** the hourly cron handler to prewarm the Neon DB connection
**So that** the first API request after a cold period doesn't pay the full Neon cold-start penalty

---

## Acceptance Criteria

- [ ] **AC-US5-01**: The `scheduled` handler in `scripts/build-worker-entry.ts` calls `getDb()` followed by a lightweight query (e.g., `SELECT 1`) before existing cron tasks
- [ ] **AC-US5-02**: Prewarm failure is caught and logged (non-blocking, does not prevent other cron tasks)
- [ ] **AC-US5-03**: Prewarm runs as the first operation inside the existing `ctx.waitUntil` block

---

## Implementation

**Increment**: [0338-api-perf-optimization](../../../../../increments/0338-api-perf-optimization/spec.md)

