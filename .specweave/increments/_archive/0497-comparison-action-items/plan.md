# Implementation Plan: Comparison Action Items Engine

## Overview

Post-comparison LLM analysis that transforms raw A/B comparison results into structured, actionable recommendations. Appends one additional LLM call to the existing compare pipeline, surfaces results in a new UI panel below the verdict card, and connects to the existing `/improve` infrastructure via an "Apply AI Fix" button.

## Architecture

### Data Flow

```
Compare endpoint (api-routes.ts)
  |
  |  1. Run A/B comparison (existing)
  |  2. Compute verdict (existing)
  v
  3. generateActionItems() -- NEW LLM call
  |     Input: verdict + comparison stats + per-case breakdown + SKILL.md content
  |     Output: ActionItems { recommendation, summary, weaknesses, strengths, suggestedFocus }
  |     Wrapped in withHeartbeat() for SSE progress ("action_items" phase)
  |     Non-fatal: comparison result is valid even if this call fails
  v
  4. Attach actionItems to BenchmarkResult
  |
  v
  5. SSE done event -> ComparisonPage renders ActionItemsPanel
  |
  v
  6. "Apply AI Fix" -> navigates to /workspace/:plugin/:skill?improve=true&notes=...
```

### Components

#### 1. Action Items Engine (`src/eval/action-items.ts`)

Pure function module -- no side effects, no file I/O. Takes comparison data in, returns structured recommendations out.

- **`generateActionItems(client, verdict, stats, cases, skillContent)`** -- orchestrator function. Builds prompt, calls LLM, parses response.
- **`buildUserPrompt(verdict, stats, cases, skillContent)`** -- assembles structured context for the LLM. Truncates SKILL.md to 2000 chars to avoid token bloat.
- **`parseActionItems(raw)`** -- defensive JSON parser with fallback. Handles code-fenced and raw JSON responses. Returns safe defaults on parse failure.

LLM prompt design decisions:
- System prompt defines the evaluator role, JSON schema, and recommendation criteria thresholds (keep >= 80% pass rate + delta > +1, remove = baseline consistently wins, etc.)
- User prompt provides verdict, aggregate stats, per-case breakdown with failed assertions, and truncated SKILL.md
- JSON-only response format (no code fences requested, but parser handles them anyway)

#### 2. Type Extensions (`src/eval/benchmark.ts`)

Two new types added to the shared benchmark type system:

```typescript
type ActionRecommendation = "keep" | "improve" | "rewrite" | "remove";

interface ActionItems {
  recommendation: ActionRecommendation;
  summary: string;          // 1-2 sentence overview
  weaknesses: string[];     // Specific, eval-case-referencing weaknesses
  strengths: string[];      // Specific strengths
  suggestedFocus: string;   // Single most impactful improvement
}
```

Added as optional field `actionItems?: ActionItems` on `BenchmarkResult`. Optional because: (a) only comparison runs produce action items, (b) the LLM call is non-fatal.

#### 3. Frontend Type Mirror (`src/eval-ui/src/types.ts`)

Duplicated `ActionRecommendation` and `ActionItems` types in the eval-ui type system. The frontend has its own type file to avoid tsconfig cross-contamination between Node.js ESM backend and Vite React frontend.

#### 4. Server Integration (`src/eval-server/api-routes.ts`)

Wired into the existing compare endpoint after verdict computation:

- Maps `comparisonResults` to the `CaseResult[]` shape expected by the engine
- Wraps `generateActionItems()` in `withHeartbeat(res, undefined, "action_items", "Generating recommendations", ...)` for SSE progress
- Catch block sets `actionItems = undefined` on failure -- non-fatal, comparison result is still complete
- Spreads `actionItems` into the `BenchmarkResult` before `writeHistoryEntry()` and `sendSSEDone()`

#### 5. ActionItemsPanel (`src/eval-ui/src/components/ActionItemsPanel.tsx`)

React component rendered below the verdict card in `ComparisonPage.tsx`:

- Color-coded recommendation badge (green=keep, yellow=improve, orange=rewrite, red=remove)
- Summary text
- Two-column grid: weaknesses (red dots) and strengths (green dots)
- "Suggested Focus" callout box
- "Apply AI Fix" button (shown only for "improve" and "rewrite" recommendations)
  - Navigates to `/workspace/:plugin/:skill?improve=true&notes=<encoded context>`
  - Reuses existing improve infrastructure -- no new backend endpoint needed

#### 6. Progress Log Phase (`src/eval-ui/src/components/ProgressLog.tsx`)

Added `"action_items"` to both `spinnerPhases` and `accentPhases` sets so the SSE heartbeat messages render with a spinner during the LLM call and an accent checkmark when complete.

#### 7. API Client 404 Fix (`src/eval-ui/src/api.ts`)

`getLatestBenchmark()` now returns `null` for HTTP 404 instead of throwing, eliminating console error noise when a skill has no benchmark history.

### Data Model

No new persistence. `ActionItems` is embedded in the existing `BenchmarkResult` JSON structure and persisted via the existing `writeHistoryEntry()` mechanism to the skill's `evals/` directory.

### API Contracts

No new endpoints. The existing SSE compare endpoint (`POST /api/skills/:plugin/:skill/compare`) now includes `actionItems` in its final `done` event payload.

## Technology Stack

- **Runtime**: Node.js ESM (existing)
- **LLM Client**: Existing `LlmClient` abstraction (`src/eval/llm.ts`) -- model-agnostic, supports OpenAI/Anthropic/Google providers
- **Frontend**: React + Vite (existing eval-ui)
- **Transport**: SSE with heartbeat (existing `withHeartbeat` helper)

**Architecture Decisions**:
- **Inline LLM call vs. separate endpoint**: Chose inline (within compare flow) to avoid extra round-trip and keep the action items atomically tied to the comparison result. Trade-off: slightly longer compare time, but the SSE heartbeat keeps the UI responsive.
- **Non-fatal design**: Action items generation failure does not invalidate the comparison. The UI conditionally renders the panel only when `doneData.actionItems` is present.
- **Type duplication (backend/frontend)**: Maintained separate type files rather than sharing a package. The backend uses `--moduleResolution nodenext` with `.js` extensions while the frontend uses Vite's module resolution. Shared types would require a build step that adds complexity without proportional benefit.
- **Prompt truncation at 2000 chars**: Prevents token bloat from large SKILL.md files while preserving enough context for meaningful analysis. The truncation point is generous enough for most skills.
- **Navigation-based "Apply AI Fix"**: Reuses the existing workspace improve infrastructure via query params rather than building a new dedicated endpoint. Keeps the action items feature lightweight.

## Implementation Phases

### Phase 1: Core Engine
- Define `ActionItems` and `ActionRecommendation` types on `BenchmarkResult`
- Implement `action-items.ts` with prompt construction, LLM call, and defensive JSON parsing
- Mirror types in eval-ui

### Phase 2: Server Integration
- Wire `generateActionItems()` into compare endpoint
- Add `action_items` SSE heartbeat phase
- Handle non-fatal failure

### Phase 3: UI
- Build `ActionItemsPanel` component
- Integrate into `ComparisonPage`
- Add progress log phase support
- Implement "Apply AI Fix" navigation

### Phase 4: Polish
- Fix `getLatestBenchmark()` 404 handling
- Verify end-to-end SSE flow with action items phase

## Testing Strategy

- **Unit tests**: `action-items.ts` -- prompt construction, JSON parsing (valid, code-fenced, malformed), recommendation threshold mapping
- **Integration**: Compare endpoint produces `actionItems` in SSE done event
- **UI**: ActionItemsPanel renders all recommendation states, "Apply AI Fix" generates correct navigation URL

## Technical Challenges

### Challenge 1: LLM Response Reliability
**Solution**: Defensive `parseActionItems()` that handles code-fenced JSON, raw JSON, and returns safe defaults on any parse failure. Validates recommendation against the allowed set and falls back to "improve".
**Risk**: Low -- the fallback is graceful and the feature is explicitly non-fatal.

### Challenge 2: Token Budget for SKILL.md
**Solution**: Truncate skill content to 2000 characters in the prompt. The system prompt and per-case breakdown consume the bulk of useful context; the full skill content is less critical than the comparison data.
**Risk**: Very large skills may lose context. Mitigation: the truncation boundary is tunable and the prompt already includes the most actionable data (scores, failed assertions).
