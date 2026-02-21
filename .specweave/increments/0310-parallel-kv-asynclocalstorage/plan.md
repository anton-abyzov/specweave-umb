# Implementation Plan: Parallelize remaining sequential KV reads and fix worker-context race with AsyncLocalStorage

## Overview

This increment addresses two related performance/correctness issues in vskill-platform:

1. **Sequential KV reads**: `getStuckSubmissions` and `enumeratePublishedSkills` iterate over KV keys with sequential `await` in a `for` loop, causing O(N) latency. The fix follows the same `Promise.allSettled` pattern established in increment 0281 for `getSubmissionsFresh`.

2. **Module-level env race**: `worker-context.ts` stores the Cloudflare env in a module-level `let _env`, which is shared across all concurrent invocations in the same isolate. With `max_concurrency=10` and `max_batch_size=3`, up to 30 concurrent operations can race. Replacing with `AsyncLocalStorage` scopes the env to each batch's async execution context.

## Architecture

### Components Modified

- **submission-store.ts**: Refactor `getStuckSubmissions` and `enumeratePublishedSkills` from sequential `for` loops to `Promise.allSettled` parallel reads
- **worker-context.ts**: Replace module-level `_env` with `AsyncLocalStorage<CloudflareEnv>`, export `runWithWorkerEnv(env, fn)` and updated `getWorkerEnv()`
- **consumer.ts**: Switch from `setWorkerEnv`/`clearWorkerEnv` try/finally to `runWithWorkerEnv(env, callback)`

### Data Model

No data model changes. KV key patterns (`sub:*`, `skill:*`) remain identical.

### API Contracts

**worker-context.ts public API changes:**

```typescript
// REMOVED:
export function setWorkerEnv(env: CloudflareEnv): void;
export function clearWorkerEnv(): void;

// ADDED:
export function runWithWorkerEnv<T>(env: CloudflareEnv, fn: () => Promise<T>): Promise<T>;

// UNCHANGED (signature preserved):
export function getWorkerEnv(): CloudflareEnv | null;
```

All other modules that call `getWorkerEnv()` (submission-store, db, external-scan-store, repo-health-store, external-scan-dispatch) require **zero changes** since `getWorkerEnv()` signature is preserved.

## Technology Stack

- **Runtime**: Cloudflare Workers with `nodejs_compat`
- **AsyncLocalStorage**: `node:async_hooks` (available via `nodejs_compat` flag)
- **Testing**: Vitest with `vi.hoisted()` + `vi.mock()` for ESM

## Architecture Decision: AsyncLocalStorage vs alternatives

**Options considered:**
1. **AsyncLocalStorage** (chosen): Built-in Node.js primitive, available in Workers via `nodejs_compat`. Zero-dependency, well-tested, designed exactly for this use case.
2. **WeakMap keyed by batch ID**: Requires passing batch ID through all call chains. Invasive change to every `getKV()` caller.
3. **Pass env as parameter**: Most explicit, but requires changing signatures of 10+ functions across 5+ files. Too invasive for this increment.

**Decision**: AsyncLocalStorage provides request-scoped context without changing any intermediate function signatures. The only call-site change is in `consumer.ts`.

## Implementation Phases

### Phase 1: AsyncLocalStorage in worker-context (US-003)
1. Import `AsyncLocalStorage` from `node:async_hooks`
2. Create `workerEnvStorage` instance
3. Implement `runWithWorkerEnv(env, fn)` that calls `workerEnvStorage.run(env, fn)`
4. Update `getWorkerEnv()` to read from `workerEnvStorage.getStore()` instead of `_env`
5. Keep `setWorkerEnv`/`clearWorkerEnv` as deprecated stubs for any edge cases (or remove entirely if consumer.ts is the only caller)

### Phase 2: Update consumer.ts (US-003)
1. Replace `setWorkerEnv(env)` + `try/finally { clearWorkerEnv() }` with `runWithWorkerEnv(env, async () => { ... })`
2. Update consumer tests for new API

### Phase 3: Parallel KV reads (US-001, US-002)
1. Refactor `getStuckSubmissions` to use `Promise.allSettled`
2. Refactor `enumeratePublishedSkills` to use `Promise.allSettled`
3. Both follow the exact pattern from `getSubmissionsFresh` (increment 0281)

## Testing Strategy (TDD)

All tests written RED first, then GREEN.

1. **submission-store.test.ts**: New test cases for parallel execution in `getStuckSubmissions` and `enumeratePublishedSkills`
2. **consumer.test.ts**: Updated tests for `runWithWorkerEnv` pattern, new test for concurrent batch isolation
3. Concurrency probes using the same pattern as TC-050 (track `maxConcurrent` via async timing)

## Technical Challenges

### Challenge 1: AsyncLocalStorage in Cloudflare Workers
**Solution**: `nodejs_compat` is already enabled in `wrangler.jsonc`, confirmed by existing usage patterns. `AsyncLocalStorage` from `node:async_hooks` works in Workers with this flag.
**Risk**: Low. This is a documented Cloudflare feature.

### Challenge 2: Existing test mocks for worker-context
**Solution**: Update `vi.mock("../worker-context", ...)` in all test files to mock the new API (`runWithWorkerEnv`, `getWorkerEnv`). Only `consumer.test.ts` needs significant changes; other test files only mock `getWorkerEnv` which retains its signature.
**Risk**: Low. Mock changes are mechanical.
