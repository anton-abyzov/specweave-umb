# Implementation Plan: Skill Generation Performance & Integration Test Auto-Generation

## Overview

This increment addresses three performance bottlenecks and one feature gap in the vskill eval pipeline. The architecture decomposes into four independent pillars, each touching a narrow slice of the codebase:

1. **Parallel skill generation** -- split the monolithic LLM call in `skill-create-routes.ts` into two concurrent calls (body + evals) using `Promise.allSettled()`
2. **Concurrent batch generation** -- replace the sequential loop + 2s delay in `generate-all.ts` with `Semaphore`-gated concurrency from `concurrency.ts`
3. **Integration test auto-generation** -- extend `prompt-builder.ts` and `init.ts` to produce `testType: "integration"` cases with `cleanup`, `requirements`, and `requiredCredentials` fields, gated on `mcp-detector.ts` and `chrome-profile.ts` detection
4. **Anthropic Batch API** -- new `batch-judge.ts` module that collects judge calls into a single `messages.batches.create` request, with polling and sequential fallback

All four pillars are independent and can be implemented in parallel. No new external dependencies are required -- `@anthropic-ai/sdk` already ships the batch API surface.

## Architecture

### Component Map

```
repositories/anton-abyzov/vskill/src/
  eval-server/
    skill-create-routes.ts   <-- Pillar 1: parallel body + evals generation
    concurrency.ts           <-- Reused (no changes)
    benchmark-runner.ts      <-- Pillar 4: optional batch judge path

  commands/eval/
    generate-all.ts          <-- Pillar 2: semaphore-gated concurrency
    init.ts                  <-- Pillar 3: --type flag, parallel model dispatch
    run.ts                   <-- Pillar 4: --batch flag, batch judge orchestration

  eval/
    prompt-builder.ts        <-- Pillar 3: new buildIntegrationEvalPrompt()
    mcp-detector.ts          <-- Read-only (existing detection)
    chrome-profile.ts        <-- Read-only (existing detection)
    schema.ts                <-- Pillar 3+4: integration validation rules
    judge.ts                 <-- Read-only (sequential fallback path)
    llm.ts                   <-- Pillar 2: auto-provider selection logic
    batch-judge.ts           <-- NEW: Pillar 4, Anthropic Batch API wrapper
    integration-types.ts     <-- Extended: cleanup schema types for evals.json
```

### Pillar 1: Parallel Skill Generation (US-001)

**Current**: Single `client.generate()` call in `skill-create-routes.ts` POST `/api/skills/generate` produces both SKILL.md body and evals in one monolithic prompt/response.

**Target**: Two concurrent `Promise.allSettled()` calls:
- Call A (capable model, e.g. Sonnet): generates SKILL.md body + metadata
- Call B (fast model, e.g. Haiku): generates evals only

```
POST /api/skills/generate
  |
  +-- Promise.allSettled([
  |     callA: client.generate(BODY_SYSTEM_PROMPT, userPrompt),   // Sonnet
  |     callB: evalClient.generate(EVAL_SYSTEM_PROMPT, userPrompt) // Haiku
  |   ])
  |
  +-- Merge: body from A, evals from B
  +-- If B fails: body from A, evals=[], warning field
  +-- If A fails: return error (body is required)
```

**Key decisions**:
- Split the existing `GENERATE_SYSTEM_PROMPT` into two: `BODY_SYSTEM_PROMPT` (body + metadata, no evals) and `EVAL_SYSTEM_PROMPT` (evals only, given a brief skill description)
- Call B receives a condensed version of Call A's context (skill name + description + key instructions) rather than the full SKILL.md body, since it only needs to generate test cases
- The eval model is configurable via `VSKILL_EVAL_GEN_MODEL` env var, defaulting to Haiku
- SSE events updated: `"generating-body"` and `"generating-evals"` phases emitted concurrently
- `parseGenerateResponse()` splits into `parseBodyResponse()` and `parseEvalsResponse()`, then a `mergeGenerateResults()` function combines them into the existing `GenerateSkillResult` shape

**Response shape**: Unchanged -- `GenerateSkillResult` keeps the same fields. A new optional `warning?: string` field is added for partial failures.

### Pillar 2: Concurrent Batch Generate-All (US-002)

**Current**: `generate-all.ts` loops skills sequentially with `await new Promise(r => setTimeout(r, 2000))` between each call.

**Target**: Semaphore-gated `Promise.allSettled()` over all skills.

```
generate-all --concurrency 3
  |
  +-- scanSkills(root)
  +-- Semaphore(concurrency)    // from concurrency.ts
  +-- Promise.allSettled(
        skills.map(skill => {
          await sem.acquire()
          try { await generateSingleSkill(skill, client) }
          finally { sem.release() }
        })
      )
  +-- Print summary
```

**Key decisions**:
- New `--concurrency <N>` flag on `generate-all` command. Default: 3 for API providers, 1 for CLI providers
- Auto-provider selection (AC-US2-03): in `generate-all.ts`, when starting a batch op, check `ANTHROPIC_API_KEY` + `VSKILL_EVAL_PROVIDER`. If key is set and provider is not set, auto-select `"anthropic"` and log `"Auto-selected anthropic provider for batch operation"`
- The 2-second delay is removed when concurrency > 1; the Semaphore handles backpressure
- The `createLlmClient()` call is made once before the batch loop (single client instance shared across concurrent tasks -- it is stateless per call)
- Summary stats remain: scanned, generated, skipped, failed
- The `Semaphore` from `concurrency.ts` is imported directly (it is already in `eval-server/` but can be moved or re-exported from `eval/` if preferred -- however since `generate-all.ts` already imports from `../../eval/`, we import from `../../eval-server/concurrency.js` or extract a shared `concurrency.ts` to `eval/`)

**Import path decision**: Move `Semaphore` to `eval/concurrency.ts` (shared module) and re-export from `eval-server/concurrency.ts` for backward compat. This avoids `commands/eval/generate-all.ts` reaching into `eval-server/`.

### Pillar 3: Integration Test Auto-Generation (US-003, US-004)

**Current**: `buildEvalInitPrompt()` in `prompt-builder.ts` generates unit tests only. MCP detection is used for simulation instructions but not for integration test scaffolding.

**Target**: New `--type <unit|integration|all>` flag on `vskill eval init`. When `integration` or `all`:

```
vskill eval init --type integration
  |
  +-- Read SKILL.md
  +-- detectMcpDependencies(skillContent)    // existing
  +-- detectBrowserRequirements(skillContent) // new function
  +-- detectPlatformTargets(skillContent)     // new function
  |
  +-- if (no MCP deps && no browser reqs):
  |     log "No integration targets detected, generating unit tests only"
  |     return
  |
  +-- buildIntegrationEvalPrompt(skillContent, mcpDeps, browserReqs, platforms)
  +-- client.generate(INTEGRATION_SYSTEM, integrationPrompt)  // Sonnet
  +-- parseGeneratedIntegrationEvals(result)
  |
  +-- if --type all:
  |     Promise.allSettled([
  |       unitClient.generate(unitPrompt),       // Haiku
  |       integrationClient.generate(intgPrompt)  // Sonnet
  |     ])
  |     merge results into single evals.json
  |
  +-- Write evals.json
```

**New functions in `prompt-builder.ts`**:

- `buildIntegrationEvalPrompt(skillContent, mcpDeps, browserReqs, platforms)`: Constructs a prompt that instructs the LLM to generate `testType: "integration"` cases with:
  - `requiredCredentials` populated from detected MCP server environment variable patterns
  - `requirements.chromeProfile` when browser tools or Chrome profile hints are detected
  - `cleanup` blocks with `{ action: "delete_post" | "remove_artifact" | "custom", platform, identifier: "{POSTED_ID}" }` for platform-targeting skills
- `parseGeneratedIntegrationEvals(raw)`: Parses and validates integration-specific fields

**New detection functions** (in `prompt-builder.ts` or a new `integration-detector.ts`):

- `detectBrowserRequirements(skillContent)`: Scans for `Bash` in allowed-tools + browser/Chrome/Playwright references in the body. Returns `{ hasBrowser: boolean, suggestedProfile?: string }`
- `detectPlatformTargets(skillContent)`: Scans for known platform keywords (X/Twitter, Slack, LinkedIn, Instagram, YouTube). Returns `string[]` of detected platforms

**Schema validation extensions (US-004)** in `schema.ts`:

Add to `loadAndValidateEvals()`:
1. For `testType: "integration"` cases missing `requiredCredentials`: emit **warning** (not error)
2. For `cleanup[].action` not in `["delete_post", "remove_artifact", "custom"]`: emit **ValidationError** with path and allowed values
3. For integration assertions that look like LLM-judged prose (heuristic: assertion text > 100 chars and no verb like "returns", "contains", "exists", "equals"): emit **warning** suggesting API status codes or resource existence assertions

**Credential mapping**: The prompt for integration eval generation includes a mapping of MCP server -> typical env var names:
```
Slack -> SLACK_BOT_TOKEN
GitHub -> GITHUB_TOKEN
Linear -> LINEAR_API_KEY
...
```
This is derived from the existing `MCP_REGISTRY` in `mcp-detector.ts` plus a new `CREDENTIAL_HINTS` map.

### Pillar 4: Anthropic Batch API for Judge Calls (US-005)

**Current**: `judgeAssertion()` in `judge.ts` makes individual `messages.create` calls per assertion. In `run.ts`, assertions are judged sequentially. In `benchmark-runner.ts`, they are parallelized via `Promise.all` per case but still individual API calls.

**Target**: New `batch-judge.ts` module that:
1. Collects all judge prompts across all cases in a run
2. Submits them as a single `messages.batches.create` request
3. Polls for completion with escalating intervals (5s -> 15s -> 30s)
4. Maps results back to assertion IDs
5. Falls back to sequential `judgeAssertion()` on any failure

```
NEW: eval/batch-judge.ts

  batchJudgeAssertions(requests: BatchJudgeRequest[]): Promise<AssertionResult[]>
    |
    +-- Build batch request body:
    |     requests = assertions.map(a => ({
    |       custom_id: `${evalId}_${assertionId}`,
    |       params: {
    |         model, system: judgeSystemPrompt,
    |         messages: [{ role: "user", content: judgeUserPrompt }],
    |         max_tokens: 256
    |       }
    |     }))
    |
    +-- client.messages.batches.create({ requests })
    |
    +-- Poll loop:
    |     0-60s:  poll every 5s
    |     60s-5m: poll every 15s
    |     5m+:    poll every 30s
    |     10m:    TIMEOUT -> cancel batch -> fallback to sequential
    |
    +-- Parse results: map custom_id -> AssertionResult
    +-- On any error: fallback to sequential judgeAssertion() calls
```

**Integration into `run.ts`**:

New `--batch` flag:
- If `--batch` and provider is `anthropic`: use `batchJudgeAssertions()` for all judge calls
- If `--batch` and provider is not `anthropic`: print warning, ignore flag, run sequentially
- Two-round execution: Round 1 runs all generation calls (existing sequential/concurrent flow). Round 2 collects all judge prompts from all cases and submits a single batch

**Cost reporting**:
- `GenerateResult.cost` field (already nullable) is populated with the 50% discounted rate for batch calls
- Summary line in `run.ts` reports: `Batch cost: $X.XX (50% discount vs $Y.YY sequential)`

**Minimum batch size**: If total judge calls < 5, skip batch API and run sequentially (batch API has ~30s minimum processing time, not worth it for small runs).

**Integration into `benchmark-runner.ts`** (SSE server path):
- Not in scope for initial implementation. Batch API is inherently non-streaming and the SSE endpoint needs per-assertion progress events. A future increment could batch judges at end-of-run and emit a single "judging-batch" phase.

### Data Flow Summary

```
                    Pillar 1                      Pillar 2
               (Parallel Gen)              (Concurrent Batch)
                     |                            |
  POST /generate --> Promise.allSettled    generate-all --> Semaphore
  [body|evals]       [bodyCall|evalCall]   [skill1|skill2|skill3]
                     |                            |
                     v                            v
              mergeGenerateResults          per-skill generate
                                                  |
                    Pillar 3                      |
            (Integration TestGen)                 |
                     |                            |
  eval init --type --> detectMcpDeps       (shared createLlmClient)
  [integration]       detectBrowser
                      detectPlatform
                     |
                     v
              buildIntegrationEvalPrompt
              parseGeneratedIntegrationEvals
                     |
                     v
              write evals.json (with testType: "integration")
                     |
                    Pillar 4
              (Batch Judge API)
                     |
  eval run --batch --> collect all judge prompts
                     |
                     v
              messages.batches.create
              poll -> parse -> map back to AssertionResult
              fallback -> sequential judgeAssertion()
```

## Technology Stack

- **Language**: TypeScript (ESM, `.js` extensions in imports per vskill convention)
- **Runtime**: Node.js 20+
- **SDK**: `@anthropic-ai/sdk` (existing dep) -- `messages.batches.create`, `messages.batches.retrieve`, `messages.batches.cancel`
- **Concurrency**: `Semaphore` class from `concurrency.ts` (existing)
- **Testing**: Vitest (unit), existing eval runner for integration validation

**No new dependencies required.**

## Architecture Decisions

### AD-1: Promise.allSettled over Promise.all for parallel generation

**Decision**: Use `Promise.allSettled()` for the dual LLM call in Pillar 1.

**Why**: `Promise.all()` rejects on first failure, losing the successful result. Since body and evals are independent, we want partial results (body without evals) rather than total failure. The spec explicitly requires graceful degradation: "If Call A succeeds but Call B fails, return body with empty evals and warning."

**Alternative rejected**: `Promise.all()` with individual try-catch wrapping. More verbose, same semantics, less idiomatic.

### AD-2: Move Semaphore to shared eval/ directory

**Decision**: Extract `Semaphore` and `getSkillSemaphore` from `eval-server/concurrency.ts` to `eval/concurrency.ts`. Re-export from the original location for backward compatibility.

**Why**: `commands/eval/generate-all.ts` needs the Semaphore but should not import from `eval-server/` (server-specific code). The Semaphore is a generic concurrency primitive with no server dependencies.

**Alternative rejected**: Duplicate the class. Violates DRY.

### AD-3: Two separate system prompts for body vs evals generation

**Decision**: Split `GENERATE_SYSTEM_PROMPT` into `BODY_SYSTEM_PROMPT` and `EVAL_SYSTEM_PROMPT`.

**Why**: The current monolithic prompt asks the LLM to produce both body and evals in one JSON response. Splitting allows: (1) different models for each task, (2) each prompt is shorter and more focused, (3) the eval prompt can be reused for `eval init --type` generation.

**Risk**: Two prompts means two response parsers. Mitigated by keeping the JSON shapes simple and using shared validation.

### AD-4: Auto-provider selection scoped to batch operations only

**Decision**: When `ANTHROPIC_API_KEY` is set and `VSKILL_EVAL_PROVIDER` is not set, auto-select `anthropic` provider only in `generate-all` (batch context), not in `eval init` or `eval run`.

**Why**: Users who set `ANTHROPIC_API_KEY` for batch judge purposes may still prefer `claude-cli` for interactive single-skill operations. Auto-selection should be limited to the batch context where API is clearly superior (3x faster, no CLI spawning overhead).

**Implementation**: The auto-selection logic lives in `generate-all.ts` before calling `createLlmClient()`, not in `createLlmClient()` itself. This keeps the core LLM client provider-agnostic.

### AD-5: Batch API with sequential fallback, not the reverse

**Decision**: The `--batch` flag opts into batch mode. On any failure (network, API error, timeout), fall back to sequential `judgeAssertion()` calls. The user never needs to manually retry.

**Why**: Batch API is an optimization, not a requirement. Users should never be blocked by batch infrastructure issues. The fallback path is the existing, well-tested sequential judge flow.

**Timeout**: 10 minutes max polling time before cancellation + fallback. This is generous (Anthropic batch typically completes in 1-3 minutes for small batches) but prevents indefinite hangs.

### AD-6: Integration detection as pure functions, no new classes

**Decision**: `detectBrowserRequirements()` and `detectPlatformTargets()` are pure functions co-located in `prompt-builder.ts` (alongside existing `detectBashTools()`), not a separate "integration-detector" module.

**Why**: These functions are small (10-20 lines each), pure, and only used during prompt construction. A separate module would be over-engineering. If they grow, extract later.

### AD-7: Validation warnings for integration cases, not hard errors

**Decision**: Missing `requiredCredentials` on integration cases produces a warning, not an error. Invalid `cleanup.action` values produce a hard error.

**Why**: Some integration tests legitimately don't need credentials (e.g., browser-only tests against public pages). But invalid cleanup actions indicate structural errors that would cause runtime failures. The asymmetry is intentional and matches the spec (AC-US4-01 vs AC-US4-02).

## Implementation Phases

### Phase 1: Foundation (can parallelize)

1. **Move Semaphore** to `eval/concurrency.ts`, re-export from `eval-server/concurrency.ts` (AD-2)
2. **Add `warning` field** to `GenerateSkillResult` interface in `skill-create-routes.ts`
3. **Add integration schema types** to `integration-types.ts`: `EvalCleanupSchema` with `action` enum, `EvalRequirementsSchema` with `chromeProfile`, `platform`
4. **Extend `EvalCase` in `schema.ts`**: add `cleanup`, `requirements` optional fields for integration cases

### Phase 2: Core -- Parallel Generation (Pillar 1)

5. Split `GENERATE_SYSTEM_PROMPT` into `BODY_SYSTEM_PROMPT` + `EVAL_SYSTEM_PROMPT`
6. Add `parseBodyResponse()` and `parseEvalsResponse()` functions
7. Refactor `POST /api/skills/generate` to use `Promise.allSettled([bodyCall, evalCall])`
8. Update SSE events: emit `"generating-body"` and `"generating-evals"` phases
9. Handle partial failure: body success + eval failure = return with warning

### Phase 3: Core -- Concurrent Batch Generation (Pillar 2)

10. Add `--concurrency` flag to `generate-all` command registration
11. Refactor `runEvalGenerateAll()` to use `Semaphore`-gated `Promise.allSettled()`
12. Add auto-provider selection: check `ANTHROPIC_API_KEY` when `VSKILL_EVAL_PROVIDER` is unset
13. Remove 2-second delay when concurrency > 1
14. Print selected provider and concurrency level in output

### Phase 4: Core -- Integration Test Auto-Generation (Pillar 3)

15. Add `detectBrowserRequirements()` and `detectPlatformTargets()` to `prompt-builder.ts`
16. Add `CREDENTIAL_HINTS` map (MCP server -> env var names)
17. Implement `buildIntegrationEvalPrompt()` with cleanup/requirements/credentials scaffolding
18. Implement `parseGeneratedIntegrationEvals()` with integration field validation
19. Add `--type <unit|integration|all>` flag to `eval init` command
20. Refactor `runEvalInit()` to support type selection and parallel model dispatch for `--type all`
21. Extend `loadAndValidateEvals()` with integration-specific validation (US-004)

### Phase 5: Enhancement -- Anthropic Batch API (Pillar 4)

22. Create `eval/batch-judge.ts`: `batchJudgeAssertions()` function
23. Implement polling loop with escalating intervals (5s/15s/30s) and 10-minute timeout
24. Implement sequential fallback on batch failure
25. Add `--batch` flag to `eval run` command
26. Refactor `runEvalRun()` to support two-round execution (generate all, then batch-judge all)
27. Add cost calculation with 50% batch discount to `GenerateResult`
28. Print batch cost comparison in summary

## Testing Strategy

**Unit tests (Vitest)**:
- `prompt-builder.test.ts`: test `buildIntegrationEvalPrompt()`, `detectBrowserRequirements()`, `detectPlatformTargets()` with various SKILL.md contents
- `batch-judge.test.ts`: test polling logic, timeout handling, fallback triggering (mock `@anthropic-ai/sdk`)
- `generate-all.test.ts`: test concurrency behavior, auto-provider selection, delay removal
- `schema.test.ts`: test integration validation warnings/errors (cleanup action validation, missing credentials warning)
- `skill-create-routes.test.ts`: test parallel generation merge logic, partial failure handling

**Integration validation**: Run `vskill eval init --type integration` on existing MCP-dependent skills (social-media-posting, github-pr-reviewer) and verify generated evals.json contains valid integration cases.

**TDD approach**: Each new function gets a test file first (red), then implementation (green), then refactor.

## Technical Challenges

### Challenge 1: Prompt splitting without quality regression

The current monolithic prompt produces body and evals in a single context, which means the LLM has full body context when generating evals. Splitting means Call B (evals) only gets a condensed description, potentially reducing eval quality.

**Solution**: Call B's prompt includes: skill name, description, key workflow steps (extracted from the user's original prompt), and the Skill Studio eval best practices. This gives enough context for quality evals without needing the full body. If eval quality drops noticeably, we can pass Call A's body to Call B as a second round (sequential for evals, parallel for body generation).

**Risk**: Low. Eval generation is already a "scaffold" -- users refine generated evals. Slightly lower initial quality is acceptable given 30-40% speed improvement.

### Challenge 2: Anthropic Batch API SDK surface

The `@anthropic-ai/sdk` batch API (`messages.batches.create`) has a different request shape than individual `messages.create`. The custom_id-based result mapping requires careful handling.

**Solution**: Encapsulate entirely in `batch-judge.ts`. The rest of the codebase only sees `AssertionResult[]` -- the batch/sequential distinction is an internal implementation detail. Use `custom_id` format `{evalId}_{assertionId}` for unambiguous result mapping.

**Risk**: Low. The SDK is well-documented and the batch shape is straightforward.

### Challenge 3: Race conditions in concurrent generate-all

When multiple skills generate concurrently, each writes to its own `evals/evals.json` in its own skill directory. No shared file contention exists by design. However, console output from concurrent tasks may interleave.

**Solution**: Buffer per-skill output and print atomically after each skill completes. Use `Semaphore` to control concurrency (already proven in `benchmark-runner.ts`).

**Risk**: Very low. Each skill directory is independent.

## Domain Skill Recommendations

No additional domain skills needed. This increment is entirely within the vskill CLI/eval infrastructure (TypeScript, Node.js, Vitest). The `backend:nodejs` skill could assist during implementation but the architecture is straightforward enough that it is not required.
