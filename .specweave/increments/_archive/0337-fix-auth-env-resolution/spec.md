# 0337: Fix Auth Endpoints process.env on Cloudflare Workers

## Problem
Production endpoints return 500 "Worker threw exception" because `auth.ts`, `oauth-state.ts`, and `user/refresh/route.ts` read `JWT_SECRET` from `process.env` which is unreliable on Cloudflare Workers.

## Solution
Apply the same 3-tier CF env resolution pattern from increment 0333:
`resolveEnv()` → `getWorkerEnv() ?? getCloudflareContext({ async: true }).env`

## Acceptance Criteria
- [x] AC-01: `getJwtSecret()` in auth.ts uses resolveEnv() instead of process.env
- [x] AC-02: `isAdminUsername()` in auth.ts uses resolveEnv() instead of process.env
- [x] AC-03: `getSigningKey()` in oauth-state.ts uses resolveEnv()
- [x] AC-04: Duplicate getJwtSecret() in refresh route replaced with shared import
- [x] AC-05: JWT_SECRET and ADMIN_GITHUB_USERNAMES added to CloudflareEnv in env.d.ts
- [x] AC-06: All existing tests pass
- [x] AC-07: Build succeeds (db:generate + build + build:worker)

## Out of Scope
- Other process.env reads (github-oauth, email, external-scan-dispatch) — follow-up increment
- Persistent logging infrastructure
