# Spec: Parallelize remaining sequential KV reads and fix worker-context module-level race

## Background

Increment 0281 parallelized `getSubmissionsFresh` (sequential `for await kv.get()` → `Promise.allSettled`).
Three more functions still have the same O(N) sequential KV read pattern:

1. **`getStuckSubmissions`** — called by cron + admin panel. Enumerates all `sub:*` keys, then reads each one sequentially.
2. **`enumeratePublishedSkills`** — called by marketplace page. Enumerates all `skill:*` keys, then reads each one sequentially.

Additionally, `worker-context.ts` uses a **module-level `let _env`** variable shared across concurrent isolate invocations. With `max_concurrency: 10` and `max_batch_size: 3`, up to 30 queue batches may be in-flight simultaneously. When batch A's `clearWorkerEnv()` fires in its `finally` block, it nulls `_env` for other in-flight batches — causing `getKV()` to fall through to `getCloudflareContext()`, which throws outside Next.js request context (the root cause of ERR logs seen in queue execution history).

---

## User Stories

### US-001: Parallelize getStuckSubmissions

**As** the queue system,
**I want** `getStuckSubmissions` to read all sub:* keys in parallel,
**so that** the stuck-submission cron completes in O(1) time regardless of how many submissions exist.

**Acceptance Criteria:**

- [x] AC-US1-01: `getStuckSubmissions` uses `Promise.allSettled` to initiate all `kv.get()` calls concurrently
- [x] AC-US1-02: Keys that return null or throw are silently skipped (same resilience as current code)
- [x] AC-US1-03: Test TC-056 proves maxConcurrent > 1 during getStuckSubmissions (concurrency counter pattern)

---

### US-002: Parallelize enumeratePublishedSkills

**As** a user browsing the skill marketplace,
**I want** the published skills list to load quickly,
**so that** the marketplace page does not time out when many skills are published.

**Acceptance Criteria:**

- [x] AC-US2-01: `enumeratePublishedSkills` uses `Promise.allSettled` to initiate all `kv.get()` calls concurrently
- [x] AC-US2-02: Keys that return null or throw are silently skipped
- [x] AC-US2-03: Test TC-057 proves maxConcurrent > 1 during enumeratePublishedSkills

---

### US-003: Fix worker-context module-level race with AsyncLocalStorage

**As** the queue consumer,
**I want** each concurrent batch to have its own isolated `CloudflareEnv` context,
**so that** `clearWorkerEnv()` in one batch never nulls the env for another in-flight batch.

**Acceptance Criteria:**

- [x] AC-US3-01: `worker-context.ts` uses `AsyncLocalStorage<CloudflareEnv>` instead of module-level `let _env`
- [x] AC-US3-02: `consumer.ts` uses `workerEnvStorage.run(env, callback)` — no explicit `setWorkerEnv` / `clearWorkerEnv` calls needed
- [x] AC-US3-03: Test TC-058 verifies that two concurrent "batches" using different envs each see only their own env (no cross-contamination)
- [x] AC-US3-04: `clearWorkerEnv()` is removed from the public API (AsyncLocalStorage handles cleanup automatically when the run() scope exits)
- [x] AC-US3-05: `setWorkerEnv(env)` is removed from the public API; replaced by `runWithWorkerEnv(env, callback)`
