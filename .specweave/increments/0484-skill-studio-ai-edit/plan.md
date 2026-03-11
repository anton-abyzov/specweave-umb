# Implementation Plan: Skill Studio AI Edit Feature

## Overview

Add a freeform "AI Edit" capability to the Skill Studio workspace, letting authors type a natural-language instruction (e.g., "add error handling section") and receive a diffed preview before applying. The design extends the existing `/improve` endpoint with a new `mode: "instruct"` parameter on the backend, and adds a lightweight `AiEditBar` component plus five new reducer actions on the frontend. No new endpoints, no new API routes, no new dependencies.

## Architecture

### Data Flow

```
User types instruction in AiEditBar
        |
        v
api.instructEdit(plugin, skill, { instruction, content, provider?, model? })
        |
        v
POST /api/skills/:plugin/:skill/improve  { mode: "instruct", instruction, content, provider?, model? }
        |
        v
improve-routes.ts: mode branch
  - "instruct" -> instruction-focused system prompt + user content
  - default    -> existing benchmark-failure improvement flow (unchanged)
        |
        v
createLlmClient({ provider, model }).generate(systemPrompt, userPrompt)
        |
        v
Parse ---REASONING--- separator -> { improved, reasoning }
        |
        v
Response: { original: content, improved, reasoning }
        |
        v
Frontend: dispatch AI_EDIT_RESULT -> computeDiff(content, improved) -> show diff panel
        |
        v
User clicks Apply -> dispatch SET_CONTENT + api.applyImprovement -> save to disk
User clicks Discard -> dispatch CLOSE_AI_EDIT -> reset state
```

### Components

- **improve-routes.ts (backend)**: Extended with `mode: "instruct"` branch. When mode is "instruct", uses a focused system prompt that applies the user's instruction verbatim against the provided `content` field. Skips benchmark failure context entirely. Records history entry with `type: "instruct"`.

- **AiEditBar.tsx (new frontend component)**: Inline prompt bar rendered at the bottom of EditorPanel when `state.aiEditOpen === true`. Contains: auto-focused textarea, submit button, loading spinner, error display, Escape-to-dismiss handler. Approximately 80-120 lines. Located at `src/eval-ui/src/components/AiEditBar.tsx`.

- **workspaceTypes.ts (extended)**: Five new fields on `WorkspaceState`, five new action types on `WorkspaceAction`, new method on `WorkspaceContextValue`.

- **workspaceReducer.ts (extended)**: Five new case handlers for the AI edit actions.

- **WorkspaceContext.tsx (extended)**: New `submitAiEdit` async action that calls `api.instructEdit`, dispatches loading/result/error actions.

- **EditorPanel.tsx (extended)**: Toolbar gets an "AI Edit" button. Cmd/Ctrl+K shortcut registered. AiEditBar rendered conditionally. Diff panel rendered below editor when result is available (reuses `computeDiff` and the same diff rendering pattern from SkillImprovePanel).

- **api.ts (extended)**: New `instructEdit` method that calls the same `/improve` endpoint with `mode: "instruct"`.

### State Design

New fields added to `WorkspaceState`:

```
aiEditOpen: boolean          // prompt bar visible
aiEditLoading: boolean       // request in-flight
aiEditResult: {              // LLM response (null when no result)
  improved: string
  reasoning: string
} | null
aiEditError: string | null   // error message
```

New actions added to `WorkspaceAction`:

```
OPEN_AI_EDIT     -> { aiEditOpen: true, aiEditError: null, aiEditResult: null }
CLOSE_AI_EDIT    -> { aiEditOpen: false, aiEditLoading: false, aiEditResult: null, aiEditError: null }
AI_EDIT_LOADING  -> { aiEditLoading: true, aiEditError: null }
AI_EDIT_RESULT   -> { aiEditLoading: false, aiEditResult: { improved, reasoning } }
AI_EDIT_ERROR    -> { aiEditLoading: false, aiEditError: message }
```

New method on `WorkspaceContextValue`:

```
submitAiEdit: (instruction: string) => Promise<void>
```

### API Contract

**Endpoint**: `POST /api/skills/:plugin/:skill/improve` (existing, extended)

**New request fields** (additive, backward-compatible):

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| mode | `"instruct"` | No | Enables freeform instruction mode. Omit for existing behavior. |
| instruction | string | When mode=instruct | The natural-language edit instruction |
| content | string | When mode=instruct | Current editor content (including unsaved changes) |
| provider | string | No | LLM provider override |
| model | string | No | Model override |

**Response**: Same `{ original, improved, reasoning }` shape as existing improve endpoint.

**Backward compatibility**: When `mode` is omitted or any value other than `"instruct"`, the handler falls through to the existing benchmark-failure improvement logic. Zero breaking changes.

### Backend: Instruct Mode System Prompt

The instruct-mode system prompt is narrowly scoped:

```
You are an AI skill editor. The user has provided a SKILL.md file and a specific
instruction for how to modify it. Apply the instruction precisely. Do not make
other changes beyond what the instruction asks for.

Return the full modified SKILL.md content followed by ---REASONING--- and a brief
explanation of what you changed.
```

This contrasts with the existing improve system prompt which applies opinionated best-practice improvements. The instruct prompt is intentionally minimal to give the user precise control.

### Frontend: AiEditBar Interaction Model

1. User clicks "AI Edit" toolbar button OR presses Cmd/Ctrl+K
2. `OPEN_AI_EDIT` dispatched -> prompt bar appears with auto-focused textarea
3. User types instruction, presses Enter or clicks submit
4. `AI_EDIT_LOADING` dispatched -> button disabled, spinner shown
5. `submitAiEdit(instruction)` calls `api.instructEdit(plugin, skill, { instruction, content: state.skillContent })`
6. On success: `AI_EDIT_RESULT` dispatched -> diff panel appears below editor (reasoning box + unified diff + Apply/Discard buttons)
7. On error: `AI_EDIT_ERROR` dispatched -> error shown in prompt bar area
8. Apply: `SET_CONTENT` with improved content + `api.applyImprovement` + `CONTENT_SAVED` + `CLOSE_AI_EDIT`
9. Discard: `CLOSE_AI_EDIT` -> everything reset
10. Escape at any point: `CLOSE_AI_EDIT`

### Key Constraint: Content Source

The `content` field sent to the backend is always `state.skillContent` (current in-editor text, including unsaved edits), NOT the disk version. This matches the spec requirement and ensures the AI operates on exactly what the user sees.

## Technology Stack

- **Backend**: Node.js, existing eval-server router, existing `createLlmClient` + `---REASONING---` parsing
- **Frontend**: React (existing eval-ui), `useReducer` pattern (existing WorkspaceContext), `computeDiff` utility (existing)
- **No new dependencies**: Everything needed already exists in the codebase

## Architecture Decisions

### AD-1: Extend existing /improve endpoint vs. new endpoint

**Decision**: Extend with `mode: "instruct"` parameter.

**Rationale**: The improve endpoint already has the full infrastructure (LLM client creation, `---REASONING---` parsing, history recording, error handling). A new endpoint would duplicate all of this. The mode parameter creates a clean branch point at the prompt construction step, which is the only meaningful difference.

**Trade-off**: Slightly larger handler function (~30 lines added). Acceptable given the alternative is a separate 100+ line file duplicating infrastructure.

### AD-2: Separate AiEditBar component vs. extending SkillImprovePanel

**Decision**: New `AiEditBar` component.

**Rationale**: SkillImprovePanel serves a different purpose (opinionated best-practice improvements with model picker UI). AiEditBar is an inline prompt bar -- different layout, different interaction model, different visual weight. Cramming both into one component would violate single responsibility and create confusing conditional rendering. However, the diff rendering logic in the result view reuses the same `computeDiff` utility and visual pattern.

### AD-3: Diff rendering location

**Decision**: Diff panel renders inside EditorPanel (below the editor area, same as current SkillImprovePanel placement).

**Rationale**: The spec says "a bottom panel (same pattern as the existing SkillImprovePanel)". Keeping the diff in the same visual location maintains consistency. The diff rendering code (color-coded lines, reasoning box, Apply/Discard buttons) is extracted inline rather than shared as a component, because the SkillImprovePanel manages its own local state (model picker, improve request) while AiEditBar uses workspace reducer state. The visual pattern is the same, but the data sources differ.

### AD-4: Keyboard shortcut scope

**Decision**: Cmd/Ctrl+K registered at the EditorPanel level (not window-global).

**Rationale**: SkillWorkspace already registers window-level Ctrl+1..6 and Ctrl+S shortcuts. Adding Ctrl+K at window level would conflict if other panels eventually want it. Scoping to EditorPanel ensures the shortcut only fires when the editor tab is active, which matches user expectation. The shortcut only opens the bar; it does not toggle (pressing Ctrl+K when bar is open does nothing, Escape closes it).

## Implementation Phases

### Phase 1: Backend (improve-routes.ts)

- Add `mode`, `instruction`, `content` to the request body type
- Add mode branch: when `mode === "instruct"`, use instruction-focused system prompt with provided content
- Record history with `type: "instruct"`
- Validate: instruction must be non-empty when mode is instruct

### Phase 2: Frontend State (workspaceTypes.ts, workspaceReducer.ts)

- Add 4 new state fields to `WorkspaceState`
- Add 5 new action types to `WorkspaceAction`
- Add reducer cases
- Add `submitAiEdit` to `WorkspaceContextValue`

### Phase 3: Frontend API + Context (api.ts, WorkspaceContext.tsx)

- Add `api.instructEdit()` method
- Add `submitAiEdit` async callback in WorkspaceContext

### Phase 4: Frontend UI (AiEditBar.tsx, EditorPanel.tsx)

- Create AiEditBar component
- Add toolbar button to EditorPanel
- Add Cmd/Ctrl+K shortcut handler
- Add diff result view with Apply/Discard

## Testing Strategy

- **Backend unit tests**: Verify mode branching in improve-routes (instruct mode uses correct prompt, skips benchmark context, validates instruction field)
- **Frontend unit tests**: Reducer tests for all 5 new action types. AiEditBar component tests for render/submit/escape/loading/error states.
- **Integration test**: Full flow: open bar -> type instruction -> mock API response -> verify diff displayed -> apply -> verify content updated

## Technical Challenges

### Challenge 1: Prompt Bar Focus Management
**Solution**: Use `useEffect` with `autoFocus` on the textarea and `ref.current?.focus()` as fallback. Escape handler uses `onKeyDown` on the textarea element.
**Risk**: Low. Standard React focus pattern, proven in many codebases.

### Challenge 2: Preventing Ctrl+K Browser Default
**Solution**: `e.preventDefault()` in the keydown handler. Must be registered on the EditorPanel div (or within the workspace keydown handler) before the browser processes it.
**Risk**: Low. Ctrl+K opens the browser address bar in some browsers; preventDefault stops this.

### Challenge 3: Content Drift Between Editor and Request
**Solution**: Always read `state.skillContent` at submission time (not at bar-open time). The content captured in the closure of `submitAiEdit` is the latest reducer state.
**Risk**: None. The `useCallback` dependency on `state.skillContent` ensures freshness.
