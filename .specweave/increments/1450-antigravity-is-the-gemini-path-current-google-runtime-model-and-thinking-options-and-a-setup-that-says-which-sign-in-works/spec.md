# Antigravity is the Gemini path: current Google runtime, model and thinking options, and a setup that says which sign-in works

## Problem

Google stopped serving Gemini CLI to personal accounts on June 18, 2026, and points everyone at Antigravity. SpecWithCode already has an Antigravity provider, but on November 23, 2026 it lags Google's runtime and does not tell the user which sign-in fits their account. Evidence from M5 is in [reports/research.md](reports/research.md).

- The app installs Google's ACP server `agy_acp_server` 1.3.0 (`apps/server/src/provider/antigravityRelease.ts:1`, hashes checked October 5, 2026). The ACP registry lists 1.5.2 since November 21. Both still answer a prompt on M5 today.
- 1.5.2 changed the session shape. The `model` option is now `gemini-3.8-flash`, with a separate `thinking_level` option (low, medium, high). 1.3.0 sent three combined ids such as `gemini-3.8-flash-high`. The bundled manifest lists only the combined ids (`apps/server/src/provider/model-manifest.json:107, 856-875`), so a bump breaks saved model selections and the default.
- 1.5.2 reports the account's tier in `_meta.antigravity.tier` on `authenticate` and `session/new` (for example "Antigravity Starter Quota", `free-tier`, with an upgrade link). The app shows none of it, so a Workspace account that gets only Gemini 3.8 Flash on a small quota looks the same as a paid one.
- The manifest's compatibility policy for Antigravity still says `=1.1.1` (`apps/server/src/provider/model-manifest.json:81-85`), so the app's own install reads as "unknown".
- The provider form offers four sign-in methods (`packages/contracts/src/settings.ts:1125-1130`) with one line of help. It does not say that a Workspace account has no Antigravity plan, that only Agent Platform can draw on Google Cloud credits, or that Google's terms (section 6) forbid third-party tools on the subscription sign-in.
- Enabling Antigravity needs the Settings page. On a machine an agent sets up, there is no command for it: on M5 it took a hand edit of `settings.json`.
- Upstream T3 Code moved from `agy_acp_server` to the native `agy acp` CLI (1.5+) and now refuses runtimes below 1.5.

## Scope

In:
- Move the managed Antigravity runtime to the current 1.5 line and handle its model, thinking and tier data.
- Setup text that says which sign-in works for which account and who pays, plus the terms warning on the subscription sign-in.
- A CLI command to enable a built-in provider and start its install.
- Align the compatibility policy with the runtime the app installs.

Out:
- The Gemini CLI refusal status and its two actions (increment 1449).
- A new provider or a new sign-in method. The four ACP methods already cover API key, Agent Platform (Vertex AI) and Gemini Enterprise.
- Copying a sign-in from the Antigravity desktop app. The ACP server keeps its own sign-in and Google forbids token extraction.
- Usage limits for Antigravity (upstream `5283f33ca9`), as a follow-up.

## Acceptance Criteria

- [ ] AC-01: A fresh install downloads the current 1.5 runtime on all six platforms, each archive checked against a sha256 and sizes recorded in `antigravityRelease.ts` from the registry entry. The Linux launch passes the registry's `--uid=` argument. A test fails if a platform lacks a hash.
- [ ] AC-02: A machine that already has 1.3.0 keeps working until the user updates, and the provider card offers the update. A thread started after the update runs a turn.
- [ ] AC-03: With a 1.5 runtime the model picker lists the models from the `model` option (for example Gemini 3.8 Flash) and a thinking level option built from `thinking_level`. A saved selection of `gemini-3.8-flash-high`, `-medium` or `-low` maps to `gemini-3.8-flash` plus that level, in settings, thread model selections and model lanes. A unit test covers each mapping and the default alias.
- [ ] AC-04: With a 1.3.0 runtime the picker and turns behave as today. A test runs both shapes through `applyAntigravityAcpModelSelection`.
- [ ] AC-05: The provider card shows the tier name from `_meta.antigravity.tier` when present, and a "See plans" link to its `upgradeUri` when the tier id is `free-tier`. With no tier data the card is unchanged.
- [ ] AC-06: Each sign-in method in the Antigravity form has one sentence saying who it is for and who pays: Google account (a personal account with Google AI Pro or Ultra; a Workspace account gets a small starter quota), Gemini Enterprise (a company licence, needs project and location), Gemini API key (AI Studio, billed to the key's project), Agent Platform (a Google Cloud project, the only method Cloud credits can pay for). The phrases exist in all nine locales.
- [ ] AC-07: Choosing Google account shows a notice before sign-in: Google's terms restrict third-party tools on this sign-in to one person working interactively, and Google can suspend the account. Background and delegated threads never start on an Antigravity instance that uses this method unless the user turned on a per-instance switch, off by default. A server test covers the refusal and its message.
- [ ] AC-08: `specweave-studio provider enable antigravity --install` enables the provider on this machine, starts the managed install and prints its progress and final state. It never signs in. A CLI test covers an already-enabled provider and a failed download.
- [ ] AC-09: The bundled compatibility policy marks the installed 1.5 line supported and 1.3.0 graceful, and the policy test covers both.

## Approach

1. `antigravityRelease.ts`, `AntigravityInstallation.ts`: new version, six hashes and sizes, Linux `--uid=`. Decide D-01 first.
2. `AntigravityAcpSupport.ts`, `AntigravityProtocol.ts`, `model-manifest.json`, `packages/contracts/src/model.ts`: read both session shapes, map old ids, set `thinking_level` through the existing `thought_level` path in `AcpSessionConfig.ts:103`.
3. `AntigravityDriver.ts`, provider snapshot contracts, the provider card: tier name and link.
4. `packages/contracts/src/settings.ts` and the web form: per-method sentences and the terms notice. Server: the background-thread refusal in turn start.
5. `apps/server/src/cli/`: the `provider enable` command, calling the same install service as the Settings button.
6. `model-manifest.json`: compatibility ranges.

Risks:
- Google changes the runtime weekly. Pin a version and keep the hashes; never follow "latest".
- The terms reading comes from Google's published terms plus unofficial forum replies. Keep the notice factual and link the terms.
- Upstream's sign-in through `agy acp --login` uses a pasted code; that flow needs its own design if D-01 picks the CLI.

Rejected:
- Following the registry version at run time. An unpinned 100 MB binary with no recorded hash is a supply-chain risk.
- Adding a separate "Gemini (Vertex)" provider. Agent Platform on the Antigravity provider already does this.

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01 Stay on Google's registry binary `agy_acp_server` 1.5.2 for this increment, and plan the move to the native `agy acp` CLI (what upstream did) as its own increment → default (reversible). The registry binary is what Google lists for ACP clients, and the CLI changes sign-in.
- D-02 Background and delegated threads are refused on the subscription sign-in by default, with a per-instance switch → default (reversible)
- D-03 The tier is shown as Google names it, never mapped to our own plan names → default
### Open
- none

## Tasks

### T-01 Current runtime on six platforms
- AC: AC-01, AC-02, AC-09 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/provider/antigravityRelease.ts, repositories/anton-abyzov/specwithcode/apps/server/src/provider/AntigravityInstallation.ts, repositories/anton-abyzov/specwithcode/apps/server/src/provider/AntigravityInstallation.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/provider/model-manifest.json, repositories/anton-abyzov/specwithcode/apps/server/src/provider/providerCompatibility.test.ts | Test: node node_modules/vite-plus/bin/vp test run apps/server/src/provider/AntigravityInstallation.test.ts apps/server/src/provider/providerCompatibility.test.ts

### T-02 Model and thinking options for both runtime shapes
- AC: AC-03, AC-04 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/provider/acp/AntigravityAcpSupport.ts, repositories/anton-abyzov/specwithcode/apps/server/src/provider/acp/AntigravityAcpSupport.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/provider/acp/AntigravityProtocol.ts, repositories/anton-abyzov/specwithcode/apps/server/src/provider/model-manifest.json, repositories/anton-abyzov/specwithcode/packages/contracts/src/model.ts | Test: node node_modules/vite-plus/bin/vp test run apps/server/src/provider/acp/AntigravityAcpSupport.test.ts

### T-03 Tier on the provider card
- AC: AC-05 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/provider/Drivers/AntigravityDriver.ts, repositories/anton-abyzov/specwithcode/apps/server/src/provider/Drivers/AntigravityDriver.test.ts, repositories/anton-abyzov/specwithcode/packages/contracts/src/server.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/ | Test: node node_modules/vite-plus/bin/vp test run apps/server/src/provider/Drivers/AntigravityDriver.test.ts

### T-04 Sign-in guidance, terms notice and the background refusal
- AC: AC-06, AC-07 | Files: repositories/anton-abyzov/specwithcode/packages/contracts/src/settings.ts, repositories/anton-abyzov/specwithcode/apps/server/src/provider/antigravityAuthSupport.ts, repositories/anton-abyzov/specwithcode/apps/server/src/orchestration-v2/Adapters/AntigravityAdapterV2.ts, repositories/anton-abyzov/specwithcode/apps/server/src/orchestration-v2/Adapters/AntigravityAdapterV2.test.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/phrases/ | Test: node node_modules/vite-plus/bin/vp test run apps/server/src/orchestration-v2/Adapters/AntigravityAdapterV2.test.ts

### T-05 Enable and install a provider from the CLI
- AC: AC-08 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/cli/provider.ts, repositories/anton-abyzov/specwithcode/apps/server/src/cli/provider.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/cli.ts | Test: node node_modules/vite-plus/bin/vp test run apps/server/src/cli/provider.test.ts
