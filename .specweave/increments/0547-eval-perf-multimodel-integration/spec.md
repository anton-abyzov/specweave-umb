---
increment: 0547-eval-perf-multimodel-integration
title: 'vSkill Studio: Eval Performance, Multi-Model & Integration Tests'
status: completed
priority: P1
type: feature
created: 2026-03-16T00:00:00.000Z
---

# vSkill Studio: Eval Performance, Multi-Model & Integration Tests

## Brainstorm
**Source**: [reports/brainstorm.md](reports/brainstorm.md) — Deep brainstorm with 4 parallel agents covering performance, multi-model, integration tests, and per-model leaderboard design.

## Problem Statement

vSkill Studio runs all 25-35 LLM calls per eval sequentially, resulting in 5-12 minute runs. There is no way to compare skill quality across models (only 2-model compare exists), and while the schema supports `testType: "integration"` and `requiredCredentials`, no integration test runner exists. Skill authors cannot prove their skills work against real APIs/browsers, cannot benchmark across the model ecosystem, and waste significant time waiting for sequential eval runs.

## Goals

- Reduce eval run duration by 4-6x through parallel execution and tiered judge models
- Enable multi-model evaluation via OpenRouter provider and `vskill eval sweep` command
- Build a browser-based integration test runner that proves skills work against real services
- Provide leaderboard UI for comparing model quality, cost, and latency
- Differentiate unit vs. integration tests visually in Studio and on the platform

## User Stories

### US-001: Parallel Eval Execution
**Project**: vskill
**As a** skill author
**I want** eval cases to run concurrently with a configurable concurrency limit
**So that** my eval suite completes in minutes instead of 10+ minutes

**Acceptance Criteria**:
- [x] **AC-US1-01**: Given an eval suite with 10 cases, when I run `vskill eval run`, then cases execute concurrently up to the semaphore limit (default 5) using the existing `Semaphore` class from `concurrency.ts`
- [x] **AC-US1-02**: Given the `--concurrency N` CLI flag is passed, when the eval runs, then at most N LLM calls execute simultaneously
- [x] **AC-US1-03**: Given a case fails during parallel execution, when other cases are still running, then `Promise.allSettled` captures the failure without aborting remaining cases
- [x] **AC-US1-04**: Given assertions within a single case, when the case output is ready, then all assertion judges for that case run via `Promise.all` concurrently
- [x] **AC-US1-05**: Given the comparator mode, when generating outputs, then skill and baseline generation run concurrently via `Promise.all([generateSkill(), generateBaseline()])`

---

### US-002: Tiered Judge Model
**Project**: vskill
**As a** skill author
**I want** to use a fast/cheap model for assertion judging while keeping an expensive model for generation
**So that** I reduce eval cost and duration without sacrificing generation quality

**Acceptance Criteria**:
- [x] **AC-US2-01**: Given `judgeModel` is configured in the eval config, when assertions are judged, then the judge uses the specified model instead of the generation model
- [x] **AC-US2-02**: Given the `--judge-model <provider/model>` CLI flag, when running evals, then assertion judging uses that model
- [x] **AC-US2-03**: Given `judgeModel` is not set, when running evals, then the generation model is used for judging (backward compatible)
- [x] **AC-US2-04**: Given a judge model is weaker than the generation model (e.g., Haiku judging Opus output), when the eval starts, then a warning is emitted to stderr

---

### US-003: Judge Result Caching
**Project**: vskill
**As a** skill author
**I want** judge results cached by content hash
**So that** re-running evals with identical outputs skips redundant judge calls

**Acceptance Criteria**:
- [x] **AC-US3-01**: Given a judge call completes, when the result is returned, then it is cached keyed by SHA-256 hash of `(assertion_text, skill_output)`
- [x] **AC-US3-02**: Given a subsequent judge call with the same assertion text and skill output, when the cache is checked, then the cached result is returned without an LLM call
- [x] **AC-US3-03**: Given the `--no-cache` CLI flag, when running evals, then the judge cache is bypassed entirely
- [x] **AC-US3-04**: Given the cache file, when inspected, then it is stored at `<skillDir>/evals/.judge-cache.json` and is gitignored

---

### US-004: OpenRouter Provider
**Project**: vskill
**As a** skill author
**I want** OpenRouter as a 6th LLM provider
**So that** I can evaluate my skills against 100+ models with a single API key

**Acceptance Criteria**:
- [x] **AC-US4-01**: Given `VSKILL_EVAL_PROVIDER=openrouter` and `OPENROUTER_API_KEY` is set, when `createLlmClient()` is called, then it returns a client that sends requests to `https://openrouter.ai/api/v1/chat/completions`
- [x] **AC-US4-02**: Given an OpenRouter model ID like `meta-llama/llama-3.1-70b-instruct`, when passed as `VSKILL_EVAL_MODEL`, then the request uses that model ID in the `model` field
- [x] **AC-US4-03**: Given a successful OpenRouter response, when `usage.total_cost` is present, then the cost is included in `GenerateResult` via a new `cost` field
- [x] **AC-US4-04**: Given `OPENROUTER_API_KEY` is not set and provider is `openrouter`, when `createLlmClient()` is called, then it throws a descriptive error with setup instructions
- [x] **AC-US4-05**: Given the Studio config UI, when provider `openrouter` is selected, then a model search dropdown queries `GET /api/v1/models` and shows available models

---

### US-005: Multi-Model Sweep Command
**Project**: vskill
**As a** skill author
**I want** `vskill eval sweep` to run the same evals across N models
**So that** I can compare quality, cost, and latency across the model ecosystem

**Acceptance Criteria**:
- [x] **AC-US5-01**: Given the command `vskill eval sweep --models "anthropic/claude-sonnet-4,openrouter/meta-llama/llama-3.1-70b" --judge anthropic/claude-sonnet-4`, when executed, then each model runs the full eval suite with the specified judge
- [x] **AC-US5-02**: Given the `--runs N` flag, when sweeping, then each model runs N iterations and results include mean and standard deviation for pass rate and rubric score
- [x] **AC-US5-03**: Given a sweep completes, when results are stored, then they are written to `<skillDir>/evals/leaderboard/<ISO-timestamp>.json`
- [x] **AC-US5-04**: Given a model fails during sweep (API error, timeout), when other models remain, then the sweep continues and the failed model shows status `error` with the error message
- [x] **AC-US5-05**: Given sweep progress, when running, then SSE events report per-model progress with model name, current case, and completion percentage

---

### US-006: Studio Leaderboard UI
**Project**: vskill
**As a** skill author
**I want** a leaderboard view in Studio showing sweep results
**So that** I can visually compare model performance at a glance

**Acceptance Criteria**:
- [x] **AC-US6-01**: Given sweep results exist in `evals/leaderboard/`, when the leaderboard page loads, then a table displays columns: rank, model name, pass rate, rubric score (mean), duration (mean), cost, and sparkline trend
- [x] **AC-US6-02**: Given the leaderboard table, when the highest-scoring model is determined, then it displays a "Best Model" badge
- [x] **AC-US6-03**: Given multiple sweep runs exist, when viewing the leaderboard, then the sparkline shows the last 10 data points per model
- [x] **AC-US6-04**: Given no sweep results exist, when the leaderboard page loads, then an empty state shows instructions for running `vskill eval sweep`

---

### US-007: Unit vs. Integration Test UI Differentiation
**Project**: vskill
**As a** skill author
**I want** unit and integration tests visually distinguished in Studio
**So that** I can immediately see which tests need credentials and which run standalone

**Acceptance Criteria**:
- [x] **AC-US7-01**: Given an eval case with `testType: "unit"`, when displayed in TestsPanel, then it shows a blue `[U]` badge
- [x] **AC-US7-02**: Given an eval case with `testType: "integration"`, when displayed in TestsPanel, then it shows an amber `[I]` badge
- [x] **AC-US7-03**: Given an integration test with `requiredCredentials` that are not configured, when displayed, then a lock icon appears with tooltip "Configure credentials to run"
- [x] **AC-US7-04**: Given the TestsPanel, when filter tabs are present, then "All", "Unit", and "Integration" tabs filter the test list by `testType`
- [x] **AC-US7-05**: Given the vskill platform (verified-skill.com), when viewing a skill's eval results, then integration tests show "Run locally in vSkill Studio" instead of run results

---

### US-008: Credential Management CLI
**Project**: vskill
**As a** skill author
**I want** CLI commands to manage credentials for integration tests
**So that** I can set up, verify, and list secrets without editing files manually

**Acceptance Criteria**:
- [x] **AC-US8-01**: Given the command `vskill credentials set X_API_KEY`, when executed, then it prompts for the value and stores it in `.env.local` (gitignored)
- [x] **AC-US8-02**: Given the command `vskill credentials list`, when executed, then it shows all credentials referenced by integration tests with status `Ready`, `Missing`, or `Untested`
- [x] **AC-US8-03**: Given the command `vskill credentials check`, when executed, then it resolves each credential through the chain (env var -> `.env.local` -> OS keychain) and reports the source
- [x] **AC-US8-04**: Given `.env.local` does not exist, when `vskill credentials set` runs, then it creates the file and adds it to `.gitignore` if not already present

---

### US-009: Integration Test Runner
**Project**: vskill
**As a** skill author
**I want** an integration test runner that executes skills against real services via browser automation
**So that** I can prove my skills work in the real world, not just in simulation

**Acceptance Criteria**:
- [x] **AC-US9-01**: Given an eval case with `testType: "integration"` and `requirements.chromeProfile: "Profile 3"`, when the integration runner starts, then it launches Playwright with `--user-data-dir` pointing to the resolved Chrome profile directory
- [x] **AC-US9-02**: Given the runner phases, when executing, then they proceed in order: Preflight (validate credentials/profile) -> Connect (launch browser/MCP) -> Execute (LLM with real tools) -> Verify (check outcomes) -> Cleanup (delete test artifacts)
- [x] **AC-US9-03**: Given a `cleanup` action defined in the eval case, when the test completes (pass or fail), then the cleanup action executes to remove test artifacts (e.g., delete posted tweet)
- [x] **AC-US9-04**: Given Ctrl+C during an integration test, when the signal is received, then cleanup runs before the process exits
- [x] **AC-US9-05**: Given the `--dry-run` flag, when running integration tests, then all phases execute except the actual API calls, logging what would have happened

---

### US-010: Integration Test Rate Limiting and Safety
**Project**: vskill
**As a** skill author
**I want** per-platform rate limiting and safety guardrails for integration tests
**So that** I do not get rate-limited or accidentally pollute production accounts

**Acceptance Criteria**:
- [x] **AC-US10-01**: Given platform rate limit config (e.g., X: 3 requests/min, LinkedIn: 2 requests/min), when integration tests run, then the runner throttles requests to stay within limits
- [x] **AC-US10-02**: Given all integration test content, when posted to platforms, then it includes the `[VSKILL-TEST-{RUN_ID}]` prefix for identification and cleanup
- [x] **AC-US10-03**: Given the `--confirm` flag is not set, when running integration tests for the first time against a platform, when a confirmation prompt appears, then it lists the actions that will be performed
- [x] **AC-US10-04**: Given Playwright is not installed, when `vskill eval run --integration` is invoked, then a clear error explains that Playwright is an optional peer dependency with install instructions

## Out of Scope

- Batch API support (Anthropic batch endpoint) -- deferred to future increment
- Judge calibration layer for weak-model score adjustment -- deferred to future increment
- Leaderboard on verified-skill.com platform -- local Studio only for now
- Auto-fallback when OpenRouter is down -- show clear error only
- CI/CD integration for integration tests -- local execution only for now
- Confidence threshold re-judging (borderline 40-60% scores re-judged with stronger model)

## Non-Functional Requirements

- **Performance**: Eval suite with 10 cases and 30 assertions completes in < 3 minutes with `--concurrency 5` using an API provider (down from 12+ minutes sequential)
- **Security**: Credentials never appear in evals.json, benchmark results, or SSE events. `.env.local` is always gitignored. Secret-scanning pre-flight rejects eval definitions containing token patterns
- **Compatibility**: OpenRouter adapter works with any model available on their platform. Chrome profile resolution supports macOS (Linux/Windows paths deferred)
- **Reliability**: Partial failures in parallel execution do not abort the entire run. Integration test cleanup runs even on crash/interrupt

## Edge Cases

- API 429 rate limit during parallel execution: Retry with exponential backoff (max 3 retries, 1s/2s/4s delays), then mark case as `error`
- SSE progress interleaving: Events from parallel cases include `caseId` field so the UI can route them to the correct case panel
- OpenRouter returns no `usage.total_cost`: Set `cost` to `null`, do not fail the request
- Chrome profile directory does not exist: Preflight phase fails with clear error listing available profiles
- Sweep model string parsing: Accept formats `provider/model` (e.g., `anthropic/claude-sonnet-4`) and `provider/org/model` (e.g., `openrouter/meta-llama/llama-3.1-70b`)
- Judge cache corruption: If `.judge-cache.json` fails to parse, delete and rebuild (log warning)
- Playwright not installed: `require.resolve('playwright')` check in preflight, not at import time
- Cleanup failure during integration test: Log the failure, report it in results, but do not throw -- the test result stands independently of cleanup success

## Risks

| Risk | Probability | Impact | Severity | Mitigation |
|------|-------------|--------|----------|------------|
| API rate limits under parallel load | 0.6 | 5 | 3.0 | Semaphore caps concurrency; exponential backoff on 429 |
| OpenRouter latency variance across models | 0.5 | 3 | 1.5 | Per-model timeout config; show latency in sweep results |
| Integration test cleanup failure leaves orphaned posts | 0.3 | 7 | 2.1 | `[VSKILL-TEST-]` prefix enables manual identification; cleanup retries |
| Chrome profile path changes across OS versions | 0.4 | 4 | 1.6 | Centralized path resolver; user-configurable override |
| Weak judge model produces unreliable scores | 0.5 | 6 | 3.0 | Warning when judge weaker than generator; calibration deferred |
| SSE event ordering breaks under parallelism | 0.3 | 5 | 1.5 | Case-scoped event IDs; UI sorts by caseId then sequence |

## Technical Notes

### Dependencies
- OpenRouter API (`https://openrouter.ai/api/v1`) -- OpenAI-compatible chat completions endpoint
- Playwright (optional peer dependency) -- required only for integration tests
- Chrome user profiles -- macOS path: `~/Library/Application Support/Google/Chrome/{Profile Name}`

### Constraints
- CLI providers (claude-cli, codex-cli, gemini-cli) spawn child processes and may not support true parallelism -- concurrency applies primarily to API providers (anthropic, openrouter, ollama)
- SSE progress events must remain ordered per-case even under parallel execution -- use case-scoped event IDs
- `GenerateResult` interface needs a new optional `cost: number | null` field for OpenRouter cost tracking
- `ProviderName` union type extends from 5 to 6 members

### Architecture Decisions
- Reuse existing `Semaphore` from `concurrency.ts` rather than introducing a new concurrency primitive
- OpenRouter adapter follows the same pattern as the Anthropic client (direct HTTP, not CLI spawn)
- Judge cache stored per-skill to avoid cross-skill hash collisions
- Sweep results stored as timestamped JSON files for append-only history
- Integration test runner is a separate module (`src/eval/integration-runner.ts`), not embedded in the existing benchmark runner

## Success Metrics

- Eval duration: 4-6x speedup measured on a 10-case suite (from ~12 min to ~2-3 min)
- Multi-model adoption: Sweep command successfully runs across 3+ providers in a single invocation
- OpenRouter integration: Model search returns results and eval runs complete end-to-end
- Integration test completion: At least one browser-based integration test runs through all 5 phases (preflight through cleanup)
- Judge cost reduction: Using Haiku as judge model reduces per-eval cost by 50%+ compared to using the generation model
