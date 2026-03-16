# Tasks: vSkill Studio: Eval Performance, Multi-Model & Integration Tests

## Lane Assignments

| Lane | Agent | User Stories | Tasks |
|------|-------|-------------|-------|
| PERF | Performance agent | US-001, US-002, US-003 | T-001 – T-015 |
| MULTI | Multi-model agent | US-004, US-005 | T-016 – T-029 |
| INTG | Integration agent | US-008, US-009, US-010 | T-030 – T-044 |
| FE | Frontend agent | US-006, US-007 | T-045 – T-057 |

---

## LANE: PERF — Performance agent

### US-001: Parallel Eval Execution

---

### T-001: Parallelize case execution in benchmark-runner via Semaphore
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-03
**Lane**: PERF
**Status**: [x] Completed

**Implementation Details**:
- In `src/eval-server/benchmark-runner.ts`, replace the sequential `for` loop over eval cases with `cases.map(case => asyncTask)` collected into an array
- Wrap each task with `semaphore.acquire()` / `semaphore.release()` in a `try/finally`
- Replace `Promise.all` at the outer level with `Promise.allSettled` so individual failures are isolated
- Default semaphore limit: `5` for API providers, `1` for CLI providers (detect by `ProviderName`)
- Reuse the `Semaphore` class from `src/eval-server/concurrency.ts` — do not introduce a new primitive

**Test**:
Given a 10-case eval suite with default concurrency 5, when `runBenchmarkSSE` is called, then at most 5 LLM calls execute simultaneously (verified by a concurrency counter spy), and all 10 results are present in the settled array regardless of individual failures.
- **File**: `src/eval-server/benchmark-runner.test.ts`
- **TC-001**: Semaphore limits concurrency to default 5 — Given 10 cases and default concurrency, When runBenchmarkSSE runs, Then max concurrent calls never exceeds 5
- **TC-002**: Promise.allSettled isolates failures — Given case 3 throws, When other cases complete, Then results array length is 10 with case 3 showing status "rejected"

**Dependencies**: None

---

### T-002: Add --concurrency CLI flag to `vskill eval run`
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02
**Lane**: PERF
**Status**: [x] Completed

**Implementation Details**:
- In `src/commands/eval.ts`, add `--concurrency <N>` option to the `run` subcommand (type: `number`, default: `5`)
- Pass `concurrency` down through the API request body to `benchmark-runner.ts` (create semaphore with `new Semaphore(concurrency)`)
- Add `concurrency` query param to `POST /api/skills/:p/:s/benchmark` in `src/eval-server/api-routes.ts`

**Test**:
Given `vskill eval run --concurrency 2` is executed against a 6-case suite, when the eval runs, then at most 2 LLM calls run simultaneously.
- **File**: `src/eval-server/benchmark-runner.test.ts`
- **TC-003**: Custom concurrency flag respected — Given --concurrency 2, When 6 cases run, Then peak concurrent calls is 2

**Dependencies**: T-001

---

### T-003: Parallelize intra-case assertion judges via Promise.all
**User Story**: US-001 | **Satisfies ACs**: AC-US1-04
**Lane**: PERF
**Status**: [x] Completed

**Implementation Details**:
- In `runSingleCaseSSE`, replace sequential assertion judging with `Promise.all(assertions.map(a => judgeAssertion(output, a, judgeClient)))`
- All assertion judges for a single case execute concurrently once the generation output is ready
- No additional semaphore needed for intra-case judges (they are lightweight and bounded per case)

**Test**:
Given a case with 5 assertions and a mock judge that records call start times, when the case output is generated, then all 5 judge calls are initiated before any of them resolves.
- **File**: `src/eval-server/benchmark-runner.test.ts`
- **TC-004**: Intra-case assertions run concurrently — Given 5 assertions on one case, When case output is ready, Then all 5 judgeAssertion calls are in-flight simultaneously

**Dependencies**: T-001

---

### T-004: Parallelize comparator skill+baseline generation
**User Story**: US-001 | **Satisfies ACs**: AC-US1-05
**Lane**: PERF
**Status**: [x] Completed

**Implementation Details**:
- In `src/eval/comparator.ts`, replace sequential skill/baseline generation with `Promise.all([generateSkill(prompt, skillClient), generateBaseline(prompt, baselineClient)])`
- Only apply to API providers; CLI providers keep sequential order (CLI concurrency caveat from plan)
- Destructure `[skillResult, baselineResult]` from the settled array

**Test**:
Given comparator mode with a mock skillClient and baselineClient, when `runComparatorCase` is called, then both generate calls are initiated before either resolves (verified by recording call timestamps).
- **File**: `src/eval/comparator.test.ts`
- **TC-005**: Skill and baseline generation are concurrent — Given mock skill and baseline clients, When runComparatorCase runs, Then both generate() calls start within 1ms of each other

**Dependencies**: T-001

---

### T-005: Add separate judgeClient param to judgeAssertion and runSingleCaseSSE
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-03
**Lane**: PERF
**Status**: [x] Completed

**Implementation Details**:
- In `src/eval/judge.ts`, update `judgeAssertion(output, assertion, client, judgeClient?, mcpDeps?)` — when `judgeClient` is provided, use it for the judge LLM call; otherwise use `client` (backward compatible)
- In `benchmark-runner.ts`, thread `judgeClient` through `runSingleCaseSSE(opts: { ..., judgeClient?: LlmClient })`
- When `judgeModel` is configured, `benchmark-runner` creates a second `LlmClient` and passes it as `judgeClient`

**Test**:
Given judgeClient is provided, when judgeAssertion runs, then it calls judgeClient.generate (not the generation client). Given judgeClient is absent, when judgeAssertion runs, then the generation client is used.
- **File**: `src/eval/judge.test.ts`
- **TC-006**: judgeClient overrides generation client — Given separate judgeClient, When judgeAssertion called, Then judgeClient.generate is called, not generationClient.generate
- **TC-007**: Backward compatibility — Given no judgeClient, When judgeAssertion called, Then generationClient.generate is used

**Dependencies**: T-001

---

### T-006: Wire --judge-model CLI flag through API and runner
**User Story**: US-002 | **Satisfies ACs**: AC-US2-02, AC-US2-04
**Lane**: PERF
**Status**: [x] Completed

**Implementation Details**:
- Add `--judge-model <provider/model>` option to `vskill eval run` in `src/commands/eval.ts`
- Pass `judgeModel` as a request param on `POST /api/skills/:p/:s/benchmark`
- In `benchmark-runner.ts`, when `judgeModel` is set, call `createLlmClient({ provider, model })` to get a second client and pass it as `judgeClient`
- Emit weak-model warning: if judge model name contains `"haiku"` while generator contains `"opus"` or `"sonnet"`, emit `console.warn` to stderr and an SSE `warning` event

**Test**:
Given --judge-model anthropic/claude-haiku-3 while generator is claude-opus, when eval starts, then a warning is emitted to stderr. Given --judge-model anthropic/claude-haiku-3, when assertions run, then the haiku client is used for judging.
- **File**: `src/eval-server/benchmark-runner.test.ts`
- **TC-008**: Weak-model warning emitted — Given haiku judge with opus generator, When eval starts, Then console.warn is called with a "weaker model" message
- **TC-009**: judgeModel wired end-to-end — Given --judge-model flag, When API route processes request, Then a separate LlmClient is created for judging

**Dependencies**: T-005

---

### T-007: Implement judge-cache.ts with SHA-256 content-hash keying
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-04
**Lane**: PERF
**Status**: [x] Completed

**Implementation Details**:
- Create `src/eval/judge-cache.ts`
- Cache key: `SHA-256(assertion_text + "||" + skill_output + "||" + judgeModel)` using `crypto.createHash('sha256')`
- Cache file: `<skillDir>/evals/.judge-cache.json` (gitignored)
- Schema: `{ version: 1, entries: Record<string, { pass: boolean, reasoning: string, cachedAt: string, judgeModel: string }> }`
- Export `JudgeCache` class with `getOrCompute(assertion, output, judgeModel, compute: () => Promise<AssertionResult>): Promise<AssertionResult>`
- On cache file load failure (`JSON.parse` throws), delete the file, log a warning, and start fresh

**Test**:
Given a completed judge call, when getOrCompute is called with the same assertion+output+judgeModel, then the cached result is returned without calling compute. Given cache file is corrupted, when JudgeCache loads, then it deletes the file and rebuilds.
- **File**: `src/eval/judge-cache.test.ts`
- **TC-010**: Cache hit returns stored result — Given identical assertion+output+judgeModel, When getOrCompute called twice, Then compute() called only once
- **TC-011**: Cache miss calls compute — Given new assertion+output, When getOrCompute called, Then compute() is invoked and result stored
- **TC-012**: Corruption recovery — Given malformed JSON in cache file, When JudgeCache initializes, Then file is deleted and empty cache created
- **TC-013**: Cache stored at correct path — Given skillDir, When JudgeCache writes, Then file is at <skillDir>/evals/.judge-cache.json

**Dependencies**: None

---

### T-008: Wire judge cache into benchmark-runner and add --no-cache flag
**User Story**: US-003 | **Satisfies ACs**: AC-US3-02, AC-US3-03
**Lane**: PERF
**Status**: [x] Completed

**Implementation Details**:
- In `benchmark-runner.ts`, instantiate `JudgeCache` per run (keyed to skillDir) and wrap each `judgeAssertion` call with `judgeCache.getOrCompute(...)`
- Add `--no-cache` flag to `vskill eval run` in `src/commands/eval.ts`
- When `noCache: true`, bypass `getOrCompute` and call `judgeAssertion` directly (or pass a `bypass` flag to `JudgeCache`)
- Add `noCache` query param to `POST /api/skills/:p/:s/benchmark`

**Test**:
Given --no-cache flag, when eval runs, then getOrCompute is bypassed and compute() is called for every assertion regardless of cache state. Given --no-cache is absent, when the same eval runs twice, then the second run uses cached results.
- **File**: `src/eval-server/benchmark-runner.test.ts`
- **TC-014**: --no-cache bypasses cache — Given --no-cache flag, When eval runs, Then compute() called for every assertion
- **TC-015**: Cache used when flag absent — Given no --no-cache, When same eval runs twice, Then compute() called once per unique assertion+output pair

**Dependencies**: T-007

---

### T-009: Add .judge-cache.json to .gitignore
**User Story**: US-003 | **Satisfies ACs**: AC-US3-04
**Lane**: PERF
**Status**: [x] Completed

**Implementation Details**:
- In `vskill credentials set` (or a shared initialization path), when the judge cache file is first created, check if `evals/.judge-cache.json` is in the nearest `.gitignore`; if not, append it
- Alternatively, add it to the vskill project template `.gitignore` if one exists
- Verify the pattern `evals/.judge-cache.json` is covered

**Test**:
Given a new skillDir without a .gitignore entry, when JudgeCache writes its first entry, then evals/.judge-cache.json is added to .gitignore.
- **File**: `src/eval/judge-cache.test.ts`
- **TC-016**: gitignore updated on first write — Given no existing gitignore entry, When JudgeCache first writes, Then .gitignore contains evals/.judge-cache.json

**Dependencies**: T-007

---

### T-010: Integration test — parallel benchmark end-to-end with SSE ordering
**User Story**: US-001, US-002, US-003 | **Satisfies ACs**: AC-US1-01, AC-US1-03, AC-US1-04
**Lane**: PERF
**Status**: [x] Completed

**Implementation Details**:
- Create `src/eval-server/benchmark-runner.integration.test.ts`
- Use a mocked `LlmClient` that resolves with artificial delays (randomized 10-100ms) to simulate real concurrency
- Run 8 cases with concurrency 3; assert all 8 results present, max concurrent count never exceeds 3, SSE events include `caseId`, and events per case arrive in sequence order

**Test**:
Given 8 eval cases with a delay-simulating LLM mock and concurrency 3, when runBenchmarkSSE is called, then all 8 results are returned, concurrency never exceeds 3, and each case's SSE events are ordered by sequence field.
- **File**: `src/eval-server/benchmark-runner.integration.test.ts`
- **TC-017**: End-to-end parallel run — Given 8 cases + concurrency 3, When runBenchmarkSSE runs, Then all 8 results present and peak concurrency <= 3
- **TC-018**: SSE event ordering — Given parallel execution, When events emitted, Then each case's events have monotonically increasing sequence numbers

**Dependencies**: T-001, T-002, T-003, T-007, T-008

---

### T-011: Add 429 retry with exponential backoff in benchmark-runner
**User Story**: US-001 | **Satisfies ACs**: AC-US1-03 (edge case)
**Lane**: PERF
**Status**: [x] Completed

**Implementation Details**:
- In `benchmark-runner.ts`, when a case's LLM generate call throws with status 429, retry with delays 1s, 2s, 4s (max 3 retries) before marking the case as `error`
- Use `setTimeout` wrapped in a `Promise` for delays
- Log each retry attempt as an SSE `warning` event with `{ caseId, attempt, delayMs }`

**Test**:
Given an LLM client that returns 429 twice then succeeds, when runBenchmarkSSE processes that case, then it retries twice and the case completes successfully. Given 3 consecutive 429s, then the case is marked error after exhausting retries.
- **File**: `src/eval-server/benchmark-runner.test.ts`
- **TC-019**: Retry on 429 — Given LLM throws 429 twice then succeeds, When case runs, Then case result is success after 2 retries
- **TC-020**: Exhausted retries mark case error — Given 3 consecutive 429s, When case runs, Then case result status is "error"

**Dependencies**: T-001

---

### T-012: SSE events include caseId under parallelism
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01 (edge case from spec)
**Lane**: PERF
**Status**: [x] Completed

**Implementation Details**:
- Verify all SSE events emitted from `runSingleCaseSSE` include `caseId` in the data payload
- Add a `sequence` counter (per-case integer starting at 0) to each SSE event emitted within a case
- Update SSE event type definitions in `src/eval-server/` to include `caseId: string | number` and `sequence: number`

**Test**:
Given parallel execution of 3 cases, when SSE events are captured, then every event has a caseId field and events within each case have ascending sequence numbers.
- **File**: `src/eval-server/benchmark-runner.test.ts`
- **TC-021**: SSE events carry caseId — Given parallel cases, When events captured, Then every event.data.caseId is set
- **TC-022**: Sequence numbers per case — Given single case emitting 4 events, When events captured, Then sequence is 0,1,2,3

**Dependencies**: T-001

---

### T-013: Unit tests for judge-cache corruption and model-keyed invalidation
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02
**Lane**: PERF
**Status**: [x] Completed

**Implementation Details**:
- Create thorough unit tests verifying that changing `judgeModel` in the cache key causes a cache miss (different SHA-256 produces a different key)
- Test that same assertion+output but different judgeModel hits compute() again
- Test the integration cycle: write cache, read from real filesystem, corrupt file, verify recovery

**Test**:
Given identical assertion+output but different judgeModel values, when getOrCompute called, then compute() is invoked for each distinct judgeModel. Given cache written and file corrupted, when JudgeCache reloaded, then a fresh empty cache is used.
- **File**: `src/eval/judge-cache.test.ts`
- **TC-023**: Different judgeModel = cache miss — Given same assertion+output, different judgeModel, When getOrCompute called, Then compute() invoked each time
- **TC-024**: Filesystem round-trip — Given cache written to disk, When JudgeCache reloads, Then entries are read back correctly

**Dependencies**: T-007

---

### T-014: Performance benchmark — verify 4-6x speedup on 10-case suite
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02
**Lane**: PERF
**Status**: [x] Completed

**Implementation Details**:
- Create a timing test in `benchmark-runner.integration.test.ts` that simulates 10 cases each taking ~200ms with a delay mock
- Sequential baseline (concurrency 1): ~2000ms total
- Parallel run (concurrency 5): ~400-600ms total
- Assert that parallel duration is < 50% of sequential duration

**Test**:
Given 10 cases each simulated at 200ms and concurrency 5, when runBenchmarkSSE runs, then total duration is under 800ms (vs ~2000ms sequential).
- **File**: `src/eval-server/benchmark-runner.integration.test.ts`
- **TC-025**: Parallel speedup measured — Given 10 x 200ms cases, concurrency 5, When run, Then duration < 800ms

**Dependencies**: T-001, T-002

---

### T-015: Update api-routes.ts to accept concurrency, judgeModel, noCache params
**User Story**: US-001, US-002, US-003 | **Satisfies ACs**: AC-US1-02, AC-US2-02, AC-US3-03
**Lane**: PERF
**Status**: [x] Completed

**Implementation Details**:
- In `src/eval-server/api-routes.ts`, update the `POST /api/skills/:p/:s/benchmark` handler to extract `concurrency`, `judgeModel`, `noCache` from request body/query
- Validate `concurrency` is a positive integer (default 5); validate `judgeModel` matches `provider/model` format if present
- Pass all three into the `runBenchmarkSSE` options object

**Test**:
Given a POST with body { concurrency: 3, judgeModel: "anthropic/claude-haiku", noCache: true }, when api-routes processes it, then runBenchmarkSSE is called with exactly those options.
- **File**: `src/eval-server/api-routes.test.ts`
- **TC-026**: API params parsed and forwarded — Given request with concurrency/judgeModel/noCache, When POST /benchmark handled, Then runBenchmarkSSE called with those options
- **TC-027**: Invalid concurrency rejected — Given concurrency: -1, When POST /benchmark, Then 400 response returned

**Dependencies**: T-001, T-005, T-008

---

## LANE: MULTI — Multi-model agent

### US-004: OpenRouter Provider

---

### T-016: Extend ProviderName union and create OpenRouter LLM client
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02, AC-US4-04
**Lane**: MULTI
**Status**: [x] Completed

**Implementation Details**:
- In `src/eval/llm.ts`, extend `ProviderName` to `"anthropic" | "claude-cli" | "codex-cli" | "gemini-cli" | "ollama" | "openrouter"`
- Add `case "openrouter":` to all `switch` statements on `ProviderName`
- Implement `createOpenRouterClient(model: string, apiKey: string): LlmClient`
  - Base URL: `https://openrouter.ai/api/v1/chat/completions`
  - Auth: `Authorization: Bearer ${apiKey}` header
  - Model ID passed as-is in the `model` field (e.g., `meta-llama/llama-3.1-70b-instruct`)
  - When `OPENROUTER_API_KEY` is missing, throw `Error("OPENROUTER_API_KEY is not set. Get your key at https://openrouter.ai/keys")`
- In `createLlmClient()`, add `case "openrouter"` that reads `OPENROUTER_API_KEY` from env

**Test**:
Given VSKILL_EVAL_PROVIDER=openrouter and OPENROUTER_API_KEY set, when createLlmClient() is called, then the returned client sends requests to openrouter.ai/api/v1/chat/completions. Given OPENROUTER_API_KEY missing, when called, then it throws a descriptive error.
- **File**: `src/eval/openrouter-client.test.ts`
- **TC-028**: Client sends to correct URL — Given valid API key, When client.generate() called, Then fetch is called with openrouter.ai URL
- **TC-029**: Model ID passed as-is — Given model "meta-llama/llama-3.1-70b-instruct", When generate() called, Then request body model field is exactly that string
- **TC-030**: Missing API key throws — Given no OPENROUTER_API_KEY, When createLlmClient("openrouter"), Then error message contains "OPENROUTER_API_KEY" and setup URL

**Dependencies**: None (defines shared ProviderName — perf agent reads this)

---

### T-017: Add cost field to GenerateResult and extract from OpenRouter response
**User Story**: US-004 | **Satisfies ACs**: AC-US4-03
**Lane**: MULTI
**Status**: [x] Completed

**Implementation Details**:
- In `src/eval/llm.ts`, add `cost: number | null` to `GenerateResult` interface
- In `createOpenRouterClient`, after parsing the response, set `cost = response.usage?.total_cost ?? null`
- All other provider clients return `cost: null` to satisfy the interface
- Ensure `GenerateResult` is exported and all consumers compile without type errors

**Test**:
Given an OpenRouter response with usage.total_cost: 0.0025, when generate() resolves, then result.cost is 0.0025. Given usage.total_cost absent, when generate() resolves, then result.cost is null.
- **File**: `src/eval/openrouter-client.test.ts`
- **TC-031**: Cost extracted from response — Given total_cost: 0.0025, When generate() resolves, Then result.cost === 0.0025
- **TC-032**: Missing total_cost yields null — Given no total_cost in response, When generate() resolves, Then result.cost === null

**Dependencies**: T-016

---

### T-018: Add GET /api/openrouter/models proxy endpoint
**User Story**: US-004 | **Satisfies ACs**: AC-US4-05
**Lane**: MULTI
**Status**: [x] Completed

**Implementation Details**:
- Add `GET /api/openrouter/models` route in `src/eval-server/api-routes.ts`
- Proxy to `GET https://openrouter.ai/api/v1/models` using `OPENROUTER_API_KEY` from env
- Return `{ models: { id: string, name: string, pricing: { prompt: number, completion: number } }[] }`
- If `OPENROUTER_API_KEY` is missing, return `{ error: "OPENROUTER_API_KEY not configured" }` with status 400

**Test**:
Given OPENROUTER_API_KEY set and OpenRouter API returns a list, when GET /api/openrouter/models is called, then it returns a list of model objects. Given missing API key, then it returns 400 with an error.
- **File**: `src/eval-server/api-routes.test.ts`
- **TC-033**: Models proxied correctly — Given valid API key + mocked OR response, When GET /api/openrouter/models, Then response contains model id and name fields
- **TC-034**: Missing key returns 400 — Given no OPENROUTER_API_KEY, When GET /api/openrouter/models, Then 400 with error message

**Dependencies**: T-016

---

### T-019: Implement sweep-runner.ts for multi-model orchestration
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01, AC-US5-02, AC-US5-04, AC-US5-05
**Lane**: MULTI
**Status**: [x] Completed

**Implementation Details**:
- Create `src/eval-server/sweep-runner.ts`
- Export `runSweep(opts: SweepOpts): AsyncGenerator<SweepSSEEvent>`
- Parse `models` string: split on first `/` for provider; for `openrouter/org/model`, provider=`openrouter`, model=`org/model`
- For each model (sequentially, not parallel — models may share rate limits):
  - Create LLM client, run N iterations via `runBenchmarkSSE` (reusing the parallel runner from Phase 1)
  - Emit `sweep_model_start`, `sweep_model_progress` (per case per run), `sweep_model_complete`
  - On error: mark model status `"error"` with message, continue to next model
- After all models: aggregate `{ mean, stddev }` for passRate, rubricScore, duration, cost per model
- Emit `sweep_complete` with full leaderboard entry

**Test**:
Given sweep --models "anthropic/claude-sonnet-4,openrouter/meta-llama/llama-3.1-70b" with 2 runs, when runSweep executes, then both models run 2 iterations each, mean/stddev computed, and sweep_complete emitted. Given one model errors, then sweep continues and errored model shows status "error".
- **File**: `src/eval-server/sweep-runner.test.ts`
- **TC-035**: Both models run and aggregate — Given 2 models 2 runs, When runSweep completes, Then result has 2 ModelResult entries with mean and stddev fields
- **TC-036**: Failed model continues sweep — Given model 1 throws API error, When sweep runs, Then model 1 has status "error" and model 2 completes normally
- **TC-037**: SSE progress events emitted — Given sweep running, When a case completes, Then sweep_model_progress event contains { model, currentCase, percentComplete }

**Dependencies**: T-016, T-001 (reuses parallel benchmark runner from perf lane)

---

### T-020: Parse model spec strings (provider/model and provider/org/model)
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01
**Lane**: MULTI
**Status**: [x] Completed

**Implementation Details**:
- Implement `parseModelSpec(spec: string): { provider: ProviderName, model: string }` in `sweep-runner.ts`
- Known providers: `anthropic`, `openrouter`, `ollama`, `claude-cli`, `codex-cli`, `gemini-cli`
- Split on first `/` only: `"openrouter/meta-llama/llama-3.1-70b"` → `{ provider: "openrouter", model: "meta-llama/llama-3.1-70b" }`
- Throw descriptive error for unknown providers

**Test**:
Given "openrouter/meta-llama/llama-3.1-70b", when parseModelSpec called, then provider is "openrouter" and model is "meta-llama/llama-3.1-70b". Given "anthropic/claude-sonnet-4", then provider "anthropic" and model "claude-sonnet-4". Given "unknown/foo", then error thrown.
- **File**: `src/eval-server/sweep-runner.test.ts`
- **TC-038**: openrouter/org/model parsed correctly — Given "openrouter/meta-llama/llama-3.1-70b", When parseModelSpec, Then { provider: "openrouter", model: "meta-llama/llama-3.1-70b" }
- **TC-039**: anthropic/model parsed — Given "anthropic/claude-sonnet-4", When parseModelSpec, Then { provider: "anthropic", model: "claude-sonnet-4" }
- **TC-040**: Unknown provider throws — Given "unknown/foo", When parseModelSpec, Then error thrown with provider name in message

**Dependencies**: T-016

---

### T-021: Write sweep results to leaderboard storage
**User Story**: US-005 | **Satisfies ACs**: AC-US5-03
**Lane**: MULTI
**Status**: [x] Completed

**Implementation Details**:
- In `sweep-runner.ts`, after sweep completes, write results to `<skillDir>/evals/leaderboard/<ISO-timestamp>.json`
- Ensure `evals/leaderboard/` directory is created if absent (`fs.mkdir` with `recursive: true`)
- File schema: `{ sweepId: UUID, timestamp: ISO-8601, judge: string, runs: number, models: ModelResult[] }`
- `ModelResult` includes: provider, model, passRate `{mean, stddev}`, rubricScore `{mean, stddev}`, duration `{mean, stddev}`, cost `{total, perCase}`, status, errorMessage, caseResults

**Test**:
Given a completed sweep, when runSweep finalizes, then a JSON file exists at evals/leaderboard/<timestamp>.json with correct sweepId, judge, and model results.
- **File**: `src/eval-server/sweep-runner.test.ts`
- **TC-041**: Leaderboard file written — Given sweep completes, When checkLeaderboardDir, Then timestamped JSON file exists
- **TC-042**: File schema correct — Given sweep result, When file parsed, Then sweepId, timestamp, models array all present

**Dependencies**: T-019

---

### T-022: Add POST /api/skills/:p/:s/sweep SSE endpoint
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01, AC-US5-05
**Lane**: MULTI
**Status**: [x] Completed

**Implementation Details**:
- Create `src/eval-server/sweep-routes.ts`
- Add `POST /api/skills/:plugin/:skill/sweep` route with SSE response
- Accept body: `{ models: string[], judge: string, runs?: number, concurrency?: number }`
- Stream `runSweep` generator events as SSE (`event: sweep_model_progress\ndata: {...}\n\n`)
- Handle client disconnect (close generator early)

**Test**:
Given POST /api/skills/my-plugin/my-skill/sweep with 2 models, when the request executes, then SSE events are streamed including sweep_model_start, sweep_model_progress, and sweep_complete events.
- **File**: `src/eval-server/sweep-routes.integration.test.ts`
- **TC-043**: SSE events streamed — Given 2-model sweep request, When POST /sweep, Then SSE includes sweep_model_start for each model and sweep_complete at end
- **TC-044**: Leaderboard file written after sweep API call — Given sweep API call completes, When leaderboard dir checked, Then file exists

**Dependencies**: T-019, T-021

---

### T-023: Add GET /api/skills/:p/:s/leaderboard endpoints
**User Story**: US-005, US-006 | **Satisfies ACs**: AC-US5-03, AC-US6-01
**Lane**: MULTI
**Status**: [x] Completed

**Implementation Details**:
- In `sweep-routes.ts`, add:
  - `GET /api/skills/:plugin/:skill/leaderboard` — returns `{ entries: SweepResult[] }` sorted by timestamp desc, latest 20
  - `GET /api/skills/:plugin/:skill/leaderboard/:timestamp` — returns single full `SweepResult`
- Read from `<skillDir>/evals/leaderboard/` using `fs.readdir` + `fs.readFile`
- Return `{ entries: [] }` if directory does not exist

**Test**:
Given 3 leaderboard files exist, when GET /leaderboard, then returns all 3 sorted newest first. Given directory absent, then returns { entries: [] }. Given a specific timestamp, when GET /leaderboard/:timestamp, then returns that specific result.
- **File**: `src/eval-server/sweep-routes.integration.test.ts`
- **TC-045**: Returns sorted entries — Given 3 files, When GET /leaderboard, Then entries sorted newest first
- **TC-046**: Empty state — Given no leaderboard dir, When GET /leaderboard, Then { entries: [] }
- **TC-047**: Single entry lookup — Given specific timestamp, When GET /leaderboard/:timestamp, Then that entry returned

**Dependencies**: T-021

---

### T-024: Add vskill eval sweep CLI subcommand
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01, AC-US5-02
**Lane**: MULTI
**Status**: [x] Completed

**Implementation Details**:
- Create `src/commands/eval/sweep.ts`
- Register `sweep` subcommand under `vskill eval` in `src/commands/eval.ts`
- Flags: `--models <string>` (required, comma-separated), `--judge <provider/model>` (required), `--runs <N>` (default 1), `--concurrency <N>` (default 5)
- Invoke `runSweep` directly (not via API) and render progress table to stdout
- Print summary table on completion (rank, model, pass rate, mean duration)

**Test**:
Given `vskill eval sweep --models "anthropic/claude-sonnet-4" --judge "anthropic/claude-sonnet-4" --runs 2`, when executed, then sweep runs with 2 iterations and prints a summary table.
- **File**: `src/commands/eval/sweep.test.ts`
- **TC-048**: CLI sweep invokes runner — Given valid --models and --judge flags, When sweep command runs, Then runSweep is called with correct options
- **TC-049**: Summary table printed — Given sweep completes, When output checked, Then stdout contains rank and model name columns

**Dependencies**: T-019, T-020

---

### T-025: Compute mean and stddev for sweep multi-run aggregation
**User Story**: US-005 | **Satisfies ACs**: AC-US5-02
**Lane**: MULTI
**Status**: [x] Completed

**Implementation Details**:
- In `sweep-runner.ts`, implement `aggregateRuns(results: BenchmarkResult[]): ModelStats`
- Compute `mean = sum/N` and `stddev = sqrt(sum((x-mean)^2)/N)` for passRate, rubricScore (if present), duration, cost (if present)
- Handle N=1 gracefully (stddev = 0)

**Test**:
Given 3 runs with passRates [0.8, 0.9, 0.7], when aggregateRuns called, then mean is 0.8 and stddev is approximately 0.0816. Given 1 run, then stddev is 0.
- **File**: `src/eval-server/sweep-runner.test.ts`
- **TC-050**: Mean computed correctly — Given passRates [0.8, 0.9, 0.7], When aggregateRuns, Then mean === 0.8
- **TC-051**: Stddev computed correctly — Given passRates [0.8, 0.9, 0.7], When aggregateRuns, Then stddev ≈ 0.0816
- **TC-052**: N=1 stddev is 0 — Given single run, When aggregateRuns, Then stddev === 0

**Dependencies**: T-019

---

### T-026: Integration test — full sweep with 2 mocked providers writes leaderboard
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01, AC-US5-03, AC-US5-04
**Lane**: MULTI
**Status**: [x] Completed

**Implementation Details**:
- Create `src/eval-server/sweep-routes.integration.test.ts`
- Mock `createLlmClient` to return different fake clients per provider
- Run a 2-model sweep with --runs 2
- Assert: correct leaderboard file written, SSE `sweep_complete` event emitted, ModelResult for each model present

**Test**:
Given 2-model sweep with 3 eval cases and 2 runs, when full sweep integration test runs, then leaderboard JSON file exists with 2 ModelResult entries each having 2 runs worth of data.
- **File**: `src/eval-server/sweep-routes.integration.test.ts`
- **TC-053**: Full sweep writes leaderboard — Given 2 models, 2 runs, 3 cases, When sweep completes, Then leaderboard file has 2 ModelResult entries
- **TC-054**: Failed provider in sweep — Given provider 2 throws, When sweep completes, Then provider 2 has status "error" and leaderboard file still written

**Dependencies**: T-019, T-021, T-022

---

### T-027: Handle OpenRouter API key validation and error messages
**User Story**: US-004 | **Satisfies ACs**: AC-US4-04
**Lane**: MULTI
**Status**: [x] Completed

**Implementation Details**:
- When `OPENROUTER_API_KEY` is not set and provider is `openrouter`, throw: `Error("OPENROUTER_API_KEY is not set. Visit https://openrouter.ai/keys to get your key, then run: export OPENROUTER_API_KEY=<your-key>")`
- Validate at `createLlmClient()` call time, not at module import time
- Ensure the error message is surfaced via SSE `error` event when thrown during a benchmark run

**Test**:
Given provider "openrouter" and missing OPENROUTER_API_KEY, when createLlmClient is called, then error thrown with URL. Given error during benchmark run, when SSE captures it, then error event includes the message.
- **File**: `src/eval/openrouter-client.test.ts`
- **TC-055**: Error contains setup URL — Given missing API key, When createLlmClient("openrouter"), Then error message contains openrouter.ai/keys
- **TC-056**: Error surfaced in SSE — Given missing key during bench run, When events captured, Then SSE includes event type "error" with message

**Dependencies**: T-016

---

### T-028: CLI provider sequential default — cap concurrency to 1 for CLI providers
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02 (CLI edge case from plan)
**Lane**: MULTI
**Status**: [x] Completed

**Implementation Details**:
- In `benchmark-runner.ts`, when provider is `claude-cli`, `codex-cli`, or `gemini-cli`, default concurrency to `1` (overrideable via explicit `--concurrency` flag)
- Log a warning when a user sets `--concurrency > 1` for CLI providers: "CLI providers may not support true parallelism"
- Add a `getDefaultConcurrency(provider: ProviderName): number` helper

**Test**:
Given provider "claude-cli" and no --concurrency flag, when benchmark runs, then semaphore limit is 1. Given provider "anthropic", then default is 5.
- **File**: `src/eval-server/benchmark-runner.test.ts`
- **TC-057**: CLI provider defaults to concurrency 1 — Given claude-cli provider, When no --concurrency flag, Then semaphore limit is 1
- **TC-058**: API provider defaults to concurrency 5 — Given anthropic provider, When no --concurrency flag, Then semaphore limit is 5

**Dependencies**: T-001, T-016

---

### T-029: Unit tests — OpenRouter client end-to-end with fetch mock
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02, AC-US4-03
**Lane**: MULTI
**Status**: [x] Completed

**Implementation Details**:
- Create `src/eval/openrouter-client.test.ts`
- Use `vi.mock` or `vi.hoisted` to mock `fetch`
- Test: correct URL, correct model passthrough, cost extraction, null cost fallback, error on missing key
- Verify `Authorization: Bearer` header is set

**Test**:
Given a mock fetch that returns a successful OpenRouter response, when createOpenRouterClient("meta-llama/llama-3.1-70b").generate() is called, then fetch was called with openrouter.ai URL, Authorization header set, model field correct, and cost extracted.
- **File**: `src/eval/openrouter-client.test.ts`
- **TC-059**: Correct request structure — Given mock fetch, When generate() called, Then request has correct URL, Authorization header, and model field
- **TC-060**: Full response parsing — Given response with choices, usage.total_cost, When generate() called, Then result.text and result.cost both populated

**Dependencies**: T-016, T-017

---

## LANE: INTG — Integration agent

### US-008: Credential Management CLI

---

### T-030: Implement credential-resolver.ts (env -> .env.local chain)
**User Story**: US-008 | **Satisfies ACs**: AC-US8-03
**Lane**: INTG
**Status**: [x] Completed

**Implementation Details**:
- Create `src/eval/credential-resolver.ts`
- Export `resolveCredential(name: string, skillDir: string): { value: string, source: "env" | "dotenv" } | null`
- Resolution order: 1) `process.env[name]`, 2) `.env.local` in `skillDir` parsed via `dotenv.parse()` (not `dotenv.config()`)
- Export `resolveAllCredentials(names: string[], skillDir: string): CredentialStatus[]`
  - `CredentialStatus: { name: string, status: "ready" | "missing", source?: string }`

**Test**:
Given X_API_KEY in process.env, when resolveCredential called, then returns { value, source: "env" }. Given X_API_KEY not in env but in .env.local, then returns { value, source: "dotenv" }. Given neither, then returns null.
- **File**: `src/eval/credential-resolver.test.ts`
- **TC-061**: env var takes priority — Given key in process.env and .env.local, When resolveCredential, Then source is "env"
- **TC-062**: .env.local fallback — Given key absent from env but in .env.local, When resolveCredential, Then source is "dotenv"
- **TC-063**: Missing credential returns null — Given key absent from both, When resolveCredential, Then returns null

**Dependencies**: None

---

### T-031: Implement vskill credentials set command
**User Story**: US-008 | **Satisfies ACs**: AC-US8-01, AC-US8-04
**Lane**: INTG
**Status**: [x] Completed

**Implementation Details**:
- Create `src/commands/eval/credentials.ts`
- Register `vskill credentials set <KEY>` subcommand
- Prompt for value using `readline` or `@inquirer/password` (hidden input)
- Write to `<cwd>/.env.local` (create if absent): append `KEY=value` line
- After writing, check if `.gitignore` exists; if not present or `.env.local` not in it, append `.env.local` to `.gitignore`

**Test**:
Given vskill credentials set X_API_KEY with value "secret", when command runs, then .env.local contains X_API_KEY=secret. Given .gitignore exists without .env.local, then .env.local is added to .gitignore.
- **File**: `src/commands/eval/credentials.test.ts`
- **TC-064**: Credential written to .env.local — Given set command with value, When command runs, Then .env.local contains KEY=value
- **TC-065**: .env.local added to .gitignore — Given .gitignore without .env.local entry, When set command runs, Then .gitignore contains .env.local line

**Dependencies**: T-030

---

### T-032: Implement vskill credentials list and check commands
**User Story**: US-008 | **Satisfies ACs**: AC-US8-02, AC-US8-03
**Lane**: INTG
**Status**: [x] Completed

**Implementation Details**:
- `vskill credentials list`: reads skill's `evals/*.json` to find all `requiredCredentials` across integration test cases; prints table with `name`, `status` (Ready/Missing/Untested)
- `vskill credentials check`: calls `resolveCredential` for each credential found; prints table with `name`, `status`, `source`
- Both commands require the current directory to contain a vskill skill (check for `skill.json` or similar marker)

**Test**:
Given an eval file with requiredCredentials: ["X_API_KEY", "LINKEDIN_TOKEN"] and X_API_KEY set in env, when vskill credentials list, then X_API_KEY is "Ready" and LINKEDIN_TOKEN is "Missing".
- **File**: `src/commands/eval/credentials.test.ts`
- **TC-066**: credentials list shows correct statuses — Given 2 credentials, 1 in env, When list command, Then Ready and Missing statuses shown
- **TC-067**: credentials check shows source — Given credential in .env.local, When check command, Then source column shows "dotenv"

**Dependencies**: T-030

---

### T-033: Implement chrome-profile.ts macOS path resolver
**User Story**: US-009 | **Satisfies ACs**: AC-US9-01
**Lane**: INTG
**Status**: [x] Completed

**Implementation Details**:
- Create `src/eval/chrome-profile.ts`
- Export `resolveProfile(profileName: string): string`
  - macOS path: `~/Library/Application Support/Google/Chrome/<profileName>`
  - Expand `~` to `os.homedir()`
  - Check `fs.existsSync(path)`; if not found, throw error listing available profiles (from `fs.readdirSync` of parent Chrome dir)
- Throw `UnsupportedPlatformError` on non-macOS (`process.platform !== "darwin"`)
- Export `listProfiles(): string[]` — returns profile names from the Chrome dir

**Test**:
Given macOS with profile "Profile 3" existing, when resolveProfile("Profile 3"), then returns correct absolute path. Given profile not found, then error lists available profiles. Given non-macOS, then UnsupportedPlatformError thrown.
- **File**: `src/eval/chrome-profile.test.ts`
- **TC-068**: macOS path resolved correctly — Given profile "Profile 3", When resolveProfile on macOS, Then returns ~/Library/...Google/Chrome/Profile 3 expanded path
- **TC-069**: Missing profile lists available — Given profile "Nonexistent", When resolveProfile, Then error message includes available profile names
- **TC-070**: Non-macOS throws — Given process.platform !== "darwin", When resolveProfile, Then UnsupportedPlatformError thrown

**Dependencies**: None

---

### T-034: Implement integration-types.ts (phase types, rate-limit, safety)
**User Story**: US-009, US-010 | **Satisfies ACs**: AC-US9-02, AC-US10-01
**Lane**: INTG
**Status**: [x] Completed

**Implementation Details**:
- Create `src/eval/integration-types.ts`
- Export `IntegrationPhase = "preflight" | "connect" | "execute" | "verify" | "cleanup"`
- Export `PhaseResult = { phase: IntegrationPhase, status: "pass" | "fail" | "skipped", errorMessage?: string }`
- Export `IntegrationRunResult = { evalId: string, phases: PhaseResult[], overallPass: boolean, testArtifactIds: string[] }`
- Export `PlatformRateLimit = { requestsPerMinute: number }`
- Export `RateLimit config shape that matches eval case JSON schema`

**Test**:
Given a PhaseResult with status "fail", when type-checked, then TypeScript compiles without errors. Given an IntegrationRunResult, then it includes all 5 phases.
- **File**: `src/eval/integration-types.test.ts`
- **TC-071**: Type exports compile — Given integration-types imported, When used in test file, Then TypeScript compilation succeeds
- **TC-072**: PhaseResult shape validated — Given { phase: "preflight", status: "pass" }, When assigned to PhaseResult, Then no TS error

**Dependencies**: None

---

### T-035: Implement PlatformRateLimiter class
**User Story**: US-010 | **Satisfies ACs**: AC-US10-01
**Lane**: INTG
**Status**: [x] Completed

**Implementation Details**:
- In `src/eval/integration-runner.ts` or a separate `rate-limiter.ts`
- `PlatformRateLimiter` class: maintains per-platform token buckets
- `acquire(platform: string): Promise<void>` — waits until a token is available for the platform
- Config from eval case: `requirements.rateLimit.requestsPerMinute`
- Default limits: `x: 3/min`, `linkedin: 2/min`, others: `10/min`

**Test**:
Given platform "x" configured at 3/min, when acquire("x") called 4 times in rapid succession, then the 4th call waits at least 20 seconds (1 token = 1/3 min). Given platform with no config, then uses default limit.
- **File**: `src/eval/rate-limiter.test.ts`
- **TC-073**: Rate limit enforced — Given 3/min limit, When 4 acquires called, Then 4th acquire delayed by ~20s (use fake timers)
- **TC-074**: Default limit applied — Given unknown platform, When acquire called, Then uses 10/min default

**Dependencies**: T-034

---

### T-036: Implement integration-runner.ts — 5-phase runner
**User Story**: US-009 | **Satisfies ACs**: AC-US9-01, AC-US9-02, AC-US9-05
**Lane**: INTG
**Status**: [x] Completed

**Implementation Details**:
- Create `src/eval/integration-runner.ts`
- Export `runIntegrationCase(evalCase: EvalCase, opts: IntegrationRunOpts): Promise<IntegrationRunResult>`
- Phase 1 PREFLIGHT: call `credentialResolver.check(requiredCredentials)`, call `chromeProfile.resolve(profileName)`, call `checkPlaywright()`
- Phase 2 CONNECT: dynamic `import("playwright")`, launch `chromium.launchPersistentContext(profileDir, headless: false)`
- Phase 3 EXECUTE: call `rateLimiter.acquire(platform)`, inject `[VSKILL-TEST-{RUN_ID}]` prefix, call LLM with real MCP tools
- Phase 4 VERIFY: call `judgeAssertion(output, assertion, judgeClient)` for each assertion
- Phase 5 CLEANUP: run `evalCase.cleanup` actions, call `browser.close()`
- When `dryRun: true`, skip actual API calls in EXECUTE phase, log would-have-happened actions

**Test**:
Given an eval case with testType "integration", chromeProfile "Profile 1", and requiredCredentials ["X_API_KEY"], when runIntegrationCase runs with all prereqs met, then it proceeds through all 5 phases and returns IntegrationRunResult. Given dryRun: true, then EXECUTE phase logs but does not call LLM.
- **File**: `src/eval/integration-runner.test.ts`
- **TC-075**: All 5 phases execute — Given valid eval case and all prereqs, When runIntegrationCase, Then result.phases has 5 entries all with status "pass"
- **TC-076**: Dry run skips LLM call — Given dryRun: true, When runIntegrationCase runs, Then LLM generate() not called but phases logged
- **TC-077**: Preflight fails on missing credential — Given missing credential, When runIntegrationCase, Then preflight phase returns status "fail" and runner aborts

**Dependencies**: T-030, T-033, T-034, T-035

---

### T-037: Implement SIGINT cleanup handler for integration tests
**User Story**: US-009 | **Satisfies ACs**: AC-US9-04
**Lane**: INTG
**Status**: [x] Completed

**Implementation Details**:
- In `integration-runner.ts`, register `process.on('SIGINT', cleanupAndExit)` before starting EXECUTE phase
- `cleanupAndExit` flag prevents double-cleanup
- On SIGINT: run cleanup actions, call `browser.close()`, log "Cleanup complete, exiting", then `process.exit(0)`
- Cleanup failures during SIGINT are logged but do not throw (test result stands independently)
- Deregister SIGINT handler after cleanup completes

**Test**:
Given an integration test in progress and SIGINT emitted, when signal handler fires, then cleanup actions are executed and browser.close() is called before exit.
- **File**: `src/eval/integration-runner.test.ts`
- **TC-078**: SIGINT triggers cleanup — Given integration test running, When process.emit("SIGINT"), Then cleanup actions run and browser.close() called
- **TC-079**: Cleanup failure does not throw — Given cleanup action throws, When SIGINT cleanup runs, Then error logged but process exits cleanly

**Dependencies**: T-036

---

### T-038: Implement Playwright peer dependency lazy check
**User Story**: US-010 | **Satisfies ACs**: AC-US10-04
**Lane**: INTG
**Status**: [x] Completed

**Implementation Details**:
- In `integration-runner.ts` Phase 1 PREFLIGHT, add `checkPlaywright()`:
  ```ts
  try { require.resolve("playwright"); } catch { throw new Error("Playwright is not installed...") }
  ```
- Error message: `"Playwright is required for integration tests. Install it with: npm install --save-dev playwright && npx playwright install chromium"`
- Do NOT import Playwright at module top level — use dynamic `import()` in CONNECT phase only

**Test**:
Given Playwright is not installed (require.resolve throws), when runIntegrationCase is called, then preflight fails with a clear error containing install instructions. Given Playwright is installed, then preflight passes.
- **File**: `src/eval/integration-runner.test.ts`
- **TC-080**: Missing Playwright caught at preflight — Given require.resolve mocked to throw, When runIntegrationCase, Then phase 1 fails with install instructions in error
- **TC-081**: Playwright present passes preflight check — Given require.resolve succeeds, When preflight runs, Then playwright check passes

**Dependencies**: T-036

---

### T-039: Inject [VSKILL-TEST-{RUN_ID}] prefix into integration test content
**User Story**: US-010 | **Satisfies ACs**: AC-US10-02
**Lane**: INTG
**Status**: [x] Completed

**Implementation Details**:
- In EXECUTE phase of `integration-runner.ts`, generate `RUN_ID = crypto.randomUUID().slice(0, 8).toUpperCase()`
- Prepend `[VSKILL-TEST-${RUN_ID}]` to all content passed to platform APIs (injected into LLM prompt instructions)
- Store `testArtifactIds` in `IntegrationRunResult` for cleanup reference
- In the CLEANUP phase, use the prefix to identify and remove test artifacts

**Test**:
Given an integration test posting to platform "x", when execute phase runs, then the LLM prompt includes [VSKILL-TEST-<RUN_ID>] prefix instructions. Given cleanup phase runs, then it uses the same RUN_ID for artifact identification.
- **File**: `src/eval/integration-runner.test.ts`
- **TC-082**: Test prefix injected into prompt — Given execute phase, When LLM prompt captured, Then prompt contains [VSKILL-TEST-xxxxx] prefix instruction
- **TC-083**: RUN_ID consistent across phases — Given execute and cleanup phases, When RUN_ID compared, Then same value used in both

**Dependencies**: T-036

---

### T-040: Implement --confirm flag and first-run confirmation prompt
**User Story**: US-010 | **Satisfies ACs**: AC-US10-03
**Lane**: INTG
**Status**: [x] Completed

**Implementation Details**:
- In the integration runner or CLI command, when `--confirm` flag is not set and this is the first run against a platform, display a confirmation prompt listing the actions to be performed
- Detect "first run" by checking for absence of a run history file at `<skillDir>/evals/.integration-history.json`
- Prompt: "This will perform the following actions on <platform>: [action list]. Proceed? (y/N)"
- Skip prompt when `--confirm` is explicitly set or when `CI=true` env var is present

**Test**:
Given --confirm not set and no prior run history, when integration test starts, then a confirmation prompt is shown listing the actions. Given --confirm flag set, then no prompt shown.
- **File**: `src/eval/integration-runner.test.ts`
- **TC-084**: Confirmation prompt shown — Given no --confirm and no history, When runner starts, Then prompt displayed with action list
- **TC-085**: --confirm skips prompt — Given --confirm flag, When runner starts, Then no prompt and execution proceeds

**Dependencies**: T-036

---

### T-041: Add POST /api/skills/:p/:s/integration-run SSE endpoint
**User Story**: US-009 | **Satisfies ACs**: AC-US9-02
**Lane**: INTG
**Status**: [x] Completed

**Implementation Details**:
- In `src/eval-server/api-routes.ts`, add `POST /api/skills/:plugin/:skill/integration-run`
- Accept body: `{ eval_ids?: number[], dryRun?: boolean, confirm?: boolean }`
- Stream phase events as SSE: `preflight_start`, `preflight_result`, `connect`, `execute`, `verify`, `cleanup`, `done`
- Each event includes `evalId`, `phase`, `status`, and optional `error`

**Test**:
Given POST /integration-run with eval_ids: [1, 2], when request processed, then SSE events include preflight_start and eventually done event.
- **File**: `src/eval-server/api-routes.test.ts`
- **TC-086**: SSE events streamed for integration run — Given POST /integration-run, When request processes, Then SSE preflight_start and done events emitted
- **TC-087**: dryRun param forwarded — Given dryRun: true in body, When API handles request, Then runner called with dryRun: true

**Dependencies**: T-036

---

### T-042: Add GET /api/credentials/:plugin/:skill endpoint
**User Story**: US-008 | **Satisfies ACs**: AC-US8-02
**Lane**: INTG
**Status**: [x] Completed

**Implementation Details**:
- In `src/eval-server/api-routes.ts`, add `GET /api/credentials/:plugin/:skill`
- Read integration test cases from `<skillDir>/evals/` to find all `requiredCredentials`
- Call `resolveAllCredentials(names, skillDir)` to check status
- Return `{ credentials: { name: string, status: "ready" | "missing" | "untested", source?: "env" | "dotenv" }[] }`

**Test**:
Given a skill with integration tests requiring ["X_API_KEY", "LINKEDIN_TOKEN"] and X_API_KEY in env, when GET /api/credentials/plugin/skill, then X_API_KEY is "ready" and LINKEDIN_TOKEN is "missing".
- **File**: `src/eval-server/api-routes.test.ts`
- **TC-088**: Credentials endpoint returns statuses — Given 2 required credentials, 1 set, When GET /credentials, Then correct ready/missing statuses returned
- **TC-089**: Source included for ready credentials — Given credential resolved from dotenv, When GET /credentials, Then source "dotenv" included in response

**Dependencies**: T-030, T-032

---

### T-043: Unit tests for credential-resolver with real fs mocks
**User Story**: US-008 | **Satisfies ACs**: AC-US8-01, AC-US8-03, AC-US8-04
**Lane**: INTG
**Status**: [x] Completed

**Implementation Details**:
- Create `src/eval/credential-resolver.test.ts`
- Use `vi.mock("fs")` or a temp directory to simulate `.env.local` reads
- Test: env var priority, `.env.local` fallback, missing key, multiple credentials, dotenv parse error

**Test**:
Given .env.local with X_API_KEY=test123 and no env var, when resolveCredential("X_API_KEY") called, then returns { value: "test123", source: "dotenv" }.
- **File**: `src/eval/credential-resolver.test.ts`
- **TC-090**: dotenv file parsed without mutating process.env — Given .env.local with KEY=val, When resolveCredential, Then process.env unchanged after call
- **TC-091**: Multi-credential resolution — Given 3 credentials with mixed presence, When resolveAllCredentials, Then each status is correct

**Dependencies**: T-030

---

### T-044: Integration test — credential resolution and chrome profile end-to-end
**User Story**: US-008, US-009 | **Satisfies ACs**: AC-US9-01, AC-US8-03
**Lane**: INTG
**Status**: [x] Completed

**Implementation Details**:
- Create a test that writes a temporary `.env.local`, resolves credentials from it, and verifies source is "dotenv"
- Mock `fs.existsSync` to simulate Chrome profile existence; verify `resolveProfile` returns correct macOS path
- Assert both resolve correctly together in a simulated preflight phase

**Test**:
Given a temp .env.local with credentials and a mocked Chrome profile directory, when a simulated preflight runs, then credentials resolved from dotenv and profile path resolved to the macOS path.
- **File**: `src/eval/integration-runner.test.ts`
- **TC-092**: Preflight succeeds with valid credentials and profile — Given .env.local and mocked profile dir, When preflight runs, Then both checks pass
- **TC-093**: Preflight fails with missing profile — Given valid credentials but missing profile, When preflight runs, Then phase status "fail" with profile error message

**Dependencies**: T-030, T-033, T-036

---

## LANE: FE — Frontend agent

### US-007: Unit vs. Integration Test UI Differentiation

---

### T-045: Add testType type badges to TestsPanel
**User Story**: US-007 | **Satisfies ACs**: AC-US7-01, AC-US7-02
**Lane**: FE
**Status**: [x] Completed

**Implementation Details**:
- In `src/eval-ui/src/pages/workspace/TestsPanel.tsx`, add a badge alongside each eval case row
- Blue `[U]` badge (Tailwind: `bg-blue-100 text-blue-700 text-xs font-mono px-1 rounded`) for `testType: "unit"`
- Amber `[I]` badge (`bg-amber-100 text-amber-700`) for `testType: "integration"`
- Default to `"unit"` if `testType` is absent (backward compatible)

**Test**:
Given a unit test case, when rendered in TestsPanel, then a blue [U] badge is present. Given an integration test case, then an amber [I] badge is present.
- **File**: `src/eval-ui/src/pages/workspace/TestsPanel.test.tsx`
- **TC-094**: Unit badge rendered — Given testType "unit", When TestsPanel renders, Then [U] badge present with blue styling
- **TC-095**: Integration badge rendered — Given testType "integration", When TestsPanel renders, Then [I] badge present with amber styling
- **TC-096**: Default to unit badge — Given no testType field, When TestsPanel renders, Then [U] badge shown

**Dependencies**: None

---

### T-046: Add lock icon for integration tests with missing credentials
**User Story**: US-007 | **Satisfies ACs**: AC-US7-03
**Lane**: FE
**Status**: [x] Completed

**Implementation Details**:
- In `TestsPanel.tsx`, for each integration test case, call `api.getCredentials()` to check credential status
- If any required credential has status `"missing"`, render a lock icon (`LockClosedIcon` from Heroicons or SVG) with `title="Configure credentials to run"` tooltip
- Lock icon only appears on integration test rows with unconfigured credentials

**Test**:
Given an integration test with LINKEDIN_TOKEN as requiredCredential and status "missing", when rendered in TestsPanel, then a lock icon with tooltip "Configure credentials to run" is shown.
- **File**: `src/eval-ui/src/pages/workspace/TestsPanel.test.tsx`
- **TC-097**: Lock icon on missing credentials — Given integration test with missing credential, When rendered, Then lock icon with correct tooltip present
- **TC-098**: No lock icon when credentials ready — Given integration test with all credentials "ready", When rendered, Then no lock icon shown

**Dependencies**: T-042 (credentials API endpoint)

---

### T-047: Add All/Unit/Integration filter tabs to TestsPanel
**User Story**: US-007 | **Satisfies ACs**: AC-US7-04
**Lane**: FE
**Status**: [x] Completed

**Implementation Details**:
- Add filter tabs `["All", "Unit", "Integration"]` above the test list in `TestsPanel.tsx`
- Active tab state: `useState<"all" | "unit" | "integration">("all")`
- Filter eval cases by `testType`: "All" shows all, "Unit" shows `testType !== "integration"`, "Integration" shows `testType === "integration"`
- Tabs styled with active indicator (border-b-2 on active tab)

**Test**:
Given a mix of unit and integration tests, when "Integration" tab is clicked, then only integration tests are shown. When "All" tab is clicked, then all tests are shown.
- **File**: `src/eval-ui/src/pages/workspace/TestsPanel.test.tsx`
- **TC-099**: Unit filter shows only unit tests — Given 3 unit + 2 integration cases, When "Unit" tab clicked, Then only 3 cases shown
- **TC-100**: Integration filter shows only integration — Given mix, When "Integration" tab clicked, Then only 2 cases shown
- **TC-101**: All tab restores full list — Given "Integration" tab active, When "All" tab clicked, Then all 5 cases shown

**Dependencies**: T-045

---

### T-048: Add platform note for integration tests on vskill platform
**User Story**: US-007 | **Satisfies ACs**: AC-US7-05
**Lane**: FE
**Status**: [x] Completed

**Implementation Details**:
- In the platform-facing eval results view (if it exists in eval-ui), when an eval case has `testType: "integration"`, replace run result columns with the text: `"Run locally in vSkill Studio"`
- If the results view is shared between Studio and platform contexts, gate on a `isPlatform` prop or env variable
- Add a `data-testid="platform-integration-note"` attribute for testability

**Test**:
Given platform context and an integration test with no result, when the eval result row renders, then "Run locally in vSkill Studio" text is shown instead of result data.
- **File**: `src/eval-ui/src/pages/workspace/TestsPanel.test.tsx`
- **TC-102**: Platform note shown for integration tests — Given isPlatform=true and integration test, When results rendered, Then "Run locally in vSkill Studio" present
- **TC-103**: Unit tests still show results on platform — Given isPlatform=true and unit test with result, When rendered, Then actual result data shown

**Dependencies**: T-045

---

### T-049: Create LeaderboardPage component with model table
**User Story**: US-006 | **Satisfies ACs**: AC-US6-01, AC-US6-02
**Lane**: FE
**Status**: [x] Completed

**Implementation Details**:
- Create `src/eval-ui/src/pages/LeaderboardPage.tsx`
- Fetch from `GET /api/skills/:p/:s/leaderboard` via `api.getLeaderboard()`
- Render table with columns: Rank, Model Name, Pass Rate (%), Rubric Score, Duration (mean ms), Cost ($ or "N/A"), Trend (sparkline)
- Highest pass rate model gets a `"Best Model"` badge (amber star icon + "Best Model" text)
- Sort by pass rate descending; rank is position in sorted list

**Test**:
Given leaderboard with 3 model results, when LeaderboardPage renders, then table shows 3 rows with rank, model name, and pass rate. The highest-scoring model has a "Best Model" badge.
- **File**: `src/eval-ui/src/pages/LeaderboardPage.test.tsx`
- **TC-104**: Table renders model data — Given 3 entries, When LeaderboardPage renders, Then 3 rows with rank, model, pass rate columns
- **TC-105**: Best model badge on top scorer — Given models with pass rates 0.7, 0.9, 0.8, When rendered, Then model with 0.9 has "Best Model" badge
- **TC-106**: Sorted by pass rate desc — Given unsorted entries, When rendered, Then rank 1 has highest pass rate

**Dependencies**: T-023 (leaderboard API)

---

### T-050: Add sparkline trend chart to leaderboard
**User Story**: US-006 | **Satisfies ACs**: AC-US6-03
**Lane**: FE
**Status**: [x] Completed

**Implementation Details**:
- In `LeaderboardPage.tsx`, fetch the last 10 sweep results per model using the leaderboard history endpoint
- Render an inline SVG sparkline (follow the existing `TrendChart.tsx` pattern in eval-ui)
- Sparkline shows pass rate over last 10 data points; if < 10 points, show what's available
- Sparkline column header: "Trend (last 10)"

**Test**:
Given a model with 5 historical sweep results, when sparkline rendered, then SVG contains 5 data points. Given 15 results, then only the last 10 are shown.
- **File**: `src/eval-ui/src/pages/LeaderboardPage.test.tsx`
- **TC-107**: Sparkline renders correct data points — Given 5 results, When sparkline rendered, Then SVG has 5 path segments
- **TC-108**: Sparkline caps at 10 points — Given 15 results, When sparkline rendered, Then only 10 data points shown

**Dependencies**: T-049

---

### T-051: Add empty state to LeaderboardPage
**User Story**: US-006 | **Satisfies ACs**: AC-US6-04
**Lane**: FE
**Status**: [x] Completed

**Implementation Details**:
- In `LeaderboardPage.tsx`, when `entries.length === 0`, render an empty state card
- Empty state content: heading "No sweep results yet", subtext "Run your first model sweep to compare performance across models:", code block showing `vskill eval sweep --models "anthropic/claude-sonnet-4,openrouter/meta-llama/llama-3.1-70b" --judge "anthropic/claude-sonnet-4"`

**Test**:
Given no sweep results exist, when LeaderboardPage renders, then empty state with vskill eval sweep command shown. Given results exist, then the table is shown instead.
- **File**: `src/eval-ui/src/pages/LeaderboardPage.test.tsx`
- **TC-109**: Empty state shown when no entries — Given entries: [], When LeaderboardPage renders, Then empty state heading and code block visible
- **TC-110**: Empty state hidden when entries present — Given 1+ entries, When renders, Then table shown and empty state not rendered

**Dependencies**: T-049

---

### T-052: Add LeaderboardPage route to App.tsx router
**User Story**: US-006 | **Satisfies ACs**: AC-US6-01
**Lane**: FE
**Status**: [x] Completed

**Implementation Details**:
- In `src/eval-ui/src/App.tsx`, add route `/leaderboard` pointing to `<LeaderboardPage />`
- Add "Leaderboard" nav link in the sidebar/nav (after existing nav items)
- Pass `plugin` and `skill` context to LeaderboardPage so it can construct the API URL

**Test**:
Given the eval-ui app loaded, when user navigates to /leaderboard, then LeaderboardPage renders. Given sidebar/nav present, then a "Leaderboard" link is visible.
- **File**: `src/eval-ui/src/App.test.tsx`
- **TC-111**: /leaderboard route renders page — Given app loaded, When navigating to /leaderboard, Then LeaderboardPage component rendered
- **TC-112**: Nav link present — Given app renders, When sidebar inspected, Then "Leaderboard" link exists

**Dependencies**: T-049

---

### T-053: Build ModelSearchDropdown for OpenRouter model selection
**User Story**: US-004 | **Satisfies ACs**: AC-US4-05
**Lane**: FE
**Status**: [x] Completed

**Implementation Details**:
- Create `src/eval-ui/src/components/ModelSearchDropdown.tsx`
- When `provider === "openrouter"` is selected in the config UI, render a search input + dropdown
- Fetch model list from `GET /api/openrouter/models` on mount (debounced 300ms on search input)
- Show each model as `{name} ({id})` with pricing hint `$X/1M tokens`
- On selection, update parent config with selected model ID

**Test**:
Given provider "openrouter" selected and API returns 5 models, when ModelSearchDropdown renders, then dropdown shows 5 options. When user types in search, then list is filtered by model name.
- **File**: `src/eval-ui/src/components/ModelSearchDropdown.test.tsx`
- **TC-113**: Models populated from API — Given API returns 5 models, When dropdown renders, Then 5 options shown
- **TC-114**: Search filters list — Given 5 models, When user types "llama", Then only matching models shown
- **TC-115**: Selection updates parent — Given user selects "meta-llama/llama-3.1-70b", When onChange fires, Then parent receives the model id

**Dependencies**: T-018 (OpenRouter models API)

---

### T-054: Add SweepResult and LeaderboardEntry types to eval-ui types.ts
**User Story**: US-006 | **Satisfies ACs**: AC-US6-01
**Lane**: FE
**Status**: [x] Completed

**Implementation Details**:
- In `src/eval-ui/src/types.ts`, add:
  - `ModelResult`: matches the backend schema (provider, model, passRate `{mean,stddev}`, rubricScore, duration, cost, status, errorMessage)
  - `SweepResult`: sweepId, timestamp, judge, runs, models: `ModelResult[]`
  - `LeaderboardEntry`: abbreviated view for the table (rank, model, passRate.mean, duration.mean, cost.total, sparklineData)
  - `CredentialStatus`: `{ name: string, status: "ready" | "missing" | "untested", source?: string }`

**Test**:
Given SweepResult type imported, when TypeScript compiles LeaderboardPage.tsx, then no type errors. Given CredentialStatus imported, when used in TestsPanel, then no type errors.
- **File**: `src/eval-ui/src/types.test.ts` (type-only compile check)
- **TC-116**: SweepResult type compiles — Given LeaderboardPage using SweepResult, When tsc runs, Then no type errors
- **TC-117**: CredentialStatus type compiles — Given TestsPanel using CredentialStatus, When tsc runs, Then no type errors

**Dependencies**: None

---

### T-055: Add api.getLeaderboard, api.startSweep, api.getCredentials to API client
**User Story**: US-005, US-006, US-008 | **Satisfies ACs**: AC-US6-01, AC-US5-01, AC-US8-02
**Lane**: FE
**Status**: [x] Completed

**Implementation Details**:
- In `src/eval-ui/src/api.ts`, add:
  - `getLeaderboard(plugin, skill): Promise<{ entries: SweepResult[] }>`
  - `getLeaderboard(plugin, skill, timestamp): Promise<SweepResult>`
  - `startSweep(plugin, skill, body: SweepRequest): EventSource` (SSE)
  - `getCredentials(plugin, skill): Promise<{ credentials: CredentialStatus[] }>`
- Use the existing `fetchJSON` / `createSSE` patterns already in api.ts

**Test**:
Given a mock API server, when api.getLeaderboard() called, then returns { entries: [] }. When api.startSweep() called, then returns an EventSource pointed at /sweep endpoint.
- **File**: `src/eval-ui/src/api.test.ts`
- **TC-118**: getLeaderboard calls correct endpoint — Given mock fetch, When getLeaderboard(plugin, skill) called, Then fetch called with /api/skills/plugin/skill/leaderboard
- **TC-119**: getCredentials calls correct endpoint — Given mock fetch, When getCredentials(plugin, skill) called, Then fetch called with /api/credentials/plugin/skill

**Dependencies**: T-054

---

### T-056: E2E test — LeaderboardPage renders with mock data
**User Story**: US-006 | **Satisfies ACs**: AC-US6-01, AC-US6-02, AC-US6-04
**Lane**: FE
**Status**: [x] Completed

**Implementation Details**:
- Create Playwright E2E test `tests/e2e/leaderboard.spec.ts`
- Use a mock server fixture to serve 3 model sweep results
- Navigate to `/leaderboard`, assert table rows, "Best Model" badge, column headers

**Test**:
Given eval-ui running with mock leaderboard data (3 models), when Playwright navigates to /leaderboard, then the page shows 3 table rows, a "Best Model" badge on the top scorer, and all 7 column headers.
- **File**: `tests/e2e/leaderboard.spec.ts`
- **TC-120**: Leaderboard table renders via Playwright — Given mock data, When /leaderboard loaded, Then 3 rows visible
- **TC-121**: Best model badge visible — Given top scorer identified, When page loaded, Then "Best Model" badge present on that row
- **TC-122**: Empty state Playwright — Given no entries, When /leaderboard loaded, Then empty state text visible

**Dependencies**: T-049, T-051, T-052

---

### T-057: E2E test — TestsPanel filter tabs and badge rendering
**User Story**: US-007 | **Satisfies ACs**: AC-US7-01, AC-US7-02, AC-US7-04
**Lane**: FE
**Status**: [x] Completed

**Implementation Details**:
- Create Playwright E2E test `tests/e2e/tests-panel.spec.ts`
- Mock eval cases: 3 unit + 2 integration
- Assert: [U] badge on unit tests, [I] badge on integration, filter tabs switch list correctly

**Test**:
Given TestsPanel with 3 unit and 2 integration tests, when Playwright clicks "Integration" tab, then only 2 rows visible. When "All" tab clicked, then 5 rows visible.
- **File**: `tests/e2e/tests-panel.spec.ts`
- **TC-123**: Filter tabs work via Playwright — Given 3 unit + 2 integration, When "Integration" clicked, Then 2 rows visible
- **TC-124**: Badges visible via Playwright — Given unit case rendered, When badge inspected, Then [U] text present with blue color

**Dependencies**: T-045, T-047

---

## Coverage Summary

| AC-ID | Task | Lane |
|-------|------|------|
| AC-US1-01 | T-001, T-010, T-014 | PERF |
| AC-US1-02 | T-002, T-015, T-028 | PERF, MULTI |
| AC-US1-03 | T-001, T-011 | PERF |
| AC-US1-04 | T-003 | PERF |
| AC-US1-05 | T-004 | PERF |
| AC-US2-01 | T-005 | PERF |
| AC-US2-02 | T-006, T-015 | PERF |
| AC-US2-03 | T-005 | PERF |
| AC-US2-04 | T-006 | PERF |
| AC-US3-01 | T-007, T-013 | PERF |
| AC-US3-02 | T-007, T-008, T-013 | PERF |
| AC-US3-03 | T-008, T-015 | PERF |
| AC-US3-04 | T-007, T-009 | PERF |
| AC-US4-01 | T-016, T-029 | MULTI |
| AC-US4-02 | T-016, T-029 | MULTI |
| AC-US4-03 | T-017, T-029 | MULTI |
| AC-US4-04 | T-016, T-027 | MULTI |
| AC-US4-05 | T-018, T-053 | MULTI, FE |
| AC-US5-01 | T-019, T-020, T-024, T-026 | MULTI |
| AC-US5-02 | T-024, T-025 | MULTI |
| AC-US5-03 | T-021, T-026 | MULTI |
| AC-US5-04 | T-019, T-026 | MULTI |
| AC-US5-05 | T-019, T-022 | MULTI |
| AC-US6-01 | T-023, T-049, T-052, T-055 | MULTI, FE |
| AC-US6-02 | T-049, T-056 | FE |
| AC-US6-03 | T-050 | FE |
| AC-US6-04 | T-051, T-056 | FE |
| AC-US7-01 | T-045, T-057 | FE |
| AC-US7-02 | T-045, T-057 | FE |
| AC-US7-03 | T-046 | FE |
| AC-US7-04 | T-047, T-057 | FE |
| AC-US7-05 | T-048 | FE |
| AC-US8-01 | T-031 | INTG |
| AC-US8-02 | T-032, T-042 | INTG |
| AC-US8-03 | T-030, T-032, T-043 | INTG |
| AC-US8-04 | T-031 | INTG |
| AC-US9-01 | T-033, T-036, T-044 | INTG |
| AC-US9-02 | T-036, T-041 | INTG |
| AC-US9-03 | T-036 | INTG |
| AC-US9-04 | T-037 | INTG |
| AC-US9-05 | T-036, T-038 | INTG |
| AC-US10-01 | T-035 | INTG |
| AC-US10-02 | T-039 | INTG |
| AC-US10-03 | T-040 | INTG |
| AC-US10-04 | T-038 | INTG |
