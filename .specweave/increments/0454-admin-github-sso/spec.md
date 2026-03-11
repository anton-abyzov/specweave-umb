---
increment: 0454-admin-github-sso
title: "Unify Admin Auth with GitHub SSO"
status: active
priority: P1
type: feature
created: 2026-03-08
---

# Unify Admin Auth with GitHub SSO

## Problem Statement

The admin dashboard at `/admin` uses a separate email/password authentication system backed by the `Admin` Prisma table. Meanwhile, regular users already authenticate via GitHub SSO which sets `isAdmin: true` in the JWT for allowlisted usernames (`ADMIN_GITHUB_USERNAMES` env var). This creates a fragmented auth experience: the sole admin (anton-abyzov) must maintain two separate credentials, admin pages depend on `localStorage` for token storage (insecure, no HttpOnly), and the 24-hour admin token expiry differs from the 15-minute user token TTL with proactive refresh.

## Goals

- Eliminate separate admin credentials by reusing the existing GitHub SSO session for admin access
- Replace insecure localStorage token storage with HttpOnly cookie-based auth across all admin pages
- Maintain legacy Authorization header auth as a fallback during the transition period
- Provide clear feedback to non-admin GitHub users who navigate to `/admin`

## User Stories

### US-001: Admin Authentication Middleware
**Project**: vskill-platform
**As a** platform developer
**I want** a unified `requireAdmin()` middleware that accepts both cookie-based GitHub SSO (primary) and legacy Authorization header admin JWT (fallback)
**So that** all admin API routes can be migrated to a single auth check without breaking existing tooling

**Acceptance Criteria**:
- [x] **AC-US1-01**: Given a request with a valid `vskill_access` cookie containing `isAdmin: true`, when `requireAdmin()` is called, then it returns the `UserTokenPayload` with admin access granted
- [x] **AC-US1-02**: Given a request with a valid `vskill_access` cookie where `isAdmin` is false or absent, when `requireAdmin()` is called, then it returns a 403 "Insufficient permissions" error
- [x] **AC-US1-03**: Given a request with no cookie but a valid `Authorization: Bearer` header containing a legacy admin JWT, when `requireAdmin()` is called, then it returns the `AdminTokenPayload` with admin access granted (fallback path)
- [x] **AC-US1-04**: Given a request with neither a valid cookie nor a valid Authorization header, when `requireAdmin()` is called, then it returns a 401 error
- [x] **AC-US1-05**: Given the existing `requireAdminUser()` function already checks cookie + `isAdminUsername()`, when `requireAdmin()` is implemented, then it reuses `requireAdminUser()` for the primary path and falls back to the existing `requireAuth()` for legacy header auth

### US-002: Admin Login Page with GitHub SSO
**Project**: vskill-platform
**As an** admin user
**I want** the admin login page to detect my existing GitHub SSO session and grant admin access automatically
**So that** I do not need to enter separate email/password credentials

**Acceptance Criteria**:
- [x] **AC-US2-01**: Given a user who is already authenticated via GitHub SSO with `isAdmin: true`, when they navigate to `/admin`, then they are automatically redirected to `/admin/dashboard`
- [x] **AC-US2-02**: Given a user who is authenticated via GitHub SSO but is NOT an admin, when they navigate to `/admin`, then they see "You don't have admin access" with their GitHub username displayed and a link back to the main site
- [x] **AC-US2-03**: Given an unauthenticated user, when they navigate to `/admin`, then they see a "Sign in with GitHub" button that initiates the GitHub OAuth flow with a redirect back to `/admin`
- [x] **AC-US2-04**: Given the GitHub OAuth callback sets a `vskill_redirect` cookie, when the admin login initiates GitHub auth, then it sets `vskill_redirect` to `/admin` so the callback redirects back to the admin login page for the auto-redirect check

### US-003: Admin Layout with GitHub Identity
**Project**: vskill-platform
**As an** admin user
**I want** the admin sidebar to show my GitHub avatar and username
**So that** I can confirm which account I am using and log out via the standard cookie-based flow

**Acceptance Criteria**:
- [x] **AC-US3-01**: Given an authenticated admin user, when the admin layout renders, then the sidebar footer shows the user's GitHub avatar image and username instead of the hardcoded "A" avatar and "Admin" text
- [x] **AC-US3-02**: Given an authenticated admin user, when they click Logout, then the `vskill_access` and `vskill_refresh` cookies are cleared via `POST /api/v1/auth/logout` and the user is redirected to `/admin`
- [x] **AC-US3-03**: Given the admin layout mounts in the browser, when `admin_token` or `admin_refresh_token` exist in localStorage, then they are proactively cleared (clean break from legacy storage)
- [x] **AC-US3-04**: Given an unauthenticated user navigating to any `/admin/*` subpage, when the layout detects no valid session, then it redirects to `/admin` (login page)

### US-004: Admin API Route Migration
**Project**: vskill-platform
**As a** platform developer
**I want** all ~51 admin API routes migrated from `requireRole()`/`requireAuth()` to `requireAdmin()`
**So that** admin endpoints accept both cookie-based SSO and legacy header auth uniformly

**Acceptance Criteria**:
- [x] **AC-US4-01**: Given every admin API route under `src/app/api/v1/admin/`, when the route handler calls auth middleware, then it uses `requireAdmin()` instead of `requireRole()` or `requireAuth()`
- [x] **AC-US4-02**: Given routes that previously used `requireRole(request, 'SUPER_ADMIN')`, when migrated to `requireAdmin()`, then the SUPER_ADMIN role check is preserved in the legacy fallback path (the legacy `requireAuth()` already enforces the admin token audience)
- [x] **AC-US4-03**: Given `requireAdmin()` may return either `UserTokenPayload` or `AdminTokenPayload`, when route handlers access the payload, then they use a union type or type guard to handle both shapes safely

### US-005: Remove localStorage Token Dependency from Admin Pages
**Project**: vskill-platform
**As a** platform developer
**I want** all admin pages to use cookie-based `authFetch()` instead of reading `admin_token` from localStorage
**So that** admin API calls use the secure HttpOnly cookie automatically

**Acceptance Criteria**:
- [x] **AC-US5-01**: Given the 8 admin pages (dashboard, submissions, submissions/[id], queue, blocklist, evals, reports, and the login page), when they make API calls, then they use `authFetch()` (credentials: "include") instead of manually attaching `Authorization: Bearer ${localStorage.getItem("admin_token")}`
- [x] **AC-US5-02**: Given an admin page where `authFetch()` receives a 401 response, when the automatic refresh via `POST /api/v1/auth/user/refresh` also fails, then the page redirects to `/admin` (login page)
- [x] **AC-US5-03**: Given admin pages that currently check `localStorage.getItem("admin_token")` on mount to guard access, when migrated, then they rely on the admin layout's session check instead of per-page localStorage guards

### US-006: Proactive Token Refresh in Admin Layout
**Project**: vskill-platform
**As an** admin user
**I want** the admin layout to proactively refresh my JWT before it expires
**So that** I am not logged out mid-session due to the 15-minute user token TTL

**Acceptance Criteria**:
- [x] **AC-US6-01**: Given the `vskill_token_exp` cookie contains a Unix timestamp of the access token expiry, when the admin layout mounts, then it schedules a refresh via `POST /api/v1/auth/user/refresh` 60 seconds before expiry
- [x] **AC-US6-02**: Given a successful proactive refresh, when the new access token is set via cookies, then the layout reschedules the next refresh based on the new `vskill_token_exp` value
- [x] **AC-US6-03**: Given a failed proactive refresh (network error or invalid refresh token), when the refresh attempt returns non-200, then the layout redirects to `/admin` with a session-expired indication

## Out of Scope

- Removing the `Admin` Prisma table, `/api/v1/auth/login`, or `/api/v1/auth/refresh` endpoints (separate cleanup increment)
- Multi-admin support beyond the current `ADMIN_GITHUB_USERNAMES` env var mechanism
- Role-based permissions within the admin dashboard (all admins are SUPER_ADMIN equivalent)
- Migrating admin API tests to the new auth pattern (tests can be updated alongside route migration)

## Technical Notes

### Dependencies
- Existing `requireAdminUser()` in `src/lib/auth.ts` (already checks cookie + isAdminUsername)
- Existing `authFetch()` in `src/lib/auth-fetch.ts` (cookie-based fetch with 401 retry)
- Existing `setAuthCookies()` / `clearAuthCookies()` in `src/lib/auth-cookies.ts`
- Existing `POST /api/v1/auth/user/refresh` for token rotation
- `vskill_token_exp` non-HttpOnly cookie for client-side expiry scheduling

### Constraints
- Legacy `Authorization: Bearer` header auth must continue working as fallback
- The `Admin` table and its endpoints remain untouched (future cleanup)
- User JWT access token TTL is 15 minutes (vs 24h for legacy admin tokens)

### Architecture Decisions
- `requireAdmin()` composes existing `requireAdminUser()` (cookie path) and `requireAuth()` (header path) rather than duplicating verification logic
- Admin pages switch from manual `fetch()` with `Authorization` header to `authFetch()` which sends cookies via `credentials: "include"` and handles 401 refresh automatically
- The admin layout becomes the single auth gate for all admin subpages, replacing per-page localStorage checks

## Success Metrics

- Zero separate admin logins required: admin accesses dashboard via existing GitHub SSO session
- All 51 admin API routes accept cookie-based auth
- No `localStorage.getItem("admin_token")` references remain in admin page code
- Legacy header auth continues to work for any external tooling or scripts
