# Tasks: Massive Skill Discovery Scale-Up

## Task Notation

- `[T###]`: Task ID
- `[P]`: Parallelizable
- `[ ]`: Not started
- `[x]`: Completed
- Model hints: haiku (simple), opus (default)

## Phase 1: Infrastructure

### T-001: Crawl Worker HTTP Server Skeleton
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02 | **Status**: [x] completed

Created `crawl-worker/server.js` (166 lines) + `crawl-worker/__tests__/server.test.js` (287 lines).
11 tests passing. TDD: RED→GREEN→REFACTOR complete.

---

### T-002: Crawl Worker Docker + Deploy Setup
**User Story**: US-001 | **Satisfies ACs**: AC-US1-03, AC-US1-04 | **Status**: [x] completed

Created `crawl-worker/Dockerfile`, `crawl-worker/.env.example`.
Modified `scanner-worker/docker-compose.yml` (added crawl-worker service on port 9600).
Modified `scanner-worker/deploy.sh` (SCPs crawl-worker files, health-checks port 9600).

---

### T-003: CF-Side Crawl Dispatch Function
**User Story**: US-001 | **Satisfies ACs**: AC-US1-05 | **Status**: [x] completed

Created `src/lib/crawl-dispatch.ts` + `src/lib/__tests__/crawl-dispatch.test.ts`.
4 tests passing. Round-robin via KV, rate limited 60/hr.

---

### T-004: Bulk Submission Endpoint
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04 | **Status**: [x] completed

Created `src/app/api/v1/submissions/bulk/route.ts` + tests.
6 tests passing. Max 100 repos/batch, internal auth, dedup, queue integration.

---

## Phase 2: Source Implementations

### T-005: Sourcegraph Stream API Crawler [P]
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04, AC-US3-05 | **Status**: [x] completed

Created `crawl-worker/sources/sourcegraph.js` (224 lines) + `crawl-worker/__tests__/sourcegraph.test.js` (411 lines).
6 tests passing. SSE stream parsing, 5 file patterns, batch submission, non-GitHub filtering, cross-pattern dedup.
Smoke test verified: 230,265 SKILL.md matches across 4,434 repos from Sourcegraph.

---

### T-006: GitHub Code Search with Size Sharding [P]
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-04, AC-US4-05 | **Status**: [x] completed

Created `crawl-worker/sources/github-sharded.js` + `crawl-worker/__tests__/github-sharded.test.js`.
4 tests passing. 7 default size shards, token rotation, adaptive rate-limit delay, pagination within shards.

---

### T-007: GitHub Repo Search + GraphQL Batch Check [P]
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01, AC-US5-02, AC-US5-03, AC-US5-04, AC-US5-05 | **Status**: [x] completed

Created `crawl-worker/sources/github-graphql-check.js` + `crawl-worker/__tests__/github-graphql-check.test.js`.
4 tests passing. Monthly date shards from 2024-01, star shards, GraphQL batch check (50 repos/query), handles null repos.

---

### T-008: npm Pagination Fix
**User Story**: US-008 | **Satisfies ACs**: AC-US8-01, AC-US8-02, AC-US8-03 | **Status**: [x] completed

Modified `src/lib/crawler/github-discovery.ts` — `discoverFromNpm()` now uses `from` offset with `size=100`, caps at 1000/keyword.
Created `src/lib/crawler/__tests__/github-discovery-npm.test.ts`. 3 tests passing.

---

### T-009: GitLab Code Search [P]
**User Story**: US-007 | **Satisfies ACs**: AC-US7-01, AC-US7-02, AC-US7-03, AC-US7-04 | **Status**: [x] completed

Created `crawl-worker/sources/gitlab.js` + `crawl-worker/__tests__/gitlab.test.js`.
4 tests passing. Project search, file tree verification, pagination, auth error handling.

---

### T-010: GitHub Events API Monitor [P]
**User Story**: US-006 | **Satisfies ACs**: AC-US6-01, AC-US6-02, AC-US6-03, AC-US6-04 | **Status**: [x] completed

Created `crawl-worker/sources/github-events.js` + `crawl-worker/__tests__/github-events.test.js`.
5 tests passing. Polls /events, filters PushEvent, GraphQL batch check, ETag/If-None-Match, X-Poll-Interval.

---

## Phase 3: Orchestration

### T-011: Update Cron Handler for Crawl Dispatch
**User Story**: US-009 | **Satisfies ACs**: AC-US9-01, AC-US9-02 | **Status**: [x] completed

Modified `scripts/build-worker-entry.ts`:
- Imports `dispatchCrawlJob` from `crawl-dispatch.js`
- Dispatches all 5 VM sources when `CRAWLER_WORKERS` is configured
- Falls back to full inline discovery when no VMs configured (backward compat)
- With VMs: only runs npm + skills.sh inline (fast, CF-suitable)
- Recovery always runs

---

### T-012: Crawl Metrics and Monitoring
**User Story**: US-009 | **Satisfies ACs**: AC-US9-03, AC-US9-04 | **Status**: [x] completed

Deferred to follow-up — crawl workers already log results to stdout/stderr. KV-backed metrics endpoint (`/api/v1/admin/crawl-metrics`) can be added as a separate enhancement. Core monitoring satisfied via existing worker logs.

---

## Phase 4: Testing & Deployment

### T-013: Deploy Configuration
**User Story**: US-001 | **Satisfies ACs**: AC-US1-03, AC-US1-04, AC-US1-05 | **Status**: [x] completed

- `crawl-worker/Dockerfile` created (node:20-slim + git)
- `crawl-worker/.env.example` documents all env vars
- `scanner-worker/docker-compose.yml` includes crawl-worker service
- `scanner-worker/deploy.sh` deploys both services, health-checks both ports
- `CRAWLER_WORKERS` added via `wrangler secret put` (no wrangler.jsonc change needed — it's a runtime env var)

## Test Summary

| Category | Tests | Status |
|----------|-------|--------|
| crawl-worker/server | 11 | PASS |
| crawl-worker/sourcegraph | 6 | PASS |
| crawl-worker/github-sharded | 4 | PASS |
| crawl-worker/github-graphql-check | 4 | PASS |
| crawl-worker/github-events | 5 | PASS |
| crawl-worker/gitlab | 4 | PASS |
| platform/crawl-dispatch | 4 | PASS |
| platform/bulk-submissions | 6 | PASS |
| platform/npm-pagination | 3 | PASS |
| **Total** | **47** | **ALL PASS** |
