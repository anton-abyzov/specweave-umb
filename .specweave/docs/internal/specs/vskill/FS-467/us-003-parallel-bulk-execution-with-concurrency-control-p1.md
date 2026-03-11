---
id: US-003
feature: FS-467
title: "Parallel Bulk Execution with Concurrency Control (P1)"
status: completed
priority: P1
created: 2026-03-10
tldr: "**As a** skill developer."
project: vskill
external:
  github:
    issue: 55
    url: https://github.com/anton-abyzov/vskill/issues/55
---

# US-003: Parallel Bulk Execution with Concurrency Control (P1)

**Feature**: [FS-467](./FEATURE.md)

**As a** skill developer
**I want** to run all test cases in parallel (with a concurrency limit) instead of sequentially
**So that** bulk benchmark runs complete faster while not overwhelming the LLM provider

---

## Acceptance Criteria

- [x] **AC-US3-01**: Given a "Run All" action, when executed, then all cases transition to "queued" state and begin executing in parallel up to the concurrency limit (default: 3 concurrent cases)
- [x] **AC-US3-02**: Given 5 cases and concurrency limit of 3, when bulk run starts, then 3 cases are in "running" state and 2 are in "queued" state; as running cases complete, queued cases start
- [x] **AC-US3-03**: Given a Semaphore class in `concurrency.ts`, when multiple cases attempt to acquire, then at most N cases execute simultaneously, and others wait until a slot is released
- [x] **AC-US3-04**: Given a bulk run in progress, when all cases have completed (via `Promise.allSettled`), then the bulk run is marked complete and a summary result is assembled from all individual case results
- [x] **AC-US3-05**: Given a case that errors during a bulk run, then other cases continue executing (no fail-fast behavior)

---

## Implementation

**Increment**: [0467-parallel-per-case-benchmark](../../../../../increments/0467-parallel-per-case-benchmark/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-006**: Implement `BULK_RUN_START` and `BULK_RUN_COMPLETE` reducer actions
- [x] **T-007**: Implement `runAll()` with server-side semaphore-limited parallel execution
- [x] **T-008**: Implement per-case status transitions (queued → running → complete/error)
