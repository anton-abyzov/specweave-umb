# Tasks — 0350 Queue Architecture & Performance Overhaul

### T-001: Write submissions to Prisma DB on creation
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05 | **Status**: [ ] pending
**Test**: Given a batch submission of 56 skills → When createSubmissionsBatch completes → Then db.submission.count() returns 56 AND stats endpoint shows non-zero totals

### T-002: Remove KV submissions:index blob and switch GET to DB
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04, AC-US2-05 | **Status**: [ ] pending
**Test**: Given 56 submissions in DB → When GET /api/v1/submissions called → Then returns paginated results from DB with accurate total count

### T-003: Fix external-scan-dispatch.ts process.env bug
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03 | **Status**: [ ] pending
**Test**: Given SCANNER_WORKERS configured in CF env → When dispatchExternalScans called in queue context → Then HTTP request sent to Hetzner VM

### T-004: Add repoUrl to search matching
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02 | **Status**: [ ] pending
**Test**: Given skills from "awesome-copilot" repo → When searching "awesome-copilot" → Then all skills from that repo returned

### T-005: Parallel cron crawl dispatch
**User Story**: US-005 | **Satisfies ACs**: AC-US5-05 | **Status**: [ ] pending
**Test**: Given 5 VM crawl sources → When cron fires → Then all 5 dispatched in parallel (not sequential)

### T-006: Fix process.env across admin routes
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01, AC-US5-02, AC-US5-03, AC-US5-04 | **Status**: [ ] pending
**Test**: Given admin route with X-Internal-Key header → When called in CF Worker context → Then auth succeeds via resolveEnv

### T-007: Update tests and verify
**User Story**: All | **Satisfies ACs**: All | **Status**: [ ] pending
**Test**: Given all changes applied → When npm test runs → Then all tests pass
