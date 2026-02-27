# 0345 — Auth Architecture Rework

## Problem

The vskill-platform authentication causes 10+ second page loads, 500 errors, and inconsistent UI:
1. Every page load triggers client-side `fetch("/api/v1/auth/me")` → Neon DB cold start (1-8s)
2. Blocklist endpoint has race condition on concurrent auto-seeding → 500
3. Auth state only available after React hydration + client fetch → "Checking authentication..." flash
4. Nav shows "Login" while submit page shows "Login with GitHub" — inconsistent

## Solution

Move to server-side JWT-only auth with zero DB calls on page load.

## User Stories

### US-001: Server-side auth resolution
As a user, I want pages to load instantly with my auth state already resolved, so I don't wait 10+ seconds for authentication.

**ACs:**
- [x] AC-US1-01: JWT payload enriched with `avatarUrl` and `isAdmin` fields
- [x] AC-US1-02: New `getServerAuth()` helper verifies JWT from cookies in Server Components (zero DB calls)
- [x] AC-US1-03: Root layout calls `getServerAuth()` and passes `initialUser` to AuthProvider
- [x] AC-US1-04: AuthProvider accepts `initialUser` prop, skips `/me` fetch when provided
- [x] AC-US1-05: Silent token refresh when access token expired but refresh token valid

### US-002: Eliminate DB calls from auth endpoints
As a user, I want the `/me` endpoint to respond instantly without database queries.

**ACs:**
- [x] AC-US2-01: `/api/v1/auth/me` returns JWT claims directly for enriched tokens (zero DB)
- [x] AC-US2-02: Falls back to DB lookup for old tokens (backward compat)
- [x] AC-US2-03: OAuth callback signs enriched tokens with `avatarUrl` + `isAdmin`
- [x] AC-US2-04: Token refresh carries forward enriched claims; self-heals old tokens via DB lookup
- [x] AC-US2-05: Duplicate `getJwtSecret()` in refresh route removed — uses shared export from `auth.ts`

### US-003: Fix blocklist 500 errors
As a user, I want the blocklist endpoint to never return 500 errors.

**ACs:**
- [x] AC-US3-01: Blocklist seeding uses `createMany({ skipDuplicates: true })` instead of upsert loop
- [x] AC-US3-02: KV-based seeding flag prevents unnecessary DB calls after first seed

### US-004: Consolidated auth UI
As a user, I want a consistent login experience across all pages.

**ACs:**
- [x] AC-US4-01: UserNav shows "Login with GitHub" with icon (matches submit page style)
- [x] AC-US4-02: Submit page relies on server-resolved auth state (no "Checking authentication..." flash)
- [x] AC-US4-03: Null `avatarUrl` handled gracefully with fallback
