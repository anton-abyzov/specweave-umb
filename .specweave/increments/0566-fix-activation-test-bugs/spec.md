---
increment: 0566-fix-activation-test-bugs
title: Fix Skill Studio Activation Test Bugs
type: bug
priority: P1
status: completed
created: 2026-03-18T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Fix Skill Studio Activation Test Bugs

## Problem Statement

The Skill Studio activation test workflow has five bugs that degrade reliability and user experience. When backend activation tests throw errors, the frontend silently swallows the error payload from SSE `done` events, leaving users with a stopped spinner and no feedback. Phase 1 auto-classification makes N sequential LLM calls with zero progress events, causing 40-80 seconds of unexplained silence. The "Generate" button silently disables when no skill description exists with no visible explanation. The `/activation-test` and `/activation-prompts` endpoints handle missing frontmatter descriptions inconsistently. Prompt generation provides no heartbeat during a 5-20 second LLM call. Additionally, there are zero tests covering any activation endpoints, components, or flows.

## Goals

- Ensure all backend errors in activation test SSE streams surface visibly to users
- Provide continuous progress feedback during all long-running activation operations
- Make all disabled UI states self-explanatory with visible inline messages
- Unify description fallback behavior across activation endpoints
- Establish test coverage for activation API routes, frontend components, and SSE event processing

## User Stories

### US-001: Surface Error Payloads from SSE Done Events (P0)
**Project**: vskill

**As a** skill developer running activation tests
**I want** backend errors in SSE `done` events to display inline in the results panel
**So that** I understand why my activation test failed instead of seeing a silent spinner stop

**Acceptance Criteria**:
- [x] **AC-US1-01**: Given the backend sends `{error: "..."}` inside an SSE `done` event during `runActivationTest`, when the frontend processes this event, then it dispatches `ACTIVATION_ERROR` with the error message instead of `ACTIVATION_DONE`
- [x] **AC-US1-02**: Given an `ACTIVATION_ERROR` is dispatched, when the results panel renders, then it displays the error message inline in the results area with error styling
- [x] **AC-US1-03**: Given an activation test fails with an error in the `done` event, when the run completes, then no entry is added to the activation history
- [x] **AC-US1-04**: Given the backend sends `{error: "..."}` inside an SSE `done` event during `generateActivationPrompts`, when the frontend processes this event, then it throws an error with the message from the `error` field instead of defaulting `data.prompts` to `[]`

---

### US-002: Emit Progress Events During Phase 1 Auto-Classification (P1)
**Project**: vskill

**As a** skill developer running activation tests with unprefixed prompts
**I want** to see classification progress during Phase 1
**So that** I know the system is working during the 40-80 second auto-classification phase

**Acceptance Criteria**:
- [x] **AC-US2-01**: Given `resolvePrompts` is classifying N prompts with `expected: "auto"`, when each prompt classification completes, then a `classifying` SSE event is emitted with `{index, total}` payload
- [x] **AC-US2-02**: Given `classifying` SSE events are received by the frontend, when the status area renders, then it displays text in the format "Classifying prompt {index}/{total}..." below the progress bar
- [x] **AC-US2-03**: Given all prompts have `expected` values other than `"auto"`, when `resolvePrompts` runs, then no `classifying` events are emitted

---

### US-003: Show Inline Hint When Generate Button Is Disabled (P1)
**Project**: vskill

**As a** skill developer viewing the ActivationPanel
**I want** a visible message explaining why the Generate button is disabled
**So that** I know how to fix the issue instead of guessing why the button is unresponsive

**Acceptance Criteria**:
- [x] **AC-US3-01**: Given the skill has no `description` in its frontmatter, when the ActivationPanel renders, then an inline hint is displayed below the Generate button with the text "Add a description to your skill's frontmatter to enable prompt generation."
- [x] **AC-US3-02**: Given the skill has a valid `description` in its frontmatter, when the ActivationPanel renders, then no inline hint is displayed below the Generate button

---

### US-004: Unify Description Fallback Across Activation Endpoints (P1)
**Project**: vskill

**As a** skill developer using activation features
**I want** both `/activation-test` and `/activation-prompts` to handle missing frontmatter descriptions the same way
**So that** I get consistent behavior regardless of which endpoint I call

**Acceptance Criteria**:
- [x] **AC-US4-01**: Given the skill's SKILL.md has no frontmatter `description` field, when the `/activation-prompts` endpoint is called, then it falls back to `skillContent.slice(0, 500)` instead of returning a 400 error
- [x] **AC-US4-02**: Given the skill's SKILL.md has a valid frontmatter `description` field, when either endpoint is called, then the frontmatter description is used (existing behavior preserved)

---

### US-005: Emit Heartbeat During Prompt Generation (P2)
**Project**: vskill

**As a** skill developer generating activation prompts
**I want** periodic heartbeat events during the LLM call
**So that** I know the connection is alive during the 5-20 second generation window

**Acceptance Criteria**:
- [x] **AC-US5-01**: Given the `/activation-prompts` endpoint starts an LLM generation call, when the call is in progress, then heartbeat SSE events are emitted every approximately 3 seconds using the `withHeartbeat()` pattern
- [x] **AC-US5-02**: Given the LLM generation call completes, when the `done` event is sent, then heartbeat emission stops

## Out of Scope

- Retry logic for failed activation tests (future increment)
- Activation test result caching or persistence beyond in-memory history
- Refactoring the SSE event protocol (adding new event types is in scope, changing existing ones is not)
- UI redesign of the ActivationPanel layout
- Backend error categorization or error codes (plain error messages are sufficient)

## Technical Notes

### Dependencies
- `WorkspaceContext.tsx` SSE event processing (lines 522-559, 630-670)
- `ActivationPanel.tsx` button rendering (line 86)
- `api-routes.ts` activation endpoints (lines 1220-1340)
- `activation-tester.ts` resolvePrompts function (lines 89-108)
- Existing `withHeartbeat()` utility used by other SSE endpoints

### Constraints
- All changes are within the vskill repo only
- SSE event format must remain backward-compatible (additive changes only)
- TDD mode is active -- tests must be written before implementation

### Architecture Decisions
- Use `ACTIVATION_ERROR` dispatch action (additive to existing reducer) rather than repurposing `ACTIVATION_DONE`
- The `classifying` SSE event is a new event type added to the existing SSE protocol
- Description fallback aligns to the more forgiving `slice(0, 500)` approach used by `/activation-test`

## Non-Functional Requirements

- **Performance**: No additional latency introduced; heartbeat and progress events are lightweight metadata-only SSE writes
- **Accessibility**: Inline error messages and hints must be readable by screen readers (use appropriate ARIA attributes)
- **Compatibility**: SSE event additions must not break existing frontend versions that do not handle `classifying` events (unknown events are ignored by the cursor pattern)
- **Test Coverage**: Unit tests for all modified API routes, component tests for ActivationPanel states, integration tests for SSE event flows

## Edge Cases

- Backend sends `done` event with both `error` field AND summary fields: `error` field takes precedence, treat as error
- Backend sends `classifying` events but the test completes before all are processed: no impact, cursor pattern handles this
- `skillContent.slice(0, 500)` produces empty string for empty SKILL.md: existing 404 guard for missing SKILL.md prevents this
- Multiple rapid heartbeat events arrive after generation completes: frontend ignores unknown/late events naturally
- `resolvePrompts` called with mix of `auto` and pre-classified prompts: only `auto` prompts emit `classifying` events, index/total reflects only auto prompts

## Risks

| Risk | Probability | Impact | Severity | Mitigation |
|------|-------------|--------|----------|------------|
| New `classifying` SSE event breaks older frontend builds | 0.1 | 3 | 0.3 | Frontend cursor pattern ignores unknown event types by design |
| `slice(0, 500)` fallback produces low-quality activation results | 0.3 | 4 | 1.2 | Acceptable tradeoff -- matches existing `/activation-test` behavior; user can add proper description |
| Heartbeat timer not cleaned up on abort | 0.2 | 5 | 1.0 | Use `withHeartbeat()` utility which handles cleanup on response close |

## Success Metrics

- Zero silent failures: every backend error in activation SSE streams displays a visible error message
- Continuous feedback: no operation produces more than 5 seconds of silence without a progress or heartbeat event
- Test coverage: activation API routes, ActivationPanel, and WorkspaceContext activation functions all have test files with passing suites
