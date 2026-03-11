# Implementation Plan: Skill Studio AI-Assisted Skill Creation

## Overview

This feature adds an AI-assisted creation mode to Skill Studio's Create Skill page. The architecture follows a clean frontend-backend split: the backend exposes an SSE-capable generation endpoint that calls an LLM with Skill Studio best-practice instructions, while the frontend provides a two-mode UI (AI-Assisted / Manual) that streams progress and populates form fields from generated output. The implementation touches three layers: backend routes, frontend page component, and shared types.

## Architecture

### Components

- **CreateSkillPage (frontend)**: Full-page component with mode toggle (manual/AI), prompt input, provider/model selectors, SSE streaming consumer, and form auto-population after generation
- **skill-create-routes.ts (backend)**: Express-style route handler for `POST /api/skills/generate` with SSE and JSON dual-mode support
- **GENERATE_SYSTEM_PROMPT (backend)**: Expert system prompt encoding Skill Studio best practices for skill authoring
- **parseGenerateResponse (backend)**: Response parser that extracts JSON skill definition and reasoning from LLM output
- **error-classifier.ts (backend)**: Classifies LLM errors into user-friendly categories with recovery hints
- **sse-helpers.ts (backend)**: SSE utilities for streaming progress events and heartbeats
- **ProgressLog (frontend)**: Reusable component for displaying real-time progress entries
- **ErrorCard (frontend)**: Reusable error display with category-specific icons, retry countdown, and dismiss

### Data Model

**GenerateSkillRequest** (frontend -> backend):
```typescript
{ prompt: string; provider?: ProviderName; model?: string }
```

**GenerateSkillResult** (backend -> frontend via SSE `done` event or JSON response):
```typescript
{
  name: string;           // kebab-case skill name
  description: string;    // trigger description for frontmatter
  model: string;          // "" for any, or "opus"/"sonnet"/"haiku"
  allowedTools: string;   // comma-separated or ""
  body: string;           // full SKILL.md body (markdown)
  evals: GeneratedEval[]; // 2-3 test cases with assertions
  reasoning: string;      // AI's design rationale
}
```

**GeneratedEval**:
```typescript
{
  id: number;
  name: string;
  prompt: string;
  expected_output: string;
  assertions: Array<{ id: string; text: string; type: string }>;
}
```

**SSE Event Types**:
- `progress`: `{ phase: "preparing" | "generating" | "parsing", message: string }`
- `done`: Full `GenerateSkillResult`
- `error`: `ClassifiedError` with category, title, description, hint, retryable flag

### API Contracts

- `POST /api/skills/generate` (JSON mode): Request `GenerateSkillRequest`, Response `GenerateSkillResult`
- `POST /api/skills/generate?sse` (SSE mode): Request `GenerateSkillRequest`, Response SSE stream with `progress`, `done`, `error` events
- `POST /api/skills/create` (extended): Request `CreateSkillRequest` with optional `evals` array, Response `CreateSkillResponse`
- `GET /api/config`: Returns `ConfigResponse` with available providers and their models
- `GET /api/project-layout`: Returns `ProjectLayoutResponse` with detected layouts and suggestion
- `GET /api/skill-creator-status`: Returns `SkillCreatorStatus` for legacy CLI banner

## Technology Stack

- **Frontend**: React 18, TypeScript, Vite, Tailwind CSS (utility classes), React Router
- **Backend**: Node.js, custom HTTP router (no Express), SSE streaming
- **LLM Abstraction**: `eval/llm.ts` supporting claude-cli, codex-cli, gemini-cli, anthropic, ollama providers
- **Styling**: CSS custom properties (design tokens), glass-card components, consistent with existing Skill Studio design

**Architecture Decisions**:

1. **SSE over WebSocket for generation streaming**: The generation is a single request-response cycle, not a persistent bidirectional channel. SSE is simpler, works through proxies, and the existing `sse-helpers.ts` infrastructure was already battle-tested for improve/benchmark operations.

2. **Two-mode UI (AI then Manual) over inline editing**: Rather than building a separate AI-only creation flow, generation populates the existing manual form. This reuses all validation, preview, and creation logic, lets users edit any field after generation, and avoids duplicating the manual form.

3. **System prompt embedding best practices over few-shot examples**: The `GENERATE_SYSTEM_PROMPT` uses explicit rules and anti-patterns rather than example skills. This produces more consistent output across diverse skill types and is easier to maintain as best practices evolve.

4. **Heartbeat-based progress over token streaming**: The backend waits for the full LLM response rather than streaming tokens. This simplifies parsing (the response must be valid JSON) and the heartbeat mechanism provides sufficient UX feedback during the 10-30 second generation window.

5. **Eval cap at 10 over unbounded**: LLMs occasionally over-generate when asked for "2-3" items. The `.slice(0, 10)` cap prevents resource waste while being generous enough for edge cases.

## Implementation Phases

### Phase 1: Backend Generation Endpoint
- System prompt for Skill Studio best practices
- `POST /api/skills/generate` with JSON and SSE dual-mode
- Response parser with JSON extraction, code fence stripping, reasoning separation
- Skill name sanitization and validation
- Prompt length validation (10K character limit)
- Error classification integration for SSE error events
- Heartbeat SSE events during LLM calls

### Phase 2: Frontend AI Mode
- Mode toggle (Manual / AI-Assisted) in CreateSkillPage header
- Prompt textarea with Cmd+Enter shortcut
- Provider/model selector dropdowns (from config API)
- SSE streaming consumer with ReadableStream API
- Progress log display during generation
- Form auto-population from generation result
- Mode switch to manual after successful generation
- Cancel button with AbortController

### Phase 3: Generated Content Display
- AI reasoning banner above manual form (dismissible)
- Generated test cases card list with eval name, truncated prompt, assertion badges
- SKILL.md preview panel (sticky right sidebar) in both modes
- Pending evals count badge in reasoning banner

### Phase 4: Create Flow Extension
- Extend `POST /api/skills/create` to accept optional `evals` array
- Write `evals/evals.json` when evals are provided
- Plugin name regex validation for path traversal prevention
- Navigate to new skill workspace after creation

## Testing Strategy

- **Unit tests**: `parseGenerateResponse` (valid JSON, code fences, missing fields, invalid names), `classifyError` (all 7 categories), `buildSkillMd` (frontmatter serialization)
- **Integration tests**: SSE streaming consumer (mock ReadableStream), form population after generation, error display
- **E2E tests**: Full generation flow with mocked LLM response, cancel mid-generation, error recovery
- See tasks.md for detailed BDD test plans per task

## Technical Challenges

### Challenge 1: SSE Parsing in the Frontend
**Solution**: Use `ReadableStream` reader with manual line-by-line SSE parsing (event/data pairs). Buffer partial chunks across reads. Handle both `done` and `complete` event names for compatibility.
**Risk**: Malformed SSE data from network interruption. Mitigated by try/catch around JSON.parse with skip on failure.

### Challenge 2: Non-deterministic LLM Output
**Solution**: Defensive parsing -- strip code fences, handle missing fields with defaults, sanitize skill name aggressively, cap eval array size. The `---REASONING---` separator provides a reliable split point even if the JSON varies.
**Risk**: Completely unparseable response. Mitigated by `parse_error` classification with "Try again" hint and retryable flag.

### Challenge 3: Long LLM Response Times
**Solution**: SSE heartbeat events every 3 seconds during the LLM call. The frontend shows elapsed time in the progress log. AbortController allows cancellation.
**Risk**: Provider timeout (120s for CLI tools). Mitigated by `timeout` error classification with clear messaging.
