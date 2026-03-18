---
increment: 0578-fix-eval-comparison-metrics
title: Fix eval comparison metrics and improve generation prompts
type: bug
priority: P1
status: completed
created: 2026-03-18T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Fix Eval Comparison Metrics and Improve Generation Prompts

## Problem Statement

The eval comparison system has 4 interconnected bugs that make comparison results unreliable. `baselinePassRate` is hardcoded to 0 (assertions are never judged against baseline output), the delta metric uses rubric scores on a 1-5 scale instead of pass rates (producing nonsensical "-50.0%" displays), the verdict function has a catch-all `>= 0.4` branch that labels even 100% pass rates as INEFFECTIVE, and the overall pass rate only reflects skill assertions without baseline context. Additionally, LLM-generated eval assertions are often too rigid — testing formatting minutiae (blank lines, paragraph count) instead of functional correctness.

## Goals

- Compute real baseline assertion pass rates by judging assertions against baseline output
- Fix delta to use assertion pass rates (0-1 scale) instead of rubric averages (1-5 scale)
- Redesign verdict logic to factor in baseline comparison, not just absolute skill pass rate
- Clearly separate skill vs baseline pass rates in the comparison result
- Improve generation prompts to produce functional, non-brittle assertions

## User Stories

### US-001: Compute Real Baseline Assertion Pass Rate (P0)
**Project**: vskill
**As a** skill developer
**I want** eval assertions judged against both skill AND baseline outputs
**So that** I can see how the baseline model performs on the same assertions and understand the skill's actual improvement

**Acceptance Criteria**:
- [x] **AC-US1-01**: Given a comparison eval run, when assertions are evaluated, then each assertion is judged against both `comparison.skillOutput` and `comparison.baselineOutput` independently
- [x] **AC-US1-02**: Given assertion judging completes, when `baselinePassRate` is computed, then it equals the number of baseline-passing assertions divided by total assertions (not hardcoded to 0)
- [x] **AC-US1-03**: Given a comparison with 3 assertions where baseline passes 2, when the history result is built, then `comparison.baselinePassRate` equals approximately 0.667
- [x] **AC-US1-04**: Given baseline assertion judging, when results are streamed via SSE, then baseline assertion results are included in the event stream so the UI can display per-assertion baseline status

---

### US-002: Fix Delta Calculation to Use Pass Rates (P0)
**Project**: vskill
**As a** skill developer
**I want** the delta metric to show the difference in assertion pass rates
**So that** the displayed percentage reflects actual skill improvement over baseline, not a rubric-scale difference

**Acceptance Criteria**:
- [x] **AC-US2-01**: Given skill pass rate is 0.8 and baseline pass rate is 0.6, when delta is computed, then `delta` equals 0.2 (not `skillRubricAvg - baselineRubricAvg`)
- [x] **AC-US2-02**: Given delta is 0.2, when the UI renders `delta * 100`, then it displays "+20.0%" (a meaningful percentage improvement)
- [x] **AC-US2-03**: Given both skill and baseline pass all assertions (pass rates both 1.0), when delta is computed, then delta equals 0.0 and the UI shows "0.0%"

---

### US-003: Redesign Verdict Logic for Baseline Comparison (P1)
**Project**: vskill
**As a** skill developer
**I want** the verdict to consider how the skill performs relative to baseline
**So that** a skill with 100% pass rate is never labeled INEFFECTIVE just because it exceeds the 0.4 catch-all threshold

**Acceptance Criteria**:
- [x] **AC-US3-01**: Given `assertionPassRate` is 1.0 and `baselinePassRate` is 0.5, when verdict is computed, then it returns "EFFECTIVE" (not "INEFFECTIVE")
- [x] **AC-US3-02**: Given `assertionPassRate` is 0.8 and `baselinePassRate` is 0.8, when verdict is computed, then it returns "MARGINAL" or lower (skill shows no improvement over baseline)
- [x] **AC-US3-03**: Given `assertionPassRate` is 0.3 and `baselinePassRate` is 0.7, when verdict is computed, then it returns "DEGRADING" (skill is worse than baseline)
- [x] **AC-US3-04**: Given the `computeVerdict` function signature, when it is updated, then it accepts `baselinePassRate` as a parameter and uses it in its decision logic
- [x] **AC-US3-05**: Given any `assertionPassRate` between 0.0 and 1.0, when verdict is computed, then no catch-all branch can produce "INEFFECTIVE" for pass rates above 0.8

---

### US-004: Separate Skill and Baseline Pass Rates in Results (P2)
**Project**: vskill
**As a** skill developer
**I want** the comparison result to clearly distinguish skill pass rate from baseline pass rate
**So that** the "overall pass rate" is not misleading in comparison context

**Acceptance Criteria**:
- [x] **AC-US4-01**: Given a comparison eval result, when `overall_pass_rate` is set, then it reflects the skill assertion pass rate and the field name or context makes this clear
- [x] **AC-US4-02**: Given a comparison eval result, when the history entry is written, then `comparison.skillPassRate` and `comparison.baselinePassRate` are both present as separate numeric fields

---

### US-005: Improve Generation Prompts for Functional Assertions (P1)
**Project**: vskill
**As a** skill developer
**I want** auto-generated eval assertions to focus on functional correctness
**So that** assertions don't fail on trivial formatting differences like blank lines, paragraph count, or whitespace

**Acceptance Criteria**:
- [x] **AC-US5-01**: Given the `EVAL_SYSTEM_PROMPT` in `skill-create-routes.ts`, when it is updated, then it includes instructions to focus assertions on functional correctness rather than formatting minutiae
- [x] **AC-US5-02**: Given the `BEST_PRACTICES` in `prompt-builder.ts`, when it is updated, then it includes guidance to prefer unit-test-style assertions (one behavior per assertion)
- [x] **AC-US5-03**: Given the updated prompts, when they instruct assertion design, then they explicitly warn against being rigid about blank lines, paragraph count, whitespace, or exact formatting

## Out of Scope

- Changing the rubric scoring system itself (content/structure scores)
- Adding new verdict tiers beyond the existing 5 (EFFECTIVE, MARGINAL, INEFFECTIVE, EMERGING, DEGRADING)
- Modifying the skill generation prompt (SKILL_SYSTEM_PROMPT) — only eval-related prompts
- UI redesign of the RunPanel comparison section beyond the delta fix
- Changing how `runComparison` generates skill/baseline outputs

## Technical Notes

### Dependencies
- `src/eval-server/api-routes.ts` — comparison endpoint (bugs 1, 2, 4)
- `src/eval/verdict.ts` — verdict computation (bug 3)
- `src/eval-ui/src/pages/workspace/RunPanel.tsx` — delta display (bug 2 UI side)
- `src/eval-server/skill-create-routes.ts` — EVAL_SYSTEM_PROMPT (prompt improvement)
- `src/eval/prompt-builder.ts` — BEST_PRACTICES (prompt improvement)
- `judgeAssertion` function — reused for baseline assertion judging

### Constraints
- Baseline assertion judging adds a second LLM call per assertion per eval case — latency will increase
- The `computeVerdict` function signature changes — all callers must be updated
- History entries must remain backwards-compatible (old entries have `baselinePassRate: 0`)

### Architecture Decisions
- Reuse existing `judgeAssertion` for baseline judging — no new judge function needed
- Store baseline assertion results alongside skill assertion results in the comparison data
- Verdict redesign should use `baselinePassRate` as the comparison anchor, not absolute thresholds alone

## Non-Functional Requirements

- **Performance**: Baseline assertion judging doubles judge LLM calls; accept this latency increase as comparisons are not latency-critical
- **Compatibility**: Old history entries with `baselinePassRate: 0` must still render correctly in the UI
- **Accuracy**: Delta displayed in UI must be mathematically correct (pass rate difference, not rubric difference)

## Edge Cases

- **Zero assertions**: If an eval case has 0 assertions, both skill and baseline pass rates should be 0
- **All-pass baseline**: If baseline passes all assertions (1.0), skill must exceed it to be EFFECTIVE
- **Equal pass rates**: If skill and baseline have identical pass rates, verdict should reflect no improvement
- **No baseline output**: If `comparison.baselineOutput` is empty/null, baseline pass rate defaults to 0

## Risks

| Risk | Probability | Impact | Severity | Mitigation |
|------|-------------|--------|----------|------------|
| Doubled LLM calls slow comparisons noticeably | 0.4 | 3 | 1.2 | Comparisons are already slow; users expect this |
| Verdict changes break existing workflows | 0.3 | 4 | 1.2 | Old history entries remain unchanged; new verdicts only affect new runs |
| Prompt changes degrade assertion quality | 0.2 | 5 | 1.0 | Changes are additive guidance, not removing existing instructions |

## Success Metrics

- `baselinePassRate` is non-zero for comparisons where baseline passes any assertions
- Delta percentage in UI matches `(skillPassRate - baselinePassRate) * 100`
- No skill with 80%+ assertion pass rate receives INEFFECTIVE verdict
- Generated assertions contain zero formatting-only checks (blank lines, paragraph count)
