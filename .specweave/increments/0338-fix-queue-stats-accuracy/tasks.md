# Tasks — 0338 Fix Queue Stats Accuracy

### T-001: Rewrite stats endpoint to use Prisma DB + KV cache
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02 | **Status**: [x] completed
**Test**: Given stats cache is empty → When GET /api/v1/submissions/stats → Then queries DB, caches in KV, returns accurate counts

### T-002: Fix list endpoint total count
**User Story**: US-001 | **Satisfies ACs**: AC-US1-03 | **Status**: [x] completed
**Test**: Given KV index has 100 entries but DB has 530 → When GET /api/v1/submissions → Then total=530

### T-003: Deduplicate auth call via useAdminStatus
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01 | **Status**: [x] completed
**Test**: Given page loads → When useAdminStatus resolves → Then only 1 auth/me request fires

### T-004: Conditional polling + search debounce
**User Story**: US-002 | **Satisfies ACs**: AC-US2-02, AC-US2-03 | **Status**: [x] completed
**Test**: Given SSE connected → When 30s passes → Then no polling requests fire

### T-005: Update tests
**User Story**: US-001, US-002 | **Satisfies ACs**: all | **Status**: [x] completed
**Test**: All existing + new tests pass
