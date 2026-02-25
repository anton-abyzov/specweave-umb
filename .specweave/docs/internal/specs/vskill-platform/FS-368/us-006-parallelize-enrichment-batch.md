---
id: US-006
feature: FS-368
title: Parallelize Enrichment Batch
status: complete
priority: P2
created: 2026-02-24
project: vskill-platform
external:
  github:
    issue: 1323
    url: https://github.com/anton-abyzov/specweave/issues/1323
---
# US-006: Parallelize Enrichment Batch

**Feature**: [FS-368](./FEATURE.md)

platform operator
**I want** the enrichment cron to process skills in parallel chunks
**So that** total cron execution time is reduced ~5x

---

## Acceptance Criteria

- [x] **AC-US6-01**: Skills are processed in chunks of 10 using `Promise.allSettled`
- [x] **AC-US6-02**: Error counting remains accurate per-skill
- [x] **AC-US6-03**: Trending score recomputation still runs after all chunks complete

---

## Implementation

**Increment**: [0368-queue-per-item-latency](../../../../../increments/0368-queue-per-item-latency/spec.md)

