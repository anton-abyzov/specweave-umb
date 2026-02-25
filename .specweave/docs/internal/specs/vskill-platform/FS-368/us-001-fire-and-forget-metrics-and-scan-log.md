---
id: US-001
feature: FS-368
title: Fire-and-Forget Metrics and Scan Log
status: complete
priority: P1
created: 2026-02-24
project: vskill-platform
external:
  github:
    issue: 1318
    url: https://github.com/anton-abyzov/specweave/issues/1318
---
# US-001: Fire-and-Forget Metrics and Scan Log

**Feature**: [FS-368](./FEATURE.md)

platform operator
**I want** metrics and scan log recording to not block message acknowledgment
**So that** per-item processing latency is reduced by ~400-700ms

---

## Acceptance Criteria

- [x] **AC-US1-01**: `recordProcessed`, `recordFailed`, `recordTimeout` calls in `consumer.ts` are fire-and-forget (no `await`)
- [x] **AC-US1-02**: `writeScanLog` calls in `consumer.ts` are fire-and-forget (no `await`)
- [x] **AC-US1-03**: All fire-and-forget calls have `.catch(() => {})` to suppress unhandled rejections
- [x] **AC-US1-04**: Message `ack()`/`retry()` happens immediately after processing, not after telemetry

---

## Implementation

**Increment**: [0368-queue-per-item-latency](../../../../../increments/0368-queue-per-item-latency/spec.md)

