# Implementation Plan: vskill-platform Audit Fixes: Performance, Simplicity & Correctness

## Overview

Refactor vskill-platform across 4 domains: (1) split the 1,781-line submission-store.ts monolith into cohesive modules, (2) fix correctness issues (race conditions, CSRF, env resolution), (3) improve performance (enrichment parallelization, incremental stats, streaming), (4) reduce queue page duplication. All changes are internal refactors with zero public API surface changes.

## Architecture

### ADR-1: submission-store.ts Module Split

**Decision**: Split submission-store.ts (1,781 lines, 30+ exports, 28+ consumers) into 4 focused modules with a barrel re-export for backward compatibility.

**Module boundaries**:

```
src/lib/submission/
  index.ts              # Barrel re-export (all existing imports keep working)
  kv-store.ts           # KV CRUD: getKV(), createSubmission, updateState,
                        #   updateStateMulti, storeScanResult, getSubmission,
                        #   getSubmissionFull, ensureKVEntry, markVendor,
                        #   setContentHash, getSubmissionsFresh (~400 lines)
  db-persist.ts         # DB persistence helpers: persistSubmissionToDb,
                        #   persistStateChangeToDb, persistScanResultToDb,
                        #   raw SQL fallbacks (getNeonSql, persistStateChangeRaw,
                        #   persistStateEventRaw) (~250 lines)
  publish.ts            # Publish workflow: publishSkill, deriveCertTier,
                        #   resolveSlug, enumeratePublishedSkills,
                        #   getPublishedSkillsList, getPublishedSkill,
                        #   migrateSkillSlugs (~500 lines)
  recovery.ts           # Stuck submission recovery: getStuckSubmissions,
                        #   getStaleReceivedSubmissions, StuckSubmission type (~200 lines)
  types.ts              # All shared interfaces: StoredSubmission, StoredScanResult,
                        #   StoredScanFinding, StateHistoryEntry, SubmissionSummary,
                        #   PublishedSkillSummary, MigrationResult, StuckSubmission (~120 lines)
```

**Import graph impact**: Zero — `src/lib/submission/index.ts` re-exports everything from `src/lib/submission-store.ts`. The 28+ consumers continue importing from `@/lib/submission-store` (keep the old file as a thin re-export from `@/lib/submission/index`). Over time, consumers can migrate to targeted imports.

**Why this split**:
- KV operations and DB persistence have different failure modes (KV is fast/ephemeral, DB is slow/durable)
- Publish workflow is the most complex function (publishSkill is ~300 lines) and has its own dependency chain (trust scoring, GitHub metrics, search index)
- Recovery functions are cron-only, never called from request paths
- Types are imported independently by 5+ consumers (tests, admin pages)

**Alternatives rejected**:
- Split by submission lifecycle phase (create/scan/approve/publish) — too many cross-phase dependencies
- Keep as single file with regions — doesn't solve the testability or import-weight problem

### ADR-2: Publish Workflow Transaction Boundaries

**Decision**: Use Prisma `$transaction` with optimistic concurrency check (version field) for the approve-to-publish flow.

**Current problem**: The approve route (`/api/v1/admin/submissions/[id]/approve/route.ts`) has a TOCTOU race:
1. Line 53-63: Reads submission state, checks `APPROVABLE_STATES`
2. Line 130-154: Updates state to PUBLISHED
3. Line 158-181: Calls `publishSkill()` which does a `skill.upsert()`

Between steps 1 and 2, another admin could approve the same submission, causing duplicate Skill creation.

**Solution**: Wrap the state check + state update + publishSkill in a single Prisma transaction with a `version` check:

```typescript
await prisma.$transaction(async (tx) => {
  const sub = await tx.submission.findUnique({ where: { id } });
  if (!sub || !APPROVABLE_STATES.has(sub.state)) throw new ConflictError();
  
  // Optimistic lock: ensure no concurrent modification
  const updated = await tx.submission.updateMany({
    where: { id, state: sub.state },  // state acts as version guard
    data: { state: 'PUBLISHED', updatedAt: new Date() },
  });
  if (updated.count === 0) throw new ConflictError();
  
  // publishSkill within same transaction
  await publishSkillInTx(tx, id);
});
```

**Why `$transaction` over optimistic locking with retries**:
- PrismaClient over Neon HTTP supports interactive transactions (non-pooled connection)
- The operation is admin-initiated (low frequency), not hot-path
- Retry-based optimistic locking adds complexity without benefit at this scale

**Why not database-level advisory locks**:
- Neon serverless doesn't support `pg_advisory_lock` reliably across HTTP connections
- Prisma transaction isolation (READ COMMITTED default) is sufficient for this use case

### ADR-3: Enrichment Parallelization Strategy

**Decision**: Use `pLimit(concurrency=5)` for GitHub API calls within the enrichment batch, with per-request rate-limit detection and circuit-breaking.

**Current state**: The enrichment loop (`src/lib/cron/enrichment.ts`) already fetches npm downloads in bulk (lines 90-98), but GitHub metrics are fetched sequentially in the `for (const skill of skills)` loop (line 104). Each iteration does a `Promise.allSettled` for GitHub + npm registry (line 124), but only for a single skill.

**Proposed change**:
```typescript
import pLimit from "p-limit";

const limit = pLimit(5);  // 5 concurrent GitHub API calls

// Replace sequential for-loop with parallel-limited execution
const results = await Promise.allSettled(
  skills.map((skill) => limit(() => processSkill(skill, rateLimitState, opts)))
);
```

**Concurrency level justification**:
- GitHub's unauthenticated rate limit: 60 req/hr. Authenticated: 5,000 req/hr.
- With token (always present in prod), 5 concurrent calls = ~50 skills processed in 10s vs ~50s sequential
- Rate-limit backoff (lines 107-116) already handles 429s — shared `rateLimitState` with mutex prevents thundering herd

**Error isolation**: Each skill's processing is isolated via `Promise.allSettled`. A 429 from one request triggers backoff for subsequent requests but doesn't fail the batch.

**Backoff strategy enhancement**: Current exponential backoff (30s start, 2m max) is correct. Add: if 3+ consecutive 429s, short-circuit remaining skills in the batch (they'll be picked up next cron cycle).

### ADR-4: Stats Incremental Computation

**Decision**: Use application-level change detection with KV-based delta tracking. No DB-level materialized views.

**Current state**: `stats-compute.ts` runs 10+ aggregate queries per refresh. `stats-refresh.ts` writes results to KV and DB. The cron runs every 30 minutes.

**Problem**: Full table scans of 55K+ skills every 30 minutes is expensive on Neon serverless (cold start + query time).

**Proposed approach**:
1. Track a `lastStatsComputedAt` timestamp in KV
2. On each cron tick, query only skills modified since `lastStatsComputedAt`:
   ```sql
   SELECT COUNT(*), SUM(CASE WHEN certTier='CERTIFIED' THEN 1 ELSE 0 END), ...
   FROM "Skill" WHERE "updatedAt" > $lastComputedAt AND "isDeprecated" = false
   ```
3. Apply deltas to the cached stats object (add new, subtract deprecated)
4. Every 6 hours, run a full recompute to correct drift

**Why not DB materialized views**:
- Neon serverless doesn't support `REFRESH MATERIALIZED VIEW CONCURRENTLY` reliably
- Application-level delta is simpler and allows KV caching (sub-ms reads)
- Full recompute every 6h catches any drift

**Why not Cloudflare Durable Objects**:
- Overengineered for a 30-min cron job
- Adds operational complexity (DO lifecycle, billing model)
- KV + application-level delta achieves the same result

### ADR-5: Queue Page Shared Module

**Decision**: Extract shared types, constants, and data-fetching hooks into `src/app/queue/shared/`.

**Current duplication analysis**:
- `admin/queue/page.tsx` (1,496 lines): Admin queue dashboard with DLQ management, queue pause/resume, metrics
- `queue/QueuePageClient.tsx` (1,309 lines): Public queue view with SSE streaming, search, filters

**Shared surface** (to extract):
```
src/app/queue/shared/
  types.ts       # QueueStatus, DLQEntry, StuckEntry, Submission, state badge maps (~80 lines)
  constants.ts   # STATES array, STATE_BADGES map, FilterCategory type (~40 lines)
  hooks/
    useQueueData.ts     # Shared fetch + pagination logic (~100 lines)
    useQueuePolling.ts  # Shared auto-refresh interval logic (~50 lines)
```

**What stays separate**:
- Admin page keeps DLQ management, queue pause/resume, metrics visualization (admin-only features)
- Public page keeps SSE streaming, URL-driven state, keyboard shortcuts (public-facing UX)

**Why not a single unified component with role-based rendering**:
- Admin and public pages have fundamentally different data sources (admin uses `authFetch`, public uses standard fetch)
- Merging would create a larger component with more conditional branches
- Separate pages allow different caching strategies (admin: no-cache, public: ISR)

### ADR-6: Streaming Architecture for Skills API

**Decision**: Use cursor-based pagination with ETag support. No streaming.

**Current state**: `GET /api/v1/skills/route.ts` returns paginated JSON (limit/offset). KV cache with 35-min TTL.

**Why not NDJSON/ReadableStream**:
- Cloudflare Workers support `ReadableStream`, but the current payload size is small (20 items/page, ~50KB)
- No consumer currently needs streaming — the React frontend fetches pages
- NDJSON requires custom client parsing; standard `fetch().json()` is simpler
- Adding streaming for a paginated endpoint that already works is overengineering

**What to add instead**:
1. **ETag header**: Hash of the response body. Return 304 on `If-None-Match` match.
2. **Cursor-based pagination**: Replace offset with cursor (`?after=<skillId>`) for consistent results during data changes. Offset-based pagination skips/duplicates items when skills are added/deprecated between pages.

### ADR-7: CSRF Protection

**Decision**: Enforce `SameSite=Strict` on auth cookies + validate `Origin`/`Referer` headers on mutating requests.

**Current state**: Auth tokens are stored in cookies (`src/lib/auth-cookies.ts`). Login route (`/api/v1/auth/login/route.ts`) generates JWT tokens. No CSRF protection beyond rate limiting.

**Why SameSite + Origin check over CSRF tokens**:
- CSRF tokens require server-side state (or double-submit cookie pattern) — adds complexity on Cloudflare Workers
- `SameSite=Strict` prevents cross-site cookie inclusion entirely
- `Origin` header validation catches edge cases where SameSite is downgraded (old browsers, 302 redirects)
- The application uses JWT bearer tokens for API routes (not cookie-based auth for API) — CSRF risk is limited to admin panel routes that use cookie auth

**Implementation**:
1. Set `SameSite=Strict` on all auth cookies (currently may be `Lax` or unset)
2. Add middleware that validates `Origin` header on POST/PATCH/DELETE requests matches `verified-skill.com`
3. Skip validation for webhook routes (use HMAC signature instead)

### ADR-8: Env Resolution Consolidation

**Decision**: Use `resolveEnv()` consistently across all routes. Remove direct `process.env` fallbacks.

**Current state**: `scan-results/route.ts` (line 29) uses `env.WEBHOOK_SECRET || process.env.WEBHOOK_SECRET` as a fallback chain. Other routes use `resolveEnv()` from `src/lib/env-resolve.ts`.

**Problem**: Inconsistent env resolution leads to silent failures on Cloudflare Workers where `process.env` is not populated.

**Fix**: All routes should use `resolveEnv()` exclusively. The `env-resolve.ts` module already handles the 3-tier fallback (worker env → CF context → process.env).

## Technology Stack

- **Runtime**: Cloudflare Workers (via OpenNext)
- **Framework**: Next.js 15, React 19
- **Database**: Neon PostgreSQL via Prisma 6.4
- **Cache**: Cloudflare KV
- **New dependency**: `p-limit` (already in the npm ecosystem, zero transitive deps, ~1KB)

## Implementation Phases

### Phase 1: Foundation (Types + Module Split)
1. Extract `src/lib/submission/types.ts` from submission-store.ts
2. Extract `src/lib/submission/db-persist.ts` (DB persistence helpers)
3. Extract `src/lib/submission/kv-store.ts` (KV CRUD operations)
4. Extract `src/lib/submission/publish.ts` (publish workflow)
5. Extract `src/lib/submission/recovery.ts` (stuck submission recovery)
6. Create `src/lib/submission/index.ts` barrel + thin `submission-store.ts` re-export
7. Verify all 28+ consumers still compile and tests pass

### Phase 2: Correctness Fixes
8. Fix approve route race condition with transaction boundary
9. Consolidate env resolution (remove process.env fallbacks in scan-results webhook)
10. Add CSRF protection (SameSite cookies + Origin validation middleware)
11. Fix rate-limit ordering in submissions POST (rate limit before body parse)

### Phase 3: Performance
12. Parallelize enrichment loop with pLimit(5)
13. Add enrichment circuit-breaker (3+ consecutive 429s = stop batch)
14. Implement incremental stats computation with delta tracking
15. Add ETag support to skills API route
16. Add cursor-based pagination to skills API route

### Phase 4: Simplicity + Duplication
17. Extract shared queue types and constants
18. Extract shared queue data-fetching hooks
19. Add Suspense boundary to layout.tsx for auth provider

## Testing Strategy

- **Unit tests**: Each extracted module gets focused unit tests (mock KV, mock Prisma)
- **Integration tests**: Publish workflow transaction tested with concurrent approve simulation
- **Regression**: All existing tests must pass after module split (barrel re-export guarantees API compatibility)
- **Performance**: Enrichment parallelization measured by batch completion time (target: 50% reduction)

## Technical Challenges

### Challenge 1: Barrel Re-export Preserves Module-Level State
**Problem**: `submission-store.ts` has module-level `sleep()` function and relies on shared `getKV()` for KV binding resolution. Splitting into modules means each module has its own scope.
**Solution**: Shared utilities (`getKV`, `sleep`, `isWasmError`, `getNeonSql`) go into `kv-store.ts` and are imported by other modules. The barrel re-export ensures a single module graph — no duplicate state.
**Risk**: Low — Node.js ESM modules are singletons. Two imports of the same module share state.

### Challenge 2: Prisma HTTP Mode Transaction Support
**Problem**: Comment at line 269 says "PrismaNeonHTTP doesn't support transactions (HTTP mode is stateless)". The approve route needs a transaction for race condition fix.
**Solution**: Use the non-pooled (direct) connection URL for transaction routes. Neon supports interactive transactions over WebSocket (`?sslmode=require`), and Prisma 6.4 handles this via `@prisma/adapter-neon`. Only the approve route (admin, low frequency) needs this.
**Risk**: Medium — must verify the Neon WebSocket adapter is configured. If not, fall back to `updateMany` with state guard (optimistic concurrency).

### Challenge 3: Stats Delta Drift
**Problem**: Incremental stats computation can drift from actual values if events are missed (e.g., skill deprecated during KV write).
**Solution**: Full recompute every 6 hours as drift correction. Consistency checks (`statsAreConsistent`) already exist and will catch gross drift.
**Risk**: Low — 6-hour full recompute is a safety net, not primary mechanism.
