---
increment: 0310-parallel-kv-asynclocalstorage
title: "Parallelize remaining sequential KV reads and fix worker-context race with AsyncLocalStorage"
type: feature
priority: P1
status: planned
created: 2026-02-21
structure: user-stories
test_mode: TDD
coverage_target: 80
---

# Feature: Parallelize remaining sequential KV reads and fix worker-context race with AsyncLocalStorage

## Overview

Increment 0281 fixed `getSubmissionsFresh` (sequential to parallel). Three more functions still have the same O(N) sequential KV read pattern. Additionally, `worker-context.ts` uses a module-level `_env` variable that creates a race condition when multiple queue batches run concurrently in the same isolate (`max_concurrency=10`, `max_batch_size=3` = up to 30 concurrent invocations). When one batch's `clearWorkerEnv()` fires in its `finally` block, it nulls the env for other in-flight batches.

## User Stories

### US-001: Parallel KV reads in getStuckSubmissions (P1)
**Project**: specweave

**As a** platform operator running the cron-based stuck submission recovery
**I want** `getStuckSubmissions` to read all `sub:*` KV keys in parallel
**So that** stuck submission detection completes faster and does not hit wall-clock timeouts on large datasets

**Acceptance Criteria**:
- [ ] **AC-US1-01**: `getStuckSubmissions` uses `Promise.allSettled` to read all `sub:*` keys concurrently instead of a sequential `for` loop
- [ ] **AC-US1-02**: Individual KV read failures (rejected promises) are silently skipped, matching the existing `try/catch { /* skip malformed */ }` behavior
- [ ] **AC-US1-03**: Return value and filtering logic (STUCK_STATES, STUCK_THRESHOLD_MS) remain identical to current behavior

---

### US-002: Parallel KV reads in enumeratePublishedSkills (P1)
**Project**: specweave

**As a** marketplace user browsing published skills
**I want** `enumeratePublishedSkills` to read all `skill:*` KV keys in parallel
**So that** marketplace enumeration is fast even with hundreds of published skills

**Acceptance Criteria**:
- [ ] **AC-US2-01**: `enumeratePublishedSkills` uses `Promise.allSettled` to read all `skill:*` keys concurrently instead of a sequential `for` loop
- [ ] **AC-US2-02**: Individual KV read failures or malformed JSON are silently skipped, matching the existing `catch { /* skip malformed */ }` behavior
- [ ] **AC-US2-03**: Alias keys (`skill:alias:*`) are still filtered out before reads

---

### US-003: AsyncLocalStorage isolation for worker-context (P1)
**Project**: specweave

**As a** platform operator running the queue consumer with `max_concurrency=10`
**I want** the worker env context to be isolated per-batch using `AsyncLocalStorage`
**So that** concurrent batches in the same isolate do not corrupt each other's env references

**Acceptance Criteria**:
- [ ] **AC-US3-01**: `worker-context.ts` exports a `workerEnvStorage` instance of `AsyncLocalStorage<CloudflareEnv>` and a `getWorkerEnv()` that reads from it
- [ ] **AC-US3-02**: The old `setWorkerEnv`/`clearWorkerEnv` API is replaced with a `runWithWorkerEnv(env, callback)` pattern that scopes env to the callback's async context
- [ ] **AC-US3-03**: `consumer.ts` uses `runWithWorkerEnv(env, async () => { ... })` instead of `setWorkerEnv`/`clearWorkerEnv` try/finally
- [ ] **AC-US3-04**: All existing consumers of `getWorkerEnv()` (submission-store, db, external-scan-store, repo-health-store, external-scan-dispatch) continue to work without changes
- [ ] **AC-US3-05**: Two concurrent batches with different env objects do not interfere; each batch's `getWorkerEnv()` returns its own env throughout its async chain

## Functional Requirements

### FR-001: Parallel reads must use Promise.allSettled (not Promise.all)
`Promise.allSettled` ensures partial failures do not abort the entire batch, matching existing error-swallowing behavior in both functions.

### FR-002: AsyncLocalStorage must be from node:async_hooks
Cloudflare Workers with `nodejs_compat` flag provide `AsyncLocalStorage` via `node:async_hooks`. This is already enabled in `wrangler.jsonc`.

### FR-003: Backward-compatible getWorkerEnv signature
`getWorkerEnv()` must still return `CloudflareEnv | null` so all existing callers (submission-store, db, external-scan-store, etc.) compile without changes.

## Success Criteria

- All existing tests pass (no regressions)
- New tests demonstrate parallel execution (concurrency > 1 for N > 1 keys)
- New tests demonstrate AsyncLocalStorage isolation between concurrent batches
- Coverage target: 80%+

## Out of Scope

- `migrateSkillSlugs`: one-time admin migration, sequential reads acceptable (deferred)
- Rewriting `getPublishedSkillsList` or `getSubmissionIndex` (these are index-blob reads, not N+1 problems)
- Performance benchmarks (functional correctness only in this increment)

## Dependencies

- Increment 0281 (parallel KV in getSubmissionsFresh) -- completed, established pattern
- `nodejs_compat` flag in `wrangler.jsonc` -- already enabled
