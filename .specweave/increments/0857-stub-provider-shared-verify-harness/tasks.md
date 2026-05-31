# 0857 — Tasks

### T-001: Add deterministic `stub` provider to src/eval/llm.ts
**AC**: AC-US1-01 | **Status**: [x] completed
**Test**: Given `createLlmClient({provider:'stub', model:'haiku'})` → When `generate()` runs twice with the same prompt → Then `client.model === 'haiku'` and both outputs are byte-identical, with no network/key.

### T-002: Hide stub from provider discovery + API
**AC**: AC-US3-01, AC-US3-02 | **Status**: [x] completed
**Test**: Given `detectAvailableProviders()` → When inspected → Then no entry has `id === 'stub'`; and `KNOWN_PROVIDER_NAMES` does not contain `stub`.

### T-003: Preserve 0856 CLAUDE_CLI_NORMALIZE 4.8 line
**AC**: AC-US3-03 | **Status**: [x] completed
**Test**: Given CLAUDE_CLI_NORMALIZE → When read → Then `claude-opus-4-8` maps to `opus` (unchanged).

### T-004: Thread --provider/--model into `vskill skill new`
**AC**: AC-US1-02 | **Status**: [x] completed
**Test**: Given `skill new --prompt X --provider stub --model opus` → When run → Then `generateSkill` receives `{provider:'stub', model:'opus'}` and SKILL.md gets `model: opus` on claude-code.

### T-005: Promote 0853 harness into vskill test/verify/ with re-rooted paths
**AC**: AC-US1-05, AC-US2-01 | **Status**: [x] completed
**Test**: Given `node test/verify/run-verify.mjs` → When run → Then it resolves VSKILL_BIN/fixtures against the vskill root and writes the VerifyResult JSON + agent handle.

### T-006: package.json verify scripts
**AC**: AC-US1-05 | **Status**: [x] completed
**Test**: Given `npm run verify` and `npm run verify:matrix` → When invoked → Then they run the harness and the matrix node:test.

### T-007: U-GOLDEN unit (create->install->run-with-non-default-model)
**AC**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05, AC-US2-03 | **Status**: [x] completed
**Test**: Given a tmp-isolated workdir → When create(stub,opus)->install->eval-run(stub,opus) → Then surface has `ranModel === requestedModel === 'opus'` and benchmark cases>0; probes: unknown-provider BLOCKED, model-ignored FAIL.

### T-008: run.test.ts judge-model plumbing guard
**AC**: AC-US1-05 | **Status**: [x] completed
**Test**: Given `runEvalRun(dir,{judgeModel:'anthropic/claude-opus-4-6'})` → When run → Then `createLlmClient` is called with `{provider:'anthropic', model:'claude-opus-4-6'}`.

### T-009: llm.test.ts argv + stub determinism
**AC**: AC-US1-01 | **Status**: [x] completed
**Test**: Given claude-cli `model:'opus'`/`'sonnet'` → Then argv is `['-p','--model',<model>]` and `client.model===normalized`. Stub `model:'haiku'` echoes + deterministic.

### T-010: claude-cli compliance contract pin
**AC**: AC-US3-03 | **Status**: [x] completed
**Test**: Given claude-cli client with no ANTHROPIC_API_KEY → Then no throw, CLAUDE* stripped from child env, `billingMode==='subscription'`.

### T-011: Cross-surface default-model invariant test
**AC**: AC-US1-01 | **Status**: [x] completed
**Test**: Given CLI vs Studio claude-cli defaults → Then CLI default alias is `sonnet` and Studio `PROVIDER_MODELS['claude-cli'][0].id` is `opus`.

### T-012: Loud-skip gate in matrix.test.mjs
**AC**: AC-US2-01, AC-US2-02 | **Status**: [x] completed
**Test**: Given a verify run → When all model lanes SKIP → Then the gate fails (≥1 PASS required) and each SKIP emits `::warning::` with provider+reason.
