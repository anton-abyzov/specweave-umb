---
id: US-004
feature: FS-368
title: Parallelize getMetricsWindow Reads
status: complete
priority: P2
created: 2026-02-24
project: vskill-platform
external:
  github:
    issue: 1321
    url: https://github.com/anton-abyzov/specweave/issues/1321
---
# US-004: Parallelize getMetricsWindow Reads

**Feature**: [FS-368](./FEATURE.md)

platform operator
**I want** the admin dashboard metrics to load faster
**So that** the 24 sequential KV reads are parallelized

---

## Acceptance Criteria

- [x] **AC-US4-01**: `getMetricsWindow` uses `Promise.all` instead of sequential loop for 24 hourly bucket reads
- [x] **AC-US4-02**: Totals read is included in the parallel batch

---

## Implementation

**Increment**: [0368-queue-per-item-latency](../../../../../increments/0368-queue-per-item-latency/spec.md)

