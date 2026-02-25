---
id: US-005
feature: FS-356
title: Parallelize Discovery Submission Loop
status: complete
priority: P1
created: 2026-02-25
project: vskill-platform
---
# US-005: Parallelize Discovery Submission Loop

**Feature**: [FS-356](./FEATURE.md)

platform operator
**I want** the discovery submission loop in `runGitHubDiscovery` to process candidates in parallel batches
**So that** the enqueue phase (which is currently a sequential for-loop with per-repo dedup + HTTP call) completes faster when processing thousands of candidates

---

## Acceptance Criteria

- [x] **AC-US5-01**: The sequential `for (const candidate of allCandidates)` loop in `runGitHubDiscovery` is replaced with batched `Promise.allSettled` processing
- [x] **AC-US5-02**: Batch size is configurable via a constant (default 20 candidates per batch)
- [x] **AC-US5-03**: The `maxResults` cap is still respected -- processing stops once `enqueued >= maxResults`
- [x] **AC-US5-04**: Per-skill dedup via `hasBeenDiscovered` / `markDiscovered` still works correctly under parallelism (no duplicate submissions)
- [x] **AC-US5-05**: Error counting (`errors`) and dedup counting (`skippedDedup`) remain accurate
- [x] **AC-US5-06**: Per-repo stats logging (`repoStats`) remains functional

---

## Implementation

**Increment**: [0356-scale-queue-throughput](../../../../../increments/0356-scale-queue-throughput/spec.md)

