---
increment: 0628-code-review-fixes-type-safety
total_tasks: 11
completed_tasks: 11
---

# Tasks: Code Review Fixes — Type Safety, NaN Guards, Logic Gaps

## Phase 1: Platform Security Fixes (US-001)

### T-001: Add tests for empty providers, invalid enums, NaN criticalCount
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03 | **Status**: [x] completed
**Test Plan**:
- Given API returns empty providers array, When checkPlatformSecurity is called, Then overallVerdict is "PENDING"
- Given provider status is "fail" (lowercase), When parsed, Then status is normalized to "FAIL"
- Given provider status is "BOGUS" (invalid), When parsed, Then status falls back to "PENDING"
- Given criticalCount is "N/A", When parsed, Then criticalCount is 0 (not NaN)

### T-002: Implement runtime validation in platform-security.ts
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03 | **Status**: [x] completed
**Test Plan**:
- Given T-001 tests exist, When implementation is added, Then all T-001 tests pass

### T-003: Add fetch timeout
**User Story**: US-001 | **Satisfies ACs**: AC-US1-04 | **Status**: [x] completed
**Test Plan**:
- Given fetch hangs indefinitely, When 10s timeout fires, Then function returns null (caught by existing error handler)

## Phase 2: Verdict Type Fixes (US-002)

### T-004: Add test for FAIL/DEGRADING with score in [0.4, 0.7)
**User Story**: US-002 | **Satisfies ACs**: AC-US2-03 | **Status**: [x] completed
**Test Plan**:
- Given verdict is "FAIL" and score is 0.5, When verdictExplanation is called, Then recommendations array is non-empty
- Given verdict is "DEGRADING" and score is 0.6, When verdictExplanation is called, Then recommendations array is non-empty

### T-005: Widen FAIL/DEGRADING score check to < 0.7
**User Story**: US-002 | **Satisfies ACs**: AC-US2-03 | **Status**: [x] completed
**Test Plan**:
- Given T-004 tests exist, When score range widened, Then T-004 tests pass

### T-006: Tighten verdictExplanation parameter type
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01 | **Status**: [x] completed
**Test Plan**:
- Given verdictExplanation accepts EvalVerdict | "PASS" | "FAIL", When called with valid values, Then existing tests still pass
- Given tsc --noEmit, When type-checked, Then no errors

### T-007: Replace as-cast in verdictLabel with type guard
**User Story**: US-002 | **Satisfies ACs**: AC-US2-02 | **Status**: [x] completed
**Test Plan**:
- Given verdictLabel uses isEvalVerdict guard, When called with known verdicts, Then returns labels
- Given verdictLabel called with unknown string, When not in VERDICT_LABELS, Then returns input unchanged

## Phase 3: RunPanel + Test Coverage Fixes (US-003)

### T-008: Remove | string from passRateLabel and winnerLabel
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01 | **Status**: [x] completed
**Test Plan**:
- Given signatures use precise unions, When tsc --noEmit, Then no type errors

### T-009: Change MODE_BADGE to Record<RunMode, ...>
**User Story**: US-003 | **Satisfies ACs**: AC-US3-02 | **Status**: [x] completed
**Test Plan**:
- Given MODE_BADGE typed as Record<RunMode, ...>, When tsc --noEmit, Then no type errors

### T-010: Add missing test cases (negative input, boundary, EMERGING)
**User Story**: US-003 | **Satisfies ACs**: AC-US3-03, AC-US3-04, AC-US3-05 | **Status**: [x] completed
**Test Plan**:
- Given formatComparisonScore(-1, -2), When called, Then returns { skill: 0, baseline: 0 }
- Given computeVerdict(0.5, 3.0, 3.0), When called, Then returns expected medium-zone verdict
- Given verdictExplanation("EMERGING", 0.35, rubric), When called, Then explanation contains "EMERGING"

### T-011: Fix misleading test description
**User Story**: US-003 | **Satisfies ACs**: AC-US3-06 | **Status**: [x] completed
**Test Plan**:
- Given test description says ">= 0.5", When reading test, Then description matches actual boundary
