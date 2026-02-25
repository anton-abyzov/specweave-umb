---
id: US-005
feature: FS-368
title: Batch updateState for Publish Flow
status: complete
priority: P1
created: 2026-02-24
project: vskill-platform
external:
  github:
    issue: 1322
    url: https://github.com/anton-abyzov/specweave/issues/1322
---
# US-005: Batch updateState for Publish Flow

**Feature**: [FS-368](./FEATURE.md)

platform operator
**I want** sequential state transitions (AUTO_APPROVED → PUBLISHED) to be batched
**So that** 4 KV reads + 4 KV writes are reduced to 2+2

---

## Acceptance Criteria

- [x] **AC-US5-01**: New `updateStateMulti` function accepts array of `{state, message}` transitions
- [x] **AC-US5-02**: Single KV read/write cycle for submission + history
- [x] **AC-US5-03**: DB persistence fires per-transition (best-effort, as before)
- [x] **AC-US5-04**: `processSubmission` uses `updateStateMulti` for AUTO_APPROVED→PUBLISHED sequences

---

## Implementation

**Increment**: [0368-queue-per-item-latency](../../../../../increments/0368-queue-per-item-latency/spec.md)

