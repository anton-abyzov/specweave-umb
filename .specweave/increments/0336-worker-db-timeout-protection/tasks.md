# Tasks — 0336 Worker DB Timeout Protection

### T-001: Add Prisma $extends timeout interceptor to db.ts
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-03 | **Status**: [x] completed
**Test**: Given a Prisma model operation → When it exceeds 8s → Then it rejects with "DB query timed out after 8000ms [Model.operation]"

### T-002: Wrap $queryRaw in search.ts with withDbTimeout
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02 | **Status**: [x] completed
**Test**: Given a $queryRaw call → When it exceeds timeout → Then it rejects with timeout error

### T-003: Wrap $transaction calls with withDbTimeout
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02 | **Status**: [x] completed
Files: blocklist-upsert.ts, auth/refresh, auth/user/refresh, admin/dequeue, admin/reprioritize, problem-reports/mine

### T-004: Clean up OAuth callback redundant wrapping
**User Story**: US-001 | **Satisfies ACs**: AC-US1-05 | **Status**: [x] completed

### T-005: Update/add tests for timeout behavior
**User Story**: US-001 | **Satisfies ACs**: AC-US1-06 | **Status**: [x] completed

### T-006: Build, deploy, verify production
**User Story**: US-001 | **Satisfies ACs**: AC-US1-04 | **Status**: [x] completed
