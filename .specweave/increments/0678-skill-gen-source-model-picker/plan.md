---
increment: 0678-skill-gen-source-model-picker
title: Skill-Gen Source Model Picker — Technical Plan
type: plan
status: draft
created: 2026-04-22
architect: sw:architect
---

# Plan: Skill-Gen Source Model Picker

## 1. Architecture Overview

The existing skill-creation flow in vSkill is nominally configurable but effectively hardcoded: `src/eval-server/skill-create-routes.ts:940` reads `body.provider` and falls back to `"claude-cli"`, but ignores `body.model` entirely. The UI side never surfaces a picker at all. This increment closes that gap along three axes — server, UI, CLI — plus persistence to make the choice sticky.

Four cooperating changes:

1. **Server (source of truth for validation)** — `skill-create-routes.ts` reads `body.model`, validates both provider and model against `detectAvailableProviders()` output, returns 400 with a structured error when invalid, and falls back to `claude-cli`/`sonnet` only when both fields are absent.
2. **UI (source of truth for selection)** — `CreateSkillPage.tsx` gains a "Source model" dropdown that mirrors the ComparisonPage selector. The dropdown is populated from `detectAvailableProviders()`, preselects the last-used value from `useStudioPreferences`, and falls back to `claude-cli`/`sonnet` otherwise.
3. **Persistence (source of truth for stickiness)** — extend `useStudioPreferences` with a `skillGenModel?: { provider: string; model: string }` field. Storage key remains `vskill-studio-preferences` (introduced in 0674); no new key.
4. **CLI (source of truth for automation)** — `vskill skill new` gains `--provider` and `--model` flags that populate the same request body as the UI. Defaults match the UI defaults exactly.

## 2. Component Map

| File | Change | Rationale |
|---|---|---|
| `src/eval-server/skill-create-routes.ts` (around line 940) | Read `body.model`; validate provider+model against detection cache; 400 on invalid; preserve legacy defaults | Server validation & dispatch |
| `src/eval-ui/src/pages/CreateSkillPage.tsx` | Add provider+model dropdown wired to `useStudioPreferences().skillGenModel` | Primary UI surface |
| `src/eval-ui/src/hooks/useStudioPreferences.ts` | Add `skillGenModel?: { provider: string; model: string }` field + getter/setter | Persistence |
| `src/cli/skill.ts` (command definition) | Add `--provider`, `--model` options; wire into HTTP body | CLI parity |
| `src/eval-server/__tests__/skill-create-routes.test.ts` | Extend to cover new validation paths | TDD gate |
| `src/eval-ui/src/__tests__/create-skill-model-picker.test.tsx` | New jsdom test for dropdown behavior | TDD gate |
| `src/cli/__tests__/skill-new-flags.test.ts` | New CLI integration test | TDD gate |

**Note on shared component.** The ComparisonPage and the new CreateSkillPage dropdown share UI structure. A refactor into a `<ProviderModelPicker>` component is tempting but out of scope for this 1-day increment. A TODO comment in both files flags the opportunity. A future increment can extract the component without changing either page's behavior.

## 3. Data & Types

Extend `StudioPreferences` type (already exported by 0674):

```ts
interface StudioPreferences {
  // ...existing fields from 0674
  skillGenModel?: { provider: string; model: string };
}
```

Request body type for the skill-create endpoint:

```ts
interface CreateSkillRequest {
  // ...existing fields
  provider?: string;   // default "claude-cli"
  model?: string;      // default "sonnet" when provider is "claude-cli"
}
```

Error response shape:

```ts
{ error: "unknown_provider" | "unknown_model"; validProviders?: string[]; validModels?: string[] }
```

## 4. Validation Pipeline

The server calls `detectAvailableProviders()` (the detection cache shared with 0677) once per request handler invocation. Because detection is cached for 30 seconds, this is effectively free. Validation order:

1. If `body.provider` is present and not in the detected list → 400 `unknown_provider`.
2. If `body.model` is present but `body.provider` is not → treat as `unknown_model` against whatever default provider resolves; cleaner UX than silently defaulting the provider.
3. If `body.provider` is present and `body.model` is present but not in that provider's model list → 400 `unknown_model`.
4. If neither → `{ provider: "claude-cli", model: "sonnet" }`.

Validation runs before any generation work, so invalid requests do not consume LLM budget.

## 5. Persistence Semantics

`useStudioPreferences` in 0674 serializes the whole preferences object to `localStorage["vskill-studio-preferences"]` and listens for the `storage` event to propagate changes across tabs. The new `skillGenModel` field participates in both behaviors automatically.

If the persisted `skillGenModel` references a provider no longer detected in the current session (e.g., Ollama was running last time but is off now), the UI falls back to the default and surfaces a one-time non-modal toast. The persisted value is not cleared — it will become usable again when the provider returns. This avoids thrashing the preference across reboots of a local server.

## 6. CLI Flag Parsing

The existing `vskill skill new` command already uses Commander (or whichever parser is in place). Adding `.option("--provider <string>", "...")` and `.option("--model <string>", "...")` is a one-line change each. Validation happens server-side (consistent with UI). The CLI does a preflight call to `detectAvailableProviders` before the create request to surface unknown-provider errors locally for faster feedback.

## 7. Testing Strategy

- **Unit (Vitest)** — server validation paths: valid, unknown provider, unknown model, defaults preserved, 4 tests.
- **Unit (Vitest)** — `useStudioPreferences` round-trip for `skillGenModel`, including malformed localStorage recovery, 3 tests.
- **jsdom** — `CreateSkillPage` dropdown: renders detected providers, preselects default, persists on change, falls back on unavailable persisted selection, 4 tests.
- **CLI integration** — `vskill skill new --provider X --model Y` produces expected request body; unknown provider exits 2; no flags uses legacy defaults, 3 tests.

## 8. ADRs

### ADR-0678-01: Server-side validation against detection cache (not a static allow-list)

**Status**: Accepted
**Context**: Two validation approaches: (a) hardcode the valid provider set in the server, (b) validate against `detectAvailableProviders()` which is dynamic.
**Decision**: Use (b). The detection cache is the single source of truth for "what providers are available" everywhere else in the product; diverging here would create drift.
**Consequences**: If a user stops their Ollama server mid-session and then POSTs with `provider: "ollama"`, the request is rejected with 400 at the next detection TTL. This is correct behavior — a better failure mode than trying to dispatch to a dead endpoint.

### ADR-0678-02: Do not extract a shared `<ProviderModelPicker>` component in this increment

**Status**: Accepted
**Context**: The ComparisonPage picker and the new CreateSkillPage picker will have near-identical markup.
**Decision**: Keep two implementations for now; flag the extraction opportunity with a TODO. A follow-up increment can do the refactor once both usage sites are stable.
**Consequences**: ~30 lines of duplication, paid for by reduced coordination cost (this increment is 1 day; a premature abstraction would push it to 1.5+ days).

### ADR-0678-03: Preserve legacy defaults unconditionally

**Status**: Accepted
**Context**: Existing callers (including 0670-skill-builder-universal in flight) POST without `provider` or `model`. Breaking them is not acceptable.
**Decision**: When both fields are absent, behavior is bit-identical to today: `provider = "claude-cli"`, `model = "sonnet"`. This is an expansion, not a migration.
**Consequences**: 0670 T-005 can land independently and later adopt explicit selection without any forced update.

## 9. Rollout

1. Land server tests + implementation (validation + default preservation).
2. Land UI tests + dropdown.
3. Land persistence (trivial — one field added to existing type).
4. Land CLI tests + flags.
5. Update README's "Creating a skill" section to document the new options.

No feature flag. Opt-in by user action (picking a non-default) means the change is invisible to users who don't look for it.
