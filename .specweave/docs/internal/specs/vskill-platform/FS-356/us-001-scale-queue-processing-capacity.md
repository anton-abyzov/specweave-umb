---
id: US-001
feature: FS-356
title: Scale Queue Processing Capacity
status: complete
priority: P1
created: 2026-02-25
project: vskill-platform
external:
  github:
    issue: 1358
    url: https://github.com/anton-abyzov/specweave/issues/1358
---
# US-001: Scale Queue Processing Capacity

**Feature**: [FS-356](./FEATURE.md)

platform operator
**I want** the queue consumer to process larger batches with higher concurrency
**So that** the pipeline can handle thousands of submissions per hour instead of hundreds

---

## Acceptance Criteria

- [x] **AC-US1-01**: `wrangler.jsonc` queue consumer `max_batch_size` is set to 10 (was 3)
- [x] **AC-US1-02**: `wrangler.jsonc` queue consumer `max_concurrency` is set to 20 (was 10)
- [x] **AC-US1-03**: No other queue config values are changed (max_retries, max_batch_timeout, retry_delay, dead_letter_queue remain unchanged)

---

## Implementation

**Increment**: [0356-scale-queue-throughput](../../../../../increments/0356-scale-queue-throughput/spec.md)

