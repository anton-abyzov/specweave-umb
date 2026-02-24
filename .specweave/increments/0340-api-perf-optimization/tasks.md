# Tasks: API Performance Optimization

## Task Notation

- `[T###]`: Task ID
- `[P]`: Parallelizable
- `[ ]`: Not started
- `[x]`: Completed
- Model hints: haiku (simple), opus (default)

## Phase 1: Configuration

### T-001: Enable Smart Placement in wrangler.jsonc
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02 | **Status**: [x] Completed
**Test**: Given wrangler.jsonc → When deployed → Then Smart Placement is active and deployment succeeds

**Implementation Details**:
- Add `"placement": { "mode": "smart" }` top-level key to `wrangler.jsonc`
- Verify no wrangler validation errors

**Dependencies**: None
**Hint**: haiku

---

## Phase 2: Core Optimizations

### T-002: Add JWT secret isolate-lifetime cache [P]
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-04 | **Status**: [x] Completed
**Test**: Given `getJwtSecret()` called twice → When second call executes → Then `resolveEnv` is NOT called again

**Implementation Details**:
- In `src/lib/auth.ts`, add `let _cachedJwtSecret: Uint8Array | null = null` at module level
- In `getJwtSecret()`, return `_cachedJwtSecret` if non-null; otherwise resolve, cache, and return
- No TTL or invalidation logic

**Test Plan**:
- **File**: `src/lib/__tests__/auth.test.ts`
- **Tests**:
  - **TC-001**: JWT secret cache hit
    - Given `resolveEnv` is mocked
    - When `signAccessToken` is called twice
    - Then `resolveEnv` was called exactly once

**Dependencies**: None
**Hint**: opus

---

### T-003: Dynamic import of bcryptjs [P]
**User Story**: US-006 | **Satisfies ACs**: AC-US6-01, AC-US6-02, AC-US6-03, AC-US6-04 | **Status**: [x] Completed
**Test**: Given `signAccessToken` is called → When checking imports → Then bcryptjs was NOT loaded

**Implementation Details**:
- Remove `import bcrypt from 'bcryptjs'` static import from `src/lib/auth.ts`
- Add module-level `let _bcrypt: typeof import('bcryptjs') | null = null`
- Add `async function getBcrypt()` that does `_bcrypt ??= await import('bcryptjs'); return _bcrypt`
- Update `hashPassword` to use `(await getBcrypt()).default.hash(password, BCRYPT_ROUNDS)`
- Update `verifyPassword` to use `(await getBcrypt()).default.compare(password, hash)`

**Test Plan**:
- **File**: `src/lib/__tests__/auth.test.ts`
- **Tests**:
  - **TC-002**: bcrypt only loaded on password operations
    - Given a fresh module import (vi.resetModules)
    - When `signAccessToken` is called
    - Then bcryptjs import was not triggered
  - **TC-003**: bcrypt loaded on hashPassword
    - Given a fresh module import
    - When `hashPassword` is called
    - Then bcryptjs dynamic import was invoked

**Dependencies**: None
**Hint**: opus

---

### T-004: Login route parallelization + waitUntil
**User Story**: US-003, US-004 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-04, AC-US3-05, AC-US4-01, AC-US4-02, AC-US4-03 | **Status**: [x] Completed
**Test**: Given a valid login request → When POST executes → Then getDb starts concurrently with rate limit AND waitUntil is called for deferred writes

**Implementation Details**:
- In `src/app/api/v1/auth/login/route.ts`:
  - Get `{ env, ctx }` from `getCloudflareContext({ async: true })` at top of handler
  - Start `const dbPromise = getDb()` before rate-limit check
  - After rate-limit passes, `const prisma = await dbPromise`
  - After generating tokens, build response immediately
  - Defer `refreshToken.create` + `admin.update(lastLoginAt)` via `ctx.waitUntil()`
  - Wrap deferred ops in `Promise.allSettled` with error logging

**Test Plan**:
- **File**: `src/app/api/v1/auth/login/__tests__/route.test.ts`
- **Tests**:
  - **TC-004**: waitUntil called with deferred operations
    - Given mocked getCloudflareContext with waitUntil spy
    - When valid login POST is made
    - Then waitUntil was called exactly once
    - And the response is returned with tokens
  - **TC-005**: rate limit rejection returns 429 without DB queries
    - Given rate limit exceeded
    - When login POST is made
    - Then 429 is returned
    - And no DB write operations occurred

**Dependencies**: T-002 (JWT cache used during token signing in login route)
**Hint**: opus

---

### T-005: OAuth callback waitUntil for refresh token [P]
**User Story**: US-003 | **Satisfies ACs**: AC-US3-03, AC-US3-04, AC-US3-05 | **Status**: [x] Completed
**Test**: Given a valid OAuth callback → When GET executes → Then refresh token storage is deferred via waitUntil

**Implementation Details**:
- In `src/app/api/v1/auth/github/callback/route.ts`:
  - Import `getCloudflareContext` from `@opennextjs/cloudflare`
  - After building response and setting cookies (step 9-10), obtain `ctx` via `getCloudflareContext({ async: true })`
  - Move refresh token storage (step 7) to `ctx.waitUntil()` block after the response is built
  - Return response before deferred write completes
  - Wrap in try/catch for local dev fallback (no ctx available)

**Dependencies**: None
**Hint**: opus

---

### T-006: DB connection prewarm in cron handler [P]
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01, AC-US5-02, AC-US5-03 | **Status**: [x] Completed
**Test**: Given the hourly cron fires → When scheduled handler runs → Then a SELECT 1 query executes before discovery/recovery

**Implementation Details**:
- In `scripts/build-worker-entry.ts`, update the generated wrapper string:
  - Add `import { getDb, withDbTimeout } from "../src/lib/db.js";` to imports
  - Add prewarm block as first operation inside `ctx.waitUntil`:
    ```
    try {
      const db = await getDb();
      await withDbTimeout(() => db.$queryRawUnsafe("SELECT 1"), 5000);
      console.log("[cron] DB prewarm OK");
    } catch (err) {
      console.error("[cron] DB prewarm failed (non-blocking):", err);
    }
    ```
  - Prewarm failure must not block subsequent cron tasks

**Dependencies**: None
**Hint**: opus

---

## Phase 3: Verification

### T-007: Run full test suite and verify no regressions
**User Story**: All | **Status**: [x] Completed
**Test**: Given all optimizations applied → When `npm test` runs → Then all existing + new tests pass

**Implementation Details**:
- Run `npm test` in vskill-platform
- Verify all new tests (TC-001 through TC-005) pass
- Verify existing auth, login, and OAuth callback tests still pass
- Check AC completion across all user stories

**Dependencies**: T-001, T-002, T-003, T-004, T-005, T-006
**Hint**: opus
