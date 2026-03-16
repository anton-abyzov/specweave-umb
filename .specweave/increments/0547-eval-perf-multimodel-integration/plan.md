# Implementation Plan: vSkill Studio: Eval Performance, Multi-Model & Integration Tests

## Overview

This epic adds three orthogonal capabilities to vSkill's eval system: (1) parallel execution with tiered judging and caching, (2) OpenRouter as a 6th provider plus multi-model sweep with leaderboard, and (3) a browser-based integration test runner with credential management. The existing sequential `for` loop in `benchmark-runner.ts` becomes a `Promise.allSettled` pipeline gated by the existing `Semaphore` from `concurrency.ts`. OpenRouter slots in as a new `case` in `createLlmClient()` following the same direct-HTTP pattern as the Anthropic client. The integration runner is a new module that orchestrates Playwright browser sessions with Chrome profile support, kept entirely separate from the existing benchmark runner.

Team-lead will parallelize across 4 agents: **perf** (US-001/002/003), **multi-model** (US-004/005/006), **integration** (US-008/009/010), **frontend** (US-006/007 UI).

## Architecture

### Component Map

```
src/eval/
  llm.ts                    # MODIFY: add "openrouter" to ProviderName, createOpenRouterClient()
  llm.ts (GenerateResult)   # MODIFY: add optional cost: number | null
  judge.ts                  # MODIFY: accept optional judgeClient param
  judge-cache.ts            # NEW: SHA-256 content-hash cache for judge results
  schema.ts                 # STABLE: testType/requiredCredentials already exist
  comparator.ts             # MODIFY: parallelize skill+baseline generation
  credential-resolver.ts    # NEW: env -> .env.local -> keychain chain

src/eval-server/
  concurrency.ts            # STABLE: reuse existing Semaphore + registry
  benchmark-runner.ts       # MODIFY: parallel case execution via Semaphore
  sweep-runner.ts           # NEW: multi-model sweep orchestration + SSE
  sweep-routes.ts           # NEW: POST /api/skills/:p/:s/sweep SSE endpoint
  api-routes.ts             # MODIFY: add --concurrency, --judge-model, --no-cache params

src/eval/
  integration-runner.ts     # NEW: Playwright-based integration test runner
  integration-types.ts      # NEW: phase types, rate-limit config, safety types
  chrome-profile.ts         # NEW: macOS Chrome profile path resolver

src/commands/
  eval.ts                   # MODIFY: add "sweep" and "credentials" subcommands
  eval/sweep.ts             # NEW: CLI entry for vskill eval sweep
  eval/credentials.ts       # NEW: CLI entry for vskill credentials set/list/check

src/eval-ui/src/
  pages/workspace/TestsPanel.tsx   # MODIFY: unit/integration badges, filter tabs
  pages/LeaderboardPage.tsx        # NEW: sweep results table with sparklines
  components/ModelSearchDropdown.tsx # NEW: OpenRouter model search
  api.ts                           # MODIFY: add sweep, leaderboard, credentials endpoints
  types.ts                         # MODIFY: add SweepResult, LeaderboardEntry types
```

### Data Flow: Parallel Benchmark Execution

```
runBenchmarkSSE(opts)
  |
  +--> evalCases.map(case => async () => {
  |      semaphore.acquire()
  |      try {
  |        const genResult = await client.generate(...)     // generation LLM call
  |        const judgeResults = await Promise.all(          // parallel assertions
  |          case.assertions.map(a =>
  |            judgeCache.getOrCompute(a, genResult.text,   // cache layer
  |              () => judgeAssertion(output, a, judgeClient) // judge LLM call
  |            )
  |          )
  |        )
  |        return assembleBenchmarkCase(genResult, judgeResults)
  |      } finally {
  |        semaphore.release()
  |      }
  |    })
  |
  +--> Promise.allSettled(caseTasks)
  |
  +--> assembleBulkResult(settledResults)
```

### Data Flow: Multi-Model Sweep

```
vskill eval sweep --models "anthropic/claude-sonnet-4,openrouter/meta-llama/llama-3.1-70b"
  |
  +--> parseModelSpecs(modelString)          # parse "provider/model" or "provider/org/model"
  |      returns: ModelSpec[]
  |
  +--> for each ModelSpec:
  |      +--> createLlmClient({ provider, model })
  |      +--> for run in 1..N (--runs):
  |      |      +--> runBenchmarkSSE(client, evalCases)   # reuses parallel runner
  |      |      +--> sendSSE("sweep_model_progress", { model, run, ... })
  |      +--> aggregateRuns(results)                      # mean, stddev
  |
  +--> writeLeaderboard(skillDir, aggregated)             # evals/leaderboard/<ISO>.json
  +--> sendSSE("sweep_complete", leaderboardEntry)
```

### Data Flow: Integration Test Runner

```
integration-runner.ts
  |
  +--> Phase 1: PREFLIGHT
  |     +--> credentialResolver.check(requiredCredentials)
  |     +--> chromeProfile.resolve(profileName)           # macOS path lookup
  |     +--> require.resolve("playwright")                # lazy check, not import-time
  |
  +--> Phase 2: CONNECT
  |     +--> playwright.chromium.launchPersistentContext(profileDir, { ... })
  |     +--> connectMcpServers(evalCase.mcpConfig)        # real mode, not simulation
  |
  +--> Phase 3: EXECUTE
  |     +--> rateLimiter.acquire(platform)                # per-platform throttle
  |     +--> client.generate(systemPrompt, userPrompt)    # LLM with real tool access
  |     +--> mark content with [VSKILL-TEST-{RUN_ID}]
  |
  +--> Phase 4: VERIFY
  |     +--> judgeAssertion(output, assertion, judgeClient)
  |
  +--> Phase 5: CLEANUP (runs on success, failure, and SIGINT)
  |     +--> executeCleanupActions(evalCase.cleanup)
  |     +--> browser.close()
```

### Data Model: Sweep / Leaderboard

Stored at `<skillDir>/evals/leaderboard/<ISO-timestamp>.json`:

```
leaderboard/<ISO>.json
---------------------------------------------
sweepId         string        UUID
timestamp       string        ISO-8601
judge           string        "anthropic/claude-sonnet-4"
runs            number        iterations per model
models          ModelResult[]  per-model aggregated results

ModelResult
---------------------------------------------
provider        string        "anthropic" | "openrouter" | "ollama"
model           string        "claude-sonnet-4" | "meta-llama/llama-3.1-70b"
passRate        { mean, stddev }
rubricScore     { mean, stddev }    (if comparator used)
duration        { mean, stddev }    ms
cost            { total, perCase }  from OpenRouter usage.total_cost
status          "complete" | "error"
errorMessage    string | null
caseResults     CaseResult[]        per-case detail per run
```

### Data Model: Judge Cache

Stored at `<skillDir>/evals/.judge-cache.json`:

```
.judge-cache.json
---------------------------------------------
version         number        1
entries         Record<string, CacheEntry>    key = SHA-256(assertion_text + "||" + skill_output)

CacheEntry
---------------------------------------------
pass            boolean
reasoning       string
cachedAt        string        ISO-8601
judgeModel      string        model used for judging
```

### Data Model: Credential Resolution

```
Resolution chain (first match wins):
  1. process.env[CREDENTIAL_NAME]              # CI/CD environments
  2. .env.local (dotenv, gitignored)           # local development
  3. OS keychain (macOS Keychain, deferred)    # future enhancement
```

### API Contracts

**Existing endpoint modifications:**

`POST /api/skills/:plugin/:skill/benchmark` (existing)
- New query params: `concurrency=N`, `judgeModel=provider/model`, `noCache=true`
- SSE events unchanged; now emitted concurrently with `caseId` scoping

**New endpoints:**

`POST /api/skills/:plugin/:skill/sweep`
- Request body:
  ```json
  {
    "models": ["anthropic/claude-sonnet-4", "openrouter/meta-llama/llama-3.1-70b"],
    "judge": "anthropic/claude-sonnet-4",
    "runs": 3,
    "concurrency": 5
  }
  ```
- SSE events: `sweep_start`, `sweep_model_start`, `sweep_model_progress`, `sweep_model_complete`, `sweep_complete`
- Response (final SSE `done`): Full leaderboard entry

`GET /api/skills/:plugin/:skill/leaderboard`
- Response: `{ entries: SweepResult[] }` sorted by timestamp desc, latest 20

`GET /api/skills/:plugin/:skill/leaderboard/:timestamp`
- Response: Full `SweepResult` with per-model detail

`GET /api/openrouter/models`
- Proxies `GET https://openrouter.ai/api/v1/models`
- Response: `{ models: { id: string, name: string, pricing: { prompt, completion } }[] }`

`POST /api/skills/:plugin/:skill/integration-run`
- Request body: `{ eval_ids?: number[], dryRun?: boolean, confirm?: boolean }`
- SSE events: `preflight_start`, `preflight_result`, `connect`, `execute`, `verify`, `cleanup`, `done`

`GET /api/credentials/:plugin/:skill`
- Response: `{ credentials: { name: string, status: "ready" | "missing" | "untested", source?: "env" | "dotenv" | "keychain" }[] }`

## Technology Stack

- **Runtime**: Node.js ESM (existing)
- **LLM Providers**: Anthropic SDK, OpenRouter (fetch-based, OpenAI-compatible), Ollama, CLI providers
- **Browser Automation**: Playwright (optional peer dependency, lazy `require.resolve` check)
- **Hashing**: Node.js `crypto.createHash('sha256')` for judge cache keys
- **UI Framework**: React 18 + Vite (existing eval-ui stack)
- **Charts**: Inline SVG sparklines (no new chart library; existing `TrendChart.tsx` pattern)

## Architecture Decisions

### AD-1: Reuse existing Semaphore for case-level concurrency

The `Semaphore` class in `concurrency.ts` already exists with acquire/release semantics and a per-skill registry. The spec explicitly requires reusing it rather than introducing a new primitive. The semaphore gates the outer generate call per case; within a case, assertions run via `Promise.all` without additional gating since they are lightweight judge calls on already-generated output.

**Alternative considered**: Worker threads for true parallelism. Rejected because LLM calls are I/O-bound, not CPU-bound, and the existing event loop handles concurrent HTTP requests efficiently.

### AD-2: OpenRouter as direct HTTP client (not CLI spawn)

OpenRouter exposes an OpenAI-compatible REST API at `https://openrouter.ai/api/v1/chat/completions`. It follows the same pattern as `createAnthropicClient()` -- direct `fetch` calls with API key auth. Model IDs like `meta-llama/llama-3.1-70b-instruct` are passed as-is in the `model` field.

The response includes `usage.total_cost` which maps to a new optional `cost` field on `GenerateResult`. When absent, `cost` is `null`.

**Key detail**: The `ProviderName` union extends from 5 to 6 members. All switch statements on `ProviderName` must add the `"openrouter"` case.

### AD-3: Judge cache keyed by content hash, not eval ID

Cache key = `SHA-256(assertion_text || skill_output)`. This means identical outputs from different runs hit the same cache entry, maximizing reuse. The cache is per-skill (`evals/.judge-cache.json`) to avoid cross-skill collisions. Cache entries include `judgeModel` so that switching judge models invalidates stale entries implicitly (lookup includes model in the hash).

Revised key formula: `SHA-256(assertion_text + "||" + skill_output + "||" + judgeModel)`.

**Corruption handling**: If the cache file fails `JSON.parse`, delete it and log a warning. The next run rebuilds it.

### AD-4: Separate judge client for tiered judging

`judgeAssertion()` currently takes a single `LlmClient`. The modification adds an optional `judgeClient` parameter. When provided, the judge uses this client instead of the generation client. This enables using Haiku for judging while Opus generates.

The `runSingleCaseSSE` function gains a `judgeClient?: LlmClient` option. When `judgeModel` is set via CLI flag or API param, `benchmark-runner.ts` creates a second `LlmClient` and passes it through.

**Warning emission**: If the judge model is "weaker" than the generation model (heuristic: model name contains "haiku" while generator contains "opus" or "sonnet"), emit a warning to stderr and SSE.

### AD-5: Integration runner as separate module

`integration-runner.ts` is a standalone module, not embedded in `benchmark-runner.ts`. Rationale: it has fundamentally different dependencies (Playwright, Chrome profiles, rate limiters, cleanup handlers) and a different execution model (phased: preflight -> connect -> execute -> verify -> cleanup).

The integration runner is invoked when `testType === "integration"` cases are selected for execution. The existing `benchmark-runner.ts` filters these out and delegates to the integration runner.

### AD-6: Sweep results as append-only timestamped JSON

Sweep results go to `evals/leaderboard/<ISO-timestamp>.json`, following the same pattern as `evals/history/<ISO>.json`. This provides:
- Append-only history (no overwrites)
- Easy listing via `readdir`
- Consistent with existing history storage

The leaderboard UI reads the last N entries and aggregates sparkline data.

### AD-7: Credential resolution chain

Resolution order: env var -> `.env.local` -> OS keychain (keychain deferred). The `credential-resolver.ts` module provides `resolve(name: string): { value: string, source: string } | null`. The `.env.local` file is read via `dotenv.parse()` (not `dotenv.config()` which mutates `process.env`).

`vskill credentials set X_API_KEY` writes to `.env.local` and ensures `.gitignore` includes it. `vskill credentials check` resolves each credential and reports the source.

### AD-8: SSE event scoping under parallelism

Existing SSE events include `eval_id` which identifies the case. Under parallel execution, multiple cases emit events concurrently. The UI already uses `eval_id` to route events via `useMultiSSE`. The key addition is a `sequence` counter per case to guarantee ordering within a case's event stream.

For sweep SSE, events are scoped by `modelId` (the model being evaluated) in addition to `eval_id`.

### AD-9: Chrome profile resolution (macOS only)

Chrome profiles on macOS are at `~/Library/Application Support/Google/Chrome/<Profile Name>`. The `chrome-profile.ts` module resolves profile names to paths and validates existence. Linux/Windows paths are out of scope per spec; the resolver throws a descriptive error on non-macOS platforms.

Users can override the path via `requirements.chromeProfilePath` in the eval case definition (absolute path, bypasses resolver).

### AD-10: Rate limiting for integration tests

Per-platform rate limits are configurable in the eval case metadata:

```json
{
  "testType": "integration",
  "requirements": {
    "platform": "x",
    "rateLimit": { "requestsPerMinute": 3 }
  }
}
```

A `PlatformRateLimiter` class maintains per-platform token buckets. The `[VSKILL-TEST-{RUN_ID}]` prefix is injected into all content posted during integration tests for identification and cleanup.

## Implementation Phases

### Phase 1: Performance Foundation (Agent: perf)

**Files**: `concurrency.ts`, `benchmark-runner.ts`, `judge.ts`, `judge-cache.ts`, `api-routes.ts`

1. Modify `runBenchmarkSSE` to use `Promise.allSettled` with `Semaphore` for case-level parallelism
2. Modify `runSingleCaseSSE` to run assertion judges via `Promise.all` (intra-case parallelism)
3. Add `judgeClient` parameter to `judgeAssertion()` and `runSingleCaseSSE`
4. Implement `judge-cache.ts` with SHA-256 content-hash keying
5. Add `--concurrency`, `--judge-model`, `--no-cache` CLI flags to `eval.ts`
6. Wire `judgeModel` through API routes and SSE params
7. Parallelize comparator: `Promise.all([generateSkill(), generateBaseline()])` for API providers
8. Emit weak-model judge warning

**Dependencies**: None (foundational)

### Phase 2: Multi-Model (Agent: multi-model)

**Files**: `llm.ts`, `sweep-runner.ts`, `sweep-routes.ts`, `eval.ts`

1. Add `"openrouter"` to `ProviderName` union and `createOpenRouterClient()` in `llm.ts`
2. Add `cost: number | null` to `GenerateResult` interface
3. Implement `sweep-runner.ts` for multi-model orchestration
4. Add `POST /api/skills/:p/:s/sweep` SSE endpoint
5. Add `GET /api/openrouter/models` proxy endpoint
6. Add `vskill eval sweep` CLI subcommand
7. Implement leaderboard storage (`evals/leaderboard/`)
8. Add `GET /api/skills/:p/:s/leaderboard` endpoint

**Dependencies**: Phase 1 (sweep reuses parallel benchmark runner)

### Phase 3: Integration Runner (Agent: integration)

**Files**: `integration-runner.ts`, `integration-types.ts`, `chrome-profile.ts`, `credential-resolver.ts`, `eval.ts`

1. Implement `credential-resolver.ts` (env -> .env.local chain)
2. Implement `chrome-profile.ts` (macOS path resolver)
3. Implement `integration-runner.ts` (5-phase runner)
4. Add `PlatformRateLimiter` class
5. Add SIGINT/cleanup handler
6. Add `vskill credentials set/list/check` CLI subcommands
7. Add `POST /api/skills/:p/:s/integration-run` SSE endpoint
8. Add `--dry-run`, `--confirm`, `--integration` CLI flags
9. Implement Playwright peer dependency check (lazy `require.resolve`)

**Dependencies**: Phase 1 (reuses judge for verify phase)

### Phase 4: Frontend (Agent: frontend)

**Files**: `TestsPanel.tsx`, `LeaderboardPage.tsx`, `ModelSearchDropdown.tsx`, `api.ts`, `types.ts`, `App.tsx`

1. Add unit `[U]` / integration `[I]` badges to TestsPanel
2. Add "All" / "Unit" / "Integration" filter tabs
3. Add lock icon for missing credentials on integration tests
4. Build LeaderboardPage with table (rank, model, pass rate, rubric, duration, cost, sparkline)
5. Implement "Best Model" badge
6. Add empty state with `vskill eval sweep` instructions
7. Build OpenRouter model search dropdown for config UI
8. Add `api.getLeaderboard()`, `api.startSweep()`, `api.getCredentials()` to API client
9. Add LeaderboardPage route to App.tsx router

**Dependencies**: Phase 2 (leaderboard API), Phase 3 (credentials API)

## Testing Strategy

### Unit Tests (Vitest)
- `judge-cache.test.ts`: hash computation, cache hit/miss, corruption recovery, `--no-cache` bypass
- `credential-resolver.test.ts`: env var priority, `.env.local` parsing, missing credential behavior
- `chrome-profile.test.ts`: macOS path resolution, missing profile error, override path
- `sweep-runner.test.ts`: model spec parsing, multi-run aggregation (mean/stddev), partial failure handling
- `openrouter-client.test.ts`: API key validation, cost extraction, model ID passthrough
- `benchmark-runner.test.ts`: parallel execution, semaphore limiting, `Promise.allSettled` error isolation

### Integration Tests (Vitest)
- `benchmark-runner.integration.test.ts`: end-to-end parallel run with mocked LLM client, verify SSE event ordering
- `sweep-routes.integration.test.ts`: full sweep API call with 2 mocked providers, verify leaderboard file written
- `judge-cache.integration.test.ts`: write/read/corrupt/recover cycle on real filesystem

### E2E Tests (Playwright, where applicable)
- Leaderboard page renders with mock data
- TestsPanel filter tabs switch between unit/integration
- Model search dropdown populates and selects

### TDD Cycle
Per config `testMode: "TDD"` -- RED (write failing test) -> GREEN (implement) -> REFACTOR.

## Technical Challenges

### Challenge 1: SSE Event Ordering Under Parallelism
**Problem**: Multiple cases emit SSE events concurrently to the same HTTP response. Events from different cases may interleave.
**Solution**: Each SSE event already includes `eval_id`. The UI routes events by `eval_id` using the existing `useMultiSSE` hook. For the server side, `sendSSE` is called synchronously within each case's async flow -- Node's single-threaded event loop guarantees that individual `res.write()` calls are atomic. No additional synchronization needed.
**Risk**: If a case emits multiple `res.write` calls in rapid succession, they may buffer and arrive in a batch. Mitigation: each SSE message is a complete `event: X\ndata: Y\n\n` block written in a single `res.write()` call.

### Challenge 2: Semaphore Interaction with CLI Providers
**Problem**: CLI providers (claude-cli, codex-cli, gemini-cli) spawn child processes. Running 5 concurrent CLI processes may overwhelm the system.
**Solution**: Default concurrency for CLI providers is 1 (sequential). For API providers (anthropic, openrouter, ollama), default is 5. The `--concurrency` flag overrides this. `estimateDurationSec` already has per-provider timing estimates.

### Challenge 3: OpenRouter Model ID Format
**Problem**: Model IDs can be `org/model` (e.g., `meta-llama/llama-3.1-70b`) which conflicts with the `provider/model` parsing used in sweep.
**Solution**: Sweep model spec format is `provider/model-id` where `model-id` can contain slashes. Parsing splits on the first `/` only for known providers (`anthropic`, `openrouter`, `ollama`, etc.). For `openrouter/meta-llama/llama-3.1-70b`, the provider is `openrouter` and the model is `meta-llama/llama-3.1-70b`.

### Challenge 4: Playwright as Optional Peer Dependency
**Problem**: Playwright is heavy (~100MB) and only needed for integration tests. It should not be required for unit eval users.
**Solution**: Check `require.resolve('playwright')` in the integration runner's preflight phase (not at module import time). If not found, throw a descriptive error with install instructions. The integration runner module uses dynamic `import()` to load Playwright.

### Challenge 5: Integration Test Cleanup on SIGINT
**Problem**: If a user presses Ctrl+C during an integration test that posted content to X/LinkedIn, the test artifacts remain.
**Solution**: Register a SIGINT handler in the integration runner that executes cleanup actions before process exit. Use `process.on('SIGINT', cleanupHandler)` with a flag to prevent double-cleanup. Cleanup failures are logged but do not throw.

### Challenge 6: Judge Cache Invalidation When Switching Judge Models
**Problem**: Cached judge results from Haiku should not be reused when switching to Opus as judge.
**Solution**: Include `judgeModel` in the cache key hash: `SHA-256(assertion_text + "||" + output + "||" + judgeModel)`. Switching models naturally produces different cache keys.

## Agent Boundaries and Shared Interfaces

To enable parallel agent work, these interfaces serve as contracts between agents:

### Shared Interface: GenerateResult (perf + multi-model)
```typescript
// llm.ts -- multi-model agent adds `cost`, perf agent consumes it
export interface GenerateResult {
  text: string;
  durationMs: number;
  inputTokens: number | null;
  outputTokens: number | null;
  cost: number | null;  // NEW: OpenRouter total_cost
}
```

### Shared Interface: judgeAssertion signature (perf + integration)
```typescript
// judge.ts -- perf agent adds judgeClient param
export async function judgeAssertion(
  output: string,
  assertion: Assertion,
  client: LlmClient,          // generation client (existing)
  judgeClient?: LlmClient,    // NEW: optional separate judge client
  mcpDeps?: McpDependency[],
): Promise<AssertionResult>
```

### Shared Interface: ProviderName (perf + multi-model)
```typescript
// llm.ts -- multi-model agent extends union
export type ProviderName = "anthropic" | "claude-cli" | "codex-cli" | "gemini-cli" | "ollama" | "openrouter";
```

### Merge Coordination
- **perf** agent owns `benchmark-runner.ts`, `judge.ts`, `concurrency.ts`
- **multi-model** agent owns `llm.ts` (adds openrouter), `sweep-runner.ts`, `sweep-routes.ts`
- **integration** agent owns `integration-runner.ts`, `chrome-profile.ts`, `credential-resolver.ts`
- **frontend** agent owns all `eval-ui/` changes

The `llm.ts` file is touched by both perf (consuming `cost` in estimates) and multi-model (adding `cost` to `GenerateResult` and `openrouter` provider). Multi-model agent makes the structural changes; perf agent reads the interface.
