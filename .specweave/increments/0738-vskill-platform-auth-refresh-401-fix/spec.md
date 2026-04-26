---
increment: 0738-vskill-platform-auth-refresh-401-fix
title: 'vskill-platform: fix intermittent 401 on /api/v1/auth/user/refresh'
type: bug
priority: P1
status: completed
created: 2026-04-26T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: vskill-platform — fix intermittent 401 on /api/v1/auth/user/refresh

## Overview

Users on `/submit` intermittently see `401 Unauthorized` from `POST /api/v1/auth/user/refresh`. Three independent, stacked causes were verified by parallel investigation:

1. **Non-atomic rotation** (`src/app/api/v1/auth/user/refresh/route.ts:104-105, 122-124`) — `deleteMany` then `create` is no longer wrapped in `$transaction` (commit `41ef396`). Two concurrent requests with the same refresh cookie compute the same `oldTokenHash`; the loser's `deleteMany` returns `count === 0` and the route returns 401.
2. **Split client dedup** — `src/lib/auth-fetch.ts:32-54` has a 1 s in-flight Promise cache; `src/app/components/AuthProvider.tsx:55, 58-79` uses only a `refreshingRef` boolean. They cannot dedupe across each other, so an `authFetch` 401-retry can race AuthProvider's mount/visibility refresh **in the same tab**. Multi-tab is wholly unprotected.
3. **`SameSite=Strict` cookie strip** (`src/lib/auth-cookies.ts:13, 44, 62`, commit `fc24418`) — strips the refresh cookie on cross-site navigation entry to `/submit` (Gmail link, Google search, OAuth callback), so the very first POST returns 401 `"Missing refresh token"`. CSRF defense already lives in `src/middleware.ts:28-52` via Origin allowlist, so `Strict` was a hardening overshoot.

## User Stories

### US-001: Concurrent refreshes never 401 the loser (P1)
**Project**: vskill-platform

**As a** logged-in user with multiple tabs of `/submit` open
**I want** simultaneous silent refreshes to all succeed
**So that** I am never silently logged out by a race I cannot perceive or avoid

**Acceptance Criteria**:
- [x] **AC-US1-01**: When two requests arrive at `/api/v1/auth/user/refresh` with the same valid refresh cookie within 10 s, both receive `200 OK` with newly minted access + refresh tokens.
- [x] **AC-US1-02**: When a request arrives more than 10 s after the matching token row was rotated, the route returns `401` with the existing `"Refresh token not found or expired"` body — replay-detection unchanged.
- [x] **AC-US1-03**: The grace-window lookup uses an indexed query (`UserRefreshToken.userId` index, `prisma/schema.prisma:144`) — no full-table scan.
- [x] **AC-US1-04**: The retry loop on transient DB errors (`route.ts:96-120`) is preserved; the grace-window branch only fires when `deleteMany` legitimately returned `count === 0`.

### US-002: One refresh per tab, regardless of trigger (P1)
**Project**: vskill-platform

**As a** logged-in user
**I want** a single in-flight refresh promise shared across every client caller
**So that** the AuthProvider mount/visibility scheduler and the `authFetch` 401-retry never fire two POSTs to `/api/v1/auth/user/refresh` for the same cookie

**Acceptance Criteria**:
- [x] **AC-US2-01**: A new module `src/lib/auth-refresh-client.ts` exposes `refreshUserSession()` returning a shared in-flight `Promise<RefreshResult>`; concurrent callers receive the **same** Promise reference.
- [x] **AC-US2-02**: `src/lib/auth-fetch.ts` no longer maintains its own `refreshPromise`; it imports and calls `refreshUserSession()`.
- [x] **AC-US2-03**: `src/app/components/AuthProvider.tsx` no longer maintains its own `refreshingRef`; it imports and calls `refreshUserSession()` from both the mount effect and the visibility-change handler.
- [x] **AC-US2-04**: The shared Promise is cleared 500 ms after settle so subsequent user-initiated refreshes are not held back by stale dedup state.
- [x] **AC-US2-05**: React StrictMode dev double-mount of AuthProvider produces exactly one POST to `/api/v1/auth/user/refresh`.

### US-003: Cold loads from external referrers succeed (P1)
**Project**: vskill-platform

**As a** logged-in user clicking a link to `/submit` from Gmail, Google, or an OAuth callback
**I want** my refresh cookie to be sent on the first POST
**So that** I am not bounced to login by an empty-cookie 401

**Acceptance Criteria**:
- [x] **AC-US3-01**: `src/lib/auth-cookies.ts` sets `sameSite: "lax"` on `vskill_access`, `vskill_refresh`, and `vskill_token_exp` cookies.
- [x] **AC-US3-02**: A request arriving on `/submit` from a non-verified-skill.com referrer carries the `vskill_refresh` cookie and the subsequent POST `/api/v1/auth/user/refresh` succeeds. **Verification**: unit-asserted via `auth-cookies.test.ts` (Set-Cookie header carries `SameSite=Lax`); browser-level cross-site nav verified manually because Playwright's `setExtraHTTPHeaders` cannot synthesize a real cross-site navigation that exercises the SameSite cookie-attachment policy.
- [x] **AC-US3-03**: CSRF protection remains enforced — `src/middleware.ts` still rejects mutating cookie-auth requests whose `Origin` header is outside the allowlist (`verified-skill.com`, `www.verified-skill.com`, localhost in dev).

## Functional Requirements

### FR-001: Server grace window
On `deleteMany` returning `count === 0` the route MUST query the most recent `UserRefreshToken` row for `userId` with `createdAt > NOW() - 10s`. If found, mint fresh tokens and return 200 (idempotent rotation success). If not found, return 401 (existing behavior).

### FR-002: Shared client refresh module
A single module owns the in-flight `Promise` for `/api/v1/auth/user/refresh`. Both `auth-fetch.ts` and `AuthProvider.tsx` MUST import and call it; neither may maintain its own dedup state. The module returns `{ success: boolean; user?: AuthUser }` so `AuthProvider` can update state without a second `/auth/me` round-trip.

### FR-003: Cookie SameSite policy
Auth cookies (`vskill_access`, `vskill_refresh`, `vskill_token_exp`) MUST set `SameSite=Lax`. CSRF defense is provided by `middleware.ts` Origin validation; `SameSite=Strict` is redundant for our threat model.

## Success Criteria

- Zero `401` responses from `/api/v1/auth/user/refresh` in production for valid refresh cookies (measured against last 7 days of logs).
- E2E test pair `auth-refresh-race.spec.ts` + `submit-cold-load.spec.ts` green.
- All four unit-test additions green; existing 18 auth-related unit tests remain green.
- Manual two-tab `/submit` smoke produces zero 401 in network panel.

## Known limitations

- **10 s grace window vs revocation lag** — the grace path queries by `userId` only (not by the specific token). After any successful login/rotation for a user, a previously-revoked token presented to `/auth/user/refresh` within the next 10 s will be re-validated and a fresh pair minted. This is a deliberate trade-off: the alternative (binding the grace lookup to the request's stale token hash) loses the very signal the grace window relies on (the stale token is, by definition, already deleted). Multi-device "logout everywhere" remains correct because the next refresh from the revoked device after that 10 s window is rejected. **Threat-model note**: an attacker who has obtained the refresh-token plaintext (XSS, malicious extension, shared device) gets at most a 10 s replay window per subsequent legitimate user activity — bounded but non-zero. Tightening would require a per-user revocation marker (e.g., `User.tokensRevokedAt`); recommended as a follow-up if telemetry shows abuse.
- **Cross-site cold-load is unit-asserted, not E2E-asserted** — the `SameSite=Lax` cookie attribute is verified by `auth-cookies.test.ts` against the literal `Set-Cookie` header. End-to-end browser-level cross-site navigation cannot be reliably synthesized in our Playwright setup (`setExtraHTTPHeaders` does not change the request's site origin). Manual verification: paste a deployed preview URL into a Gmail message and click — the first POST `/auth/user/refresh` must succeed.
- **Multi-tab grace path can leave N parallel `UserRefreshToken` rows for one user** — each concurrent grace-path request inserts its own row. All expire on the same 7-day schedule and self-rotate normally, but a heavy user with many tabs can accumulate stale rows. Acceptable for now; consider a row-count cap or scheduled cleanup if telemetry shows row-count drift.

## Out of Scope

- Admin `/api/v1/auth/refresh` route (separate audit; same `deleteMany`+`create` race exists, no user reports yet — flagged by code-review F-002, follow-up increment recommended).
- `src/app/admin/hooks/useTokenRefresh.ts` missing `credentials: 'include'` (different surface).
- Rotating the JWT signing secret.
- Migrating to a transactional DB driver (would obviate the grace window but is a multi-week project).

## Dependencies

- Prisma model `UserRefreshToken` already exposes `createdAt` (default `now()`, `prisma/schema.prisma:135-145`) and a `userId` index — no migration required.
- `middleware.ts` Origin allowlist is the active CSRF defense; this increment depends on it remaining in place.
