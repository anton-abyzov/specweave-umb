---
increment: 0550-skill-gen-perf-intg-testgen
title: "Skill Generation Performance & Integration Test Auto-Generation"
status: active
---

# Tasks: 0550-skill-gen-perf-intg-testgen

## Agent Lanes

| Lane | Agent | User Stories | Tasks |
|------|-------|-------------|-------|
| gen-perf | Agent A | US-001, US-002 | T-001 – T-010 |
| test-gen | Agent B | US-003, US-004 | T-011 – T-020 |
| batch | Agent C | US-005 | T-021 – T-028 |

---

## Lane: gen-perf (Agent A) — Parallel Skill Generation + Concurrent Batch Generate-All

### T-001: Extract Semaphore to shared eval/concurrency.ts
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01
**Lane**: gen-perf
**Status**: [x] Completed
**Test**: Given `eval-server/concurrency.ts` and `commands/eval/generate-all.ts` both need `Semaphore` → When `Semaphore` is moved to `eval/concurrency.ts` and re-exported from `eval-server/concurrency.ts` → Then `eval-server/` and `commands/eval/` can both import it without cross-layer violations and all existing tests pass

---

### T-002: Add `warning` field to GenerateSkillResult interface
**User Story**: US-001 | **Satisfies ACs**: AC-US1-03
**Lane**: gen-perf
**Status**: [x] Completed
**Test**: Given the `GenerateSkillResult` type definition in `skill-create-routes.ts` → When a `warning?: string` optional field is added → Then TypeScript compiles cleanly and existing callers of the interface receive no type errors

---

### T-003: Split GENERATE_SYSTEM_PROMPT into BODY_SYSTEM_PROMPT and EVAL_SYSTEM_PROMPT
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02
**Lane**: gen-perf
**Status**: [x] Completed
**Test**: Given the monolithic `GENERATE_SYSTEM_PROMPT` constant in `skill-create-routes.ts` → When it is split into `BODY_SYSTEM_PROMPT` (body + metadata only) and `EVAL_SYSTEM_PROMPT` (evals only, given skill description) → Then each prompt when sent to an LLM independently produces only its designated section of output (verified by unit tests with mocked LLM responses)

---

### T-004: Implement parseBodyResponse() and parseEvalsResponse()
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02
**Lane**: gen-perf
**Status**: [x] Completed
**Test**: Given raw JSON strings from the body LLM call and the evals LLM call respectively → When `parseBodyResponse(raw)` and `parseEvalsResponse(raw)` are called → Then each returns its typed result without cross-contamination and invalid JSON throws a descriptive parse error

---

### T-005: Implement mergeGenerateResults() with partial-failure handling
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03
**Lane**: gen-perf
**Status**: [x] Completed
**Test**: Given a fulfilled body result and a rejected evals result from `Promise.allSettled` → When `mergeGenerateResults(bodySettled, evalsSettled)` is called → Then the return value contains the body fields, `evals: []`, and `warning: "eval generation failed: <reason>"`; and when both are fulfilled the merged result contains body + evals with no warning field

---

### T-006: Refactor POST /api/skills/generate to parallel Promise.allSettled
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03
**Lane**: gen-perf
**Status**: [x] Completed
**Test**: Given a POST to `/api/skills/generate` with a valid skill prompt → When the handler runs → Then `Promise.allSettled([bodyCall, evalCall])` is invoked with bodyCall using the capable model (Sonnet) and evalCall using the fast model (Haiku/configurable via `VSKILL_EVAL_GEN_MODEL`) and both run concurrently (start timestamps within 100ms of each other in tests)

---

### T-007: Update SSE events for parallel generation phases
**User Story**: US-001 | **Satisfies ACs**: AC-US1-04
**Lane**: gen-perf
**Status**: [x] Completed
**Test**: Given SSE mode is active on `/api/skills/generate` → When parallel generation runs → Then SSE stream emits `"generating-body"` and `"generating-evals"` progress events before the final `"done"` event, and the done event payload contains the merged result

---

### T-008: Add --concurrency flag and refactor generate-all to Semaphore-gated Promise.allSettled
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-04
**Lane**: gen-perf
**Status**: [x] Completed
**Test**: Given `generate-all` is invoked with `--concurrency 3` and an API provider → When `runEvalGenerateAll()` processes 5 skills → Then a `Semaphore(3)` gates the concurrent execution, no 2-second delays exist between skill starts, and all 5 skills complete via `Promise.allSettled` (verified with fake timers asserting no artificial delays)

---

### T-009: Auto-provider selection for batch operations
**User Story**: US-002 | **Satisfies ACs**: AC-US2-03
**Lane**: gen-perf
**Status**: [x] Completed
**Test**: Given `ANTHROPIC_API_KEY=sk-test` is set in env and `VSKILL_EVAL_PROVIDER` is unset → When `generate-all` starts → Then provider auto-selects `"anthropic"`, logs `"Auto-selected anthropic provider for batch operation"`, and default concurrency is 3; when provider is CLI-based (or `VSKILL_EVAL_PROVIDER=claude-cli`), concurrency defaults to 1

---

### T-010: Unit tests for gen-perf pillar
**User Story**: US-001, US-002 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04
**Lane**: gen-perf
**Status**: [x] Completed
**Test**: Given the full gen-perf implementation in `skill-create-routes.ts` and `generate-all.ts` → When `npx vitest run src/eval-server/__tests__/skill-create-routes.test.ts src/commands/eval/__tests__/generate-all.test.ts` → Then all tests pass with 95%+ branch coverage for the parallel generation and concurrency paths

---

## Lane: test-gen (Agent B) — Integration Test Auto-Generation + Schema Validation

### T-011: Add detectBrowserRequirements() to prompt-builder.ts
**User Story**: US-003 | **Satisfies ACs**: AC-US3-02
**Lane**: test-gen
**Status**: [x] Completed
**Test**: Given SKILL.md content containing `Bash` in allowed-tools and the word "browser" or "Chrome" in the body → When `detectBrowserRequirements(skillContent)` is called → Then it returns `{ hasBrowser: true, suggestedProfile: "Default" }`; given content with no browser references → Then it returns `{ hasBrowser: false }`

---

### T-012: Add detectPlatformTargets() to prompt-builder.ts
**User Story**: US-003 | **Satisfies ACs**: AC-US3-03
**Lane**: test-gen
**Status**: [x] Completed
**Test**: Given SKILL.md content mentioning "Twitter", "LinkedIn", and "Slack" → When `detectPlatformTargets(skillContent)` is called → Then it returns `["Twitter", "LinkedIn", "Slack"]` (case-insensitive, deduped); given content with no platform keywords → Then it returns `[]`

---

### T-013: Add CREDENTIAL_HINTS map and extend integration types
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01
**Lane**: test-gen
**Status**: [x] Completed
**Test**: Given the `CREDENTIAL_HINTS` map keyed by MCP server name (e.g. `"slack" -> "SLACK_BOT_TOKEN"`) → When `buildIntegrationEvalPrompt()` receives detected MCP deps including `"slack"` → Then the generated prompt instructs the LLM to populate `requiredCredentials` with `["SLACK_BOT_TOKEN"]`

---

### T-014: Add EvalCleanupSchema and EvalRequirementsSchema types to integration-types.ts
**User Story**: US-003, US-004 | **Satisfies ACs**: AC-US3-03, AC-US4-02
**Lane**: test-gen
**Status**: [x] Completed
**Test**: Given `integration-types.ts` is extended with `EvalCleanupSchema` (action enum: `"delete_post" | "remove_artifact" | "custom"`, platform, identifier) and `EvalRequirementsSchema` (chromeProfile, platform) → When TypeScript compiles and an `EvalCase` has a `cleanup` block with `action: "delete_post"` → Then no type errors are raised; when `action: "invalid"` is used → Then TypeScript emits a type error

---

### T-015: Extend EvalCase schema in schema.ts with cleanup and requirements fields
**User Story**: US-003, US-004 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US4-01
**Lane**: test-gen
**Status**: [x] Completed
**Test**: Given an `evals.json` parsed by `loadAndValidateEvals()` with a case containing `testType: "integration"`, `cleanup: [{action: "delete_post", platform: "Twitter", identifier: "{POSTED_ID}"}]`, and `requiredCredentials: ["TWITTER_BEARER_TOKEN"]` → When validation runs → Then the case passes without errors

---

### T-016: Implement buildIntegrationEvalPrompt()
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03
**Lane**: test-gen
**Status**: [x] Completed
**Test**: Given SKILL.md content for a social-media-posting skill with Slack MCP dep, browser references, and platform "Twitter" detected → When `buildIntegrationEvalPrompt(skillContent, mcpDeps, browserReqs, platforms)` is called → Then the returned prompt string contains instructions to produce `testType: "integration"`, `requiredCredentials`, `requirements.chromeProfile`, and `cleanup` blocks with `delete_post` action for Twitter

---

### T-017: Implement parseGeneratedIntegrationEvals()
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03
**Lane**: test-gen
**Status**: [x] Completed
**Test**: Given raw LLM output containing a JSON array of integration eval cases with all required fields → When `parseGeneratedIntegrationEvals(raw)` is called → Then it returns a typed array of `EvalCase[]` with `testType: "integration"` set; given malformed JSON → Then it throws a descriptive ParseError

---

### T-018: Add --type flag to eval init and implement parallel dispatch for --type all
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-04, AC-US3-05
**Lane**: test-gen
**Status**: [x] Completed
**Test**: Given `vskill eval init --type all` on a skill with MCP dependencies → When `runEvalInit()` executes → Then `Promise.allSettled([unitGenCall(Haiku), integrationGenCall(Sonnet)])` runs in parallel and results are merged into a single `evals.json` containing both unit and integration cases; given `--type integration` on a skill with no MCP/browser deps → Then logs "No integration targets detected, generating unit tests only" and exits without writing

---

### T-019: Extend loadAndValidateEvals() with integration-specific validation rules
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02, AC-US4-03
**Lane**: test-gen
**Status**: [x] Completed
**Test**: Given an `evals.json` with three integration cases: one missing `requiredCredentials`, one with `cleanup.action: "invalid_action"`, and one with an assertion text longer than 100 chars with no outcome verb → When `loadAndValidateEvals()` runs → Then: (1) missing-credentials emits a warning (not error), (2) invalid action returns a `ValidationError` with path and allowed values `["delete_post","remove_artifact","custom"]`, (3) prose assertion emits a warning suggesting API/existence assertions

---

### T-020: Unit tests for test-gen pillar
**User Story**: US-003, US-004 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04, AC-US3-05, AC-US4-01, AC-US4-02, AC-US4-03
**Lane**: test-gen
**Status**: [x] Completed
**Test**: Given the full test-gen pillar implementation → When `npx vitest run src/eval/__tests__/prompt-builder.test.ts src/eval/__tests__/schema.test.ts` → Then all tests pass with 95%+ branch coverage for detection functions, prompt building, parsing, and schema validation paths

---

## Lane: batch (Agent C) — Anthropic Batch API for Eval Judge Calls

### T-021: Create eval/batch-judge.ts with batchJudgeAssertions() scaffold
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01
**Lane**: batch
**Status**: [x] completed
**Test**: Given a `BatchJudgeRequest[]` of 6 judge prompts and an Anthropic client mock → When `batchJudgeAssertions(requests, client)` is called → Then `client.messages.batches.create` is called exactly once with all 6 requests using `custom_id` format `"{evalId}_{assertionId}"` and each request has `max_tokens: 256`

---

### T-022: Implement polling loop with escalating intervals and 10-minute timeout
**User Story**: US-005 | **Satisfies ACs**: AC-US5-02
**Lane**: batch
**Status**: [x] completed
**Test**: Given a batch that reports `processing` status for 70 seconds then completes → When the polling loop runs (using fake timers) → Then polls fire at 5s intervals for the first 60s (12 polls), then at 15s intervals after 60s (at least 1 poll before completion), never at 30s intervals in this scenario; and given a batch that stays `processing` for 600s → Then the loop cancels the batch via `client.messages.batches.cancel` and throws a timeout error

---

### T-023: Implement custom_id result mapping back to AssertionResult[]
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01
**Lane**: batch
**Status**: [x] completed
**Test**: Given a completed batch response with results keyed by `custom_id: "eval1_assert0"` and `custom_id: "eval1_assert1"` → When results are mapped back → Then the returned `AssertionResult[]` contains entries at the correct indices with pass/fail derived from the LLM response content matching judge scoring logic

---

### T-024: Implement sequential fallback on batch failure
**User Story**: US-005 | **Satisfies ACs**: AC-US5-03
**Lane**: batch
**Status**: [x] completed
**Test**: Given `client.messages.batches.create` throws a network error on first call → When `batchJudgeAssertions()` executes → Then it catches the error, logs a warning containing the error message, and falls back to calling `judgeAssertion()` sequentially for each request, returning the same `AssertionResult[]` shape as the batch path

---

### T-025: Add --batch flag to eval run command
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01, AC-US5-04
**Lane**: batch
**Status**: [x] completed
**Test**: Given `vskill eval run --batch` is invoked with `VSKILL_EVAL_PROVIDER=anthropic` → When the command parses flags → Then `runEvalRun()` receives `batch: true` and routes to `batchJudgeAssertions()`; given `--batch` with provider `claude-cli` → Then a warning is printed "Batch mode only supported with anthropic provider, running sequentially" and sequential judge path is used

---

### T-026: Implement two-round execution in runEvalRun() for batch mode
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01
**Lane**: batch
**Status**: [x] completed
**Test**: Given `--batch` mode with 3 eval cases each containing 2 assertions → When `runEvalRun()` executes → Then Round 1 completes all generation calls for all 3 cases before Round 2 collects all 6 judge prompts and submits them as a single `batchJudgeAssertions()` call (verified by checking that `batchJudgeAssertions` is called once with 6 requests, not 6 times with 1 each)

---

### T-027: Add batch cost calculation with 50% discount to GenerateResult
**User Story**: US-005 | **Satisfies ACs**: AC-US5-05
**Lane**: batch
**Status**: [x] completed
**Test**: Given a batch eval run completes with token usage reported by the Anthropic batch response → When cost is calculated → Then `GenerateResult.cost` reflects the 50% batch discount (sequential_cost * 0.5) and the summary prints `"Batch cost: $X.XX (50% discount vs $Y.YY sequential)"`

---

### T-028: Unit tests for batch pillar
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01, AC-US5-02, AC-US5-03, AC-US5-04, AC-US5-05
**Lane**: batch
**Status**: [x] completed
**Test**: Given the full batch pillar implementation in `eval/batch-judge.ts` and `commands/eval/run.ts` → When `npx vitest run src/eval/__tests__/batch-judge.test.ts src/commands/eval/__tests__/run.test.ts` → Then all tests pass with 95%+ branch coverage for batch submission, polling intervals, timeout cancellation, fallback path, and cost calculation

---

## AC Coverage Matrix

| AC-ID | Task(s) | Lane |
|-------|---------|------|
| AC-US1-01 | T-003, T-004, T-006, T-010 | gen-perf |
| AC-US1-02 | T-003, T-004, T-005, T-006, T-010 | gen-perf |
| AC-US1-03 | T-002, T-005, T-006, T-010 | gen-perf |
| AC-US1-04 | T-007, T-010 | gen-perf |
| AC-US2-01 | T-001, T-008, T-010 | gen-perf |
| AC-US2-02 | T-008, T-009, T-010 | gen-perf |
| AC-US2-03 | T-009, T-010 | gen-perf |
| AC-US2-04 | T-008, T-010 | gen-perf |
| AC-US3-01 | T-013, T-015, T-016, T-018, T-020 | test-gen |
| AC-US3-02 | T-011, T-016, T-018, T-020 | test-gen |
| AC-US3-03 | T-012, T-014, T-016, T-017, T-020 | test-gen |
| AC-US3-04 | T-018, T-020 | test-gen |
| AC-US3-05 | T-018, T-020 | test-gen |
| AC-US4-01 | T-015, T-019, T-020 | test-gen |
| AC-US4-02 | T-014, T-019, T-020 | test-gen |
| AC-US4-03 | T-019, T-020 | test-gen |
| AC-US5-01 | T-021, T-023, T-025, T-026, T-028 | batch |
| AC-US5-02 | T-022, T-028 | batch |
| AC-US5-03 | T-024, T-028 | batch |
| AC-US5-04 | T-025, T-028 | batch |
| AC-US5-05 | T-027, T-028 | batch |
