---
increment: 0562-vskill-studio-activation-category-model
generated: 2026-03-17
---

# Tasks: vSkill Studio Activation, Category, Model

## US-003: Fix Duplicate SSE Event Dispatch in Activation Tests

### T-001: Add processed-events cursor to activation SSE effect in WorkspaceContext
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03
**Status**: [x] Done
**Test**: Given `activationSSE.events` accumulates 5 `prompt_result` events over 5 renders → When the `useEffect` processes them using `lastActivationIdxRef` → Then exactly 5 `ACTIVATION_RESULT` dispatches occur (not 15 from re-processing)

### T-002: Reset cursor on new activation run start
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02
**Status**: [x] Done
**Test**: Given a first activation run completes with cursor at 5 → When `runActivationTest` is called again → Then `lastActivationIdxRef.current` is reset to 0 before the new SSE stream starts

### T-003: Apply same cursor pattern to genEvalsSSE and aiEditSSE effects
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01
**Status**: [x] Done
**Test**: Given `genEvalsSSE.events` fires 3 eval events → When the effect processes them with an index ref → Then exactly 3 dispatches occur with no duplicates (preventive fix, same pattern as T-001)

### T-004: Unit test SSE duplicate dispatch fix
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03
**Status**: [x] Done
**Test**: Given a mock `useSSE` that emits 3 `prompt_result` events sequentially → When rendered in a test harness with the fixed WorkspaceContext → Then dispatch is called exactly 3 times total (1+1+1, not 1+2+3)

---

## US-004: Connect Model Selector to Activation Tests

### T-005: Extend activation-test endpoint to accept provider/model in POST body
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02, AC-US4-03
**Status**: [x] Done
**Test**: Given a POST to `/api/skills/:plugin/:skill/activation-test` with `{ prompts, provider: "openai", model: "gpt-4o" }` → When the endpoint processes the body → Then it calls `createLlmClient({ provider: "openai", model: "gpt-4o" })` instead of the global `getClient()`

### T-006: Fall back to global getClient when provider/model are absent
**User Story**: US-004 | **Satisfies ACs**: AC-US4-03
**Status**: [x] Done
**Test**: Given a POST to `/api/skills/:plugin/:skill/activation-test` with only `{ prompts }` (no provider/model) → When the endpoint runs → Then it calls the global `getClient()` with no arguments (backward compat preserved)

### T-007: Forward ConfigContext provider/model in runActivationTest
**User Story**: US-004 | **Satisfies ACs**: AC-US4-04
**Status**: [x] Done
**Test**: Given `ConfigContext` has `provider: "claude-cli"` and `model: "claude-sonnet"` → When `runActivationTest` calls `activationSSE.start()` → Then the POST body includes `{ prompts, provider: "claude-cli", model: "claude-sonnet" }`

### T-008: Unit test model passthrough for activation-test endpoint
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02, AC-US4-03
**Status**: [x] Done
**Test**: Given a mocked `createLlmClient` and `getClient` → When the endpoint is called with provider/model vs without → Then the correct factory function is invoked in each case

---

## US-002: AI-Generated Activation Test Prompts

### T-009: Add POST /api/skills/:plugin/:skill/activation-prompts endpoint
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-04
**Status**: [x] Done
**Test**: Given a skill with description "Chrome automation for social media" → When `POST /api/skills/google-workspace/chrome-social/activation-prompts` is called with `{ count: 6, provider: "openai", model: "gpt-4o" }` → Then it returns an SSE stream containing 3 `should_activate` and 3 `should_not_activate` prompts using the specified model

### T-010: Read skill description from SKILL.md for prompt generation
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-05
**Status**: [x] Done
**Test**: Given a SKILL.md with `description: "automate browser tasks"` → When the activation-prompts endpoint parses the file → Then the LLM system prompt contains the exact description text from the frontmatter

### T-011: Add generateActivationPrompts action and state to WorkspaceContext and reducer
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-03
**Status**: [x] Done
**Test**: Given `GENERATE_PROMPTS_START` is dispatched → When reducer handles the action → Then `generatingPrompts: true` and `generatingPromptsError: null` are set in workspace state

### T-012: Replace PROMPT_TEMPLATES with "Generate Test Prompts" button in ActivationPanel
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03
**Status**: [x] Done
**Test**: Given ActivationPanel renders with a skill that has a description → When it mounts → Then there is no `PROMPT_TEMPLATES` static button row and a single "Generate Test Prompts" button is present and enabled

### T-013: Show "Regenerate" label after first generation
**User Story**: US-002 | **Satisfies ACs**: AC-US2-03
**Status**: [x] Done
**Test**: Given prompts have already been generated (textarea is non-empty) → When the user looks at the panel → Then the button label reads "Regenerate Test Prompts" and clicking it replaces the textarea content with fresh prompts

### T-014: Disable generate button when no skill description is available
**User Story**: US-002 | **Satisfies ACs**: AC-US2-05
**Status**: [x] Done
**Test**: Given ActivationPanel renders for a skill with no description → When it mounts → Then the "Generate Test Prompts" button is disabled and a tooltip reads "No skill description available"

### T-015: Unit test activation-prompts endpoint and UI state
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-04, AC-US2-05
**Status**: [x] Done
**Test**: Given a mocked LLM that returns two JSON lines → When the endpoint is called → Then the SSE stream emits two `prompt_generated` events followed by a `done` event with the full prompt array

---

## US-005: Persist Activation Test History

### T-016: Create src/eval/activation-history.ts with write/read/prune logic
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01, AC-US5-02
**Status**: [x] Done
**Test**: Given `activation-history.json` does not exist → When `writeActivationRun(skillDir, run)` is called → Then the file is created with `{ runs: [run] }` and the run has the correct schema fields (id, timestamp, model, provider, promptCount, summary)

### T-017: Enforce 50-run cap in writeActivationRun
**User Story**: US-005 | **Satisfies ACs**: AC-US5-02
**Status**: [x] Done
**Test**: Given `activation-history.json` has exactly 50 runs → When `writeActivationRun` appends a 51st run → Then the file contains 50 runs with the oldest evicted and the newest at the end

### T-018: Add GET /api/skills/:plugin/:skill/activation-history endpoint (summaries)
**User Story**: US-005 | **Satisfies ACs**: AC-US5-03
**Status**: [x] Done
**Test**: Given `activation-history.json` has 3 runs → When `GET /api/skills/plugin/skill/activation-history` is called → Then the response contains an array of 3 run summaries without the full `results` array

### T-019: Add GET /api/skills/:plugin/:skill/activation-history/:runId endpoint (full run)
**User Story**: US-005 | **Satisfies ACs**: AC-US5-03
**Status**: [x] Done
**Test**: Given a run with `id: "run-1710000000000"` in activation-history.json → When `GET /api/skills/plugin/skill/activation-history/run-1710000000000` is called → Then the response contains the full run including the `results` array

### T-020: Write activation history entry on test completion in activation-test endpoint
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01
**Status**: [x] Done
**Test**: Given an activation test run completes and the server sends the `done` SSE event → When the endpoint finishes → Then `writeActivationRun(skillDir, run)` is called with timestamp, provider, model, promptCount, and summary fields populated

### T-021: Add ACTIVATION_HISTORY_LOADED action and activationHistory state
**User Story**: US-005 | **Satisfies ACs**: AC-US5-03, AC-US5-04
**Status**: [x] Done
**Test**: Given `ACTIVATION_HISTORY_LOADED` is dispatched with 3 run summaries → When the reducer handles the action → Then `workspaceState.activationHistory` equals the 3 summaries

### T-022: Add fetchActivationHistory to WorkspaceContext and call on panel mount
**User Story**: US-005 | **Satisfies ACs**: AC-US5-03
**Status**: [x] Done
**Test**: Given ActivationPanel mounts for a skill with existing history → When the component mounts → Then `GET /api/skills/:plugin/:skill/activation-history` is called and the returned runs are stored in workspace state

### T-023: Render collapsible History section in ActivationPanel
**User Story**: US-005 | **Satisfies ACs**: AC-US5-03, AC-US5-04
**Status**: [x] Done
**Test**: Given `activationHistory` state has 2 runs → When ActivationPanel renders → Then a "History" section shows 2 rows, each displaying date, model, and precision/recall/reliability scores

### T-024: Prepend new run to history list without page reload
**User Story**: US-005 | **Satisfies ACs**: AC-US5-04
**Status**: [x] Done
**Test**: Given the History section is visible with 2 existing runs → When the current activation test run completes (ACTIVATION_DONE dispatched) → Then the new run appears at the top of the history list without a fetch call

### T-025: Unit test activation-history.ts (write, read, prune)
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01, AC-US5-02
**Status**: [x] Done
**Test**: Given a temp directory with no activation-history.json → When write is called 51 times → Then the file contains exactly 50 runs (oldest evicted) and `listActivationRuns` returns 50 summaries without `results` arrays

---

## US-001: LLM-Based Category Matching During Skill Generation

### T-026: Add matchExistingPlugin heuristic to skill-create-routes.ts
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02
**Status**: [x] Done
**Test**: Given plugins ["google-workspace", "marketing", "testing"] and a skill with tags ["testing", "eval"] → When `matchExistingPlugin(skillMeta, pluginList)` is called → Then it returns `{ plugin: "testing", confidence: "high", reason: "2 matching tags: testing, eval" }`

### T-027: Include suggestedPlugin in generate SSE done event
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-05
**Status**: [x] Done
**Test**: Given skill generation completes and matching plugin "testing" is found → When the server sends the SSE `done` event → Then `data.suggestedPlugin` includes `{ plugin: "testing", layout: 1, confidence: "high", reason: "..." }`

### T-028: Return suggestedPlugin null when no existing plugin matches
**User Story**: US-001 | **Satisfies ACs**: AC-US1-04
**Status**: [x] Done
**Test**: Given no existing plugins share tags or description keywords with the new skill → When `matchExistingPlugin` runs → Then it returns `null` and the generate `done` event contains `suggestedPlugin: null`

### T-029: Consume suggestedPlugin in useCreateSkill and update plugin state
**User Story**: US-001 | **Satisfies ACs**: AC-US1-03, AC-US1-04
**Status**: [x] Done
**Test**: Given the SSE `done` event contains `suggestedPlugin: { plugin: "marketing", layout: 1, ... }` → When `useCreateSkill` processes the event → Then `setPlugin("marketing")` and the matching layout are set, replacing the first-available default

### T-030: Enter "New Plugin" mode when suggestedPlugin is a new name
**User Story**: US-001 | **Satisfies ACs**: AC-US1-04
**Status**: [x] Done
**Test**: Given `suggestedPlugin.plugin` is "seo-tools" and "seo-tools" is not in the existing plugin list → When `useCreateSkill` processes the event → Then the UI switches to new-plugin input mode with "seo-tools" pre-filled in the `newPlugin` field

### T-031: Add PluginSuggestionCard component replacing recommendation banner
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-03, AC-US1-04
**Status**: [x] Done
**Test**: Given `suggestedPlugin` state is non-null → When PluginSuggestionCard renders → Then it shows plugin name, reason, and two buttons: "Use this plugin" (calls setPlugin) and "Create new plugin" (enters new-plugin mode)

### T-032: Hide suggestion card when suggestedPlugin is null
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01
**Status**: [x] Done
**Test**: Given `suggestedPlugin` state is null (no match found) → When CreateSkillPage renders → Then neither the old recommendation banner nor the new PluginSuggestionCard is present in the DOM

### T-033: Unit test matchExistingPlugin with tag overlap, keyword overlap, and no-match cases
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-04
**Status**: [x] Done
**Test**: Given three test cases (high tag overlap, low overlap, zero overlap) → When `matchExistingPlugin` is called for each → Then it returns high-confidence match, low-confidence match, and null respectively

---

## US-006: Draft Cleanup on Plugin Change

### T-034: Track draft path in a ref inside useCreateSkill after saveDraft
**User Story**: US-006 | **Satisfies ACs**: AC-US6-05
**Status**: [x] Done
**Test**: Given AI generation calls `api.saveDraft()` for plugin "google-workspace" → When `useCreateSkill` processes the `done` SSE event → Then `draftDirRef.current` is set to the path `{layout}/{google-workspace}/{skillName}`

### T-035: Include draftDir in POST /api/skills/create request when plugin changed
**User Story**: US-006 | **Satisfies ACs**: AC-US6-01
**Status**: [x] Done
**Test**: Given draft was saved under "google-workspace" (tracked in ref) and user changed plugin to "marketing" → When `handleCreate()` is called → Then the create POST body includes `draftDir: "{layout}/google-workspace/{skillName}"`

### T-036: Skip draftDir field when no draft was saved (manual creation)
**User Story**: US-006 | **Satisfies ACs**: AC-US6-04
**Status**: [x] Done
**Test**: Given the user creates a skill manually without AI generation (draftDirRef is null) → When `handleCreate()` is called → Then the create POST body does NOT include a `draftDir` field

### T-037: Delete draftDir directory on successful skill creation in backend
**User Story**: US-006 | **Satisfies ACs**: AC-US6-02
**Status**: [x] Done
**Test**: Given `draftDir` is present in the create request and differs from the created skill path → When skill creation succeeds → Then `fs.rm(draftDir, { recursive: true, force: true })` is called and the old directory is removed

### T-038: Do NOT delete draftDir when skill creation fails
**User Story**: US-006 | **Satisfies ACs**: AC-US6-03
**Status**: [x] Done
**Test**: Given `draftDir` is present in the create request → When skill creation throws an error → Then the draft directory at `draftDir` is NOT deleted and the error is returned to the client

### T-039: Skip cleanup when draftDir is absent from create request
**User Story**: US-006 | **Satisfies ACs**: AC-US6-04
**Status**: [x] Done
**Test**: Given a create request with no `draftDir` field → When the endpoint processes the request → Then no filesystem cleanup is attempted (no `fs.rm` call)

### T-040: Unit test draft cleanup (success, failure, absent) paths
**User Story**: US-006 | **Satisfies ACs**: AC-US6-01, AC-US6-02, AC-US6-03, AC-US6-04
**Status**: [x] Done
**Test**: Given mocked fs module and three scenarios (draftDir present + success, draftDir present + failure, no draftDir) → When create endpoint handles each → Then cleanup is called only for success case, and never on failure or absence
