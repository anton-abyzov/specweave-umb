---
increment: 0815-multi-file-skill-generation
tasks_generated: 2026-04-30
total: 33
---

# Tasks: Multi-file skill generation with parallel sub-agents

---

## US-001: Manifest schema extension (backwards-compatible)

### T-001: Add SkillSecret / SkillRuntime / SkillIntegrationTests interfaces to types.ts
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01 | **Status**: [x] completed
**Test Plan**: Given the updated `types.ts`, when TypeScript compiles, then `SkillInfo` exports optional `secrets?`, `runtime?`, `integrationTests?` fields and the three new interfaces (`SkillSecret`, `SkillRuntime`, `SkillIntegrationTests`) are exported from the same module without breaking any existing field.
**Artifact**: `repositories/anton-abyzov/vskill/src/eval-ui/src/types.ts`
**Test command**: `npm test`

---

### T-002: RED — frontmatter parser unit test (lib)
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02, AC-US1-05 | **Status**: [x] completed
**Test Plan**: Given `src/lib/__tests__/frontmatter.secrets.test.ts`, when it parses YAML with `secrets`, `runtime`, and `integrationTests` blocks, then the parser returns the correct typed shapes; when those blocks are absent, then every new field is `undefined` (not an error). Tests must FAIL before the parser is updated.
**Artifact**: `repositories/anton-abyzov/vskill/src/lib/__tests__/frontmatter.secrets.test.ts`
**Test command**: `npm test`

---

### T-003: GREEN — extend lib/frontmatter.ts parser
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02, AC-US1-05 | **Status**: [x] completed
**Test Plan**: Given the RED tests from T-002, when `lib/frontmatter.ts` is updated to read `secrets`, `runtime`, and `integrationTests` from YAML, then all tests pass. Existing fields (`name`, `description`, `version`, `mcpDeps`, etc.) remain unchanged and their tests still pass.
**Artifact**: `repositories/anton-abyzov/vskill/src/lib/frontmatter.ts`
**Test command**: `npm test`

---

### T-004: Extend installer/frontmatter.ts to mirror lib parser
**User Story**: US-001 | **Satisfies ACs**: AC-US1-03 | **Status**: [x] completed
**Test Plan**: Given a SKILL.md file with all three new blocks, when it is parsed through `installer/frontmatter.ts`, then the same typed output produced by `lib/frontmatter.ts` is returned; when blocks are absent, fields are `undefined`.
**Artifact**: `repositories/anton-abyzov/vskill/src/installer/frontmatter.ts`
**Test command**: `npm test`

---

### T-005: RED — skill-scanner propagation unit test
**User Story**: US-001 | **Satisfies ACs**: AC-US1-04, AC-US1-05 | **Status**: [x] completed
**Test Plan**: Given `src/eval/__tests__/skill-scanner.multiFile.test.ts`, when the scanner normalizes a skill with `secrets`, `runtime`, and `integrationTests` blocks, then the resulting `SkillInfo` carries those fields; when blocks are absent, the fields are `null` (not `undefined`) per the `SkillInfo` contract. Tests must FAIL before the scanner is updated.
**Artifact**: `repositories/anton-abyzov/vskill/src/eval/__tests__/skill-scanner.multiFile.test.ts`
**Test command**: `npm test`

---

### T-006: GREEN — propagate new fields in skill-scanner.ts normalizer
**User Story**: US-001 | **Satisfies ACs**: AC-US1-04, AC-US1-06 | **Status**: [x] completed
**Test Plan**: Given the RED tests from T-005, when `skill-scanner.ts` `normalizeSkillInfo` is updated to propagate `secrets`, `runtime`, and `integrationTests`, then all T-005 tests pass. Full `npm test` suite shows no regressions against existing skills.
**Artifact**: `repositories/anton-abyzov/vskill/src/eval/skill-scanner.ts`
**Test command**: `npm test`

---

## US-002: Multi-file generation pipeline (5 parallel agents + sequential body)

### T-007: RED — agent-prompts parser unit tests
**User Story**: US-002 | **Satisfies ACs**: AC-US2-06 | **Status**: [x] completed
**Test Plan**: Given `src/core/__tests__/agent-prompts.test.ts`, when each of the four new parsers (`parseScriptResponse`, `parseGraderResponse`, `parseTestResponse`, `parseReferenceResponse`) is called with malformed JSON, then they throw a typed error matching the existing pattern. When called with valid JSON, they return the documented shape. Tests must FAIL before `agent-prompts.ts` exists.
**Artifact**: `repositories/anton-abyzov/vskill/src/core/__tests__/agent-prompts.test.ts`
**Test command**: `npm test`

---

### T-008: GREEN — create src/core/agent-prompts.ts with 4 prompts + parsers
**User Story**: US-002 | **Satisfies ACs**: AC-US2-06, AC-US2-03 | **Status**: [x] completed
**Test Plan**: Given the RED tests from T-007, when `src/core/agent-prompts.ts` exports `SCRIPT_SYSTEM_PROMPT`, `GRADER_SYSTEM_PROMPT`, `TEST_SYSTEM_PROMPT`, `REFERENCE_SYSTEM_PROMPT` as constants (not factory), plus `parseScriptResponse`, `parseGraderResponse`, `parseTestResponse`, `parseReferenceResponse` modeled on `parseBodyResponse`/`parseEvalsResponse`, then all T-007 tests pass. Sonnet model assigned for script/grader/test; Haiku for reference.
**Artifact**: `repositories/anton-abyzov/vskill/src/core/agent-prompts.ts`
**Test command**: `npm test`

---

### T-009: Extend GenerateSkillRequest / GenerateSkillResult types
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-05 | **Status**: [x] completed
**Test Plan**: Given the updated `skill-generator.ts` type definitions, when TypeScript compiles, then `GenerateSkillRequest` has optional `multiFile?: boolean` and `GenerateSkillResult` has optional `files?: Record<string, string>`, `secrets?`, `runtime?`, `integrationTests?`. Existing `body` and `evals` fields are unchanged.
**Artifact**: `repositories/anton-abyzov/vskill/src/core/skill-generator.ts` (type section only)
**Test command**: `npm test`

---

### T-010: RED — multi-file generator unit tests
**User Story**: US-002 | **Satisfies ACs**: AC-US2-02, AC-US2-03, AC-US2-04, AC-US2-07, AC-US2-08 | **Status**: [x] completed
**Test Plan**: Given `src/core/__tests__/skill-generator.multiFile.test.ts` mocking all 5 LLM clients, when `generateSkill({ multiFile: true, ... })` is called, then: (a) 5 fan-out calls fire before body-agent; (b) body-agent runs after `Promise.allSettled` resolves; (c) the produced file map matches the expected paths; (d) when one fan-out agent throws, body-agent still runs with the reduced filename list; (e) when `multiFile !== true`, the existing 2-call path is invoked unchanged. Tests must FAIL before the multi-file branch exists.
**Artifact**: `repositories/anton-abyzov/vskill/src/core/__tests__/skill-generator.multiFile.test.ts`
**Test command**: `npm test`

---

### T-011: GREEN — implement multiFile branch in generateSkill()
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04, AC-US2-07, AC-US2-08 | **Status**: [x] completed
**Test Plan**: Given the RED tests from T-010, when `generateSkill()` in `skill-generator.ts` is extended with the `multiFile` branch (5 `Promise.allSettled` calls then sequential body call with produced filename list), then all T-010 tests pass. `buildAgentAwareSystemPrompt()` is applied to all 5 agent prompts. Existing `multiFile !== true` path remains identical; no existing test breaks.
**Artifact**: `repositories/anton-abyzov/vskill/src/core/skill-generator.ts`
**Test command**: `npm test`

---

## US-003: Batch atomic file write in POST /api/skills/create

### T-012: Add resolveSafe() helper and buildEnvExample() to path-safety module
**User Story**: US-003 | **Satisfies ACs**: AC-US3-03, AC-US3-04 | **Status**: [x] completed
**Test Plan**: Given `resolveSafe(base, rel)`, when `rel` is `../../etc/passwd` or `/etc/passwd` or any path that resolves outside `base`, then the function throws. When `rel` is a normal relative path like `scripts/audit.py`, then it returns the safe absolute path. `buildEnvExample(secrets)` returns one `KEY=hint` line per secret, never emitting real values.
**Artifact**: `repositories/anton-abyzov/vskill/src/lib/path-safety.ts` (new) or inline helper in `skill-create-routes.ts`
**Test command**: `npm test`

---

### T-013: RED — skill-create-routes multi-file supertest
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04, AC-US3-05, AC-US3-06 | **Status**: [x] completed
**Test Plan**: Given `src/eval-server/__tests__/skill-create-routes.multiFile.test.ts` using supertest, when `POST /api/skills/create` is called with a `files` map containing a valid file, then all files are written to disk. When called with `../../etc/passwd` as a key, then 400 is returned. When called with an absolute path `/etc/passwd`, then 400 is returned. When a mid-write error is injected, then the skill directory is removed via `rmSync`. When `isUpdateMode` is true and a write fails, the directory is NOT removed. When `secrets` is non-empty, `.env.example` is written. Tests must FAIL before the route is extended.
**Artifact**: `repositories/anton-abyzov/vskill/src/eval-server/__tests__/skill-create-routes.multiFile.test.ts`
**Test command**: `npm test`

---

### T-014: GREEN — extend POST /api/skills/create with files map handling
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04, AC-US3-05, AC-US3-06 | **Status**: [x] completed
**Test Plan**: Given the RED tests from T-013, when `skill-create-routes.ts` is updated to accept `files?`, `secrets?`, `runtime?`, `integrationTests?` in `CreateSkillRequest`, loop `body.files` through `resolveSafe()`, write each file with `mkdirSync(dirname(safe), { recursive: true })`, write `.env.example` from `body.secrets`, and rollback with `rmSync` on error (unless `isUpdateMode`), then all T-013 tests pass.
**Artifact**: `repositories/anton-abyzov/vskill/src/eval-server/skill-create-routes.ts`
**Test command**: `npm test`

---

## US-004: vskill check <skill> preflight command

### T-015: RED — check command unit tests
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-04, AC-US4-05, AC-US4-06, AC-US4-07, AC-US4-08, AC-US4-09 | **Status**: [x] completed
**Test Plan**: Given `src/commands/__tests__/check.test.ts` with mocked `resolveAllCredentials`, mocked `MCP_REGISTRY`, and mocked `exec` for shell commands, when `checkCommand` is called with all env present and MCPs configured, then exit code is 0. When a required secret is missing, then exit code is 1. When only an unknown MCP (not in registry) is encountered, then exit code is 2. When `--json` is passed, then stdout is a valid JSON object with shape `{ skill, mcps, secrets, runtime, tests, exitCode }`. Secret values are never logged in any code path. Tests must FAIL before `check.ts` exists.
**Artifact**: `repositories/anton-abyzov/vskill/src/commands/__tests__/check.test.ts`
**Test command**: `npm test`

---

### T-016: GREEN — implement src/commands/check.ts
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-04, AC-US4-05, AC-US4-06, AC-US4-07, AC-US4-08, AC-US4-09 | **Status**: [x] completed
**Test Plan**: Given the RED tests from T-015, when `src/commands/check.ts` implements `checkCommand(skillName, opts)` reusing `resolveAllCredentials()` for secrets, `MCP_REGISTRY` for MCP lookup, shell exec for Python version validation, and `pytest --collect-only` for test collection, then all T-015 tests pass. Exit codes 0/1/2 are correct. `--json` flag emits the documented shape. Secret values are never echoed.
**Artifact**: `repositories/anton-abyzov/vskill/src/commands/check.ts`
**Test command**: `npm test`

---

### T-017: Register check command in src/index.ts
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01 | **Status**: [x] completed
**Test Plan**: Given the updated `src/index.ts`, when `vskill --help` is run after build, then `check <skill> [path]` appears in the command list immediately after `audit`. The dynamic-import pattern mirrors `audit` registration exactly. No existing commands are affected.
**Artifact**: `repositories/anton-abyzov/vskill/src/index.ts`
**Test command**: `npm test`

---

## US-005: stripe-refund-auditor fixture skill

### T-018: Create SKILL.md for stripe-refund-auditor
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01 | **Status**: [x] completed
**Test Plan**: Given `plugins/personal/skills/stripe-refund-auditor/SKILL.md`, when `lib/frontmatter.ts` parses it, then `secrets[0].name === "STRIPE_API_KEY"`, `runtime.python === ">=3.10"`, `integrationTests.runner === "pytest"`, `integrationTests.file === "tests/integration_test.py"`, and `mcpDeps` includes `stripe`.
**Artifact**: `repositories/anton-abyzov/vskill/plugins/personal/skills/stripe-refund-auditor/SKILL.md`
**Test command**: `npm test`

---

### T-019: Create scripts/audit.py
**User Story**: US-005 | **Satisfies ACs**: AC-US5-02 | **Status**: [x] completed
**Test Plan**: Given `scripts/audit.py`, when it is imported with no env vars set, then it does not crash or raise an exception on import. When `STRIPE_API_KEY` is not set, `os.environ.get("STRIPE_API_KEY")` returns `None` and the script degrades gracefully (exits with a clear message, no unhandled exception).
**Artifact**: `repositories/anton-abyzov/vskill/plugins/personal/skills/stripe-refund-auditor/scripts/audit.py`
**Test command**: `python3 -c "import importlib.util; spec=importlib.util.spec_from_file_location('audit','scripts/audit.py')"` (manual in fixture dir)

---

### T-020: Create scripts/grader.py
**User Story**: US-005 | **Satisfies ACs**: AC-US5-03 | **Status**: [x] completed
**Test Plan**: Given `scripts/grader.py`, when its grader function is called with a known input shape (a list of mock refund records with anomaly counts), then it returns a deterministic numeric score between 0 and 1. No network calls are made.
**Artifact**: `repositories/anton-abyzov/vskill/plugins/personal/skills/stripe-refund-auditor/scripts/grader.py`
**Test command**: Manual: `python3 -c "from grader import grade; assert isinstance(grade([]), float)"` in scripts dir

---

### T-021: Create tests/integration_test.py
**User Story**: US-005 | **Satisfies ACs**: AC-US5-04 | **Status**: [x] completed
**Test Plan**: Given `tests/integration_test.py`, when `python3 -m pytest --collect-only` is run with no env vars, then the test is collected without error. When run without `STRIPE_API_KEY`, then the test is skipped via `pytest.skip`. The test file contains no real API key values.
**Artifact**: `repositories/anton-abyzov/vskill/plugins/personal/skills/stripe-refund-auditor/tests/integration_test.py`
**Test command**: `python3 -m pytest --collect-only tests/` (manual in fixture dir)

---

### T-022: Create references/refund-schema.md
**User Story**: US-005 | **Satisfies ACs**: AC-US5-05 | **Status**: [x] completed
**Test Plan**: Given `references/refund-schema.md`, when a developer reads it, then it documents the Stripe Refund object fields used by `scripts/audit.py` (id, amount, currency, status, reason, metadata) with their types and descriptions.
**Artifact**: `repositories/anton-abyzov/vskill/plugins/personal/skills/stripe-refund-auditor/references/refund-schema.md`
**Test command**: Artifact presence check (`ls references/`)

---

### T-023: Create evals/evals.json
**User Story**: US-005 | **Satisfies ACs**: AC-US5-06 | **Status**: [x] completed
**Test Plan**: Given `evals/evals.json`, when parsed as JSON, then it contains 3-5 eval cases each with `id`, `input`, `expected`, and `grader` fields following the existing `IntegrationEvalCase` shape from `integration-types.ts`. No real secret values appear in the file.
**Artifact**: `repositories/anton-abyzov/vskill/plugins/personal/skills/stripe-refund-auditor/evals/evals.json`
**Test command**: `node -e "const d=JSON.parse(require('fs').readFileSync('evals/evals.json','utf8'));console.assert(d.length>=3)"` (manual in fixture dir)

---

### T-024: Create .env.example
**User Story**: US-005 | **Satisfies ACs**: AC-US5-07 | **Status**: [x] completed
**Test Plan**: Given `.env.example`, when its content is inspected, then it contains `STRIPE_API_KEY=sk_test_...` with a placeholder value and no real secret. The file has exactly one non-comment line matching the `SKILL.md` secrets declaration.
**Artifact**: `repositories/anton-abyzov/vskill/plugins/personal/skills/stripe-refund-auditor/.env.example`
**Test command**: Artifact presence check; manual grep for no real keys

---

### T-025: RED — vskill check stripe-fixture vitest test
**User Story**: US-005 | **Satisfies ACs**: AC-US5-08 | **Status**: [x] completed
**Test Plan**: Given `src/commands/__tests__/check.stripe-fixture.test.ts` with mocked env, when `checkCommand("stripe-refund-auditor")` is invoked with no `STRIPE_API_KEY`, then exit code is 1 and the secrets result includes `{ name: "STRIPE_API_KEY", status: "missing" }`. When `STRIPE_API_KEY=sk_test_dummy` is in env, then `secrets[0].status === "ready"` and secret value is never present in any log output. Tests must FAIL before the fixture is wired to the check command path.
**Artifact**: `repositories/anton-abyzov/vskill/src/commands/__tests__/check.stripe-fixture.test.ts`
**Test command**: `npm test`

---

### T-026: GREEN — wire stripe-refund-auditor fixture into check command path
**User Story**: US-005 | **Satisfies ACs**: AC-US5-08 | **Status**: [x] completed
**Test Plan**: Given the RED tests from T-025, when the fixture is discovered via the skill-scanner path and `check.ts` resolves its path correctly, then T-025 tests pass. Running `node dist/bin.js check stripe-refund-auditor` (after build) with no env exits 1 and prints "STRIPE_API_KEY: missing". With `STRIPE_API_KEY=sk_test_dummy`, the secrets row shows ready status.
**Artifact**: Wiring in `check.ts` skill-path resolution (no new file if scanner already discovers the fixture)
**Test command**: `npm test`

---

## Integration gates

### T-027: Vitest suite green — schema layer (US-001 gate)
**User Story**: US-001 | **Satisfies ACs**: AC-US1-06 | **Status**: [x] completed
**Test Plan**: Given all T-001..T-006 complete, when `npm test` is run from `repositories/anton-abyzov/vskill/`, then 0 tests fail and existing skills including `obsidian-brain` parse without errors.
**Test command**: `npm test`

---

### T-028: Vitest suite green — generator layer (US-002 gate)
**User Story**: US-002 | **Satisfies ACs**: AC-US2-08 | **Status**: [x] completed
**Test Plan**: Given all T-007..T-011 complete, when `npm test` is run, then all agent-prompts and skill-generator.multiFile tests pass. The existing 2-call path tests remain green.
**Test command**: `npm test`

---

### T-029: Vitest suite green — route layer (US-003 gate)
**User Story**: US-003 | **Satisfies ACs**: AC-US3-06 | **Status**: [x] completed
**Test Plan**: Given all T-012..T-014 complete, when `npm test` is run, then all skill-create-routes.multiFile supertest cases pass: happy path, path-traversal 400s, rollback on partial failure, update-mode preservation, and `.env.example` emission.
**Test command**: `npm test`

---

### T-030: Vitest suite green — check command (US-004 gate)
**User Story**: US-004 | **Satisfies ACs**: AC-US4-09 | **Status**: [x] completed
**Test Plan**: Given all T-015..T-017 complete, when `npm test` is run, then all `check.test.ts` and `check.stripe-fixture.test.ts` cases pass with exit codes 0/1/2 correct and no secret values logged.
**Test command**: `npm test`

---

### T-031: npm run build — TypeScript compilation clean
**User Story**: US-001, US-002, US-003, US-004 | **Satisfies ACs**: AC-US1-01, AC-US2-01, AC-US3-01, AC-US4-01 | **Status**: [x] completed
**Test Plan**: Given all T-001..T-026 complete, when `npm run build` is run from `repositories/anton-abyzov/vskill/`, then it exits 0 with no TypeScript errors and produces `dist/bin.js`.
**Artifact**: `repositories/anton-abyzov/vskill/dist/bin.js`
**Test command**: `npm run build`

---

### T-032: Manual E2E — vskill check stripe-refund-auditor (no env then with env)
**User Story**: US-004, US-005 | **Satisfies ACs**: AC-US4-07, AC-US5-08 | **Status**: [x] completed
**Test Plan**: Given the built binary from T-031, when `node dist/bin.js check stripe-refund-auditor` is run with no `STRIPE_API_KEY`, then exit code 1 and output contains "STRIPE_API_KEY: missing". When `STRIPE_API_KEY=sk_test_dummy node dist/bin.js check stripe-refund-auditor --json` is run, then JSON output has `secrets[0].status = "ready"` and exit code is still 1 (MCP not configured).
**Test command**: `node dist/bin.js check stripe-refund-auditor` (in `repositories/anton-abyzov/vskill/`)

---

### T-033: Manual E2E — studio multiFile generation and create
**User Story**: US-002, US-003 | **Satisfies ACs**: AC-US2-02, AC-US3-02 | **Status**: [x] completed
**Test Plan**: Given the running studio (`node dist/bin.js studio --port 3077`), when `POST /api/skills/generate` is called with `{ "prompt": "...", "multiFile": true }`, then the response includes a `files` map with at least `scripts/audit.py`, `tests/integration_test.py`, `references/refund-schema.md`, and `evals/evals.json`. When the result is then posted to `POST /api/skills/create`, then all files land on disk under the skill directory.
**Test command**: `curl -X POST http://localhost:3077/api/skills/generate -d '{"prompt":"...","multiFile":true}'` (manual)
