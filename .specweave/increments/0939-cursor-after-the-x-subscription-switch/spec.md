# Cursor after the X Subscription switch

## Problem

SpaceX (which absorbed xAI) closed its purchase of Cursor on 14 August 2026. Since 12 October 2026 new Cursor accounts get The X Subscription: one weekly Grok/Composer pool shared with the Grok apps and X, Plus has Grok and Composer models only, and Claude, GPT and Gemini need Premium or higher and bill prepaid credit at API list price. OpenAI ends model access through Cursor on 12 November 2026 (proposed date).

SpecWithCode runs Cursor through `@cursor/sdk` (local runtime). A re-verified audit of specweave-studio origin/main found:

- A failed Cursor run shows "sent no details": `CursorAdapterV2` passes the SDK `RunError` to `makeProviderFailure`, which cannot read its message. Thrown SDK errors always become `transport_error`.
- Cursor failures never get class `usage_limit`, so the limit banner, usage-limit recovery and provider fallback never run when the weekly pool or credit runs out.
- A plan-gated or retired model fails at turn start as "could not start this turn. Retry", which retrying cannot fix.
- Cursor Limits never appear for an instance signed in inside SpecWithCode: `CursorDriver` hands the browser sign-in key to `readCursorUsageLimits` as `CURSOR_API_KEY`, which that reader treats as a different account.
- Every Cursor bar is labelled monthly with no window length; X Subscription accounts reset weekly (`DashboardService/GetPlanInfo` `includedUsagePeriod`), and merged accounts should show one included-pool bar, not the legacy Cursor Models / Other Models split whose text says GPT uses the plan pool.
- Text generation defaults to the retired `composer-2` and drops Cursor's error text.
- Docs say Cursor needs the CLI and `agent login`, imply cloud agents are coming, describe only the legacy monthly plan, and have no plans and billing section. The spec-weave.com architecture page says Cursor uses the machine's existing sign-ins.

## Scope

In: Cursor error text and classification, model-gating message, Cursor usage limits for signed-in instances, weekly/merged usage windows, text-generation default model, Cursor custom-model placeholder, key redaction, studio user docs and marketing footer, spec-weave.com copy. Out: `@cursor/sdk` upgrade to 1.0.38 (verified: no API, error, usage or grok_ key changes SpecWithCode needs, and it requires a reviewed lockfile audit change), prepaid credit balance display, Grok Bot (Sand) allowance, changing how `auto` maps to the SDK model id.

## Acceptance Criteria

- [ ] AC-01: When a Cursor run ends with an SDK error, the thread error shows Cursor's own (redacted) message instead of "sent no details"; thrown `CursorSdkError`s keep their message, code and retryable flag; bare `grok_`/`xai_`/`crsr_` keys are redacted.
- [ ] AC-02: Cursor usage-limit errors (`RateLimitError`, usage-limit run error codes, or usage/credit messages) produce failure class `usage_limit`, so recovery and provider fallback run.
- [ ] AC-03: A `ConfigurationError` at Cursor turn start (model not available on this account, retired model) shows a message that names the model and says to pick another model, not "Retry the turn".
- [ ] AC-04: A Cursor instance signed in inside SpecWithCode can show Limits from the machine's Cursor CLI login when `AuthService/GetEmail` confirms that login is the instance's account; a different or unknown account returns unsupported, and an explicit `CURSOR_API_KEY` still returns unsupported.
- [ ] AC-05: When `GetPlanInfo` reports a weekly included-usage period, Cursor windows are weekly with a 7-day duration and reset at `includedUsageResetsAt`; merged (X Subscription) accounts show one included-pool window from `totalPercentUsed`; legacy accounts keep the three monthly windows and gain a window duration from the billing cycle; any `GetPlanInfo` failure keeps legacy behaviour.
- [ ] AC-06: Cursor text generation defaults to `composer-2.5` and includes Cursor's redacted error text when the SDK request fails; the Cursor custom-model placeholder is a Cursor model.
- [ ] AC-07: Studio docs (cursor.md, install.md, usage.md, muse-code.md), in-app Cursor pool text and settings copy, the marketing footer and spec-weave.com (architecture page, comparison guide, subscription caveats, Cursor tutorial beat) describe the X Subscription, local-only runs and SpecWithCode's own Cursor sign-in correctly.

## Approach

Studio changes land in one PR on branch `fix/cursor-x-subscription` (worktree `~/.specwithcode/m4/scratch/cursor-x-subscription`). Site changes land in one specweave PR to develop.

- Failures: in `CursorAdapterV2.ts`, pass `RunResult.error.message` to `makeProviderFailure`; unwrap `CursorAgentSdkRunnerError.cause` and read `CursorSdkError` message/code/isRetryable; a `cursorFailureClass` helper maps `RateLimitError`, usage-limit codes and usage/credit message text to `usage_limit`. Export `RateLimitError` and `ConfigurationError` from `cursorSdk.ts`. Wrap a turn-start `ConfigurationError` in `ProviderSetupError` (operation `model`). Extend `redactProviderFailureText`.
- Usage: `CursorDriver` passes `CURSOR_API_KEY` to the reader only when the key is configured (`auth.usesApiKey`); for a browser sign-in it passes the stored email and the reader compares it with `AuthService/GetEmail` for the CLI login before reading usage. GetPlanInfo has its own 4 s timeout; a weekly period without a reset date is still weekly; merged enterprise plans keep the split view, as Cursor's client does. `readCursorUsageLimits` also calls `DashboardService/GetPlanInfo` with the same token; decode `isMerged` and `planInfo.includedUsagePeriod/includedUsageResetsAt` (enum name or number, int64 as string or number); failure means legacy. Add `billingCycleStart` for monthly duration. New `includedPool` entry first in `CURSOR_USAGE_WINDOWS`; legacy descriptions say they are for earlier plans.
- Text generation: `composer-2.5` default and alias in `packages/contracts/src/model.ts`; error detail in `CursorTextGeneration.ts`.
- Risk: no live X Subscription usage response was captured, and no Keychain probe is allowed, so the GetPlanInfo path is built from Cursor's own client schema and falls back to today's behaviour on any mismatch.

## Decisions

### Asked
- D-01 Rework everything the Cursor/X Subscription audit found → yes (user, "yes, complete and rework all what's needed", 2026-10-19)
- D-02 Verify and close the increment in the same thread → yes (user, 2026-10-19)
### Defaulted (change any before sw-do)
- D-03 Keep `@cursor/sdk` at 1.0.35 → the 1.0.38 diff has nothing SpecWithCode needs and its lockfile change needs a reviewed preservation-audit entry (reversible).
- D-04 Keep `auto` mapped to SDK id `default` → no recorded catalog shows `auto` listed; changing it blind could break every Auto run (reversible).
- D-05 Weekly windows only when GetPlanInfo says weekly → falls back to monthly on any error (reversible).
### Open
- none

## Tasks

### T-01 Cursor failure text, usage-limit class and model-gating message
- AC: AC-01, AC-02, AC-03 | Files: apps/server/src/orchestration-v2/Adapters/CursorAdapterV2.ts, apps/server/src/orchestration-v2/Adapters/CursorAdapterV2.test.ts, apps/server/src/orchestration-v2/Adapters/cursorFailure.ts, apps/server/src/orchestration-v2/Adapters/cursorFailure.test.ts, apps/server/src/provider/cursorSdk.ts, apps/server/src/orchestration-v2/ProviderFailure.ts, apps/server/src/orchestration-v2/ProviderFailure.test.ts | Test: cd ~/.specwithcode/m4/scratch/cursor-x-subscription/apps/server && pnpm exec vp test run src/orchestration-v2/Adapters/cursorFailure.test.ts src/orchestration-v2/Adapters/CursorAdapterV2.test.ts src/orchestration-v2/ProviderFailure.test.ts

### T-02 Cursor usage limits for signed-in instances, weekly and merged pools
- AC: AC-04, AC-05 | Files: apps/server/src/provider/Drivers/CursorDriver.ts, apps/server/src/provider/cursorUsageLimits.ts, apps/server/src/provider/cursorUsageLimits.test.ts, packages/shared/src/usageLimits.ts, apps/web/src/components/settings/UsageProviderSettings.tsx | Test: cd ~/.specwithcode/m4/scratch/cursor-x-subscription/apps/server && pnpm exec vp test run src/provider/cursorUsageLimits.test.ts src/provider/Drivers/CursorDriver.test.ts

### T-03 Cursor text-generation default and placeholder
- AC: AC-06 | Files: packages/contracts/src/model.ts, apps/server/src/textGeneration/CursorTextGeneration.ts, apps/server/src/textGeneration/CursorTextGeneration.test.ts, apps/web/src/components/settings/ProviderModelsSection.tsx | Test: cd ~/.specwithcode/m4/scratch/cursor-x-subscription/apps/server && pnpm exec vp test run src/textGeneration/CursorTextGeneration.test.ts

### T-04 Docs, in-app copy and site
- AC: AC-07 | Files: docs/user/cursor.md, docs/user/install.md, docs/user/usage.md, docs/studio/muse-code.md, apps/marketing/src/pages/index.astro, repositories/anton-abyzov/specweave/docs-site/docs/overview/studio-architecture.mdx, repositories/anton-abyzov/specweave/docs-site/docs/guides/specwithcode-vs-opencode-t3-code.md, repositories/anton-abyzov/specweave/docs-site/src/components/ecosystem/SubscriptionValue.tsx, repositories/anton-abyzov/specweave/docs-site/src/data/tutorials.json | Test: cd /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specweave/docs-site && npm run build

### T-05 Ship: studio PR, site PR, release, deploy
- AC: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06, AC-07 | Files: none | Test: cd ~/.specwithcode/m4/scratch/cursor-x-subscription && bash scripts/studio-verify/typecheck-gate.sh --jobs 1 --out /tmp/claude-501/tc-gate-0939
- Note: the plain `vp run typecheck` also fails on origin/main (51 Effect plugin diagnostics in untouched files); the repo's PR Gate (typecheck) uses this baseline gate, so it is the Test.
