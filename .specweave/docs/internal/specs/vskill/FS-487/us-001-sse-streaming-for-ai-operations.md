---
id: US-001
feature: FS-487
title: "SSE Streaming for AI Operations"
status: completed
priority: P1
created: 2026-03-11T00:00:00.000Z
tldr: "**As a** skill developer."
project: vskill
external:
  github:
    issue: 79
    url: https://github.com/anton-abyzov/vskill/issues/79
---

# US-001: SSE Streaming for AI Operations

**Feature**: [FS-487](./FEATURE.md)

**As a** skill developer
**I want** AI Edit, Generate Evals, and Auto-Improve endpoints to stream progress via SSE
**So that** the frontend can show real-time feedback instead of blocking on a single HTTP response

---

## Acceptance Criteria

- [x] **AC-US1-01**: Given the `/api/skills/:plugin/:skill/improve` endpoint is called (both auto and instruct modes), when the request is in progress, then it emits SSE events with `Content-Type: text/event-stream` using `initSSE()` from sse-helpers.ts
- [x] **AC-US1-02**: Given the `/api/skills/:plugin/:skill/generate-evals` endpoint is called, when the request is in progress, then it emits SSE progress events followed by a `done` event containing the generated evals data
- [x] **AC-US1-03**: Given the `/api/skills/generate` endpoint is called, when the request is in progress, then it emits SSE progress events followed by a `done` event containing the generated skill data
- [x] **AC-US1-04**: Given any of the three SSE endpoints is processing, when the LLM call is active, then heartbeat progress events are emitted every 3 seconds with shape `{ phase, message, elapsed_ms }`
- [x] **AC-US1-05**: Given an SSE endpoint is processing, then it emits three distinct phases in order: "preparing" (building prompt), "generating" (LLM call with heartbeats), "parsing" (extracting result from LLM response)

---

## Implementation

**Increment**: [0487-skill-studio-execution-observability](../../../../../increments/0487-skill-studio-execution-observability/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-001**: Make withHeartbeat evalId optional in sse-helpers.ts
- [x] **T-002**: Create error-classifier.ts with all 7 error categories
- [x] **T-003**: Convert improve-routes.ts, api-routes.ts, skill-create-routes.ts to SSE
