---
increment: 0550-skill-gen-perf-intg-testgen
title: Skill Generation Performance & Integration Test Auto-Generation
type: feature
priority: P1
status: completed
created: 2026-03-16T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Skill Generation Performance & Integration Test Auto-Generation

## Problem Statement

Skill generation in vskill suffers from three bottlenecks. First, the single monolithic LLM call in `skill-create-routes.ts` generates both SKILL.md body and evals sequentially (12-30s CLI, 4-12s API) when they could run in parallel. Second, `generate-all.ts` loops skills sequentially with hardcoded 2-second delays, making batch generation painfully slow for repos with 10+ skills. Third, eval runs spend 60-70% of their LLM budget on judge calls that are independent and non-interactive -- perfect candidates for Anthropic's Message Batches API (50% cost savings) -- yet zero batch API usage exists in the codebase. Additionally, integration test cases must be hand-written despite the integration test runner (from increment 0547) already existing; `buildEvalInitPrompt()` only generates unit tests.

## Goals

- Reduce single skill generation wall-time by 30-40% via parallel LLM calls
- Achieve 3-5x batch generation speedup for repos with 10+ skills
- Auto-generate integration test cases from SKILL.md with MCP and browser detection
- Cut eval judge costs by 50% via Anthropic Message Batches API
- Auto-prefer API provider for batch operations when ANTHROPIC_API_KEY is set

## User Stories

### US-001: Parallel Skill Generation (P1)
**Project**: vskill
**As a** skill author using Skill Studio
**I want** SKILL.md body and evals to be generated in parallel
**So that** single skill generation completes 30-40% faster

**Acceptance Criteria**:
- [x] **AC-US1-01**: Given a POST to `/api/skills/generate`, when the LLM is invoked, then two parallel calls execute simultaneously -- Call A generates SKILL.md body, Call B generates evals -- and results are merged into the same response shape as today
- [x] **AC-US1-02**: Given Call B (evals) uses a faster/cheaper model (configurable, default Haiku), when both calls complete, then the merged result contains body from Call A and evals from Call B
- [x] **AC-US1-03**: Given Call A succeeds but Call B fails, when the response is built, then the body is returned with an empty evals array and a warning field indicating eval generation failed
- [x] **AC-US1-04**: Given SSE mode is active, when parallel generation runs, then progress events report both phases ("generating-body", "generating-evals") and the final SSE done event contains the merged result

---

### US-002: Batch Generate-All with Concurrency (P1)
**Project**: vskill
**As a** skill author with many skills in a repo
**I want** `vskill eval generate-all` to process skills concurrently
**So that** batch generation for 10+ skills takes 3-5x less wall-time

**Acceptance Criteria**:
- [x] **AC-US2-01**: Given `generate-all` is invoked, when the provider is API-based (anthropic, openrouter), then skills are processed with the existing `Semaphore` from `concurrency.ts` at concurrency 3 (configurable via `--concurrency` flag)
- [x] **AC-US2-02**: Given `generate-all` is invoked, when the provider is CLI-based (claude-cli, codex-cli, gemini-cli), then concurrency defaults to 1 (sequential) to avoid spawning multiple CLI processes
- [x] **AC-US2-03**: Given `ANTHROPIC_API_KEY` is set and `VSKILL_EVAL_PROVIDER` is not set, when `generate-all` runs, then the provider auto-selects `anthropic` instead of `claude-cli` for the batch operation
- [x] **AC-US2-04**: Given the 2-second delay between calls currently exists, when concurrency > 1, then per-skill delays are removed and rate limiting is handled by the semaphore

---

### US-003: Integration Test Auto-Generation (P1)
**Project**: vskill
**As a** skill author with MCP-dependent or browser-based skills
**I want** `vskill eval init` to auto-generate integration test cases alongside unit tests
**So that** I do not have to hand-write integration test scaffolds

**Acceptance Criteria**:
- [x] **AC-US3-01**: Given `vskill eval init --type integration` is run on a skill with MCP dependencies detected by `mcp-detector.ts`, then the generated evals include cases with `testType: "integration"` and `requiredCredentials` populated from the detected MCP servers
- [x] **AC-US3-02**: Given a skill references browser-based tools or contains Chrome profile hints, when integration evals are generated, then the cases include `requirements.chromeProfile` suggesting an available profile
- [x] **AC-US3-03**: Given a skill targets a specific platform (X, Slack, LinkedIn), when integration evals are generated, then each case includes a `cleanup` block with `{ action: "delete_post", platform: "<detected>", identifier: "{POSTED_ID}" }` format
- [x] **AC-US3-04**: Given `vskill eval init --type all` is run, then unit tests are generated with a fast model (Haiku) and integration tests with a capable model (Sonnet) in parallel, and results are merged into a single `evals.json`
- [x] **AC-US3-05**: Given a skill has no MCP dependencies and no browser requirements, when `--type integration` is specified, then the command skips integration generation and logs "No integration targets detected, generating unit tests only"

---

### US-004: Integration Test Schema Validation (P1)
**Project**: vskill
**As a** skill author
**I want** schema validation to enforce `cleanup` and `requirements.browser` fields on integration test cases
**So that** malformed integration evals are caught before execution

**Acceptance Criteria**:
- [x] **AC-US4-01**: Given an `evals.json` with `testType: "integration"` cases, when `loadAndValidateEvals()` runs, then cases missing `requiredCredentials` produce a validation warning (not error, since some integration tests may not need credentials)
- [x] **AC-US4-02**: Given a `cleanup` block with an invalid `action` value (not in the allowed set: `delete_post`, `remove_artifact`, `custom`), when validation runs, then a `ValidationError` is returned with the path and allowed values
- [x] **AC-US4-03**: Given assertions in integration test cases use LLM-judged text instead of outcome-based checks, when validation runs, then a warning is emitted suggesting API status codes or resource existence assertions

---

### US-005: Anthropic Batch API for Eval Judge Calls (P2)
**Project**: vskill
**As a** skill author running evals with Anthropic provider
**I want** judge calls to use the Message Batches API
**So that** I get 50% cost savings on the 60-70% of LLM calls that are judge assertions

**Acceptance Criteria**:
- [x] **AC-US5-01**: Given `vskill eval run --batch` is invoked with `anthropic` provider, then all judge calls for a run are submitted as a single Anthropic Message Batches API request instead of individual `messages.create` calls
- [x] **AC-US5-02**: Given a batch is submitted, when polling for results, then the interval follows the pattern: 5s for the first 60s, 15s until 5min, 30s thereafter
- [x] **AC-US5-03**: Given batch submission fails (network error, API error), when the fallback triggers, then the runner falls back to sequential judge calls using existing `judgeAssertion()` and logs a warning
- [x] **AC-US5-04**: Given `--batch` is used with a non-anthropic provider, then the flag is ignored and a warning is printed: "Batch mode only supported with anthropic provider, running sequentially"
- [x] **AC-US5-05**: Given a batch eval run completes, then the cost field in `GenerateResult` reflects the 50% batch discount and the total cost is reported in the summary

## Out of Scope

- Streaming support for batch API (Anthropic batch API is inherently non-streaming)
- UI changes to Skill Studio web interface for batch progress visualization
- Batch API for providers other than Anthropic (none offer equivalent batch pricing)
- Rewriting the integration test runner itself (already complete from increment 0547)
- Auto-detection of Chrome profiles across OS variants (use existing `chrome-profile.ts`)
- Real-time batch progress bars (polling-based status is sufficient)

## Technical Notes

### Dependencies
- `@anthropic-ai/sdk` -- existing dependency, used for `messages.create`; batch API uses `messages.batches.create` from the same SDK
- `concurrency.ts` -- existing `Semaphore` class, already used by benchmark-runner
- `mcp-detector.ts` -- existing MCP dependency detection
- `integration-runner.ts`, `credential-resolver.ts`, `chrome-profile.ts` -- existing from increment 0547

### Constraints
- CLI providers (claude-cli, codex-cli, gemini-cli) do not support parallel spawning safely; concurrency must default to 1
- Anthropic Batch API has a minimum processing time (~30s) making it unsuitable for single-case runs; only beneficial for 5+ judge calls
- `generate-all.ts` current 2s delay is for API throttling; with semaphore-based concurrency, the delay becomes unnecessary

### Architecture Decisions
- **Parallel generation**: `Promise.allSettled()` for the two LLM calls, so one failure does not block the other
- **Semaphore reuse**: Use existing `Semaphore` class rather than introducing a new concurrency primitive
- **Batch API module**: New `batch-eval-runner.ts` encapsulates all batch API logic; existing `judge.ts` remains for sequential fallback
- **Auto-provider selection**: When `ANTHROPIC_API_KEY` is set and `VSKILL_EVAL_PROVIDER` is unset, batch operations default to `anthropic` provider (3x faster than CLI)
- **Two-round batching**: Round 1 batches generation prompts, Round 2 batches judge prompts; generation must complete before judging begins

## Non-Functional Requirements

- **Performance**: Single skill generation wall-time reduced from 12-30s to 8-18s (CLI) and 4-12s to 3-7s (API)
- **Performance**: Batch `generate-all` for 10 skills reduced from ~40s sequential to ~12s with concurrency 3
- **Cost**: Batch judge calls at 50% Anthropic batch pricing for eval runs with 5+ assertions
- **Compatibility**: All existing non-batch workflows remain unchanged; `--batch` is opt-in
- **Reliability**: Batch API failure gracefully falls back to sequential with no data loss

## Edge Cases

- **One parallel call fails**: If body generation succeeds but eval generation fails, return body with empty evals and a `warning` field; if body fails, return error (body is required)
- **Batch API timeout**: If batch polling exceeds 10 minutes without completion, cancel the batch and fall back to sequential
- **Skill with no content**: If SKILL.md is empty or only frontmatter, skip integration test generation and log a warning
- **Concurrent file writes**: When `generate-all` runs concurrently, each skill writes to its own directory; no shared file contention
- **API key present but invalid**: Batch submission returns 401; fallback to sequential with a specific error message about key validity
- **Mixed test types in evals.json**: Existing unit-only evals.json files remain valid; adding integration cases via `--type all` appends without overwriting unit cases

## Risks

| Risk | Probability | Impact | Severity | Mitigation |
|------|-------------|--------|----------|------------|
| Anthropic Batch API rate limits for large eval suites | 0.3 | 5 | 1.5 | Implement exponential backoff on 429 responses; document max batch sizes |
| Parallel LLM calls may hit per-minute token limits | 0.4 | 4 | 1.6 | Semaphore limits concurrency; default 3 is conservative; configurable via flag |
| Integration test generation quality varies by skill complexity | 0.5 | 3 | 1.5 | Generated cases are scaffolds; author can refine; validation catches structural issues |
| Auto-provider selection surprises users who prefer CLI | 0.2 | 3 | 0.6 | Only auto-select for batch operations; print which provider was chosen |

## Success Metrics

- Single skill generation p50 latency drops below 10s (API) and 20s (CLI)
- `generate-all` for 10 skills completes in under 15 seconds with API provider
- 80%+ of MCP-dependent skills get usable integration test scaffolds on first generation
- Batch eval runs show 40-50% cost reduction vs sequential runs in billing comparison
