# Implementation Plan: Fix Skill Studio Activation Test Bugs

## Overview

Five bugs in the activation test feature spanning the eval-ui (React/Vite) and eval-server/eval-engine (Node.js) layers. All fixes are surgical -- each touches 1-2 files with well-established patterns already present in adjacent code. No new dependencies, no schema changes, no new APIs.

## Bug Analysis and Fix Design

### Bug 1 (CRITICAL): SSE done event error field silently swallowed

**Location**: `WorkspaceContext.tsx:530-536`

**Root Cause**: When the activation test SSE stream emits a `done` event with an `error` field (backend catch block at `api-routes.ts:1278` calls `sendSSEDone(res, { error: ... })`), the frontend casts the data directly to `ActivationSummary` and dispatches `ACTIVATION_DONE` without checking for the error. The summary then contains no results, no metrics -- just a silent "complete" state with empty UI.

**Established Pattern**: The generate-evals SSE handler at `WorkspaceContext.tsx:477-485` shows the correct approach: it checks for a separate `error` event before processing `done`. However, for activation, the backend sends errors as part of the `done` event data (not as a separate `error` event), so the fix must inspect the `done` data payload.

**Fix Design**:
```
WorkspaceContext.tsx, activation SSE event processing (line 530 area):

Before dispatching ACTIVATION_DONE, check if evt.data contains an error field.
If error is present:
  - Clear timeout (same as now)
  - Dispatch ACTIVATION_ERROR with the error message
  - Do NOT dispatch ACTIVATION_DONE
  - Do NOT append to activation history
If no error:
  - Proceed with existing ACTIVATION_DONE + history append logic
```

The same pattern must also be applied to the prompt-generation SSE parser at line 653. The `done` event from the prompt generation endpoint (`api-routes.ts:1343`) can also carry `{ error: ... }` per the catch block at `api-routes.ts:1346`. The existing code at line 653 only checks for `data.prompts` -- if there's an error instead, it silently produces empty prompts.

**Files Modified**:
- `src/eval-ui/src/pages/workspace/WorkspaceContext.tsx` (2 locations)

---

### Bug 2 (HIGH): No SSE events during Phase 1 auto-classification

**Location**: `activation-tester.ts:89-108` (resolvePrompts), `api-routes.ts:1246-1250`

**Root Cause**: The `testActivation` function accepts an `onResult` callback that fires per-prompt during Phase 2 (activation evaluation). But Phase 1 (auto-classification via `resolvePrompts`) runs first and has no progress reporting. When the user submits prompts with `auto` expected values, the UI shows a loading spinner with "0 / N prompts tested" and no progress events for the entire duration of Phase 1 classification calls. For N auto-prompts, this is N separate LLM calls with zero feedback.

**Fix Design**: Add an `onProgress` callback parameter to `testActivation` and call it during Phase 1. The server route already wraps `onResult` with SSE emission -- add equivalent wrapping for progress events.

Two-part change:

1. **activation-tester.ts**: Add optional `onProgress?: (phase: string, message: string) => void` parameter to `testActivation`. Call it from within `resolvePrompts` (either by passing it through, or by extracting the resolve loop inline). Emit progress at the start of Phase 1 and after each classification completes.

2. **api-routes.ts**: In the activation-test route handler, pass an `onProgress` callback that calls `sendSSE(res, "progress", { phase, message })`. This follows the exact pattern used by the benchmark runner with `startDynamicHeartbeat`.

The frontend already ignores unknown SSE event types (the useSSE hook just appends them), so no frontend change is needed for this to work. However, the `ActivationPanel.tsx` loading skeleton area (line 245-252) could optionally display progress messages. This is enhancement, not bug fix -- defer to a future increment.

**Signature Change**:
```typescript
export async function testActivation(
  skillDescription: string,
  prompts: ActivationPrompt[],
  client: LlmClient,
  onResult?: (result: ActivationResult) => void,
  meta?: SkillMeta,
  onProgress?: (phase: string, message: string) => void,  // NEW
): Promise<ActivationSummary>
```

**Files Modified**:
- `src/eval/activation-tester.ts`
- `src/eval-server/api-routes.ts` (activation-test route)

---

### Bug 3 (MEDIUM): Generate button silently disabled without explanation

**Location**: `ActivationPanel.tsx:86`

**Root Cause**: The "Generate Test Prompts" button is disabled when `!cleanDescription` is true, but the only UX signal is reduced opacity (0.5) and `cursor: not-allowed`. There is a `title` attribute set to "No skill description available" when `!cleanDescription` (line 95), but native tooltips are unreliable, slow to appear, and invisible on touch devices. The user has no way to understand why the button does nothing.

**Established Pattern**: Throughout the eval-ui, error states are shown inline with red-tinted backgrounds (see `generatingPromptsError` display at line 127-131, `activationError` at line 235-242).

**Fix Design**: Add an inline hint below the button area when the description is unavailable. This is a conditional render that shows a short message in the same style as `generatingPromptsError`.

```
When !cleanDescription and not already running:
  Show: "Add a description to your SKILL.md to enable AI prompt generation"
  Style: text-[11px], color: var(--text-tertiary), with an info icon
```

Additionally, improve the disabled button styling -- currently it relies solely on opacity + cursor which looks identical to the "loading" state. Add a distinct visual:
- When disabled due to no description: use `var(--text-tertiary)` text, no accent color
- When disabled due to running: existing spinner style (already correct)

**Files Modified**:
- `src/eval-ui/src/pages/workspace/ActivationPanel.tsx`

---

### Bug 4 (MEDIUM): Description fallback inconsistency between endpoints

**Location**: `api-routes.ts:1232-1233` vs `api-routes.ts:1301-1302`

**Root Cause**: Two endpoints extract the skill description from SKILL.md but handle the missing-description case differently:

| Endpoint | Line | Fallback when no match |
|---|---|---|
| `/activation-test` | 1232-1233 | `skillContent.slice(0, 500)` (first 500 chars of raw SKILL.md) |
| `/activation-prompts` | 1301-1302 | `""` (empty string, then returns 400 error) |

The activation-test endpoint silently uses raw SKILL.md content (including frontmatter `---` blocks) as the "description", which feeds garbage into the LLM prompt. The activation-prompts endpoint correctly rejects an empty description but doesn't try the raw-content fallback.

**Fix Design**: Align both endpoints to the same extraction logic. Create a shared `extractSkillDescription(skillContent: string): string` helper or use inline identical logic:

1. Try regex match for frontmatter `description` field
2. If no match, strip frontmatter (`/^---[\s\S]*?---\s*/`) then take the first 500 chars of the remaining body
3. If the result is empty/whitespace-only, return empty string

Apply this to both endpoints. The activation-test endpoint should also check for empty description after extraction -- if truly empty, it can still proceed (the LLM will get an empty description which degrades quality but doesn't crash), but the `description` field in the done event should reflect reality.

**Extraction Logic** (shared):
```typescript
function extractDescription(skillContent: string): string {
  const fmMatch = skillContent.match(/^---[\s\S]*?description:\s*"([^"]+)"[\s\S]*?---/);
  if (fmMatch) return fmMatch[1];
  const body = skillContent.replace(/^---[\s\S]*?---\s*/, "").trim();
  return body.slice(0, 500);
}
```

This can be a local function in `api-routes.ts` or extracted to a shared utility. Given it's only used in two adjacent routes, a local function is simpler.

**Files Modified**:
- `src/eval-server/api-routes.ts`

---

### Bug 5 (LOW): No heartbeat during prompt generation LLM call

**Location**: `api-routes.ts:1326`

**Root Cause**: The `activation-prompts` endpoint makes a single `client.generate()` call (line 1326) that can take 10-30 seconds. During this time, no SSE events are emitted. The frontend shows "Generating..." but has no way to know if the server is still working or has hung. Other SSE endpoints in the codebase (benchmark runner at line 870, comparison at line 870) use `withHeartbeat` or `startDynamicHeartbeat` from `sse-helpers.ts` to keep the connection alive.

**Fix Design**: Wrap the `client.generate()` call with `withHeartbeat()` from `sse-helpers.ts`. This emits periodic `progress` events with elapsed time. The frontend prompt generation code at `WorkspaceContext.tsx:640-668` already handles arbitrary SSE events (it only acts on `done` and `error` events, skipping others), so heartbeat events will be harmlessly ignored.

```typescript
// Before:
const { text } = await client.generate(systemPrompt, userPrompt);

// After:
const { text } = await withHeartbeat(
  res, undefined, "generating",
  "Generating test prompts...",
  () => client.generate(systemPrompt, userPrompt),
);
```

Note: `initSSE` must be called before the heartbeat starts. Currently, `initSSE` is called at line 1309, after the description validation at lines 1296-1307. The `withHeartbeat` call at line 1326 is after `initSSE`, so the ordering is correct.

**Files Modified**:
- `src/eval-server/api-routes.ts`

---

## Architecture Decisions

### AD-1: Fix in-place vs. refactor SSE error handling

**Decision**: Fix in-place at each bug site. Do NOT refactor the generic `useSSE` hook to automatically extract error fields from done events.

**Rationale**: The `useSSE` hook is generic and used by multiple features. Some SSE endpoints send errors as separate `error` events (generate-evals), some embed errors in the `done` payload (activation-test, activation-prompts). Making the hook opinionated about error extraction would break the abstraction. Each consumer should handle its own error semantics.

### AD-2: `onProgress` callback vs. wrapping `testActivation` at the server level

**Decision**: Add `onProgress` to `testActivation` signature rather than wrapping the call with `startDynamicHeartbeat` at the server level.

**Rationale**: A dynamic heartbeat emits generic "still working..." messages on a timer. For Phase 1, we want semantic progress: "Classifying prompt 3 of 5..." which requires integration inside the resolve loop. The `onProgress` callback gives the engine control over message content.

### AD-3: Description extraction -- shared helper vs. inline duplication

**Decision**: Local helper function in `api-routes.ts`, not a new module.

**Rationale**: Only two call sites, both in the same file within 70 lines of each other. A shared module would be overengineering. If a third call site emerges, refactor then.

## Implementation Phases

### Phase 1: Critical Error Handling (Bug 1)
- Fix SSE done error field check in WorkspaceContext.tsx (activation test)
- Fix SSE done error field check in WorkspaceContext.tsx (prompt generation)
- Add reducer tests for error-in-done-event scenarios

### Phase 2: Progress Visibility (Bugs 2 + 5)
- Add `onProgress` callback to `testActivation`
- Wire `onProgress` to SSE in activation-test route
- Wrap prompt generation with `withHeartbeat`
- Add unit tests for `testActivation` with `onProgress`

### Phase 3: UX and Consistency (Bugs 3 + 4)
- Add inline disabled-reason hint to ActivationPanel
- Create `extractDescription` helper in api-routes.ts
- Apply consistent description fallback to both endpoints
- Add tests for description extraction edge cases

## Testing Strategy

### Unit Tests (Vitest)
- **workspaceReducer.test.ts**: Add tests for ACTIVATION_ERROR dispatch when done event contains error field (currently missing)
- **activation-tester.test.ts**: Add tests for `onProgress` callback invocation during Phase 1 auto-classification
- **api-routes tests**: Add tests for `extractDescription` helper covering: frontmatter match, frontmatter-stripped body fallback, empty content, content with no frontmatter

### Integration Behavior Verification
- Activation test with LLM error returns error to UI (not silent success)
- Activation test with auto-prompts emits progress events during Phase 1
- Prompt generation with slow LLM emits heartbeat events
- Prompt generation with LLM error shows error in UI

### Files with Expected Test Changes
| Test File | New Tests |
|---|---|
| `workspaceReducer.test.ts` | Error-in-done dispatch, prompt generation error-in-done |
| `activation-tester.test.ts` | `onProgress` callback count, Phase 1 progress messages |
| New: `api-routes` description helper test | Frontmatter extraction, body fallback, empty input |

## Risk Assessment

All changes are low-risk:
- Bug 1: Adding a conditional branch before an existing dispatch -- cannot regress existing success path
- Bug 2: Adding an optional parameter with default `undefined` -- backward compatible
- Bug 3: Adding a conditional render element -- no state changes
- Bug 4: Replacing inline regex with a function that does the same thing + a fallback -- net behavior only changes for the edge case of missing frontmatter description
- Bug 5: Wrapping an existing call with `withHeartbeat` -- the wrapped function signature is unchanged

## File Change Summary

| File | Bugs | Change Type |
|---|---|---|
| `src/eval-ui/src/pages/workspace/WorkspaceContext.tsx` | 1 | Add error check in SSE done handlers |
| `src/eval/activation-tester.ts` | 2 | Add `onProgress` param, emit during Phase 1 |
| `src/eval-ui/src/pages/workspace/ActivationPanel.tsx` | 3 | Add disabled-reason inline hint |
| `src/eval-server/api-routes.ts` | 2, 4, 5 | Progress callback, description helper, heartbeat |
| `src/eval-ui/src/pages/workspace/workspaceReducer.test.ts` | 1 | New error-in-done test cases |
| `src/eval/__tests__/activation-tester.test.ts` | 2 | New onProgress callback tests |
