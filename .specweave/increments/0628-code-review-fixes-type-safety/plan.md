# Implementation Plan: Code Review Fixes — Type Safety, NaN Guards, Logic Gaps

## Overview

Targeted fixes across 3 source files + 3 test files. No new files created. All changes are backwards-compatible refinements to existing functions.

## Approach

### platform-security.ts
- Add `validateEnum` helper for runtime union validation with Set-based membership check
- Add `safeNumber` helper for NaN-safe numeric conversion
- Guard empty providers → force overallVerdict to "PENDING"
- Add `AbortSignal.timeout(10_000)` to fetch

### verdict.ts
- Tighten `verdictExplanation` param from `string` to `EvalVerdict | "PASS" | "FAIL"`
- Add `isEvalVerdict` type guard, replace `as` cast in `verdictLabel`
- Widen FAIL/DEGRADING score check from `< 0.4` to `< 0.7`

### RunPanel.tsx
- Remove `| string` from `passRateLabel` and `winnerLabel` signatures
- Change `MODE_BADGE` to `Record<RunMode, ...>`

## Testing Strategy

TDD RED→GREEN→REFACTOR. Write failing tests first, then implement fixes.
