---
increment: 0668-vskill-platform-audit-fixes
title: "vskill-platform Audit Fixes: Performance, Simplicity & Correctness"
test_mode: TDD
coverage_target: 90
---

# Tasks: vskill-platform Audit Fixes

## Phase 1: Foundation — Types + Module Split (US-002)

### T-001: Extract shared types module
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01 | **Status**: [ ] pending
**Test Plan**: Given the existing submission-store.ts interfaces → When types.ts is created with all shared interfaces → Then `tsc --noEmit` passes and all consumers importing from submission-store continue to compile
```
Given: submission-store.ts exports StoredSubmission, StoredScanResult, StoredScanFinding, StateHistoryEntry, SubmissionSummary, PublishedSkillSummary, MigrationResult, StuckSubmission
When: src/lib/submission/types.ts is created with all those interfaces (~120 lines)
Then: No TypeScript errors across the codebase, no behavioral change
```

### T-002: Extract db-persist module
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01 | **Status**: [ ] pending
**Test Plan**: Given the DB persistence helpers in submission-store.ts → When db-persist.ts is extracted → Then unit tests for persistSubmissionToDb, persistStateChangeToDb, persistScanResultToDb pass with mocked Prisma client
```
Given: DB persistence helpers (persistSubmissionToDb, persistStateChangeToDb, persistScanResultToDb, getNeonSql, persistStateChangeRaw, persistStateEventRaw) in submission-store.ts
When: src/lib/submission/db-persist.ts is created (~250 lines) importing from types.ts
Then: Unit tests with vi.mock('@prisma/client') cover happy path + DB error path for each helper
```

### T-003: Extract kv-store module
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01 | **Status**: [ ] pending
**Test Plan**: Given KV CRUD operations in submission-store.ts → When kv-store.ts is extracted → Then unit tests for getKV, createSubmission, updateState, getSubmission pass with mocked KV binding
```
Given: KV CRUD operations (getKV, createSubmission, updateState, updateStateMulti, storeScanResult, getSubmission, getSubmissionFull, ensureKVEntry, markVendor, setContentHash, getSubmissionsFresh) in submission-store.ts
When: src/lib/submission/kv-store.ts is created (~400 lines) with shared getKV/sleep utilities
Then: Unit tests with mock KV object cover read, write, error, and not-found paths
```

### T-004: Extract publish module
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01 | **Status**: [ ] pending
**Test Plan**: Given publish workflow functions in submission-store.ts → When publish.ts is extracted → Then existing publishSkill tests pass and no TTL logic regresses
```
Given: Publish workflow (publishSkill, deriveCertTier, resolveSlug, enumeratePublishedSkills, getPublishedSkillsList, getPublishedSkill, migrateSkillSlugs) in submission-store.ts
When: src/lib/submission/publish.ts is created (~500 lines) importing from kv-store.ts and db-persist.ts
Then: All existing publishSkill unit tests pass; file is ≤500 lines
```

### T-005: Extract recovery module
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01 | **Status**: [ ] pending
**Test Plan**: Given stuck submission recovery functions in submission-store.ts → When recovery.ts is extracted → Then unit tests for getStuckSubmissions and getStaleReceivedSubmissions pass with mocked Prisma
```
Given: Recovery functions (getStuckSubmissions, getStaleReceivedSubmissions, StuckSubmission type) in submission-store.ts
When: src/lib/submission/recovery.ts is created (~200 lines) importing from types.ts
Then: Unit tests verify correct filtering logic using mocked Prisma responses
```

### T-006: Create barrel index and thin re-export shim
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02 | **Status**: [ ] pending
**Test Plan**: Given 28+ consumers importing from @/lib/submission-store → When barrel index and shim are created → Then all consumer imports resolve without changes to consumer files
```
Given: 28+ files importing from src/lib/submission-store
When: src/lib/submission/index.ts re-exports all symbols from the 4 modules AND src/lib/submission-store.ts becomes a thin re-export from src/lib/submission/index
Then: `tsc --noEmit` produces zero new errors; no consumer file is modified
```

### T-007: Verify module split — regression test run
**User Story**: US-002 | **Satisfies ACs**: AC-US2-02, AC-US2-03 | **Status**: [ ] pending
**Test Plan**: Given the completed module split → When all existing tests are run → Then zero test failures and zero TypeScript errors
```
Given: All 5 extracted modules and barrel shim in place
When: `npx vitest run` is executed in repositories/anton-abyzov/vskill-platform/
Then: All pre-existing submission-store tests pass; no behavioral regressions; each new module file ≤500 lines
```

---

## Phase 2: Correctness Fixes (US-001)

### T-008: Fix webhook env silent fallback (AC-US1-01)
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01 | **Status**: [ ] pending
**Test Plan**: Given scan-results webhook uses process.env fallback → When resolveEnv() is used exclusively → Then missing WEBHOOK_SECRET returns 500 instead of silently proceeding
```
Given: src/app/api/v1/webhooks/scan-results/route.ts line 29 uses env.WEBHOOK_SECRET || process.env.WEBHOOK_SECRET
When: The fallback chain is replaced with resolveEnv() call that throws/errors on missing secret
Then: Unit test confirms that when resolveEnv() returns null, the route returns 500; webhook auth is never bypassed
```

### T-009: Fix publish race condition with transaction boundary (AC-US1-02, AC-US1-03)
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02, AC-US1-03 | **Status**: [ ] pending
**Test Plan**: Given approve route has TOCTOU race between state check and publish → When Prisma $transaction with optimistic state guard is added → Then concurrent approvals fail with 409 and only one publish succeeds
```
Given: approve/route.ts reads state at line 53-63, updates at line 130-154, calls publishSkill at 158-181 (three separate operations)
When: All three steps are wrapped in prisma.$transaction with updateMany({ where: { id, state: sub.state } }) as optimistic lock
Then: Integration test simulating two concurrent approvals confirms only one succeeds (count===1 guard); publishSkill failure rolls back approval state
```

### T-010: Fix rate-limit ordering before KV access (AC-US1-04)
**User Story**: US-001 | **Satisfies ACs**: AC-US1-04 | **Status**: [ ] pending
**Test Plan**: Given submissions POST reads KV before rate limit check → When rate limit is moved to first check → Then unauthenticated requests are rejected before any KV read occurs
```
Given: src/app/api/v1/submissions/route.ts performs KV cache access before rate-limit check
When: Rate-limit check is moved to be the first operation in the handler
Then: Unit test with mocked rate limiter returning "blocked" confirms KV mock is never called; rate-limited requests return 429 immediately
```

### T-011: Fix broken token rotation in login route (AC-US1-05)
**User Story**: US-001 | **Satisfies ACs**: AC-US1-05 | **Status**: [ ] pending
**Test Plan**: Given login route uses Promise.allSettled which swallows refresh-token DB insertion failure → When failure causes login to fail → Then rotation failure returns 500 instead of silent success
```
Given: src/app/api/v1/auth/login/route.ts uses Promise.allSettled for refresh-token insertion
When: Promise.allSettled is replaced with Promise.all (or explicit rejection check) so DB failure propagates
Then: Unit test confirms that when DB insertion rejects, login returns 500 (not 200 with broken token state)
```

### T-012: Add CSRF protection — SameSite cookies and Origin validation (AC-US4-06)
**User Story**: US-004 | **Satisfies ACs**: AC-US4-06 | **Status**: [ ] pending
**Test Plan**: Given auth cookies lack SameSite=Strict and no Origin header validation exists → When SameSite is set and middleware validates Origin on mutating requests → Then cross-origin POST requests are rejected with 403
```
Given: src/lib/auth-cookies.ts sets cookies without SameSite=Strict; no Origin check on POST endpoints
When: auth-cookies.ts updated to SameSite=Strict; middleware added to validate Origin header matches verified-skill.com on POST/PATCH/DELETE (skipping webhook routes)
Then: Unit test with Origin: https://evil.example.com on admin POST returns 403; webhook routes bypass check
```

---

## Phase 3: Performance Optimization (US-003)

### T-013: Parallelize enrichment loop with pLimit (AC-US3-01)
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01 | **Status**: [ ] pending
**Test Plan**: Given enrichment.ts processes skills sequentially → When pLimit(5) replaces the sequential for-loop → Then batch of 50 skills completes in ≤30s (vs ~250s sequential)
```
Given: src/lib/cron/enrichment.ts iterates skills sequentially with await inside for-loop
When: pLimit is installed (npm install p-limit); sequential loop replaced with Promise.allSettled(skills.map(s => limit(() => processSkill(s, ...))))
Then: Unit test with 10 mocked skills confirms all run concurrently up to limit=5; no skill is processed more than once; circuit-breaker stops batch after 3 consecutive 429s
```

### T-014: Cache skillPathValidAt to skip redundant HEAD requests (AC-US3-02)
**User Story**: US-003 | **Satisfies ACs**: AC-US3-02 | **Status**: [ ] pending
**Test Plan**: Given enrichment.ts sends HEAD to raw.githubusercontent.com for every skill every run → When skillPathValidAt timestamp is cached in DB → Then HEAD requests are skipped for skills validated within 24h
```
Given: enrichment.ts makes HEAD request for every skill regardless of last validation time
When: skillPathValidAt column (or equivalent) is read before HEAD; if within 24h, request is skipped
Then: Unit test with 5 skills (3 validated <24h, 2 stale) confirms HEAD mock is called exactly 2 times; DB update is called only for the 2 re-validated skills
```

### T-015: Implement incremental stats computation (AC-US3-03)
**User Story**: US-003 | **Satisfies ACs**: AC-US3-03 | **Status**: [ ] pending
**Test Plan**: Given stats-refresh.ts runs full table scan every 30min → When delta tracking with lastStatsComputedAt KV key is added → Then only modified-since-last-run records are aggregated each tick
```
Given: src/lib/cron/stats-refresh.ts runs 10+ full aggregate queries per tick on 55K+ skills
When: lastStatsComputedAt is read from KV; incremental query uses WHERE updatedAt > lastStatsComputedAt; full recompute runs every 6h as drift correction
Then: Unit test with 100-row mock: incremental tick queries only rows with updatedAt after watermark; full recompute triggers when watermark is missing or >6h old
```

### T-016: Consolidate publisher double query (AC-US3-04)
**User Story**: US-003 | **Satisfies ACs**: AC-US3-04 | **Status**: [ ] pending
**Test Plan**: Given data.ts uses groupBy + separate raw SQL star-dedup → When replaced with single $queryRaw → Then publisher list endpoint makes one DB round-trip instead of two
```
Given: src/lib/data.ts runs groupBy query then a separate raw SQL star-dedup query for publishers
When: Both queries are merged into a single $queryRaw with the dedup logic inline
Then: Unit test with mocked $queryRaw confirms it is called exactly once; output matches previous two-query result for same dataset
```

### T-017: Enable ISR on skill detail page (AC-US3-05)
**User Story**: US-003 | **Satisfies ACs**: AC-US3-05 | **Status**: [ ] pending
**Test Plan**: Given skill page runs DB query on every request → When revalidate: 3600 is added → Then page is served from cache after first load and DB is not hit on subsequent requests within 1h
```
Given: src/app/skills/[owner]/[repo]/[skill]/page.tsx fetches from DB on every page view
When: export const revalidate = 3600 is added to the page module
Then: Build-time check confirms revalidate export exists with value 3600; no regression in page content for known skill slugs
```

### T-018: Add Suspense boundaries to layout.tsx (AC-US3-06)
**User Story**: US-003 | **Satisfies ACs**: AC-US3-06 | **Status**: [ ] pending
**Test Plan**: Given layout.tsx renders slow async children synchronously → When Suspense boundaries wrap slow children → Then page shell renders immediately without waiting for async children
```
Given: src/app/layout.tsx has async children (auth provider, analytics) rendered without Suspense
When: <Suspense fallback={null}> or skeleton fallback wraps slow async children
Then: Unit test with a slow child (delayed 100ms) confirms the layout renders immediately; child appears after delay without blocking parent render
```

### T-019: Add ETag and cursor-based pagination to skills API (AC-US4-04)
**User Story**: US-004 | **Satisfies ACs**: AC-US4-04 | **Status**: [ ] pending
**Test Plan**: Given skills API returns no ETag and uses offset pagination → When ETag + cursor pagination are added → Then repeated GET with matching If-None-Match returns 304; cursor-based pages return consistent results
```
Given: src/app/api/v1/skills/route.ts uses offset pagination and returns no ETag or Last-Modified headers
When: ETag (hash of response body) and Last-Modified headers are added; cursor (?after=<skillId>) replaces offset for page navigation
Then: Unit test: first GET returns 200 + ETag; second GET with If-None-Match: <etag> returns 304 with no body; cursor GET returns correct next page without skips
```

---

## Phase 4: Simplicity + Duplication (US-004)

### T-020: Extract shared queue types and constants (AC-US4-01)
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01 | **Status**: [ ] pending
**Test Plan**: Given QueueStatus, DLQEntry, state badge maps are duplicated across admin and public queue pages → When extracted to src/app/queue/shared/types.ts and constants.ts → Then both pages import from shared and combined line count is reduced by ≥40%
```
Given: admin/queue/page.tsx (1496 lines) and queue/QueuePageClient.tsx (1309 lines) duplicate type definitions and constants
When: QueueStatus, DLQEntry, StuckEntry, Submission, STATES array, STATE_BADGES map, FilterCategory are moved to src/app/queue/shared/types.ts (~80 lines) and constants.ts (~40 lines)
Then: Both files import from shared; combined line count is ≤1530 lines (≥40% reduction from 2805); TypeScript compiles clean
```

### T-021: Extract shared queue data-fetching hooks (AC-US4-01)
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01 | **Status**: [ ] pending
**Test Plan**: Given fetch+pagination and auto-refresh logic are duplicated in both queue pages → When extracted to useQueueData and useQueuePolling hooks → Then both pages use shared hooks without duplicating fetch/poll logic
```
Given: Fetch + pagination logic (~100 lines) and auto-refresh interval logic (~50 lines) are duplicated in admin/queue and queue/QueuePageClient
When: src/app/queue/shared/hooks/useQueueData.ts and useQueuePolling.ts are created; both pages refactored to use them
Then: Unit tests for both hooks pass with mocked fetch; no change in observable behavior in either queue page
```

### T-022: Eliminate any types (AC-US4-02)
**User Story**: US-004 | **Satisfies ACs**: AC-US4-02 | **Status**: [ ] pending
**Test Plan**: Given mapDbSkillToSkillData(s: any) and listAllKeys(kv: any) use untyped parameters → When replaced with proper type annotations → Then `tsc --noEmit` reports zero any-type usages in src/
```
Given: mapDbSkillToSkillData uses `s: any`; listAllKeys uses `kv: any`; other any occurrences in src/
When: All any occurrences are replaced with proper interfaces or type guards; tsconfig strict mode enforced for these files
Then: `tsc --noEmit` completes with no errors; grep for ': any' in src/ returns zero matches
```

### T-023: Remove dead code (AC-US4-03)
**User Story**: US-004 | **Satisfies ACs**: AC-US4-03 | **Status**: [ ] pending
**Test Plan**: Given _resetPublishedCache() no-op, orphaned migration scripts, and stale comment blocks exist → When deleted → Then no tests reference deleted symbols and bundle size is reduced
```
Given: _resetPublishedCache() is a no-op; orphaned migration scripts exist; stale comment blocks in production files
When: All identified dead code is deleted; grep confirms no remaining references to deleted symbols
Then: `npx vitest run` passes with no failures; no import errors; TypeScript compilation succeeds
```

### T-024: Add auth/webhook/publish test coverage to 80%+ (AC-US4-07)
**User Story**: US-004 | **Satisfies ACs**: AC-US4-07 | **Status**: [ ] pending
**Test Plan**: Given current test coverage on auth/webhook/publish routes is ~47% → When unit tests are added for all critical branches → Then coverage on these routes reaches ≥80%
```
Given: Auth (login, refresh, logout), webhooks (scan-results), and submissions/publish routes have ~47% coverage
When: Tests are added for: login success, login DB failure, token refresh, webhook HMAC validation, webhook missing secret, submission approval happy path, approval conflict (409), publish failure rollback
Then: `npx vitest run --coverage` reports ≥80% line coverage on src/app/api/v1/auth/**, src/app/api/v1/webhooks/**, src/app/api/v1/submissions/**
```

### T-025: Add OAuth callback error path tests (AC-US4-08)
**User Story**: US-004 | **Satisfies ACs**: AC-US4-08 | **Status**: [ ] pending
**Test Plan**: Given OAuth callback error rendering uses step variable with no injection protection → When tests cover all error branches → Then injection risk is confirmed absent and all error branches are tested
```
Given: OAuth callback renders error HTML using step variable; no tests cover error paths
When: Tests are written for: missing code param, invalid state, provider error, step variable with special chars (XSS probe), successful callback redirect
Then: All 5 test cases pass; XSS probe confirms step variable is escaped in output; no error branch is untested
```

### T-026: Final regression run and coverage gate
**User Story**: US-001, US-002, US-003, US-004 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05, AC-US2-01, AC-US2-02, AC-US2-03, AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04, AC-US3-05, AC-US3-06, AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-04, AC-US4-06, AC-US4-07, AC-US4-08 | **Status**: [ ] pending
**Test Plan**: Given all tasks T-001 through T-025 complete → When full test suite runs → Then zero failures, coverage ≥90%, zero TypeScript errors, no file in src/lib/ exceeds 500 lines
```
Given: All implementation tasks completed
When: npx vitest run --coverage && tsc --noEmit are executed
Then: Zero test failures; overall coverage ≥90%; tsc exits 0; no file under src/lib/ exceeds 500 lines
```
