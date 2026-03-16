---
increment: 0495-comparison-progress-observability
title: Comparison Progress Observability
type: feature
priority: P1
status: completed
created: 2026-03-11T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Comparison Progress Observability

## Problem Statement

The compare endpoint wraps 3 sequential LLM calls (skill generation, baseline generation, rubric scoring) in a single `withHeartbeat()` that emits the same generic "comparing..." message for 3-4 minutes. Users see no phase differentiation and cannot tell which step is executing or how far along the comparison is.

## Goals

- Replace the opaque "comparing..." heartbeat with per-phase progress events
- Let users see exactly which LLM call is running (skill gen, baseline gen, scoring)
- Keep the existing `withHeartbeat()` helper intact for other endpoints
- Maintain backward compatibility with existing SSE event consumers

## User Stories

### US-001: Dynamic Heartbeat SSE Helper
**Project**: vskill

**As a** backend developer
**I want** a `startDynamicHeartbeat()` SSE helper with imperative `update()`/`stop()` methods
**So that** long-running endpoints can change their progress message mid-flight without restarting the heartbeat timer

**Acceptance Criteria**:
- [x] **AC-US1-01**: Given a response stream, when `startDynamicHeartbeat(res, intervalMs)` is called, then it returns an object with `update(data)` and `stop()` methods
- [x] **AC-US1-02**: Given a running dynamic heartbeat, when `update({ phase, message, eval_id })` is called, then subsequent heartbeat ticks emit the updated phase and message
- [x] **AC-US1-03**: Given a running dynamic heartbeat, when `stop()` is called, then the interval timer is cleared and no further SSE events are emitted
- [x] **AC-US1-04**: Given the new helper is exported from `sse-helpers.ts`, when other modules import it, then the existing `withHeartbeat()` function remains available and unchanged

---

### US-002: Progress Callback in Comparator
**Project**: vskill

**As a** backend developer
**I want** an optional `onProgress` callback parameter on `generateComparisonOutputs()` and `runComparison()`
**So that** callers can receive phase transition events at each of the 3 LLM call boundaries

**Acceptance Criteria**:
- [x] **AC-US2-01**: Given `generateComparisonOutputs(prompt, skillContent, client, onProgress)` is called, when the skill generation LLM call starts, then `onProgress` fires with phase `generating_skill`
- [x] **AC-US2-02**: Given `generateComparisonOutputs()` is executing, when the baseline generation LLM call starts, then `onProgress` fires with phase `generating_baseline`
- [x] **AC-US2-03**: Given `runComparison(prompt, skillContent, client, onProgress)` is called, when the rubric scoring LLM call starts, then `onProgress` fires with phase `scoring`
- [x] **AC-US2-04**: Given no `onProgress` callback is provided, when `runComparison()` is called, then it behaves identically to the current implementation (no regression)

---

### US-003: Wire Dynamic Heartbeat in Compare Endpoint
**Project**: vskill

**As a** Skill Studio user
**I want** the compare endpoint to emit phase-specific progress events
**So that** I can see whether the system is generating the skill output, the baseline output, or scoring

**Acceptance Criteria**:
- [x] **AC-US3-01**: Given a comparison is running, when the skill generation starts, then the SSE stream emits a progress event with `phase: "generating_skill"` and a descriptive message
- [x] **AC-US3-02**: Given a comparison is running, when the baseline generation starts, then the SSE stream emits a progress event with `phase: "generating_baseline"`
- [x] **AC-US3-03**: Given a comparison is running, when rubric scoring starts, then the SSE stream emits a progress event with `phase: "scoring"`
- [x] **AC-US3-04**: Given the compare endpoint replaces `withHeartbeat()` with the dynamic heartbeat, when `stop()` is called in both success and error paths, then no timer leaks occur
- [x] **AC-US3-05**: Given periodic heartbeat ticks continue between phase transitions, when a tick fires, then it uses the most recently updated phase and message

---

### US-004: ProgressLog Phase Support
**Project**: vskill

**As a** Skill Studio user
**I want** ProgressLog to recognize the new comparison phases with appropriate spinners and accent colors
**So that** the progress display is visually consistent with existing phases

**Acceptance Criteria**:
- [x] **AC-US4-01**: Given ProgressLog receives a progress entry with phase `generating_skill`, `generating_baseline`, or `scoring`, when that entry is the latest and running, then it renders with a spinner icon
- [x] **AC-US4-02**: Given ProgressLog receives a completed entry with phase `generating_skill`, `generating_baseline`, or `scoring`, then it renders with the accent color dot (not the green dot)

---

### US-005: ProgressLog on ComparisonPage
**Project**: vskill

**As a** Skill Studio user
**I want** to see a ProgressLog on the ComparisonPage during a running comparison
**So that** I get real-time feedback about which phase is executing instead of a static spinner

**Acceptance Criteria**:
- [x] **AC-US5-01**: Given a comparison is running, when progress SSE events arrive, then ComparisonPage renders a ProgressLog component with accumulated entries
- [x] **AC-US5-02**: Given a comparison completes or errors, when `running` becomes false, then the ProgressLog stops showing the active spinner
- [x] **AC-US5-03**: Given multiple eval cases run sequentially, when a new case starts, then progress entries for the new case appear with fresh phase labels (per-case reset via eval_id context)

## Out of Scope

- Migrating other endpoints (benchmark, improve) to the dynamic heartbeat pattern
- Sub-phase granularity within LLM calls (e.g., "parsing rubric JSON")
- Persistent progress logging or progress history
- Changes to the SSE protocol or event naming beyond the new phases

## Technical Notes

- `startDynamicHeartbeat()` lives in `src/eval-server/sse-helpers.ts` alongside `withHeartbeat()`
- `onProgress` callback type: `(phase: string, message: string) => void`
- The compare endpoint loop already has `aborted` flag + `res.on("close")` for cleanup; `stop()` calls go in the existing try/finally or try/catch structure
- ProgressLog already handles `eval_id` in entries, so per-case context comes free
- All files in `repositories/anton-abyzov/vskill/`

## Success Criteria

- During a comparison run, users see at least 3 distinct phase messages instead of a single repeated "comparing..." message
- No timer leaks: every `startDynamicHeartbeat()` call is matched by a `stop()` call
- Existing endpoints using `withHeartbeat()` are unaffected
- All new code covered by TDD tests (Vitest)
