# Implementation Plan: Fix intermittent search failures and preferences 500 on cold starts

## Overview

Extract a shared `withRetry<T>` utility and apply it to two route files to handle Neon Postgres cold-start timeouts. The change is minimal: one new file (~25 lines), two modified route files (replacing an inline loop and adding retry wrappers), and their corresponding tests.

## Architecture

### Components

- **`src/lib/retry.ts`** (NEW): Generic retry utility with fixed delay. Follows the same pattern as existing `src/lib/with-timeout.ts` -- a single-purpose, zero-dependency helper that wraps an async operation.
- **`src/app/api/v1/skills/search/route.ts`** (MODIFIED): Replace the inline `for` loop with a `withRetry` call around `searchSkills()`.
- **`src/app/api/v1/user/preferences/route.ts`** (MODIFIED): Add `withRetry` around DB operations in both GET and PATCH handlers.

### Data Flow

```
[Request] → [Auth/Validation] → [withRetry wrapper] → [DB call via Prisma]
                                       |                      |
                                       |  (on error)          |
                                       |← 500ms delay ←──────|
                                       |                      |
                                       └→ [DB call retry] ────→ [Response]
```

Key constraint: Auth validation and request parsing remain **outside** the retry boundary. Only the DB-dependent operations are retried.

### API Design: `withRetry`

```typescript
// src/lib/retry.ts
export interface RetryOptions {
  /** Total attempts including initial (default: 2) */
  maxAttempts?: number;
  /** Fixed delay in ms between attempts (default: 500) */
  delayMs?: number;
  /** Called before each retry — use for route-specific logging */
  onRetry?: (attempt: number, error: unknown) => void;
}

export async function withRetry<T>(
  fn: () => Promise<T>,
  opts?: RetryOptions,
): Promise<T>;
```

Design decisions:
1. **Function factory (`fn: () => Promise<T>`)** not a raw promise -- the operation must be re-invocable. This matches `withDbTimeout` in `db.ts`.
2. **`onRetry` callback** instead of built-in logging -- keeps the utility generic. Each route provides its own context string (route path) without coupling the utility to console.warn.
3. **Fixed delay, not exponential** -- with only 2 attempts, exponential backoff adds complexity for no benefit. A single 500ms pause is sufficient to let Neon finish waking up.

### Retry Boundary Placement

| Route | What is retried | What is NOT retried |
|-------|----------------|-------------------|
| Search (GET) | `searchSkills({ query, category, page, limit })` | Edge KV path, param parsing, response building |
| Preferences (GET) | `getDb()` + `prisma.user.findUnique()` | `requireUser()` auth check |
| Preferences (PATCH) | `getDb()` + `findUnique` + merge + `prisma.user.update()` | `requireUser()`, `request.json()`, Zod validation |

For PATCH, the entire read-merge-write is wrapped as one unit. This is safe because the preferences merge (`{ ...current, ...parsed.data }`) is idempotent -- if attempt 1 partially committed, attempt 2 re-reads and produces the same result.

## Technology Stack

- **Language**: TypeScript (ESM, existing project)
- **Framework**: Next.js 15 (App Router)
- **Database**: Prisma + Neon (serverless Postgres)
- **Runtime**: Cloudflare Workers via OpenNext
- **Testing**: Vitest with `vi.hoisted()` + `vi.mock()` (existing pattern)

No new dependencies. `setTimeout` is available in Cloudflare Workers via `nodejs_compat`.

## Implementation Phases

### Phase 1: Utility (US-001)

1. Create `src/lib/retry.ts` with `withRetry<T>` function
2. Create `src/lib/__tests__/retry.test.ts` with unit tests:
   - Success on first attempt (no retry)
   - Failure then success (retry works)
   - Failure after all attempts (re-throws last error)
   - `onRetry` callback is called with correct args
   - Custom `maxAttempts` and `delayMs` are respected
   - Delay timing verification (uses `vi.useFakeTimers`)

### Phase 2: Search Route Integration (US-002)

1. Modify `src/app/api/v1/skills/search/route.ts`:
   - Import `withRetry` from `@/lib/retry`
   - Replace the inline for-loop (lines 44-61) with a single `withRetry` call
   - Provide `onRetry` callback that logs attempt number + route path
   - Edge-first path (lines 29-42) remains unchanged
2. Update `src/app/api/v1/skills/search/__tests__/route.test.ts`:
   - Add test: Postgres retry-then-success with delayed success
   - Verify existing tests still pass (no behavior change for happy path)

### Phase 3: Preferences Route Integration (US-003)

1. Modify `src/app/api/v1/user/preferences/route.ts`:
   - Import `withRetry` from `@/lib/retry`
   - GET: wrap DB calls in `withRetry`
   - PATCH: wrap the entire read-merge-write block in `withRetry`
   - Auth and validation remain outside retry boundary
2. Update `src/app/api/v1/user/preferences/__tests__/route.test.ts`:
   - Add test: GET retry-then-success
   - Add test: PATCH retry-then-success
   - Verify existing tests still pass

## Testing Strategy

- **Unit tests** for `withRetry` utility (isolated, with fake timers for delay verification)
- **Route-level tests** mock `searchSkills`/`searchSkillsEdge` and Prisma to simulate cold-start failure then success
- **Coverage target**: 80% (per spec)
- **Pattern**: Follow existing test patterns using `vi.hoisted()` + `vi.mock()` for ESM module mocking

## Technical Challenges

### Challenge 1: `setTimeout` delay in Cloudflare Workers
**Solution**: Cloudflare Workers with `nodejs_compat` support `setTimeout`. The existing `db.ts` already uses `setTimeout` in `Promise.race` patterns, confirming availability.
**Risk**: None -- proven pattern in the codebase.

### Challenge 2: Prisma client reuse across retry attempts
**Solution**: `getDb()` caches the Prisma client at module level (`_cachedClient` in db.ts). Both retry attempts reuse the same cached client, but Neon establishes a new underlying HTTP connection per query. The retry delay gives Neon time to warm the connection pool, not the Prisma client.
**Risk**: None -- Neon's HTTP-based driver creates fresh connections per query.

### Challenge 3: PATCH idempotency during retry
**Solution**: The preferences PATCH reads current state, merges with patch data, then writes. If attempt 1's write succeeds but the response times out (rare), attempt 2 re-reads the already-updated state and re-applies the same patch. Since merge is `{ ...current, ...parsed.data }`, the result is identical.
**Risk**: Minimal -- even the worst case produces the correct final state.
