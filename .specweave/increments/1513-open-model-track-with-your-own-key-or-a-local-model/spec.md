# SpecWithCode open-model track: your own key or a local model

## Problem

On November 27, 2026 the owner approved plan C (`decision_anymodel_future`). SpecWithCode should run work on open-weight models with the user's own key or a local runtime, offered as a first-class choice rather than a hand-built provider instance. Claude Code and Codex stay native on the user's own plans. On November 28, 2026 the owner confirmed that C goes ahead whatever the anymodel.dev funnel shows.

The plumbing exists, but no one can find it:

- `repositories/anton-abyzov/specwithcode/apps/server/src/provider/ProviderInstanceEnvironment.ts:6-30` keeps `ANTHROPIC_BASE_URL` and `ANTHROPIC_AUTH_TOKEN` on explicit API instances. Consumer-login launches strip them.
- `repositories/anton-abyzov/specwithcode/packages/shared/src/modelBilling.ts:168-187` classifies DeepSeek, Moonshot (Kimi) and Z.ai hosts as per-token `api`, OpenRouter as `paid-router`, and loopback Ollama or LM Studio as `local`. Coding-plan paths (`/coding`) are `unknown`.
- `repositories/anton-abyzov/specwithcode/apps/web/src/components/ProviderLogoMarks.tsx` already has marks for DeepSeek, Kimi and Ollama.

What is missing:

- A guided way to add such a route, using presets with the vendor's own Anthropic-compatible endpoint.
- A clear label in the model picker saying a route is "Your key" or "Local", not a subscription.
- A track rule so open-model work runs only where the person put it, and never silently replaces the Complex or Review track.

The AnyModel bench (increment 1512) shows which models finish agent tasks, and the docs link to it.

## Scope

In:

- Presets for DeepSeek, Kimi (Moonshot), Z.ai GLM, OpenRouter (BYOK), and local Ollama and LM Studio.
  - Each runs on Claude Code through the vendor's Anthropic-compatible base URL.
  - Mistral is out: it has no Anthropic-compatible endpoint (D-04).
- The key is stored locally and never logged, synced or printed into a thread.
- A "Your key" or "Local" label and the list-price note in the picker.
- A rule that nothing automatic picks an open-model route: it runs only where the person added it.
- A history handoff when a thread moves between Anthropic and a vendor endpoint.
- Docs.

Out:

- Any hosted proxy, and any pooled or resold access.
- Savings claims.
- Coding-plan subscriptions on third-party endpoints (Kimi Code, the Z.ai or BigModel coding plans), beyond reading them as `unknown`.
- Changes to the Complex or Review track defaults.
- Changing how instances built by hand with a custom base URL behave today (D-05).
- Live bench runs inside the app; the docs link to the bench instead.

## Acceptance Criteria

- [ ] AC-01: The Add provider wizard (Settings > Providers and onboarding) offers "Add an open model".
  - It lists the six presets with their official marks.
  - Choosing a keyed preset asks only for the key. OpenRouter also asks for a model id.
  - Choosing a local preset asks for nothing. The address and model can be changed but are optional; models are discovered from the runtime.
  - The result is a Claude Code instance with the vendor's Anthropic-compatible base URL, the vendor's model ids, and the preset marker row.
- [ ] AC-02: The key is stored like other provider secrets, on this machine only.
  - It never appears in `settings.json`, client settings, logs, crash reports or machine sync.
  - It never appears in a thread transcript: Claude Code's subprocess scrub keeps it out of Bash commands, hooks and stdio MCP servers.
  - No host credential (`ANTHROPIC_API_KEY`, the OAuth token, cloud switches) reaches the vendor or local endpoint.
  - Tests assert redaction and the launch environment.
  - The spike `reports/spike-credentials-and-scrub.md` shows the request-level behaviour.
- [ ] AC-03: The model picker shows these routes with the preset's mark and a "Your key" or "Local" label.
  - Their models' billing reads `api`, `paid-router` or `local` per `modelBilling.ts`, never `subscription`.
  - A list-price note says the vendor bills the key at its own list price, with no numbers or savings claims.
- [ ] AC-04: Nothing automatic picks an open-model route. That covers provider fallback, the any-ready worker pick, Auto task routing, learned preferences, same-model alternates (including a review's reviewer order), the coordinator and worker defaults, and a Complex chain continuing into Daily entries.
  - It runs only on a track or a thread where the person put it.
  - The person can add it to Daily (the documented case) or Complex by hand. The Review track refuses it, since reviews never spend a key.
  - A test proves a Daily launch lands on a route the person added there.
- [ ] AC-05: A thread can move onto or off an open-model route in the same conversation.
  - The permission mode is kept. An approval card still open on the running turn is interrupted, as with any switch.
  - History is kept: by native resume on the same endpoint, and by the budgeted history handoff when the endpoint changes (Anthropic to a vendor, or back).
- [ ] AC-06: The docs page `docs/studio/open-models.md` explains own-key and local routes and links the AnyModel bench. It states: "SpecWithCode never sells, pools or resells model access." `docs/README.md` and `docs/user/providers-claude.md` link to it.

## Approach

1. **Seam** (first commit of app PR #1018).
   - `packages/shared/src/openModelPresets.ts` holds the preset data, `buildOpenModelEnvironment`, the marker reader and `isOpenModelRoute`. It imports contracts only.
   - `ServerProvider.openModelPreset` carries the marker to clients.
2. **Launch and snapshot.**
   - `mergeNativeSubscriptionEnvironment` hardens marker instances only: it blanks host credentials the preset does not set, and forces `CLAUDE_CODE_SUBPROCESS_ENV_SCRUB=1`.
     - A keyed preset whose key rows are empty gets a placeholder token, so Claude Code cannot fall back to the host's claude.ai sign-in.
     - An inherited marker variable is dropped from instances whose rows name no preset.
   - `ClaudeDriver` stamps the following on marker instances:
     - `openModelPreset`;
     - an auth label of "Your key" or "Local". Claude Code reports `ANTHROPIC_AUTH_TOKEN` as an unverified subscription token, so that answer becomes a signed-in `apiKey` (keyed) or `local` sign-in and its warning clears;
     - per-model billing from `classifyBaseUrlBilling(baseUrl, billingProviderId)`;
     - a catalog of the preset's model ids, with no built-in Claude slugs.
   - Local presets discover models from the runtime's `/v1/models`, reusing `localModelServer.ts`, and point the background and subagent slots at the launching model.
   - Crash-report and failure redaction learn the Z.ai key shape.
3. **Switching.**
   - The Claude continuation key folds in a normalized base URL for marker instances.
   - The native-transcript transfer refuses to cross endpoints, so a switch between Anthropic and a vendor takes the budgeted handoff. This avoids replaying signed thinking blocks on another endpoint.
4. **Tracks.**
   - `isHeldSource` holds open-model routes whatever their billing.
   - `trackEntryRefusal` lets a person add them to Daily or Complex by hand and refuses them on Review.
   - The any-ready filter, Auto routing, learned preferences, reviewer alternates, the coordinator and worker defaults, and the model-mode Complex-into-Daily chain skip them unless named.
   - Edits to `providerFallback.ts` (1,932 lines) swap expressions only, with no net growth.
5. **Web.**
   - `AddOpenModelDialog` is reached from the wizard's step 0.
   - New official marks: Z.ai, OpenRouter, LM Studio.
   - The instance icon follows the preset brand.
   - The picker header pill and the tooltip carry the list-price note.
6. **Docs** as AC-06.

Files over 1,500 lines must not grow: `providerFallback.ts`, `ClaudeAdapterV2.ts`, `ModelPickerContent.tsx`, `serverSettings.ts`, `contracts/settings.ts`, `rpc.ts`, `Orchestrator.ts`.

## Decisions

### Asked
- D-01: Plan C approved by the owner (November 27, 2026).
- D-02: A switch to D does not cancel C. The owner answered "Yes, go ahead and do as recommended" on November 28, 2026.
### Defaulted (change any before sw-do)
- D-03: Routes run on Claude Code through an Anthropic-compatible endpoint. OpenCode and Pi routes stay as they are.
- D-04: Presets are DeepSeek, Kimi, Z.ai GLM, OpenRouter, Ollama and LM Studio, with values from the vendors' Claude Code guides read November 28, 2026. Mistral is dropped: docs.mistral.ai lists no Messages endpoint. Kimi Code and the BigModel coding plan are subscriptions, so they are out of scope.
- D-05: Every new rule keys on the `SPECWITHCODE_OPEN_MODEL_PRESET` marker row. Instances built by hand with a base URL behave exactly as before. Hardening those would be an auth change, raised with the owner separately.
- D-06: Preset instances use the default Claude home, so the person's skills and settings apply. `ANTHROPIC_AUTH_TOKEN` outranks a stored claude.ai login (Claude Code authentication docs, spike), and the preset blanks `ANTHROPIC_API_KEY` and `CLAUDE_CODE_OAUTH_TOKEN`.
- D-07: When the endpoint changes, the switch is a history handoff, never a native resume.
- D-08: An open-model route is never picked automatically. A person may put it on Daily or Complex by hand, and Daily is the documented case. Review refuses it, as it refuses other keyed or token-billed routes.
- D-09: OpenRouter asks for one model id, since it serves hundreds. Local presets discover their models; if discovery finds none, the instance shows "No models found at <address>".
### Open
- none

## Tasks

### T-01 Presets data and instance creation
- AC: AC-01 | Files: repositories/anton-abyzov/specwithcode/packages/shared/src/openModelPresets.ts, repositories/anton-abyzov/specwithcode/packages/shared/src/openModelPresets.test.ts, repositories/anton-abyzov/specwithcode/packages/shared/package.json, repositories/anton-abyzov/specwithcode/packages/contracts/src/server.ts | Test: vp test run packages/shared/src/openModelPresets.test.ts

### T-02 Launch hardening, snapshot stamp and model catalog
- AC: AC-01, AC-02, AC-03 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/provider/ProviderInstanceEnvironment.ts, repositories/anton-abyzov/specwithcode/apps/server/src/provider/ProviderInstanceEnvironment.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/provider/Drivers/ClaudeDriver.ts, repositories/anton-abyzov/specwithcode/apps/server/src/provider/openModelRoute.ts, repositories/anton-abyzov/specwithcode/apps/server/src/provider/openModelRoute.test.ts, repositories/anton-abyzov/specwithcode/packages/shared/src/crashReport.ts, repositories/anton-abyzov/specwithcode/packages/shared/src/crashReport.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/orchestration-v2/ProviderFailure.ts, repositories/anton-abyzov/specwithcode/apps/server/src/orchestration-v2/ProviderFailure.test.ts | Test: vp test run apps/server/src/provider/openModelRoute.test.ts apps/server/src/provider/ProviderInstanceEnvironment.test.ts packages/shared/src/crashReport.test.ts

### T-03 Endpoint-aware switching
- AC: AC-05 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/provider/Drivers/ClaudeHome.ts, repositories/anton-abyzov/specwithcode/apps/server/src/provider/Drivers/ClaudeHome.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/orchestration-v2/ProviderSwitchService.ts, repositories/anton-abyzov/specwithcode/apps/server/src/orchestration-v2/ProviderSwitchService.test.ts | Test: vp test run apps/server/src/orchestration-v2/ProviderSwitchService.test.ts apps/server/src/provider/Drivers/ClaudeHome.test.ts

### T-04 Track rule
- AC: AC-04 | Files: repositories/anton-abyzov/specwithcode/packages/shared/src/modelTracks.ts, repositories/anton-abyzov/specwithcode/packages/shared/src/modelTrackRules.ts, repositories/anton-abyzov/specwithcode/packages/shared/src/modelTiers.ts, repositories/anton-abyzov/specwithcode/packages/shared/src/modelLanes.ts, repositories/anton-abyzov/specwithcode/packages/shared/src/taskRouting.ts, repositories/anton-abyzov/specwithcode/packages/shared/src/providerFallback.ts, repositories/anton-abyzov/specwithcode/packages/shared/src/providerFallback.openModel.test.ts | Test: vp test run packages/shared/src/providerFallback.openModel.test.ts packages/shared/src/modelTrackRules.test.ts packages/shared/src/modelTracks.test.ts

### T-05 Add an open model in Settings, marks and icon
- AC: AC-01 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/AddOpenModelDialog.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/AddOpenModelDialog.test.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/openModelInstance.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/openModelInstance.test.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/AddProviderInstanceDialog.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/ProviderLogo.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/ProviderLogoMarks.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/chat/ProviderInstanceIcon.tsx | Test: vp test run apps/web/src/components/settings/openModelInstance.test.ts apps/web/src/components/settings/AddOpenModelDialog.test.tsx

### T-06 Picker label and list-price note
- AC: AC-03 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/chat/ProviderGroupHeader.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/chat/modelStatusIcons.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/chat/modelStatusIcons.test.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/chat/openModelPickerLabel.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/chat/openModelPickerLabel.test.ts | Test: vp test run apps/web/src/components/chat/openModelPickerLabel.test.ts apps/web/src/components/chat/modelStatusIcons.test.tsx, plus a headless picker screenshot

### T-07 Docs
- AC: AC-06 | Files: repositories/anton-abyzov/specwithcode/docs/studio/open-models.md, repositories/anton-abyzov/specwithcode/docs/README.md, repositories/anton-abyzov/specwithcode/docs/user/providers-claude.md | Test: grep -q "never sells, pools or resells" docs/studio/open-models.md
