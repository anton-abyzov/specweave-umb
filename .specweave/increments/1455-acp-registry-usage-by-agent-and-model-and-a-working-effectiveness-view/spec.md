# ACP Registry usage by agent and model, and a working Effectiveness view

## Problem

Two faults in Models > Limits by account (owner report, November 23, 2026, with a screenshot):

1. **Effectiveness crashes the app.** Clicking Effectiveness (and All accounts) replaces the whole window with "Something went wrong. useSidebar must be used within a SidebarProvider." Reproduced headless on M5 against the running 1.0.409 server: coordinator model picker > Limits by account > Effectiveness. Cause: the Usage sheet's section list uses `SidebarMenuButton`, which calls `useSidebar()` and throws without a `SidebarProvider`; `UsageSheetHost` is mounted in `routes/__root.tsx`, outside `AppSidebarLayout`'s provider. The `/usage` page works because it renders inside the layout. `UsageSheet.test.tsx` mocks `UsagePage`, so no test rendered the real sheet. The release history is squashed, but the sheet's section list (with `SidebarMenuButton`) arrived in 1.0.116 while the root mount dates from 1.0.77, so every open of the sheet has crashed since 1.0.116; All accounts fails the same way.
2. **"ACP Registry" is one row with no logo and a claim it cannot back.** The "Used before reset" summary groups by driver, so every registry agent (GitHub Copilot, Copilot Enterprise, Gemini CLI and others) collapses into one "ACP Registry" row drawn as the letters "AR", with empty bars, "new", and "Nov 30 · on pace to use it all". Both Copilot accounts read 0% left, so the account had in fact used it all; the line called a spent limit a pace, and the same pace line appears for any provider with no recorded reset. The Subscriptions dashboard's "By provider" grouping has the same driver-level label. Nothing shows which agents and models actually ran through the registry.

Evidence from M5's own records (`specwithcode db query`, read-only, November 23): 154 recorded turns, every one with token usage, and 154 run attempts on two Copilot instances (`acpRegistry_github_copilot` 98, `acpRegistry_github_copilot_2` 56), by model `claude-opus-5.5` 120, `gemini-4-neon` 26, `gpt-6.2-sol` 5, `gpt-6-astra` 3. The server already reports these turns per account and model in `usage.machineReport` (1357), unused by the Limits views.

## Scope

In: the crash fix for every Usage sheet entry point; registry agents shown per agent with their own logo and name in the summary and the dashboard's provider grouping; an honest line for a provider with no recorded reset; an "Agents and models" section on Usage > Limits > Subscriptions built from each machine's `usage.machineReport` (turns, tokens where the agent reports them, per agent and per model, by day), covering registry agents and Antigravity. Out: new server data or RPCs, changes to how accounts are attributed (1357 rules stand), Copilot's quota reader, per-model limits (Copilot reports one premium-request pool per account).

## Acceptance Criteria

- [x] AC-01: Effectiveness and All accounts in Limits by account open the Usage sheet over the current page without an error; the sheet's section list renders and switches sections when no `SidebarProvider` is above it. A test renders the real sheet navigation outside a provider.
- [x] AC-02: In "Used before reset", each registry agent is its own row named and drawn as the agent (GitHub Copilot with the Copilot mark), never "ACP Registry" or "AR"; two accounts of one agent share its row. The Subscriptions dashboard's "Provider" grouping uses the same names.
- [x] AC-03: A provider whose account-wide window is spent on every live account says "at its limit until <reset>", whatever its history. A provider with no recorded reset shows its reading ("40% used · resets Nov 30") and no projected bar. Providers with recorded resets keep the projection.
- [x] AC-04: Usage > Limits > Subscriptions has an "Agents and models" section: for the last 30 days, per registry agent (and Antigravity) its turns, tokens when reported, and share by model, plus a by-day chart of turns stacked by model, merged across every machine that answers `usage.machineReport`. With no registry turns it says so in one line; a machine that cannot answer is named, not counted as zero.
- [x] AC-05: A headless screenshot shows the summary and the new section with the correct logos, and a headless run of the built app opens Effectiveness without the error.

## Approach

1. `apps/web/src/components/ui/sidebar.tsx`: `SidebarMenuButton` reads the context without throwing (no provider means an expanded, desktop sidebar: tooltip hidden). Fixes the Usage sheet and any other sheet that reuses the menu rows. Rejected: moving `UsageSheetHost` into `AppSidebarLayout`, which would close the sheet on pages without that layout and leave the trap for the next sheet.
2. `packages/shared/src/usageLimits.ts` and `subscriptionRows.ts` carry the instance's registry `iconUrl` (from `ServerProvider.iconUrl`). `apps/web/src/components/usage/subscriptions/providerGroups.ts` (new, pure): the group a subscription belongs to: its driver, or for `acpRegistry` the agent brand from the registry icon URL (registry-assigned), else from the instance name (`providerBrandForName`), with the agent's name. Two accounts of one agent share the group; account labels keep the instance's own name. `effectivenessIndex.ts` groups by it; `EffectivenessSummary.tsx` draws `ProviderInstanceIcon` with the agent name; `SubscriptionsView.tsx`/`SubscriptionsDashboard.tsx` provider grouping uses it.
3. `EffectivenessSummary.tsx` subline: projection only with at least one recorded reset; otherwise the reading.
4. `apps/web/src/components/usage/subscriptions/registryAgents.ts` (new, pure): folds `UsageMachineReport[]` into per-agent, per-model totals and a daily series (`acpRegistry` and `antigravity` accounts, by `usageAccountKeyDriver`; a shared transcript source counted once). An account resolves to its agent through the limit account (email keys) or the instance (`:instance:` keys), registry icon first. `RegistryAgentsView.tsx` (new) draws the per-agent model share and the by-day stacked bars with the validated dataviz palette, legend and a screen-reader table; `RegistryAgentsSection.tsx` (new) reads the reports (same RPC, capability and scope checks as Usage > Machines). Mounted in `SubscriptionsView.tsx`. No server change: the report already carries ACP turns per account and model.
5. The existing headless fixture `apps/web/tests/effectiveness-index/` gains registry agents and the section; an isolated server built from this branch proves the crash fix.

Risks: an agent's instance name not naming a brand falls back to the instance name with the generic mark (never "AR" on a known agent). Agents that report no tokens show turns only, labelled.

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01 Statistics count turns (and tokens where reported) from `usage.machineReport`, not provider-side billing: Copilot's ACP adapter reports no per-model premium-request split, so turns are the only per-model measure the app has. Labelled as SpecWithCode turns.
- D-02 Two accounts of one agent (Copilot and Copilot Enterprise) share one row in the summary, as Claude's accounts do; the Subscriptions "Account" grouping and the account list keep them apart.
- D-03 The section covers registry agents and Antigravity (the owner named it; it is its own driver, read from transcripts). Claude Code, Codex and Grok models already appear in Usage > Tokens and Machines; Muse is left out.
- D-04 A provider with no recorded reset shows its reading, not a projection: with no history there is nothing to say the pace holds. Reversible in `effectivenessIndex.ts` (`projects`).
### Open
- none

## Tasks

### T-01 Usage sheet opens without a sidebar provider
- AC: AC-01 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/ui/sidebar.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/ui/sidebarMenuButton.test.tsx | Test: cd repositories/anton-abyzov/specwithcode/apps/web && node ../../node_modules/vite-plus/bin/vp test run src/components/ui/sidebarMenuButton.test.tsx src/components/usage/UsageSheet.test.tsx

### T-02 Registry agents grouped and named per agent
- AC: AC-02, AC-03 | Files: repositories/anton-abyzov/specwithcode/packages/shared/src/usageLimits.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/usage/subscriptions/subscriptionRows.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/copilotIcon.test.tsx, repositories/anton-abyzov/specwithcode/apps/web/tests/subscription-resets/main.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/usage/subscriptions/SubscriptionsView.test.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/usage/subscriptions/providerGroups.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/usage/subscriptions/providerGroups.test.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/usage/subscriptions/effectivenessIndex.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/usage/subscriptions/effectivenessIndex.test.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/usage/subscriptions/EffectivenessSummary.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/usage/subscriptions/SubscriptionsView.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/usage/subscriptions/SubscriptionsDashboard.tsx | Test: cd repositories/anton-abyzov/specwithcode/apps/web && node ../../node_modules/vite-plus/bin/vp test run src/components/usage/subscriptions

### T-03 Agents and models section
- AC: AC-04 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/usage/subscriptions/registryAgents.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/usage/subscriptions/registryAgents.test.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/usage/subscriptions/RegistryAgentsSection.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/usage/subscriptions/RegistryAgentsView.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/usage/subscriptions/SubscriptionsView.tsx | Test: cd repositories/anton-abyzov/specwithcode/apps/web && node ../../node_modules/vite-plus/bin/vp test run src/components/usage/subscriptions/registryAgents.test.ts

### T-04 Headless evidence
- AC: AC-05 | Files: repositories/anton-abyzov/specwithcode/apps/web/tests/effectiveness-index/main.tsx, repositories/anton-abyzov/specwithcode/apps/web/tests/effectiveness-index/verify.mjs, repositories/anton-abyzov/specwithcode/docs/operations/checks.md | Test: cd repositories/anton-abyzov/specwithcode && node node_modules/vite-plus/bin/vp build --config apps/web/tests/effectiveness-index/vite.config.ts && node apps/web/tests/effectiveness-index/verify.mjs "$PWD/../../../.specweave/increments/1455-acp-registry-usage-by-agent-and-model-and-a-working-effectiveness-view/reports"
