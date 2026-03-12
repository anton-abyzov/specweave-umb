---
id: US-005
feature: FS-487
title: API Client Migration to SSE
status: completed
priority: P1
created: "2026-03-11T00:00:00.000Z"
tldr: "**As a** skill developer."
project: vskill
external:
  github:
    issue: 78
    url: "https://github.com/anton-abyzov/vskill/issues/78"
---

# US-005: API Client Migration to SSE

**Feature**: [FS-487](./FEATURE.md)

**As a** skill developer
**I want** the frontend API calls for improve, generate-evals, and generate-skill to use SSE streaming
**So that** progress events are consumed in real-time rather than waiting for the full response

---

## Acceptance Criteria

- [x] **AC-US5-01**: Given `api.improveSkill()` is called, then it uses the `useSSE` hook to consume the SSE stream, accumulating progress events and extracting the final result from the `done` event
- [x] **AC-US5-02**: Given `api.instructEdit()` is called, then it uses SSE streaming with the same progress/done event pattern as improveSkill
- [x] **AC-US5-03**: Given `api.generateEvals()` is called, then it uses SSE streaming with progress events and extracts the generated evals from the `done` event
- [x] **AC-US5-04**: Given `api.generateSkill()` is called, then it uses SSE streaming with progress events and extracts the generated skill data from the `done` event
- [x] **AC-US5-05**: Given an SSE endpoint returns an `error` event, then the frontend extracts the classified error and renders the structured error card from US-003

---

## Implementation

**Increment**: [0487-skill-studio-execution-observability](../../../../../increments/0487-skill-studio-execution-observability/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-012**: Wire WorkspaceContext to use useSSE for AI Edit and generate-evals
- [x] **T-013**: Update workspaceTypes.ts and workspaceReducer.ts for progress state
- [x] **T-014**: Wire CreateSkillPage and SkillImprovePanel to SSE (generate-skill and auto-improve)
