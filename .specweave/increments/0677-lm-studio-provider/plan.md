---
increment: 0677-lm-studio-provider
title: LM Studio Provider — Technical Plan
type: plan
status: draft
created: 2026-04-22
architect: sw:architect
---

# Plan: LM Studio Provider

## 1. Architecture Overview

LM Studio exposes an OpenAI-compatible REST API at `http://localhost:1234/v1` (configurable in the app). Because the surface area is a strict subset of OpenAI's chat completions API, the existing OpenRouter provider adapter in `src/eval/llm.ts` is the cleanest template: both speak OpenAI-shaped HTTP, both stream SSE, both require only a base URL + API key to differ. The LM Studio adapter is therefore a pointwise clone of the OpenRouter adapter with three constants swapped:

| Constant | OpenRouter | LM Studio |
|---|---|---|
| Base URL | `https://openrouter.ai/api/v1` | `process.env.LM_STUDIO_BASE_URL ?? "http://localhost:1234/v1"` |
| API key | `process.env.OPENROUTER_API_KEY` (required) | `"lm-studio"` (dummy; LM Studio ignores it) |
| Provider id | `"openrouter"` | `"lm-studio"` |

No new streaming code, no new error path, no new retry logic. This is the minimum viable change.

Detection mirrors the Ollama pattern already present in `src/eval-server/api-routes.ts:381-405` — a `GET /models` probe with a 500 ms `AbortSignal.timeout`, a 30-second in-memory cache, and silent failure treated as "not installed". The two probes (Ollama + LM Studio) run concurrently via `Promise.all`.

UI additions are data-driven: the two dropdowns in `ComparisonPage.tsx` and `workspace/RunPanel.tsx` already map over `detectAvailableProviders()` output, so they automatically render LM Studio once it is added to the detection result. The only UI change is ensuring the two pages use the same typed provider enum.

## 2. Component Map

| File | Change | Rationale |
|---|---|---|
| `src/eval/llm.ts` (around line 358, after Ollama) | Add `callLMStudio(...)` adapter cloned from OpenRouter; extend provider union to include `"lm-studio"` | Minimum viable new provider |
| `src/eval-server/api-routes.ts` (around line 381, next to Ollama probe) | Add `probeLMStudio()` helper; call alongside Ollama inside `detectAvailableProviders()` | Detection surface |
| `src/eval-ui/src/pages/ComparisonPage.tsx` | Verify typed enum includes `"lm-studio"`; no UI code change if dropdown is data-driven | UI selector |
| `src/eval-ui/src/pages/workspace/RunPanel.tsx` | Same as ComparisonPage | UI selector parity |
| `src/eval/__tests__/lm-studio.test.ts` | New Vitest unit suite for the adapter | TDD gate |
| `src/eval-server/__tests__/detect-providers.test.ts` | Extend existing detection suite with LM Studio cases | TDD gate |
| `src/eval-ui/src/__tests__/run-panel-selector.test.tsx` | Small jsdom smoke test for the dropdown | TDD gate |
| `tests/e2e/lm-studio.spec.ts` | Playwright smoke; `test.skip()` if endpoint not reachable | Regression guard for real users |
| `README.md` or docs page | Document `LM_STUDIO_BASE_URL` env override | Discoverability |

## 3. Data & Types

Extend the existing provider union in `src/eval/llm.ts`:

```ts
type Provider = "claude-cli" | "openrouter" | "ollama" | "lm-studio";
```

Detection result entry shape matches the Ollama entry:

```ts
{ id: "lm-studio", name: "LM Studio", models: string[] }
```

No new database schema, no new config file entries beyond the optional env var.

## 4. Detection Cache

The existing 30-second cache in `api-routes.ts` is keyed by provider id. Extend the same map rather than introducing a parallel cache. A single `Map<string, { at: number; providers: DetectedProvider[] }>` keyed by a host-scope string is sufficient; the cache invalidation rule is "TTL expired or explicit `?refresh=1` query param on the probe endpoint".

## 5. Error Handling

The Ollama adapter treats every exception from `fetch` as "not available" and silently omits Ollama from the result. The LM Studio probe does the same. The adapter itself (as opposed to the probe) surfaces errors verbosely because the caller is an eval run that must fail loudly — this mirrors the OpenRouter adapter's behavior and requires zero new logic.

## 6. Testing Strategy

Three levels:

1. **Unit** (Vitest, mocked `fetch`) — adapter behavior under success, 4xx, 5xx, network error, env-var override. Target: 5 tests, < 200 ms total.
2. **Integration** (Vitest with a mock server via `msw` or the existing test harness) — `detectAvailableProviders()` returns LM Studio when the mock responds; cache hit on second call; concurrency with Ollama.
3. **E2E** (Playwright) — one happy-path test that opens Comparison, picks LM Studio, runs an eval. Gated on endpoint reachability; `test.skip()` otherwise.

## 7. ADRs

### ADR-0677-01: Clone OpenRouter adapter rather than abstracting a generic "OpenAI-compatible" adapter

**Status**: Accepted
**Context**: LM Studio and OpenRouter both speak the OpenAI chat-completions protocol. A generalization is tempting: one `createOpenAICompatibleAdapter({ baseUrl, apiKey, id })` factory to replace both. The factory would reduce duplication today.
**Decision**: Clone the OpenRouter function body verbatim with three constants swapped. Do not introduce the factory.
**Consequences**:
- **Pro**: Zero risk of regressing OpenRouter (code path unchanged); zero new abstractions; change footprint is minimal.
- **Pro**: When LM Studio ships a feature OpenRouter does not (or vice versa), the two can diverge without coordination.
- **Con**: ~40 lines of duplication between the two adapters.
- **Counter**: The duplication is stable (OpenAI API shape) and visible; DRY fatigue would be worse than the duplication itself. If a third OpenAI-compatible provider lands later, the factory refactor can happen then with three call sites giving it real pressure.

### ADR-0677-02: Dummy API key `lm-studio` instead of requiring a user-supplied token

**Status**: Accepted
**Context**: LM Studio accepts any non-empty Bearer token. Requiring users to configure an env var for a localhost-only service would be friction without security benefit.
**Decision**: Hardcode the literal string `"lm-studio"` as the Bearer token; document that LM Studio does not check it.
**Consequences**: Zero-config for the happy path. Users on LM Studio forks that do enforce tokens can still override via a forthcoming `LM_STUDIO_API_KEY` env var — not shipped in this increment, but called out in the adapter's JSDoc.

### ADR-0677-03: Detection probe hits `/models`, not `/health` or a TCP connect

**Status**: Accepted
**Context**: Options considered: (a) TCP `connect()` to port 1234 — not portable in Node's `fetch`; (b) `/health` — not part of the OpenAI API and not served by LM Studio; (c) `GET /v1/models` — always served by LM Studio, returns the actual model list (useful for the UI dropdown).
**Decision**: Use `/models`. One round-trip both answers "is it up?" and populates the model list.
**Consequences**: Slightly more data per probe than a health check would return, but within any reasonable bandwidth budget for a localhost call. Saves a second probe.

## 8. Rollout

1. Land adapter + tests (TDD: test first, then adapter).
2. Land detection + tests.
3. Land UI confirmation tests (the dropdowns should just work if they are data-driven — verify, do not rewrite).
4. Land Playwright smoke with `test.skip()` fallback.
5. Update `README.md` with a one-paragraph section on the `LM_STUDIO_BASE_URL` env var.

No feature flag. LM Studio appears only when detected, so the change is invisible to users without LM Studio installed.
