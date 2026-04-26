---
increment: 0738-vskill-platform-auth-refresh-401-fix
---

# Plan: vskill-platform auth-refresh 401 hardening

## Design

### Architecture (component view)

```
                    ┌───────────────────────────────────────┐
                    │  src/lib/auth-refresh-client.ts (NEW) │
                    │  refreshUserSession(): Promise<R>     │
                    │  - module-scoped `inflight` Promise   │
                    │  - 500 ms post-settle TTL             │
                    └────────────┬───────────────┬──────────┘
                                 │               │
        imports from             │               │     imports from
        ┌────────────────────────┘               └─────────────────────┐
        ▼                                                              ▼
 src/lib/auth-fetch.ts                          src/app/components/AuthProvider.tsx
 (drops local refreshPromise,                    (drops refreshingRef,
  delegates to refreshUserSession)                consumes user from refreshUserSession)
        │                                                              │
        └────────────────────┬─────────────────────────────────────────┘
                             ▼
                   POST /api/v1/auth/user/refresh
                             │
                             ▼
                ┌──────────────────────────────────────────────┐
                │  route.ts (MODIFIED — Fix A grace window)    │
                │  1. read cookie → jwtVerify                  │
                │  2. deleteMany(oldHash)                       │
                │  3a. count > 0  → create new + 200            │
                │  3b. count == 0 → findFirst createdAt>now-10s │
                │      ↳ found    → mint fresh tokens + 200    │
                │      ↳ none     → 401 (existing behavior)     │
                └──────────────────────────────────────────────┘

Cookie surface (Fix C):
  src/lib/auth-cookies.ts:13, 44, 62  →  sameSite: "lax"
```

### Fix A — server idempotent rotation grace window
**File**: `src/app/api/v1/auth/user/refresh/route.ts`

After the existing retry loop sets `rotationResult = null` (because `deleted.count === 0`), insert a recovery branch BEFORE the 401 return. The retry loop is left intact for transient DB errors. The grace path runs exactly once per request and only when `deleted.count === 0`.

```ts
if (!rotationResult) {
  const recent = await withDbTimeout(() =>
    prisma.userRefreshToken.findFirst({
      where: { userId, createdAt: { gt: new Date(Date.now() - 10_000) } },
      orderBy: { createdAt: "desc" },
      select: { id: true, expiresAt: true },
    }),
  );

  if (!recent) {
    return errorResponse("Refresh token not found or expired", 401);
  }

  // Sibling request rotated within the grace window — mint a fresh pair.
  // Identity is already verified by jwtVerify above (line 39-45).
  const [graceAccess, graceRefresh] = await Promise.all([
    signUserAccessToken(tokenPayload),
    signUserRefreshToken(tokenPayload),
  ]);
  const graceHash = await hashToken(graceRefresh);
  const expiresAt2 = new Date();
  expiresAt2.setDate(expiresAt2.getDate() + 7);
  await withDbTimeout(() =>
    prisma.userRefreshToken.create({
      data: { userId, token: graceHash, expiresAt: expiresAt2 },
    }),
  );
  rotationResult = { newAccessToken: graceAccess, newRefreshToken: graceRefresh };
}
```

**Why mint fresh tokens, not return the sibling's tokens?**
The sibling's tokens were transmitted in its own `Set-Cookie` response and are not retrievable from this request's context (HTTP-only cookies are unidirectional). Minting a parallel pair is safe because (a) the OLD token has been deleted, and (b) the JWT signature has been verified against `getJwtSecret()` so we already know the request came from a legitimate session. The user ends up with two valid refresh tokens for ~7 days — acceptable; both are tied to the same user, both expire on the same schedule, and the next refresh from either tab rotates only its own.

### Fix B — shared in-flight refresh promise
**New file**: `src/lib/auth-refresh-client.ts`

```ts
import type { AuthUser } from "@/app/components/AuthProvider";

export interface RefreshResult {
  success: boolean;
  user?: AuthUser;
}

let inflight: Promise<RefreshResult> | null = null;

export function refreshUserSession(): Promise<RefreshResult> {
  if (inflight) return inflight;

  inflight = (async () => {
    try {
      const res = await fetch("/api/v1/auth/user/refresh", {
        method: "POST",
        credentials: "include",
      });
      if (!res.ok) return { success: false };
      const data = (await res.json()) as { user?: AuthUser };
      return data?.user?.id ? { success: true, user: data.user } : { success: false };
    } catch {
      return { success: false };
    } finally {
      setTimeout(() => {
        inflight = null;
      }, 500);
    }
  })();

  return inflight;
}

// Test-only — reset between tests.
export function __resetRefreshClientForTests(): void {
  inflight = null;
}
```

`auth-fetch.ts` simplification — replace the local `refreshPromise` + `attemptRefresh` (lines 32-54) with `refreshUserSession()` import and call site update on line 285.

`AuthProvider.tsx` simplification — replace `refreshingRef` + inline fetch (lines 55, 58-79) with `refreshUserSession()` import. The user-data shape (`{ id, githubUsername, avatarUrl, isAdmin }`) is what AuthProvider consumes; the shared module returns it.

### Fix C — cookie SameSite revert
**File**: `src/lib/auth-cookies.ts`

Three character-level edits:

- Line 13: `sameSite: "strict" as const,` → `sameSite: "lax" as const,`
- Line 44: same
- Line 62: same

CSRF defense remains enforced by `src/middleware.ts:28-52` Origin allowlist. `SameSite=Lax` is the OWASP-recommended default for auth cookies and tolerates the GET that loads `/submit` from external origins.

### Compatibility / migration

- No DB migration: `UserRefreshToken.createdAt` already present (`prisma/schema.prisma:135-145`).
- No env var changes.
- Cookie attribute change rolls forward on next `setAuthCookies()` call (login, refresh). Existing `Strict` cookies in browsers continue to work for their TTL — they only become `Lax` after the next refresh response.

## Rationale

### Why not move back to `$transaction`?
Commit `41ef396` dropped `$transaction` because Prisma+Neon HTTP mode is stateless. Reverting would break the platform on Cloudflare. The grace window is the architecturally compatible fix.

### Why 10 s, not 5 s or 60 s?
- ≥ 5 s: covers Neon cold-start (worst observed: ~3 s) plus a multi-tab gap.
- ≤ 60 s: keeps the replay-detection signal sharp. A token presented 11 s after rotation is genuinely stale and worth 401-ing.
- 10 s: middle of the band, easy to reason about, easy to tune later if telemetry shows otherwise.

### Why a 500 ms client-side TTL on the shared Promise?
- Long enough to absorb StrictMode dev double-mount and the AuthProvider mount + visibility ping that fires within ~1 frame.
- Short enough that a user clicking "log in again" 600 ms later doesn't reuse a stale Promise.

### Why not lockfile / mutex on the server?
Cloudflare Workers have no shared memory across isolates; a mutex would require Durable Objects or Redis. Both are overkill for what is a benign double-rotation. The grace window converts a "loser" into a "winner with extra tokens" without any cross-isolate coordination.

### Why not extend `auth-fetch.ts` itself instead of extracting?
`auth-fetch.ts` is 290 lines and already mixes auth refresh + workspace lockdown (0723) + telemetry. Extraction is consistent with the file's existing direction (each concern in its own module) and yields a small module that is trivially unit-testable.

## Risks and mitigations

| Risk | Mitigation |
|---|---|
| Grace window masks a real replay attack | Window is 10 s; OLD token is deleted by the legitimate winner; attacker without the cookie plaintext cannot trigger the path |
| Two valid refresh tokens per user (one per concurrent rotation) | Acceptable — both expire on schedule; OWASP rotation does not require strict 1-token invariant |
| Shared Promise leaks across tabs | It does not — `inflight` is module-scoped per JS execution context; tabs have separate contexts |
| `SameSite=Lax` weakens CSRF defense | It does not — middleware Origin allowlist is the active defense; `Lax` is the OWASP default for auth cookies |
| Existing `auth-fetch.test.ts` may break on import-graph change | Update those tests; behavioral contract (deduped 401-retry) is preserved |
