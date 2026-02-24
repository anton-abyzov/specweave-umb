---
id: US-006
feature: FS-367
title: Admin Timeout Metrics
status: active
priority: P2
created: 2026-02-24
project: vskill-platform
---
# US-006: Admin Timeout Metrics

**Feature**: [FS-367](./FEATURE.md)

---

## Acceptance Criteria

- [x] **AC-US6-01**: Timeout metrics stored in existing `QUEUE_METRICS_KV` hourly buckets via `timedOut` field (backward-compatible)
- [x] **AC-US6-02**: `recordTimeout(kv, durationMs)` function increments both `failed` and `timedOut` on bucket and totals
- [x] **AC-US6-03**: Admin queue status API extended with `totalTimedOut` in throughput and `timedOut` in recentHours
- [ ] **AC-US6-04**: Hourly bucket KV keys have 48-hour TTL for automatic cleanup

---

## Implementation

**Increment**: [0367-stuck-submission-detection](../../../../../increments/0367-stuck-submission-detection/spec.md)

