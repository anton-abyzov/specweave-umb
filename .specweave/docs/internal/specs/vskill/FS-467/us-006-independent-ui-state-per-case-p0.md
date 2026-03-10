---
id: US-006
feature: FS-467
title: Independent UI State Per Case (P0)
status: not_started
priority: P1
created: 2026-03-10
tldr: "**As a** skill developer."
project: vskill
external:
  github:
    issue: 58
    url: https://github.com/anton-abyzov/vskill/issues/58
---

# US-006: Independent UI State Per Case (P0)

**Feature**: [FS-467](./FEATURE.md)

**As a** skill developer
**I want** each test case to have its own run state independent of all other cases
**So that** I can see real-time progress on multiple cases simultaneously without UI blocking

---

## Acceptance Criteria

- [ ] **AC-US6-01**: Given the workspace state, then `isRunning: boolean` is replaced by a `caseRunStates: Map<number, CaseRunState>` where CaseRunState is one of: idle, queued, running, complete, error, cancelled
- [ ] **AC-US6-02**: Given a `useMultiSSE` hook, then it manages a `Map<number, { controller: AbortController, events: SSEEvent[] }>` supporting concurrent independent streams
- [ ] **AC-US6-03**: Given case A is running and case B is complete, then case B's Run button is enabled, case B's results are fully visible, and the UI is not blocked in any way
- [ ] **AC-US6-04**: Given new reducer actions CASE_RUN_START, CASE_RUN_COMPLETE, CASE_RUN_ERROR, and CASE_RUN_CANCEL, then each action updates only the targeted case's state in the caseRunStates map
- [ ] **AC-US6-05**: Given the workspace context, then `runCase(evalId)`, `runAll()`, `cancelCase(evalId)`, and `cancelAll()` replace the current `runBenchmark(mode, scope)` and `cancelRun()` functions

---

## Implementation

**Increment**: [0467-parallel-per-case-benchmark](../../../../../increments/0467-parallel-per-case-benchmark/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-012**: Replace `isRunning` with `caseRunStates` map in workspace types and initial state
- [x] **T-013**: Update WorkspaceContext API — replace `runBenchmark`/`cancelRun` with per-case functions
- [x] **T-014**: Update RunPanel and TestsPanel to use per-case state; add per-case Run/Cancel controls
