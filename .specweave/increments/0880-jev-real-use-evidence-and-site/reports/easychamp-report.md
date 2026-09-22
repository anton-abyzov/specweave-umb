# EasyChamp Jev evidence — 2026-09-22

## Decision

Useful narrow capability: route an unmatched, unfiltered collection-read request directly to existing authenticated handlers. **Do not enable globally yet.** The measured dataset recovered only 5 of 41 provider calls. No measured production productivity or conversion lift exists.

## What shipped

- Optional `JEV_READ_ROUTING_MODE=off|shadow|enabled`, default off. Strict .95 threshold for both answer confidence and winning probability.
- Regex remains first. Only previously unmatched requests reach Jev. Existing deterministic write guard, JWT transport, API authorization, and approval flow remain unchanged.
- Exactly three direct-read choices: leagues, competitions, teams. Everything scoped, filtered, contextual, mutating, mixed, or uncertain returns to the existing agent.
- One provider request, 1.5-second total deadline, no retries. Invalid schemas/choices/probabilities, rate limits, missing key and transport failures fall back.
- Only eligible message text is sent to OpenRouter. No JWT, history or entity/API data. Secret-like messages are skipped; this screening is heuristic, not a PII guarantee. Global opt-in requires a privacy/traffic decision.

## Reproducible evaluation

`easychamp-evaluation.json` records every case. Original 26-case corpus plus 36 new held-out cases fixed before this run; all authored synthetic inputs. Uses actual Python `detect_intent`, not the previous JavaScript port. Labels represent the narrower direct-read catalog; original broad intent labels are retained separately. No accuracy claim across incompatible labels.

| Measure | Result |
|---|---:|
| Total cases | 62 |
| Actual provider calls | 41 |
| Correct additional direct routes | 5 |
| Wrong Jev direct routes in this sample | 0 |
| Held-out route decisions correct | 24/36 baseline → 29/36 hybrid |
| All route decisions correct | 45/62 baseline → 50/62 hybrid |
| Existing regex wrong direct routes | 3 |
| Provider p50 / p95 | 288.6 / 437.3 ms |
| Local Python baseline p50 | 0.0704 ms |
| API-reported cost, this replay | $0.000862344 |
| Failed provider calls / missing cost | 0 / 0 |

### Overhead and break-even

All 41 Jev calls together took **12.883 seconds**; only 5 removed a generative route. Other 36 calls added delay before the original path. Ignoring API/render differences, those five avoided generative routes must each save **2.577 seconds on average** just to offset aggregate Jev latency on this corpus. That is arithmetic on measured classifier durations, not a demonstrated full-corpus speedup. Do not advertise overall time savings. Regex remains materially faster and free of provider charges.

## Actual agent demonstration

`easychamp-agent-comparison.json` runs the real `MCPServerInstance.process_message`, real registered tools, actual Gemini 2.5 Flash API, and real Jev API. EasyChamp API responses are local fixtures. No production data, auth token, MongoDB or writes. Five successful reads were selected from the replay, so this is a demonstration rather than an independent test.

Four of five reruns routed directly. Their individual times were 276–400 ms, versus 1.2–3.3 seconds for the existing Gemini path. More materially, the current generic agent lacks a collection-list tool: it asks for a league name/ID or says it cannot list. Jev reaches existing read handlers and returns the supplied fixture data. Example:

> Input: Could I see the leagues available to me?
>
> Existing agent (1,988 ms): “I'm sorry, I can't retrieve a list of all available leagues. I can only provide information for a specific league if you give me its name or ID.”
>
> Jev route (307 ms): “I found 1 league(s): Demo Community League.”

Gemini took two provider requests / 13,297 input tokens / 49 output tokens for this example. Jev cost $0.000021042, with zero Gemini calls. Gemini bill cost was unavailable, so no billed-dollar saving is claimed. API fixtures have negligible latency; actual customer end-to-end latency is unmeasured. All initialization occurred before timing, no retries, one sequential pair per case.

One Russian case moved from .95 confidence to .94 and fell back on repeat. The feature correctly abstained, but this is direct evidence that threshold-bound outcomes vary. Spanish direct replies currently use existing English templates; multilingual response quality is unfinished.

## Problems found

1. Existing regex misroutes negation (“don't show me my teams, show me the fixtures instead”) and multi-step requests (“List leagues and tell me which has the most teams”). Jev only sees unmatched input, so cannot repair these.
2. `list my competitions` reaches the existing general `/aioptimize/champs` listing without an explicit ownership filter. New Jev criteria conservatively reject ownership-specific competitions/teams. Endpoint authorization remains authoritative; this is a semantic scope issue, not proven cross-user data exposure.
3. Existing full agent lacks generic collection-list tools; adding deterministic tool coverage may yield broader gains than another classifier. Not measured here.
4. English keyword write approval misses some paraphrases and languages; Jev is not authorized to lower that boundary or decide write permissions. This integration never selects write handlers.
5. Existing `detect_intent` logging can include query/parameters. New Jev logs metadata only, but no claim of application-wide PII-safe logging is made.
6. 62 authored examples are small and nonrepresentative. Confidence calibration and benefit on actual traffic are unknown. Provider error/timeout fixtures pass, but no reliability SLA inferred.

## Deployment

Live prestate: `ghcr.io/anton-abyzov/ec-chat-api:develop-81ef02e`; ArgoCD ec-chat-api watches ec-gitops `develop`. Local `argocd-app.yaml` still says `main` and is stale. Production current model configuration: `ACTIVE_MODEL=gemini`, `GEMINI_MODEL=gemini-2.5-flash`.

GitHub `develop` branch records for ec-chat-api and ec-gitops both report `protected:false`; protection/ruleset endpoints return 403 plan limitation. Workflow `Build and Deploy` validates on PR/push; image build runs **only on push**, so workflow_dispatch does not publish an image. Push reviewed source to develop, wait required CI, inspect produced image digest, verify GitOps image tag changed, wait ArgoCD/pod rollout, and read health/image/pod ages back.

No provider key or feature flag is added to production by this change. Existing deployment therefore stays off. Enable only through explicit secret/env configuration after canary/traffic validation. Rollback flag `off` immediately restores previous routing without removing source. Deploying source is not proof of live feature use.

## Verification

Focused routing + approval + auth + runtime + retired-MCP regression suite: **87 passed**, `services.jev_read_router` coverage **99%**. Blocking Python syntax/undefined-name lint: **0 findings**. Test files and replay scripts are committed alongside implementation. Live provider costs above exclude one exploratory request before the corpus, and the separate five-case agent demonstration.

### Release gate correction

Initial CI run failed final i18n registration on an internal caught exception message. Removed the unused message; no user-visible text changed and no gate was waived. Fresh exact local i18n gate: `i18n gate OK: 378 translatable strings all registered.` Fresh routing/authority suite: 87 passed, 99% module coverage. Final source SHA: `e8e0a5d8723a444057309a1377a72525c2769342`.

## Verified deployment — 2026-09-22 04:05 UTC

Final source: `e8e0a5d8723a444057309a1377a72525c2769342`. [Build and Deploy run 35683367197](https://github.com/anton-abyzov/ec-chat-api/actions/runs/35683367197) succeeded. Final full suite: **4,875 passed, 299 skipped, 9 deselected**; required Jev/authority gate: **87 passed**; i18n: **378 registered strings**, green.

GitOps `ce752bf721a50c632125d0bc95bed7804ba06ee9` deployed `ghcr.io/anton-abyzov/ec-chat-api:develop-e8e0a5d`. ArgoCD is Synced/Healthy. Both new replicas were created at 04:02:58 UTC, are ready, and run the same digest `sha256:e53268b8d6452127a88d2702b9133fa7330e40782ad74f1a463f0f2ffcc5ff9c`. Both pod-local health endpoints pass; the public `/ec-chat-api/healthz` endpoint returns HTTP 200 / `healthy`. See `easychamp-deployment.json`.

**Normal production mode remains OFF.** First and only isolated smoke attempt imported the shipped module inside one new pod, verified its source hash, and enabled Jev only in that one-off process. It used an authored sentence and an in-memory fixture API/session, with no customer data, DB writes, or real authorization-path timing. The read routed successfully at confidence .95; actual provider request 431 ms / $0.000021042; local fixture handler path 458 ms. Receipt: `easychamp-pod-smoke-attempt-1.json`. This is deployment proof, not an independent productivity benchmark. No attempts or abstentions were discarded.

No deployment work remains in this lane. Global enablement remains intentionally withheld: representative traffic, multilingual output, and net latency benefit need a controlled pilot before a user-wide rollout claim.
