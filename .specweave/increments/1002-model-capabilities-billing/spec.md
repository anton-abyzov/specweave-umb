# Model capabilities and paid-router safety

## Problem
Pi and OpenCode instances can reach OpenRouter and other keyed cloud providers, but SpecWithCode has no idea those models cost money. Pi reports no usage at all, so `usable()` in `packages/shared/src/providerFallback.ts` accepts it and the any-ready step can move a usage-limited thread onto a paid OpenRouter model without asking. Separately, `ServerProviderModel` carries no capability data: OpenCode throws away models.dev's tool-call, reasoning, image and context data, Pi throws away context and input types, OpenCode invents a Low to Extra High effort ladder for models with no reasoning, every model gets the full studio-code MCP even when it can't call tools, and an image can be sent to a text-only model. This is Phase 1 of `/Users/antonabyzov/.specwithcode/m4/scratch/local-models-20261022/local-models-plan.md`.

## Scope
In: per-model `billing` class and capability fields on `ServerProviderModel`; filling them for OpenCode (v1 and v2) and Pi from data they already return; a per-model paid check in fallback so paid-router and API-billed models are never picked automatically and show a paid label on the limit card; `local` and `paid-router` in Auto routing billing; removing the fake effort ladder; model-aware MCP attachment (none for models that can't call tools); blocking image sends to text-only models; tests.
Out: OpenRouter settings, balance, paid-continuation choice or automatic paid step (Phase 2, not now); local runtime probe and presets (Phase 3); handoff target-choice (Phase 4); any change to Claude or Codex model catalogs beyond leaving the new fields unset.

## Acceptance Criteria
- [x] AC-01: `ServerProviderModel` has optional `billing` (`subscription | local | paid-router | api | unknown`), `toolCalls`, `reasoning` (`none | optional | mandatory`), `imageInput`, `contextWindow` and `maxOutput`; old snapshots without them still decode.
- [x] AC-02: OpenCode (v1 and v2) and Pi fill those fields from the model data they already receive: OpenRouter models are `paid-router`; models served from a loopback base URL are `local`; keyed cloud API providers are `api`; anything not provable stays `unknown` or unset.
- [x] AC-03: A model whose billing is `paid-router` or `api` is never chosen automatically by usage-limit fallback (`usable()`, the any-ready step, the coordinator and worker-launch steps), and the limit card renders it as paid ("billed per token") instead of choosable. A Pi instance with an OpenRouter model is the regression test.
- [x] AC-04: Auto routing (`billingOf` in `packages/shared/src/taskRouting.ts`) reports `local` and `paid-router`; `paid-router` follows the paid-API rule, never picked when paid API is off.
- [x] AC-05: OpenCode no longer adds the Low to Extra High effort ladder to a model whose data says it has no reasoning.
- [x] AC-06: `prepareMcpSession` gets the selected model; a model with `toolCalls === false` gets no studio-code MCP, and everything else behaves as today.
- [x] AC-07: The composer blocks sending an image to a model with `imageInput === false` and says why; unset means allowed.
- [x] AC-08: Focused unit tests cover every AC above; server and web typecheck and the focused suites pass; a PR is open with CI green.

## Approach
Contracts first (`packages/contracts/src/server.ts`), all fields optional so nothing else changes. A small shared helper `packages/shared/src/modelBilling.ts` exports `modelBilling(provider, model)` and `isPaidModel(provider, model)` (per-token instance or paid model). `providerFallback.ts` gets the minimum edit: the places that call `isPerTokenProvider(provider)` with a model in hand call `isPaidModel(provider, model)` instead, so open PRs #593, #599, #605 and #612 that touch this file conflict as little as possible. Providers map their native data: OpenCode models.dev fields (`tool_call`, `reasoning`, `attachment`/modalities, `limit.context`, `limit.output`, provider id and base URL) and Pi `get_available_models` fields (provider, `reasoning`, `input`, `contextWindow`, `maxTokens`, cost, base URL). MCP gating lives in `ProviderSessionManager.prepareMcpSession`. The image guard reads the selected model's `imageInput` in the composer send path.

## Decisions
### Defaulted
- Unknown billing keeps today's behaviour; only provable paid models change. Rationale: no regressions for Pi/OpenCode subscription logins.
- Phase 2 (OpenRouter paid choice) is out by user decision, October 22, 2026.
- Lean MCP profile for small-context models is deferred; only "no tools, no MCP" ships now.
### Open
- none

## Tasks
### T-01 Contracts and shared billing helper
- AC: AC-01, AC-03 | Files: /Users/antonabyzov/.specwithcode/m4/worktrees/model-capabilities/packages/contracts/src/server.ts, /Users/antonabyzov/.specwithcode/m4/worktrees/model-capabilities/packages/shared/src/modelBilling.ts, /Users/antonabyzov/.specwithcode/m4/worktrees/model-capabilities/packages/shared/src/modelBilling.test.ts, /Users/antonabyzov/.specwithcode/m4/worktrees/model-capabilities/packages/shared/package.json | Test: vitest modelBilling.test.ts and contracts decode test

### T-02 Fallback and Auto routing use per-model paid checks
- AC: AC-03, AC-04 | Files: /Users/antonabyzov/.specwithcode/m4/worktrees/model-capabilities/packages/shared/src/providerFallback.ts, /Users/antonabyzov/.specwithcode/m4/worktrees/model-capabilities/packages/shared/src/providerFallback.test.ts, /Users/antonabyzov/.specwithcode/m4/worktrees/model-capabilities/packages/shared/src/taskRouting.ts, /Users/antonabyzov/.specwithcode/m4/worktrees/model-capabilities/packages/contracts/src/taskRouting.ts, /Users/antonabyzov/.specwithcode/m4/worktrees/model-capabilities/apps/server/src/orchestration-v2/ProviderFallbackWorker.ts | Test: vitest providerFallback.test.ts taskRouting.test.ts

### T-03 OpenCode and Pi fill capabilities and billing; no fake effort ladder
- AC: AC-02, AC-05 | Files: /Users/antonabyzov/.specwithcode/m4/worktrees/model-capabilities/apps/server/src/provider/OpenCodeProvider.ts, /Users/antonabyzov/.specwithcode/m4/worktrees/model-capabilities/apps/server/src/provider/opencodeRuntime.ts, /Users/antonabyzov/.specwithcode/m4/worktrees/model-capabilities/apps/server/src/provider/PiProvider.ts | Test: vitest OpenCodeProvider.test.ts PiProvider.test.ts

### T-04 Model-aware MCP attachment and image send guard
- AC: AC-06, AC-07 | Files: /Users/antonabyzov/.specwithcode/m4/worktrees/model-capabilities/apps/server/src/orchestration-v2/ProviderSessionManager.ts, /Users/antonabyzov/.specwithcode/m4/worktrees/model-capabilities/apps/web/src/components/ChatView.tsx | Test: focused server and web tests

### T-05 Typecheck, focused suites, review, PR with CI green
- AC: AC-08 | Files: PR on anton-abyzov/specwithcode-dev | Test: server and web tsc, focused vitest, CI

### T-06 Verify and close 1002
- AC: AC-08 | Files: verification evidence | Test: specweave verify, fresh-context review, specweave complete
