---
increment: 0467-parallel-per-case-benchmark
title: "Parallel Per-Case Benchmark Execution"
type: feature
priority: P1
status: planned
created: 2026-03-10
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Parallel Per-Case Benchmark Execution

## Problem Statement

The eval-ui Skill Builder benchmark system executes all test cases sequentially through a single SSE stream. A global `isRunning: boolean` flag blocks the entire UI whenever any case is running, preventing users from running, viewing, or cancelling individual cases independently. Single-case runs cannot be cancelled on their own and are not saved to history. There is no concurrency control or parallel execution capability on the server.

This architecture forces users to wait for all cases to complete before interacting with results, making iterative skill development slow and frustrating.

## Goals

- Enable independent per-case benchmark execution with individual SSE streams
- Support per-case cancellation without affecting other running cases
- Implement parallel bulk execution with configurable concurrency control
- Save all runs (single and bulk) to history for traceability
- Keep the UI fully interactive while cases are running

## User Stories

### US-001: Run a Single Test Case Independently (P0)
**Project**: vskill

**As a** skill developer
**I want** to run a single test case without blocking other cases or the UI
**So that** I can iterate quickly on one failing case without waiting for the full suite

**Acceptance Criteria**:
- [x] **AC-US1-01**: Given a test case in idle state, when I click its Run button, then only that case transitions to "running" state and other cases remain in their current state (idle, complete, etc.)
- [x] **AC-US1-02**: Given a running case, when its SSE stream emits progress events, then only that case's inline result updates while other cases' results are unchanged
- [x] **AC-US1-03**: Given a single-case run, when the server receives a POST to `/api/skills/:plugin/:skill/benchmark/case/:evalId`, then it executes only that case and streams SSE events scoped to that evalId
- [x] **AC-US1-04**: Given a case that errors during execution (LLM timeout, network failure), then that case transitions to "error" state with an error message, and no other cases are affected

---

### US-002: Cancel a Running Case Independently (P0)
**Project**: vskill

**As a** skill developer
**I want** to cancel a specific running test case without stopping other in-flight cases
**So that** I can abort a stuck or unwanted run while preserving results from other cases

**Acceptance Criteria**:
- [x] **AC-US2-01**: Given a case in "running" state, when I click its Cancel button, then that case's AbortController is aborted, the SSE stream for that case closes, and the case transitions to "cancelled" state
- [x] **AC-US2-02**: Given cases A (running) and B (running), when I cancel case A, then case B continues running uninterrupted and eventually completes normally
- [x] **AC-US2-03**: Given a case in "cancelled" state, when its Run button is clicked again, then it transitions back to "running" and starts a fresh SSE stream
- [x] **AC-US2-04**: Given a case in any non-running state (idle, complete, error, cancelled), then the Cancel button is either hidden or disabled for that case

---

### US-003: Parallel Bulk Execution with Concurrency Control (P1)
**Project**: vskill

**As a** skill developer
**I want** to run all test cases in parallel (with a concurrency limit) instead of sequentially
**So that** bulk benchmark runs complete faster while not overwhelming the LLM provider

**Acceptance Criteria**:
- [x] **AC-US3-01**: Given a "Run All" action, when executed, then all cases transition to "queued" state and begin executing in parallel up to the concurrency limit (default: 3 concurrent cases)
- [x] **AC-US3-02**: Given 5 cases and concurrency limit of 3, when bulk run starts, then 3 cases are in "running" state and 2 are in "queued" state; as running cases complete, queued cases start
- [x] **AC-US3-03**: Given a Semaphore class in `concurrency.ts`, when multiple cases attempt to acquire, then at most N cases execute simultaneously, and others wait until a slot is released
- [x] **AC-US3-04**: Given a bulk run in progress, when all cases have completed (via `Promise.allSettled`), then the bulk run is marked complete and a summary result is assembled from all individual case results
- [x] **AC-US3-05**: Given a case that errors during a bulk run, then other cases continue executing (no fail-fast behavior)

---

### US-004: Per-Case History Saving (P1)
**Project**: vskill

**As a** skill developer
**I want** single-case runs to be saved to benchmark history
**So that** I can track per-case progress over time and compare results across iterations

**Acceptance Criteria**:
- [x] **AC-US4-01**: Given a single-case run that completes successfully, when the server writes the history entry, then the entry includes a `scope: "single"` field and contains only the one executed case
- [x] **AC-US4-02**: Given a bulk run that completes, when the server writes the history entry, then the entry includes `scope: "bulk"` and contains all cases that completed (including errored ones)
- [x] **AC-US4-03**: Given a single-case history entry, when viewed in the history panel, then it is visually distinguishable from bulk run entries (e.g., labeled "Single: case-name" vs "Full Run")
- [x] **AC-US4-04**: Given a per-case history query (`GET /api/skills/:plugin/:skill/history/case/:evalId`), then entries from both single-case and bulk runs appear in the timeline

---

### US-005: Cancel All Running Cases (P1)
**Project**: vskill

**As a** skill developer
**I want** a "Cancel All" action that aborts every in-flight case at once
**So that** I can quickly stop a bulk run without clicking cancel on each case individually

**Acceptance Criteria**:
- [x] **AC-US5-01**: Given multiple cases in "running" or "queued" state, when I click "Cancel All", then all running cases' AbortControllers are aborted and all queued cases are removed from the queue
- [x] **AC-US5-02**: Given a "Cancel All" action, then every affected case transitions to "cancelled" state and no further SSE events are processed for those cases
- [x] **AC-US5-03**: Given a "Cancel All" during a bulk run, then server-side semaphore slots are properly released for all cancelled cases (no resource leaks)

---

### US-006: Independent UI State Per Case (P0)
**Project**: vskill

**As a** skill developer
**I want** each test case to have its own run state independent of all other cases
**So that** I can see real-time progress on multiple cases simultaneously without UI blocking

**Acceptance Criteria**:
- [x] **AC-US6-01**: Given the workspace state, then `isRunning: boolean` is replaced by a `caseRunStates: Map<number, CaseRunState>` where CaseRunState is one of: idle, queued, running, complete, error, cancelled
- [x] **AC-US6-02**: Given a `useMultiSSE` hook, then it manages a `Map<number, { controller: AbortController, events: SSEEvent[] }>` supporting concurrent independent streams
- [x] **AC-US6-03**: Given case A is running and case B is complete, then case B's Run button is enabled, case B's results are fully visible, and the UI is not blocked in any way
- [x] **AC-US6-04**: Given new reducer actions CASE_RUN_START, CASE_RUN_COMPLETE, CASE_RUN_ERROR, and CASE_RUN_CANCEL, then each action updates only the targeted case's state in the caseRunStates map
- [x] **AC-US6-05**: Given the workspace context, then `runCase(evalId)`, `runAll()`, `cancelCase(evalId)`, and `cancelAll()` replace the current `runBenchmark(mode, scope)` and `cancelRun()` functions

## Out of Scope

- Configurable concurrency limit via UI (will use hardcoded default of 3; can be exposed in a future increment)
- Parallel execution for comparison (A/B) runs (comparison mode keeps its existing flow)
- WebSocket migration (staying with SSE)
- Reordering or prioritizing queued cases
- Retry logic for failed cases (user can manually re-run)

## Technical Notes

### Dependencies
- Existing `benchmark-runner.ts` (refactor target)
- Existing `useSSE` hook in `sse.ts` (replaced by `useMultiSSE`)
- Existing `workspaceReducer.ts` and `workspaceTypes.ts` (extended)

### Constraints
- Node.js ESM: all imports must use `.js` extensions
- React 19 with Vite 6 and Tailwind CSS v4
- Semaphore must handle cleanup on error/cancel to prevent slot leaks
- SSE streams must be properly closed on client disconnect (server must detect `res.on('close')`)
- Backward compatibility: existing `/api/skills/:plugin/:skill/benchmark` endpoint continues to work for bulk runs

### Architecture Decisions
- **Semaphore over queue library**: Simple custom Semaphore class in `concurrency.ts` rather than pulling in a dependency. The concurrency needs are straightforward (limit parallel LLM calls)
- **Per-case SSE endpoints**: New `POST .../benchmark/case/:evalId` and `POST .../baseline/case/:evalId` routes rather than multiplexing on the existing bulk endpoint, keeping the API semantics clean
- **Map-based state over boolean**: `caseRunStates: Map<number, CaseRunState>` gives O(1) per-case state lookup and naturally supports independent lifecycle management
- **Promise.allSettled for bulk**: Unlike Promise.all, allSettled ensures all cases run to completion even if some fail

## Success Metrics

- Single-case run works independently without blocking UI
- Bulk run of N cases completes in roughly ceil(N/3) times the average single-case duration (parallel speedup)
- All runs (single and bulk) appear in benchmark history
- Zero resource leaks: semaphore slots released on cancel/error, AbortControllers cleaned up
