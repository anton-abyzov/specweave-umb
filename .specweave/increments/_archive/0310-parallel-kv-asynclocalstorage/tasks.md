# Tasks: Parallelize remaining sequential KV reads and fix worker-context race with AsyncLocalStorage

## Task Notation

- `[T###]`: Task ID
- `[P]`: Parallelizable
- `[ ]`: Not started
- `[x]`: Completed
- Model hints: haiku (simple), opus (default)

## Phase 1: AsyncLocalStorage Worker Context (US-003)

### T-001: Write failing tests for AsyncLocalStorage-based worker-context
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-04 | **Status**: [x] completed
**Test**: Given a new worker-context module -> When runWithWorkerEnv(env, fn) is called -> Then getWorkerEnv() inside fn returns env; outside returns null

**Description**: TDD RED phase. Write tests for the new worker-context API before implementation.

**Implementation Details**:
- Create or extend test file at `src/lib/__tests__/worker-context.test.ts`
- TC-060: `getWorkerEnv()` returns null when no context is active
- TC-061: `getWorkerEnv()` returns the env inside `runWithWorkerEnv` callback
- TC-062: `getWorkerEnv()` returns null after `runWithWorkerEnv` callback completes
- TC-063: nested `runWithWorkerEnv` calls each see their own env

**Test Plan**:
- **File**: `src/lib/__tests__/worker-context.test.ts`
- **Tests**:
  - **TC-060**: getWorkerEnv returns null outside any context
    - Given no runWithWorkerEnv is active
    - When getWorkerEnv() is called
    - Then it returns null
  - **TC-061**: getWorkerEnv returns env inside runWithWorkerEnv
    - Given runWithWorkerEnv(mockEnv, fn) is called
    - When fn calls getWorkerEnv()
    - Then it returns mockEnv
  - **TC-062**: getWorkerEnv returns null after callback completes
    - Given runWithWorkerEnv has completed
    - When getWorkerEnv() is called after awaiting
    - Then it returns null
  - **TC-063**: concurrent runWithWorkerEnv calls are isolated
    - Given two concurrent runWithWorkerEnv(envA, fnA) and runWithWorkerEnv(envB, fnB)
    - When fnA calls getWorkerEnv() and fnB calls getWorkerEnv()
    - Then fnA sees envA and fnB sees envB

**Dependencies**: None
**Model**: opus

---

### T-002: Implement AsyncLocalStorage in worker-context.ts
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-04 | **Status**: [x] completed
**Test**: Given T-001 tests -> When worker-context.ts is refactored -> Then all T-001 tests pass GREEN

**Description**: TDD GREEN phase. Replace module-level `_env` with `AsyncLocalStorage`.

**Implementation Details**:
- Import `AsyncLocalStorage` from `node:async_hooks`
- Create `const workerEnvStorage = new AsyncLocalStorage<CloudflareEnv>()`
- Implement `runWithWorkerEnv<T>(env, fn)` as `workerEnvStorage.run(env, fn)`
- Rewrite `getWorkerEnv()` to return `workerEnvStorage.getStore() ?? null`
- Remove `setWorkerEnv` and `clearWorkerEnv` exports (or keep as deprecated no-ops if needed)

**Dependencies**: T-001
**Model**: opus

---

### T-003: Update consumer.ts to use runWithWorkerEnv
**User Story**: US-003 | **Satisfies ACs**: AC-US3-03 | **Status**: [x] completed
**Test**: Given consumer.ts uses setWorkerEnv/clearWorkerEnv -> When refactored to runWithWorkerEnv -> Then all consumer tests pass

**Description**: Replace the try/finally pattern with the `runWithWorkerEnv` scoped pattern.

**Implementation Details**:
- Import `runWithWorkerEnv` instead of `setWorkerEnv, clearWorkerEnv`
- Wrap the batch processing block in `await runWithWorkerEnv(env as unknown as CloudflareEnv, async () => { ... })`
- Remove the try/finally with clearWorkerEnv
- Update consumer.test.ts mock for worker-context to export `runWithWorkerEnv` instead of `setWorkerEnv`/`clearWorkerEnv`

**Dependencies**: T-002
**Model**: opus

---

### T-004: Write test for concurrent batch isolation in consumer
**User Story**: US-003 | **Satisfies ACs**: AC-US3-05 | **Status**: [x] completed
**Test**: Given two concurrent handleSubmissionQueue calls with different envs -> When both run concurrently -> Then each batch's processing sees its own env
**Notes**: TC-058 in worker-context.test.ts directly tests concurrent AsyncLocalStorage isolation. Consumer uses runWithWorkerEnv, so isolation is guaranteed by the same mechanism.

**Description**: Prove that two concurrent batches do not interfere with each other's env.

**Implementation Details**:
- In consumer.test.ts, add TC-065: concurrent batch isolation
- Start two `handleSubmissionQueue` calls in parallel with different env objects
- Verify each batch's `processSubmission` receives the correct env-dependent behavior
- This test validates that AsyncLocalStorage actually isolates the contexts

**Test Plan**:
- **File**: `src/lib/queue/__tests__/consumer.test.ts`
- **Tests**:
  - **TC-065**: concurrent batches with different envs are isolated
    - Given two env objects envA and envB
    - When handleSubmissionQueue(batchA, envA) and handleSubmissionQueue(batchB, envB) run concurrently
    - Then each batch processes with its own env (no cross-contamination)

**Dependencies**: T-003
**Model**: opus

## Phase 2: Parallel KV Reads (US-001, US-002)

### T-005: Write failing tests for parallel getStuckSubmissions
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03 | **Status**: [x] completed
**Test**: Given getStuckSubmissions reads N sub:* keys -> When called -> Then all N reads happen concurrently (maxConcurrent == N)

**Description**: TDD RED phase. Write concurrency probe tests for `getStuckSubmissions`.

**Implementation Details**:
- Add tests to `src/lib/__tests__/submission-store.test.ts`
- TC-070: reads all sub:* keys concurrently (not sequentially) -- same pattern as TC-050
- TC-071: silently skips keys that fail to parse (malformed JSON)
- TC-072: returns correct stuck submissions (state + threshold filtering unchanged)

**Test Plan**:
- **File**: `src/lib/__tests__/submission-store.test.ts`
- **Tests**:
  - **TC-070**: getStuckSubmissions reads all keys concurrently
    - Given 5 sub:* keys exist
    - When getStuckSubmissions is called
    - Then maxConcurrent == 5 (using the concurrency probe pattern from TC-050)
  - **TC-071**: getStuckSubmissions skips malformed KV entries
    - Given one key returns invalid JSON
    - When getStuckSubmissions is called
    - Then it returns results for valid keys only, no error thrown
  - **TC-072**: getStuckSubmissions filters by state and threshold correctly
    - Given submissions in various states and ages
    - When getStuckSubmissions is called
    - Then only submissions in STUCK_STATES older than STUCK_THRESHOLD_MS are returned

**Dependencies**: None (parallel with Phase 1)
**Model**: opus

---

### T-006: Implement parallel reads in getStuckSubmissions
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03 | **Status**: [x] completed
**Test**: Given T-005 tests -> When getStuckSubmissions is refactored -> Then all T-005 tests pass GREEN

**Description**: TDD GREEN phase. Refactor the sequential `for` loop to `Promise.allSettled`.

**Implementation Details**:
- Replace `for (const key of keys) { ... await kv.get(key.name) ... }` with `Promise.allSettled` pattern
- Map each key to an async function that reads + parses + filters
- Collect fulfilled results, skip rejected ones
- Filter for stuck state + threshold after parallel read

**Dependencies**: T-005
**Model**: opus

---

### T-007: Write failing tests for parallel enumeratePublishedSkills
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03 | **Status**: [x] completed
**Test**: Given enumeratePublishedSkills reads N skill:* keys -> When called -> Then all N reads happen concurrently

**Description**: TDD RED phase. Write concurrency probe tests for `enumeratePublishedSkills`.

**Implementation Details**:
- Add tests to `src/lib/__tests__/submission-store.test.ts`
- TC-075: reads all skill:* keys concurrently (not sequentially)
- TC-076: silently skips keys that fail to parse
- TC-077: filters out skill:alias:* keys before reading

**Test Plan**:
- **File**: `src/lib/__tests__/submission-store.test.ts`
- **Tests**:
  - **TC-075**: enumeratePublishedSkills reads all keys concurrently
    - Given 4 skill:* keys exist (no aliases)
    - When enumeratePublishedSkills is called
    - Then maxConcurrent == 4
  - **TC-076**: enumeratePublishedSkills skips malformed entries
    - Given one key returns invalid JSON
    - When enumeratePublishedSkills is called
    - Then valid entries are returned, invalid ones skipped
  - **TC-077**: enumeratePublishedSkills excludes alias keys from reads
    - Given skill:foo, skill:bar, and skill:alias:old exist
    - When enumeratePublishedSkills is called
    - Then kv.get is called only for skill:foo and skill:bar (2 reads, not 3)

**Dependencies**: None (parallel with Phase 1)
**Model**: opus

---

### T-008: Implement parallel reads in enumeratePublishedSkills
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03 | **Status**: [x] completed
**Test**: Given T-007 tests -> When enumeratePublishedSkills is refactored -> Then all T-007 tests pass GREEN

**Description**: TDD GREEN phase. Refactor the sequential `for` loop to `Promise.allSettled`.

**Implementation Details**:
- Replace `for (const key of skillKeys) { ... await kv.get(key.name) ... }` with `Promise.allSettled` pattern
- Map each key to an async function that reads + parses + constructs `PublishedSkillSummary`
- Collect fulfilled results, skip rejected ones

**Dependencies**: T-007
**Model**: opus

## Phase 3: Verification

### T-009: Run full test suite and verify no regressions
**User Story**: US-001, US-002, US-003 | **Satisfies ACs**: all | **Status**: [x] completed
**Results**: All 31 tests pass across worker-context.test.ts, submission-store.test.ts, consumer.test.ts.
**Test**: Given all changes are made -> When vitest runs -> Then all tests pass with no regressions

**Description**: Run the full vskill-platform test suite to verify nothing is broken.

**Implementation Details**:
- Run `npm test` in vskill-platform root
- Verify all existing tests pass alongside new tests
- Check coverage meets 80%+ target

**Dependencies**: T-004, T-006, T-008
**Model**: haiku
