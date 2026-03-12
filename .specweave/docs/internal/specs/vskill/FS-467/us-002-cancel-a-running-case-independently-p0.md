---
id: US-002
feature: FS-467
title: "Cancel a Running Case Independently (P0)"
status: completed
priority: P1
created: 2026-03-10
tldr: "**As a** skill developer."
project: vskill
external:
  github:
    issue: 54
    url: "https://github.com/anton-abyzov/vskill/issues/54"
---

# US-002: Cancel a Running Case Independently (P0)

**Feature**: [FS-467](./FEATURE.md)

**As a** skill developer
**I want** to cancel a specific running test case without stopping other in-flight cases
**So that** I can abort a stuck or unwanted run while preserving results from other cases

---

## Acceptance Criteria

- [x] **AC-US2-01**: Given a case in "running" state, when I click its Cancel button, then that case's AbortController is aborted, the SSE stream for that case closes, and the case transitions to "cancelled" state
- [x] **AC-US2-02**: Given cases A (running) and B (running), when I cancel case A, then case B continues running uninterrupted and eventually completes normally
- [x] **AC-US2-03**: Given a case in "cancelled" state, when its Run button is clicked again, then it transitions back to "running" and starts a fresh SSE stream
- [x] **AC-US2-04**: Given a case in any non-running state (idle, complete, error, cancelled), then the Cancel button is either hidden or disabled for that case

---

## Implementation

**Increment**: [0467-parallel-per-case-benchmark](../../../../../increments/0467-parallel-per-case-benchmark/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-004**: Implement `useMultiSSE` hook with per-case AbortController management
- [x] **T-005**: Wire cancel controls in reducer and context; hide Cancel button for non-running cases
