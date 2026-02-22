---
increment: 0281-queue-loading-worker-context-kv-fixes
title: "Fix queue page loading, worker-context race condition, and sequential KV reads"
type: bug
priority: P1
status: completed
created: 2026-02-21
structure: user-stories
test_mode: TDD
coverage_target: 80
---

# Bug Fix: Queue page loading, worker-context race condition, and sequential KV reads

## Overview

Three related bugs in the vskill-platform queue/submission infrastructure:

1. **Queue page shows all zeros on load** -- The `/queue` page fetches submissions via `GET /api/v1/submissions?limit=500`, but stat cards show 0/0/0/0 until data arrives. The `getSubmissionIndex()` function returns the shared `submissions:index` KV blob which can be stale or empty, and the re-hydration path via `getSubmissionsFresh()` reads KV keys **sequentially** in a `for` loop rather than in parallel, causing unnecessary latency. When the index is empty or slow, the page renders zeros.

2. **`getCloudflareContext` race condition in worker-context** -- The `worker-context.ts` module uses a module-level `let _env` variable to store the Cloudflare env set by the queue consumer. However, since the consumer processes batch messages via `Promise.allSettled()` (concurrently), and `clearWorkerEnv()` is called in the `finally` block after all messages complete, there is a potential race: if a Next.js request also calls `getKV()` during batch processing, it could pick up the worker env intended for the queue consumer, or vice versa. The current pattern of set-then-clear at batch level is fragile.

3. **Sequential KV reads in `getSubmissionsFresh`** -- The `getSubmissionsFresh()` function in `submission-store.ts` reads individual `sub:{id}` keys one at a time in a `for` loop. With 10+ active submissions, this creates sequential network round-trips to KV, adding ~50-100ms per key. This should use `Promise.all()` for parallel reads.

## User Stories

### US-001: Parallel KV reads in getSubmissionsFresh (P1)
**Project**: vskill-platform

**As a** queue page user
**I want** the submission data to load quickly
**So that** the stat cards and table show accurate data without unnecessary delay

**Acceptance Criteria**:
- [x] **AC-US1-01**: `getSubmissionsFresh()` reads all `sub:{id}` KV keys in parallel using `Promise.all()` instead of a sequential `for` loop
- [x] **AC-US1-02**: The function still handles individual key failures gracefully (skip missing/errored keys)
- [x] **AC-US1-03**: Latency for fetching N active submissions is O(1) network round-trips instead of O(N)

---

### US-002: Worker-context race condition safety (P1)
**Project**: vskill-platform

**As a** platform operator
**I want** the worker-context module to be safe against concurrent access
**So that** queue consumer batch processing does not leak env state to concurrent Next.js requests

**Acceptance Criteria**:
- [x] **AC-US2-01**: The `getKV()` pattern in submission-store, external-scan-store, repo-health-store, and external-scan-dispatch correctly prioritizes worker env over getCloudflareContext without race conditions
- [x] **AC-US2-02**: `clearWorkerEnv()` in the consumer's `finally` block does not break in-flight parallel message processing
- [x] **AC-US2-03**: If `getWorkerEnv()` returns null during queue processing (cleared prematurely), `getCloudflareContext()` fallback is invoked safely

---

### US-003: Queue page initial load data accuracy (P1)
**Project**: vskill-platform

**As a** queue page user
**I want** the stat cards to show accurate counts on first load
**So that** I can trust the dashboard data immediately without waiting for SSE updates

**Acceptance Criteria**:
- [x] **AC-US3-01**: The `GET /api/v1/submissions` endpoint returns accurate submission states by re-hydrating active submissions from individual KV keys
- [x] **AC-US3-02**: The parallel `getSubmissionsFresh()` integration in the route handler works correctly with the existing merge logic
- [x] **AC-US3-03**: Stat card counts (Total, Active, Published, Rejected) reflect actual data on initial page render

## Functional Requirements

### FR-001: Parallel KV reads
`getSubmissionsFresh()` must use `Promise.allSettled()` or `Promise.all()` with per-item error handling to read all requested submission keys concurrently.

### FR-002: Worker-context safety
The set/clear lifecycle of `_env` must be safe for concurrent batch message processing. Since Cloudflare Workers are single-threaded (no true parallelism, only concurrent I/O), the current module-level variable is acceptable for the queue consumer use case, but the `clearWorkerEnv()` must not run while async operations from `processSubmission()` are still in flight.

### FR-003: Submission API re-hydration
The GET submissions endpoint must merge fresh individual-key reads with the stale index blob to provide accurate state for in-flight submissions.

## Success Criteria

- `getSubmissionsFresh([...10 ids])` completes in roughly 1 KV round-trip time (~50ms) instead of 10 sequential (~500ms)
- Queue page stat cards show correct, non-zero values on first load when submissions exist
- No race condition errors in production logs from worker-context

## Out of Scope

- Rewriting the entire KV-based submission index (that's a larger architectural change)
- Adding a real database-backed queue page (already tracked separately)
- SSE streaming improvements
- Admin queue page (`/admin/queue`) changes

## Dependencies

- No external dependencies
- Existing test infrastructure: Vitest with ESM mocking
