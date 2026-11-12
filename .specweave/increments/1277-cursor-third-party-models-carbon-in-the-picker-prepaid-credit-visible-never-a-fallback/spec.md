# Cursor third-party models: Carbon in the picker, prepaid credit visible, never a fallback

## Problem

Google released Gemini 4 Carbon on November 10, 2026, and Cursor offers it (50% off until November 30, then $4/M input and $20/M output). Anton expects it to work in SpecWithCode out of the box. Research thread "Gemini 4 Carbon via Cursor in SpecWithCode" found it mostly does, with three gaps:

- Cursor models come live from `@cursor/sdk` 1.0.35 (`Cursor.models.list`, `apps/server/src/provider/CursorSdkCatalog.ts:63-66`), mapped 1:1 into the picker with SDK parameters such as `effort` turned into options (`CursorProvider.ts:98-185`). Nobody has confirmed that the SDK lists Carbon and its effort values, or that an SDK run bills prepaid credit. Cursor hides many models by default.
- On Cursor's current plans (Plus, Premium, Super, Ultra, Teams), third-party models such as Carbon, Claude and GPT never draw from the weekly included pool. They bill prepaid credit at list price. `readCursorUsageLimits` (`cursorUsageLimits.ts:132-252`) reads only `GetCurrentPeriodUsage` and `GetPlanInfo` percentages; the comment at line 118 says third-party models bill prepaid credit, but no balance or spend is fetched, and the contract (`packages/contracts/src/providerUsageLimits.ts:20-132`) has no money field beyond Codex's unrendered `credits.balance` string. The chip shows a pool Carbon never touches.
- No Cursor model carries billing. The SDK model type has no billing flag, so every Cursor model reports undefined billing, and `isPaidModelOn` (`packages/shared/src/providerFallback.ts:202-207`) treats a signed-in Cursor with a usage read as free. Carbon could be picked by tier fallback, limit failback, task-aware routing or machine fallback and spend Anton's credit. The project rule is no paid Gemini fallback (memory `no-gemini-vertex-fallback-spend.md`), and `isGeminiSpendProvider` (`providerFallback.ts:170-175`) matches only the instance, so a Gemini model on a Cursor instance escapes it.

The Gemini CLI route can't reach Carbon yet: `UNLISTED_AGENT_MODELS` (`apps/server/src/provider/Drivers/AcpRegistryDriver.ts:126-130`) holds only `gemini-4-argon`, and Gemini CLI support is an open request (google-gemini/gemini-cli#30125).

## Scope

In:
- A live check, on Anton's signed-in Cursor account, that Carbon and its effort options reach the picker and a turn on it runs and bills prepaid credit.
- Per-model billing for Cursor: third-party models on a current plan report `api` billing.
- No automatic path (tier fallback, limit failback, same-model-elsewhere, task routing, machine fallback) ever picks a prepaid-credit Cursor model. A Gemini-family model billed per token is never automatic even when named in a fallback order.
- Gemini 4 Carbon in the Gemini CLI hidden-model list now (Vertex has it GA; the CLI's own catalog does not).
- Prepaid credit balance and this month's spend next to the weekly pool in the picker usage band, the host limits popover and the Usage limits page.

Out:
- Buying a Cursor plan or credit. Anton decides that.
- The mobile Usage limits page; it follows in a later change if wanted.
- Reconciling `taskRouting.billingOf`, which classifies any Cursor `api-key` sign-in as `api` (`packages/shared/src/taskRouting.ts:433-460`), with `providerFallback`, which doesn't. Per-model billing makes the Carbon case agree in both; the sign-in-level difference stays.
- A release, which goes through the release thread.

## Acceptance Criteria

- [ ] AC-01: Signed in to Cursor on a current plan, the Cursor provider's picker lists Gemini 4 Carbon with an effort option carrying the values the SDK reports (high, medium, low or as Cursor names them) and the SDK default selected; a short turn on Carbon at high effort completes, and Cursor's dashboard shows it charged to prepaid credit, not the included pool.
- [ ] AC-02: On a current (merged, non-enterprise) Cursor plan, every listed model that is not Cursor's own (Composer, `auto`/`default`) or Grok reports billing `api`; Cursor's own models and Grok report `subscription`. On a legacy plan (not merged), all models report `subscription`. When plan info is missing, third-party models report `api`.
- [ ] AC-03: `resolveProviderFallbackPass`, `resolveSameModelElsewhere`, `resolveCoordinatorTurnSelection`, the tier chain, `resolveTaskRouting` and `machineFallback` never pick a Cursor model billed `api`, with or without room in the weekly pool. A Gemini-family model (slug or display name matching `gemini`) billed `api` or `paid-router` stays `never-automatic` even when the person named it in the fallback order. Choosing Carbon by hand in the picker still works.
- [ ] AC-04: With a Cursor sign-in on a current plan, the picker usage band, the host limits popover and the Usage limits page show the prepaid credit balance and this month's spend in dollars next to the weekly pool, plus the monthly spend limit when one is set. When Cursor returns no credit data the row is hidden, never shown as $0.
- [ ] AC-05: The Gemini CLI picker offers Gemini 4 Carbon (`gemini-4-carbon`) after a catalog probe, next to Gemini 4 Argon, without duplicates when the CLI or `customModels` already lists it, and it stays `never-automatic` (Vertex per-token). Verified November 11, 2026: no Gemini CLI release up to 0.69.0-preview.0 lists Carbon (`VALID_GEMINI_MODELS` at v0.68.0 has no Gemini 4 model), while Vertex model garden reports `publishers/google/models/gemini-4-carbon` as GA, so it is reachable the same way as Argon.

## Approach

Billing (`CursorDriver.ts`, `CursorProvider.ts`): a new `cursorModelBilling(slug, planInfo)` in `apps/server/src/provider/cursorModelBilling.ts` classifies by the SDK id: Cursor's own models (`composer*`, `auto`, `default`, `cursor-*`) and `grok*` are pool models, everything else is third-party. The driver already reads `GetPlanInfo` with usage (`CursorDriver.ts:229-245`); it stamps `billing` on the snapshot's models after that read, so the catalog code stays untouched. Classifying by prefix is a guess at Cursor's rule; the live check confirms it and the SDK `description` text, unused today, is checked for a better signal.

Guard (`packages/shared/src/providerFallback.ts`, `modelBilling.ts`): `api` billing already makes `isPaidModelOn` true, which every automatic picker rejects, so AC-03 mostly falls out of AC-02. The new piece is `isGeminiSpendModel(model, provider)`: a Gemini-family model with paid billing is treated like a Gemini spend provider, so `describeFallbackOrder` (619-700) and `fallbackOptions.ts` (159-160, 225-226) keep it `never-automatic` even when named. Tests extend `providerFallbackPaidModel.test.ts` and `fallbackOptions.test.ts` with a Cursor instance listing Carbon, `composer-2` and `grok-5`.

Credit (contract, server, web): add `prepaidCredit?: { balanceUsd: number | null; spentThisMonthUsd: number | null; monthlyLimitUsd: number | null }` to `ServerProviderUsageLimits`, carried across sparse updates in `applyUsageLimitsUpdate` (`providerUsageLimits.ts:148-154`). `cursorUsageLimits.ts` reads it from Cursor's dashboard service next to `GetCurrentPeriodUsage` with the same 4 s optional timeout as `GetPlanInfo`. Which method returns the credit balance and on-demand spend is not in the repo; T-05 finds it from Cursor's web dashboard calls during the live check, and T-03 builds against a recorded response fixture. The web shows one line "Prepaid $X left · $Y this month" under the weekly pool in `ModelPickerUsageBand` (`ModelUsage.tsx:755`), `HostLimits.tsx`/`hostLimitsModel.ts` and `UsageLimitsPooled.tsx:521`.

Rejected: a hard-coded third-party model list (goes stale with every Cursor release); fetching per-model pricing from Cursor (no public API; billing class is enough for the guard); reusing `credits.balance` (a unitless Codex string with different meaning).

Risks: Cursor may bill SDK runs differently from the editor, and the credit endpoint is undocumented and may change. Both are checked live before merge.

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01: Third-party = anything not Cursor-own or Grok, by id prefix → simplest rule matching Cursor's plan page; revisit after the live check.
- D-02: Missing plan info → third-party models are `api` → fails safe: no automatic spend.
- D-03: Gemini-family paid models stay `never-automatic` even when named in the fallback order → the project's no-paid-Gemini-fallback rule wins over an explicit order; other paid models keep today's named-order behavior.
- D-04: Mobile Usage limits page is out → keeps the PR to web and server.
### Open
- Which Cursor dashboard method returns prepaid balance and monthly spend; answered in T-05.

## Tasks

### T-01 Per-model billing for Cursor models
- AC: AC-02 | Files: apps/server/src/provider/cursorModelBilling.ts, apps/server/src/provider/cursorModelBilling.test.ts, apps/server/src/provider/Drivers/CursorDriver.ts, apps/server/src/provider/Drivers/CursorDriver.test.ts, apps/server/src/provider/cursorUsageLimits.ts | Test: cd repositories/anton-abyzov/specwithcode-dev && pnpm vitest run apps/server/src/provider/cursorModelBilling.test.ts apps/server/src/provider/Drivers/CursorDriver.test.ts

### T-02 Never automatic: paid Cursor models and paid Gemini-family models
- AC: AC-03 | Files: packages/shared/src/providerFallback.ts, packages/shared/src/modelBilling.ts, packages/shared/src/fallbackOptions.ts, packages/shared/src/providerFallbackPaidModel.test.ts, packages/shared/src/fallbackOptions.test.ts, packages/shared/src/taskRouting.test.ts, packages/shared/src/machineFallback.test.ts | Test: cd repositories/anton-abyzov/specwithcode-dev && pnpm vitest run packages/shared/src/providerFallbackPaidModel.test.ts packages/shared/src/fallbackOptions.test.ts packages/shared/src/taskRouting.test.ts packages/shared/src/machineFallback.test.ts packages/shared/src/providerFallback.test.ts

### T-03 Prepaid credit and monthly spend in the usage chip
- AC: AC-04 | Files: packages/contracts/src/providerUsageLimits.ts, packages/contracts/src/providerUsageLimits.test.ts, apps/server/src/provider/cursorUsageLimits.ts, apps/server/src/provider/cursorUsageLimits.test.ts, apps/server/src/provider/providerUsageLimits.ts, apps/server/src/provider/providerUsageLimits.test.ts, packages/shared/src/usageLimits.ts, apps/web/src/components/chat/ModelUsage.tsx, apps/web/src/components/chat/ModelUsage.test.tsx, apps/web/src/components/studio/shell/HostLimits.tsx, apps/web/src/studio/hostLimitsModel.ts, apps/web/src/studio/hostLimitsModel.test.ts, apps/web/src/components/usage/UsageLimitsPooled.tsx, apps/web/src/components/usage/UsageLimitsPooled.identity.test.tsx | Test: cd repositories/anton-abyzov/specwithcode-dev && pnpm vitest run packages/contracts/src/providerUsageLimits.test.ts apps/server/src/provider/cursorUsageLimits.test.ts apps/server/src/provider/providerUsageLimits.test.ts apps/web/src/components/chat/ModelUsage.test.tsx apps/web/src/studio/hostLimitsModel.test.ts apps/web/src/components/usage/UsageLimitsPooled.identity.test.tsx, plus a headless screenshot of the picker band with a fixture snapshot

### T-04 Gemini 4 Carbon in the Gemini CLI hidden-model list
- AC: AC-05 | Files: apps/server/src/provider/Drivers/AcpRegistryDriver.ts, apps/server/src/provider/Drivers/AcpRegistryDriver.test.ts | Test: cd repositories/anton-abyzov/specwithcode-dev && pnpm vitest run apps/server/src/provider/Drivers/AcpRegistryDriver.test.ts. Change: add `{ id: "gemini-4-carbon", name: "Gemini 4 Carbon" }` to `UNLISTED_AGENT_MODELS.gemini` (`AcpRegistryDriver.ts:126-130`), extend the Argon test at `AcpRegistryDriver.test.ts:340-397`, and update the JSDoc (lines 119-125). No paid live turn without Anton's OK. Drop the entry once a Gemini CLI release lists Carbon (google-gemini/gemini-cli#30125).

### T-05 Live check on Anton's Cursor account (waiting on Anton)
- AC: AC-01 | Files: none | Test: on a dev server from the branch, with Anton signed in to Cursor on a current plan with prepaid credit: read the Cursor provider catalog headless and confirm Carbon and its effort values; run one short Carbon turn at high effort; confirm the charge on Cursor's usage page; record the dashboard method and response shape that return prepaid balance and monthly spend for T-03. Waits on Anton buying a plan and signing in; nothing is bought by an agent.
