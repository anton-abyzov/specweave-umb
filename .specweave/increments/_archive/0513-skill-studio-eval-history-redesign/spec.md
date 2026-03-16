---
increment: 0513-skill-studio-eval-history-redesign
title: 'Skill Studio: eval history redesign + comparison fix'
type: feature
priority: P1
status: completed
created: 2026-03-12T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Skill Studio: Eval History Redesign + Comparison Fix

## Problem Statement

The comparison mode ("Compare All") in Skill Studio's eval system is broken at the per-case level. The comparison endpoint (`/api/skills/:plugin/:skill/compare`) emits `outputs_ready` and `comparison_scored` SSE events, but the client's `handleSSEEvent` only handles `output_ready` (singular), `assertion_result`, and `case_complete` -- events that the comparison endpoint never sends. As a result, per-case cards render empty during comparison runs (no assertions, no pass rate).

Beyond the bug, the eval history UI needs improvement: the flat list of history entries per case mixes all run types with no visual distinction between skill runs and baseline runs, and the MiniTrend sparkline conflates all run types into a single line, making it impossible to see how the skill and baseline trends diverge over time.

## Goals

- Fix comparison mode so per-case cards display assertions and pass rates in real time during "Compare All" runs
- Provide clear visual separation between skill (benchmark) and baseline run history using a split-lane two-column timeline
- Enable at-a-glance trend comparison between skill and baseline performance via a dual-line sparkline

## User Stories

### US-001: Fix comparison mode per-case SSE rendering (P0 -- BUG)
**Project**: vskill
**As a** skill developer
**I want** per-case cards to display assertion results and pass rates during a "Compare All" run
**So that** I can see real-time progress and results for each eval case, matching the benchmark run experience

**Acceptance Criteria**:
- [x] **AC-US1-01**: Given a comparison run is in progress, when the server processes assertions for a case, then it emits an `assertion_result` SSE event per assertion with fields `eval_id`, `assertion_id`, `text`, `pass`, and `reasoning` (same shape as benchmark-runner.ts line 84-90)
- [x] **AC-US1-02**: Given a comparison run finishes all assertions for a case, when the case is complete, then the server emits a `case_complete` SSE event with fields `eval_id`, `status`, `pass_rate`, `durationMs`, and `tokens`
- [x] **AC-US1-03**: Given a comparison run is in progress, when the server emits `outputs_ready`, then the client's `handleSSEEvent` captures `skillOutput` from the event data and stores it as the case's `output` in the inline result accumulator
- [x] **AC-US1-04**: Given the server emits both legacy comparison events (`outputs_ready`, `comparison_scored`) and the new benchmark-style events (`assertion_result`, `case_complete`), then both event types are emitted per case (additive, not replacing)
- [x] **AC-US1-05**: Given a "Compare All" run completes all cases, when the per-case cards render, then each card displays its assertion list with pass/fail status and a numeric pass rate percentage identical to what benchmark runs show

---

### US-002: Split-lane timeline for per-case eval history (P1)
**Project**: vskill
**As a** skill developer
**I want** the per-case execution history to use a two-column "Skill | Baseline" layout
**So that** I can visually distinguish benchmark runs from baseline runs and see how they compare over time

**Acceptance Criteria**:
- [x] **AC-US2-01**: Given the CaseHistorySection renders, then it displays a two-column layout with "Skill" label on the left column and "Baseline" label on the right column
- [x] **AC-US2-02**: Given history entries exist, when an entry has type `benchmark`, then it renders in the left (Skill) column only
- [x] **AC-US2-03**: Given history entries exist, when an entry has type `baseline`, then it renders in the right (Baseline) column only
- [x] **AC-US2-04**: Given history entries exist, when an entry has type `comparison`, then it renders as a single merged card spanning both columns with the delta and verdict badge centered between the two sides
- [x] **AC-US2-05**: Given only benchmark entries exist and no baseline entries, then the left column is populated with entries and the right column displays "No baseline runs" in `var(--text-tertiary)` color at font-size 12px

---

### US-003: Dual-line MiniTrend sparkline (P1)
**Project**: vskill
**As a** skill developer
**I want** the MiniTrend sparkline to show two separate polylines -- one for skill runs and one for baseline runs
**So that** I can see at a glance whether the skill is trending up relative to the baseline

**Acceptance Criteria**:
- [x] **AC-US3-01**: Given the `CaseHistoryEntry` type, then it includes an optional `baselinePassRate` field of type `number | undefined`
- [x] **AC-US3-02**: Given the `getCaseHistory` function reads a comparison-type history entry, then it populates `baselinePassRate` by deriving it from the existing `comparisonDetail` rubric scores (average of `baselineContentScore` and `baselineStructureScore`, normalized to 0-1 range)
- [x] **AC-US3-03**: Given the MiniTrend component receives entries, then it renders two SVG polylines: a blue line (`var(--accent)`) for skill pass rates and a gray line (`var(--text-tertiary)`) for baseline pass rates
- [x] **AC-US3-04**: Given a `benchmark`-type entry, then it contributes a point to the skill (blue) line only and does not contribute to the baseline (gray) line
- [x] **AC-US3-05**: Given a `baseline`-type entry, then it contributes a point to the baseline (gray) line only and does not contribute to the skill (blue) line
- [x] **AC-US3-06**: Given a `comparison`-type entry, then it contributes `pass_rate` to the skill (blue) line and `baselinePassRate` to the baseline (gray) line
- [x] **AC-US3-07**: Given entries of types `improve`, `instruct`, `model-compare`, `ai-generate`, or `eval-generate`, then they are excluded from both sparkline polylines entirely

## Out of Scope

- Judging assertions against baseline output separately (too expensive; rubric scores suffice)
- Redesigning the overall benchmark summary view or the top-level history list
- Adding filtering/sorting controls to the split-lane timeline
- Sparkline interactivity (tooltips, click-to-navigate)
- Persisting user preference for timeline column collapse

## Technical Notes

### Dependencies
- Server: `src/eval-server/api-routes.ts` (comparison endpoint, lines 640-860)
- Server: `src/eval-server/benchmark-runner.ts` (reference for event shapes)
- Client SSE: `src/eval-ui/src/pages/workspace/WorkspaceContext.tsx` (handleSSEEvent)
- History UI: `src/eval-ui/src/pages/workspace/TestsPanel.tsx` (CaseHistorySection)
- Sparkline: `src/eval-ui/src/utils/historyUtils.tsx` (MiniTrend)
- Types: `src/eval-ui/src/types.ts` (CaseHistoryEntry), `src/eval/benchmark-history.ts` (CaseHistoryEntry server-side)

### Constraints
- The comparison endpoint must continue emitting `outputs_ready` and `comparison_scored` (additive approach) for any consumers that depend on them
- `baselinePassRate` derivation must not introduce additional LLM calls -- use existing rubric scores from `comparisonDetail`
- MiniTrend SVG dimensions remain 80x24px to avoid layout shifts

### Architecture Decisions
- **Additive SSE events**: The comparison endpoint gains `assertion_result` and `case_complete` emissions without removing its existing events. This avoids breaking any current consumers while allowing the shared `handleSSEEvent` to process comparison results identically to benchmark results.
- **Rubric-derived baselinePassRate**: Rather than running a second set of assertion judgments against baseline output, `baselinePassRate` is computed as the average of `baselineContentScore` and `baselineStructureScore` from `comparisonDetail`, normalized to 0-1. This keeps comparison runs cheap.
- **Client-side `outputs_ready` handler**: The client adds a handler for `outputs_ready` (plural) to capture `skillOutput` as the case output, bridging the naming gap between comparison and benchmark event formats.

## Non-Functional Requirements

- **Performance**: No additional LLM calls introduced; baselinePassRate derived from existing data
- **Accessibility**: Split-lane columns use semantic headings; sparkline polylines have distinct colors meeting WCAG contrast requirements against the dark background
- **Compatibility**: All changes within the existing React + Vite + Node.js stack; no new dependencies

## Edge Cases

- **No history entries at all**: CaseHistorySection shows "No history for this case" (existing behavior, unchanged)
- **Only benchmark entries, no baseline**: Left column populated, right column shows "No baseline runs" placeholder text
- **Only baseline entries, no benchmark**: Right column populated, left column shows "No skill runs" placeholder text
- **Comparison entry with missing comparisonDetail**: `baselinePassRate` defaults to `undefined`; gray sparkline line skips that point
- **Single entry total**: MiniTrend returns null (existing behavior: requires 2+ entries)
- **All entries filtered out by type**: If after excluding non-core types only 0-1 entries remain for either line, that polyline is not rendered
- **SSE connection drops mid-comparison**: Existing abort handling in the comparison endpoint is preserved; partially-received assertion_result events still render in the UI

## Risks

| Risk | Probability | Impact | Severity | Mitigation |
|------|-------------|--------|----------|------------|
| Additive SSE events increase payload size per comparison run | 0.2 | 2 | 0.4 | Events are small JSON; negligible bandwidth impact |
| Rubric-derived baselinePassRate diverges from "true" baseline assertion pass rate | 0.4 | 3 | 1.2 | Acceptable tradeoff -- rubric scores are the best available proxy without extra LLM calls |
| Two-column layout awkward on narrow viewports | 0.3 | 4 | 1.2 | Eval UI is a desktop tool; minimum supported width is already ~900px |

## Success Metrics

- Per-case cards during "Compare All" show assertion results and pass rates (currently show nothing)
- History entries are visually separated into Skill and Baseline lanes
- MiniTrend sparkline shows two distinct trend lines for skill vs baseline performance
