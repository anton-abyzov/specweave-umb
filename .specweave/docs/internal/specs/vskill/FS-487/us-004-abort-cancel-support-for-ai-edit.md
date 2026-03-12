---
id: US-004
feature: FS-487
title: "Abort/Cancel Support for AI Edit"
status: completed
priority: P1
created: "2026-03-11T00:00:00.000Z"
tldr: "**As a** skill developer."
project: vskill
external:
  github:
    issue: 77
    url: "https://github.com/anton-abyzov/vskill/issues/77"
---

# US-004: Abort/Cancel Support for AI Edit

**Feature**: [FS-487](./FEATURE.md)

**As a** skill developer
**I want** to cancel an in-progress AI Edit generation by pressing Escape
**So that** I don't have to wait for a slow or unwanted generation to complete

---

## Acceptance Criteria

- [x] **AC-US4-01**: Given an AI Edit generation is in progress, when the user presses Escape, then the SSE connection is aborted via AbortController and the server-side LLM process is terminated
- [x] **AC-US4-02**: Given an AI Edit generation is cancelled, then the UI returns to the instruction input with the original instruction text preserved, ready for re-submission
- [x] **AC-US4-03**: Given an AI Edit generation is in progress, then the Submit button changes to a Cancel button (or shows a cancel affordance) indicating the operation can be interrupted
- [x] **AC-US4-04**: Given the SSE connection drops unexpectedly (network error, laptop sleep), then the frontend shows a "Connection lost" error state with a Retry button, without auto-retry

---

## Implementation

**Increment**: [0487-skill-studio-execution-observability](../../../../../increments/0487-skill-studio-execution-observability/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-010**: Implement Escape key abort and server-side close detection in AI Edit
- [x] **T-011**: Handle unexpected SSE connection drops
