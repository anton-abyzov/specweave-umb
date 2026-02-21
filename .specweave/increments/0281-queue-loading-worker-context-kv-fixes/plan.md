# Implementation Plan: Queue Loading, Worker-Context, and KV Fixes

## Overview

Three targeted fixes in the vskill-platform submission infrastructure. All changes are in the `repositories/anton-abyzov/vskill-platform/` repo. No schema changes, no API contract changes, no new endpoints.

## Architecture

### Affected Components

1. **`src/lib/submission-store.ts`** -- `getSubmissionsFresh()` function
   - Change: Replace sequential `for` loop with `Promise.allSettled()` for parallel KV reads
   - Impact: Performance improvement for active submission re-hydration

2. **`src/lib/worker-context.ts`** -- Module-level env state
   - Change: Ensure `clearWorkerEnv()` is only called after all async work completes (already the case with the `finally` block, but document the contract)
   - Risk assessment: Low -- Cloudflare Workers are single-threaded, so there's no true race between JS execution contexts. The "race condition" is about async I/O ordering, which the current `try/finally` pattern handles correctly since `Promise.allSettled()` awaits all messages before the `finally` block runs. The real fix is ensuring `getKV()` callers don't throw if env is null.

3. **`src/lib/queue/consumer.ts`** -- Queue consumer batch handler
   - Change: Ensure `clearWorkerEnv()` only runs after all `processSubmission()` promises settle
   - Current status: Already correct -- `Promise.allSettled()` is used, and `clearWorkerEnv()` is in `finally`. No change needed here.

4. **`src/app/api/v1/submissions/route.ts`** -- GET handler
   - Change: Verify the merge logic works correctly with parallel `getSubmissionsFresh()`
   - Current status: Already correct pattern -- just needs the underlying function to be parallel.

### Data Flow (Submission Loading)

```
Queue Page → GET /api/v1/submissions
  → getSubmissionIndex() → reads "submissions:index" KV blob
  → filter active IDs (RECEIVED, TIER1_SCANNING, TIER2_SCANNING, AUTO_APPROVED)
  → getSubmissionsFresh(activeIds) → reads sub:{id} keys IN PARALLEL (fix)
  → merge fresh data over stale index entries
  → return JSON response
```

## Technology Stack

- **Language/Framework**: TypeScript, Next.js 15, Cloudflare Workers
- **KV Store**: Cloudflare Workers KV
- **Testing**: Vitest with ESM mocking (`vi.hoisted()` + `vi.mock()`)

**Architecture Decisions**:
- Use `Promise.allSettled()` over `Promise.all()` for KV reads to handle individual key failures gracefully without aborting all reads
- Keep the module-level `_env` pattern in worker-context since Cloudflare Workers are single-threaded -- add defensive null checks in `getKV()` callers instead
- No changes to the GET submissions API contract -- same response shape

## Implementation Phases

### Phase 1: Fix getSubmissionsFresh (Core Bug)
- Refactor the sequential `for` loop to `Promise.allSettled()`
- Add unit tests for parallel behavior and error handling

### Phase 2: Worker-context hardening
- Add defensive error handling in `getKV()` when both `getWorkerEnv()` and `getCloudflareContext()` fail
- Add test coverage for the fallback path

### Phase 3: Verification
- Run existing test suites
- Verify no regressions in submission-store, consumer, and route tests

## Testing Strategy

- **Unit tests**: `submission-store.test.ts` -- add tests for parallel KV reads in `getSubmissionsFresh()`
- **Existing tests**: Run consumer.test.ts, route.pagination.test.ts to verify no regressions
- **TDD**: Write failing tests first, then implement fixes

## Technical Challenges

### Challenge 1: ESM mocking for parallel reads
**Solution**: Use existing `vi.hoisted()` + `vi.mock()` pattern already established in the codebase
**Risk**: Low -- pattern is proven in existing tests

### Challenge 2: Ensuring getKV() never throws unhandled
**Solution**: Wrap `getCloudflareContext()` call in try/catch with informative error message
**Risk**: Low -- affects only edge cases where neither env source is available
