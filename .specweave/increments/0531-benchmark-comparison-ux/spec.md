---
increment: 0531-benchmark-comparison-ux
title: Benchmark Comparison UX Improvements
type: feature
priority: P1
status: completed
created: 2026-03-15T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Benchmark Comparison UX Improvements

## Problem Statement

The VSCSKILL Studio benchmark comparison workflow has four UX issues that confuse users and reduce actionability: (1) no running summary during execution, (2) no per-case fix action, (3) contradictory verdict labels when baseline is zero, and (4) unclear button group semantics. These issues slow down the skill-tuning feedback loop.

## Goals

- Show progressive running totals during comparison so users can monitor quality without waiting for full completion
- Enable per-case AI fix actions so users can address individual failures immediately
- Eliminate contradictory verdict labels by introducing an EMERGING tier and restricting DEGRADING to actual regressions
- Clarify benchmark action buttons with tooltips and visual hierarchy

## User Stories

### US-001: Progressive Skill vs Baseline Summary (P1)
**Project**: vskill

**As a** skill developer running a benchmark comparison
**I want** a running summary of skill avg, baseline avg, delta, and preview verdict that updates as each case completes
**So that** I can monitor quality trends during execution without waiting for the full run to finish

**Acceptance Criteria**:
- [x] **AC-US1-01**: Given a comparison is running and 0 cases have completed, when the ComparisonPage renders, then a "Comparing..." placeholder is shown with a progress bar displaying "0/N cases"
- [x] **AC-US1-02**: Given K of N cases have completed via SSE events, when a new case-complete event arrives, then the summary bar updates to show the current skill avg, baseline avg, and rubric delta computed client-side from accumulated results
- [x] **AC-US1-03**: Given K of N cases have completed, when the summary bar renders, then a preview verdict label is displayed using the same tier logic as the final verdict (EFFECTIVE / MARGINAL / INEFFECTIVE / EMERGING / DEGRADING)
- [x] **AC-US1-04**: Given all N cases have completed (done SSE event), when the summary bar renders, then it matches the final verdict bar exactly with no visual jump or flicker

---

### US-002: Per-Case Fix with AI Button (P1)
**Project**: vskill

**As a** skill developer reviewing comparison results
**I want** a "Fix" button on each comparison card that has failing assertions
**So that** I can navigate directly to the improve page scoped to that case instead of using only the global fix action

**Acceptance Criteria**:
- [x] **AC-US2-01**: Given a comparison card where the case has completed with at least one failing assertion, when the card renders, then a "Fix" button is visible inline in the bottom area of the card near the assertions
- [x] **AC-US2-02**: Given a comparison card where the case has completed with zero failing assertions, when the card renders, then no "Fix" button is shown
- [x] **AC-US2-03**: Given a comparison card where the case has zero total assertions, when the card renders, then no "Fix" button is shown
- [x] **AC-US2-04**: Given the user clicks a per-case "Fix" button, when navigation occurs, then the browser navigates to the workspace improve page with `eval_id` query parameter scoped to that case
- [x] **AC-US2-05**: Given the user clicks a per-case "Fix" button, when the improve page loads, then the failing assertion context from that case is included in the navigation state

---

### US-003: Fix Contradictory Verdict Labels (P1)
**Project**: vskill

**As a** skill developer reviewing benchmark verdicts
**I want** the verdict tier to correctly distinguish between "skill outperforms a weak baseline" and "skill is actually degrading"
**So that** I am not confused by a positive delta paired with a DEGRADING label

**Acceptance Criteria**:
- [x] **AC-US3-01**: Given baseline=0% and skill=33% (passRate < 0.4 AND skillAvg > baselineAvg), when the verdict is computed, then the tier is EMERGING
- [x] **AC-US3-02**: Given baseline=50% and skill=30% (passRate < 0.4 AND skillAvg <= baselineAvg), when the verdict is computed, then the tier is DEGRADING
- [x] **AC-US3-03**: Given passRate >= 0.4, when the verdict is computed, then the existing tier logic applies unchanged (INEFFECTIVE at >= 0.4, MARGINAL at >= 0.6, EFFECTIVE at >= 0.8 with skillAvg > baselineAvg + 1)
- [x] **AC-US3-04**: Given any verdict display, when the delta label renders, then it reads "Rubric Delta" instead of "Delta"

---

### US-004: Clearer Button Group UX (P2)
**Project**: vskill

**As a** skill developer on the BenchmarkPage
**I want** the Run All, Run Baseline, and Run A/B buttons to have tooltips, visual hierarchy, and explanatory text
**So that** I understand what each mode does before clicking

**Acceptance Criteria**:
- [x] **AC-US4-01**: Given the BenchmarkPage renders, when the user hovers over "Run All", then a tooltip appears explaining that it runs skill evaluation on all cases
- [x] **AC-US4-02**: Given the BenchmarkPage renders, when the user hovers over "Run Baseline", then a tooltip appears explaining that it runs baseline-only evaluation for reference scores
- [x] **AC-US4-03**: Given the BenchmarkPage renders, when the user hovers over "Run A/B", then a tooltip appears explaining that it runs skill vs baseline comparison on all cases
- [x] **AC-US4-04**: Given the BenchmarkPage renders, when the button group is visible, then "Run All" has primary filled styling, "Run Baseline" has secondary outline styling, and "Run A/B" has accent purple styling
- [x] **AC-US4-05**: Given the BenchmarkPage renders, when the button group area is visible, then info text is displayed below the buttons explaining when to use A/B comparison

## Out of Scope

- Server-side changes to SSE event format or new event types
- Redesign of the global ActionItemsPanel (only adding per-case complement)
- Changes to the improve page itself (only navigation to it)
- New verdict tiers beyond EMERGING (keeping 5-tier structure)
- Mobile/responsive layout changes

## Non-Functional Requirements

- **Performance**: Client-side progressive summary computation must not cause visible frame drops with up to 200 cases
- **Compatibility**: Works in Chrome, Firefox, Safari (latest 2 versions)

## Edge Cases

- All cases pass with 100% on both sides: verdict is EFFECTIVE, no Fix buttons appear
- Baseline is never run (no baseline data): progressive summary shows skill-only scores, verdict falls back to pass-rate-only tiers
- SSE connection drops mid-run: summary freezes at last received state, no crash
- Single case in benchmark: progressive summary shows 0/1 then 1/1 with no intermediate flicker

## Risks

| Risk | Probability | Impact | Severity | Mitigation |
|------|-------------|--------|----------|------------|
| Progressive summary flickers on rapid SSE events | 0.3 | 3 | 0.9 | Debounce or batch state updates |
| EMERGING tier confuses users unfamiliar with new label | 0.2 | 2 | 0.4 | Add tooltip explaining what EMERGING means |

## Technical Notes

- Key files: `src/eval/verdict.ts` (verdict logic), `src/eval-ui/src/pages/ComparisonPage.tsx`, `src/eval-ui/src/pages/BenchmarkPage.tsx`, `src/eval-ui/src/components/ActionItemsPanel.tsx`
- Backend already supports `eval_id` filtering for the improve page navigation
- SSE events include per-case results; no server changes needed for progressive summary
- Rename "Delta" label to "Rubric Delta" in both progressive and final verdict displays

## Success Metrics

- Users can see running verdict within 2 seconds of first case completing (no waiting for full run)
- Per-case Fix button reduces average time-to-fix by allowing direct navigation instead of global action only
- Zero instances of contradictory "positive delta + DEGRADING" verdict after deployment
