---
increment: 0633-validation-hardening
total_tasks: 9
completed_tasks: 9
---

# Tasks: Validation Hardening

### T-001: Tests for safeNumber/validateEnum warnings
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02 | **Status**: [x] completed
**Test Plan**:
- Given a non-numeric `criticalCount` ("N/A"), when `checkPlatformSecurity` processes it, then `console.warn` is called with `[platform-security]` prefix and the original value
- Given an invalid enum value ("garbage"), when `validateEnum` processes it, then `console.warn` is called with the invalid value and fallback

---

### T-002: Add console.warn to safeNumber + validateEnum
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02 | **Status**: [x] completed
**Test Plan**:
- Given the implementation from T-001 tests, when tests are run, then all warning assertions pass

---

### T-003: ReadonlySet on validation constants
**User Story**: US-001 | **Satisfies ACs**: AC-US1-03 | **Status**: [x] completed
**Test Plan**:
- Given `VALID_STATUSES`, `VALID_VERDICTS`, `VALID_OVERALL` are `ReadonlySet<T>`, when `validateEnum` is called, then it accepts `ReadonlySet<T>` and type-checks pass (`npx tsc --noEmit`)

---

### T-004: Fix fixture default verdict
**User Story**: US-001 | **Satisfies ACs**: AC-US1-04 | **Status**: [x] completed
**Test Plan**:
- Given `makePlatformResponse` defaults to `verdict: "PASS"`, when tests run, then all existing tests still pass

---

### T-005: Tests for MARGINAL/EMERGING/INEFFECTIVE recommendations
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01 | **Status**: [x] completed
**Test Plan**:
- Given verdict "MARGINAL" with score 0.65 and rubric with weak criteria, when `verdictExplanation` is called, then result has `recommendations` array
- Given verdict "EMERGING" with score 0.35 and rubric with failed+weak criteria, when `verdictExplanation` is called, then result has `recommendations` array
- Given verdict "INEFFECTIVE" with score 0.45 and rubric, when `verdictExplanation` is called, then result has `recommendations` array

---

### T-006: Add recommendation branches for MARGINAL/EMERGING/INEFFECTIVE
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01 | **Status**: [x] completed
**Test Plan**:
- Given the tests from T-005, when tests are run, then all recommendation assertions pass

---

### T-007: NaN input tests for computeVerdict
**User Story**: US-002 | **Satisfies ACs**: AC-US2-02 | **Status**: [x] completed
**Test Plan**:
- Given `computeVerdict(NaN, 3.0, 2.0)`, when called, then returns "DEGRADING"
- Given `computeVerdict(0.8, NaN, NaN)`, when called, then returns "MARGINAL"

---

### T-008: APPROX_COST_PER_CALL typing
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01 | **Status**: [x] completed
**Test Plan**:
- Given `APPROX_COST_PER_CALL` typed as `Partial<Record<string, number>>`, when `npx tsc --noEmit` runs, then no type errors

---

### T-009: NaN guard + test for formatComparisonScore
**User Story**: US-003 | **Satisfies ACs**: AC-US3-02 | **Status**: [x] completed
**Test Plan**:
- Given `formatComparisonScore(NaN, 3)`, when called, then returns `{ skill: 0, baseline: 60 }`
