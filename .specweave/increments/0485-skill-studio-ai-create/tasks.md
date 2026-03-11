# Tasks: Skill Studio AI-Assisted Skill Creation

## Task Notation

- `[T###]`: Task ID
- `[P]`: Parallelizable
- `[ ]`: Not started
- `[x]`: Completed
- Model hints: haiku (simple), opus (default)

## Phase 1: Backend Generation Endpoint

### US-005: Backend Skill Generation Endpoint (P1)

#### T-001: Implement GENERATE_SYSTEM_PROMPT

**Description**: Write the expert system prompt that instructs the LLM to generate production-quality skill definitions following Skill Studio best practices.

**References**: AC-US5-02

**Implementation Details**:
- Define the prompt as a const string in `skill-create-routes.ts`
- Encode SKILL.md anatomy (frontmatter fields, markdown body)
- Encode description quality rules (third-person triggers, activation phrases)
- Encode writing style (imperative, not second person)
- Encode progressive disclosure (500-2000 words)
- Encode content quality rules (procedural knowledge, examples, workflow sections)
- Define JSON output schema with field rules
- Define `---REASONING---` separator convention
- Specify eval generation rules (2-3 cases, verifiable assertions)

**Test Plan**:
- **File**: N/A (prompt content verified via integration tests in T-003)
- **Tests**:
  - **TC-001**: System prompt contains Skill Studio best practices keywords
    - Given the GENERATE_SYSTEM_PROMPT constant
    - When inspected
    - Then it mentions "description", "trigger", "imperative", "progressive disclosure", "SKILL.md", "evals"

**Dependencies**: None
**Status**: [x] Completed

---

#### T-002: Implement parseGenerateResponse

**Description**: Write the response parser that extracts JSON skill definition and reasoning from LLM output, with defensive sanitization.

**References**: AC-US5-03, AC-US5-04, AC-US5-05

**Implementation Details**:
- Split raw text on `---REASONING---` separator
- Strip code fences (`\`\`\`json ... \`\`\``) from JSON part
- Parse JSON and extract fields with type coercion
- Sanitize skill name: lowercase, strip non-alphanumeric/hyphen, trim leading/trailing hyphens
- Throw descriptive error if name is empty after sanitization
- Cap evals array at 10 entries
- Default reasoning to "Skill generated using Skill Studio best practices."

**Test Plan**:
- **File**: `src/eval-server/__tests__/skill-create-routes.test.ts`
- **Tests**:
  - **TC-002**: Parses valid JSON with reasoning
    - Given LLM output with valid JSON and `---REASONING---` block
    - When parseGenerateResponse is called
    - Then it returns name, description, body, evals, and reasoning
  - **TC-003**: Strips code fences
    - Given LLM output wrapped in \`\`\`json ... \`\`\`
    - When parseGenerateResponse is called
    - Then it extracts the JSON correctly
  - **TC-004**: Sanitizes invalid skill name characters
    - Given JSON with name "My Awesome Skill!"
    - When parseGenerateResponse is called
    - Then name is "my-awesome-skill" (kebab-case, no special chars)
  - **TC-005**: Throws on empty name after sanitization
    - Given JSON with name "!!!"
    - When parseGenerateResponse is called
    - Then it throws "AI returned an invalid skill name"
  - **TC-006**: Caps evals at 10
    - Given JSON with 15 evals
    - When parseGenerateResponse is called
    - Then result.evals has length 10
  - **TC-007**: Handles missing reasoning
    - Given LLM output with only JSON (no ---REASONING---)
    - When parseGenerateResponse is called
    - Then reasoning defaults to the fallback message

**Dependencies**: None
**Status**: [x] Completed

---

#### T-003: Implement POST /api/skills/generate endpoint

**Description**: Wire up the generation endpoint with dual-mode (SSE and JSON) support, LLM client integration, and error handling.

**References**: AC-US5-01, AC-US5-06, AC-US5-07, AC-US4-05, AC-US4-06

**Implementation Details**:
- Register `POST /api/skills/generate` route in `registerSkillCreateRoutes`
- Validate prompt is non-empty and under 10,000 characters
- Detect SSE mode from `?sse` query param or `Accept: text/event-stream` header
- Construct user prompt wrapping the user's input
- Create LLM client with provider/model overrides
- In SSE mode: send progress events (preparing, generating, parsing), use `withHeartbeat` for LLM call, send `done` event with parsed result
- In JSON mode: return parsed result directly
- On error: classify via `classifyError` and send as SSE error event or JSON error
- Handle client abort (res `close` event)

**Test Plan**:
- **File**: `src/eval-server/__tests__/skill-create-routes.test.ts`
- **Tests**:
  - **TC-008**: Returns 400 for empty prompt
    - Given POST with `{ prompt: "" }`
    - When the endpoint processes the request
    - Then it returns 400 with error message
  - **TC-009**: Returns 400 for prompt > 10,000 chars
    - Given POST with prompt of 10,001 characters
    - When the endpoint processes the request
    - Then it returns 400 with "too long" error
  - **TC-010**: Returns valid GenerateSkillResult in JSON mode
    - Given POST with valid prompt (no `?sse`)
    - When the LLM returns valid output
    - Then it returns 200 with name, description, body, evals, reasoning
  - **TC-011**: Returns 422 for unparseable LLM response
    - Given POST with valid prompt
    - When the LLM returns non-JSON text
    - Then it returns 422 with parse error message

**Dependencies**: T-001, T-002
**Status**: [x] Completed

---

## Phase 2: Backend Create Flow Extension

### US-006: Skill Creation with AI-Generated Evals (P2)

#### T-004: Extend POST /api/skills/create for evals

**Description**: Extend the create endpoint to accept and persist AI-generated evals alongside the SKILL.md.

**References**: AC-US6-01, AC-US6-02, AC-US6-03, AC-US6-04

**Implementation Details**:
- Add optional `evals` field to `CreateSkillRequest` interface
- Create `evals/` subdirectory during skill creation
- When evals are provided, write `evals/evals.json` with `{ skill_name, evals }` schema
- Add plugin name regex validation: `/^[a-z0-9]([a-z0-9._-]*[a-z0-9])?$/i`
- Return 400 for invalid plugin names

**Test Plan**:
- **File**: `src/eval-server/__tests__/skill-create-routes.test.ts`
- **Tests**:
  - **TC-012**: Creates skill with evals
    - Given create request with name, description, body, and 2 evals
    - When the endpoint processes the request
    - Then SKILL.md and evals/evals.json are both written
  - **TC-013**: Creates skill without evals
    - Given create request without evals field
    - When the endpoint processes the request
    - Then only SKILL.md is written (no evals.json)
  - **TC-014**: Rejects path traversal in plugin name
    - Given create request with plugin name "../etc"
    - When the endpoint processes the request
    - Then it returns 400

**Dependencies**: None
**Status**: [x] Completed

---

## Phase 3: Frontend AI Mode UI

### US-001: AI-Assisted Skill Generation (P1)

#### T-005: Implement mode toggle (Manual / AI-Assisted)

**Description**: Add the mode toggle to the CreateSkillPage header with proper styling and state management.

**References**: AC-US1-01

**Implementation Details**:
- Add `mode` state: `"manual" | "ai"`
- Render toggle with two buttons (Manual, AI-Assisted with sparkle icon)
- Active state uses accent color for AI mode (purple), surface color for manual
- Toggle switches between two render branches

**Test Plan**:
- **File**: `src/eval-ui/src/pages/__tests__/CreateSkillPage.test.tsx`
- **Tests**:
  - **TC-015**: Mode toggle renders with both options
    - Given the CreateSkillPage is mounted
    - When inspecting the header
    - Then both "Manual" and "AI-Assisted" buttons are visible
  - **TC-016**: Clicking AI-Assisted shows the prompt form
    - Given mode is "manual"
    - When user clicks "AI-Assisted"
    - Then the prompt textarea and generate button appear

**Dependencies**: None
**Status**: [x] Completed

---

#### T-006: Implement AI prompt form and generation trigger

**Description**: Build the AI mode form with prompt textarea, provider/model selectors, and generate button with keyboard shortcut.

**References**: AC-US1-02, AC-US1-03, AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04

**Implementation Details**:
- Prompt textarea with placeholder, auto-focus on mode switch, Cmd+Enter shortcut
- Provider dropdown populated from `api.getConfig()`, filtered to available only
- Model dropdown updates when provider changes (first model auto-selected)
- Default to claude-cli / sonnet
- Generate button disabled when prompt is empty, shows SparkleIcon
- All inputs disabled during generation

**Test Plan**:
- **File**: `src/eval-ui/src/pages/__tests__/CreateSkillPage.test.tsx`
- **Tests**:
  - **TC-017**: Provider dropdown shows only available providers
    - Given config with 2 available and 1 unavailable provider
    - When the dropdown renders
    - Then only available providers are options
  - **TC-018**: Generate button disabled for empty prompt
    - Given AI mode with empty prompt
    - When inspecting the button
    - Then it is disabled with muted styling

**Dependencies**: T-005
**Status**: [x] Completed

---

#### T-007: Implement SSE streaming consumer

**Description**: Build the fetch + ReadableStream SSE consumer that handles progress, done, and error events.

**References**: AC-US1-03, AC-US1-04, AC-US1-05, AC-US1-06, AC-US4-02

**Implementation Details**:
- `handleGenerate` function: POST to `/api/skills/generate?sse` with AbortController
- Read response body via `ReadableStream` reader
- Parse SSE events line-by-line (buffer partial chunks)
- On `progress`: append to `aiProgress` state array
- On `done`/`complete`: populate form fields (name, description, model, allowedTools, body), set pendingEvals, set reasoning, switch to manual mode
- On `error`: set error state, optionally set classified error for ErrorCard
- Handle AbortError silently

**Test Plan**:
- **File**: `src/eval-ui/src/pages/__tests__/CreateSkillPage.test.tsx`
- **Tests**:
  - **TC-019**: Progress events update the progress log
    - Given generation is in progress
    - When SSE progress events arrive
    - Then ProgressLog component shows entries
  - **TC-020**: Done event populates form fields
    - Given generation completes
    - When SSE done event arrives with skill data
    - Then name, description, body fields are populated and mode switches to manual

**Dependencies**: T-006
**Status**: [x] Completed

---

#### T-008: Implement cancel generation

**Description**: Add cancel button that aborts the SSE stream mid-generation.

**References**: AC-US4-04

**Implementation Details**:
- Store `AbortController` in `abortRef`
- During generation: show "Cancel Generation" button instead of "Generate Skill"
- On cancel: call `abortRef.current?.abort()`, set generating to false
- Cleanup abort controller on unmount

**Test Plan**:
- **File**: `src/eval-ui/src/pages/__tests__/CreateSkillPage.test.tsx`
- **Tests**:
  - **TC-021**: Cancel button appears during generation
    - Given generation is in progress
    - When inspecting the UI
    - Then "Cancel Generation" button is visible
  - **TC-022**: Clicking cancel stops generation
    - Given generation is in progress
    - When user clicks "Cancel Generation"
    - Then the abort controller is triggered and generating state resets

**Dependencies**: T-007
**Status**: [x] Completed

---

### US-004: Error Handling and Cancellation (P1)

#### T-009: Implement error display with ErrorCard

**Description**: Display classified errors via ErrorCard and plain errors via inline banner. Handle validation errors.

**References**: AC-US4-01, AC-US4-02, AC-US4-03

**Implementation Details**:
- Empty prompt validation: set `aiError` inline
- SSE error events: if `data.category` exists, use ErrorCard with retry/dismiss callbacks
- Non-SSE errors: show inline error banner
- ErrorCard handles rate-limit countdown timer automatically
- Wire onRetry to `handleGenerate`, onDismiss to clear error state

**Test Plan**:
- **File**: `src/eval-ui/src/pages/__tests__/CreateSkillPage.test.tsx`
- **Tests**:
  - **TC-023**: Empty prompt shows validation error
    - Given AI mode with empty prompt
    - When user clicks Generate
    - Then error "Describe what your skill should do" appears
  - **TC-024**: Classified error shows ErrorCard
    - Given a rate_limit error from SSE
    - When the error is processed
    - Then ErrorCard renders with countdown timer

**Dependencies**: T-007
**Status**: [x] Completed

---

## Phase 4: Generated Content Display

### US-001 (continued): AI-Generated Content Review

#### T-010: Implement AI reasoning banner

**Description**: Show a dismissible banner above the manual form after AI generation, showing the AI's reasoning and pending eval count.

**References**: AC-US1-07, AC-US1-08

**Implementation Details**:
- Render when `aiReasoning` state is non-null
- Purple-tinted background with sparkle icon, "AI Generated" label, reasoning text
- Badge showing "+N test cases" when pendingEvals exist
- Close button clears reasoning and pending evals independently

**Test Plan**:
- **File**: `src/eval-ui/src/pages/__tests__/CreateSkillPage.test.tsx`
- **Tests**:
  - **TC-025**: Reasoning banner appears after generation
    - Given AI generation completed with reasoning "Chose kebab-case name..."
    - When mode switches to manual
    - Then the purple reasoning banner is visible with the text
  - **TC-026**: Close button dismisses banner
    - Given reasoning banner is visible
    - When user clicks close
    - Then banner disappears and aiReasoning is null

**Dependencies**: T-007
**Status**: [x] Completed

---

### US-003: Generated Test Cases (P1)

#### T-011: Implement generated eval cards display

**Description**: Show AI-generated test cases as a card list in the manual form, with name, prompt preview, and assertion badges.

**References**: AC-US3-01, AC-US3-02, AC-US3-03

**Implementation Details**:
- Render when `pendingEvals` is non-null and non-empty
- Card list inside glass-card container with sparkle icon header
- Each card shows: eval name (bold), truncated prompt (120 chars), assertion badges (50 char truncation)
- Purple accent for assertion badges

**Test Plan**:
- **File**: `src/eval-ui/src/pages/__tests__/CreateSkillPage.test.tsx`
- **Tests**:
  - **TC-027**: Eval cards render after generation
    - Given generation produced 3 evals
    - When viewing the manual form
    - Then 3 eval cards are visible with names and assertion badges
  - **TC-028**: Long prompts are truncated
    - Given an eval with a 200-character prompt
    - When the card renders
    - Then the prompt text is truncated at 120 chars with "..."

**Dependencies**: T-007
**Status**: [x] Completed

---

### US-007: SKILL.md Preview Panel (P2)

#### T-012: Implement SKILL.md preview in AI mode

**Description**: Add a sticky right panel showing the live SKILL.md preview in both AI and manual modes.

**References**: AC-US7-01, AC-US7-02, AC-US7-03

**Implementation Details**:
- 340px fixed-width right panel with sticky positioning
- `skillMdPreview` computed from current form fields (description, model, allowedTools, body, name)
- Monospace font, pre-wrap, scrollable (max-height 500px)
- Renders in both AI and manual mode branches

**Test Plan**:
- **File**: `src/eval-ui/src/pages/__tests__/CreateSkillPage.test.tsx`
- **Tests**:
  - **TC-029**: Preview updates when form fields change
    - Given manual mode with description "test"
    - When description changes to "updated"
    - Then preview reflects "updated" in frontmatter
  - **TC-030**: Preview visible in both modes
    - Given the CreateSkillPage
    - When switching between AI and manual mode
    - Then the preview panel is visible in both

**Dependencies**: T-005
**Status**: [x] Completed

---

## Phase 5: Integration and Polish

#### T-013: Wire create button to pass pending evals

**Description**: Ensure the Create Skill button sends AI-generated evals in the create request.

**References**: AC-US3-04, AC-US6-01

**Implementation Details**:
- In `handleCreate`, include `pendingEvals` in the `api.createSkill` call
- Navigate to new skill workspace on success

**Test Plan**:
- **File**: `src/eval-ui/src/pages/__tests__/CreateSkillPage.test.tsx`
- **Tests**:
  - **TC-031**: Create request includes evals when present
    - Given AI generation produced 2 evals
    - When user clicks Create Skill
    - Then the POST body includes the evals array

**Dependencies**: T-004, T-011
**Status**: [x] Completed

---

#### T-014: Security hardening

**Description**: Apply security findings from grill report -- name sanitization, eval cap, prompt length, plugin path traversal.

**References**: AC-US5-05, AC-US4-05, AC-US6-04, AC-US3-05

**Implementation Details**:
- `parseGenerateResponse`: trim leading/trailing hyphens from sanitized name, throw if empty
- `parseGenerateResponse`: cap evals array at 10 entries via `.slice(0, 10)`
- `POST /api/skills/generate`: reject prompts > 10,000 characters with 400
- `POST /api/skills/create`: validate plugin name with `/^[a-z0-9]([a-z0-9._-]*[a-z0-9])?$/i`

**Test Plan**:
- **File**: `src/eval-server/__tests__/skill-create-routes.test.ts`
- **Tests**:
  - **TC-032**: Empty name after sanitization throws
    - Given JSON with name "---"
    - When parseGenerateResponse is called
    - Then it throws descriptive error
  - **TC-033**: Evals capped at 10
    - Given JSON with 15 evals
    - When parseGenerateResponse is called
    - Then result has 10 evals
  - **TC-034**: Prompt over 10K rejected
    - Given POST with 10,001 char prompt
    - When endpoint processes request
    - Then 400 returned
  - **TC-035**: Path traversal plugin rejected
    - Given create request with plugin "../../etc"
    - When endpoint processes request
    - Then 400 returned

**Dependencies**: T-002, T-003, T-004
**Status**: [x] Completed
