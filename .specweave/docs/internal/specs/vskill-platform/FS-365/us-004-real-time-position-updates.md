---
id: US-004
feature: FS-365
title: Real-Time Position Updates
status: complete
priority: P1
created: 2026-02-24
project: vskill-platform
external:
  github:
    issue: 1337
    url: https://github.com/anton-abyzov/specweave/issues/1337
---
# US-004: Real-Time Position Updates

**Feature**: [FS-365](./FEATURE.md)

**As a** user watching the queue,
**I want** positions to update automatically as items are processed.

---

## Acceptance Criteria

- [x] **AC-US4-01**: On SSE state_changed/scan_complete events, positions refresh automatically
- [x] **AC-US4-02**: Polling fallback refreshes positions every 30s when SSE disconnects

---

## Implementation

**Increment**: [0365-queue-position-ux](../../../../../increments/0365-queue-position-ux/spec.md)

## Tasks

_Completed_
