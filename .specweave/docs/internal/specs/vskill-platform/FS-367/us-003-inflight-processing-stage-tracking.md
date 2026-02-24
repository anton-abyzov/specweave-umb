---
id: US-003
feature: FS-367
title: Inflight Processing Stage Tracking
status: complete
priority: P1
created: 2026-02-24
project: vskill-platform
---
# US-003: Inflight Processing Stage Tracking

**Feature**: [FS-367](./FEATURE.md)

platform component
**I want** the current processing stage and timestamp tracked in KV during submission processing
**So that** the system knows exactly where a submission is stuck and can report it to users

---

## Acceptance Criteria

- [x] **AC-US3-01**: Consumer writes `inflight:{submissionId}` KV with `{ startedAt, attempt }` before processing
- [x] **AC-US3-02**: Inflight KV key deleted on success or failure (cleanup in both paths)
- [x] **AC-US3-04**: Inflight KV key has TTL of 5 minutes to auto-expire orphaned records

---

## Implementation

**Increment**: [0367-stuck-submission-detection](../../../../../increments/0367-stuck-submission-detection/spec.md)

