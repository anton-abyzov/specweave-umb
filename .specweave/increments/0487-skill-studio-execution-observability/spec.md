---
increment: 0487-skill-studio-execution-observability
title: "Skill Studio Execution Observability"
type: feature
priority: P1
status: active
created: 2026-03-11
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Skill Studio Execution Observability

## Problem Statement

The Skill Studio's AI operations (AI Edit, Generate Evals, Auto-Improve) currently show only a static spinner with no progress feedback. Users stare at frozen UIs for 5-30 seconds with no indication of what's happening. When errors occur (API rate limits, context window exceeded, timeouts), they see raw, unactionable error messages like "Improvement failed: Connection timeout". The Run tab already has excellent SSE-based observability with heartbeats and ProgressLog -- the AI operations should match that quality.

## Goals

- Eliminate "frozen UI" perception during all AI operations by showing real-time progress with elapsed time and phase indicators
- Replace raw error strings with classified, actionable error cards that tell users what went wrong and how to fix it
- Add abort/cancel support so users can interrupt long-running AI operations
- Reuse existing SSE infrastructure (sse-helpers.ts, useSSE hook, ProgressLog component) to minimize new code

## User Stories

### US-001: SSE Streaming for AI Operations
**Project**: vskill
**As a** skill developer
**I want** AI Edit, Generate Evals, and Auto-Improve endpoints to stream progress via SSE
**So that** the frontend can show real-time feedback instead of blocking on a single HTTP response

**Acceptance Criteria**:
- [x] **AC-US1-01**: Given the `/api/skills/:plugin/:skill/improve` endpoint is called (both auto and instruct modes), when the request is in progress, then it emits SSE events with `Content-Type: text/event-stream` using `initSSE()` from sse-helpers.ts
- [x] **AC-US1-02**: Given the `/api/skills/:plugin/:skill/generate-evals` endpoint is called, when the request is in progress, then it emits SSE progress events followed by a `done` event containing the generated evals data
- [x] **AC-US1-03**: Given the `/api/skills/generate` endpoint is called, when the request is in progress, then it emits SSE progress events followed by a `done` event containing the generated skill data
- [x] **AC-US1-04**: Given any of the three SSE endpoints is processing, when the LLM call is active, then heartbeat progress events are emitted every 3 seconds with shape `{ phase, message, elapsed_ms }`
- [x] **AC-US1-05**: Given an SSE endpoint is processing, then it emits three distinct phases in order: "preparing" (building prompt), "generating" (LLM call with heartbeats), "parsing" (extracting result from LLM response)

---

### US-002: Progress UI for AI Operations
**Project**: vskill
**As a** skill developer
**I want** to see ProgressLog-style feedback during AI Edit, Generate Evals, and Auto-Improve
**So that** I know the system is working and can see elapsed time and current phase

**Acceptance Criteria**:
- [x] **AC-US2-01**: Given AI Edit is submitted in the AiEditBar, when the generation is in progress, then a ProgressLog component appears below the input showing phase transitions and elapsed time
- [x] **AC-US2-02**: Given Auto-Improve is triggered in the SkillImprovePanel, when the improvement is running, then a ProgressLog component appears showing progress phases and elapsed time
- [x] **AC-US2-03**: Given Generate Evals is triggered, when generation is in progress, then a ProgressLog component appears showing progress phases and elapsed time
- [x] **AC-US2-04**: Given Generate Skill (AI-assisted creation) is triggered, when generation is in progress, then a ProgressLog component appears showing progress phases and elapsed time
- [x] **AC-US2-05**: Given an AI operation completes successfully, then the ProgressLog collapses and the result (diff view, generated evals, etc.) is displayed as before

---

### US-003: Error Classification and Structured Error Cards
**Project**: vskill
**As a** skill developer
**I want** errors from AI operations to be classified into categories with actionable hints
**So that** I can quickly understand what went wrong and how to fix it

**Acceptance Criteria**:
- [x] **AC-US3-01**: Given an AI operation fails, then the server-side error is classified into one of these categories: `rate_limit`, `context_window`, `auth`, `timeout`, `provider_unavailable`, `parse_error`, `unknown`
- [x] **AC-US3-02**: Given a `rate_limit` error occurs, then the error card shows a countdown timer (using `retry-after` header value, defaulting to 30 seconds if absent) and an inline Retry button
- [x] **AC-US3-03**: Given a `context_window` error occurs, then the error card shows a hint like "SKILL.md content is too large for this model. Try a model with a larger context window or reduce the skill content."
- [x] **AC-US3-04**: Given any classified error occurs, then the frontend renders a structured error card with: category icon, error title, description, actionable hint, and Retry button -- replacing the current plain red error box
- [x] **AC-US3-05**: Given a CLI provider (claude-cli, codex-cli, gemini-cli) returns an error via stderr, then regex pattern matching classifies it into the appropriate error category rather than showing the raw stderr text

---

### US-004: Abort/Cancel Support for AI Edit
**Project**: vskill
**As a** skill developer
**I want** to cancel an in-progress AI Edit generation by pressing Escape
**So that** I don't have to wait for a slow or unwanted generation to complete

**Acceptance Criteria**:
- [x] **AC-US4-01**: Given an AI Edit generation is in progress, when the user presses Escape, then the SSE connection is aborted via AbortController and the server-side LLM process is terminated
- [x] **AC-US4-02**: Given an AI Edit generation is cancelled, then the UI returns to the instruction input with the original instruction text preserved, ready for re-submission
- [x] **AC-US4-03**: Given an AI Edit generation is in progress, then the Submit button changes to a Cancel button (or shows a cancel affordance) indicating the operation can be interrupted
- [x] **AC-US4-04**: Given the SSE connection drops unexpectedly (network error, laptop sleep), then the frontend shows a "Connection lost" error state with a Retry button, without auto-retry

---

### US-005: API Client Migration to SSE
**Project**: vskill
**As a** skill developer
**I want** the frontend API calls for improve, generate-evals, and generate-skill to use SSE streaming
**So that** progress events are consumed in real-time rather than waiting for the full response

**Acceptance Criteria**:
- [x] **AC-US5-01**: Given `api.improveSkill()` is called, then it uses the `useSSE` hook to consume the SSE stream, accumulating progress events and extracting the final result from the `done` event
- [x] **AC-US5-02**: Given `api.instructEdit()` is called, then it uses SSE streaming with the same progress/done event pattern as improveSkill
- [x] **AC-US5-03**: Given `api.generateEvals()` is called, then it uses SSE streaming with progress events and extracts the generated evals from the `done` event
- [x] **AC-US5-04**: Given `api.generateSkill()` is called, then it uses SSE streaming with progress events and extracts the generated skill data from the `done` event
- [x] **AC-US5-05**: Given an SSE endpoint returns an `error` event, then the frontend extracts the classified error and renders the structured error card from US-003

## Out of Scope

- True token-level streaming from LLM providers (heartbeat approach instead)
- Changes to the LlmClient interface or provider implementations
- Reconnection/auto-retry logic for dropped SSE connections
- Progress for the apply-improvement endpoint (it's a fast file write, no SSE needed)
- Changes to the Run tab's existing SSE implementation

## Technical Notes

### Dependencies
- Existing `sse-helpers.ts` (server): `initSSE()`, `sendSSE()`, `sendSSEDone()`, `withHeartbeat()`
- Existing `sse.ts` (frontend): `useSSE` hook with abort support
- Existing `ProgressLog.tsx` component

### Constraints
- Heartbeat interval: 3 seconds (matches existing benchmark SSE)
- Progress event shape: `{ phase: string, message: string, elapsed_ms: number }` -- no operationId needed since operations are one-at-a-time per session
- Three phases per operation: "preparing", "generating", "parsing"
- Error classification must handle both structured HTTP errors (Anthropic API) and raw stderr text (CLI providers) via regex pattern matching

### Architecture Decisions
- Reuse `withHeartbeat()` from sse-helpers.ts for the LLM call phase, adapting its signature to not require evalId
- Error classification happens server-side, returning structured error objects via SSE error events
- The `done` SSE event carries the full result payload (improved content, generated evals, etc.) to maintain compatibility with the existing result-handling UI code

## Success Metrics

- Zero "frozen spinner" states: all AI operations show phase + elapsed time within 3 seconds of starting
- Error classification coverage: at least 5 distinct error categories with actionable hints
- Abort latency: Escape key cancels AI Edit generation within 1 second
