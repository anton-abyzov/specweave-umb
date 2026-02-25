---
id: US-002
feature: FS-367
title: Expanded Retry Budget with Exponential Backoff
status: complete
priority: P1
created: 2026-02-24
project: vskill-platform
external:
  github:
    issue: 1313
    url: https://github.com/anton-abyzov/specweave/issues/1313
---
# US-002: Expanded Retry Budget with Exponential Backoff

**Feature**: [FS-367](./FEATURE.md)

platform operator
**I want** stuck submissions retried up to 3 times with increasing backoff windows
**So that** transient failures have multiple chances to resolve before permanent rejection

---

## Acceptance Criteria

- [x] **AC-US2-01**: Retry count stored in existing KV key `recovery:retried:{submissionId}` as integer string ("1", "2", "3")
- [x] **AC-US2-04**: After 3 retries exhausted, submission marked REJECTED with descriptive message
- [x] **AC-US2-05**: KV key has 24-hour TTL for automatic cleanup

---

## Implementation

**Increment**: [0367-stuck-submission-detection](../../../../../increments/0367-stuck-submission-detection/spec.md)

