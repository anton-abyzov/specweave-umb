# Model tracks: Daily, Complex and Review orders, real usage left, one fallback model

## Problem

Owner's request, November 14, 2026: the model, fallback and limit settings are too many and contradict each other, the app does not show real usage left for some accounts, and a thread on a stand-in model is hard to read.

Evidence from the code and this Mac (app repo `repositories/anton-abyzov/specwithcode`):

- Four ordered model lists decide the same thing. "Fallback order" (`providerLimitFallbackModels`), "Everyday work / Hardest work" (`modelLanes`, used as the fallback chain only when Fallback order is empty), "Also served by" (`defaultModelProviders`) and "Reviewer order" (`adversarialReview.reviewers`). The "Also served by" text says the same model elsewhere is tried first; with a Fallback order set, the order wins (`packages/shared/src/providerFallback.ts:857` before `:888`).
- 40 model, fallback and limit rows are spread over Settings > General, Settings > Models, Settings > Projects, the project dialog and two popovers. `ModelLanesSettings` renders on General (all machines) and on Models (one machine). "Model tiers" in the UI is the key `modelLanes`; the key `modelTiers` is shown as "Regular and frontier models", a per-provider grid of 9 providers by 2 dropdowns, mostly "No model".
- A thread copies the project's thread model once at creation. The "threads follow the project model" decision of November 9 was never built. A thread created under GPT-6 Astra stays on Astra after the project moves to Fable 5.2, and the fallback card does not say so.
- The project's thread model has two stores (the project record and a settings override). The override wins (`apps/server/src/project/ProjectDelegation.ts:25`), so the project dialog can change nothing. The limit worker resolves settings without the project (`apps/server/src/orchestration-v2/ProviderFallbackWorker.ts:914`, `:1761`), so launches and fallbacks disagree on "home".
- Copilot Enterprise shows no usage because the token comes only from `gh` signed in as the same login. Cached reading on the M4: "Sign in to the GitHub CLI as abycrash to read Copilot usage". The reason is hidden in a tooltip. A paid seat whose premium bucket has no positive `entitlement` maps to zero windows. Copilot on a GHE host is skipped. Devin, Gemini and DeepSeek report nothing, and a limit reply from them never reaches `provider.usageLimits`.
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

- [ ] AC-01: With nothing saved, the three tracks resolve to the built-in orders: Daily = Claude Opus 5.5, GPT-6.1 Sol, Muse Wonder 1.0, then the free tail GPT-6 Luna; Complex = Claude Fable 5.2, GPT-6 Astra; Review = GPT-6.1 Sol, Muse Wonder 1.0, Gemini 4 Carbon. A model no enabled source lists is skipped. A saved track replaces its built-in order, and a track can be switched off (`modelTracksOff`), which is stored apart from an empty list.
- [ ] AC-02: A track entry is a model; where it runs is decided by one Sources order shared by every track. Default order: the model's own harness first (Claude Code for Claude models, Codex for GPT, Muse Code, Gemini CLI, Grok), then other subscriptions that serve it (GitHub Copilot, Cursor, Devin), then listed order. The person can reorder Sources by drag-and-drop and the saved order wins over the default. A free-tail entry tries a free plan first. A source is used automatically only when it is installed, signed in, lists the model, is billed by plan and has no limit now; per-token, Vertex, paid-router and unknown-billing sources are never picked for a built-in entry and only for an entry the person saved on that exact source. Only when no source can run the model does the chain move to the next entry.
- [ ] AC-03: A limited thread continues down its own track (Complex thread on Complex, a reviewer thread on Review only, everything else on Daily), then the other of Daily and Complex; Complex and Review never use a free-tail entry. The person's choices keep their rank: a saved Fallback order, the same model on another source, the project model and the coordinator's proven model are tried before any built-in entry, built-in entries are tried before the "any ready provider" guess, and "Stay on my tracks" counts only entries the person saved. The picker card, the settings page and the server use the same chain.
- [ ] AC-04: A worker launched without a named model in a project set to "Tracks" starts on the first available entry of the track for its task lane (complex, else Daily). Every project that exists before this ships stays on "One model" and launches as today, with or without a saved thread model; only a project created afterwards, or one the owner switches, uses Tracks.
- [ ] AC-05: An entry follows its family: when a source lists a newer version of the same family, or the manifest names a successor, and both are billed the same way on that source, the entry resolves to it with no settings change, the saved model stays directly behind it, and the row shows "Follows newest".. A pinned entry never moves. Codename slugs are parsed from a published table (`gpt-6.1-sol` is family `gpt-sol` 6.1, `gpt-6-astra` is `gpt-astra` 6, `gpt-6-luna` is `gpt-luna` 6); tiers never merge. The manifest can switch successor adoption off (`successors: false`).
- [ ] AC-06: Review is on or off per project; the reviewer comes from the Review track, skips the author's model family and refuses with reasons when no entry can run, as in increment 1324.
- [ ] AC-07: Each track row shows the model and its sources as chips in the order they will be tried, each chip marked Ready, Sign in, Not installed (with an Install action) or Limit until a time. No percent is shown on the row; usage lives in the popover (AC-10). Tracks and the Sources list reorder by drag-and-drop and by keyboard. A move that cannot work is refused with the reason: a model no source lists cannot be added without its "Not installed" mark, a per-token source cannot be dragged into the automatic part of Sources, a free entry cannot enter Complex or Review, and Review warns when every entry is in one family.
- [ ] AC-08: Copilot usage reads its token in this order: the instance or process environment, the Copilot sign-in file (`~/.config/github-copilot/apps.json`, matched by login and host), then `gh`. A sign-in kept only in the system keyring is never probed; that account shows the reason and a "Sign in with gh" action (AC-09). A paid seat whose premium bucket has a percent but no positive entitlement shows that percent; an unlimited bucket shows "Unlimited"; the plan name is shown. GHE hosts are out of this increment.
- [ ] AC-09: Any account whose usage cannot be read is listed under "Limits by account" with the reason in plain text and one action (Sign in, Turn on, or Not reported by this provider). A limit reply from an ACP provider marks that account limited until its reset in the picker. A reading older than 5 minutes shows its age, not "Usage unknown".
- [ ] AC-10: Clicking the usage ring on the model chip opens a usage popover: plan name, each window with percent and reset, the five threads that used the most tokens in this project over the last 7 days (from `projects.usageRead`), and a link to full project usage. The rest of the chip still opens the picker.
- [ ] AC-11: Settings > Models holds the three tracks, a "When a limit hits" group of four rows, and one Advanced disclosure. The removed rows listed in the inventory are gone from General, Projects and the project dialog, and every stored value still applies or is migrated as the inventory says.
- [ ] AC-12: The project's thread model has one store, the project settings override, written by the project dialog and read by launches, the limit worker and the UI. Each thread records whether it follows the project or has its own model. A following thread takes a project change on the first turn accepted after the change; queued and running turns keep the model they were accepted with; a change of provider goes through the existing handoff and context-fit path. Coordinator threads, workers launched with a named model, and any thread moved by a launch fallback, pre-switch, proven fallback or credit continuation are not followers while moved. A fork follows only when its parent followed and was not on a stand-in. The fallback card names the model the thread was created with when the project has since changed, with one action to move it.
- [ ] AC-13: Tracks, the Sources order, the track off switches, favorites, favorite families and follow-newest are stored per account in Connect and reach every signed-in desktop machine. Each track and each favorite is its own entry with its own stamp, so edits to different tracks on two machines both survive; the relay's receive time breaks ties. Entries are stored as driver plus model, never a machine's instance id. A value over the 64 KiB cap stays local with a visible reason. Account deletion removes the stored settings. Signed out, everything stays local and nothing is lost. Favorites start empty on a new account. Phones only decode the new keys.
- [ ] AC-14: The first-run provider screen shows a "Start free" card with ChatGPT Free and Copilot Free only when no enabled source is signed in to a paid plan (an API-key source, a free plan and a source that reports no plan do not count as a subscription); no wizard step is added.
- [ ] AC-15: On a project set to Tracks the project dialog has one place for models: it shows the Daily, Complex and Review lists, top entry marked as the model new threads start on and the rest as its fallbacks, each editable there or in Settings > Models. "Recommended model for threads", the separate "Fallback order" list and "Only these models" are not shown on Tracks; "Stay on my tracks" replaces the last. A fallback order saved before the switch is offered once as "Add to Daily" and otherwise kept and applied as stored, never dropped. One model projects keep today's fields.

## Approach

### The model

Storage reuses the keys that already have readers, so nothing is renamed on disk: `modelLanes.routine` is Daily, `modelLanes.complex` is Complex, `adversarialReview.reviewers` is Review. Stored entries stay `ModelSelection` (`instanceId` plus `model`), so an older client that re-saves a list loses nothing. A saved entry tries the source it names first, then the other sources of the same model in Sources order. No `pinned` or `free` field is stored on an entry: free is read from the source's plan, pins live in the new sparse key `pinnedTrackModels`, and an off track in `modelTracksOff`. Built-in orders are `DEFAULT_MODEL_TRACKS` in `packages/contracts/src/modelTracks.ts`, fitted to the machine by `packages/shared/src/modelTracks.ts`; nothing is written for a person who never edits.

Sources: the one ordered list of harnesses and subscriptions, stored in the existing `defaultModelProviders` key ("Also served by" today). Empty means the default order of AC-02. `providersForModel` ranks by the saved order, a free plan for a free entry, the model's own harness, plan billing before per-token, most room, listed order.

Origin decides trust. Every chain entry is marked built-in or saved by the person (`FallbackChain.builtIn`). The three spending guards stay as they are for saved entries (naming is consent). A built-in entry gets the trust of an unnamed guess: never per-token, never Gemini spend, never an unknown-billing agent, never ahead of a choice the person made. `effectiveFallbackOrder`, `resolveLaneRouting`, `resolveReviewer` and `tierModelFor` read the tracks through `effectiveModelLanes` and `defaultTrackSelections`.

Successors: `modelFamily` and `compareModelVersions` in `packages/shared/src/modelTiers.ts` learn codename slugs (`gpt-6.1-sol` is family `gpt-sol`, version 6.1). `model-manifest.json` gains an optional `succeeds: <slug>` per model and a top-level `successors: false` switch; both are carried to the shared resolver on the provider model (`ServerProviderModel.succeeds` in `packages/contracts/src/server.ts`). The manifest is fetched from `main` hourly, so a new frontier model with a new name is adopted without an app release, and a bad successor is undone by publishing a newer file without it.

Regular and frontier per provider: derived, not configured. Regular is the first Daily entry that provider serves, frontier the first Complex entry, then the built-in default. A stored `modelTiers` override still wins and is shown as one line under Advanced with "Reset".

Project choice: `ProjectWorkspaceSettings.threadModelMode: "tracks" | "model"`, absent means "model". A new project is created with "tracks" through the workspace store and its revision rules. No existing project is rewritten.

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
| Also served by | `defaultModelProviders` | Becomes the Sources list: one drag-and-drop order of harnesses and subscriptions with availability | Same key, a saved order still ranks first |
| Only these models | `providerLimitFallbackListOnly` | Advanced: "Stay on my tracks" | Same key |
| Where a limited thread can continue (6 vendor lists) | `providerLimitExcludedModels` | Advanced: "Never use automatically", a searchable list of the excluded models only | Same key |
| When a provider runs out | `providerLimitAction` | When a limit hits: Action | Same key |
| Switch before the limit | `providerLimitSwitchAtPercent` | When a limit hits | Same key |
| Wait when the reset is close | `providerLimitWaitUnderMinutes` | When a limit hits | Same key |
| Use quota before it resets | `taskRouting.spendExpiringQuota` | When a limit hits | Same key |
| Auto-resume limited threads | `autoResumeLimitedThreads` | Folded into Action ("switch" and "wait" both resume) ; Advanced keeps the off switch | Same key |
| Auto-continue this project's threads when limits reset | workspace `autoResume` | Shown in the project dialog only while the global switch is off | Same key |
| Snooze limited threads | `snoozeLimitedThreads` | Advanced | Same key |
| Continue on a new subscription automatically | `autoApproveSubscriptionChange` | Advanced | Same key |
| Redeem a banked reset first | `providerLimitRedeemResets` | Advanced, "Spend before switching" group | Same key |
| Spend Codex credits first | `providerLimitSpendCredits` | Same group | Same key |
| Use API credits first | `providerLimitUseApiCredits` | Same group | Same key |
| Other machines, Try first, Use machines with unknown usage | `providerLimitMachineTargets`, `providerLimitTargetOrder`, `providerLimitUnknownUsageEligible` | Advanced: one "Other machines" row; the two sub-rows appear only when a machine is added | Same keys |
| Auto model routing and its six rows | `taskRouting.*` | Advanced: one "Automatic routing" row that opens the six | Same key |
| Learned model preferences | `learnedModelPreferences` | Advanced, shown only when not empty | Same key |
| Use Jev for decisions | `decisionModel` | Advanced | Same key |
| Thread and worker model (Settings > Projects) | override `defaultModelSelection` | Row removed from Settings > Projects; the project dialog writes this store | Same key, the one store |
| Recommended model for threads | project `defaultModelSelection` | "New threads use: Tracks or One model", saved to the override | Mirrored for older builds |
| Coordinator model, coordinator effort | `coordinatorModelSelection` | Unchanged | Same |
| Model list stars, order, hidden, follow newest | client settings | Unchanged UI; stars and follow-newest sync per account | Moved to the account document, local copy kept |
| Text generation model, Source control writer model | unchanged | Advanced: "Background models" | Same keys |

Count: 40 visible rows on five surfaces become 7 visible rows on one page, plus Advanced. No key is deleted from the contract; removed rows keep decoding and keep their behaviour until the owner clears them.

Migration: none at load. The one store for the project model is the override, the direction `foldLegacyProjectSettings` already folds, so older builds and other machines keep reading it. The project dialog writes the override (and still mirrors the project record for builds before the fold). Every other key stays in place. Sparse writes keep defaults unwritten.

### Bugs fixed here

- A. Two stores for the project's thread model (`ProjectDelegation.ts:20-30`): a save from the project dialog now removes an older override, so the newest save is the answer.
- B. The limit worker calls `resolveProjectSettings` without the project record (`ProviderFallbackWorker.ts:914`, `:1761`), so on an install that has not folded, a model saved only on the project record is missing from the limit rule. Pinned by a test with the model on the record only.
- C. "Also served by" text and order disagree (`providerFallback.ts:857-888`): the chain now tries the same model on another provider before the next entry in every path.
- D. The picker's "Order" row is built from the stand-in, not the original model (`apps/web/src/components/ChatView.tsx:11086`).
- E. `threadModelIdentity` compares models exactly while `limitFallbackPairing` ignores `[1m]` style suffixes (`packages/shared/src/threadModelIdentity.ts:212`).
- F. Copilot: `gh` only, github.com only, `entitlement` rule, lost failure cause (`apps/server/src/provider/copilotUsageLimits.ts:48`, `:162-176`, `:417-499`).
- G. ACP limit replies never reach `provider.usageLimits` (`apps/server/src/provider/acp/acpLimitReply.ts`).
- H. Stale reading shown as "Usage unknown" (`providerFallback.ts:221`, `FallbackOrderList.tsx:89`).
- I. Editing one field of `modelLanes`, `taskRouting` or `adversarialReview` at project scope freezes the whole object as an override (`apps/web/src/components/settings/scopedSettings.ts:269-295`): tracks save per track.

### Account sync

The relay has no settings table. Add `account_settings (account_id, key, value_json, updated_at)` to `infra/relay/src/persistence/schema.ts` with `GET/PUT /v1/account/settings`, authenticated like the existing account routes, value capped at 64 KiB per key. The server module `apps/server/src/connect/AccountSettingsSync.ts` copies the `MachineNicknameSync` shape: per-key `updatedAt`, newest wins, exchange on change and every 5 minutes, capability `accountSettings`. Entries, each with its own stamp: `track.daily`, `track.complex`, `track.review`, `tracksOff`, `sources`, `reviewDefaults`, one per favorite, `favoriteModelFamilies`, `modelFollowLatest`. Values are normalised to driver plus model before leaving the machine. Favorites are browser settings, so the web client pushes them to its server through a new `accountSettings.put` request and reads them back. The relay stamps receive time and deletes the rows with the account. Providers and provider instances stay per machine; an entry whose model no machine serves shows "Not installed".

### Slices, one PR each, each shippable

1. Tracks core: contract, defaults, resolver, successor parsing, bugs A, B, C, E. Built-in orders act only as the last guess of the limit fallback here; the existing tier lists show the built-in order as their empty state so the page matches the behaviour. Launch routing by Tracks starts with slice 2's project choice.
2. Models page: tracks UI with drag-and-drop and row states, "When a limit hits", Advanced, removal of the old rows, fold migration, bug I.
3. Usage: Copilot read, reasons, ACP limits, staleness, usage popover, bugs F, G, H.
4. Threads: follow-or-own record, fallback card wording, bug D.
5. Account sync through Connect (relay migration and deploy first, app syncs only when the relay reports the `accountSettings` capability) and the "Start free" card.

Rejected: a new `modelTracks` settings key (a second store beside `modelLanes`, and a rename migration for nothing); a third model lane (every `MODEL_LANES` consumer hardcodes two; Review stays in `adversarialReview`); syncing through paired machines only (not account-wide, the owner asked for the account); DeepSeek and Gemini in the default free tail (per-token and Vertex billing).

Risks: checked November 14 on the M4 without any Keychain call: the Copilot CLI keeps only login names in `~/.copilot/config.json` (token in the keyring), while `~/.config/github-copilot/apps.json` holds a readable token per host and login. So an account signed in through the editor plugin reads without `gh`; a CLI-only account (the Enterprise seat here) shows the reason and action. Default tracks change which model an unconfigured install falls back to; the legacy order still wins where set. Relay schema change needs a D1 migration and deploy before the app slice.

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

- D-10 Sources is one global order, not one per model: a model row shows the sources in that order, and a saved entry can still name its first source (owner asked for a reorderable, validated source order, November 14).
- D-11 Track rows show availability per source, not percent used; usage moves to the popover (owner, November 14).
- D-12 Existing projects never move to Tracks on their own; built-in orders never outrank a choice the person saved (review round 1).
- D-13 With no reviewers saved, the reviewer is the built-in Review order first, then the per-provider frontier models as today.
- D-14 "Also served by" order keeps ranking first where saved; the harness-first rule is the default only.
- D-15 GHE Copilot hosts and a credits bucket are cut from this increment (no fixture, per-host token needed).

### Review round 1 (Muse Wonder 1.0, design, "fix first")
All 13 findings re-checked against the code; 12 accepted and folded into the ACs and Approach above, one narrowed (free tail on a paid maker account: still plan-billed, now ordered after a free plan). Report: `reports/review-muse-wonder-1.0.md`.

### Open
- none

## Tasks

### T-01 Track contract, defaults and resolver
- AC: AC-01, AC-02 | Files: repositories/anton-abyzov/specwithcode/packages/contracts/src/modelTracks.ts, repositories/anton-abyzov/specwithcode/packages/contracts/src/taskRouting.ts, repositories/anton-abyzov/specwithcode/packages/contracts/src/index.ts, repositories/anton-abyzov/specwithcode/packages/shared/src/modelTracks.ts, repositories/anton-abyzov/specwithcode/packages/shared/src/modelTracks.test.ts, repositories/anton-abyzov/specwithcode/packages/shared/src/modelVendor.ts, repositories/anton-abyzov/specwithcode/packages/shared/src/fallbackOptions.ts, repositories/anton-abyzov/specwithcode/packages/shared/src/modelTiers.ts, repositories/anton-abyzov/specwithcode/packages/shared/src/modelTiers.test.ts, repositories/anton-abyzov/specwithcode/packages/shared/src/providerFallback.ts, repositories/anton-abyzov/specwithcode/packages/shared/src/providerFallback.exclusions.test.ts, repositories/anton-abyzov/specwithcode/packages/shared/package.json | Test: cd repositories/anton-abyzov/specwithcode/packages/shared && npx vp test run src/modelTracks.test.ts src/modelTiers.test.ts src/providerFallback.test.ts src/providerFallback.exclusions.test.ts

### T-02 Successor adoption
- AC: AC-05 | Files: repositories/anton-abyzov/specwithcode/packages/shared/src/modelTiers.ts, repositories/anton-abyzov/specwithcode/packages/shared/src/modelTiers.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/provider/model-manifest.json, repositories/anton-abyzov/specwithcode/apps/server/src/provider/ModelManifest.ts, repositories/anton-abyzov/specwithcode/packages/contracts/src/server.ts, repositories/anton-abyzov/specwithcode/packages/shared/src/modelFamilies.ts | Test: cd repositories/anton-abyzov/specwithcode/packages/shared && npx vp test run src/modelTiers.test.ts

### T-03 One chain for limits and reviewers, bugs A, B, C, E
- AC: AC-03, AC-06 | Files: repositories/anton-abyzov/specwithcode/packages/shared/src/providerFallback.ts, repositories/anton-abyzov/specwithcode/packages/shared/src/modelTracks.test.ts, repositories/anton-abyzov/specwithcode/packages/shared/src/adversarialReview.ts, repositories/anton-abyzov/specwithcode/packages/shared/src/adversarialReview.test.ts, repositories/anton-abyzov/specwithcode/packages/shared/src/threadModelIdentity.ts, repositories/anton-abyzov/specwithcode/packages/shared/src/threadModelIdentity.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/project/ProjectDelegation.ts, repositories/anton-abyzov/specwithcode/apps/server/src/project/ProjectDelegation.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/project/ProjectService.ts, repositories/anton-abyzov/specwithcode/apps/server/src/orchestration-v2/ProviderFallbackWorker.ts, repositories/anton-abyzov/specwithcode/apps/server/src/provider/ModelManifest.test.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/ModelLanesSettings.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/ModelLanesSettings.test.tsx | Test: cd repositories/anton-abyzov/specwithcode && npx vp test run packages/shared/src/providerFallback.test.ts packages/shared/src/modelTracks.test.ts packages/shared/src/adversarialReview.test.ts packages/shared/src/threadModelIdentity.test.ts apps/server/src/project/ProjectDelegation.test.ts apps/server/src/orchestration-v2/ProviderFallbackWorker.test.ts apps/web/src/components/settings/ModelLanesSettings.test.tsx

### T-04 Models page: tracks, limit policy, Advanced
- AC: AC-07, AC-11 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/ModelTracksSettings.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/ModelTrackList.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/ModelSourcesList.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/ModelLanesSettings.tsx, repositories/anton-abyzov/specwithcode/packages/shared/src/modelTrackRules.ts, repositories/anton-abyzov/specwithcode/packages/contracts/src/settings.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/LimitPolicySettings.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/ModelSettingsPanel.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/ProjectDefaultsSettings.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/ProviderLimitSettings.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/scopedSettings.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/ProjectWorkspaceSettings.tsx, repositories/anton-abyzov/specwithcode/apps/web/tests/model-tracks/verify.mjs | Test: cd repositories/anton-abyzov/specwithcode && node node_modules/vite-plus/bin/vp build --config apps/web/tests/model-tracks/vite.config.ts && node apps/web/tests/model-tracks/verify.mjs

### T-05 Project choice (Tracks or One model) and launch routing
- AC: AC-04, AC-11, AC-12 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/serverSettings.ts, repositories/anton-abyzov/specwithcode/apps/server/src/serverSettings.test.ts, repositories/anton-abyzov/specwithcode/packages/shared/src/projectSettings.ts, repositories/anton-abyzov/specwithcode/packages/shared/src/serverSettings.ts | Test: cd repositories/anton-abyzov/specwithcode && npx vp test run apps/server/src/serverSettings.test.ts packages/shared/src/projectSettings.test.ts

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

### T-13 One model list in the project dialog on Tracks
- AC: AC-15 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/ProjectWorkspaceSettings.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/ProjectWorkspaceSettings.test.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/ProviderLimitSettings.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/ModelTracksSettings.tsx, repositories/anton-abyzov/specwithcode/apps/web/tests/model-tracks/verify.mjs | Test: cd repositories/anton-abyzov/specwithcode/apps/web && npx vp test run src/components/studio/ProjectWorkspaceSettings.test.tsx

### T-11 Release, installed check, screenshots
- AC: AC-01, AC-07, AC-08, AC-10, AC-11 | Files: repositories/anton-abyzov/specwithcode/CHANGELOG.md | Test: cd repositories/anton-abyzov/specwithcode && bash scripts/release/request-release.sh --released HEAD

### T-12 Verify and close 1339
- AC: AC-01 | Files: .specweave/increments/1339-model-tracks-daily-complex-and-review-orders-real-usage-left-one-fallback-model/spec.md | Test: specweave verify 1339

## Addendum: per-model routes (November 18, 2026)

Anton's question on Complex > Claude Fable 5.2 ("Claude Ready, then Cursor Ready"): does the app scan every provider and take whichever lists the model? Yes. `providersForModel` takes every enabled provider whose catalog lists the model (`sameModelOn`), then ranks them by the global Sources order, a free plan for a free entry, the maker's harness, plan billing before per-token, most room, then listed order. Per-token and unknown-billing sources never start work on their own (`isHeldSource`). There is no per-model control.

What M4 actually lists, read from the provider caches on November 18, 2026: Claude Code and Cursor list `claude-fable-5-2`; both Copilot accounts list only `claude-fable-5`; Devin's catalog lists two SWE models and no Fable; OpenRouter is not set up. So Claude itself serves Fable 5.2, and Cursor is the second source. One bug found: a built-in row takes "any release of its family" (`family: true`), and `newestOfFamily` returns an older release too, so a built-in Fable 5.2 row also routes to Copilot running Fable 5. An older release may stand in on the maker's own harness, and elsewhere only when no source lists the model or a newer one.

### Approach

Route: for one model, the sources it may run on, in order. Stored in a new optional machine key `modelRoutes` (schema in `packages/contracts/src/modelRoutes.ts`, one line each in `ServerSettings` and `ServerSettingsPatch`), keyed by the model's identity key (`claude-fable-5-2`, the same key Copilot's `claude-fable-5.2` reduces to), so every spelling of one model shares one route. Each route holds `order` (sources the person ranked, first to last), `dropped` (never run this model there), `pinned` (only the first source in `order`, no fallback to another source) and `allowed` (paid or unknown-billing sources the person said "always allow for this model" to). A model with no route keeps the automatic order above. Nothing is written until the person changes a route; "Use the automatic order" deletes it.

One function applies a route, `routeSources` in `packages/shared/src/modelRoutes.ts`, on top of `providersForModel`. Its readers are `describeTrack` (the Models page), `defaultTrackSelections` and `launchTrackLanes` (new threads and workers), and the review track (`adversarialReview`). A dropped source loses everywhere, including the source a saved entry names and the built-in "best" pick; a pinned route returns one source. `modelTiers`, `advisor` and the limit fallback chain keep today's order in this slice.

Cost and limit per source: each route source shows how it bills (the provider's plan name, such as "Claude Max", for a subscription; "Credits" for Cursor and Devin; "Per token" for API keys and OpenRouter; "Billing unknown") and its limit chip (Ready, Limit until 14:05, Not signed in).

Paid ask: a per-token or unknown-billing source is never used silently. Listing one in a route makes it eligible; before its first run the app asks on the existing access card (`AccessRequests`, new subject kind `source`): "Run Claude Fable 5.2 on OpenRouter? Billed per token." with Allow once, Always allow for this model, and Deny. "Always allow" writes the source into the route's `allowed`. Denied, timed out, or launched from a place with no thread to ask in (a new thread from the composer), the source is skipped and the next one is tried. Today's consent rules stay as they are: a saved track entry that names a held source, or a held source named in the Sources order, still runs without asking.

Available via: under each route, every source known to offer the model, including ones not installed or off, each with its fix (Install, Sign in, Turn on, Open Providers). An installed provider's live catalog always wins. For a provider with no live catalog, a small approximate table (`KNOWN_MODEL_OFFERS` in `packages/shared/src/modelOffers.ts`) answers, limited to offers seen in a live catalog: Fable 5.2 on Claude Code, Cursor and Devin; Fable 5 on GitHub Copilot. Copilot is never shown for Fable 5.2.

### Acceptance Criteria (routes)

- [ ] AC-16: Each track row opens its route: the sources that will run that model, first to last, with a cost label and limit chip each. The person can reorder them (drag or keyboard), drop one, or pin one; the change is saved under that model only and applies on every track that lists the model. A model with no saved route shows "Automatic order" and runs as before; "Use the automatic order" clears the route.
- [ ] AC-17: A dropped source is never used for that model: not on the Models page, not when a thread or worker launches, not on Review, even when a saved entry names it. A pinned route uses only its pinned source; when that source cannot run, the chain moves to the next model, never to another source.
- [ ] AC-18: A per-token or unknown-billing source in a route asks before its first run on the access card, with Allow once, Always allow for this model, and Deny. Always allow is stored in the route and later launches run without asking. Denied, unanswered, or with no thread to ask in, the source is skipped. Nothing paid runs silently.
- [ ] AC-19: "Available via" lists every source known to offer the model: installed ones from their live catalog, others from the known-offers table, each with its state and one fix. An installed provider whose catalog does not list the model is not shown. On M4 Fable 5.2 shows Claude Code and Cursor; on a machine without Devin it also shows Devin, Not installed, with Install; Copilot is never listed for Fable 5.2.
- [ ] AC-20: On a built-in row, an older release of the family stands in on the maker's own harness (GPT-6.1 Sol on Codex for GPT-6.2 Sol), and on any other source only while no source here lists the model or a newer release: with Claude Code and Cursor listing Fable 5.2, Copilot's Fable 5 does not serve the Fable 5.2 row. On a machine where nothing lists the model, the older release still stands in, as before.

### T-14 Per-model routes
- AC: AC-16, AC-17, AC-18, AC-19, AC-20 | Files: repositories/anton-abyzov/specwithcode/packages/contracts/src/modelRoutes.ts, repositories/anton-abyzov/specwithcode/packages/contracts/src/settings.ts, repositories/anton-abyzov/specwithcode/packages/contracts/src/accessRequest.ts, repositories/anton-abyzov/specwithcode/packages/shared/src/modelRoutes.ts, repositories/anton-abyzov/specwithcode/packages/shared/src/modelRoutes.test.ts, repositories/anton-abyzov/specwithcode/packages/shared/src/modelOffers.ts, repositories/anton-abyzov/specwithcode/packages/shared/src/modelTracks.ts, repositories/anton-abyzov/specwithcode/packages/shared/src/modelTrackRules.ts, repositories/anton-abyzov/specwithcode/apps/server/src/project/TaskRouting.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/ModelRouteCard.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/ModelRouteCard.test.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/ModelTracksSettings.tsx | Test: cd repositories/anton-abyzov/specwithcode && npx vp test run packages/shared/src/modelRoutes.test.ts apps/web/src/components/settings/ModelRouteCard.test.tsx
