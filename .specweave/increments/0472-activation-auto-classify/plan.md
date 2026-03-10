# Plan: Auto-classify Activation Test Expectations

## Overview

Add a two-phase evaluation flow to `activation-tester.ts`: Phase 1 uses a lightweight LLM call to classify unlabeled prompts as related/unrelated based on skill name + tags, then Phase 2 runs the existing activation evaluation. This eliminates false FN results from ambiguous prompts that were incorrectly assumed to mean "should activate."

## Architecture

```
Client (ActivationPanel)
  |
  | Parse prefixes: ! → should_not_activate, + → should_activate, none → "auto"
  v
Server (api-routes.ts /activation-test)
  |
  | Extract name + tags from SKILL.md frontmatter → SkillMeta
  v
activation-tester.ts: testActivation(description, prompts, client, skillMeta?, onResult?)
  |
  |--- Phase 1: classifyExpectation() for each prompt where expected === "auto"
  |    LLM call: "Is '{prompt}' related to a skill named '{name}' with tags [{tags}]?"
  |    Response: {"related": true/false} → resolve to should_activate / should_not_activate
  |    Fallback on error/bad JSON: should_activate (backward compat)
  |    Skip if skillMeta is missing or has no name
  |
  |--- Phase 2: existing evaluate loop (unchanged)
  |    Each prompt now has a resolved expected value
  |
  v
Results (with autoClassified: boolean flag on each result)
```

## Component Changes

### 1. `src/eval/activation-tester.ts` (core logic)

**New types**:
- `SkillMeta`: `{ name: string; tags: string[] }`
- Extend `ActivationPrompt.expected` to include `"auto"`
- Add `autoClassified: boolean` to `ActivationResult`

**New exported function** -- `classifyExpectation(prompt, skillMeta, client)`:
- System prompt: "You classify whether a user prompt is related to a specific AI skill. Respond with ONLY valid JSON: {\"related\": true/false}"
- User prompt: "Skill: {name}\nTags: {tags.join(', ')}\nUser prompt: {prompt}\nIs this prompt related to this skill?"
- Parse response, extract `related` boolean
- Return `"should_activate"` if related, `"should_not_activate"` if not
- On any error or invalid JSON: return `"should_activate"` (backward compat per AC-US2-02)

**Modified function** -- `testActivation(description, prompts, client, skillMeta?, onResult?)`:
- **Phase 1**: Filter prompts where `expected === "auto"`. If `skillMeta` has a name, call `classifyExpectation` for each. If no skillMeta or no name, default to `"should_activate"`. Resolve all auto prompts before proceeding.
- **Phase 2**: Existing evaluation loop runs on all prompts with resolved expectations.
- Set `autoClassified: true` on results that went through Phase 1.

**Backward compatibility**: `skillMeta` is optional. Without it, all `"auto"` prompts default to `"should_activate"`, which is the current behavior for unprefixed prompts.

### 2. `src/eval-server/api-routes.ts` (server)

In the `/activation-test` route handler:
- After reading SKILL.md, parse frontmatter for `name` and `metadata.tags` (or top-level `tags`)
- Construct `SkillMeta` object
- Pass it to `testActivation` as the new optional parameter

Frontmatter parsing: simple regex on the YAML frontmatter block. Extract `name:` value and `tags:` array. No new YAML parser dependency -- the existing codebase already uses regex for frontmatter extraction (see the `description` regex on line 232 of api-routes.ts).

### 3. `src/eval-ui/src/pages/workspace/WorkspaceContext.tsx` (client)

In `runActivationTest`:
- Lines with `+` prefix: `expected: "should_activate"`, strip prefix
- Lines with `!` prefix: `expected: "should_not_activate"`, strip prefix (existing)
- Lines with no prefix: `expected: "auto"` (was `"should_activate"`)

### 4. `src/eval-ui/src/pages/workspace/ActivationPanel.tsx` (UI)

- Update help text below the textarea to document all three conventions: no prefix (auto), `+` (force activate), `!` (not activate)
- In `ResultRow`, show an "Auto" pill/badge when `result.autoClassified` is true, next to the classification pill

### 5. `src/eval-ui/src/types.ts` (types)

- Add `autoClassified?: boolean` to `ActivationResult`

### 6. `src/eval/__tests__/activation-tester.test.ts` (tests)

New test cases:
- `classifyExpectation` returns `"should_activate"` when LLM says `{"related": true}`
- `classifyExpectation` returns `"should_not_activate"` when LLM says `{"related": false}`
- `classifyExpectation` returns `"should_activate"` on LLM error (fallback)
- `testActivation` with mixed prefixes: only `"auto"` prompts go through classification
- `testActivation` without `skillMeta`: auto prompts default to `"should_activate"`

## Design Decisions

**Why name + tags only (not full description)?** The classification prompt must be cheap, fast, and cross-model compatible. Full descriptions can be long and model-specific. Name + tags provide sufficient signal for related/unrelated classification at minimal token cost.

**Why batch Phase 1 before Phase 2?** Clean separation makes debugging easier (inspect Phase 1 results independently) and allows future optimization (e.g., batching all classifications in a single LLM call).

**Why default to `should_activate` on error?** Backward compatibility. The current behavior treats all unprefixed prompts as `should_activate`. If classification fails, we preserve that behavior rather than introducing new false negatives.

**Why optional `skillMeta`?** The existing `testActivation` signature is used by tests and potentially by CLI commands. Making it optional preserves all existing callers without changes.

## Implementation Order

1. Types + `classifyExpectation` in `activation-tester.ts`
2. Two-phase flow in `testActivation`
3. Unit tests for classification logic
4. Server-side frontmatter extraction in `api-routes.ts`
5. Client prefix handling in `WorkspaceContext.tsx`
6. UI updates in `ActivationPanel.tsx` + `types.ts`
