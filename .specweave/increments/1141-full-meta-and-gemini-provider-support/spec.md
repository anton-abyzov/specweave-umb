# 1141 Full Meta and Gemini provider support

## Problem

1. A project coordinator running on Gemini (ACP Registry -> Gemini CLI, model `gemini-4-argon`/"Auto", per-token key) dies permanently after its native session is reopened: Gemini CLI rebuilds history from its chat recording without `thoughtSignature` on past `functionCall` parts, Gemini 3+ validation rejects the request ("Function call is missing a thought_signature ... `mcp_studio-code_orchestrator_capabilities`, position 2"), and SpecWithCode shows "The coordinator did not answer." Retry reopens the same poisoned session. Evidence: user screenshots 2026-10-29; diagnosis in this increment's reports.
2. Meta support is Preview-grade: Muse driver works for agentic turns, but text generation is an always-failing stub that is still selectable, discovered models carry no billing/toolCalls/context metadata, usage freshness has no on-demand read, the Studio MCP toolkit is not forwarded to Muse sessions, there is no default instance/discovery, and no direct Meta Model API route (per-token Muse Wonder `muse-wonder-1.0` / Spark at `https://api.meta.ai/v1`).
3. Gemini-spend providers are hard-blocked as automatic fallbacks even when the user explicitly names them in the fallback order, so Meta <-> Gemini fallback pairs cannot be configured.

## Scope

In: Gemini poisoned-session recovery in the ACP adapter; Muse completeness (model metadata, usage freshness, usage_limit classification, MCP pass-through, real text generation, default model entries); Meta Model API per-token route for text generation; explicitly-named Gemini fallback entries honored; fallback family classification for Meta. Owned checkout: `/Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/meta-gemini-providers`, branch `muse/meta-gemini-providers` from origin/main `2ff660b088`.

Out: fixing Gemini CLI itself (upstream); a new raw-API agentic harness for Meta (agentic turns stay on Muse Code CLI/MSP; Wonder Full remains subscription-only through it); Antigravity quota reader (no upstream quota source identified); release publication without the release gates and Anton's acceptance of new UI/auth.

## Acceptance Criteria

- [ ] AC-01: A Gemini ACP turn that fails with a missing-thought-signature error recovers once on a fresh native session (with context handoff) instead of failing the coordinator turn; a second identical failure still fails cleanly with actionable text.
- [ ] AC-02: Muse models publish billing (subscription vs api), toolCalls and context window; fallback/coordinator pickers classify `muse-*` as Meta; Muse has default model entries.
- [ ] AC-03: Muse fallback eligibility is reliable: on-demand usage read exists and a native allowance timestamp is recorded, so a healthy subscription instance is not dropped by the 5-minute staleness edge.
- [ ] AC-04: Muse text generation works (titles/commit text) via an ephemeral session, or Muse is not selectable for text generation until it does.
- [ ] AC-05: The Studio MCP toolkit reaches Muse sessions, so a Muse coordinator can launch/manage workers like other coordinators (verified by fixture/unit evidence, not just types).
- [ ] AC-06: Meta Model API models (Wonder, Spark) are usable per-token for text generation with a Meta API key; Wonder Full is never implied by an API key.
- [ ] AC-07: A user-named Gemini-spend entry in the fallback order is honored as an explicit fallback (never auto-picked unnamed); Muse <-> Gemini pairs work as main/fallback in both directions per the shared resolver tests.
- [ ] AC-08: Focused tests and production server/web builds pass; no other owner's checkout or in-flight fallback work is overwritten.

## Approach

Order: T-01 Gemini recovery (smallest, unblocks the dead coordinator), T-02 Muse metadata/defaults/family, T-03 Muse usage freshness + usage_limit classification, T-04 Muse MCP pass-through, T-05 Muse text generation, T-06 Meta Model API text generation, T-07 named Gemini fallback consent.

Key evidence (origin/main 2ff660b088): prompt failure path `apps/server/src/orchestration-v2/Adapters/AcpAdapterV2.ts:7553`, fresh-session load fallback `:6631`; Muse stub `apps/server/src/provider/Drivers/MuseDriver.ts:216`; discovery `apps/server/src/provider/muse/MuseDiscovery.ts:13`; MCP drop `MuseDriver.ts:56`, `MuseRuntime.ts:108`; Gemini spend block `packages/shared/src/providerFallback.ts:159`; family typo `packages/shared/src/fallbackOptions.ts:61` (`wander`).

All browser automation headless:true, PWDEBUG=0, PLAYWRIGHT_HTML_OPEN=never. Node 22.20 + isolated pnpm 11.10 per repo AGENTS.md. Focused tests only.

## Decisions

### Asked
- D-01 "add full support of meta models like wonder or wonder full in specwithcode ... we could put Meta and Gemini models also as a fallback or as a main model" (Anton, 2026-10-29) -> full parity scope above.
### Defaulted (change any before sw-do)
- D-02 Direct Meta Model API = text-generation route only; agentic main/coordinator stays on the Muse Code driver (reversible; a raw-API agent harness is a separate increment).
- D-03 Gemini-spend fallback honored only when explicitly named in the user's fallback order (reversible; unnamed auto-pick stays blocked).
- D-04 Muse stays opt-in (no auto-created default instance) in this increment; manual instance add remains, defaults only fill model picks once an instance exists (reversible).
### Open
- Release: needs the release train + Anton's acceptance of new provider UI/auth before a desktop version ships.

## Tasks

### T-01 Gemini poisoned-session recovery
- AC: AC-01 | Files: apps/server/src/orchestration-v2/Adapters/AcpAdapterV2.ts, apps/server/src/orchestration-v2/Adapters/AcpRegistryAdapterV2.ts, apps/server/src/orchestration-v2/Adapters/AcpAdapterV2.test.ts, apps/server/scripts/acp-mock-agent.ts | Test: cd /Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/meta-gemini-providers && node node_modules/vite-plus/bin/vp test run apps/server/src/orchestration-v2/Adapters/AcpAdapterV2.test.ts apps/server/src/orchestration-v2/Adapters/AcpRegistryAdapterV2.test.ts
### T-02 Muse model metadata, defaults, Meta family
- AC: AC-02 | Files: apps/server/src/provider/muse/MuseDiscovery.ts, apps/server/src/provider/muse/MuseDiscovery.test.ts, packages/contracts/src/model.ts, packages/shared/src/fallbackOptions.ts, packages/shared/src/fallbackOptions.test.ts, apps/server/src/provider/model-manifest.json | Test: cd /Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/meta-gemini-providers && node node_modules/vite-plus/bin/vp test run apps/server/src/provider/muse/MuseDiscovery.test.ts packages/shared/src/fallbackOptions.test.ts packages/shared/src/providerFallback.test.ts
### T-03 Muse usage freshness and limit classification
- AC: AC-03 | Files: apps/server/src/provider/Drivers/MuseDriver.ts, apps/server/src/provider/muse/MuseRuntime.ts, apps/server/src/provider/muse/MuseDiscovery.ts | Test: cd /Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/meta-gemini-providers && node node_modules/vite-plus/bin/vp test run apps/server/src/provider/muse/
### T-04 Muse MCP pass-through
- AC: AC-05 | Files: apps/server/src/provider/Drivers/MuseDriver.ts, apps/server/src/provider/muse/MuseRuntime.ts, apps/server/src/provider/muse/MuseRuntime.test.ts | Test: cd /Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/meta-gemini-providers && node node_modules/vite-plus/bin/vp test run apps/server/src/provider/muse/MuseRuntime.test.ts
### T-05 Muse text generation
- AC: AC-04 | Files: apps/server/src/textGeneration/MuseTextGeneration.ts, apps/server/src/textGeneration/MuseTextGeneration.test.ts, apps/server/src/provider/Drivers/MuseDriver.ts, apps/server/src/serverSettings.ts | Test: cd /Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/meta-gemini-providers && node node_modules/vite-plus/bin/vp test run apps/server/src/textGeneration/MuseTextGeneration.test.ts apps/server/src/textGeneration/TextGeneration.test.ts
### T-06 Meta Model API text generation
- AC: AC-06 | Files: apps/server/src/textGeneration/MetaTextGeneration.ts, apps/server/src/textGeneration/MetaTextGeneration.test.ts, apps/server/src/provider/Drivers/MuseDriver.ts | Test: cd /Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/meta-gemini-providers && node node_modules/vite-plus/bin/vp test run apps/server/src/textGeneration/MetaTextGeneration.test.ts
### T-07 Named Gemini fallback consent
- AC: AC-07 | Files: packages/shared/src/providerFallback.ts, packages/shared/src/providerFallback.test.ts, packages/shared/src/fallbackOptions.ts | Test: cd /Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/meta-gemini-providers && node node_modules/vite-plus/bin/vp test run packages/shared/src/providerFallback.test.ts packages/shared/src/coordinatorDefault.test.ts

## Receipts

- 2026-10-29 diagnosis (parallel read-only audits at origin/main 2ff660b088): Gemini root cause is inside Gemini CLI session reload (signatures dropped when rebuilding history); Studio-side recovery is fresh-session retry. Muse gaps and fallback map recorded from the same audits; key file:line evidence in Approach.
