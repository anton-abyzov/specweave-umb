---
increment: 0677-lm-studio-provider
title: LM Studio Provider — Local LLM Adapter for vSkill Eval
type: feature
priority: P2
status: planned
created: 2026-04-22
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: LM Studio Provider — Local LLM Adapter for vSkill Eval

## Overview

LM Studio is an OpenAI-compatible local LLM server (default endpoint `http://localhost:1234/v1`) widely used by developers evaluating open-weight models privately. vSkill already supports Ollama (see `src/eval/llm.ts:358` and detection in `src/eval-server/api-routes.ts:381-405`). This increment adds LM Studio as a first-class peer provider:

- A new provider adapter in `src/eval/llm.ts` (clone of the OpenRouter code path, pointed at the LM Studio base URL with the dummy API key `lm-studio`).
- Detection in `detectAvailableProviders()` — probe `GET /v1/models` with a 500 ms `AbortSignal.timeout`, 30-second in-memory cache, mirroring the Ollama detection shape.
- UI selector entries in the two places users pick a provider/model today: `ComparisonPage.tsx` and `workspace/RunPanel.tsx`.
- Full test coverage: unit tests for the adapter (mocked `fetch`), integration test for detection surfacing LM Studio when the endpoint responds, jsdom smoke for the selector, optional Playwright E2E that skips when LM Studio is absent.

## Code Location & Scope

**Target codebase:** `repositories/anton-abyzov/vskill/`

**In scope:**
- `src/eval/llm.ts` — adapter + provider union type
- `src/eval-server/api-routes.ts` — `detectAvailableProviders()` health probe
- `src/eval-ui/src/pages/ComparisonPage.tsx` — provider dropdown entry
- `src/eval-ui/src/pages/workspace/RunPanel.tsx` — provider dropdown entry
- New tests under `src/eval/__tests__/` and `tests/e2e/`

**Out of scope:**
- Skill-creation-flow model picker — covered by **0678-skill-gen-source-model-picker**
- SKILL.md emission spec compliance — covered by **0679-skills-spec-compliance**
- Any LM Studio support in `vskill-platform` (Next.js site) — different codebase

## Personas

- **P1 — Privacy-focused evaluator**: runs skills against local-only LM Studio models for IP-sensitive prompts; needs zero egress.
- **P2 — Cost-conscious developer**: wants to A/B compare skills against free local models versus paid cloud models in the same Comparison view.
- **P3 — Offline author**: drafting and evaluating skills on a flight with no network; LM Studio is their only available provider.

## User Stories

### US-001: LM Studio Adapter in `eval/llm.ts` (P1)
**Project**: vskill

**As a** vSkill eval engine consumer
**I want** LM Studio available as a selectable provider that streams OpenAI-compatible completions
**So that** I can evaluate skills against any local model loaded in LM Studio without leaving the eval pipeline

**Acceptance Criteria**:
- [x] **AC-US1-01**: Given `src/eval/llm.ts` declares a provider union type, when the LM Studio adapter is added, then the union includes `"lm-studio"` and the adapter exports a function matching the same signature as the OpenRouter adapter (same parameter shape, same return shape, same streaming contract).
- [x] **AC-US1-02**: Given the LM Studio adapter is invoked with a `model` string and a `messages` array, when it builds the HTTP request, then the request targets `${LM_STUDIO_BASE_URL ?? "http://localhost:1234/v1"}/chat/completions`, the `Authorization` header is `Bearer lm-studio` (dummy key), and the body matches the OpenAI chat completions schema.
- [x] **AC-US1-03**: Given the LM Studio adapter streams responses, when the server returns SSE `data:` frames, then each token chunk is forwarded to the caller's stream handler identically to the OpenRouter path (no special-casing for LM Studio required).
- [x] **AC-US1-04**: Given the LM Studio endpoint returns a non-2xx status, when the adapter receives the error body, then it throws an `Error` whose message includes the HTTP status and the first 200 characters of the response body, matching the OpenRouter adapter's error shape.
- [x] **AC-US1-05**: Given an environment variable `LM_STUDIO_BASE_URL` is set, when the adapter constructs the request URL, then it uses the env value instead of the default; this is documented in the adapter's JSDoc.

---

### US-002: Provider Detection in `api-routes.ts` (P1)
**Project**: vskill

**As a** vSkill Studio user
**I want** LM Studio to appear automatically in provider dropdowns when my local server is running
**So that** I do not need to configure anything if LM Studio is already available

**Acceptance Criteria**:
- [x] **AC-US2-01**: Given `detectAvailableProviders()` in `src/eval-server/api-routes.ts`, when LM Studio is added, then the function probes `GET ${LM_STUDIO_BASE_URL ?? "http://localhost:1234/v1"}/models` using `fetch` with `signal: AbortSignal.timeout(500)` and a catch-all that treats any error as "unavailable" — identical timeout/error semantics to the Ollama probe at lines 381-405.
- [x] **AC-US2-02**: Given the probe returns HTTP 200 with a JSON `{ data: Array<{ id: string }> }` body, when the response is parsed, then the provider entry `{ id: "lm-studio", name: "LM Studio", models: <id-list> }` is pushed into the returned providers array in the same shape as the Ollama entry.
- [x] **AC-US2-03**: Given the probe times out, returns non-2xx, or throws a network error, when the detection runs, then LM Studio is silently omitted from the providers list and no log is emitted above `debug` level.
- [x] **AC-US2-04**: Given the detection result for a given host, when `detectAvailableProviders()` is called again within 30 seconds, then the cached result is returned without a new probe (cache key: provider id + base URL); the 30-second TTL matches the Ollama cache policy.
- [x] **AC-US2-05**: Given detection runs in parallel, when LM Studio and Ollama probes both fire, then they run concurrently via `Promise.all` and the total detection time is ≤ 550 ms even if both time out.

---

### US-003: UI Selector Entries (P2)
**Project**: vskill

**As a** vSkill Studio user viewing the Comparison or Workspace Run panels
**I want** LM Studio to appear in the provider dropdown with the list of loaded models
**So that** I can pick a local model the same way I pick a cloud model

**Acceptance Criteria**:
- [x] **AC-US3-01**: Given `ComparisonPage.tsx` renders the provider dropdown, when `detectAvailableProviders()` returns LM Studio in its result, then the dropdown shows an "LM Studio" option group whose children are the model ids returned by the probe, ordered alphabetically.
- [x] **AC-US3-02**: Given `workspace/RunPanel.tsx` renders the provider dropdown, when LM Studio is detected, then the same option group appears there with identical labeling and identical model ordering as in `ComparisonPage`.
- [x] **AC-US3-03**: Given LM Studio is detected but its `/models` response contained zero models, when the dropdown renders, then the group label "LM Studio" is shown with a single disabled child "No models loaded — open LM Studio and load a model".
- [x] **AC-US3-04**: Given LM Studio is not detected (endpoint down), when either page renders, then no "LM Studio" group appears in the dropdown.

---

### US-004: Test Coverage (P1)
**Project**: vskill

**As a** maintainer
**I want** every new code path covered by a fast deterministic test
**So that** regressions are caught before merge and the provider can be added to new features safely

**Acceptance Criteria**:
- [x] **AC-US4-01**: Given a Vitest unit test file for the LM Studio adapter with `fetch` mocked, when it runs, then it covers: success streaming, non-2xx error, network error, env-var override, and custom model string — all 5 scenarios in < 200 ms total.
- [x] **AC-US4-02**: Given an integration test that stubs the LM Studio `/models` endpoint with a mock server, when `detectAvailableProviders()` is invoked, then the returned array contains the LM Studio entry with the stubbed model ids, and a second invocation within 30 s does not re-probe.
- [x] **AC-US4-03**: Given a jsdom smoke test for `ComparisonPage.tsx` with `detectAvailableProviders` mocked to return LM Studio, when the dropdown is opened, then the LM Studio group and its children are present in the DOM.
- [x] **AC-US4-04**: Given a Playwright E2E test at `tests/e2e/lm-studio.spec.ts`, when the LM Studio endpoint is not reachable at test time, then the test is skipped via `test.skip()` with a descriptive message; when the endpoint is reachable, the test selects LM Studio in Comparison and asserts a successful completion.

## Functional Requirements

- **FR-01**: LM Studio adapter lives at `src/eval/llm.ts` and exports a function matching the OpenRouter adapter signature.
- **FR-02**: Base URL is env-overridable via `LM_STUDIO_BASE_URL` with a sensible default `http://localhost:1234/v1`.
- **FR-03**: Detection is cached for 30 seconds per base URL and runs in parallel with other provider probes.
- **FR-04**: UI selector entries appear automatically when detection succeeds; no manual configuration required.

## Non-Functional Requirements

- **NFR-01 (Performance)**: Provider detection total time ≤ 550 ms when LM Studio and Ollama are both unreachable (both probes honor 500 ms timeout, run in parallel).
- **NFR-02 (Privacy)**: No telemetry or network egress beyond `localhost:1234` for the LM Studio probe; the dummy API key is never sent to any external host.
- **NFR-03 (Test speed)**: Unit test suite for this increment runs in < 500 ms on CI.
- **NFR-04 (Degradation)**: Every failure mode (timeout, 404, parse error, missing models) must leave the UI functional — LM Studio simply does not appear in the list.

## Scope Boundaries

- **In scope**: The adapter, detection probe, UI selector entries, tests.
- **Out of scope**: Skill-generation model picker (0678), SKILL.md spec compliance (0679), any vskill-platform integration.

## Dependencies

- None inbound. This increment unblocks 0678 (which will include LM Studio in its selector because this increment registers it).
