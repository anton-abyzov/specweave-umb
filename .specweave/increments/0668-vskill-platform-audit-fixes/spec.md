---
increment: 0668-vskill-platform-audit-fixes
title: 'vskill-platform Audit Fixes: Performance, Simplicity & Correctness'
type: refactor
priority: P1
status: completed
created: 2026-04-16T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: vskill-platform Audit Fixes: Performance, Simplicity & Correctness

## Overview

Comprehensive refactor of the vskill-platform codebase (verified-skill.com) based on a full audit that identified 46 issues. This increment addresses the 20 highest-priority findings across security/data-integrity (P0), performance (P1), code quality (P1), and testing gaps (P2). The changes harden webhook authentication, close race conditions in the publish flow, eliminate N+1 query patterns, split an oversized monolith module, and raise test coverage on critical API paths.

## User Stories

### US-001: Security & Data Integrity (P0)
**Project**: vskill-platform

**As a** platform operator
**I want** all critical security and data-integrity gaps closed
**So that** webhook auth cannot be bypassed, double-approvals cannot occur, published skills are always visible, rate limits fire before expensive work, and token rotation never silently fails

**Acceptance Criteria**:
- [x] **AC-US1-01**: Webhook env silent fallback removed — `resolveEnv()` failure in `src/app/api/v1/webhooks/scan-results/route.ts` throws or returns an error response instead of silently falling back to `process.env`, preventing webhook auth bypass
- [x] **AC-US1-02**: Publish race condition fixed — `src/app/api/v1/submissions/route.ts` approval path uses a Prisma transaction with an optimistic version check (or equivalent atomic guard) so that concurrent double-approval is impossible
- [x] **AC-US1-03**: Invisible published skills eliminated — `src/app/api/v1/admin/submissions/[id]/approve/route.ts` makes `publishSkill()` failure a hard error (approval rolls back) and KV records use no expiring TTL (or TTL is refreshed by a cron) so skills remain visible indefinitely
- [x] **AC-US1-04**: Rate limit fires before KV — in `src/app/api/v1/submissions/route.ts`, rate-limit check executes before any KV cache access so that unauthenticated spam cannot trigger cache reads
- [x] **AC-US1-05**: Broken token rotation fixed — in `src/app/api/v1/auth/login/route.ts`, refresh-token DB insertion failure causes the entire login response to fail (not silently swallowed by `Promise.allSettled()`), ensuring rotation is never silently broken

---

### US-002: Code Architecture — submission-store Split (P0)
**Project**: vskill-platform

**As a** developer maintaining the platform
**I want** the 1,781-line `submission-store.ts` monolith split into focused modules
**So that** each concern (KV caching, Prisma persistence, state machine, TTL management, batching) is independently testable and maintainable

**Acceptance Criteria**:
- [x] **AC-US2-01**: `submission-store.ts` is replaced by separate modules — at minimum: a KV-layer module, a Prisma-layer module, and a state-machine module — with no single file exceeding 500 lines
- [x] **AC-US2-02**: All existing callers of `submission-store.ts` exports continue to work without API changes (re-exports from an index barrel are acceptable)
- [x] **AC-US2-03**: Existing tests for submission-store pass after the split with no behavioral changes

---

### US-003: Performance Optimization (P1)
**Project**: vskill-platform

**As a** platform operator
**I want** cron jobs, database queries, and page loads optimized
**So that** enrichment completes in seconds instead of minutes, stats refresh is incremental, duplicate queries are eliminated, skill pages leverage ISR caching, and slow async children don't block the entire layout

**Acceptance Criteria**:
- [x] **AC-US3-01**: Enrichment N+1 eliminated — `src/lib/cron/enrichment.ts` processes skills concurrently via a worker pool (e.g., `pLimit`) instead of sequential `await fetch()` in a for loop
- [x] **AC-US3-02**: SkillPath HEAD spam cached — `src/lib/cron/enrichment.ts` caches `skillPathValidAt` timestamp in the DB so HEAD requests to `raw.githubusercontent.com` are skipped when validation is still fresh (e.g., within 24h)
- [x] **AC-US3-03**: Stats full-scan replaced with incremental computation — `src/lib/cron/stats-refresh.ts` stores previous stats in KV and only recomputes buckets that changed since last run
- [x] **AC-US3-04**: Publisher double query consolidated — `src/lib/data.ts` replaces the `groupBy` + separate raw SQL star-dedup pattern with a single `$queryRaw` call
- [x] **AC-US3-05**: Skill page ISR enabled — `src/app/skills/[owner]/[repo]/[skill]/page.tsx` adds `revalidate: 3600` (or equivalent ISR config) so DB queries are not repeated on every page view
- [x] **AC-US3-06**: Suspense boundaries added — `src/app/layout.tsx` wraps slow async children in `<Suspense>` boundaries so the page shell renders immediately

---

### US-004: Code Quality & Testing (P1/P2)
**Project**: vskill-platform

**As a** developer maintaining the platform
**I want** duplicated code extracted, type safety enforced, dead code removed, HTTP caching improved, large responses streamed, CSRF mitigated, and critical-path test coverage raised to 80%+
**So that** the codebase is maintainable, safe, and performant

**Acceptance Criteria**:
- [x] **AC-US4-01**: Queue page deduplicated — shared logic between `src/app/admin/queue/page.tsx` (1,496 lines) and `src/app/queue/QueuePageClient.tsx` (1,309 lines) is extracted into a shared module, reducing total combined size by at least 40%
- [x] **AC-US4-02**: `any` types eliminated — all `any` occurrences (including `mapDbSkillToSkillData(s: any)`, `listAllKeys(kv: any)`) are replaced with proper type annotations or type guards
- [x] **AC-US4-03**: Dead code removed — `_resetPublishedCache()` no-op, orphaned migration scripts, and stale comment blocks in production code are deleted
- [x] **AC-US4-04**: ETag support added — `src/app/api/v1/skills/route.ts` returns `ETag` and `Last-Modified` headers and responds with `304 Not Modified` for conditional GET requests
- [x] **AC-US4-06**: CSRF protection enforced — all state-changing POST endpoints using cookie auth (`vskill_access`) enforce `SameSite=Strict` (or `Lax` with CSRF token) to prevent cross-site request forgery
- [x] **AC-US4-07**: Auth/webhook/publish test coverage at 80%+ — critical API paths (auth, webhooks, submissions/publish) have test coverage of at least 80%, up from current 47%
- [x] **AC-US4-08**: OAuth callback error paths tested — OAuth callback error fallback HTML (error rendering with `step` variable) has tests covering injection risk and all error branches

## Functional Requirements

### FR-001: Atomic Publish Flow
The approval endpoint must wrap status update + KV publish + DB commit in a single Prisma interactive transaction. If any step fails, the entire operation rolls back. No partial state (approved in DB but missing from KV) is possible.

### FR-002: Rate Limit Ordering
Rate limiting must be the first middleware check on submission endpoints, executing before any KV reads, DB queries, or business logic. This applies to all public-facing endpoints that accept unauthenticated or lightly-authenticated requests.

### FR-003: Module Split Contract
The submission-store split must preserve the existing public API surface. A barrel `index.ts` re-exports all current symbols. Internal module boundaries follow the single-responsibility principle: KV operations, Prisma operations, and state transitions live in separate files.

### FR-004: Incremental Stats
Stats refresh must track a high-water mark (timestamp or version) in KV. On each cron tick, only records modified after the high-water mark are re-aggregated. Full recomputation is a fallback triggered only when the high-water mark is missing or stale beyond a configurable threshold.

### FR-005: Streaming Response Format
The streaming skills endpoint must produce newline-delimited JSON (NDJSON) so clients can parse incrementally. The `Content-Type` header must be `application/x-ndjson`. Existing clients using `NextResponse.json()` format must continue to work via content negotiation or a query parameter opt-in.

## Success Criteria

- Zero P0 security/data-integrity issues remaining (items 1-6 verified closed)
- Enrichment cron wall time reduced by 80%+ (from 100-250s to under 30s)
- No file in `src/lib/` exceeds 500 lines
- `any` count across `src/` drops to 0
- API test coverage on auth/webhook/publish routes reaches 80%+
- All existing tests pass with no behavioral regressions

## Out of Scope

- New features or UI changes — this is purely a refactor/hardening increment
- Database schema migrations that alter existing column semantics
- Rewriting the OAuth provider integration (only error-path testing is in scope)
- Horizontal scaling or infrastructure changes (e.g., worker queues, CDN)
- Addressing the remaining 26 lower-priority audit findings (future increments)
- **Deferred: large-response streaming (formerly AC-US4-05)** — dropped during planning; ETag + cursor pagination (AC-US4-04 / T-019) mitigates the primary performance concern. Track separately if still needed.

## Dependencies

- Prisma interactive transactions must be supported by the current database adapter (Cloudflare D1 / libSQL — verify before implementation)
- `pLimit` or equivalent concurrency-limiting library must be added as a dependency for enrichment parallelization
- KV namespace must support TTL-less writes (or infinite TTL) for the published-skills fix
