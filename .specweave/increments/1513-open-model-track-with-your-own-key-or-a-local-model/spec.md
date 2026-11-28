# SpecWithCode open-model track: your own key or a local model

## Problem

On November 27, 2026 the owner approved plan C (`decision_anymodel_future`): SpecWithCode should run work on open-weight models with the user's own key or a local runtime. It should do this as a first-class choice, not as a hand-built provider instance. Claude Code and Codex stay native on the user's own plans.

The plumbing exists, but no one can find it:

- `repositories/anton-abyzov/specwithcode/apps/server/src/provider/ProviderInstanceEnvironment.ts:6-30`: explicit API instances keep `ANTHROPIC_BASE_URL` and `OPENAI_BASE_URL`. Consumer-login launches strip them.
- `repositories/anton-abyzov/specwithcode/packages/shared/src/modelBilling.ts:50-99,155-188` classifies DeepSeek, Moonshot (Kimi), Z.ai, Mistral and other hosts as per-token `api`, OpenRouter as `paid-router`, and loopback Ollama or LM Studio as `local`. Coding-plan paths (`/coding`) are `unknown`.
- `repositories/anton-abyzov/specwithcode/apps/web/src/components/ProviderLogoMarks.tsx` already has marks for DeepSeek, Qwen, Kimi, Mistral and Ollama.
- What is missing:
  - a guided way to add such a route (presets with the vendor's Anthropic-compatible endpoint);
  - a clear label in the model picker that a route is "your key" or "local", not a subscription;
  - a track rule so open-model work stays on the Daily track and never silently replaces the Complex track.

The AnyModel bench (increment 1512) shows which models finish agent tasks. The app should show the same verdict where the user picks a model.

## Scope

In:

- Presets for DeepSeek, Kimi (Moonshot), Z.ai GLM, Mistral, OpenRouter (BYOK) and local Ollama or LM Studio, on Claude Code through its Anthropic-compatible base URL.
- Local key storage that is never logged or synced.
- A "Your key" or "Local" label and the list-price note in the picker.
- An opt-in rule to put such a route on the Daily track.
- Docs.

Out:

- Any hosted proxy, and any pooled or resold access.
- Savings claims.
- Coding-plan subscriptions on third-party endpoints, beyond reading them as `unknown`.
- Changes to the Complex or Review track defaults.
- Live bench runs inside the app (link to the bench instead).

## Acceptance Criteria

- [ ] AC-01: Settings > Providers offers "Add an open model". It lists the presets above with their official marks. Choosing one asks only for the key, or for nothing in the local case, and creates a Claude Code instance with the vendor's Anthropic-compatible base URL.
- [ ] AC-02: The key is stored like other provider secrets on this machine only. It never appears in logs, thread transcripts, crash reports or machine sync. A test asserts redaction.
- [ ] AC-03: The model picker shows these routes under "Your key" or "Local", with the provider mark. Their billing reads `api`, `paid-router` or `local` per `modelBilling.ts`, never `subscription`.
- [ ] AC-04: An open-model route joins the Daily track only when the user adds it there. Fallback never moves Complex or Review work onto it without that rule.
- [ ] AC-05: A thread can continue on an open-model route from the same conversation, with approvals and history kept, as with any other instance switch.
- [ ] AC-06: Docs page `docs/studio/open-models.md` explains own-key and local routes, links the AnyModel bench, and states: "SpecWithCode never sells, pools or resells model access."

## Approach

To be refined by the implementing worker after reading the provider settings and picker code. Starting points:

- the `ProviderInstance` settings UI under `apps/web/src/components/settings/`;
- `apps/server/src/provider/ClaudeProvider.ts` for the launch environment;
- `packages/shared/src/providerFallback.ts:443` for unknown-billing fallback;
- `modelBilling.ts` for labels.

Presets are data (`packages/shared/src/openModelPresets.ts`), not code paths. Keep every file under 1,500 lines.

## Decisions

### Asked
- D-01: Plan C approved by the owner (November 27, 2026).
- D-02: Does a switch to D (the anymodel.dev funnel is near zero) also cancel this increment? Asked November 27, 2026; awaiting the owner. Recommended: no, C stands on its own.
### Defaulted (change any before sw-do)
- D-03: The route runs on Claude Code through an Anthropic-compatible endpoint first. OpenCode or Pi routes stay as they are.
### Open
- D-02 above.

## Tasks

### T-01 Presets data and instance creation
- AC: AC-01 | Files: repositories/anton-abyzov/specwithcode/packages/shared/src/openModelPresets.ts, repositories/anton-abyzov/specwithcode/packages/shared/src/openModelPresets.test.ts | Test: vp test run packages/shared/src/openModelPresets.test.ts

### T-02 Add an open model in Settings
- AC: AC-01, AC-02 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/ (exact files chosen by the worker), repositories/anton-abyzov/specwithcode/apps/server/src/provider/ | Test: web and server unit tests for the dialog and redaction

### T-03 Picker labels and track rule
- AC: AC-03, AC-04, AC-05 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/ (picker), repositories/anton-abyzov/specwithcode/packages/shared/src/providerFallback.ts | Test: unit tests plus a headless picker screenshot

### T-04 Docs
- AC: AC-06 | Files: repositories/anton-abyzov/specwithcode/docs/studio/open-models.md | Test: grep -q "never sells, pools or resells" docs/studio/open-models.md
