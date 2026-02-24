# Tasks — 0369: Fix Duplicate Processing False Rejections

## Phase 1: Prevention

### T-001: Add state guard to updateState()
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03 | **Status**: [x] completed
**Test**: Given a submission in PUBLISHED state → When updateState(id, "REJECTED") is called without force → Then state remains PUBLISHED and warning is logged

### T-002: Add idempotency check to processSubmission()
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02 | **Status**: [x] completed
**Test**: Given a submission in PUBLISHED state → When processSubmission() is called → Then it returns immediately without scanning

## Phase 2: Remediation

### T-003: Create bulk restore admin endpoint
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03 | **Status**: [x] completed
**Test**: Given rejected submissions with PUBLISHED in history → When POST /restore-published → Then state restored to PUBLISHED with audit trail

## Phase 3: Tests & Verification

### T-004: Write unit tests
**User Story**: US-001, US-002 | **Status**: [x] completed
**Test**: Tests cover updateState guard, processSubmission idempotency, restore endpoint

### T-005: Build and full test suite
**User Story**: US-001, US-002, US-003 | **Status**: [x] completed
**Test**: npm run build succeeds, all tests pass
