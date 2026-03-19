# Brainstorm: vSkill Studio Performance, Multi-Model, and Integration Tests
**Date**: 2026-03-16 | **Depth**: deep | **Lens**: default (4 parallel agents) | **Status**: complete

## Problem Frame
**Statement**: vSkill Studio runs all LLM calls sequentially (25-35 calls per eval = 5-12 min), lacks validation with non-Claude models, and has no real integration test execution despite schema support. Users need faster evals, multi-model quality comparison, and the ability to prove skills work in the real world.

## Approaches

### Theme 1: Performance Optimization

#### Approach A: Parallel Semaphore-Gated Concurrency
**Source**: Performance agent | **Effort**: Medium | **Speedup**: 4-6x
**Summary**: Activate existing `concurrency.ts` semaphore. Replace sequential loops with `Promise.all` for cases, assertions, and skill+baseline generation.
**Key Steps**:
1. Wire `concurrency.ts` with configurable max (default 5), wrap every LLM call
2. Replace case `for` loop with `Promise.allSettled` (partial-failure tolerance)
3. Within each case, run assertion judges via `Promise.all` (independent evaluations)
4. In comparator, run skill+baseline concurrently: `Promise.all([generateSkill(), generateBaseline()])`
5. Expose `--concurrency N` CLI flag with API rate limit safety cap
**Strengths**: Uses existing infrastructure, near-linear speedup, no behavioral change to results
**Risks**: API rate limits (429 errors need retry-with-backoff), SSE progress interleaving

#### Approach B: Tiered Model Strategy (Fast Judges)
**Source**: Performance agent | **Effort**: Medium | **Speedup**: 2-4x (8-15x with A)
**Summary**: Use Haiku/GPT-4o-mini for assertion judging, keep expensive model for generation only. Judges are 60-70% of total calls.
**Key Steps**:
1. Add `judgeModel` config field separate from `model` (defaults to `same`)
2. Route assertion judgments through fast model
3. Implement confidence threshold: borderline scores (40-60%) re-judge with primary model
4. Cache judge prompts by hash `(assertion, output, input)` — skip on identical outputs
5. Add `--judge-model` CLI flag
**Strengths**: Haiku 1-3s vs Sonnet 12-30s per judge call, 10-25x cheaper, composable with parallelism
**Risks**: Weaker judges may disagree on nuanced assertions (needs calibration)

#### Approach C: Anthropic Batch API (Bulk Runs)
**Source**: Performance agent | **Effort**: High | **Speedup**: 5-10x for large evals
**Summary**: Submit all LLM calls as batch API requests. 50% cost, eliminates per-call latency. Best for CI/scheduled benchmarks, not interactive use.
**Strengths**: Eliminates network latency, 50% cost reduction
**Risks**: Two-phase dependency (generate then judge), no streaming progress, requires Anthropic API key

### Theme 2: Multi-Model Support

#### Approach D: OpenRouter as First-Class Provider
**Source**: Multi-model agent | **Effort**: Medium
**Summary**: Add OpenRouter as 6th provider. Single API key unlocks 100+ models via unified OpenAI-compatible endpoint. Returns per-request cost data.
**Key Steps**:
1. Add `"openrouter"` to provider union type
2. Implement adapter targeting `https://openrouter.ai/api/v1/chat/completions`
3. Handle OpenRouter model IDs (`meta-llama/llama-3.1-70b-instruct`)
4. Use `usage.total_cost` for automatic cost tracking
5. Add model search/autocomplete in Studio dropdown (hit `/api/v1/models`)
**Config example**:
```json
{ "provider": "openrouter", "model": "meta-llama/llama-3.1-70b-instruct", "env": "OPENROUTER_API_KEY" }
```
**Strengths**: One key = all models, built-in cost tracking, OpenAI-compatible adapter
**Risks**: Proxy latency, variable pricing, shared rate limits across models

#### Approach E: Separated Judge Model with Calibration
**Source**: Multi-model agent | **Effort**: High
**Summary**: Decouple judge from generation model. When Llama generates, Claude judges. Add calibration layer to adjust scores (weak models are generous self-judges: llama3.1:8b routinely gives 8-9/10 to mediocre output).
**Config example**:
```json
{
  "generation": { "provider": "ollama", "model": "llama3.1:8b" },
  "judge": { "provider": "anthropic", "model": "claude-sonnet-4-20250514" },
  "calibration": { "enabled": true, "referenceJudge": "anthropic/claude-sonnet-4" }
}
```
**Strengths**: Solves core problem of weak self-judging, calibration factors reusable
**Risks**: 20-50 reference evals needed per model for calibration, philosophical question of cross-model bias

#### Approach F: Per-Model Quality Leaderboard
**Source**: Multi-model agent + UI agent | **Effort**: High
**Summary**: `vskill eval sweep` runs same evals across N models, stores results, renders comparison dashboard with table/bar/radar views.
**CLI**:
```bash
vskill eval sweep --models "anthropic/claude-sonnet-4,openrouter/meta-llama/llama-3.1-70b,ollama/llama3.1:8b" --judge anthropic/claude-sonnet-4 --runs 3
```
**Leaderboard UI**:
```
#  Model              Pass   Rubric  Duration  Trend
1  Claude Sonnet 4    95%    4.7/5   2.1s      ▁▃▅▇█   Best
2  Gemini 2.5 Pro     90%    4.5/5   1.8s      ▁▂▅▆█
3  Llama 4 Scout      82%    4.1/5   3.4s      ▁▃▃▅▆
4  Codex Mini         75%    3.8/5   1.2s      ▁▂▃▄▅
```
**Platform badge**: `Claude Sonnet 4 (8.7) | GPT-4o (8.2) | Llama 70B (7.1) | Llama 8B (4.3)`
**Strengths**: Transforms from "does it work?" to "how well across ecosystem?", cost/latency alongside quality
**Risks**: Expensive sweep runs, score variance needs confidence intervals

### Theme 3: Integration Tests

#### Approach G: Integration Test Runner with Real API Execution
**Source**: Integration test agent | **Effort**: High
**Summary**: Build a real integration test runner that executes skill output against real APIs (post to X, verify post exists, cleanup). Phases: Credential Check -> Generate -> Execute -> Verify -> Cleanup -> Report.
**evals.json example** (social-media-posting):
```json
{
  "id": 100,
  "name": "integration-post-to-x-and-verify",
  "testType": "integration",
  "requiredCredentials": ["X_API_KEY", "X_API_SECRET", "X_ACCESS_TOKEN", "X_ACCESS_TOKEN_SECRET"],
  "requirements": { "browser": false, "mcp": ["social-media-posting"], "sandbox": true },
  "prompt": "Post a test message: '[VSKILL-TEST-{RUN_ID}] Integration test...'",
  "cleanup": { "action": "delete_post", "platform": "x", "identifier": "{POSTED_TWEET_ID}" },
  "timeout": 120000,
  "assertions": [
    { "id": "api-call-made", "text": "X API returned 201 for tweet creation", "type": "boolean" },
    { "id": "post-retrievable", "text": "GET /2/tweets/{id} confirms tweet exists", "type": "boolean" },
    { "id": "cleanup-successful", "text": "DELETE /2/tweets/{id} returns 200", "type": "boolean" }
  ]
}
```
**Safety guardrails**: Test account isolation, dry-run mode, confirmation prompts, rate limiting, `[VSKILL-TEST-]` content prefix, emergency kill switch with cleanup
**Strengths**: Proves skills actually work in the real world, cleanup prevents pollution
**Risks**: Real API costs, cleanup failures leaving orphaned posts, platform rate limits

#### Approach H: Credential Vault and Management
**Source**: UI agent | **Effort**: Medium-High
**Summary**: Layered secrets system: env vars -> `.env.integration` -> OS keychain -> CI vault. Studio Settings panel shows credential status (green/red/yellow dots). CLI: `vskill credentials set/list/test`.
**Resolution chain**: `ENV var -> .env.integration -> OS keychain -> CI vault`
**UI**:
```
Credential          Status     Source    Actions
SLACK_TOKEN         Ready      env var   [Test] [Remove]
GITHUB_TOKEN        Ready      vault     [Test] [Remove]
SENDGRID_API_KEY    Missing    --        [Set]
AWS_ACCESS_KEY      Untested   vault     [Test] [Remove]
```
**Safety**: Secret-scanning pre-flight rejects evals.json containing token patterns, .gitignore enforcement
**Strengths**: Security-first, instant visibility, CLI parity for CI/CD
**Risks**: Cross-platform keychain differences, credential test probes need author implementation

#### Approach I: Unit vs Integration Test UI Visualization
**Source**: UI agent | **Effort**: Medium
**Summary**: Visual taxonomy in TestsPanel — blue `[U]` badges for unit, amber `[I]` for integration. Lock icon + "Configure Credentials" for gated tests. Platform shows "Unit tests only" with local Studio CTA.
**Studio UI**:
```
── Unit Tests ──────────────────
  [U] Generates correct summary      pass  Run
  [U] Handles empty input            pass  Run
── Integration Tests ───────────
  [I] Posts to Slack channel          idle  Run
  [I] Creates GitHub issue            idle  Run
  [I] Sends email via SendGrid     [Configure...]
```
**Platform**: "N integration tests defined -- run locally in vSkill Studio"
**Strengths**: Zero ambiguity, progressive disclosure, drives Studio adoption
**Risks**: Dead weight if no integration tests exist initially

## Evaluation Matrix

| Criterion | A: Parallel | B: Fast Judge | C: Batch | D: OpenRouter | E: Calibration | F: Leaderboard | G: Int Runner | H: Cred Vault | I: UI Viz |
|---|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| Complexity | 2 | 3 | 4 | 2 | 4 | 4 | 5 | 3 | 2 |
| Time | 2 | 3 | 4 | 2 | 4 | 4 | 5 | 3 | 2 |
| Risk | 2 | 2 | 3 | 2 | 3 | 2 | 4 | 2 | 1 |
| Extensibility | 5 | 4 | 3 | 5 | 4 | 5 | 5 | 4 | 4 |
| Alignment | 5 | 4 | 2 | 5 | 3 | 4 | 3 | 4 | 5 |
| **Score** | **16** | **16** | **16** | **16** | **18** | **19** | **22** | **16** | **14** |

## Recommended Implementation Order

### Phase 1: Quick Wins (1-2 increments)
1. **A: Parallel Semaphore** — 4-6x speedup, medium effort, existing infra
2. **I: Unit/Integration UI** — visual differentiation, low effort

### Phase 2: Multi-Model Foundation (2-3 increments)
3. **D: OpenRouter Provider** — unlocks 100+ models with one API key
4. **B: Tiered Judge Model** — fast judges + separate judge config
5. **E: Judge Calibration** — makes weak-model results trustworthy

### Phase 3: Leaderboard + Integration (3-4 increments)
6. **F: Per-Model Leaderboard** — sweep command + dashboard
7. **H: Credential Vault** — prerequisite for integration tests
8. **G: Integration Test Runner** — real API execution with cleanup

### Phase 4: Scale (optional)
9. **C: Batch API** — for CI/scheduled bulk runs

## Unit vs Integration: Side-by-Side

| Aspect | Unit Test | Integration Test |
|---|---|---|
| MCP tools | Simulated (LLM describes) | Real (actual API calls) |
| Credentials | None | `requiredCredentials` must resolve |
| Side effects | Zero | Real posts, cleaned up after |
| Speed | 10-30s/case | 30-120s/case |
| Run frequency | Every eval | On demand (`--integration`) |
| Run on platform | Yes (Verified Skill) | No (local Studio only) |
| Assertions check | LLM text output | Real outcomes (post exists, API status) |
| Cost | LLM tokens only | LLM tokens + platform API costs |

## Next Steps
- `/sw:increment` to start with Phase 1 (parallel + UI visualization)
- Brainstorm deeper on integration test runner with `--resume --depth deep`
- Park leaderboard for after OpenRouter is integrated
