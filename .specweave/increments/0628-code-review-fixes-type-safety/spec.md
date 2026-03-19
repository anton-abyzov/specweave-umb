---
increment: 0628-code-review-fixes-type-safety
title: "Fix code review findings: type safety, NaN guards, logic gaps"
type: bug
priority: P1
status: active
created: 2026-03-19T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 95
---

# Bug Fix: Code Review Findings — Type Safety, NaN Guards, Logic Gaps

## Overview

A parallel 4-reviewer code review of vskill HEAD~4..HEAD found 18 issues (1 CRITICAL, 4 HIGH, 5 MEDIUM, 6 LOW, 2 INFO). This increment resolves the 5 mustFix findings and all actionable MEDIUM/LOW findings across platform-security.ts, verdict.ts, and RunPanel.tsx.

## User Stories

### US-001: Platform Security Runtime Validation (P1)
**Project**: vskill

**As a** skill consumer running `vskill add`
**I want** the platform security check to validate API responses at runtime
**So that** malformed or empty scan data cannot silently produce an all-clear verdict

**Acceptance Criteria**:
- [x] **AC-US1-01**: Empty providers array returns result with `overallVerdict: "PENDING"` instead of silently computing `hasCritical: false`
- [x] **AC-US1-02**: Status, verdict, and overallVerdict fields are validated against their union types with uppercase normalization; invalid values fall back to `"PENDING"`
- [x] **AC-US1-03**: Non-numeric `criticalCount` values (e.g. `"N/A"`, `undefined`) are guarded against NaN and default to 0
- [x] **AC-US1-04**: Fetch call includes `AbortSignal.timeout(10_000)` to prevent indefinite hangs

---

### US-002: Verdict Function Type Narrowing (P1)
**Project**: vskill

**As a** developer using verdict.ts utilities
**I want** function signatures to use precise union types instead of `string`
**So that** TypeScript catches invalid verdict values at compile time

**Acceptance Criteria**:
- [x] **AC-US2-01**: `verdictExplanation` parameter type is `EvalVerdict | "PASS" | "FAIL"` instead of `string`
- [x] **AC-US2-02**: `verdictLabel` replaces the `as EvalVerdict` cast with a type guard (`v in VERDICT_LABELS`)
- [x] **AC-US2-03**: FAIL/DEGRADING branch in `verdictExplanation` fires for scores in [0.4, 0.7) with recommendations (not just < 0.4)

---

### US-003: RunPanel Type Precision and Test Coverage (P2)
**Project**: vskill

**As a** frontend developer working on eval-ui
**I want** union types to use precise literals without `| string` absorption
**So that** TypeScript exhaustiveness checking works correctly

**Acceptance Criteria**:
- [x] **AC-US3-01**: `passRateLabel` and `winnerLabel` signatures use precise literal unions without `| string`
- [x] **AC-US3-02**: `MODE_BADGE` uses `Record<RunMode, ...>` instead of `Record<string, ...>`
- [x] **AC-US3-03**: `formatComparisonScore` has a test for negative inputs clamped to 0
- [x] **AC-US3-04**: `computeVerdict` has a test for `passRate=0.5` boundary (MARGINAL zone)
- [x] **AC-US3-05**: `verdictExplanation` test suite covers EMERGING verdict
- [x] **AC-US3-06**: Test description for MARGINAL correctly says ">= 0.5" not ">= 0.6"

## Out of Scope

- HTTP error type differentiation (MEDIUM finding, not blocking)
- APPROX_COST_PER_CALL Record<string> narrowing (LOW, cosmetic)
- Unauthenticated fetch (LOW, by design — public API)
