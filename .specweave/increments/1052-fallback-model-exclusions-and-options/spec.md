# Fallback model exclusions and the continuation options view

## Problem

On October 20, 2026 the user asked for clear, stable model eligibility when a thread hits a usage limit:
- an ordered fallback list (shipped in 0955, PR #448);
- a way to exclude any model, for example Grok 4.7;
- a minimum per family (Claude Opus 5.5 or Fable 5.1; GPT-6.1 Sol and GPT-6 Astra; Gemini Argon 4; Grok 4.7 or later);
- a view of every handoff option, showing which access is verified and which is only potential or unknown.

As of 1.0.75 (origin/main f55a7507e3), the usage-limit planner (`packages/shared/src/providerFallback.ts`) reads none of these. `excludedSelections` covers only entries already tried for one stop. Task routing's `excludedProviders` and `minimumTier` and the 1003 lane floors (#622) apply only when new workers are routed. The banner lists only the fallback order's entries.

## Scope

In (anton-abyzov/specwithcode-dev):
- the settings contract (global and project);
- the shared planner;
- the Usage limits settings page;
- the limit banner's reasons.

Out:
- buying anything, enabling paid billing, or changing accounts;
- reading external balances such as GitHub Actions minutes, X Premium or startup credits, which SpecWithCode has no API for;
- a cross-family version order.

## Acceptance Criteria

- [ ] AC-01: Settings hold `providerLimitExcludedModels`, globally and per project. It is a list of at most 64 `{model, instanceId?}` entries, empty by default. A model is matched on its normalized slug (lowercase; `.`, `_` and spaces read as `-`), so `grok-4.7` and `grok-4-7` match, as do `claude-opus-5.5` and `claude-opus-5-5`. An entry without `instanceId` excludes the model on every provider; with one, only on that instance. Project overrides and the fleet continuity key list cover the key; a machine handoff carries the exclusions over, because clearing them would loosen a restriction.
- [ ] AC-02: No automatic limit continuation picks an excluded model. This holds for the named order, same model elsewhere, the legacy single model, the project default, the coordinator's model, any ready provider and another machine's target (global entries only), both at a stop and on an early move. An entry that cannot run here keeps its own reason (missing, not set up, at its limit, billed per token) rather than `excluded`. `describeFallbackOrder` reports an excluded entry as `excluded`. When everything left is excluded, the planner returns null, the same as when nothing is available, so the existing wait, auto-resume and manual choices apply. A manual pick from the banner is still the user's choice: an excluded model shows "excluded from automatic fallback" and stays choosable.
- [ ] AC-03: `describeFallbackOptions` lists every provider instance on this machine and each of its listed models, grouped by family (Claude, OpenAI, Google, xAI, other). Each row shows:
  - status: ready, current, limited, full until a time, signed out, not ready, excluded, per-token (needs the API-credit opt-in), Gemini/Vertex spend (never automatic), or unknown billing (only when named);
  - access: a verified usage reading, no usage reported, billed per token, or unknown;
  - its place in the fallback order, if it has one.
- [ ] AC-04: The Usage limits page shows "Where a limited thread can continue" from AC-03, with an Exclude/Include toggle per model that saves AC-01. A note says that access outside SpecWithCode (GitHub Actions minutes, an X subscription, startup credits) is not model access here unless one of the providers listed is signed in with it.
- [ ] AC-05: The per-family minimum is expressed by excluding the models below it in that family. The panel shows each family's live models together, so the user sets the floor explicitly. There is no inferred version order: Sol, Astra and Grok have no comparable tier (`modelTier` returns null).

## Decisions

### Defaulted
- D-01: Exclusions are the only stored eligibility rule. Floors are not stored as rules. A new model is eligible until the user excludes it, which matches "generally available new models should be considered stable". Opt-outs, the paid-API rules and permissions still apply to it.
- D-02: Exclusions apply to automatic continuation only. A manual pick and the user's explicit composer selection are not blocked.

## Tasks

### T-01 Contract and planner exclusions
- AC: AC-01, AC-02 | Files: packages/contracts/src/settings.ts, packages/shared/src/providerFallback.ts, apps/server/src/fleet/MachineHandoff.ts, scripts/studio-fleet/settings_continuity.py | Test: vp test run packages/shared/src/providerFallback.test.ts

### T-02 Options model
- AC: AC-03, AC-05 | Files: packages/shared/src/fallbackOptions.ts | Test: vp test run packages/shared/src/fallbackOptions.test.ts

### T-03 Settings panel and banner reason
- AC: AC-02, AC-04 | Files: apps/web/src/components/settings/FallbackOptionsPanel.tsx, apps/web/src/components/settings/ProviderLimitSettings.tsx, apps/web/src/components/settings/projectOverrideRows.ts, apps/web/src/components/chat/UsageLimitRecoveryBanner.tsx | Test: vp test run apps/web/src/components/settings/FallbackOptionsPanel.test.tsx

### T-04 Headless evidence and PR (no merge during the freeze)
- AC: AC-04 | Test: headless screenshots under ~/.specwithcode/m4/evidence/fallback-eligibility-1052/

### T-05 Verify and close 1052
