# Tasks: 0313 — Parallelize remaining sequential KV reads + fix worker-context race

## T-001: TDD RED — getStuckSubmissions parallel test
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-03 | **Status**: [x] completed
**Test**: Given N sub:* keys in KV → When getStuckSubmissions runs → Then all kv.get() calls are concurrent (maxConcurrent > 1)
- Write TC-056 in submission-store.test.ts using concurrency counter pattern (same as TC-050 for getSubmissionsFresh)
- Confirm RED: current sequential impl gives maxConcurrent=1

---

## T-002: TDD RED — enumeratePublishedSkills parallel test
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-03 | **Status**: [x] completed
**Test**: Given N skill:* keys in KV → When enumeratePublishedSkills runs → Then all kv.get() calls are concurrent (maxConcurrent > 1)
- Write TC-057 in submission-store.test.ts
- Confirm RED

---

## T-003: TDD RED — AsyncLocalStorage isolation test
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-03 | **Status**: [x] completed
**Test**: Given two concurrent runWithWorkerEnv() calls with different envs → When each reads getWorkerEnv() mid-execution → Then each sees only its own env
- Write TC-058 in consumer.test.ts
- Confirm RED (module-level var has no isolation)

---

## T-004: GREEN — Parallelize getStuckSubmissions
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02 | **Status**: [x] completed
- Replace for loop with Promise.allSettled in getStuckSubmissions
- Confirm TC-056 GREEN

---

## T-005: GREEN — Parallelize enumeratePublishedSkills
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02 | **Status**: [x] completed
- Replace for loop with Promise.allSettled in enumeratePublishedSkills
- Confirm TC-057 GREEN

---

## T-006: GREEN — Refactor worker-context.ts to AsyncLocalStorage
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-04, AC-US3-05 | **Status**: [ ] pending
- Replace module-level `let _env` with `AsyncLocalStorage<CloudflareEnv>`
- Expose `runWithWorkerEnv(env, callback)` instead of setWorkerEnv/clearWorkerEnv
- Keep `getWorkerEnv()` — internal use only (getKV fallback)

---

## T-007: GREEN — Update consumer.ts to use runWithWorkerEnv
**User Story**: US-003 | **Satisfies ACs**: AC-US3-02 | **Status**: [ ] pending
- Replace setWorkerEnv + try/finally clearWorkerEnv with runWithWorkerEnv(env, async () => { ... })
- Update consumer.test.ts imports (remove clearWorkerEnv/setWorkerEnv)
- Confirm TC-058 GREEN and all existing consumer tests pass

---

## T-008: Verify full test suite GREEN
**Status**: [ ] pending
- Run full Vitest suite in vskill-platform
- Confirm 0 new failures
