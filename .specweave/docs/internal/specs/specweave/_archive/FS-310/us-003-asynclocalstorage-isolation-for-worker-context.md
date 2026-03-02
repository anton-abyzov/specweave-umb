---
id: US-003
feature: FS-310
title: AsyncLocalStorage isolation for worker-context
status: complete
priority: P1
created: 2026-02-22
project: specweave
external:
  github:
    issue: 1263
    url: https://github.com/anton-abyzov/specweave/issues/1263
---
# US-003: AsyncLocalStorage isolation for worker-context

**Feature**: [FS-310](./FEATURE.md)

platform operator running the queue consumer with `max_concurrency=10`
**I want** the worker env context to be isolated per-batch using `AsyncLocalStorage`
**So that** concurrent batches in the same isolate do not corrupt each other's env references

---

## Acceptance Criteria

- [x] **AC-US3-01**: `worker-context.ts` exports a `workerEnvStorage` instance of `AsyncLocalStorage<CloudflareEnv>` and a `getWorkerEnv()` that reads from it
- [x] **AC-US3-02**: The old `setWorkerEnv`/`clearWorkerEnv` API is replaced with a `runWithWorkerEnv(env, callback)` pattern that scopes env to the callback's async context
- [x] **AC-US3-03**: `consumer.ts` uses `runWithWorkerEnv(env, async () => { ... })` instead of `setWorkerEnv`/`clearWorkerEnv` try/finally
- [x] **AC-US3-04**: All existing consumers of `getWorkerEnv()` (submission-store, db, external-scan-store, repo-health-store, external-scan-dispatch) continue to work without changes
- [x] **AC-US3-05**: Two concurrent batches with different env objects do not interfere; each batch's `getWorkerEnv()` returns its own env throughout its async chain

---

## Implementation

**Increment**: [0310-parallel-kv-asynclocalstorage](../../../../../increments/0310-parallel-kv-asynclocalstorage/spec.md)

