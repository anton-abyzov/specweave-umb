---
id: US-001
feature: FS-513
title: "Fix comparison mode per-case SSE rendering (P0 -- BUG)"
status: not_started
priority: P1
created: 2026-03-12
tldr: "**As a** skill developer."
project: vskill
---

# US-001: Fix comparison mode per-case SSE rendering (P0 -- BUG)

**Feature**: [FS-513](./FEATURE.md)

**As a** skill developer
**I want** per-case cards to display assertion results and pass rates during a "Compare All" run
**So that** I can see real-time progress and results for each eval case, matching the benchmark run experience

---

## Acceptance Criteria

- [ ] **AC-US1-01**: Given a comparison run is in progress, when the server processes assertions for a case, then it emits an `assertion_result` SSE event per assertion with fields `eval_id`, `assertion_id`, `text`, `pass`, and `reasoning` (same shape as benchmark-runner.ts line 84-90)
- [ ] **AC-US1-02**: Given a comparison run finishes all assertions for a case, when the case is complete, then the server emits a `case_complete` SSE event with fields `eval_id`, `status`, `pass_rate`, `durationMs`, and `tokens`
- [ ] **AC-US1-03**: Given a comparison run is in progress, when the server emits `outputs_ready`, then the client's `handleSSEEvent` captures `skillOutput` from the event data and stores it as the case's `output` in the inline result accumulator
- [ ] **AC-US1-04**: Given the server emits both legacy comparison events (`outputs_ready`, `comparison_scored`) and the new benchmark-style events (`assertion_result`, `case_complete`), then both event types are emitted per case (additive, not replacing)
- [ ] **AC-US1-05**: Given a "Compare All" run completes all cases, when the per-case cards render, then each card displays its assertion list with pass/fail status and a numeric pass rate percentage identical to what benchmark runs show

---

## Implementation

**Increment**: [0513-skill-studio-eval-history-redesign](../../../../../increments/0513-skill-studio-eval-history-redesign/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [ ] **T-001**: Add `assertion_result` and `case_complete` SSE emissions to comparison endpoint
- [ ] **T-002**: Add `outputs_ready` handler to `handleSSEEvent` in WorkspaceContext
- [ ] **T-003**: Integration test -- per-case cards render assertions during Compare All
