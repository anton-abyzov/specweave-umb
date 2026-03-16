# Implementation Plan: Unify Admin Auth with GitHub SSO

## Overview

Replace the separate admin email/password auth system with the existing GitHub SSO session. The core change introduces a `requireAdmin()` middleware that tries cookie-based user JWT first (primary path via existing `requireAdminUser()`) and falls back to legacy `Authorization: Bearer` header admin JWT (via existing `requireAuth()`). Admin pages switch from `localStorage` token management to `authFetch()` with cookie-based auth. The admin login page becomes a GitHub SSO gateway.

No new services, tables, or external dependencies. This is a consolidation of two existing auth paths into one unified function, plus a frontend migration from localStorage to cookies.

## Architecture

### Auth Flow — Before vs After

```
BEFORE (two separate paths):

  Admin Login Page ──► POST /auth/login ──► Admin table
       │                    │                    │
       │               admin JWT (aud=admin)     │
       │                    │                    │
       ▼                    ▼                    │
  localStorage ──► Authorization header ──► requireRole()

  GitHub SSO ──► vskill_access cookie ──► requireUser()
       (only for non-admin user features)


AFTER (unified):

  Admin Login Page ──► /api/v1/auth/github?redirect=/admin
       │
       │  (existing GitHub OAuth flow)
       │
       ▼
  vskill_access cookie (isAdmin=true) ──► requireAdmin()
       │                                       │
       │  primary: requireAdminUser()          │
       │  fallback: requireAuth() (header)     │
       ▼                                       ▼
  authFetch() with credentials:"include"   Legacy scripts
```

### Component: `requireAdmin()` in `src/lib/auth.ts`

This is the single new function. It composes two existing functions:

```
requireAdmin(request)
  │
  ├── 1. Try requireAdminUser(request)  [cookie path]
  │      └── requireUser() → verifyUserAccessToken(cookie)
  │      └── isAdminUsername(payload.githubUsername)
  │      └── Returns UserTokenPayload if cookie valid + admin
  │
  ├── 2. If cookie path fails → try requireAuth(request)  [header path]
  │      └── verifyAccessToken(Authorization header)
  │      └── Returns AdminTokenPayload if header valid
  │
  └── 3. Both fail → return 401 error response

Return type: UserTokenPayload | AdminTokenPayload | Response
```

**Key design decision**: The function returns a union type. Route handlers that need to access payload fields must handle both shapes. In practice, most routes only use the result for the `isAuthError()` guard and ignore the payload, so the union type has minimal impact.

### Component: `AdminIdentity` Type

```typescript
type AdminIdentity = UserTokenPayload | AdminTokenPayload;
```

Both types already share the essential field (`sub` from JWTPayload). Routes that need to distinguish can check for `type === 'user'` on the payload. No new type guard needed — the existing `isAuthError()` function already handles the Response case.

### Component: Admin Login Page (`src/app/admin/page.tsx`)

Three states, all rendered by a single client component that calls `GET /api/v1/auth/me` on mount:

```
┌────────────────────────────────────┐
│         Admin Login Page           │
│                                    │
│  State 1: Loading                  │
│  → Spinner while checking session  │
│                                    │
│  State 2: Authenticated + Admin    │
│  → router.push("/admin/dashboard") │
│                                    │
│  State 3: Authenticated + NOT admin│
│  → "No admin access" + username    │
│  → Link back to main site          │
│                                    │
│  State 4: Not authenticated        │
│  → "Sign in with GitHub" button    │
│  → href="/api/v1/auth/github       │
│     ?redirect=/admin"              │
└────────────────────────────────────┘
```

The `?redirect=/admin` query param sets the `vskill_redirect` cookie, so the GitHub OAuth callback redirects back to `/admin` after login. The page then detects the session and auto-redirects to dashboard.

### Component: Admin Layout (`src/app/admin/layout.tsx`)

Changes:
1. Replace `localStorage.removeItem("admin_token")` logout with `POST /api/v1/auth/logout` + redirect
2. Replace hardcoded "A" avatar + "Admin" text with GitHub avatar URL + username from `/api/v1/auth/me`
3. Add `useEffect` to proactively clear legacy `admin_token` and `admin_refresh_token` from localStorage
4. Add session check: if `/api/v1/auth/me` returns 401 (after refresh attempt), redirect to `/admin`
5. Add proactive token refresh scheduler based on `vskill_token_exp` cookie

### Component: Proactive Token Refresh Hook

```typescript
// useTokenRefresh.ts — custom hook used by admin layout

function useTokenRefresh() {
  useEffect(() => {
    function scheduleRefresh() {
      const expCookie = document.cookie
        .split('; ')
        .find(c => c.startsWith('vskill_token_exp='));
      if (!expCookie) return;

      const expSec = parseInt(expCookie.split('=')[1], 10);
      const nowSec = Math.floor(Date.now() / 1000);
      const msUntilRefresh = (expSec - nowSec - 60) * 1000; // 60s before expiry

      if (msUntilRefresh <= 0) {
        // Already due — refresh immediately
        doRefresh();
        return;
      }

      return setTimeout(doRefresh, msUntilRefresh);
    }

    async function doRefresh() {
      const res = await fetch('/api/v1/auth/user/refresh', {
        method: 'POST',
        credentials: 'include',
      });
      if (res.ok) {
        scheduleRefresh(); // reschedule with new expiry
      } else {
        window.location.href = '/admin'; // session expired
      }
    }

    const timer = scheduleRefresh();
    return () => { if (timer) clearTimeout(timer); };
  }, []);
}
```

This reads the non-HttpOnly `vskill_token_exp` cookie (already set by `setAuthCookies()`) and schedules a refresh 60 seconds before expiry. The existing `POST /api/v1/auth/user/refresh` endpoint handles token rotation and sets new cookies.

### Component: Admin Page Migration (8 pages)

Each admin page currently follows this pattern:
```typescript
const token = localStorage.getItem("admin_token");
const res = await fetch("/api/v1/admin/...", {
  headers: { Authorization: `Bearer ${token}` },
});
```

Migration is mechanical — replace with:
```typescript
import { authFetch } from "@/lib/auth-fetch";
const res = await authFetch("/api/v1/admin/...");
```

`authFetch()` already handles `credentials: "include"` and 401 refresh retry.

Pages to migrate:
1. `dashboard/page.tsx` — 2 fetch call sites
2. `submissions/page.tsx` — uses fetch
3. `submissions/[id]/page.tsx` — uses fetch
4. `queue/page.tsx` — 8 fetch call sites (heaviest)
5. `blocklist/page.tsx` — 3 fetch call sites
6. `evals/page.tsx` — 1 fetch call site
7. `reports/page.tsx` — uses fetch
8. `page.tsx` (login) — complete rewrite

Also remove per-page localStorage guards (replaced by layout session check).

### Component: Admin API Route Migration (54 call sites across 60 route files)

Mechanical replacement in each route:

```
BEFORE:  import { requireRole, isAuthError } from "@/lib/auth";
         const auth = await requireRole(request, "SUPER_ADMIN");

AFTER:   import { requireAdmin, isAuthError } from "@/lib/auth";
         const auth = await requireAdmin(request);
```

**Role semantics**: Currently routes use either `"REVIEWER"` or `"SUPER_ADMIN"`. Since `requireAdmin()` already checks `isAdminUsername()` for the cookie path, and the legacy header path's `verifyAccessToken()` requires `aud: "admin"`, the SUPER_ADMIN/REVIEWER distinction is effectively collapsed. This is acceptable because:
- There is only one admin user (anton-abyzov)
- The spec explicitly states: "all admins are SUPER_ADMIN equivalent"
- Multi-admin with role differentiation is out of scope

For the 2 routes using `requireAuth()` directly (`reports/route.ts`, `reports/[id]/route.ts`): same migration to `requireAdmin()`.

## Technology Stack

No new dependencies. Everything uses existing infrastructure:

- **JWT verification**: `jose` (already used)
- **Cookie management**: `auth-cookies.ts` (already exists)
- **Client fetch**: `auth-fetch.ts` / `authFetch()` (already exists)
- **OAuth flow**: `github-oauth.ts` + `/api/v1/auth/github` (already exists)
- **Token refresh**: `POST /api/v1/auth/user/refresh` (already exists)
- **Session check**: `GET /api/v1/auth/me` (already exists)

## Architecture Decisions

### AD-1: Compose existing functions, do not duplicate logic

`requireAdmin()` calls `requireAdminUser()` then falls back to `requireAuth()`. It does not re-implement JWT verification or cookie reading. This ensures a single source of truth for token validation and avoids divergence.

### AD-2: Union return type over normalized identity object

Returning `UserTokenPayload | AdminTokenPayload` directly rather than normalizing into a new `AdminIdentity` interface. Rationale: most call sites only do `if (isAuthError(auth)) return auth;` and never inspect the payload. Creating a normalized wrapper would add unnecessary mapping code for zero practical benefit.

### AD-3: Layout-level auth gate, not per-page

The admin layout checks the session once via `/api/v1/auth/me` and redirects to `/admin` if unauthenticated. Individual admin pages no longer need their own auth guards. This eliminates 8 independent localStorage checks and centralizes the auth UX.

### AD-4: Proactive refresh in layout via cookie timestamp

Using the existing `vskill_token_exp` non-HttpOnly cookie rather than decoding the JWT client-side. The cookie is already set by `setAuthCookies()` and contains only a Unix timestamp (no security data). This avoids adding a JWT decode library to the client bundle.

### AD-5: Legacy localStorage cleanup on mount, not on build

The layout clears `admin_token` and `admin_refresh_token` from localStorage via a `useEffect` rather than removing the code entirely. This ensures any tokens cached in the browser are cleaned up on first visit after deployment, preventing stale credentials from persisting.

## Implementation Phases

### Phase 1: Core Middleware (US-001)

1. Add `requireAdmin()` function to `src/lib/auth.ts`
2. Export `AdminIdentity` type alias
3. Unit test all 4 AC paths: cookie+admin, cookie+non-admin, header-only, neither

### Phase 2: Admin Login Page Rewrite (US-002)

1. Rewrite `src/app/admin/page.tsx` — replace email/password form with GitHub SSO gateway
2. Three states: loading, authenticated (redirect or denied), unauthenticated (GitHub button)
3. GitHub auth link uses `?redirect=/admin` for post-callback return

### Phase 3: Admin Layout Upgrade (US-003, US-006)

1. Add session check with `/api/v1/auth/me` on mount
2. Replace hardcoded avatar/name with GitHub identity
3. Replace localStorage logout with cookie-based logout
4. Add legacy localStorage cleanup
5. Add proactive token refresh hook (`useTokenRefresh`)

### Phase 4: Admin Page Migration (US-005)

1. Replace all `localStorage.getItem("admin_token")` + manual `Authorization` header with `authFetch()`
2. Remove per-page auth guards (layout handles it)
3. Pages: dashboard, submissions, submissions/[id], queue, blocklist, evals, reports

### Phase 5: Admin API Route Migration (US-004)

1. Replace all `requireRole(request, ...)` / `requireAuth(request)` calls with `requireAdmin(request)` across 54 call sites in 60 route files
2. Update imports in each file
3. Verify no remaining references to old pattern

## Testing Strategy

### Unit Tests
- `requireAdmin()`: 4 paths (cookie+admin, cookie+non-admin, header-valid, neither)
- `useTokenRefresh` hook: schedule timing, refresh success/failure, cleanup

### Integration Tests
- Admin login page: 3 states (already logged in + admin, logged in + not admin, not logged in)
- Admin layout: session detection, logout flow, localStorage cleanup
- End-to-end: GitHub SSO -> admin dashboard access

### Migration Verification
- Grep scan: zero remaining `requireRole` / `requireAuth` in admin routes
- Grep scan: zero remaining `localStorage.getItem("admin_token")` in admin pages
- All existing admin page tests updated to mock `authFetch` instead of localStorage

## Technical Challenges

### Challenge 1: 54 call sites across 60 route files
**Solution**: The migration is mechanical (same replacement pattern everywhere). Can be done in bulk with search-and-replace, validated by grep for remaining old patterns.
**Risk**: Missing a file. Mitigated by the grep verification step.

### Challenge 2: Union return type in route handlers
**Solution**: Most routes only check `isAuthError(auth)` and ignore the payload. The 3-4 routes that access `auth.email` or `auth.role` (e.g., `submissions/[id]/reject` for audit logging) need a type narrowing check: `if ('email' in auth)` or `if ('type' in auth && auth.type === 'user')`.
**Risk**: Type errors at compile time (caught immediately).

### Challenge 3: Race between layout session check and page render
**Solution**: Layout shows a loading state while checking session. Child pages render only after auth is confirmed. The layout uses a React context or state to gate rendering.
**Risk**: Brief flash of loading spinner (acceptable UX).

### Challenge 4: Token refresh timing precision
**Solution**: Schedule refresh 60 seconds before expiry (conservative buffer). If the timer fires and the token is already expired, `authFetch()` handles the 401 retry as a safety net.
**Risk**: Network latency causing refresh to arrive after expiry. Mitigated by the 60-second buffer and `authFetch()` fallback.
