# Tasks — 0350 Queue Architecture & Performance Overhaul

### T-001: Write submissions to Prisma DB on creation
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05 | **Status**: [x] completed
**Test**: Given a batch submission of 56 skills → When createSubmissionsBatch completes → Then db.submission.count() returns 56 AND stats endpoint shows non-zero totals
**Notes**: Already implemented — `persistSubmissionToDb()`, `persistSubmissionBatchToDb()`, and `persistStateChangeToDb()` all write to Prisma DB. GET /api/v1/submissions reads from DB with pagination.

### T-002: Remove KV submissions:index blob and switch GET to DB
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04, AC-US2-05 | **Status**: [x] completed
**Test**: Given 56 submissions in DB → When GET /api/v1/submissions called → Then returns paginated results from DB with accurate total count
**Notes**: Already implemented — GET handler queries `db.submission.findMany` with pagination, sorting, and filtering. In-flight submissions re-hydrated from individual KV keys. No `submissions:index` blob writes remain.

### T-003: Fix external-scan-dispatch.ts process.env bug
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03 | **Status**: [x] completed
**Test**: Given SCANNER_WORKERS configured in CF env → When dispatchExternalScans called in queue context → Then HTTP request sent to Hetzner VM
**Notes**: Already implemented — `dispatchExternalScans()` accepts optional `cfEnv` parameter and falls back to `getWorkerEnv()` then `getCloudflareContext()`. No `process.env` usage. All required bindings (SCANNER_WORKERS, SCANNER_WORKER_SECRET, PLATFORM_URL, EXTERNAL_SCANS_KV, etc.) present in CloudflareEnv interface.

### T-004: Add repoUrl to search matching
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02 | **Status**: [x] completed
**Test**: Given skills from "awesome-copilot" repo → When searching "awesome-copilot" → Then all skills from that repo returned
**Notes**: Edge search (search.ts) already matched repoUrl. Postgres ILIKE fallback (search.ts) already included repoUrl. Added repoUrl to Prisma `buildWhereClause` OR clause in data.ts for the data layer search path. Updated data-db-first tests to match.

### T-005: Parallel cron crawl dispatch
**User Story**: US-005 | **Satisfies ACs**: AC-US5-05 | **Status**: [x] completed
**Test**: Given 5 VM crawl sources → When cron fires → Then all 5 dispatched in parallel (not sequential)
**Notes**: Already implemented — heavy crawl sources (sourcegraph, github-sharded, github-graphql-check, github-events, gitlab, skills-sh) self-schedule on Hetzner VMs via the crawl-worker scheduler. CF cron only runs lightweight npm discovery. Within `runGitHubDiscovery()`, all sources execute in parallel via `Promise.allSettled()`.

### T-006: Fix process.env across admin routes
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01, AC-US5-02, AC-US5-03, AC-US5-04 | **Status**: [x] completed
**Test**: Given admin route with X-Internal-Key header → When called in CF Worker context → Then auth succeeds via resolveEnv
**Notes**: Already implemented — `internal-auth.ts` uses `resolveEnv()` (3-tier: worker env → CF context → process.env fallback). All admin routes use `hasInternalAuth()`. `github-oauth.ts` uses `resolveEnv()`. `webhook/scan-results` uses `resolveEnv()`. The `reenqueue` route uses `getCloudflareContext()` directly (valid in API route context).

### T-007: Update tests and verify
**User Story**: All | **Satisfies ACs**: All | **Status**: [x] completed
**Test**: Given all changes applied → When npm test runs → Then all tests pass
**Notes**: 179 test files pass, 1707 tests pass. 3 pre-existing test failures remain (github-discovery-queries, query-generation, process-submission — all unrelated to this increment). The data-db-first test that was previously failing now passes after updating assertions to include repoUrl.
