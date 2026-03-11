# Architecture Plan: Skill Studio Execution Observability

## Overview

Convert three request/response AI endpoints (improve, generate-evals, generate-skill) to SSE streaming, add error classification, abort support, and ProgressLog UI -- all by reusing the existing SSE infrastructure that already powers benchmark runs.

## Architecture Decisions

### AD-01: Reuse existing SSE infrastructure verbatim

The server already has `sse-helpers.ts` with `initSSE`, `sendSSE`, `sendSSEDone`, and `withHeartbeat`. The client has `useSSE` hook with built-in AbortController support. The `ProgressLog` component renders phase/elapsed entries.

**Decision**: Reuse all three as-is. The only change to `withHeartbeat` is adding an overload that does not require `evalId` (make the parameter optional with a default of `0`). This avoids creating parallel infrastructure.

### AD-02: Three-phase progress model

Every AI operation follows the same lifecycle: build prompt, call LLM, parse response. Rather than inventing per-operation phase names, use a uniform three-phase model.

**Decision**: All three endpoints emit phases in order:
1. `"preparing"` -- building the prompt (system prompt + context assembly)
2. `"generating"` -- LLM call in progress (heartbeats every 3s via `withHeartbeat`)
3. `"parsing"` -- extracting structured result from LLM response

Progress event shape: `{ phase: string, message: string, elapsed_ms: number }`

No `operationId` field -- operations are one-at-a-time per browser session, matching the spec constraint.

### AD-03: Server-side error classification

Errors from LLM providers have wildly different formats: Anthropic API returns structured HTTP errors with status codes, CLI providers dump raw stderr text. Classifying errors on the server keeps the frontend thin.

**Decision**: Create a new module `src/eval-server/error-classifier.ts` that exports:

```typescript
interface ClassifiedError {
  category: "rate_limit" | "context_window" | "auth" | "timeout"
           | "provider_unavailable" | "parse_error" | "unknown";
  title: string;
  description: string;
  hint: string;
  retryAfterMs?: number;
}

function classifyError(err: unknown, provider: ProviderName): ClassifiedError;
```

Classification logic:
- **Anthropic API**: Check HTTP status (429=rate_limit, 401=auth, 413/context mentions=context_window, 503=provider_unavailable)
- **CLI providers**: Regex match on stderr text (e.g., `/rate.limit|429/i`, `/context.*window|token.*limit/i`, `/timed?.?out|120s/i`, `/not found|ENOENT/i`)
- **Ollama**: Check response error text (model not found=provider_unavailable)
- **Parse failures**: JSON.parse errors from response parsing=parse_error
- **Fallback**: Everything else=unknown

### AD-04: SSE error event format

When an error occurs during SSE streaming, send it as a typed SSE event so the frontend can render a structured error card instead of a generic red box.

**Decision**: Errors are emitted as `event: error` with the `ClassifiedError` payload. The `useSSE` hook already handles arbitrary event names. The frontend checks for error events in the stream and renders the `ErrorCard` component.

### AD-05: Abort/cancel via existing AbortController pattern

The `useSSE` hook already exposes a `stop()` method that calls `abortRef.current?.abort()`. On the server side, closing the response terminates the SSE stream. For CLI providers, the spawned child process is still running after the response closes.

**Decision**: Add server-side abort detection using `res.on("close", ...)` (same pattern as benchmark routes). For CLI providers, the spawned process continues until its 120s timeout (acceptable -- the user just does not see the result). No changes to `LlmClient` interface needed; the abort is connection-level.

### AD-06: ErrorCard component (new)

Replace the current inline red error box with a structured card showing category icon, title, description, hint, and Retry button.

**Decision**: Create `src/eval-ui/src/components/ErrorCard.tsx`. For `rate_limit` errors with `retryAfterMs`, include a countdown timer using `setInterval`. All error categories get a Retry button. The card is used in AiEditBar, SkillImprovePanel, TestsPanel (generate evals), and CreateSkillPage (generate skill).

### AD-07: API client migration strategy

Currently `api.ts` uses `fetchJson()` for improve, generateEvals, and generateSkill. These must switch to SSE.

**Decision**: Do NOT change `api.ts` methods. Instead, the calling components (WorkspaceContext, SkillImprovePanel, CreateSkillPage) will use `useSSE` directly. The `api.ts` methods for these three operations become dead code and can be removed in a follow-up. This avoids changing the API client abstraction and keeps changes local to the components that consume the data.

Rationale: `useSSE` returns `{ events, running, done, error, start, stop }`. The calling component accumulates progress events for ProgressLog and extracts the final result from the `done` event. This is the same pattern the workspace already uses for activation tests.

### AD-08: WorkspaceState changes for AI operation progress

The workspace reducer needs new state fields for AI operation progress events (for ProgressLog) and structured errors.

**Decision**: Add to `WorkspaceState`:

```
aiEditProgress: ProgressEntry[]
generateEvalsLoading: boolean
generateEvalsProgress: ProgressEntry[]
generateEvalsError: ClassifiedError | null
```

New reducer actions:
- `AI_EDIT_PROGRESS` -- append progress entry
- `GENERATE_EVALS_START` / `GENERATE_EVALS_PROGRESS` / `GENERATE_EVALS_DONE` / `GENERATE_EVALS_ERROR`

For SkillImprovePanel and CreateSkillPage, since they manage their own local state (not workspace reducer), they will use `useSSE` directly with local `useState` for progress entries.

## Component Boundaries

### Server-Side Changes

```
src/eval-server/
  error-classifier.ts          [NEW]  Error classification logic
  sse-helpers.ts                [MOD]  Make evalId optional in withHeartbeat
  improve-routes.ts             [MOD]  Convert to SSE with phases + error classification
  api-routes.ts                 [MOD]  Convert generate-evals to SSE with phases
  skill-create-routes.ts        [MOD]  Convert generate-skill to SSE with phases
```

### Client-Side Changes

```
src/eval-ui/src/
  components/
    ErrorCard.tsx               [NEW]  Structured error card with category, hint, retry
    ProgressLog.tsx              [MOD]  Add support for phases without evalId
    AiEditBar.tsx                [MOD]  Add ProgressLog, ErrorCard, Cancel button, useSSE
    SkillImprovePanel.tsx        [MOD]  Add ProgressLog, ErrorCard, useSSE
  pages/
    workspace/
      workspaceTypes.ts          [MOD]  New state fields + actions for progress tracking
      workspaceReducer.ts        [MOD]  Handle new progress/error actions
      WorkspaceContext.tsx        [MOD]  Wire SSE for AI edit and generate evals
      TestsPanel.tsx              [MOD]  Wire SSE for generate evals with ProgressLog
    CreateSkillPage.tsx           [MOD]  Wire SSE for generate skill with ProgressLog + ErrorCard
  types.ts                       [MOD]  Add ClassifiedError type
  api.ts                         [NO CHANGE]  Keep existing methods (deprecated later)
```

## Data Flow

### SSE Endpoint Flow (all three endpoints follow the same pattern)

```
Client POST /api/.../improve
  |
  v
Server: initSSE(res, req)
  |
  v
sendSSE(res, "progress", { phase: "preparing", message: "Building prompt...", elapsed_ms: 0 })
  |
  v
[Build system prompt + user prompt]
  |
  v
sendSSE(res, "progress", { phase: "generating", message: "Calling LLM...", elapsed_ms: N })
  |
  v
withHeartbeat(res, 0, "generating", "Calling LLM", async () => {
  return client.generate(systemPrompt, userPrompt);
})
  |                    |
  |  (every 3s)        |
  v                    v
sendSSE "progress"    LLM returns
  |
  v
sendSSE(res, "progress", { phase: "parsing", message: "Extracting result...", elapsed_ms: N })
  |
  v
[Parse response, split reasoning]
  |
  v
sendSSEDone(res, { original, improved, reasoning })
  |
  v
Connection closed
```

### Error Flow

```
LLM call throws
  |
  v
classifyError(err, provider) -> ClassifiedError
  |
  v
sendSSE(res, "error", classifiedError)
  |
  v
res.end()
```

### Client-Side Flow

```
useSSE.start(url, body)
  |
  v
SSE events arrive
  |
  +-- event: "progress" --> append to progressEntries[] --> ProgressLog renders
  |
  +-- event: "error" --> setClassifiedError(data) --> ErrorCard renders
  |
  +-- event: "done" --> extract result payload --> render diff/evals/skill
  |
  v
useSSE.stop() on Escape/Cancel --> AbortController.abort() --> connection drops
```

## Endpoint Conversion Details

### /api/skills/:plugin/:skill/improve (improve-routes.ts)

Current: `sendJson(res, { original, improved, reasoning }, 200, req)`
After:
1. `initSSE(res, req)` -- switch from JSON to SSE
2. Emit `preparing` phase while building prompt
3. Wrap `client.generate()` in `withHeartbeat()` for `generating` phase
4. Emit `parsing` phase while splitting response
5. `sendSSEDone(res, { original, improved, reasoning })` -- final result
6. Catch block: `classifyError(err, provider)` then `sendSSE(res, "error", classified)` then `res.end()`

Both `mode: "auto"` and `mode: "instruct"` follow the same SSE pattern. The only difference is prompt construction (which happens in the `preparing` phase).

### /api/skills/:plugin/:skill/generate-evals (api-routes.ts)

Current: `sendJson(res, evalsFile, 200, req)`
After:
1. `initSSE(res, req)`
2. `preparing` phase -- reading SKILL.md, building eval init prompt
3. `generating` phase with heartbeat -- `client.generate()`
4. `parsing` phase -- `parseGeneratedEvals(genResult.text)`
5. `sendSSEDone(res, evalsFile)`
6. Error: classify and emit error event

### /api/skills/generate (skill-create-routes.ts)

Current: `sendJson(res, parsed, 200, req)`
After:
1. `initSSE(res, req)`
2. `preparing` phase -- constructing user prompt from description
3. `generating` phase with heartbeat -- `client.generate()`
4. `parsing` phase -- `parseGenerateResponse(result.text)`
5. `sendSSEDone(res, parsed)`
6. Error: classify and emit error event

## Error Classification Matrix

```
Category               Trigger Patterns                                    Hint
--------------------   -------------------------------------------------   ----------------------------------
rate_limit             HTTP 429, /rate.limit/i, /too many requests/i        "Wait N seconds and retry"
context_window         HTTP 413, /context.*window|token.*limit|too long/i   "Reduce SKILL.md content or use a larger model"
auth                   HTTP 401/403, /api.key|unauthorized|forbidden/i      "Check API key configuration"
timeout                /timed?.?out|120s|SIGTERM/i                          "Operation took too long -- try a simpler prompt"
provider_unavailable   HTTP 503, /ENOENT|not found|not running/i            "Provider not available -- check installation"
parse_error            JSON.parse failure, /not valid JSON/i                "AI response was malformed -- try again"
unknown                Everything else                                      "An unexpected error occurred"
```

## ProgressLog Adaptation

The existing `ProgressLog` component uses `ProgressEntry` with `evalId: number`. For AI operations, there is no eval ID.

**Decision**: Make `evalId` optional in `ProgressEntry` (change to `evalId?: number`). The display logic already ignores it -- it only uses `phase` and `message`. The `phaseIcon` function already handles `"generating"` phase. Add `"preparing"` and `"parsing"` to the phase icon logic.

## Cancel/Abort Flow (US-004)

1. AiEditBar: Escape key calls `useSSE.stop()` which triggers `AbortController.abort()`
2. The fetch request is cancelled, SSE stream drops
3. Server detects `res.on("close")` -- heartbeat timer is cleared by `withHeartbeat`'s `finally` block
4. For CLI providers: the spawned process continues until its 120s timeout (acceptable -- the user just does not see the result)
5. UI: `useSSE` sets `running = false` on AbortError (already handled in existing code)
6. AiEditBar returns to instruction input with text preserved (store instruction in state before starting SSE)
7. Submit button shows "Cancel" text while `running === true`

## Implementation Order

1. `error-classifier.ts` -- pure logic, no dependencies, fully testable
2. `sse-helpers.ts` -- make evalId optional in withHeartbeat
3. `ProgressLog.tsx` -- make evalId optional, add preparing/parsing phase icons
4. `ErrorCard.tsx` -- new component, no dependencies on server changes
5. `improve-routes.ts` -- convert to SSE (both auto and instruct modes)
6. `AiEditBar.tsx` + `WorkspaceContext.tsx` -- wire SSE for AI edit
7. `api-routes.ts` -- convert generate-evals to SSE
8. `WorkspaceContext.tsx` + `TestsPanel.tsx` -- wire SSE for generate evals
9. `skill-create-routes.ts` -- convert generate-skill to SSE
10. `CreateSkillPage.tsx` -- wire SSE for generate skill
11. `SkillImprovePanel.tsx` -- wire SSE for auto-improve
12. `workspaceTypes.ts` + `workspaceReducer.ts` -- state additions for progress tracking

## Testing Strategy

### Unit Tests

- `error-classifier.test.ts`: All 7 error categories with provider-specific inputs (Anthropic HTTP errors, CLI stderr patterns, Ollama responses). Edge cases: empty stderr, combined error messages.
- `sse-helpers.test.ts`: withHeartbeat with optional evalId, verify progress events contain phase/message/elapsed_ms.

### Integration Tests

- Each converted endpoint: verify SSE headers, verify three phases emitted in order, verify done event contains full payload, verify error events contain ClassifiedError shape.
- Abort test: start SSE stream, abort mid-flight, verify server cleans up (no dangling intervals).

### Component Tests (Vitest + React Testing Library)

- `ErrorCard.test.tsx`: Render each error category, verify icon/title/hint/retry button. For rate_limit, verify countdown timer decrements.
- `ProgressLog.test.tsx`: Verify rendering with optional evalId entries.
- `AiEditBar.test.tsx`: Verify Cancel button appears during loading, Escape triggers abort, instruction text preserved after cancel.

## Risks and Mitigations

| Risk | Mitigation |
|------|-----------|
| CLI process not killed on abort | Acceptable -- 120s timeout handles cleanup. Process runs in background, result discarded. |
| Breaking existing benchmark SSE | No changes to benchmark-runner.ts or its SSE flow. Only withHeartbeat signature changes (backward compatible with optional param). |
| Race condition: new request while previous SSE closing | useSSE.start() resets state. AbortController from previous request is replaced. |
| SSE buffering by reverse proxy | Already handled -- initSSE sets X-Accel-Buffering: no header. |
