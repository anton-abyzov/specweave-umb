---
increment: 0485-skill-studio-ai-create
title: "Skill Studio AI-Assisted Skill Creation"
type: feature
priority: P1
status: completed
created: 2026-03-11
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Skill Studio AI-Assisted Skill Creation

## Overview

Add an AI-assisted mode to the Create Skill page in Skill Studio (eval-ui). Users describe what a skill should do in natural language, select a provider/model, and the system generates a complete SKILL.md (name, description, system prompt body, frontmatter metadata) plus starter eval test cases -- all via a real-time SSE streaming UX. The generated content populates the manual form for review and editing before final creation.

## User Personas

- **Skill Author**: A developer or prompt engineer who uses Skill Studio to create, test, and iterate on Claude/LLM skills. They may not know Skill Studio best practices (trigger descriptions, writing style, progressive disclosure) and benefit from AI scaffolding.
- **Power User**: An experienced skill author who prefers manual creation but occasionally uses AI mode for inspiration or to bootstrap complex skills quickly.

## User Stories

### US-001: AI-Assisted Skill Generation (P1)
**Project**: vskill

**As a** skill author
**I want** to describe what my skill should do in natural language and have AI generate the full SKILL.md content
**So that** I can create production-quality skills without memorizing Skill Studio best practices

**Acceptance Criteria**:
- [x] **AC-US1-01**: The Create Skill page displays a Manual / AI-Assisted mode toggle in the header
- [x] **AC-US1-02**: Selecting AI-Assisted mode shows a prompt textarea, provider/model selectors, and a "Generate Skill" button
- [x] **AC-US1-03**: Submitting a prompt calls `POST /api/skills/generate?sse` with `{ prompt, provider, model }`
- [x] **AC-US1-04**: The backend sends SSE progress events (`preparing`, `generating`, `parsing`) so the user sees real-time feedback
- [x] **AC-US1-05**: On successful generation, the AI output (name, description, model, allowedTools, body, evals, reasoning) populates the manual form fields
- [x] **AC-US1-06**: After generation, mode switches to manual so the user can review and edit before creating
- [x] **AC-US1-07**: An AI-generated reasoning banner appears above the manual form after generation
- [x] **AC-US1-08**: The user can dismiss the reasoning banner and pending evals independently

---

### US-002: Provider and Model Selection for Generation (P1)
**Project**: vskill

**As a** skill author
**I want** to choose which AI provider and model generates my skill
**So that** I can use whichever provider is available and pick the right quality/speed tradeoff

**Acceptance Criteria**:
- [x] **AC-US2-01**: The provider dropdown shows only available providers (from `GET /api/config`)
- [x] **AC-US2-02**: Changing provider auto-selects the first available model for that provider
- [x] **AC-US2-03**: Claude CLI defaults to the `sonnet` model for generation
- [x] **AC-US2-04**: Provider and model dropdowns are disabled during generation

---

### US-003: Generated Test Cases (P1)
**Project**: vskill

**As a** skill author
**I want** the AI to generate starter eval test cases alongside the SKILL.md
**So that** I can immediately benchmark the new skill without writing evals from scratch

**Acceptance Criteria**:
- [x] **AC-US3-01**: The AI generation prompt instructs the LLM to produce 2-3 eval test cases with assertions
- [x] **AC-US3-02**: Generated evals are displayed as a card list in the manual form under "Generated Test Cases"
- [x] **AC-US3-03**: Each eval card shows name, truncated prompt, and assertion badges
- [x] **AC-US3-04**: When the skill is created with pending evals, the backend writes `evals/evals.json` alongside SKILL.md
- [x] **AC-US3-05**: Generated evals are capped at 10 to prevent LLM overgeneration

---

### US-004: Error Handling and Cancellation (P1)
**Project**: vskill

**As a** skill author
**I want** clear error messages and the ability to cancel a running generation
**So that** I understand what went wrong and don't have to wait for a stuck request

**Acceptance Criteria**:
- [x] **AC-US4-01**: An empty prompt shows inline validation: "Describe what your skill should do"
- [x] **AC-US4-02**: SSE error events are classified (rate_limit, auth, timeout, provider_unavailable, parse_error, unknown) and shown via ErrorCard with category-specific titles, descriptions, and hints
- [x] **AC-US4-03**: Rate-limit errors show a countdown timer before retry is enabled
- [x] **AC-US4-04**: A "Cancel Generation" button appears during generation and aborts the SSE stream
- [x] **AC-US4-05**: Prompt length is validated server-side (max 10,000 characters)
- [x] **AC-US4-06**: Parse failures (non-JSON LLM response) return a 422 with actionable message

---

### US-005: Backend Skill Generation Endpoint (P1)
**Project**: vskill

**As a** Skill Studio backend
**I want** a `POST /api/skills/generate` endpoint that calls an LLM with Skill Studio best-practice instructions
**So that** the frontend can offer AI-assisted skill creation

**Acceptance Criteria**:
- [x] **AC-US5-01**: The endpoint accepts `{ prompt, provider?, model? }` and returns a `GenerateSkillResult`
- [x] **AC-US5-02**: The system prompt encodes Skill Studio best practices: trigger description quality, imperative writing style, progressive disclosure, structured sections, eval generation rules
- [x] **AC-US5-03**: The LLM is asked to return JSON followed by `---REASONING---` separator
- [x] **AC-US5-04**: `parseGenerateResponse` extracts and sanitizes the JSON, strips code fences, and separates reasoning
- [x] **AC-US5-05**: Invalid skill names after sanitization throw a descriptive error
- [x] **AC-US5-06**: The endpoint supports both SSE mode (`?sse` query param or `Accept: text/event-stream`) and plain JSON mode
- [x] **AC-US5-07**: SSE mode sends heartbeat events every 3 seconds during long LLM calls via `withHeartbeat`

---

### US-006: Skill Creation with AI-Generated Evals (P2)
**Project**: vskill

**As a** skill author
**I want** the "Create Skill" action to persist both SKILL.md and the AI-generated evals
**So that** my new skill is immediately ready for benchmarking

**Acceptance Criteria**:
- [x] **AC-US6-01**: `POST /api/skills/create` accepts an optional `evals` array in the request body
- [x] **AC-US6-02**: When evals are provided, the backend writes `evals/evals.json` in the new skill directory
- [x] **AC-US6-03**: The evals JSON follows the standard `{ skill_name, evals: [...] }` schema
- [x] **AC-US6-04**: Plugin name is validated with regex to prevent path traversal

---

### US-007: SKILL.md Preview in AI Mode (P2)
**Project**: vskill

**As a** skill author
**I want** a live SKILL.md preview panel while in AI mode
**So that** I can see the current state of what will be generated

**Acceptance Criteria**:
- [x] **AC-US7-01**: A sticky right panel shows the SKILL.md preview (frontmatter + body) in AI mode
- [x] **AC-US7-02**: The preview updates reactively as form fields change
- [x] **AC-US7-03**: The preview persists when switching from AI to manual mode after generation

## Functional Requirements

### FR-001: AI Generation Pipeline
The generation pipeline follows this sequence:
1. User enters a natural language description of the desired skill
2. User selects provider (claude-cli, anthropic, codex-cli, gemini-cli, ollama) and model
3. Frontend POSTs to `/api/skills/generate?sse`
4. Backend constructs a system prompt encoding Skill Studio best practices
5. Backend calls the selected LLM via `createLlmClient`
6. SSE progress events stream to the frontend during the LLM call
7. Backend parses JSON response, separates reasoning, sanitizes skill name
8. Frontend populates the manual form with generated content
9. User reviews, edits, and creates the skill via the standard create flow

### FR-002: System Prompt Engineering
The generation system prompt (`GENERATE_SYSTEM_PROMPT`) encodes:
- SKILL.md anatomy (frontmatter fields, markdown body structure)
- Description quality rules (third-person trigger phrases, specific activation phrases)
- Writing style (imperative/infinitive, not second person)
- Progressive disclosure (500-2000 word body, structured sections)
- Content quality (procedural knowledge, concrete examples, workflow sections)
- Common mistakes to avoid
- Output format specification (JSON schema with field rules)
- Eval generation rules (2-3 realistic test cases with verifiable assertions)

### FR-003: Error Classification System
The `error-classifier.ts` module classifies LLM errors into categories:
- `rate_limit`: Throttling / 429 / capacity issues (retryable, 30s cooldown)
- `context_window`: Token limit exceeded (not retryable)
- `auth`: API key / permission issues (not retryable)
- `timeout`: Request timed out (retryable)
- `provider_unavailable`: CLI not installed / service down (not retryable)
- `parse_error`: Non-JSON LLM response (retryable)
- `unknown`: Fallback (retryable)

### FR-004: Project Layout Detection
The `detectProjectLayout` function scans the project root for existing skill layouts:
- Layout 1: Direct plugins (`{root}/{plugin}/skills/{skill}/`)
- Layout 2: Nested plugins (`{root}/plugins/{plugin}/skills/{skill}/`)
- Layout 3: Root skills (`{root}/skills/{skill}/`)
- Layout 4: Self (root is the skill) -- read-only, not creatable
Suggestion priority: Layout 2 > Layout 1 > Layout 3

## Success Criteria

- Users can go from a natural language description to a complete, deployable skill in under 60 seconds
- Generated skills follow Skill Studio best practices (trigger descriptions, imperative style, structured sections)
- Generated evals provide immediate benchmarking capability without manual authoring
- Error states are clearly communicated with actionable recovery hints
- The feature works with all supported providers (claude-cli, anthropic, codex-cli, gemini-cli, ollama)

## Out of Scope

- Multi-turn conversation for iterative skill refinement (users edit in manual mode after generation)
- AI-assisted skill improvement from the create page (existing `SkillImprovePanel` handles post-creation improvement)
- Automatic benchmarking after creation (user must manually run evals)
- Streaming token-by-token output (backend waits for full LLM response, streams progress heartbeats)
- Image or file attachment support in the prompt
- Saving generation history or prompt templates

## Dependencies

- `eval-server/skill-create-routes.ts` -- backend route registration
- `eval/llm.ts` -- LLM client abstraction supporting 5 providers
- `eval-server/sse-helpers.ts` -- SSE streaming utilities
- `eval-server/error-classifier.ts` -- Error classification for user-friendly messages
- `eval-server/router.ts` -- HTTP router for the eval server
