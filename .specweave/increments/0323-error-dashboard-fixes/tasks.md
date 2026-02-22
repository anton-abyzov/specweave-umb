# Tasks: 0323 Error Dashboard Fixes

### T-001: Disable spec-template-enforcement guard
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02 | **Status**: [x] completed
**Test**: Given guard hook is invoked → When writing full spec.md content → Then decision is "allow" with stderr warning

### T-002: Migrate vitest.config.ts to test.projects
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03 | **Status**: [x] completed
**Test**: Given `npx vitest run` → When tests execute → Then no "environmentMatchGlobs" deprecation warning appears

### T-003: Fix bulk-submission.test.ts mock
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01 | **Status**: [x] completed
**Test**: Given complete Prisma mock → When running bulk-submission tests → Then all 4 tests pass

### T-004: Fix discovery-enrichment.test.ts mock
**User Story**: US-003 | **Satisfies ACs**: AC-US3-02 | **Status**: [x] completed
**Test**: Given complete Prisma mock → When running discovery-enrichment tests → Then all 2 tests pass

### T-005: Fix blocklist-e2e.test.ts mock
**User Story**: US-003 | **Satisfies ACs**: AC-US3-03 | **Status**: [x] completed
**Test**: Given blocklistEntry.count mock → When running blocklist tests → Then GET returns 200 and all tests pass

### T-006: Verify full test suite passes
**User Story**: US-003 | **Satisfies ACs**: AC-US3-04 | **Status**: [x] completed
**Test**: Given all fixes applied → When `npx vitest run` → Then 0 failures, 0 deprecation warnings
