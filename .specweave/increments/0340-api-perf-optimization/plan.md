---
increment: 0340-api-perf-optimization
type: plan
status: planned
---

# Architecture Plan: API Performance Optimization

## ADR Reference

- **ADR-0244**: Isolate-Lifetime Caching for Worker Secrets (new, see below)

## Architecture Overview

Six independent, low-risk optimizations to the vskill-platform Worker. Each targets a different layer of the request lifecycle. No new services, schemas, or API endpoints. All changes are confined to existing files.

```
Request Flow (current):
  CF Edge → Worker → resolveEnv() → getDb() → resolveEnv() again → query → respond

Request Flow (optimized):
  CF Edge → Smart Placement → Worker (near DB region)
    → cached JWT secret (skip resolveEnv on hot path)
    → getDb() || checkRateLimit() (parallel)
    → query → respond immediately
    → waitUntil: lastLoginAt + refresh token storage (deferred)
```

## Component Breakdown

### C1: wrangler.jsonc — Smart Placement

**Change**: Add `"placement": { "mode": "smart" }` top-level key.

**Risk**: None. Smart Placement is GA and gracefully degrades. Workers that don't benefit (e.g., no backend calls) run as normal.

**Files**: `wrangler.jsonc`

---

### C2: src/lib/auth.ts — JWT Secret Cache + Dynamic bcrypt

Two changes in the same file, grouped to minimize churn:

**JWT Cache**:
```typescript
// Module-level cache — lives for the isolate lifetime
let _cachedJwtSecret: Uint8Array | null = null;

async function getJwtSecret(): Promise<Uint8Array> {
  if (_cachedJwtSecret) return _cachedJwtSecret;
  // ... existing resolve chain ...
  _cachedJwtSecret = new TextEncoder().encode(secret);
  return _cachedJwtSecret;
}
```

No TTL. Isolate recycling on deploy naturally rotates the cache. This matches how `_cachedClient` in `db.ts` already works.

**Dynamic bcrypt**:
```typescript
// Remove: import bcrypt from 'bcryptjs';
// Add lazy loader:
let _bcrypt: typeof import('bcryptjs') | null = null;
async function getBcrypt() {
  if (!_bcrypt) _bcrypt = await import('bcryptjs');
  return _bcrypt;
}

export async function hashPassword(password: string): Promise<string> {
  const bcrypt = await getBcrypt();
  return bcrypt.default.hash(password, BCRYPT_ROUNDS);
}

export async function verifyPassword(password: string, hash: string): Promise<boolean> {
  const bcrypt = await getBcrypt();
  return bcrypt.default.compare(password, hash);
}
```

Note: `await import('bcryptjs')` returns a module namespace object, so access via `.default` for the default export.

**Files**: `src/lib/auth.ts`

---

### C3: src/app/api/v1/auth/login/route.ts — Parallelization + waitUntil

Restructure the login route to:

1. Start `getDb()` concurrently with rate-limit check (both need `getCloudflareContext`, but `getDb` does its own resolution)
2. Obtain `ctx` from the same `getCloudflareContext({ async: true })` call used for rate limiting
3. After generating tokens, return response immediately
4. Defer `lastLoginAt` update and refresh token create via `ctx.waitUntil()`

**Pseudocode**:
```typescript
export async function POST(request: NextRequest) {
  try {
    const { env, ctx } = await getCloudflareContext({ async: true });

    // Start DB connection concurrently with rate-limit check
    const dbPromise = getDb();

    // Rate limit check (uses env.RATE_LIMIT_KV)
    if (env.RATE_LIMIT_KV) {
      const ip = ...;
      const rl = await checkRateLimit(env.RATE_LIMIT_KV, `login:${ip}`, 5, 900);
      if (!rl.allowed) return 429;
    }

    // Parse + validate body
    const { email, password } = parsed.data;
    const prisma = await dbPromise; // DB should be ready by now

    // ... findUnique, verifyPassword, signTokens (same as before) ...

    // Build response
    const response = jsonResponse({ accessToken, refreshToken, admin: {...} });

    // Defer non-critical writes
    ctx.waitUntil((async () => {
      const hashedRefresh = await hashToken(refreshToken);
      await Promise.allSettled([
        prisma.refreshToken.create({ data: { adminId, token: hashedRefresh, expiresAt } }),
        prisma.admin.update({ where: { id: admin.id }, data: { lastLoginAt: new Date() } }),
      ]);
    })());

    return response;
  } catch { ... }
}
```

**Key detail**: The `getCloudflareContext({ async: true })` call is already present in the login route for rate limiting. We reuse its `ctx` for `waitUntil`. This means one less `getCloudflareContext` call compared to current code (where `getDb` calls `resolveEnv` which calls `getCloudflareContext` separately).

**Fallback**: If `getCloudflareContext` fails (local dev), fall back to sequential writes (existing behavior). The `try/catch` around rate limiting already handles this.

**Files**: `src/app/api/v1/auth/login/route.ts`

---

### C4: src/app/api/v1/auth/github/callback/route.ts — waitUntil for Refresh Token

The OAuth callback already marks refresh token storage as "best-effort" (step 7 has try/catch). Move it to `waitUntil`.

```typescript
// After building response and setting cookies:
try {
  const { ctx } = await getCloudflareContext({ async: true });
  ctx.waitUntil((async () => {
    const expiresAt = new Date();
    expiresAt.setDate(expiresAt.getDate() + 7);
    const hashedToken = await hashToken(refreshToken);
    await prisma.userRefreshToken.create({
      data: { userId: dbUser.id, token: hashedToken, expiresAt },
    });
  })());
} catch {
  // waitUntil unavailable (local dev) — skip, refresh token storage is best-effort
}
```

**Files**: `src/app/api/v1/auth/github/callback/route.ts`

---

### C5: scripts/build-worker-entry.ts — DB Prewarm in Cron

Add a prewarm step as the first operation inside the `scheduled` handler's `ctx.waitUntil` block.

**In the generated wrapper string**:
```javascript
import { getDb, withDbTimeout } from "../src/lib/db.js";

// Inside scheduled handler, first line of waitUntil:
try {
  const db = await getDb();
  await withDbTimeout(() => db.$queryRawUnsafe("SELECT 1"), 5000);
  console.log("[cron] DB prewarm OK");
} catch (err) {
  console.error("[cron] DB prewarm failed (non-blocking):", err);
}
```

Uses `withDbTimeout` (already exists in `db.ts`) with 5s timeout to avoid blocking cron if Neon is genuinely down. The `$queryRawUnsafe("SELECT 1")` bypasses the `$extends` interceptor's model requirement.

**Files**: `scripts/build-worker-entry.ts`

---

## Testing Strategy (TDD)

All tests use Vitest. TDD mode: write failing test first, implement, refactor.

### T1: JWT Secret Cache Test (`src/lib/__tests__/auth.test.ts`)

```typescript
describe("getJwtSecret caching", () => {
  it("calls resolveEnv once across multiple invocations", async () => {
    // Mock resolveEnv, call signAccessToken twice, verify resolveEnv called once
  });
});
```

Expose `getJwtSecret` for testing (or test indirectly via `signAccessToken` + `verifyAccessToken` calling resolveEnv).

**Approach**: Mock `resolveEnv` at module level. Call `signAccessToken` twice. Assert `resolveEnv` was called exactly once. Reset module state between tests by using `vi.resetModules()`.

### T2: waitUntil Deferred Test (`src/app/api/v1/auth/login/__tests__/route.test.ts`)

```typescript
it("defers lastLoginAt and refresh token to waitUntil", async () => {
  const waitUntilSpy = vi.fn();
  vi.mocked(getCloudflareContext).mockResolvedValue({
    env: { RATE_LIMIT_KV: mockKv },
    ctx: { waitUntil: waitUntilSpy },
  });
  // POST login → assert waitUntilSpy.mock.calls.length === 1
  // Await the promise passed to waitUntil → verify DB writes happened
});
```

### T3: Dynamic bcrypt Import Test (`src/lib/__tests__/auth.test.ts`)

```typescript
describe("dynamic bcrypt import", () => {
  it("loads bcryptjs only when hashPassword is called", async () => {
    // signAccessToken should NOT trigger bcrypt import
    // hashPassword should trigger it
  });
});
```

### T4: Login Parallelization Test

Verify `getDb()` is initiated before rate-limit check completes. This is structural (code review) but can be tested by checking that the DB promise is created before `checkRateLimit` resolves.

## Task Dependency Graph

```
T-001 (Smart Placement) ─────────────────────── no deps
T-002 (JWT cache + tests) ──────────────────── no deps
T-003 (Dynamic bcrypt + tests) ─────────────── no deps
T-004 (Login parallelization + waitUntil) ──── depends on T-002 (cached JWT used in login)
T-005 (OAuth callback waitUntil) ───────────── no deps
T-006 (Cron DB prewarm) ───────────────────── no deps
```

T-001, T-002, T-003, T-005, T-006 can all be done in parallel. T-004 should follow T-002 since the login route will use the cached JWT path.

## Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Smart Placement routes Worker away from user | Low | Low | CF's algorithm optimizes for backend latency; front-end assets served from edge CDN regardless |
| Deferred write fails silently | Medium | Low | `lastLoginAt` and refresh token storage are already best-effort; add console.error in waitUntil catch |
| Dynamic import breaks bundling | Low | Medium | Cloudflare Workers support dynamic `import()` for ESM modules; test in staging |
| JWT cache serves stale secret after rotation | Very Low | Medium | Rotation only happens during deploy which recycles isolates; explicitly documented as acceptable |

## Files Modified (Complete List)

1. `wrangler.jsonc` — add placement config
2. `src/lib/auth.ts` — JWT cache + dynamic bcrypt
3. `src/app/api/v1/auth/login/route.ts` — parallel getDb + waitUntil
4. `src/app/api/v1/auth/github/callback/route.ts` — waitUntil for refresh token
5. `scripts/build-worker-entry.ts` — DB prewarm in cron wrapper
6. `src/lib/__tests__/auth.test.ts` — new tests for JWT cache + dynamic bcrypt
7. `src/app/api/v1/auth/login/__tests__/route.test.ts` — new/updated tests for waitUntil + parallelization (create if not exists)
