---
id: US-003
feature: FS-495
title: "Wire Dynamic Heartbeat in Compare Endpoint"
status: completed
priority: P1
created: 2026-03-11T00:00:00.000Z
tldr: "**As a** Skill Studio user."
project: vskill
---

# US-003: Wire Dynamic Heartbeat in Compare Endpoint

**Feature**: [FS-495](./FEATURE.md)

**As a** Skill Studio user
**I want** the compare endpoint to emit phase-specific progress events
**So that** I can see whether the system is generating the skill output, the baseline output, or scoring

---

## Acceptance Criteria

- [x] **AC-US3-01**: Given a comparison is running, when the skill generation starts, then the SSE stream emits a progress event with `phase: "generating_skill"` and a descriptive message
- [x] **AC-US3-02**: Given a comparison is running, when the baseline generation starts, then the SSE stream emits a progress event with `phase: "generating_baseline"`
- [x] **AC-US3-03**: Given a comparison is running, when rubric scoring starts, then the SSE stream emits a progress event with `phase: "scoring"`
- [x] **AC-US3-04**: Given the compare endpoint replaces `withHeartbeat()` with the dynamic heartbeat, when `stop()` is called in both success and error paths, then no timer leaks occur
- [x] **AC-US3-05**: Given periodic heartbeat ticks continue between phase transitions, when a tick fires, then it uses the most recently updated phase and message

---

## Implementation

**Increment**: [0495-comparison-progress-observability](../../../../../increments/0495-comparison-progress-observability/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-005**: Replace `withHeartbeat()` with `startDynamicHeartbeat()` in compare endpoint
- [x] **T-006**: Verify heartbeat ticks use latest phase between transitions
