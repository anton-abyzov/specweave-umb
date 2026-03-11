# Architecture Plan: AI Edit with Eval Change Suggestions

## Overview

Extend the existing AI Edit (instruct mode) flow to suggest eval changes alongside SKILL.md edits. A single LLM call returns both content and eval suggestions via a structured text delimiter. The frontend presents eval changes as a selectable checklist, merges selected changes client-side, and saves via the existing PUT /evals endpoint.

## Data Flow

```
User types instruction
        |
        v
[Frontend: submitAiEdit]
  - Sends instruction + content + currentEvals
        |
        v
[Backend: POST /improve (instruct mode)]
  - Builds prompt including current evals
  - Single LLM call
  - Parses response: content | ---REASONING--- | ---EVAL_CHANGES--- JSON
  - Returns { original, improved, reasoning, evalChanges[] }
        |
        v
[Frontend: dispatch AI_EDIT_RESULT]
  - Stores improved content + evalChanges in state
  - Initializes selection map (all checked by default)
        |
        v
[Frontend: AiEditBar renders]
  - SKILL.md diff (existing)
  - Eval changes section (new): cards grouped remove > modify > add
  - Checkboxes per card
        |
        v
[User clicks Apply]
  - Save SKILL.md via POST /apply-improvement (existing)
  - Compute merged evals from selected changes (client-side)
  - Save merged evals via PUT /evals (existing)
  - Error handling: SKILL.md save failure blocks all; evals save failure shows error with retry
```

## Architecture Decisions

### AD-1: Single LLM Call with Text Delimiters

The existing instruct mode already uses a `---REASONING---` delimiter to separate content from reasoning. This plan adds a second delimiter `---EVAL_CHANGES---` after the reasoning section.

**Response format:**
```
<improved SKILL.md content>
---REASONING---
<explanation of changes>
---EVAL_CHANGES---
<JSON array of eval change objects>
```

**Rationale:** Avoids a second LLM call, keeps the existing parsing pattern consistent, and the LLM has full context of both the content changes and evals to produce coherent suggestions.

**Fault tolerance:** If `---EVAL_CHANGES---` is missing or its JSON is malformed, the endpoint returns `evalChanges: []` and the SKILL.md result proceeds normally (AC-US1-04).

### AD-2: Eval Change Object Shape

```typescript
interface EvalChange {
  action: "add" | "modify" | "remove";
  reason: string;
  evalId?: number;       // required for modify/remove (references existing eval)
  eval?: EvalCase;       // required for add/modify (the full proposed case)
}
```

For `add`: `eval` contains the new case with a placeholder `id: 0` (real ID computed client-side during merge).
For `modify`: `evalId` identifies the target, `eval` contains the full replacement case.
For `remove`: `evalId` identifies the target, `eval` is omitted.

### AD-3: Client-Side Merge Logic

The merge function lives in a new pure utility `mergeEvalChanges.ts`:

```typescript
function mergeEvalChanges(
  current: EvalsFile,
  changes: EvalChange[],
  selections: Map<number, boolean>
): EvalsFile
```

1. Start with a copy of `current.evals`
2. Process selected changes in order: removes first, then modifies, then adds
3. For removes: filter out evals matching `evalId`
4. For modifies: replace eval at matching `evalId` with `eval` data (keeping original `id`)
5. For adds: assign `id = max(existing ids) + 1` (incrementing for multiple adds)
6. Return new `EvalsFile` with merged evals

**Rationale:** Processing removes first avoids index/id conflicts. Client-side merge keeps the server stateless and reuses the existing PUT /evals endpoint without modification.

### AD-4: State Extensions (useReducer)

New fields on `WorkspaceState`:

```typescript
// In WorkspaceState
aiEditEvalChanges: EvalChange[];
aiEditEvalSelections: Map<number, boolean>;  // index -> checked
```

New reducer actions:

```typescript
| { type: "AI_EDIT_RESULT"; improved: string; reasoning: string; evalChanges: EvalChange[] }
| { type: "TOGGLE_EVAL_CHANGE"; index: number }
| { type: "SELECT_ALL_EVAL_CHANGES" }
| { type: "DESELECT_ALL_EVAL_CHANGES" }
```

The existing `AI_EDIT_RESULT` action is extended (not a new action) to include `evalChanges`. On `CLOSE_AI_EDIT`, both `aiEditEvalChanges` and `aiEditEvalSelections` are cleared.

**Note on `Map<number, boolean>` vs `Set<number>`:** The spec suggests `Set<number>` for tracking selections, but `Map<number, boolean>` is more natural for the "checked by default, toggle on/off" pattern -- every change starts as `true` and toggling flips the value. A Set would require the inverse logic (tracking deselected items), which is less intuitive when rendering checkbox `checked` props.

### AD-5: API Shape Extension

The `instructEdit` API function gains an optional `evals` parameter:

```typescript
// api.ts
instructEdit(plugin, skill, {
  instruction: string,
  content: string,
  evals?: EvalsFile,       // NEW: current evals for context
  provider?: string,
  model?: string,
}): Promise<InstructEditResult>

// New return type (extends existing ImproveResult)
interface InstructEditResult {
  original: string;
  improved: string;
  reasoning: string;
  evalChanges: EvalChange[];  // NEW: may be empty
}
```

The backend `POST /improve` body type gains `evals?: EvalsFile`. The response JSON gains `evalChanges: EvalChange[]`.

### AD-6: No New API Endpoints

All changes fit within existing endpoints:
- `POST /improve` (instruct mode): extended request/response
- `POST /apply-improvement`: unchanged (saves SKILL.md)
- `PUT /evals`: unchanged (saves merged evals)

### AD-7: Eval Changes Panel UI Structure

The eval changes section in `AiEditBar.tsx` renders below the existing SKILL.md diff:

```
[SKILL.md diff -- existing]

--- Eval Changes (3 suggestions) ---  [Select All / Deselect All]

  [x] REMOVE  "Old feature test"
      Reason: This eval tests removed functionality
      > [expandable: full eval details]

  [x] MODIFY  "Basic prompt handling"
      Reason: Updated assertion to match new behavior
      > [expandable: field-level diff showing changed fields]

  [x] ADD     "Error boundary test"
      Reason: New error handling section needs coverage
      > [expandable: full proposed eval case]

[Apply] [Discard] [Try Again]
```

For modify actions, the expandable detail uses a simple field-level comparison (not the line-level LCS diff from `diff.ts`). Fields compared: `name`, `prompt`, `expected_output`, `assertions[]`. This is a shallow comparison rendered as "old value -> new value" per changed field.

### AD-8: Error Handling on Apply

Apply follows a two-phase save with partial failure tolerance:

1. Save SKILL.md via `POST /apply-improvement`
   - If this fails: show error, do NOT proceed to evals save
2. Save merged evals via `PUT /evals`
   - If this fails: SKILL.md is already saved (intentional -- content changes are preserved)
   - Show specific error message: "SKILL.md saved but eval changes failed. Click Retry to save evals."
   - A retry button calls only the evals save (not SKILL.md again)

This requires a new transient state `aiEditEvalsRetry: EvalsFile | null` that holds the merged evals for retry.

## Component Boundaries

### Backend Changes (improve-routes.ts)

1. **Prompt construction**: When `mode === "instruct"` and `body.evals` is provided, append current evals to the system prompt with instructions to analyze and suggest changes
2. **Response parsing**: After splitting on `---REASONING---`, split the reasoning portion on `---EVAL_CHANGES---` to extract the JSON array
3. **Validation**: Parse eval changes JSON with try/catch; malformed data results in `evalChanges: []`
4. **Response shape**: Add `evalChanges` to the JSON response

### Frontend Changes

| File | Change |
|------|--------|
| `workspaceTypes.ts` | Add `EvalChange` type, extend `WorkspaceState`, extend `AI_EDIT_RESULT` action, add new toggle actions |
| `workspaceReducer.ts` | Handle extended `AI_EDIT_RESULT`, `TOGGLE_EVAL_CHANGE`, `SELECT_ALL_EVAL_CHANGES`, `DESELECT_ALL_EVAL_CHANGES`, clear on `CLOSE_AI_EDIT` |
| `WorkspaceContext.tsx` | Extend `submitAiEdit` to send evals; extend `applyAiEdit` to compute merge and save evals; add `retryEvalsSave` |
| `api.ts` | Extend `instructEdit` params and return type |
| `types.ts` | Add `EvalChange` type, add `InstructEditResult` type |
| `AiEditBar.tsx` | Add eval changes section with cards, checkboxes, expand/collapse, select all/deselect all |
| `mergeEvalChanges.ts` (new) | Pure function for merge logic |

### New File

`src/eval-ui/src/utils/mergeEvalChanges.ts` -- a single pure function with no dependencies beyond the `EvalChange` and `EvalsFile` types. Easily unit-testable.

## Prompt Design (Backend)

The instruct mode system prompt is extended with an eval analysis section:

```
## Eval Analysis Rules
- Review the current evals below and determine which need updating based on your SKILL.md changes
- For each change you make to SKILL.md, consider: does any eval test the old behavior?
- Suggest REMOVE for evals testing removed/changed functionality
- Suggest MODIFY for evals that need updated assertions or expected outputs
- Suggest ADD for new capabilities that lack test coverage
- Keep suggestions focused -- only propose changes directly related to the SKILL.md edits
- If no eval changes are needed, return an empty JSON array

## Output Format
Return the modified SKILL.md content, then "---REASONING---" with your explanation,
then "---EVAL_CHANGES---" followed by a JSON array:
[
  { "action": "remove", "reason": "...", "evalId": 1 },
  { "action": "modify", "reason": "...", "evalId": 2, "eval": { ...full case... } },
  { "action": "add", "reason": "...", "eval": { "id": 0, "name": "...", ... } }
]
```

The user prompt appends the current evals after the instruction:

```
## Current Evals
<JSON of current EvalsFile>
```

When `body.evals` is null/undefined (no evals exist), the prompt sends `"evals": []` and instructs the LLM it may suggest new test cases from scratch (AC-US1-02).

## Risk Mitigations

1. **LLM produces invalid JSON in EVAL_CHANGES**: Caught by try/catch, falls back to `evalChanges: []`. The SKILL.md edit is still usable.

2. **LLM references non-existent evalId in modify/remove**: The merge function skips changes with unmatched IDs (no-op) rather than erroring. A warning could be logged but the merge proceeds.

3. **Duplicate eval IDs after merge**: The add logic starts from `max(existing ids) + 1` and increments, so no collisions.

4. **Large evals bloating the prompt**: Evals are typically small (5-15 cases, ~50-100 lines JSON total). No truncation needed for the initial implementation. If this becomes an issue, a future increment can summarize evals instead of sending raw JSON.

5. **PUT /evals validation failure**: The existing schema validation on the PUT endpoint catches malformed eval data from the LLM. The retry mechanism lets users fix and resave.

## Testing Strategy

- **Unit tests** for `mergeEvalChanges.ts`: all action types, mixed selections, empty inputs, ID assignment, unmatched evalId handling
- **Unit tests** for response parsing in `improve-routes.ts`: valid 3-part response, missing EVAL_CHANGES, malformed JSON, empty array
- **Reducer tests**: new actions, state transitions, clearing on CLOSE_AI_EDIT
- **Integration test**: full flow from submitAiEdit through applyAiEdit with mocked API
