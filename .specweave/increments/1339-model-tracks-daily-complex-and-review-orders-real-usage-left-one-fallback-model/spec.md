# Model tracks: Daily, Complex and Review orders, real usage left, one fallback model

## Problem

Owner's request, November 14, 2026: the model, fallback and limit settings are too many and contradict each other, the app does not show real usage left for some accounts, and a thread on a stand-in model is hard to read.

Evidence from the code and this Mac (app repo `repositories/anton-abyzov/specwithcode`):

- Four ordered model lists decide the same thing. "Fallback order" (`providerLimitFallbackModels`), "Everyday work / Hardest work" (`modelLanes`, used as the fallback chain only when Fallback order is empty), "Also served by" (`defaultModelProviders`) and "Reviewer order" (`adversarialReview.reviewers`). The "Also served by" text says the same model elsewhere is tried first; with a Fallback order set, the order wins (`packages/shared/src/providerFallback.ts:857` before `:888`).
- 40 model, fallback and limit rows are spread over Settings > General, Settings > Models, Settings > Projects, the project dialog and two popovers. `ModelLanesSettings` renders on General (all machines) and on Models (one machine). "Model tiers" in the UI is the key `modelLanes`; the key `modelTiers` is shown as "Regular and frontier models", a per-provider grid of 9 providers by 2 dropdowns, mostly "No model".
- A thread copies the project's thread model once at creation. The "threads follow the project model" decision of November 9 was never built. A thread created under GPT-6 Astra stays on Astra after the project moves to Fable 5.2, and the fallback card does not say so.
- The project's thread model has two stores (the project record and a settings override). The override wins (`apps/server/src/project/ProjectDelegation.ts:25`), so the project dialog can change nothing. The limit worker resolves settings without the project (`apps/server/src/orchestration-v2/ProviderFallbackWorker.ts:914`, `:1761`), so launches and fallbacks disagree on "home".
- Copilot Enterprise shows no usage because the token comes only from `gh` signed in as the same login. The cached reading asks the user to sign in to the GitHub CLI with the matching account. The reason is hidden in a tooltip. A paid seat whose premium bucket has no positive `entitlement` maps to zero windows. Copilot on a GHE host is skipped. Devin, Gemini and DeepSeek report nothing, and a limit reply from them never reaches `provider.usageLimits`.
- "Usage unknown" in the order list appears when a reading is over 5 minutes old, though the server re-reads before acting.
- Favorites, model order and "follow newest" are per device and never sync. The Connect relay stores no settings.
- The usage ring on the model chip has no action of its own.

## Scope

In (app repo `repositories/anton-abyzov/specwithcode`, plus `infra/relay` for account sync):

- Three tracks as the one ordered-model concept: Daily, Complex, Review. Default orders, drag-and-drop, per-row state, successor adoption, provider resolution inside a model, a free tail on Daily.
- One resolver chain for launches, limit fallback and reviewer choice.
- Real usage: Copilot without `gh`, GHE hosts, mapper, plan name, visible reasons, ACP limit replies, staleness chip; a usage popover on the model chip.
- One Settings > Models page; removal and folding of settings per the inventory below; migration of existing values.
- Threads say where their model came from and can follow the project.
- Account-wide sync of tracks and favorites through Connect.
- The five bugs listed under Approach.

Out: installing provider CLIs automatically; a new first-run wizard step; changing spending rules (per-token, Vertex and paid routers stay never-automatic); the subscription-resets ledger, alerts and report (sibling increment, split agreed November 14); mobile UI beyond decoding the new keys.

## Acceptance Criteria

- [ ] AC-01: The built-in Daily order is Claude Opus 5.5, Claude Sonnet 5.5, GPT-6.2 Sol and GPT-6 Luna. Complex is Claude Fable 5.2 then GPT-6.2 Astra. Review is Gemini 4 Neon at High then GPT-6.2 Sol. A saved order replaces its built-in order.
- [ ] AC-02: A track entry is a model. Its provider is chosen in this order: the maker's own subscription, then other flat-rate providers serving the same model by most verified room, never a per-token, Vertex or paid-router account unless the entry pins that provider. Only when no provider has room does the chain move to the next entry.
- [ ] AC-03: In Tracks mode, a limited thread tries other sources for its current model and then the other models on its own track. When the track is exhausted here, handoff can use the same track on another machine if enabled. Complex and Review exclude the free tail. The saved legacy fallback order still applies in single-model mode.
- [ ] AC-04: A worker launched without a named model in a project set to "Tracks" starts on the first available entry of the track for its task lane (complex, else Daily). A project set to "One model" behaves as today. Existing projects with a saved thread model stay on "One model".
- [ ] AC-05: An entry follows its family: when the catalog lists a newer version of the same family with the same billing, or the manifest names a successor, the entry resolves to it with no settings change, and the row shows "Follows newest". A pinned entry never moves. `gpt-6.1-sol` and `gpt-6-astra` style slugs are parsed as family plus version.
- [ ] AC-06: Review is on or off per project; the reviewer comes from the Review track, skips the author's model family and refuses with reasons when no entry can run, as in increment 1324.
- [ ] AC-07: Tracks reorder by drag-and-drop and by keyboard, and each row shows one state: Ready with usage left, Sign in, Not installed with an Install action, Limit until a time, or Free.
- [ ] AC-08: Copilot usage is read without `gh` when the Copilot CLI's own sign-in is readable, for github.com and GHE hosts; a paid seat shows its premium or credits percent and reset; an unlimited bucket shows "Unlimited", not unknown; the plan name is shown.
- [ ] AC-09: Any account whose usage cannot be read is listed under "Limits by account" with the reason in plain text and one action (Sign in, Turn on, or Not reported by this provider). A limit reply from an ACP provider marks that account limited until its reset in the picker. A reading older than 5 minutes shows its age, not "Usage unknown".
- [ ] AC-10: Clicking the usage ring on the model chip opens a usage popover: plan name, each window with percent and reset, the threads using the most tokens in this project, and a link to full project usage. The rest of the chip still opens the picker.
- [ ] AC-11: Settings > Models holds the three tracks, a "When a limit hits" group of four rows, and one Advanced disclosure. The removed rows listed in the inventory are gone from General, Projects and the project dialog, and every stored value still applies or is migrated as the inventory says.
- [ ] AC-12: The project's thread model has one store read by launches, the limit worker and the UI. Each thread records whether it follows the project or has its own model; a following thread takes a project change at its next turn; a usage-limit stand-in is not an own model. The fallback card names the model the thread was created with when the project has since changed, with one action to move it.
- [ ] AC-13: Tracks, review switch defaults, favorites, favorite families and follow-newest are stored per account in Connect and reach every signed-in machine and device, newest change per key winning; signed out, they stay local and nothing is lost. Favorites start empty on a new account.
- [ ] AC-14: The first-run provider screen shows a "Start free" card with ChatGPT Free and Copilot Free only when no subscription is detected; no wizard step is added.

- [ ] AC-15: In the same release sweep, Remove clears a rejoined machine's old fleet record and the app's saved connection in one action when the old install is unreachable.

- [ ] AC-16: Cursor usage reading is off by default on every platform and requires an explicit opt-in after a warning about Cursor's private endpoints and account-ban risk.

## Approach

### The model

One contract, `packages/contracts/src/modelTracks.ts`:

```
ModelTrackEntry = { model: string; provider?: ProviderInstanceId; pinned?: boolean; free?: boolean }
ModelTracks     = { daily: ModelTrackEntry[]; complex: ModelTrackEntry[]; review: ModelTrackEntry[] }
```

Storage reuses the keys that already have readers, so nothing is renamed on disk: `modelLanes.routine` is Daily, `modelLanes.complex` is Complex, `adversarialReview.reviewers` is Review. Entries gain the optional `pinned` and `free` fields (old servers ignore unknown fields). Built-in defaults live in `packages/shared/src/modelTracks.ts` (`DEFAULT_MODEL_TRACKS`) and apply when a track is empty, so no value is written for a user who never edits.

`resolveTrack(track, catalog, usage)` in `packages/shared/src/modelTracks.ts` is the single walker: follow family, then pick a provider (AC-02), then report a per-entry state. `effectiveFallbackOrder`, `resolveLaneRouting`, `resolveReviewer` and `tierModelFor` call it. "Also served by" (`defaultModelProviders`) stays as the tie-break inside step two and loses its UI row.

Successors: `modelFamily` and `compareModelVersions` in `packages/shared/src/modelTiers.ts` learn codename slugs (`gpt-6.1-sol` is family `gpt-sol`, version 6.1). `model-manifest.json` gains an optional `succeeds: <slug>` per model; the manifest is fetched from `main` hourly, so a new frontier model with a new name is adopted without an app release.

Regular and frontier per provider: derived, not configured. Regular is the first Daily entry that provider serves, frontier the first Complex entry, then the built-in default. A stored `modelTiers` override still wins and is shown as one line under Advanced with "Reset".

Project choice: `ProjectWorkspaceSettings.threadModelMode: "tracks" | "model"`. New projects get "tracks". A project with a saved thread model keeps "model".

### Settings: before and after

After: Settings > Models has three parts. The project dialog shows the same component at project scope with "Uses app defaults" per row.

1. Tracks: Daily, Complex, Review (with the per-project Review switch).
2. When a limit hits: Action (switch, wait, ask), Switch before the limit, Wait when the reset is close, Use quota before it resets.
3. Advanced, closed by default.

| Today | Key | After | Stored value |
|---|---|---|---|
| Fallback order | `providerLimitFallbackModels` | Removed. Shown under Advanced only while non-empty, as "Custom fallback order" with "Use tracks" | Kept and still wins until cleared |
| (legacy single fallback) | `providerLimitFallbackModelSelection` | Removed | Read as today |
| Everyday work / Hardest work, on General and Models | `modelLanes` | Daily and Complex tracks, on Models only | Same key |
| Seed from favorites | action | Removed; the picker adds a model to a track | n/a |
| Reviewer order | `adversarialReview.reviewers` | Review track | Same key |
| Review depth | `adversarialReview.tier` | Advanced | Same key |
| Review finished features automatically | `adversarialReview.autoOnFeatureComplete` | The Review switch | Same key |
| Regular and frontier models, 9 providers by 2 | `modelTiers` | Removed; derived from tracks. One Advanced line when an override exists | Kept, still wins, "Reset" clears |
| Also served by | `defaultModelProviders` | Removed; automatic provider rule | Kept as tie-break |
| Only these models | `providerLimitFallbackListOnly` | Advanced: "Stay on my tracks" | Same key |
| Where a limited thread can continue (6 vendor lists) | `providerLimitExcludedModels` | Advanced: "Never use automatically", a searchable list of the excluded models only | Same key |
| When a provider runs out | `providerLimitAction` | When a limit hits: Action | Same key |
| Switch before the limit | `providerLimitSwitchAtPercent` | When a limit hits | Same key |
| Wait when the reset is close | `providerLimitWaitUnderMinutes` | When a limit hits | Same key |
| Use quota before it resets | `taskRouting.spendExpiringQuota` | When a limit hits | Same key |
| Auto-resume limited threads | `autoResumeLimitedThreads` | Folded into Action ("switch" and "wait" both resume) ; Advanced keeps the off switch | Same key |
| Auto-continue this project's threads when limits reset | workspace `autoResume` | Removed, dead while the global is on | Honoured if the global is off |
| Snooze limited threads | `snoozeLimitedThreads` | Advanced | Same key |
| Continue on a new subscription automatically | `autoApproveSubscriptionChange` | Advanced | Same key |
| Redeem a banked reset first | `providerLimitRedeemResets` | Advanced, "Spend before switching" group | Same key |
| Spend Codex credits first | `providerLimitSpendCredits` | Same group | Same key |
| Use API credits first | `providerLimitUseApiCredits` | Same group | Same key |
| Other machines, Try first, Use machines with unknown usage | `providerLimitMachineTargets`, `providerLimitTargetOrder`, `providerLimitUnknownUsageEligible` | Advanced: one "Other machines" row; the two sub-rows appear only when a machine is added | Same keys |
| Auto model routing and its six rows | `taskRouting.*` | Advanced: one "Automatic routing" row that opens the six | Same key |
| Learned model preferences | `learnedModelPreferences` | Advanced, shown only when not empty | Same key |
| Use Jev for decisions | `decisionModel` | Advanced | Same key |
| Thread and worker model (Settings > Projects) | override `defaultModelSelection` | Removed; one store | Folded into the project record once |
| Recommended model for threads | project `defaultModelSelection` | "New threads use: Tracks or One model" | Same field |
| Coordinator model, coordinator effort | `coordinatorModelSelection` | Unchanged | Same |
| Model list stars, order, hidden, follow newest | client settings | Unchanged UI; stars and follow-newest sync per account | Moved to the account document, local copy kept |
| Text generation model, Source control writer model | unchanged | Advanced: "Background models" | Same keys |

Count: 40 visible rows on five surfaces become 7 visible rows on one page, plus Advanced. No key is deleted from the contract; removed rows keep decoding and keep their behaviour until the owner clears them.

Migration is one fold at load, flag `modelTracksFolded` in `apps/server/src/serverSettings.ts`, following `foldLegacyProjectSettings`: fold the `defaultModelSelection` override into the project record and delete the override; set `threadModelMode: "model"` where a project has a thread model; leave every other key in place. Sparse writes keep defaults unwritten.

### Bugs fixed here

- A. Two stores for the project's thread model (`ProjectDelegation.ts:20-30`).
- B. The limit worker resolves settings without the project (`ProviderFallbackWorker.ts:914`, `:1761`).
- C. "Also served by" text and order disagree (`providerFallback.ts:857-888`): the chain now tries the same model on another provider before the next entry in every path.
- D. The picker's "Order" row is built from the stand-in, not the original model (`apps/web/src/components/ChatView.tsx:11086`).
- E. `threadModelIdentity` compares models exactly while `limitFallbackPairing` ignores `[1m]` style suffixes (`packages/shared/src/threadModelIdentity.ts:212`).
- F. Copilot: `gh` only, github.com only, `entitlement` rule, lost failure cause (`apps/server/src/provider/copilotUsageLimits.ts:48`, `:162-176`, `:417-499`).
- G. ACP limit replies never reach `provider.usageLimits` (`apps/server/src/provider/acp/acpLimitReply.ts`).
- H. Stale reading shown as "Usage unknown" (`providerFallback.ts:221`, `FallbackOrderList.tsx:89`).
- I. Editing one field of `modelLanes`, `taskRouting` or `adversarialReview` at project scope freezes the whole object as an override (`apps/web/src/components/settings/scopedSettings.ts:269-295`): tracks save per track.

### Account sync

The relay has no settings table. Add `account_settings (account_id, key, value_json, updated_at)` to `infra/relay/src/persistence/schema.ts` with `GET/PUT /v1/account/settings`, authenticated like the existing account routes, value capped at 64 KiB per key. The server module `apps/server/src/connect/AccountSettingsSync.ts` copies the `MachineNicknameSync` shape: per-key `updatedAt`, newest wins, exchange on change and every 5 minutes, capability `accountSettings`. Keys: `modelTracks`, `reviewDefaults`, `favorites`, `favoriteModelFamilies`, `modelFollowLatest`. Providers and provider instances stay per machine; an entry whose model no machine serves shows "Not installed".

### Slices, one PR each, each shippable

1. Tracks core: contract, defaults, resolver, successor parsing, bugs A, B, C, E.
2. Models page: tracks UI with drag-and-drop and row states, "When a limit hits", Advanced, removal of the old rows, fold migration, bug I.
3. Usage: Copilot read, reasons, ACP limits, staleness, usage popover, bugs F, G, H.
4. Threads: follow-or-own record, fallback card wording, bug D.
5. Account sync through Connect and the "Start free" card.

Rejected: a new `modelTracks` settings key (a second store beside `modelLanes`, and a rename migration for nothing); a third model lane (every `MODEL_LANES` consumer hardcodes two; Review stays in `adversarialReview`); syncing through paired machines only (not account-wide, the owner asked for the account); DeepSeek and Gemini in the default free tail (per-token and Vertex billing).

Risks: the Copilot CLI may keep its token only in the system keyring, where the app must not probe; then the read stays on `gh` and AC-08 is met by the visible reason and action (to be confirmed in T-07 before coding). Default tracks change which model an unconfigured install falls back to; the legacy order still wins where set. Relay schema change needs a D1 migration and deploy before the app slice.

## Review

- Reviewer: meta (muse-wonder-1.0)
- Depth: deep
- Required: yes

## Decisions

### Asked
- D-01 Go with the recommended design (tracks, provider rule, Luna and Copilot Free tail, no wizard step) → yes (owner, November 14, 2026).
- D-02 Adversarial review of everything built → Meta Muse Wonder 1.0, highest effort (owner).
- D-03 Fix every bug found during the research → yes (owner).
- D-04 "Regular and frontier models" grid → simplify per the tracks; removed and derived (owner asked, design choice mine).

### Defaulted (change any before sw-do)
- D-05 Existing projects with a saved thread model stay on "One model"; new projects use Tracks → reversible per project.
- D-06 A legacy Fallback order keeps winning until "Use tracks" is clicked → no silent behaviour change.
- D-07 Complex and Review never fall to the free tail; they wait or ask.
- D-08 Storage reuses `modelLanes` and `adversarialReview.reviewers` instead of a new key.
- D-09 Account sync uses a new relay table, not paired-machine exchange.

### Open
- none

## Tasks

### T-01 Track contract, defaults and resolver
- AC: AC-01, AC-02 | Files: repositories/anton-abyzov/specwithcode/packages/contracts/src/modelTracks.ts, repositories/anton-abyzov/specwithcode/packages/contracts/src/taskRouting.ts, repositories/anton-abyzov/specwithcode/packages/contracts/src/index.ts, repositories/anton-abyzov/specwithcode/packages/shared/src/modelTracks.ts, repositories/anton-abyzov/specwithcode/packages/shared/src/modelTracks.test.ts | Test: cd repositories/anton-abyzov/specwithcode/packages/shared && npx vp test run src/modelTracks.test.ts

### T-02 Successor adoption
- AC: AC-05 | Files: repositories/anton-abyzov/specwithcode/packages/shared/src/modelTiers.ts, repositories/anton-abyzov/specwithcode/packages/shared/src/modelTiers.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/provider/model-manifest.json, repositories/anton-abyzov/specwithcode/apps/server/src/provider/ModelManifest.ts | Test: cd repositories/anton-abyzov/specwithcode/packages/shared && npx vp test run src/modelTiers.test.ts

### T-03 One chain for limits, launches and reviewers
- AC: AC-03, AC-04, AC-06 | Files: repositories/anton-abyzov/specwithcode/packages/shared/src/providerFallback.ts, repositories/anton-abyzov/specwithcode/packages/shared/src/providerFallback.test.ts, repositories/anton-abyzov/specwithcode/packages/shared/src/modelLanes.ts, repositories/anton-abyzov/specwithcode/packages/shared/src/adversarialReview.ts, repositories/anton-abyzov/specwithcode/packages/shared/src/threadModelIdentity.ts, repositories/anton-abyzov/specwithcode/apps/server/src/project/ProjectDelegation.ts, repositories/anton-abyzov/specwithcode/apps/server/src/project/WorkerLaunchRoom.ts, repositories/anton-abyzov/specwithcode/apps/server/src/orchestration-v2/ProviderFallbackWorker.ts, repositories/anton-abyzov/specwithcode/apps/server/src/mcp/OrchestratorMcpService.ts, repositories/anton-abyzov/specwithcode/packages/contracts/src/projectWorkspace.ts | Test: cd repositories/anton-abyzov/specwithcode && npx vp test run packages/shared/src/providerFallback.test.ts packages/shared/src/modelLanes.test.ts packages/shared/src/adversarialReview.test.ts packages/shared/src/threadModelIdentity.test.ts apps/server/src/orchestration-v2/ProviderFallbackWorker.test.ts

### T-04 Models page: tracks, limit policy, Advanced
- AC: AC-07, AC-11 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/ModelTracksSettings.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/ModelTrackList.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/LimitPolicySettings.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/ModelSettingsPanel.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/ProjectDefaultsSettings.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/ProviderLimitSettings.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/scopedSettings.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/ProjectWorkspaceSettings.tsx, repositories/anton-abyzov/specwithcode/apps/web/tests/model-tracks/verify.mjs | Test: cd repositories/anton-abyzov/specwithcode && node node_modules/vite-plus/bin/vp build --config apps/web/tests/model-tracks/vite.config.ts && node apps/web/tests/model-tracks/verify.mjs

### T-05 Settings fold and one store for the project model
- AC: AC-11, AC-12 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/serverSettings.ts, repositories/anton-abyzov/specwithcode/apps/server/src/serverSettings.test.ts, repositories/anton-abyzov/specwithcode/packages/shared/src/projectSettings.ts, repositories/anton-abyzov/specwithcode/packages/shared/src/serverSettings.ts | Test: cd repositories/anton-abyzov/specwithcode && npx vp test run apps/server/src/serverSettings.test.ts packages/shared/src/projectSettings.test.ts

### T-06 Threads follow the project or keep their own model
- AC: AC-12 | Files: repositories/anton-abyzov/specwithcode/packages/contracts/src/orchestrationV2.ts, repositories/anton-abyzov/specwithcode/apps/server/src/orchestration-v2/Orchestrator.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/chat/fallbackStatus.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/chat/FallbackStatusCard.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/ChatView.tsx, repositories/anton-abyzov/specwithcode/apps/web/tests/model-tracks/verify.mjs | Test: cd repositories/anton-abyzov/specwithcode && npx vp test run apps/web/src/components/chat/fallbackStatus.test.ts apps/server/src/orchestration-v2/Orchestrator.test.ts

### T-07 Copilot usage, visible reasons, ACP limits
- AC: AC-08, AC-09 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/provider/copilotUsageLimits.ts, repositories/anton-abyzov/specwithcode/apps/server/src/provider/copilotUsageLimits.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/provider/acp/AcpRegistryDriver.ts, repositories/anton-abyzov/specwithcode/apps/server/src/provider/acp/acpLimitReply.ts, repositories/anton-abyzov/specwithcode/apps/server/src/provider/acp/AcpAdapterV2.ts, repositories/anton-abyzov/specwithcode/packages/contracts/src/providerUsageLimits.ts, repositories/anton-abyzov/specwithcode/packages/shared/src/usageLimits.ts, repositories/anton-abyzov/specwithcode/packages/shared/src/providerFallback.ts, repositories/anton-abyzov/specwithcode/apps/web/src/studio/modelAvailability.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/FallbackOrderList.tsx | Test: cd repositories/anton-abyzov/specwithcode && npx vp test run apps/server/src/provider/copilotUsageLimits.test.ts apps/server/src/provider/acp/acpLimitReply.test.ts packages/shared/src/usageLimits.test.ts

### T-08 Usage popover on the model chip
- AC: AC-10 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/chat/ModelUsagePopover.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/chat/ModelUsage.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/chat/ProviderModelPicker.tsx, repositories/anton-abyzov/specwithcode/apps/web/tests/usage-popover/verify.mjs | Test: cd repositories/anton-abyzov/specwithcode && node node_modules/vite-plus/bin/vp build --config apps/web/tests/usage-popover/vite.config.ts && node apps/web/tests/usage-popover/verify.mjs

### T-09 Account settings in Connect
- AC: AC-13 | Files: repositories/anton-abyzov/specwithcode/infra/relay/src/persistence/schema.ts, repositories/anton-abyzov/specwithcode/infra/relay/src/routes/accountSettings.ts, repositories/anton-abyzov/specwithcode/apps/server/src/connect/AccountSettingsSync.ts, repositories/anton-abyzov/specwithcode/apps/server/src/connect/AccountSettingsSync.test.ts, repositories/anton-abyzov/specwithcode/packages/shared/src/accountSettings.ts, repositories/anton-abyzov/specwithcode/packages/contracts/src/environment.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/chat/useModelFamilyFavorites.ts | Test: cd repositories/anton-abyzov/specwithcode && npx vp test run apps/server/src/connect/AccountSettingsSync.test.ts packages/shared/src/accountSettings.test.ts infra/relay

### T-10 Start free card
- AC: AC-14 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/StartFreeCard.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/MachineReadinessChecklist.tsx | Test: cd repositories/anton-abyzov/specwithcode && npx vp test run apps/web/src/components/settings/StartFreeCard.test.tsx

### T-11 Release, installed check, screenshots
- AC: AC-01, AC-07, AC-08, AC-10, AC-11 | Files: repositories/anton-abyzov/specwithcode/CHANGELOG.md | Test: cd repositories/anton-abyzov/specwithcode && bash scripts/release/request-release.sh --released HEAD

### T-12 Verify and close 1339
- AC: AC-01 | Files: .specweave/increments/1339-model-tracks-daily-complex-and-review-orders-real-usage-left-one-fallback-model/spec.md | Test: specweave verify 1339

### T-13 Rejoined machine removal from the release sweep
- AC: AC-15 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/StudioFleetConnections.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/machinesSettings.logic.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/useReplacedMachineRecords.ts | Test: GitHub PR #499 checks and exact-head adversarial review

### T-14 Cursor usage opt-in
- AC: AC-16 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/provider/cursorUsageAccess.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/usage/UsageService.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/usage/CursorUsageEnable.tsx | Test: GitHub PR #613 checks and exact-head adversarial review
