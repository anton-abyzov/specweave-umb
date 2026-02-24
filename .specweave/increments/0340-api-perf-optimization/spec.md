---
increment: 0340-api-perf-optimization
title: "API performance optimization"
type: feature
priority: P1
status: completed
created: 2026-02-23
structure: user-stories
test_mode: TDD
coverage_target: 80
---

# Feature: API Performance Optimization

## Overview

Reduce Worker-to-DB latency and cold-start overhead across the vskill-platform API by applying Cloudflare Smart Placement, caching repeated env resolution, deferring non-critical DB writes with `waitUntil`, parallelizing login operations, prewarming the DB connection in the hourly cron, and dynamic-importing `bcryptjs` only in the login route.

## Background

The vskill-platform runs on Cloudflare Workers with a Neon Postgres backend. Every API request currently calls `resolveEnv()` multiple times (once for `getDb()`, again for `getJwtSecret()`, again for `checkRateLimit`), each performing an async `getCloudflareContext({ async: true })` call. Login and OAuth callback routes execute all DB writes sequentially, including non-critical operations like `lastLoginAt` updates and refresh token storage that don't affect the response. The `bcryptjs` library (~300KB) is bundled into the Worker entry and loaded on every request, even though only the login route uses it.

## User Stories

### US-001: Smart Placement (P1)
**Project**: vskill-platform

**As a** platform operator
**I want** Cloudflare Smart Placement enabled globally
**So that** Workers run in datacenters closest to the Neon database, reducing network latency on every DB call

**Acceptance Criteria**:
- [x] **AC-US1-01**: `wrangler.jsonc` includes `"placement": { "mode": "smart" }` at the top level
- [x] **AC-US1-02**: Deployment succeeds with Smart Placement enabled (no wrangler errors)

---

### US-002: JWT Secret Isolate-Lifetime Cache (P1)
**Project**: vskill-platform

**As a** platform operator
**I want** the JWT_SECRET resolved once per isolate lifetime and cached in a module-level variable
**So that** subsequent `getJwtSecret()` calls within the same isolate avoid repeated `resolveEnv()` overhead

**Acceptance Criteria**:
- [x] **AC-US2-01**: `getJwtSecret()` in `src/lib/auth.ts` caches the resolved `Uint8Array` in a module-level variable after first resolution
- [x] **AC-US2-02**: Second and subsequent calls to `getJwtSecret()` return the cached value without calling `resolveEnv()`
- [x] **AC-US2-03**: Unit test verifies cache hit: `resolveEnv` called once across two `getJwtSecret()` invocations
- [x] **AC-US2-04**: No TTL or invalidation logic (isolate recycling on deploy handles rotation)

---

### US-003: waitUntil for Deferred DB Writes (P1)
**Project**: vskill-platform

**As a** user logging in
**I want** the `lastLoginAt` update and refresh token storage to happen after the response is sent
**So that** login and OAuth callback responses return faster without waiting for non-critical writes

**Acceptance Criteria**:
- [x] **AC-US3-01**: Login route (`src/app/api/v1/auth/login/route.ts`) obtains `ctx` via `getCloudflareContext({ async: true })` and defers `lastLoginAt` update with `ctx.waitUntil()`
- [x] **AC-US3-02**: Login route defers refresh token `create` with `ctx.waitUntil()`
- [x] **AC-US3-03**: OAuth callback route (`src/app/api/v1/auth/github/callback/route.ts`) obtains `ctx` via `getCloudflareContext({ async: true })` and defers refresh token storage with `ctx.waitUntil()`
- [x] **AC-US3-04**: Response is returned before deferred operations complete
- [x] **AC-US3-05**: Unit test verifies `waitUntil` is called with deferred operations (mock `getCloudflareContext`)

---

### US-004: Login Route Parallelization (P1)
**Project**: vskill-platform

**As a** user logging in
**I want** the DB connection to be initiated concurrently with the rate limit check
**So that** DB cold-start latency overlaps with the rate-limit KV lookup instead of happening sequentially

**Acceptance Criteria**:
- [x] **AC-US4-01**: `getDb()` call starts concurrently with (not after) the rate-limit `checkRateLimit()` call in the login route
- [x] **AC-US4-02**: The `prisma` instance from the concurrent `getDb()` is used for subsequent `admin.findUnique` query
- [x] **AC-US4-03**: Rate-limit rejection still returns 429 before any DB query is attempted (await rate limit result before using prisma)

---

### US-005: DB Connection Prewarm in Cron (P2)
**Project**: vskill-platform

**As a** platform operator
**I want** the hourly cron handler to prewarm the Neon DB connection
**So that** the first API request after a cold period doesn't pay the full Neon cold-start penalty

**Acceptance Criteria**:
- [x] **AC-US5-01**: The `scheduled` handler in `scripts/build-worker-entry.ts` calls `getDb()` followed by a lightweight query (e.g., `SELECT 1`) before existing cron tasks
- [x] **AC-US5-02**: Prewarm failure is caught and logged (non-blocking, does not prevent other cron tasks)
- [x] **AC-US5-03**: Prewarm runs as the first operation inside the existing `ctx.waitUntil` block

---

### US-006: Dynamic Import of bcryptjs (P2)
**Project**: vskill-platform

**As a** platform operator
**I want** `bcryptjs` to be dynamically imported only when `hashPassword` or `verifyPassword` is called
**So that** the ~300KB library is not loaded on every request (only login route needs it)

**Acceptance Criteria**:
- [x] **AC-US6-01**: Top-level `import bcrypt from 'bcryptjs'` removed from `src/lib/auth.ts`
- [x] **AC-US6-02**: `hashPassword` and `verifyPassword` use `const bcrypt = await import('bcryptjs')` (or cache the import result in a module variable)
- [x] **AC-US6-03**: Other functions in `auth.ts` (JWT signing/verification) are unaffected and do not trigger bcrypt loading
- [x] **AC-US6-04**: Unit test verifies dynamic import is called only when `hashPassword` or `verifyPassword` is invoked

## Functional Requirements

### FR-001: Smart Placement Configuration
Add `"placement": { "mode": "smart" }` to `wrangler.jsonc`. No code changes needed -- this is a configuration-only optimization.

### FR-002: JWT Secret Caching
Introduce a module-level `let _cachedJwtSecret: Uint8Array | null = null` in `src/lib/auth.ts`. On first call, resolve via `resolveEnv()` with the existing fallback chain, encode, and cache. Subsequent calls return the cached value. No TTL -- isolate recycling on deploy handles secret rotation.

### FR-003: Deferred Writes with waitUntil
In login and OAuth callback routes, obtain `ctx` from `getCloudflareContext({ async: true })` (already used in submissions route as reference pattern). Wrap `lastLoginAt` update and refresh token storage in `ctx.waitUntil()`. Return the response immediately after token generation.

### FR-004: Concurrent DB + Rate Limit
In the login route, restructure to call `getDb()` in parallel with the rate-limit check using `Promise.all` or concurrent awaits. The DB promise result is used only after rate-limit passes.

### FR-005: Cron DB Prewarm
Add a prewarm step at the start of the `scheduled` handler's `waitUntil` block in the worker entry wrapper. Import `getDb` and run `(await getDb()).$queryRaw\`SELECT 1\`` wrapped in try/catch.

### FR-006: Dynamic bcryptjs Import
Replace the static `import bcrypt from 'bcryptjs'` with a lazy module-level cache pattern: `let _bcrypt: typeof import('bcryptjs') | null = null` and a helper `async function getBcrypt()` that does `_bcrypt ??= await import('bcryptjs'); return _bcrypt`.

## Success Criteria

- Reduced p50/p95 latency visible in Cloudflare analytics after deployment (compared to pre-deployment baseline)
- Login route returns response before `lastLoginAt` and refresh token writes complete
- No regressions in existing test suite
- All new unit tests pass in TDD mode (red-green-refactor)

## Out of Scope

- Lazy-loading `jose` or `@prisma/adapter-neon` (not worth the complexity)
- Formal latency benchmarks or specific percentage targets
- Worker splitting or route-level placement configuration
- Cache invalidation for JWT_SECRET (handled by isolate lifecycle)
- Any schema changes or new API endpoints

## Dependencies

- Cloudflare Smart Placement support (generally available)
- Existing hourly cron trigger in `wrangler.jsonc`
- `getCloudflareContext({ async: true })` pattern (already used in submissions route)
