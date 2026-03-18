---
increment: 0578-fix-eval-comparison-metrics
generated: 2026-03-18
test_mode: TDD
---

# Tasks: Fix Eval Comparison Metrics

## US-003: Redesign Verdict Logic for Baseline Comparison

### T-001: Add `baselinePassRate` parameter to `computeVerdict`
**User Story**: US-003 | **Satisfies ACs**: AC-US3-04
**Status**: [x] completed
**Test**: Given `computeVerdict` in `verdict.ts` → When the function signature is updated → Then it accepts `(assertionPassRate, skillRubricAvg, baselineRubricAvg, baselinePassRate)` with `baselinePassRate` defaulting to `0` for backwards compatibility

---

### T-002: Redesign verdict decision tree using baseline comparison
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-05
**Status**: [x] completed
**Test**: Given the new `computeVerdict` logic → When called with `(1.0, 4.5, 2.5, 0.5)` → Then returns "EFFECTIVE"; given `(0.8, 3.5, 3.5, 0.8)` → Then returns "MARGINAL" or lower; given `(0.3, 2.0, 4.0, 0.7)` → Then returns "DEGRADING"; given any `assertionPassRate >= 0.8` → Then no code path returns "INEFFECTIVE"

---

### T-003: Update `verdict.test.ts` for new signature and baseline-aware cases
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04, AC-US3-05
**Status**: [x] completed
**Test**: Given `src/eval/__tests__/verdict.test.ts` → When all `computeVerdict` calls are updated with the 4th `baselinePassRate` argument → Then all existing tests pass; AND new test cases cover: (passRate 1.0 + baseline 0.5 → EFFECTIVE), (passRate 0.8 + baseline 0.8 → MARGINAL or lower), (passRate 0.3 + baseline 0.7 → DEGRADING), (no passRate >= 0.8 produces INEFFECTIVE)

---

## US-001: Compute Real Baseline Assertion Pass Rate

### T-004: Judge assertions against baseline output in `api-routes.ts`
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03
**Status**: [x] completed
**Test**: Given the comparison assertion loop in `api-routes.ts` → When each assertion is processed → Then `judgeAssertion` is called for both `comparison.skillOutput` AND `comparison.baselineOutput` via `Promise.all`; AND `baselineAssertionResults` is stored on each `comparisonResults` entry; AND `baselinePassRate` equals `baselinePassed / totalAssertions` (e.g. 2 of 3 passing → 0.667)

---

### T-005: Emit `baseline_assertion_result` SSE events
**User Story**: US-001 | **Satisfies ACs**: AC-US1-04
**Status**: [x] completed
**Test**: Given `api-routes.ts` processes baseline assertions → When each baseline assertion result is computed → Then a `baseline_assertion_result` SSE event is emitted alongside the existing `assertion_result` event, enabling the UI to display per-assertion baseline status

---

## US-002: Fix Delta Calculation to Use Pass Rates

### T-006: Fix delta to use pass rate difference instead of rubric average difference
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03
**Status**: [x] completed
**Test**: Given `api-routes.ts` delta computation → When skillPassRate is 0.8 and baselinePassRate is 0.6 → Then `delta` equals 0.2 (not `skillRubricAvg - baselineRubricAvg`); AND given both pass rates are 1.0 → Then delta equals 0.0; AND since `RunPanel.tsx` already renders `(delta * 100).toFixed(1)%`, "+20.0%" displays correctly with zero UI code changes

---

## US-004: Separate Skill and Baseline Pass Rates in Results

### T-007: Store `skillPassRate` and `baselinePassRate` as separate fields in history entry
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02
**Status**: [x] completed
**Test**: Given `api-routes.ts` history entry construction → When a comparison eval completes → Then the result contains both `comparison.skillPassRate` and `comparison.baselinePassRate` as separate numeric fields; AND `overall_pass_rate` reflects only the skill assertion pass rate

---

### T-008: Update `comparison-sse-events.test.ts` for baseline events and fixed delta data
**User Story**: US-001, US-002, US-004 | **Satisfies ACs**: AC-US1-04, AC-US2-01, AC-US4-02
**Status**: [x] completed
**Test**: Given `src/eval-server/__tests__/comparison-sse-events.test.ts` → When mocks are updated to include `baselineAssertionResults` on each comparison result → Then existing tests pass; AND a new test asserts `baseline_assertion_result` events are emitted; AND delta-related assertions use pass-rate values (0–1 scale)

---

## US-005: Improve Generation Prompts for Functional Assertions

### T-009: Add anti-rigidity guidance to `EVAL_SYSTEM_PROMPT` in `skill-create-routes.ts`
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01, AC-US5-03
**Status**: [x] completed
**Test**: Given `EVAL_SYSTEM_PROMPT` in `src/eval-server/skill-create-routes.ts` → When it is updated → Then it contains instructions to focus on functional correctness; AND explicitly warns against asserting on blank lines, paragraph count, whitespace, exact heading levels, or bullet formatting

---

### T-010: Add functional-assertion best practice to `BEST_PRACTICES` in `prompt-builder.ts`
**User Story**: US-005 | **Satisfies ACs**: AC-US5-02, AC-US5-03
**Status**: [x] completed
**Test**: Given `BEST_PRACTICES` in `src/eval/prompt-builder.ts` → When updated → Then it includes a best practice item for unit-test-style assertions (one behavior per assertion); AND includes examples distinguishing bad (formatting-rigid) assertions from good (semantic/functional) assertions; AND warns against rigidity on blank lines, paragraph count, whitespace, or exact formatting
