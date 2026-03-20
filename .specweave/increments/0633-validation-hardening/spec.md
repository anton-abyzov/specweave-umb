---
increment: 0633-validation-hardening
title: 'Validation Hardening: logging, recommendations, type immutability'
type: bug
priority: P2
status: completed
created: 2026-03-19T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 95
---

# Bug Fix: Validation Hardening

## Overview

Post-implementation review of increment 0628 by 4 parallel reviewers (logic, security, types, silent-failures) found 13 new findings. The `isEvalVerdict` `Object.hasOwn` fix was already applied. This increment addresses the remaining actionable HIGH/MEDIUM findings: silent data coercion without logging, missing recommendation branches, type-level immutability, and test gaps.

## User Stories

### US-001: Platform Security Coercion Logging (P1)
**Project**: vskill

**As a** operator monitoring security scan results
**I want** fallback coercions in `safeNumber` and `validateEnum` to emit warnings
**So that** silent data loss (e.g., `criticalCount: "N/A"` → 0) is visible in logs

**Acceptance Criteria**:
- [x] **AC-US1-01**: `safeNumber` emits `console.warn` with the original value and fallback when `isNaN` triggers
- [x] **AC-US1-02**: `validateEnum` emits `console.warn` with the invalid value and fallback when the uppercase value is not in the allowed set
- [x] **AC-US1-03**: `VALID_STATUSES`, `VALID_VERDICTS`, `VALID_OVERALL` are typed as `ReadonlySet<T>` and `validateEnum` accepts `ReadonlySet<T>`
- [x] **AC-US1-04**: Test fixture default `verdict: "clean"` is changed to `verdict: "PASS"` in `makePlatformResponse`

---

### US-002: Verdict Recommendation Completeness (P2)
**Project**: vskill

**As a** developer reviewing eval results
**I want** `verdictExplanation` to return recommendations for MARGINAL, EMERGING, and INEFFECTIVE (score >= 0.2)
**So that** every verdict path provides actionable guidance

**Acceptance Criteria**:
- [x] **AC-US2-01**: `verdictExplanation` returns a `recommendations` array for MARGINAL, EMERGING, and INEFFECTIVE with score in [0.2, 0.7)
- [x] **AC-US2-02**: `computeVerdict` NaN input behavior is documented via tests

---

### US-003: RunPanel Type Safety and NaN Guards (P2)
**Project**: vskill

**As a** frontend developer using eval-ui
**I want** `APPROX_COST_PER_CALL` to use `Partial<Record>` and `formatComparisonScore` to guard against NaN
**So that** type-level and runtime safety are aligned

**Acceptance Criteria**:
- [x] **AC-US3-01**: `APPROX_COST_PER_CALL` is typed as `Partial<Record<string, number>>`
- [x] **AC-US3-02**: `formatComparisonScore` returns 0 (not NaN) when given NaN input, with a test covering this case

## Out of Scope

- HTTP error type differentiation (deferred from 0628)
- `computeVerdict` NaN input validation/guard (separate concern — only documenting behavior via tests)
