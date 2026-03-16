---
increment: 0454-admin-github-sso
title: "Unify Admin Auth with GitHub SSO"
by_user_story:
  US-001: [T-001, T-002]
  US-002: [T-003]
  US-003: [T-004, T-005, T-006]
  US-004: [T-007, T-008]
  US-005: [T-009, T-010]
  US-006: [T-011, T-012]
---

# Tasks: Unify Admin Auth with GitHub SSO

## Task Notation

- `[ ]`: Not started
- `[x]`: Completed
- `[P]`: Parallelizable with other [P] tasks

---

## User Story: US-001 — Admin Authentication Middleware

**Linked ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05
**Tasks**: 2 total, 0 completed

### T-001: Add `requireAdmin()` function and `AdminIdentity` type to `src/lib/auth.ts`

**User Story**: US-001
**Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05
**Status**: [x] completed

**Test Plan**:
- **Given** a request with a valid `vskill_access` cookie containing `isAdmin: true`
- **When** `requireAdmin()` is called
- **Then** it returns `UserTokenPayload` with admin access granted

- **Given** a request with a valid `vskill_access` cookie where `isAdmin` is false
- **When** `requireAdmin()` is called
- **Then** it returns a `Response` with status 403

- **Given** a request with no cookie but a valid `Authorization: Bearer` header with a legacy admin JWT
- **When** `requireAdmin()` is called
- **Then** it returns `AdminTokenPayload` (fallback header path)

- **Given** a request with neither a valid cookie nor a valid Authorization header
- **When** `requireAdmin()` is called
- **Then** it returns a `Response` with status 401

**Test Cases**:
1. **Unit**: `src/lib/__tests__/auth.requireAdmin.test.ts`
   - `requireAdmin_cookieAdminTrue_returnsUserPayload()`: Cookie path with isAdmin=true grants access
   - `requireAdmin_cookieAdminFalse_returns403()`: Cookie path with isAdmin=false returns 403
   - `requireAdmin_noCookieValidHeader_returnsAdminPayload()`: Fallback to header auth
   - `requireAdmin_noCookieNoHeader_returns401()`: Both paths fail returns 401
   - `requireAdmin_composesRequireAdminUser_notDuplicatesLogic()`: Delegates to requireAdminUser() for cookie path
   - **Coverage Target**: 95%

**Implementation**:
1. Open `src/lib/auth.ts`
2. Add `AdminIdentity` type alias: `type AdminIdentity = UserTokenPayload | AdminTokenPayload`
3. Add `requireAdmin(request: Request)` function:
   - Call `requireAdminUser(request)` — if not a `Response`, return the `UserTokenPayload`
   - Else call `requireAuth(request)` — if not a `Response`, return the `AdminTokenPayload`
   - Else return the 401 `Response` from `requireAuth`
4. Export both `requireAdmin` and `AdminIdentity`
5. Run unit tests: `npx vitest run src/lib/__tests__/auth.requireAdmin.test.ts`

---

### T-002: Write unit tests for `requireAdmin()` [P]

**User Story**: US-001
**Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05
**Status**: [x] completed

**Test Plan**:
- **Given** mocked `requireAdminUser` returning a `UserTokenPayload`
- **When** `requireAdmin()` is called
- **Then** the returned value equals the `UserTokenPayload`

- **Given** mocked `requireAdminUser` returning a 403 Response and mocked `requireAuth` returning an `AdminTokenPayload`
- **When** `requireAdmin()` is called
- **Then** the returned value equals the `AdminTokenPayload`

**Test Cases**:
1. **Unit**: `src/lib/__tests__/auth.requireAdmin.test.ts`
   - All 5 scenarios from T-001 test plan
   - Use `vi.mock()` with `vi.hoisted()` for ESM-safe mocking of `requireAdminUser` and `requireAuth`
   - **Coverage Target**: 95%

**Implementation**:
1. Create `src/lib/__tests__/auth.requireAdmin.test.ts`
2. Use `vi.hoisted()` to declare mocks before `vi.mock()` calls (ESM requirement)
3. Mock `requireAdminUser` and `requireAuth` via `vi.mock('@/lib/auth', ...)`
4. Test all 4 paths with realistic JWT payload fixtures
5. Run: `npx vitest run src/lib/__tests__/auth.requireAdmin.test.ts`

---

## User Story: US-002 — Admin Login Page with GitHub SSO

**Linked ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04
**Tasks**: 1 total, 0 completed

### T-003: Rewrite `src/app/admin/page.tsx` as GitHub SSO gateway

**User Story**: US-002
**Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04
**Status**: [x] completed

**Test Plan**:
- **Given** a user authenticated via GitHub SSO with `isAdmin: true`
- **When** they navigate to `/admin`
- **Then** they are automatically redirected to `/admin/dashboard`

- **Given** a user authenticated via GitHub SSO but NOT an admin
- **When** they navigate to `/admin`
- **Then** they see "You don't have admin access" with their GitHub username and a link to the main site

- **Given** an unauthenticated user
- **When** they navigate to `/admin`
- **Then** they see a "Sign in with GitHub" button linking to `/api/v1/auth/github?redirect=/admin`

- **Given** the admin login initiates GitHub auth
- **When** the GitHub button is clicked
- **Then** the redirect URL includes `?redirect=/admin` so the OAuth callback returns to `/admin`

**Test Cases**:
1. **Integration**: `src/app/admin/__tests__/page.test.tsx`
   - `adminPage_adminUser_redirectsToDashboard()`: Mocks authFetch GET /api/v1/auth/me returning isAdmin=true, expects router.push('/admin/dashboard')
   - `adminPage_nonAdminUser_showsDeniedState()`: Mocks /me returning isAdmin=false, expects denied message with username
   - `adminPage_unauthenticated_showsGitHubButton()`: Mocks /me returning 401, expects GitHub signin button with correct href
   - `adminPage_githubButton_hasCorrectRedirectParam()`: href contains `?redirect=/admin`
   - **Coverage Target**: 90%

**Implementation**:
1. Rewrite `src/app/admin/page.tsx` as `"use client"` component
2. On mount: `authFetch('/api/v1/auth/me')` to detect session state
3. State machine: `loading` → `admin` (redirect to /admin/dashboard) | `denied` (show username + message) | `unauthenticated` (show GitHub button)
4. GitHub button href: `/api/v1/auth/github?redirect=/admin`
5. Show spinner while loading, display error states clearly
6. Remove all email/password form code
7. Run: `npx vitest run src/app/admin/__tests__/page.test.tsx`

---

## User Story: US-003 — Admin Layout with GitHub Identity

**Linked ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04
**Tasks**: 3 total, 0 completed

### T-004: Add session check and GitHub identity to admin layout

**User Story**: US-003
**Satisfies ACs**: AC-US3-01, AC-US3-04
**Status**: [x] completed

**Test Plan**:
- **Given** an authenticated admin user
- **When** the admin layout renders
- **Then** the sidebar shows the user's GitHub avatar URL and username

- **Given** an unauthenticated user navigating to any `/admin/*` subpage
- **When** the layout detects no valid session via `/api/v1/auth/me`
- **Then** it redirects to `/admin`

**Test Cases**:
1. **Integration**: `src/app/admin/__tests__/layout.test.tsx`
   - `adminLayout_authenticatedUser_showsGitHubAvatar()`: Mocks /me returning avatarUrl + username, expects img src and username text
   - `adminLayout_unauthenticatedUser_redirectsToAdmin()`: Mocks /me returning 401, expects router.push('/admin')
   - **Coverage Target**: 90%

**Implementation**:
1. Open `src/app/admin/layout.tsx`
2. Add `useEffect` to call `authFetch('/api/v1/auth/me')` on mount
3. Store `{ avatarUrl, username }` in state from the response
4. Replace hardcoded "A" avatar `<span>` with `<img src={identity.avatarUrl} alt={identity.username} />`
5. Replace hardcoded "Admin" text with `{identity.username}`
6. If `/me` returns 401 after refresh attempt, call `router.push('/admin')`
7. Show loading state while session check is in progress (gate child render)
8. Run: `npx vitest run src/app/admin/__tests__/layout.test.tsx`

---

### T-005: Replace localStorage logout with cookie-based logout and clear legacy tokens

**User Story**: US-003
**Satisfies ACs**: AC-US3-02, AC-US3-03
**Status**: [x] completed

**Test Plan**:
- **Given** an authenticated admin user clicks Logout
- **When** the logout handler fires
- **Then** `POST /api/v1/auth/logout` is called and the user is redirected to `/admin`

- **Given** the admin layout mounts in the browser
- **When** `admin_token` or `admin_refresh_token` exist in localStorage
- **Then** they are proactively removed via `localStorage.removeItem()`

**Test Cases**:
1. **Integration**: `src/app/admin/__tests__/layout.test.tsx`
   - `adminLayout_logout_callsLogoutEndpointAndRedirects()`: Mocks fetch POST /logout, expects router.push('/admin')
   - `adminLayout_mount_clearsLegacyLocalStorage()`: Spies on localStorage.removeItem, expects it called for both keys
   - **Coverage Target**: 90%

**Implementation**:
1. In `src/app/admin/layout.tsx` logout handler:
   - Replace `localStorage.removeItem("admin_token")` with `await authFetch('/api/v1/auth/logout', { method: 'POST' })`
   - After logout completes, call `router.push('/admin')`
2. Add `useEffect` (runs once on mount) to clear legacy tokens:
   ```typescript
   useEffect(() => {
     localStorage.removeItem('admin_token');
     localStorage.removeItem('admin_refresh_token');
   }, []);
   ```
3. Run: `npx vitest run src/app/admin/__tests__/layout.test.tsx`

---

### T-006: Create `useTokenRefresh` hook for proactive JWT refresh [P]

**User Story**: US-003 + US-006
**Satisfies ACs**: AC-US3-04, AC-US6-01, AC-US6-02, AC-US6-03
**Status**: [x] completed

**Test Plan**:
- **Given** the `vskill_token_exp` cookie contains a Unix timestamp 120 seconds in the future
- **When** `useTokenRefresh` mounts
- **Then** it schedules a `setTimeout` to fire 60 seconds before expiry (after 60 seconds)

- **Given** a successful `POST /api/v1/auth/user/refresh`
- **When** the timer fires and refresh succeeds
- **Then** the hook reads the new `vskill_token_exp` cookie and reschedules

- **Given** a failed refresh (non-200 response)
- **When** the timer fires and refresh fails
- **Then** `window.location.href` is set to `/admin`

**Test Cases**:
1. **Unit**: `src/hooks/__tests__/useTokenRefresh.test.ts`
   - `useTokenRefresh_setsTimeoutBeforeExpiry()`: Mock cookie 120s out, expect setTimeout called with ~60000ms
   - `useTokenRefresh_refreshSuccess_reschedulesNext()`: Mock successful POST, expect scheduleRefresh called again
   - `useTokenRefresh_refreshFailure_redirectsToAdmin()`: Mock 401 POST, expect window.location.href='/admin'
   - `useTokenRefresh_noCookie_doesNotSchedule()`: No cookie present, setTimeout not called
   - `useTokenRefresh_cleanup_clearsTimer()`: Unmount clears timeout via clearTimeout
   - **Coverage Target**: 90%

**Implementation**:
1. Create `src/hooks/useTokenRefresh.ts`
2. Implement hook as described in plan.md architecture section
3. Read `vskill_token_exp` from `document.cookie`
4. Schedule setTimeout for `(expSec - nowSec - 60) * 1000` ms
5. On success: reschedule; on failure: redirect to `/admin`
6. Return cleanup function clearing the timer
7. Import and use in `src/app/admin/layout.tsx`
8. Run: `npx vitest run src/hooks/__tests__/useTokenRefresh.test.ts`

---

## User Story: US-004 — Admin API Route Migration

**Linked ACs**: AC-US4-01, AC-US4-02, AC-US4-03
**Tasks**: 2 total, 0 completed

### T-007: Migrate all admin API routes from `requireRole`/`requireAuth` to `requireAdmin`

**User Story**: US-004
**Satisfies ACs**: AC-US4-01, AC-US4-02, AC-US4-03
**Status**: [x] completed

**Test Plan**:
- **Given** every admin API route under `src/app/api/v1/admin/`
- **When** the route handler calls auth middleware
- **Then** it uses `requireAdmin()` not `requireRole()` or `requireAuth()`

- **Given** routes that previously used `requireRole(request, 'SUPER_ADMIN')`
- **When** migrated to `requireAdmin()`
- **Then** zero occurrences of `requireRole` remain in admin route files

**Test Cases**:
1. **Verification**: grep-based scan (no test file needed — checked in T-008)
   - `grep -r "requireRole\|requireAuth" src/app/api/v1/admin/ --include="route.ts"` returns 0 results
   - `grep -r "requireAdmin" src/app/api/v1/admin/ --include="route.ts"` returns count matching file count
   - **Coverage Target**: 100% of route files migrated

**Implementation**:
1. Run discovery: `grep -rl "requireRole\|requireAuth" /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/vskill-platform/src/app/api/v1/admin/ --include="route.ts"`
2. For each file found, replace:
   - `import { requireRole, isAuthError }` → `import { requireAdmin, isAuthError }`
   - `import { requireAuth, isAuthError }` → `import { requireAdmin, isAuthError }`
   - `requireRole(request, "SUPER_ADMIN")` → `requireAdmin(request)`
   - `requireRole(request, "REVIEWER")` → `requireAdmin(request)`
   - `requireAuth(request)` → `requireAdmin(request)` (only in admin routes)
3. For any route accessing typed payload fields (e.g., `auth.email`), add type narrowing: `if ('email' in auth)`
4. Run TypeScript check: `npx tsc --noEmit`

---

### T-008: Verify admin route migration completeness [P]

**User Story**: US-004
**Satisfies ACs**: AC-US4-01, AC-US4-02, AC-US4-03
**Status**: [x] completed

**Test Plan**:
- **Given** T-007 has completed the migration
- **When** grep scans admin route files
- **Then** zero remaining `requireRole` or `requireAuth` calls exist in admin routes

- **Given** `requireAdmin()` returns `UserTokenPayload | AdminTokenPayload`
- **When** route handlers access the payload
- **Then** TypeScript compilation succeeds with no type errors

**Test Cases**:
1. **Verification script**: `src/app/api/v1/admin/__tests__/migration.verify.ts`
   - Confirm `grep` returns 0 for old patterns
   - Confirm `tsc --noEmit` exits 0
   - **Coverage Target**: 100% of routes

**Implementation**:
1. Run: `grep -r "requireRole\|requireAuth" /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/vskill-platform/src/app/api/v1/admin/ --include="route.ts"` — must return empty
2. Run: `npx tsc --noEmit` from vskill-platform root — must exit 0
3. Run: `npx vitest run` — existing admin route tests must still pass

---

## User Story: US-005 — Remove localStorage Token Dependency from Admin Pages

**Linked ACs**: AC-US5-01, AC-US5-02, AC-US5-03
**Tasks**: 2 total, 0 completed

### T-009: Migrate 7 admin pages from localStorage/fetch to `authFetch`

**User Story**: US-005
**Satisfies ACs**: AC-US5-01, AC-US5-02, AC-US5-03
**Status**: [x] completed

**Test Plan**:
- **Given** the 7 admin content pages (dashboard, submissions, submissions/[id], queue, blocklist, evals, reports)
- **When** they make API calls
- **Then** they use `authFetch()` instead of manual `Authorization: Bearer ${localStorage.getItem("admin_token")}`

- **Given** an admin page where `authFetch()` receives a 401 response
- **When** the automatic refresh also fails
- **Then** the page redirects to `/admin`

**Test Cases**:
1. **Integration**: Per-page test files (one per page)
   - `dashboard.test.tsx`: `authFetch` called for stats and queue endpoints, not localStorage
   - `submissions.test.tsx`: `authFetch` called, no manual Authorization header
   - `queue.test.tsx`: All 8 call sites use `authFetch`, no localStorage reads
   - `blocklist.test.tsx`: 3 call sites use `authFetch`
   - Each: verify `localStorage.getItem("admin_token")` is never called
   - **Coverage Target**: 85%

**Implementation**:
1. For each of the 7 pages:
   a. Add import: `import { authFetch } from "@/lib/auth-fetch";`
   b. Replace all: `const token = localStorage.getItem("admin_token"); fetch(url, { headers: { Authorization: \`Bearer ${token}\` } })` with `authFetch(url)`
   c. Remove per-page `if (!token) router.push('/admin')` guards (layout handles this)
   d. Remove per-page localStorage-based auth checks on mount
2. Pages in order: dashboard, submissions, submissions/[id], queue (8 sites), blocklist, evals, reports
3. Run: `npx vitest run src/app/admin/`

---

### T-010: Verify no remaining `localStorage.getItem("admin_token")` in admin pages [P]

**User Story**: US-005
**Satisfies ACs**: AC-US5-01, AC-US5-03
**Status**: [x] completed

**Test Plan**:
- **Given** T-009 has completed the migration
- **When** grep scans admin page files
- **Then** zero occurrences of `localStorage.getItem("admin_token")` remain

**Test Cases**:
1. **Verification**:
   - `grep -r "localStorage.getItem.*admin_token" src/app/admin/ --include="*.tsx"` returns 0 results
   - `grep -r "Authorization.*localStorage" src/app/admin/ --include="*.tsx"` returns 0 results
   - **Coverage Target**: 100%

**Implementation**:
1. Run: `grep -r "localStorage.getItem.*admin_token" /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/vskill-platform/src/app/admin/ --include="*.tsx"` — must return empty
2. Run: `grep -r "Authorization.*localStorage" /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/vskill-platform/src/app/admin/ --include="*.tsx"` — must return empty
3. Run: `npx vitest run src/app/admin/` — all page tests must pass

---

## User Story: US-006 — Proactive Token Refresh in Admin Layout

**Linked ACs**: AC-US6-01, AC-US6-02, AC-US6-03
**Tasks**: 2 total, 0 completed

### T-011: Integrate `useTokenRefresh` hook into admin layout

**User Story**: US-006
**Satisfies ACs**: AC-US6-01, AC-US6-02, AC-US6-03
**Status**: [x] completed
**Depends on**: T-006

**Test Plan**:
- **Given** the `vskill_token_exp` cookie is set when the admin layout mounts
- **When** the layout renders
- **Then** `useTokenRefresh()` is called and a timer is scheduled 60s before expiry

- **Given** a failed proactive refresh
- **When** the refresh endpoint returns non-200
- **Then** the layout redirects to `/admin` with session expired indication

**Test Cases**:
1. **Integration**: `src/app/admin/__tests__/layout.test.tsx`
   - `adminLayout_callsUseTokenRefresh_onMount()`: Mock the hook, verify it is invoked
   - `adminLayout_tokenRefreshFailure_redirectsToAdmin()`: Mock hook failure path, expect redirect
   - **Coverage Target**: 90%

**Implementation**:
1. Import `useTokenRefresh` from `@/hooks/useTokenRefresh` in `src/app/admin/layout.tsx`
2. Call `useTokenRefresh()` inside the layout component
3. Ensure the hook is only active after session is confirmed (not during loading state)
4. Run: `npx vitest run src/app/admin/__tests__/layout.test.tsx`

---

### T-012: End-to-end verification and TypeScript type check [P]

**User Story**: US-006
**Satisfies ACs**: AC-US6-01, AC-US6-02, AC-US6-03
**Status**: [x] completed
**Depends on**: T-001, T-002, T-003, T-004, T-005, T-006, T-007, T-008, T-009, T-010, T-011

**Test Plan**:
- **Given** all tasks T-001 through T-011 are complete
- **When** the full test suite runs
- **Then** all tests pass with zero TypeScript errors

- **Given** the migration is complete
- **When** grep scans confirm zero legacy patterns remain
- **Then** the success metrics from spec.md are all satisfied

**Test Cases**:
1. **Full suite verification**:
   - `npx tsc --noEmit` exits 0
   - `npx vitest run` exits 0 (all tests pass)
   - `grep -r "requireRole\|requireAuth" src/app/api/v1/admin/` returns 0
   - `grep -r "localStorage.getItem.*admin_token" src/app/admin/` returns 0
   - **Coverage Target**: 95% overall

**Implementation**:
1. Run `npx tsc --noEmit` from vskill-platform root — must exit 0
2. Run `npx vitest run` — all tests must pass
3. Run grep verification commands (see T-008, T-010)
4. Manual verification gate: confirm admin dashboard accessible via GitHub SSO session
