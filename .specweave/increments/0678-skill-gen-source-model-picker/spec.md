---
increment: 0678-skill-gen-source-model-picker
title: Skill-Gen Source Model Picker — Explicit Provider+Model for vSkill CLI
type: feature
priority: P2
status: planned
created: 2026-04-22
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Skill-Gen Source Model Picker — Explicit Provider+Model for vSkill CLI

## Overview

Today, vSkill's skill-creation flow hardcodes the source model. In `src/eval-server/skill-create-routes.ts:940`:

```ts
const provider = body.provider || "claude-cli";
// model is not read from the request at all
```

As a result, every skill generated via the vSkill CLI or Studio UI uses `claude-cli` with the default model, regardless of what providers are detected. This increment exposes an explicit **source-model picker** for skill generation — mirroring the picker already present on the Comparison and Workspace Run panels — so users can generate a skill draft with any detected provider and model.

Four concurrent deliverables:

1. **UI**: a dropdown in `src/eval-ui/src/pages/CreateSkillPage.tsx` matching the ComparisonPage selector. Options = detected providers × their loaded models.
2. **Server**: `src/eval-server/skill-create-routes.ts:940` is extended to read `body.model`; the hardcoded default becomes `{ provider: "claude-cli", model: "sonnet" }` only when both are absent.
3. **Persistence**: reuse the existing `useStudioPreferences` hook (shipped in 0674, at `src/eval-ui/src/hooks/useStudioPreferences.ts`) with a new key `skillGenModel` = `{ provider: string, model: string }`.
4. **CLI parity**: `vskill skill new --provider ollama --model qwen2.5-coder:7b` flags accepted on the CLI path, surfacing the same capability.

### Explicit scope disjunction

This increment is **not** 0676-skill-gen-model-selection. The 0676 increment targets the separate `vskill-platform` codebase (the `verified-skill.com` Next.js site) — a different repository with a different skill-creation path. This increment (0678) targets the local vSkill CLI developer tool. The two should never be merged or conflated.

### 0670 unlock

This increment unlocks 0670 T-005 (`--engine=anthropic-skill-creator`) to accept any provider/model. 0670's skill-builder-universal currently ships with the same hardcoded path; once 0678 lands, 0670's emitter can pass through the caller's selection.

## Code Location & Scope

**Target codebase:** `repositories/anton-abyzov/vskill/`

**In scope:**
- `src/eval-server/skill-create-routes.ts` — accept `body.model`, default handling
- `src/eval-ui/src/pages/CreateSkillPage.tsx` — dropdown selector
- `src/eval-ui/src/hooks/useStudioPreferences.ts` — new `skillGenModel` key
- `src/cli/skill.ts` (or wherever `vskill skill new` is defined) — `--provider` and `--model` flags
- Tests: unit + jsdom + CLI integration

**Out of scope:**
- LM Studio adapter itself — covered by **0677**
- SKILL.md spec compliance of the emitted file — covered by **0679**
- `vskill-platform` skill generation — covered by **0676** (different codebase)
- Changes to 0670's internal pipeline (0670 consumes this after it lands; no cross-edits in 0678)

## Personas

- **P1 — Privacy-conscious skill author**: wants to generate skills with a local model (LM Studio or Ollama) rather than sending prompts to Claude.
- **P2 — Cost-conscious evaluator**: wants to compare draft quality across providers and pick the cheapest one that meets the bar.
- **P3 — CLI-first developer**: scripts skill generation from a shell; needs the same control as the UI user.

## User Stories

### US-001: UI Dropdown on CreateSkillPage (P1)
**Project**: vskill

**As a** vSkill Studio user opening the Create Skill page
**I want** a provider+model dropdown identical in behavior to the one on Comparison
**So that** I can choose exactly which LLM drafts my skill before the server call is made

**Acceptance Criteria**:
- [ ] **AC-US1-01**: Given `src/eval-ui/src/pages/CreateSkillPage.tsx` renders the Create form, when the page mounts, then it calls `detectAvailableProviders()` (same hook/API as ComparisonPage) and renders a "Source model" dropdown whose options are grouped by provider with model ids as children.
- [ ] **AC-US1-02**: Given the dropdown is rendered and no prior selection exists, when `useStudioPreferences().skillGenModel` is `undefined`, then the dropdown preselects `{ provider: "claude-cli", model: "sonnet" }` and a caption reads "Default".
- [ ] **AC-US1-03**: Given a user selects a provider+model, when selection changes, then `useStudioPreferences().setSkillGenModel({ provider, model })` is called synchronously and `localStorage["vskill-studio-preferences"].skillGenModel` reflects the new value on the very next tick.
- [ ] **AC-US1-04**: Given no providers are detected (all probes failed), when the dropdown renders, then it is disabled with a tooltip: "Install a provider (Ollama / LM Studio / OpenRouter) or run `claude login` to enable model selection."
- [ ] **AC-US1-05**: Given a previously persisted provider is no longer detected in this session, when `CreateSkillPage` mounts, then the component falls back to `{ provider: "claude-cli", model: "sonnet" }` and surfaces a one-time non-modal toast: "Previous selection `<provider>/<model>` unavailable — reverted to default."

---

### US-002: Server Accepts `body.model` (P1)
**Project**: vskill

**As a** vSkill backend consumer
**I want** the skill-create endpoint to honor the caller's model choice
**So that** UI and CLI selections actually reach the generation pipeline

**Acceptance Criteria**:
- [ ] **AC-US2-01**: Given `src/eval-server/skill-create-routes.ts:940`, when the endpoint handler runs, then it reads both `body.provider` and `body.model`; the defaults are applied as `provider = body.provider ?? "claude-cli"` and `model = body.model ?? (provider === "claude-cli" ? "sonnet" : <provider's first model>)`.
- [ ] **AC-US2-02**: Given a request arrives with `body.provider` set to a value not present in `detectAvailableProviders()` output, when validation runs, then the handler returns HTTP 400 with body `{ error: "unknown_provider", validProviders: [...] }` and does not start generation.
- [ ] **AC-US2-03**: Given a request arrives with `body.provider` valid but `body.model` not present in that provider's model list, when validation runs, then the handler returns HTTP 400 with body `{ error: "unknown_model", validModels: [...] }`.
- [ ] **AC-US2-04**: Given a request omits both `body.provider` and `body.model`, when the endpoint handler runs, then it uses `{ provider: "claude-cli", model: "sonnet" }` — the legacy default is preserved so existing callers are not broken.
- [ ] **AC-US2-05**: Given the generation pipeline receives the validated `{ provider, model }`, when it dispatches to `src/eval/llm.ts`, then the dispatch selects the adapter matching `provider` and passes `model` through unchanged.

---

### US-003: Persistence via `useStudioPreferences` (P2)
**Project**: vskill

**As a** returning vSkill Studio user
**I want** my last-chosen skill-gen model to stick
**So that** I don't re-pick the same model every time I open Create

**Acceptance Criteria**:
- [ ] **AC-US3-01**: Given `src/eval-ui/src/hooks/useStudioPreferences.ts` (shipped in 0674), when a new `skillGenModel?: { provider: string; model: string }` field is added to the preferences type, then reading/writing is symmetric with the other fields (same `setX`/`getX` pattern, same localStorage key `vskill-studio-preferences`).
- [ ] **AC-US3-02**: Given a selection is made in one tab, when a second tab is open on the same origin, then the `storage` event handler already registered in 0674 propagates the new `skillGenModel` into the second tab's state without requiring a reload.
- [ ] **AC-US3-03**: Given the persisted `skillGenModel` is malformed (wrong shape, non-string members, parse error), when the hook loads, then it silently resets to `undefined` rather than throwing, and a single `console.warn` is emitted in dev mode only.

---

### US-004: CLI Flag Parity (P2)
**Project**: vskill

**As a** developer scripting skill generation
**I want** `vskill skill new --provider <p> --model <m>` to map exactly to the UI selection
**So that** automation matches interactive behavior

**Acceptance Criteria**:
- [ ] **AC-US4-01**: Given the `vskill skill new` command definition (in `src/cli/skill.ts` or equivalent), when `--provider <string>` and `--model <string>` options are added, then their help text reads "Provider id (e.g., claude-cli, ollama, lm-studio, openrouter)" and "Model id (provider-scoped, e.g., sonnet, qwen2.5-coder:7b)" respectively.
- [ ] **AC-US4-02**: Given the CLI is invoked with `--provider ollama --model qwen2.5-coder:7b`, when the command runs, then the HTTP body sent to the skill-create endpoint includes `{ provider: "ollama", model: "qwen2.5-coder:7b" }`.
- [ ] **AC-US4-03**: Given the CLI is invoked with `--provider <unknown>`, when validation runs locally (before the HTTP call, via the same `detectAvailableProviders` result), then the command exits with code 2 and prints "Unknown provider '<x>'. Valid: [list]" to stderr.
- [ ] **AC-US4-04**: Given the CLI is invoked without either flag, when the command runs, then it uses the same defaults as the UI path (`claude-cli`/`sonnet`) — no prompts, no interactive questions.

## Functional Requirements

- **FR-01**: Server endpoint reads `body.model` alongside `body.provider`.
- **FR-02**: UI dropdown is a faithful copy of the ComparisonPage selector in behavior (not necessarily a shared component — that extraction is optional).
- **FR-03**: Persistence uses `useStudioPreferences` with key `skillGenModel`.
- **FR-04**: CLI flags `--provider` and `--model` produce identical request bodies to UI selections.

## Non-Functional Requirements

- **NFR-01 (Compatibility)**: Existing callers that pass neither `body.provider` nor `body.model` must continue to work unchanged (default `claude-cli`/`sonnet`).
- **NFR-02 (Validation cost)**: Server-side provider/model validation uses the detection cache from 0677 — no extra network calls per request.
- **NFR-03 (Test speed)**: Unit + jsdom suite for this increment runs in < 400 ms.

## Scope Boundaries

- **In scope**: Dropdown, server route, persistence, CLI flags, tests.
- **Out of scope**: LM Studio adapter (0677), SKILL.md shape (0679), `vskill-platform` skill generation (0676).

## Dependencies

- **0677** unlocks a broader provider list (adds LM Studio); 0678 does not hard-block on 0677 (Ollama + OpenRouter + claude-cli are already available), but the feature is most useful when both land together.
- **0670** will consume 0678 in its T-005 to pass through the caller's provider/model through the anthropic-skill-creator engine path.
