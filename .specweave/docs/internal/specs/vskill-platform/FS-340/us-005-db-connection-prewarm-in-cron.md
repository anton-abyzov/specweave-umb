---
id: US-005
feature: FS-340
title: DB Connection Prewarm in Cron
status: complete
priority: P2
created: 2026-02-24
project: vskill-platform
---
# US-005: DB Connection Prewarm in Cron

**Feature**: [FS-340](./FEATURE.md)

platform operator
**I want** the hourly cron handler to prewarm the Neon DB connection
**So that** the first API request after a cold period doesn't pay the full Neon cold-start penalty

---

## Acceptance Criteria

- [x] **AC-US5-01**: The `scheduled` handler in `scripts/build-worker-entry.ts` calls `getDb()` followed by a lightweight query (e.g., `SELECT 1`) before existing cron tasks
- [x] **AC-US5-02**: Prewarm failure is caught and logged (non-blocking, does not prevent other cron tasks)
- [x] **AC-US5-03**: Prewarm runs as the first operation inside the existing `ctx.waitUntil` block

---

## Implementation

**Increment**: [0340-api-perf-optimization](../../../../../increments/0340-api-perf-optimization/spec.md)

