# Architecture Plan: AI-Assisted Skill Authoring in Skill Studio

## Overview

Port the AI-assisted skill generation UX from the standalone `CreateSkillPage.tsx` into the inline `CreateSkillInline.tsx` component. This is a **single-component refactor** -- no new files, no new hooks, no backend changes. The inline component gains a mode toggle, SSE streaming, progress/error display, and reasoning review while preserving the existing manual flow.

## Decision: Single-File Modification vs. Extraction

### Option A: Modify `CreateSkillInline.tsx` in-place (CHOSEN)

Add AI state, SSE handler, mode toggle, and conditional rendering directly to the existing component.

**Rationale**:
- The standalone `CreateSkillPage.tsx` (852 lines) handles the same concerns in a single file and works well
- All shared sub-components (`ProgressLog`, `ErrorCard`) already exist
- The inline variant is simpler (no preview panel, no provider/model pickers, no breadcrumbs)
- Estimated final size: ~450-500 lines -- well under the 1500-line limit
- Extracting a custom hook (`useAiGeneration`) would only save ~60 lines and create an abstraction barrier for code used in exactly one place

**Trade-offs**:
- Component grows from 278 to ~480 lines (acceptable)
- If a third AI generation surface is added later, extraction would become worthwhile

### Option B: Extract `useAiGeneration` hook (REJECTED)

Factor SSE streaming, abort, progress, and error state into a shared hook used by both pages.

**Why rejected**:
- Two consumers is not enough to justify the indirection
- The standalone page has provider/model selection state interleaved with generation state -- splitting cleanly would require rethreading props
- YAGNI -- spec explicitly scopes out changes to `CreateSkillPage.tsx`

## Component Design

### State Additions to `CreateSkillInline`

```
Existing state (kept as-is):
  layout, layoutLoading, config
  name, selectedLayout, plugin, newPlugin, description, model, allowedTools, body
  creating, error

Removed state:
  creatorStatus                   -- no longer needed (banner removed)

New state:
  mode: "manual" | "ai"           -- toggle between manual form and AI prompt
  aiPrompt: string                -- user's natural language description
  generating: boolean             -- SSE stream in flight
  aiReasoning: string | null      -- reasoning text from completed generation
  aiError: string | null          -- inline error message
  aiClassifiedError: ClassifiedError | null  -- structured error for ErrorCard
  aiProgress: ProgressEntry[]     -- SSE progress events
  pendingEvals: GeneratedEval[] | null      -- test cases from generation

New refs:
  promptRef: RefObject<HTMLTextAreaElement>  -- auto-focus on mode switch
  abortRef: RefObject<AbortController | null> -- cancel SSE stream
```

### Data Flow

```
User types prompt
       |
       v
[Generate Skill] click
       |
       v
fetch("/api/skills/generate?sse", { prompt, signal })
       |
       +-- SSE "progress" events --> append to aiProgress[] --> <ProgressLog>
       |
       +-- SSE "done" event --> populate form fields (name, description,
       |                        model, allowedTools, body, evals, reasoning)
       |                        --> switch mode to "manual" for review
       |
       +-- SSE "error" event --> set aiError / aiClassifiedError --> <ErrorCard>
       |
       +-- AbortError (cancel) --> reset generating state
       |
       v
Manual mode shows populated form + reasoning banner
       |
       v
[Create Skill] click --> api.createSkill({ ...fields, evals }) --> onCreated()
```

### Rendering Structure

```
<div> (root)
  <header>
    <h2>Create a New Skill</h2>
    <ModeToggle manual|ai />           <-- replaces old passive banner
  </header>

  {mode === "ai" && (
    <AiPromptSection>
      <textarea prompt />
      {generating && <ProgressLog />}
      {aiError && (aiClassifiedError ? <ErrorCard /> : <InlineError />)}
      <GenerateButton | CancelButton>
    </AiPromptSection>
  )}

  {mode === "manual" && (
    <>
      {aiReasoning && <ReasoningBanner />}
      <LocationCard />          (existing, unchanged)
      <SkillDetailsCard />      (existing, unchanged)
      <SystemPromptCard />      (existing, unchanged)
      {error && <InlineError />}
      <CreateButton + CancelButton>
    </>
  )}
</div>
```

### Key Adaptations from CreateSkillPage

| CreateSkillPage (standalone) | CreateSkillInline (this increment) |
|---|---|
| `useNavigate()` + `<Link to="/">` | `onCreated()` / `onCancel()` callbacks |
| Provider/model selector UI | Omit -- use defaults from config |
| Side-by-side SKILL.md preview | Omit -- inline panel is single-column |
| Breadcrumb navigation | Omit -- inline context |
| `skillMdPreview` computed value | Omit -- no preview panel |
| Purple accent `#a855f7` for AI elements | Keep -- consistent AI branding |
| `SparkleIcon` SVG component | Copy inline (same 4-line SVG, local to file) |

### What Gets Removed

- The `showCreatorBanner` conditional block (lines 76, 114-136) -- replaced by the mode toggle
- The `creatorStatus` state and `api.getSkillCreatorStatus()` call -- no longer needed

### What Stays Unchanged

- All form fields, validation, and `handleCreate()` logic
- Layout detection, plugin selection, path preview
- The `onCreated` / `onCancel` callback interface (Props type unchanged)
- All existing CSS classes and style patterns

## Import Changes

```diff
- import { useState, useEffect, useMemo } from "react";
+ import { useState, useEffect, useMemo, useRef, useCallback } from "react";
  import { api } from "../api";
  import type { ConfigResponse } from "../api";
- import type { ProjectLayoutResponse, DetectedLayout, SkillCreatorStatus } from "../types";
+ import type { ProjectLayoutResponse, DetectedLayout, GeneratedEval } from "../types";
+ import { ProgressLog } from "./ProgressLog";
+ import type { ProgressEntry } from "./ProgressLog";
+ import { ErrorCard } from "./ErrorCard";
+ import type { ClassifiedError } from "./ErrorCard";
```

## SSE Streaming Implementation

Direct port from `CreateSkillPage.handleGenerate()`:

1. Create `AbortController`, store in `abortRef`
2. `fetch("/api/skills/generate?sse", { method: "POST", body: { prompt }, signal })`
3. Read `res.body` as `ReadableStream` with `TextDecoder`
4. Parse SSE lines: `event: <type>` + `data: <json>`
5. Route events: `progress` -> append to array, `done`/`complete` -> populate form + switch mode, `error` -> display
6. Cleanup: abort on unmount via `useEffect` return

Provider/model defaults: read from `config` state (already fetched on mount). Use first available provider's first model, falling back to `"claude-cli"` / `"sonnet"`.

## Error Handling Strategy

Three tiers, matching `CreateSkillPage`:

1. **Empty prompt validation**: Inline error "Describe what your skill should do" -- no API call (AC-US5-04)
2. **Classified errors** (SSE `error` event with `category`): Render `<ErrorCard>` with retry button (AC-US5-01)
3. **Unclassified errors** (network failures, HTTP errors, malformed SSE): Simple inline error div (AC-US5-02)

All errors display a "Retry" affordance that re-calls `handleGenerate()` with the same prompt (AC-US5-03).

## Testing Strategy

TDD mode (spec requires it). Test file: `src/eval-ui/src/components/__tests__/CreateSkillInline.test.tsx`

### Unit Tests (Vitest + React Testing Library)

1. **Mode toggle rendering**: Default is manual; clicking AI-Assisted shows prompt area; clicking Manual restores form
2. **Banner removal**: Assert no "Run /skill-creator" text in rendered output
3. **Empty prompt validation**: Click generate with empty textarea -> shows inline error, no fetch call
4. **Generate button disabled state**: Disabled when prompt is empty
5. **SSE streaming mock**: Mock fetch to return ReadableStream with progress/done events -> verify form fields populated
6. **Cancel generation**: Mock fetch with never-resolving stream -> click cancel -> verify AbortController.abort() called
7. **Error display (classified)**: Mock SSE error event with category -> verify ErrorCard renders
8. **Error display (unclassified)**: Mock fetch rejection -> verify inline error message
9. **Retry**: After error, click retry -> verify fetch called again
10. **Reasoning banner**: After successful generation, verify reasoning banner visible in manual mode with dismiss button
11. **Pending evals**: After generation with evals, verify eval count badge in reasoning banner
12. **Manual mode preservation**: Fill form fields, create skill -> verify api.createSkill called with correct args, no AI calls

### Mock Strategy

- Mock `fetch` globally for SSE tests (ReadableStream with encoded SSE lines)
- Mock `api.getProjectLayout()`, `api.getConfig()`, `api.createSkill()` via `vi.mock("../api")`
- Use `vi.hoisted()` for ESM-compatible mocking

## File Size Estimate

| Section | Lines |
|---|---|
| Imports + helpers (existing) | 25 |
| SparkleIcon (new) | 10 |
| State declarations (existing + new) | 30 |
| useEffect hooks (existing + new cleanup) | 25 |
| Computed values (existing) | 20 |
| handleGenerate (new) | 65 |
| handleCancelGenerate (new) | 5 |
| handleCreate (existing, +evals) | 20 |
| JSX: header + toggle | 30 |
| JSX: AI mode section | 60 |
| JSX: manual mode (existing, +reasoning banner) | 180 |
| JSX: loading state | 5 |
| **Total** | **~475** |

## Risks and Mitigations

| Risk | Mitigation |
|---|---|
| SSE parsing edge cases (partial chunks, malformed JSON) | Identical parsing logic to CreateSkillPage which is already production-tested |
| Component exceeds comfortable reading size | At ~475 lines it is well within the 1500-line limit and comparable to CreateSkillPage's 852 lines |
| Config not loaded when user clicks Generate | Use hardcoded fallback (claude-cli/sonnet) if config is null -- matches CreateSkillPage behavior |

## Implementation Order

1. Add imports, SparkleIcon, new state/refs
2. Remove banner block and creatorStatus-related code
3. Add handleGenerate, handleCancelGenerate, unmount cleanup
4. Add mode toggle to header
5. Add AI mode JSX section (prompt, progress, error, generate/cancel buttons)
6. Add reasoning banner to manual mode section
7. Modify handleCreate to include pendingEvals
8. Write tests

## Domain Skill Delegation

Not needed. This is a single React component modification with no routing, state management library, design system, or backend changes. The complexity is medium-low and falls below the threshold for domain skill invocation per the complexity gate.
