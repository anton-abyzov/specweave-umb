---
increment: 0562-vskill-studio-activation-category-model
title: "vSkill Studio: Activation Test, Category Selection, Model Connection"
type: feature
priority: P1
status: active
created: 2026-03-17
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# vSkill Studio: Activation Test, Category Selection, Model Connection

## Problem Statement

The vSkill Studio UI has four interconnected issues that degrade the skill creation and testing workflow:

1. **Category auto-selection is naive** -- When AI generates a skill, the plugin dropdown defaults to the first available plugin (`useCreateSkill.ts:173`) regardless of skill content. Users must manually pick the correct category.
2. **Activation test page has bugs and hardcoded prompts** -- The SSE event processing in `WorkspaceContext.tsx` re-processes the entire `events` array on each render (append-only, never cleared), causing duplicate dispatches. Template prompts ("How do I use this feature?", "What's the weather?") are generic and unrelated to the skill being tested.
3. **Model selector is disconnected** -- The activation test endpoint calls `getClient()` which reads the global `currentOverrides` (`api-routes.ts:40-44`), ignoring the model selected in the UI dropdown.
4. **Draft orphaning on category change** -- AI generation auto-saves a draft to the current plugin directory (`useCreateSkill.ts:315-327`). If the user changes the plugin dropdown before clicking Create, the old draft files remain on disk, producing duplicate sidebar entries.

## Goals

- Intelligent LLM-based category matching that analyzes generated skill content against existing plugins
- AI-generated activation test prompts derived from the skill description, with persistent test history
- Model selector properly wired through to activation test and prompt generation endpoints
- Draft cleanup that prevents orphaned skill directories when the target plugin changes

## User Stories

### US-001: LLM-Based Category Matching During Skill Generation
**Project**: vskill
**As a** skill author
**I want** the AI to recommend the best-fit plugin (category) based on the generated skill content
**So that** I do not have to manually guess which plugin my skill belongs to

**Acceptance Criteria**:
- [ ] **AC-US1-01**: Given existing plugins ["google-workspace", "marketing", "testing"], when AI generates a skill about "Chrome browser automation for social media posts", then the generation response includes a `plugin` field with the best-matching plugin name
- [ ] **AC-US1-02**: Given the generation prompt is sent to `/api/skills/generate`, when existing plugin names are available from `detectProjectLayout()`, then the plugin names are included in the LLM system prompt so the model can classify
- [ ] **AC-US1-03**: Given AI returns a `plugin` field in the SSE `done` event, when `useCreateSkill` processes the response, then `setPlugin()` is called with the returned plugin value instead of keeping the first-available default
- [ ] **AC-US1-04**: Given AI determines no existing plugin is a good fit, when the `plugin` field is a new name not in the existing list, then the UI switches to "New Plugin" mode with the suggested name pre-filled in the `newPlugin` field
- [ ] **AC-US1-05**: Given the user has selected a model in the config dropdown, when skill generation runs, then the same model is used for category classification (no separate LLM call needed -- classification happens within the generation prompt)

---

### US-002: AI-Generated Activation Test Prompts
**Project**: vskill
**As a** skill author
**I want** the activation test prompts to be generated from my skill's actual description
**So that** I get relevant positive and negative test cases instead of generic placeholders

**Acceptance Criteria**:
- [ ] **AC-US2-01**: Given ActivationPanel loads for a skill with a description, when the user clicks "Generate Test Prompts", then the backend generates 3-5 "should activate" and 3-5 "should not activate" prompts using the skill description as context
- [ ] **AC-US2-02**: Given the hardcoded `PROMPT_TEMPLATES` array in `ActivationPanel.tsx`, when the feature is implemented, then the static template buttons ("+ Should activate", "+ Should NOT activate") are replaced by a single "Generate Test Prompts" button
- [ ] **AC-US2-03**: Given test prompts have already been generated, when the user clicks the button again, then it shows "Regenerate" label and replaces the textarea content with fresh AI-generated prompts
- [ ] **AC-US2-04**: Given the prompt generation endpoint is called, when it receives the request, then it accepts `{provider, model}` in the POST body and uses that model for generation instead of the global `currentOverrides`
- [ ] **AC-US2-05**: Given no skill description is available, when the panel loads, then the "Generate Test Prompts" button is disabled with a tooltip "No skill description available"

---

### US-003: Fix Duplicate SSE Event Dispatch in Activation Tests
**Project**: vskill
**As a** skill author
**I want** activation test results to appear exactly once per prompt
**So that** I see accurate result counts and no duplicate entries in the results list

**Acceptance Criteria**:
- [ ] **AC-US3-01**: Given the `useEffect` in `WorkspaceContext.tsx` that processes `activationSSE.events`, when new events arrive, then only unprocessed events are handled using a processed-events index (cursor) that tracks the last processed position
- [ ] **AC-US3-02**: Given 5 activation prompts are tested, when all SSE `prompt_result` events arrive, then exactly 5 `ACTIVATION_RESULT` dispatches occur (not 5+4+3+2+1 = 15 from re-processing)
- [ ] **AC-US3-03**: Given the same cursor fix pattern, when applied to the `activationSSE.error` effect, then error dispatches also fire exactly once

---

### US-004: Connect Model Selector to Activation Tests
**Project**: vskill
**As a** skill author
**I want** activation tests to use the model I selected in the UI dropdown
**So that** I can test activation behavior across different LLM providers and models

**Acceptance Criteria**:
- [ ] **AC-US4-01**: Given the activation test endpoint at `POST /api/skills/:plugin/:skill/activation-test`, when it receives a request body, then it accepts optional `provider` and `model` fields alongside the existing `prompts` array
- [ ] **AC-US4-02**: Given `provider` and `model` are present in the request body, when the endpoint creates the LLM client, then it calls `createLlmClient({ provider, model })` instead of the global `getClient()`
- [ ] **AC-US4-03**: Given `provider` and `model` are absent from the request body, when the endpoint creates the LLM client, then it falls back to the global `getClient()` for backward compatibility
- [ ] **AC-US4-04**: Given the `runActivationTest` function in `WorkspaceContext.tsx`, when it calls `activationSSE.start()`, then it includes the current `provider` and `model` from ConfigContext in the POST body

---

### US-005: Persist Activation Test History
**Project**: vskill
**As a** skill author
**I want** activation test results to be saved and displayed as a run history
**So that** I can track how my skill's activation accuracy changes over time

**Acceptance Criteria**:
- [ ] **AC-US5-01**: Given an activation test run completes, when the server sends the `done` SSE event with the summary, then it also writes an entry to `activation-history.json` in the skill directory containing timestamp, prompt count, precision, recall, reliability, provider, and model
- [ ] **AC-US5-02**: Given `activation-history.json` has 50 entries, when a new entry is written, then the oldest entry is evicted to maintain the 50-run cap
- [ ] **AC-US5-03**: Given the ActivationPanel renders, when activation-history.json exists with past runs, then a "History" section below the results displays a list of past runs with date, model used, and precision/recall/reliability scores
- [ ] **AC-US5-04**: Given a new activation test run completes in the current session, when the history section is visible, then the new run appears at the top of the history list without requiring a page reload

---

### US-006: Draft Cleanup on Plugin Change
**Project**: vskill
**As a** skill author
**I want** draft skill files to be cleaned up when I change the target plugin before creating
**So that** I do not end up with duplicate skill entries in the sidebar

**Acceptance Criteria**:
- [ ] **AC-US6-01**: Given AI generation auto-saved a draft to plugin "google-workspace" via `api.saveDraft()`, when the user changes the plugin dropdown to "marketing" and clicks Create, then the `POST /api/skills/create` request includes a `draftDir` field pointing to the original draft location
- [ ] **AC-US6-02**: Given `draftDir` is present in the create request and differs from the target skill directory, when the skill is successfully created in the new location, then the backend deletes the directory at `draftDir`
- [ ] **AC-US6-03**: Given `draftDir` is present but the create operation fails, when the error is returned, then the draft directory is NOT deleted (preserving the user's work)
- [ ] **AC-US6-04**: Given `draftDir` is absent from the create request (manual creation, no prior draft), when the skill is created, then no cleanup is attempted
- [ ] **AC-US6-05**: Given the `useCreateSkill` hook receives a successful `done` SSE event, when it calls `api.saveDraft()`, then it stores the draft path (plugin + layout + name) in a ref so it can be sent as `draftDir` during `handleCreate()`

## Out of Scope

- Reworking the multi-provider config UI (model dropdown itself works, just not wired to activation)
- Activation test parallelism (prompts are tested sequentially, one at a time)
- Migration of existing benchmark-history.json format (activation history is a new, separate file)
- Plugin creation/management UI (only auto-selection from existing plugins)
- Batch activation testing across multiple skills

## Technical Notes

### Dependencies
- `createLlmClient()` from `src/eval/llm.ts` -- used for model-specific client creation
- `detectProjectLayout()` from `skill-create-routes.ts` -- provides existing plugin names
- `testActivation()` from `src/eval/activation-tester.ts` -- core activation logic
- `useSSE` hook from `src/eval-ui/src/sse.ts` -- SSE event consumption

### Constraints
- Activation history file size must stay bounded (50-run cap)
- Draft cleanup must be atomic with skill creation (no partial state)
- SSE cursor fix must not break the existing `genEvalsSSE` and `aiEditSSE` event processing patterns in WorkspaceContext

### Architecture Decisions
- **LLM-based category matching over heuristic**: Plugin names alone are too ambiguous for keyword matching. Including them in the generation system prompt lets the same LLM call handle both skill generation and classification with zero extra latency.
- **Processed-events cursor over switching to useMultiSSE**: The cursor approach is the minimal fix. Activation SSE uses the single-stream `useSSE` hook which is also used by AI edit and eval generation. Switching just activation to `useMultiSSE` would be inconsistent; fixing the root cause (re-processing) is cleaner.
- **Draft path tracking via ref**: Using a mutable ref in `useCreateSkill` avoids adding draft path to React state (no re-renders needed) and keeps the cleanup info co-located with the creation flow.

## Non-Functional Requirements

- **Performance**: Prompt generation should complete in under 10 seconds. No additional LLM calls for category matching (folded into generation).
- **Compatibility**: History file format must be forward-compatible (JSON with versioned schema field).
- **Reliability**: Draft cleanup failure must not block skill creation (log warning, proceed).

## Edge Cases

- **No existing plugins**: Category matching returns a new plugin name suggestion. UI enters "New Plugin" mode.
- **Empty skill description**: "Generate Test Prompts" button disabled. Activation test still works with manually typed prompts.
- **Draft directory already deleted**: If user manually deleted the draft, `draftDir` cleanup silently succeeds (no error on missing directory).
- **SSE stream aborted mid-test**: Cursor position is preserved; partial results remain visible. History entry is NOT written for incomplete runs.
- **Model provider unavailable**: Activation test falls back to global `getClient()` default if the specified provider returns an error.
- **Concurrent draft saves**: If two rapid generation runs overlap, only the latest draft path is tracked in the ref.

## Risks

| Risk | Probability | Impact | Severity | Mitigation |
|------|-------------|--------|----------|------------|
| LLM returns invalid plugin name (typo, hallucination) | 0.3 | 3 | 0.9 | Validate against known plugin list; fall back to "New Plugin" mode if no match |
| Draft cleanup deletes user-modified files | 0.1 | 7 | 0.7 | Only delete if path matches the exact draft structure (SKILL.md + evals); verify before delete |
| Cursor index gets out of sync after SSE reconnect | 0.2 | 4 | 0.8 | Reset cursor to 0 on `ACTIVATION_START` dispatch, which clears events array |
| Activation history file corruption from concurrent writes | 0.1 | 3 | 0.3 | Server-side writes are sequential (single Node.js process); use read-modify-write pattern |

## Success Metrics

- Category auto-selection matches user's eventual choice in 80%+ of AI generations
- Zero duplicate sidebar entries from draft orphaning
- Activation test results show exactly N entries for N prompts (no duplicates)
- Test history persists across page reloads and shows last 50 runs
