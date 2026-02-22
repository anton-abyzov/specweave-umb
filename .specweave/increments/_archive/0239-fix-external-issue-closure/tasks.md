# Tasks: 0239-fix-external-issue-closure

### T-001: Fix wrong method call in autoCloseExternalIssues
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02 | **Status**: [x] completed
**Test**: Given an increment transitions to COMPLETED → When autoCloseExternalIssues runs → Then it calls syncIncrementClosure() and logs closedIssues count

### T-002: Make completion sync blocking
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02 | **Status**: [x] completed
**Test**: Given spawnAsyncSync is called with COMPLETED status → When the sync runs → Then it executes synchronously without setTimeout

### T-003: Update DONE skill Step 9C
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02 | **Status**: [x] completed
**Test**: Given done skill reaches Step 9 → When closure sync runs → Then all per-US issues are targeted and results reported

### T-004: Close orphaned GitHub issues
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-04, AC-US4-05 | **Status**: [x] completed
**Test**: Given orphaned issues exist → When closure script runs → Then all issues for completed increments are closed

### T-005: Run tests and verify
**User Story**: US-001, US-002 | **Satisfies ACs**: AC-US1-01, AC-US2-01 | **Status**: [x] completed
**Test**: Given code changes applied → When test suite runs → Then all existing tests pass
