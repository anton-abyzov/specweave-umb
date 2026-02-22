---
id: US-001
feature: FS-310
title: Parallel KV reads in getStuckSubmissions
status: complete
priority: P1
created: 2026-02-22
project: specweave
external:
  github:
    issue: 1261
    url: https://github.com/anton-abyzov/specweave/issues/1261
---
# US-001: Parallel KV reads in getStuckSubmissions

**Feature**: [FS-310](./FEATURE.md)

platform operator running the cron-based stuck submission recovery
**I want** `getStuckSubmissions` to read all `sub:*` KV keys in parallel
**So that** stuck submission detection completes faster and does not hit wall-clock timeouts on large datasets

---

## Acceptance Criteria

- [x] **AC-US1-01**: `getStuckSubmissions` uses `Promise.allSettled` to read all `sub:*` keys concurrently instead of a sequential `for` loop
- [x] **AC-US1-02**: Individual KV read failures (rejected promises) are silently skipped, matching the existing `try/catch { /* skip malformed */ }` behavior
- [x] **AC-US1-03**: Return value and filtering logic (STUCK_STATES, STUCK_THRESHOLD_MS) remain identical to current behavior

---

## Implementation

**Increment**: [0310-parallel-kv-asynclocalstorage](../../../../../increments/0310-parallel-kv-asynclocalstorage/spec.md)

