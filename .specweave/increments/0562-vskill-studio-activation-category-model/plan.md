# Architecture Plan: vSkill Studio Activation, Category, Model

## Overview

Three interconnected improvements to vSkill Studio's skill creation and testing workflows. All changes are within `repositories/anton-abyzov/vskill/` (Node.js ESM backend, React frontend).

---

## Problem 1: Smart Category Selection During Skill Generation

### Current State

When generating a skill via AI (`POST /api/skills/generate`), the backend creates the skill body and evals but does NOT suggest which existing plugin the skill should be placed into. The frontend handles plugin placement via a post-hoc recommendation banner (`showPluginRecommendation` in `useCreateSkill.ts:309-312`) that only checks filesystem layout, not semantic fit.

**Files**:
- `src/eval-server/skill-create-routes.ts` (lines 728-812): `/api/skills/generate` endpoint
- `src/eval-ui/src/hooks/useCreateSkill.ts` (lines 209-216): `pluginLayoutInfo` computed from layout detection
- `src/eval-ui/src/pages/CreateSkillPage.tsx`: plugin recommendation banner

### Design

#### Backend: Add plugin matching to generate response

Extend the `/api/skills/generate` SSE response to include a `suggestedPlugin` field. After body generation completes and the skill name/description/tags are known, do a lightweight match against existing plugins:

1. Scan existing plugins via `scanSkills()` (already imported in `api-routes.ts`)
2. For each plugin, extract its skills' descriptions from SKILL.md frontmatter
3. Score semantic similarity: exact tag overlap, description keyword overlap, name prefix match
4. Return top match if score exceeds threshold, or `null` (suggest new plugin)

```
suggestedPlugin: {
  plugin: string;          // existing plugin name
  layout: 1 | 2;          // layout where this plugin exists
  confidence: "high" | "medium" | "low";
  reason: string;          // "3 skills with similar tags: testing, eval"
} | null
```

This is a **heuristic match, not LLM-based** -- avoids an extra API call and latency. The existing `scanSkills()` already reads SKILL.md frontmatter for all skills, so the data is available without new I/O.

#### Frontend: Replace banner with inline suggestion

Replace the current `showPluginRecommendation` banner with a richer inline card that appears immediately after AI generation completes:

- Show matched plugin name, reason, existing skill count
- "Use this plugin" button auto-selects layout + plugin
- "Create new plugin" button keeps current layout 3 behavior
- If no match, skip the card entirely (current behavior)

### Component Boundaries

```
skill-create-routes.ts
  mergeGenerateResults()  -- add suggestedPlugin field
  matchExistingPlugin()   -- NEW: heuristic plugin matcher

useCreateSkill.ts
  handleGenerate()  -- consume suggestedPlugin from SSE response
  state: suggestedPlugin  -- NEW state field

CreateSkillPage.tsx / CreateSkillInline.tsx
  PluginSuggestionCard  -- NEW component replacing recommendation banner
```

### Decisions

- **Heuristic over LLM**: Plugin matching uses tag/keyword overlap, not an LLM call. Rationale: matching is a classification task over a small set (typically 2-10 plugins), and adding another LLM round-trip would double generation latency.
- **Server-side matching**: The server already has `scanSkills()` and the skill list. Computing the match server-side avoids sending the full plugin catalog to the client.

---

## Problem 2: Activation Test Rework

### Current State

**SSE duplicate dispatch bug**: `WorkspaceContext.tsx` lines 487-501 process activation SSE events inside a `useEffect` that depends on `activationSSE.events`. The `useSSE` hook (`sse.ts`) accumulates ALL events in state via `setEvents((prev) => [...prev, evt])`. Every time a new event arrives, the effect re-runs over the entire accumulated array, dispatching `ACTIVATION_RESULT` for events that were already dispatched. Result: each prompt result appears N times (where N = its position in the sequence).

**No AI prompt generation**: Test prompts are manually typed or added from hardcoded `PROMPT_TEMPLATES` in `ActivationPanel.tsx:13-24`. No way to auto-generate relevant test prompts from the skill description.

**No test history**: Activation test results are ephemeral -- stored only in workspace state, lost on navigation. No persistence or trend tracking.

### Design

#### Fix: SSE duplicate dispatch

**Root cause**: `useSSE` accumulates events in an array. The `useEffect` in `WorkspaceContext.tsx` iterates the full array on every change.

**Fix approach**: Track the last processed event index in a ref, and only process new events from that index forward.

```typescript
// WorkspaceContext.tsx -- activation SSE processing
const lastActivationIdxRef = useRef(0);

useEffect(() => {
  const events = activationSSE.events;
  for (let i = lastActivationIdxRef.current; i < events.length; i++) {
    const evt = events[i];
    if (evt.event === "prompt_result") {
      dispatch({ type: "ACTIVATION_RESULT", result: evt.data as ActivationResult });
    }
    if (evt.event === "done") {
      // ... existing done handling
    }
  }
  lastActivationIdxRef.current = events.length;
}, [activationSSE.events]);
```

Reset `lastActivationIdxRef.current = 0` in `runActivationTest` before starting a new SSE stream.

This same pattern should be applied to `genEvalsSSE` event processing (lines 433-458) and `aiEditSSE` event processing (lines 298-327) as a preventive measure, though those use different event types and the duplication may be less visible.

#### Feature: AI-generated test prompts

Add a "Generate prompts" button to `ActivationPanel.tsx` that calls a new backend endpoint:

```
POST /api/skills/:plugin/:skill/activation-prompts
Request:  { count?: number, provider?: ProviderName, model?: string }
Response (SSE):
  event: prompt_generated
  data: { prompt: string, expected: "should_activate" | "should_not_activate" }
  ...
  event: done
  data: { prompts: ActivationPrompt[] }
```

Backend implementation in `api-routes.ts`:
1. Read SKILL.md description and tags
2. Call LLM with a prompt requesting N test prompts (half positive, half negative)
3. Stream each generated prompt as it is parsed
4. Use per-request model overrides if provided, else fall back to `getClient()`

System prompt for generation:

```
Given this skill description, generate test prompts to evaluate activation quality.
Generate {count} prompts: half that SHOULD activate this skill, half that should NOT.
For "should not" prompts, make them plausible but clearly outside this skill's domain.
Return one JSON object per line: {"prompt": "...", "expected": "should_activate"|"should_not_activate"}
```

#### Feature: Activation test history

Persist activation test results to a JSON file alongside the skill:

```
{skill-dir}/activation-history.json
```

Schema:

```typescript
interface ActivationHistoryFile {
  runs: ActivationHistoryRun[];
}

interface ActivationHistoryRun {
  id: string;              // "run-{timestamp}"
  timestamp: string;       // ISO 8601
  model: string;           // e.g. "claude-sonnet"
  provider: string;        // e.g. "claude-cli"
  promptCount: number;
  summary: {
    precision: number;
    recall: number;
    reliability: number;
    tp: number;
    tn: number;
    fp: number;
    fn: number;
  };
  results: ActivationResult[];
}
```

Backend endpoints:
- `POST /api/skills/:plugin/:skill/activation-test` -- after computing summary, write to `activation-history.json`
- `GET /api/skills/:plugin/:skill/activation-history` -- return history runs (summary only, not full results)
- `GET /api/skills/:plugin/:skill/activation-history/:runId` -- return full results for one run

Frontend:
- Add a collapsible "History" section below the results in `ActivationPanel.tsx`
- Show run list with date, model, reliability score, pass/fail indicator
- Click a run to expand and show its full results
- Trend sparkline showing reliability over last N runs

### Component Boundaries

```
BACKEND:
  api-routes.ts
    activation-test endpoint  -- add history write + model passthrough
    NEW: /activation-prompts  -- AI prompt generation endpoint
    NEW: /activation-history  -- history read endpoints

  activation-tester.ts
    testActivation()  -- no changes needed (already accepts LlmClient)

  NEW: src/eval/activation-history.ts
    writeActivationRun()   -- append to activation-history.json (cap at 50 runs)
    listActivationRuns()   -- return summaries (without full results array)
    getActivationRun()     -- return full run by id

FRONTEND:
  ActivationPanel.tsx
    GeneratePromptsButton  -- NEW: triggers AI prompt generation
    ActivationHistory      -- NEW: collapsible history section

  WorkspaceContext.tsx
    runActivationTest()    -- fix duplicate dispatch, pass model config
    NEW: generateActivationPrompts()  -- call prompt generation endpoint
    NEW: fetchActivationHistory()     -- fetch history on panel mount

  workspaceReducer.ts
    NEW actions: ACTIVATION_HISTORY_LOADED, GENERATE_PROMPTS_START/RESULT/DONE/ERROR

  workspaceTypes.ts
    NEW state: activationHistory, generatingPrompts, generatingPromptsError
```

### Decisions

- **File-based history**: Consistent with existing `benchmark-history.json` pattern. Skills are file-system entities; their test history belongs alongside them.
- **History stored per-skill**: Each skill's activation test history lives in its own directory. This keeps history portable (copy skill dir = copy history) and avoids a central registry.
- **Cap at 50 runs**: `writeActivationRun()` prunes oldest runs when count exceeds 50 to prevent unbounded growth.
- **Prompt generation uses same LLM pipeline**: Generated prompts are tested by the same model, which is correct since we are evaluating the description's activation quality, not the model's prompt generation ability.

---

## Problem 3: Connect Model Selector to Activation Testing

### Current State

The activation test endpoint (`api-routes.ts:1138-1173`) calls `getClient()` which reads from the global `currentOverrides` (line 40-44). This global is updated by `POST /api/config`. However:

1. `runActivationTest` in `WorkspaceContext.tsx:524-546` sends `{ prompts }` to the SSE endpoint but does NOT include provider/model overrides.
2. The activation test always uses whatever model is globally configured.
3. There is no model selector visible on the Activation panel itself.

This is inconsistent with the AI Edit flow (`submitAiEdit` at line 340) which DOES accept `provider` and `model` parameters.

### Design

#### Backend: Accept model overrides in activation-test endpoint

Extend the POST body to accept optional `provider` and `model` fields:

```typescript
// api-routes.ts activation-test endpoint
const body = (await readBody(req)) as {
  prompts: ActivationPrompt[];
  provider?: ProviderName;  // NEW
  model?: string;           // NEW
};

// Use per-request overrides if provided, fall back to global config
const client = body.provider || body.model
  ? createLlmClient({ provider: body.provider, model: body.model })
  : getClient();
```

Same pattern for the new `/activation-prompts` endpoint.

#### Frontend: Pass model config from ConfigContext

The `ConfigContext` already holds the current provider/model. Thread it through in `runActivationTest`:

```typescript
// WorkspaceContext.tsx
const runActivationTest = useCallback((promptsText: string) => {
  // ... existing prompt parsing ...

  const body: Record<string, unknown> = { prompts };
  if (config?.provider) body.provider = config.provider;
  if (config?.model) body.model = config.model;

  activationSSE.start(`/api/skills/${plugin}/${skill}/activation-test`, body);
  // ...
}, [plugin, skill, activationSSE, config]);
```

The activation test automatically uses whatever model is selected in the global ModelSelector (sidebar). No separate model picker needed on the activation panel.

#### History: Record which model was used

The `activation-history.json` records include `model` and `provider` fields (see Problem 2 design). This enables comparing activation quality across models.

### Component Boundaries

```
BACKEND:
  api-routes.ts
    activation-test endpoint  -- accept provider/model in body
    activation-prompts endpoint -- accept provider/model in body

FRONTEND:
  WorkspaceContext.tsx
    runActivationTest()  -- forward config.provider/model
    generateActivationPrompts()  -- forward config.provider/model

  WorkspaceProvider  -- needs access to ConfigContext (useConfig())
```

### Decisions

- **No separate model picker on Activation panel**: The global ModelSelector in the sidebar already controls the active model. Adding a second picker would create confusion. Just wire the existing global config through to the API call.
- **Backward compatible**: If `provider`/`model` are omitted from the request body, the server falls back to `getClient()` (global config). Existing callers continue to work.
- **ConfigContext dependency**: `WorkspaceProvider` must be rendered inside `ConfigProvider` in the component tree. This is already the case in the current app layout.

---

## Implementation Order

The three problems have dependencies:

```
P2a (SSE fix)              -- standalone bug fix, no dependencies
P3  (Model connection)     -- prerequisite for P2 history (need model info)
P2b (AI prompt gen)        -- uses model connection from P3
P2c (Activation history)   -- uses model info from P3
P1  (Category selection)   -- independent, can be parallelized
```

Recommended task order:
1. **P2a**: Fix SSE duplicate dispatch (standalone bug fix)
2. **P3**: Connect model selector to activation tests
3. **P2b**: AI prompt generation endpoint + UI
4. **P2c**: Activation test history persistence + UI
5. **P1**: Smart category/plugin selection during generation

---

## Files Modified

### Backend (`src/eval-server/`)

| File | Change |
|------|--------|
| `api-routes.ts` | Extend activation-test to accept provider/model; add `/activation-prompts` endpoint; add `/activation-history` endpoints; write history on test completion |
| `skill-create-routes.ts` | Add `matchExistingPlugin()` heuristic; include `suggestedPlugin` in generate response |

### Core (`src/eval/`)

| File | Change |
|------|--------|
| `activation-tester.ts` | No changes (already accepts LlmClient) |
| **NEW** `activation-history.ts` | History read/write/list for activation test runs |

### Frontend (`src/eval-ui/src/`)

| File | Change |
|------|--------|
| `pages/workspace/ActivationPanel.tsx` | Add generate prompts button, history section |
| `pages/workspace/WorkspaceContext.tsx` | Fix SSE duplicate dispatch, forward model config, add history + prompt-gen actions |
| `pages/workspace/workspaceReducer.ts` | Add new activation actions (HISTORY_LOADED, GENERATE_PROMPTS_*) |
| `pages/workspace/workspaceTypes.ts` | Add new state fields and action types |
| `hooks/useCreateSkill.ts` | Consume `suggestedPlugin` from generate response |
| `pages/CreateSkillPage.tsx` | Replace plugin recommendation banner with PluginSuggestionCard |
| `components/CreateSkillInline.tsx` | Same banner replacement |

### New Files

| File | Purpose |
|------|---------|
| `src/eval/activation-history.ts` | Activation test history persistence (read/write/prune) |
| `src/eval-ui/src/components/PluginSuggestionCard.tsx` | Smart plugin suggestion after AI generation |

---

## Testing Strategy

- **Unit tests** for `activation-history.ts` (write, read, prune at 50 cap)
- **Unit tests** for `matchExistingPlugin()` heuristic (tag overlap, no match, single plugin)
- **Unit tests** for SSE duplicate dispatch fix (verify event index tracking)
- **Integration tests** for new API endpoints (activation-prompts, activation-history)
- **Frontend**: Vitest + React Testing Library for reducer actions, component rendering

---

## Risk Assessment

| Risk | Mitigation |
|------|-----------|
| SSE fix might break other SSE consumers (ai-edit, gen-evals) | Apply same index-tracking pattern to all three; existing behavior preserved |
| Plugin matching heuristic may give poor suggestions | Confidence threshold + "Create new" always available; additive, never forced |
| activation-history.json grows unbounded | Cap at 50 runs, prune oldest on write |
| LLM prompt generation produces low-quality prompts | Generated prompts are editable suggestions; user reviews before running |
| ConfigContext not available in WorkspaceProvider | Already wrapped -- verify in app component tree |
