---
id: US-001
feature: FS-495
title: "Dynamic Heartbeat SSE Helper"
status: completed
priority: P1
created: "2026-03-11T00:00:00.000Z"
tldr: "**As a** backend developer."
project: vskill
---

# US-001: Dynamic Heartbeat SSE Helper

**Feature**: [FS-495](./FEATURE.md)

**As a** backend developer
**I want** a `startDynamicHeartbeat()` SSE helper with imperative `update()`/`stop()` methods
**So that** long-running endpoints can change their progress message mid-flight without restarting the heartbeat timer

---

## Acceptance Criteria

- [x] **AC-US1-01**: Given a response stream, when `startDynamicHeartbeat(res, intervalMs)` is called, then it returns an object with `update(data)` and `stop()` methods
- [x] **AC-US1-02**: Given a running dynamic heartbeat, when `update({ phase, message, eval_id })` is called, then subsequent heartbeat ticks emit the updated phase and message
- [x] **AC-US1-03**: Given a running dynamic heartbeat, when `stop()` is called, then the interval timer is cleared and no further SSE events are emitted
- [x] **AC-US1-04**: Given the new helper is exported from `sse-helpers.ts`, when other modules import it, then the existing `withHeartbeat()` function remains available and unchanged

---

## Implementation

**Increment**: [0495-comparison-progress-observability](../../../../../increments/0495-comparison-progress-observability/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-001**: Implement `startDynamicHeartbeat()` in sse-helpers.ts
- [x] **T-002**: Verify `withHeartbeat()` remains unchanged (regression guard)
