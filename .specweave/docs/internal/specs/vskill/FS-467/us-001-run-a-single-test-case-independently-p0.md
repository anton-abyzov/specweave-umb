---
id: US-001
feature: FS-467
title: "Run a Single Test Case Independently (P0)"
status: completed
priority: P1
created: 2026-03-10
tldr: "**As a** skill developer."
project: vskill
external:
  github:
    issue: 53
    url: https://github.com/anton-abyzov/vskill/issues/53
---

# US-001: Run a Single Test Case Independently (P0)

**Feature**: [FS-467](./FEATURE.md)

**As a** skill developer
**I want** to run a single test case without blocking other cases or the UI
**So that** I can iterate quickly on one failing case without waiting for the full suite

---

## Acceptance Criteria

- [x] **AC-US1-01**: Given a test case in idle state, when I click its Run button, then only that case transitions to "running" state and other cases remain in their current state (idle, complete, etc.)
- [x] **AC-US1-02**: Given a running case, when its SSE stream emits progress events, then only that case's inline result updates while other cases' results are unchanged
- [x] **AC-US1-03**: Given a single-case run, when the server receives a POST to `/api/skills/:plugin/:skill/benchmark/case/:evalId`, then it executes only that case and streams SSE events scoped to that evalId
- [x] **AC-US1-04**: Given a case that errors during execution (LLM timeout, network failure), then that case transitions to "error" state with an error message, and no other cases are affected

---

## Implementation

**Increment**: [0467-parallel-per-case-benchmark](../../../../../increments/0467-parallel-per-case-benchmark/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-001**: Create Semaphore concurrency primitive
- [x] **T-002**: Extract `runSingleCaseSSE` from benchmark runner and add per-case API routes
- [x] **T-003**: Add `scope` field to `BenchmarkResult` type
