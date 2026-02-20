# Tasks: 0259 Community Security Reports

### T-001: Add SecurityReport model to Prisma schema
**User Story**: US-001, US-002, US-003 | **Satisfies ACs**: AC-US1-01, AC-US1-02 | **Status**: [x] completed
**Test**: Given schema updated → When `prisma generate` runs → Then no errors and SecurityReport model available

### T-002: POST /api/v1/reports — public submit
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04 | **Status**: [x] completed
**Test**: Given valid report data → When POST /api/v1/reports → Then 201 with report ID; Given rate limit exceeded → When POST → Then 429

### T-003: GET /api/v1/reports — public list
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04 | **Status**: [x] completed
**Test**: Given reports exist → When GET /api/v1/reports → Then returns paginated list newest-first

### T-004: GET /api/v1/admin/reports — admin list
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02 | **Status**: [x] completed
**Test**: Given admin token → When GET with ?status=submitted → Then returns filtered reports; Given no token → Then 401

### T-005: PATCH /api/v1/admin/reports/[id] — admin update
**User Story**: US-003 | **Satisfies ACs**: AC-US3-03, AC-US3-04, AC-US3-06 | **Status**: [x] completed
**Test**: Given admin resolves as RESOLVED with note → Then status updated; Given resolution "confirmed malware" → Then BlocklistEntry auto-created

### T-006: ReportsTab UI — form + public feed
**User Story**: US-001, US-002 | **Satisfies ACs**: AC-US1-01, AC-US1-05, AC-US2-01, AC-US2-02, AC-US2-03 | **Status**: [x] completed
**Test**: Given user fills form and submits → Then success message shown and feed refreshes

### T-007: Admin reports moderation page
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04 | **Status**: [x] completed
**Test**: Given admin views reports → Then table with filters and status actions displayed

### T-008: Admin nav + auto-block integration
**User Story**: US-003 | **Satisfies ACs**: AC-US3-05, AC-US3-06 | **Status**: [x] completed
**Test**: Given admin sidebar → Then "Reports" nav item visible; Given malware resolution → Then blocklist entry created

### T-009: Full test suite verification
**User Story**: ALL | **Satisfies ACs**: ALL | **Status**: [x] completed
**Test**: Given all changes → When `npm test` runs → Then all tests pass
