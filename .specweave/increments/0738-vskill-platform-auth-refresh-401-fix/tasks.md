---
increment: 0738-vskill-platform-auth-refresh-401-fix
---

# Tasks: vskill-platform — auth-refresh 401 hardening

All tasks follow STRICT TDD (RED → GREEN → REFACTOR). Test code lands before production code.

> **Repo**: All file paths below are relative to `repositories/anton-abyzov/vskill-platform/`.

---

### T-001: RED — failing unit test for grace-window success
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-03 | **Status**: [x] completed
**File**: `src/app/api/v1/auth/user/refresh/__tests__/route.test.ts`
**Test Plan**:
- **Given** a valid refresh cookie and a `UserRefreshToken` row whose hash matches that cookie
- **When** two near-simultaneous POSTs to `/api/v1/auth/user/refresh` arrive (simulated by two awaited handlers sharing the same DB mock that returns `count:0` for the second `deleteMany`, plus `findFirst` returning a row created < 10s ago for the second)
- **Then** both responses are `200 OK` and both bodies contain a fresh `user` object
- **Then** `findFirst` was called exactly once on the second request with `where: { userId, createdAt: { gt: <10s window> } }` and `orderBy: { createdAt: 'desc' }`
- Test must FAIL on current code (which returns 401 on count=0).

### T-002: RED — failing unit test for grace-window expiry
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02 | **Status**: [x] completed
**File**: `src/app/api/v1/auth/user/refresh/__tests__/route.test.ts`
**Test Plan**:
- **Given** `deleteMany` returns `count:0` and `findFirst` returns `null` (no row in last 10s)
- **When** POST `/api/v1/auth/user/refresh` is invoked
- **Then** response is `401` with body `{ error: "Refresh token not found or expired" }`
- Confirms replay-detection unchanged for legitimately stale tokens.

### T-003: RED — failing unit test for shared client refresh dedup
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-04, AC-US2-05 | **Status**: [x] completed
**File**: `src/lib/__tests__/auth-refresh-client.test.ts` (NEW)
**Test Plan**:
- **Given** the new module `src/lib/auth-refresh-client.ts` exists
- **When** two concurrent calls to `refreshUserSession()` are made
- **Then** they receive the same Promise reference and `fetch` is called exactly once
- **When** the Promise settles and 500 ms elapse (use `vi.useFakeTimers`)
- **Then** a third call to `refreshUserSession()` triggers a new `fetch`
- Tests `__resetRefreshClientForTests()` correctly clears state between cases.
- Test must FAIL because the module does not yet exist.

### T-004: RED — failing unit test for SameSite=Lax cookie attribute
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01 | **Status**: [x] completed
**File**: `src/lib/__tests__/auth-cookies.test.ts`
**Test Plan**:
- **Given** a `NextResponse` and `setAuthCookies(response, "access", "refresh")`
- **When** the response is inspected
- **Then** the `Set-Cookie` headers for `vskill_access`, `vskill_refresh`, `vskill_token_exp` all contain `SameSite=Lax`
- Same assertion in `clearAuthCookies` for the expiry cookie clear path.
- Test must FAIL on current code (Strict).

### T-005: RED — failing E2E for refresh race
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-04 | **Status**: [x] completed
**File**: `tests/e2e/authenticated/auth-refresh-race.spec.ts` (NEW)
**Test Plan**:
- **Given** an authenticated browser context with valid `vskill_refresh` cookie
- **When** `Promise.all([fetch('/api/v1/auth/user/refresh', { method:'POST', credentials:'include' }), fetch('/api/v1/auth/user/refresh', { method:'POST', credentials:'include' })])` is fired in the same tab
- **Then** both responses are `200`
- **And** the cookie jar ends with exactly one `vskill_access` and one `vskill_refresh` (the latter overwrite is fine)
- Confirms server-level race tolerance end-to-end.

### T-006: RED — failing E2E for cold-load from external referrer
**User Story**: US-003 | **Satisfies ACs**: AC-US3-02 | **Status**: [x] completed
**File**: `tests/e2e/authenticated/submit-cold-load.spec.ts` (NEW)
**Test Plan**:
- **Given** an authenticated `storageState` and a fresh browser context
- **When** the browser navigates to `/submit` with a `Referer: https://gmail.com/...` header (or `page.setExtraHTTPHeaders`)
- **Then** the `vskill_refresh` cookie is attached to the subsequent POST `/api/v1/auth/user/refresh`
- **And** the response is `200`
- Confirms `SameSite=Lax` allows cross-site cookie attachment on the GET-driven nav.

### T-007: GREEN — implement Fix A grace window in route.ts
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04 | **Status**: [x] completed
**File**: `src/app/api/v1/auth/user/refresh/route.ts`
**Test Plan**:
- **Given** T-001 and T-002 are RED
- **When** the grace-window branch is added before the existing `if (!rotationResult)` 401 return
- **Then** T-001 and T-002 turn GREEN
- **And** existing tests in `route.test.ts` (happy path, missing cookie, invalid JWT, wrong type) remain GREEN
- The retry loop on lines 96-120 is preserved unchanged.

### T-008: GREEN — implement Fix B shared client refresh module
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-04 | **Status**: [x] completed
**File**: `src/lib/auth-refresh-client.ts` (NEW)
**Test Plan**:
- **Given** T-003 is RED
- **When** the module is created with `refreshUserSession()`, `RefreshResult` type, `__resetRefreshClientForTests()`
- **Then** T-003 turns GREEN.

### T-009: GREEN — wire `auth-fetch.ts` to shared module
**User Story**: US-002 | **Satisfies ACs**: AC-US2-02 | **Status**: [x] completed
**File**: `src/lib/auth-fetch.ts`
**Test Plan**:
- **Given** the shared module from T-008 exists
- **When** the local `refreshPromise` + `attemptRefresh` are removed and the call site at line 285 is replaced with `await refreshUserSession()`
- **Then** existing `auth-fetch.test.ts` 401-retry test passes against the new code path (mocking `refreshUserSession` directly)
- **And** workspace-lockdown logic (lines 56-260) is untouched.

### T-010: GREEN — wire `AuthProvider.tsx` to shared module
**User Story**: US-002 | **Satisfies ACs**: AC-US2-03, AC-US2-05 | **Status**: [x] completed
**File**: `src/app/components/AuthProvider.tsx`
**Test Plan**:
- **Given** the shared module from T-008 exists
- **When** `refreshingRef` + the inline `fetch` in `silentRefresh` (lines 55, 58-79) are removed and replaced with `refreshUserSession()`
- **Then** mount-effect refresh path still updates `user` state on success
- **And** visibility-change path still calls `silentRefresh` and clears `user` on failure
- **And** existing `AuthProvider` tests (if any in `__tests__/`) pass.

### T-011: GREEN — implement Fix C SameSite=Lax
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-03 | **Status**: [x] completed
**File**: `src/lib/auth-cookies.ts`
**Test Plan**:
- **Given** T-004 is RED
- **When** `sameSite: "strict"` is changed to `"lax"` on lines 13, 44, 62
- **Then** T-004 turns GREEN
- **And** an additional inspection of `middleware.ts` confirms Origin allowlist is unchanged (no edit needed).

### T-012: REFACTOR — run unit suite + e2e where available
**User Story**: All | **Satisfies ACs**: All ACs (regression gate) | **Status**: [x] completed
**File**: (no production change)
**Test Plan**:
- `cd repositories/anton-abyzov/vskill-platform && npx vitest run` — all green.
- `npx playwright test tests/e2e/authenticated/auth-refresh-race.spec.ts tests/e2e/authenticated/submit-cold-load.spec.ts` if Playwright env is wired (otherwise document the deferred E2E for the next CI run).
- Manual cross-tab smoke recorded in increment notes.

### T-013: Code review of auth surface
**User Story**: All | **Satisfies ACs**: regression-prevention | **Status**: [x] completed
**File**: (no production change unless review surfaces issues)
**Test Plan**:
- Spawn `sw:code-reviewer` over the auth surface listed in spec.md (routes + libs + middleware + provider)
- Resolve all critical/high/medium findings; iterate up to 3× per closure protocol.
