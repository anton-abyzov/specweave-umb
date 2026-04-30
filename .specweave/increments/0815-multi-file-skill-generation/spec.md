---
increment: 0815-multi-file-skill-generation
title: Multi-file skill generation with parallel sub-agents
type: feature
priority: P1
status: completed
created: 2026-04-30T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 95
---

# Feature: Multi-file skill generation with parallel sub-agents

## Problem statement

Skill Studio currently produces only two files per skill (`SKILL.md` + `evals/evals.json`) via two parallel LLM calls in `generateSkill()`. Real-world skills need deterministic Python helpers, JSON config, graders, runnable integration tests, references, and `.env.example` for declared secrets — none of which the existing pipeline can produce. Some infrastructure already exists (`IntegrationEvalCase` with `requiredCredentials`, `resolveAllCredentials()`, `IntegrationRunner`, the MCP registry, and `mcpDeps?: string[]` on `SkillInfo`), but the manifest has no top-level `secrets[]` or `runtime` declaration, the generator doesn't fan out to per-file agents, `POST /api/skills/create` cannot accept arbitrary auxiliary files, no preflight `vskill check` command exists, and there is no fixture skill demonstrating end-to-end multi-file output. This increment closes that gap with an opt-in `multiFile: true` path that fans out 5 parallel LLM calls plus a sequential body-agent, accepts a batch `files` map on the create endpoint with path-traversal hardening, ships a `vskill check` preflight command, and lands `stripe-refund-auditor` as the worked-example fixture proving the contract end to end.

## User Stories

### US-001: Manifest schema extension (backwards-compatible) (P1)
**Project**: vskill

**As a** skill author
**I want** the SKILL.md frontmatter to declare top-level `secrets`, `runtime`, and `integrationTests` blocks
**So that** generated skills can describe their credential requirements, language runtime, and integration test contract in one place — without breaking existing skills that omit these fields.

**Acceptance Criteria**:
- [x] **AC-US1-01**: `SkillInfo` (in `src/eval-ui/src/types.ts`) gains optional `secrets?: Array<{ name: string; purpose: string; test_value_hint?: string }>`, `runtime?: { python?: string; pip?: string[]; node?: string }`, and `integrationTests?: { runner: 'vitest' | 'pytest' | 'none'; file?: string; requires?: string[] }` fields. All three are optional.
- [x] **AC-US1-02**: The frontmatter parser at `src/lib/frontmatter.ts` reads the new top-level fields when present and returns `undefined` for each when absent. Existing fields (`name`, `description`, `version`, `mcpDeps`, etc.) are unchanged.
- [x] **AC-US1-03**: The installer-side parser at `src/installer/frontmatter.ts` mirrors the read behavior so installed skills round-trip the new fields correctly.
- [x] **AC-US1-04**: `src/eval/skill-scanner.ts` propagates the three new fields when normalizing scanned skills into `SkillInfo`. Skills without these fields scan unchanged (no schema regression).
- [x] **AC-US1-05**: A unit test fixture exercises both the presence and absence of `secrets`, `runtime`, and `integrationTests` in frontmatter and asserts the parser output for each case (covers backwards compatibility).
- [x] **AC-US1-06**: Existing skills (e.g. `obsidian-brain`) parse without errors after the schema change — verified by running the full vitest suite with no regressions.

---

### US-002: Multi-file generation pipeline (5 parallel agents + sequential body) (P1)
**Project**: vskill

**As a** Skill Studio user
**I want** to opt into `multiFile: true` on `GenerateSkillRequest` and receive a multi-file skill bundle
**So that** a single prompt produces `SKILL.md`, `scripts/*.py`, `tests/integration_test.py`, `references/*.md`, `evals/evals.json`, and `.env.example` in one shot, with `SKILL.md` correctly linking to the produced filenames.

**Acceptance Criteria**:
- [x] **AC-US2-01**: `GenerateSkillRequest` accepts an optional `multiFile?: boolean` flag. When `multiFile !== true`, the existing dual-LLM path (Sonnet body + Haiku evals) runs unchanged with no behavioral difference for existing callers.
- [x] **AC-US2-02**: When `multiFile === true`, `generateSkill()` fans out **5 LLM calls in parallel** via `Promise.allSettled` — `script-agent`, `grader-agent`, `test-agent`, `reference-agent`, `eval-agent` — each producing a JSON-shaped output validated against a per-role parser.
- [x] **AC-US2-03**: `script-agent`, `grader-agent`, and `test-agent` use Sonnet via `createLlmClient()`; `reference-agent` and `eval-agent` use Haiku for cost mitigation.
- [x] **AC-US2-04**: After `Promise.allSettled` resolves, `body-agent` runs **sequentially last** with the produced filename list as input, so `SKILL.md` references resolve. If a fan-out agent fails, `body-agent` receives the actual produced filename list and missing files become generic references (e.g. "see `references/` directory") rather than broken links.
- [x] **AC-US2-05**: `GenerateSkillResult` gains an optional `files?: Record<string, string>` map (relative path → contents) plus optional `secrets`, `runtime`, `integrationTests` blocks matching the US-001 schema. The existing `body` and `evals` fields are unchanged.
- [x] **AC-US2-06**: New per-role system prompts and JSON parsers live in `src/core/agent-prompts.ts`. Each parser rejects malformed JSON with a typed error matching the existing `parseBodyResponse` / `parseEvalsResponse` pattern.
- [x] **AC-US2-07**: All 5 fan-out agents and the body-agent receive `buildAgentAwareSystemPrompt()` augmentation so target-agent constraints apply uniformly across the bundle.
- [x] **AC-US2-08**: Vitest test mocks all 5 LLM clients and asserts: (a) `Promise.allSettled` fan-out behavior, (b) body-agent runs after the fan-out completes, (c) the produced file map matches the expected paths, (d) partial-failure path leaves body-agent with the actual filename subset.

---

### US-003: Batch atomic file write in `POST /api/skills/create` with path-traversal hardening (P1)
**Project**: vskill

**As a** Skill Studio backend
**I want** `POST /api/skills/create` to accept a `files: Record<string, string>` map plus the new manifest blocks and write everything atomically with path-safety enforcement
**So that** generated multi-file bundles land on disk safely, no path traversal is possible, and a partial failure doesn't leave half a skill on disk.

**Acceptance Criteria**:
- [x] **AC-US3-01**: `CreateSkillRequest` (in `src/eval-server/skill-create-routes.ts`) accepts optional `files?: Record<string, string>`, `secrets?`, `runtime?`, and `integrationTests?` matching the US-001 schema. Existing fields (`name`, `body`, `evals`, etc.) are unchanged.
- [x] **AC-US3-02**: After the existing `SKILL.md` and `evals.json` writes succeed, the route iterates `body.files ?? {}` and writes each entry. `mkdirSync(dirname(safePath), { recursive: true })` ensures parent directories exist before each `writeFileSync`.
- [x] **AC-US3-03**: A new `resolveSafe(targetDir, relPath)` helper rejects any `relPath` that is absolute (e.g. `/etc/passwd`), contains `..` segments that escape `targetDir`, or otherwise resolves outside `targetDir`. Rejection produces a 400 response.
- [x] **AC-US3-04**: When `body.secrets?.length > 0`, the route writes `.env.example` at the target directory root with one `KEY=` line per secret using `buildEnvExample(body.secrets)`. Real secret values are never written — only placeholders or `test_value_hint` if present.
- [x] **AC-US3-05**: Atomicity: if any write inside the batch fails, the entire `targetDir` is removed via `rmSync(targetDir, { recursive: true, force: true })` — **except** when `isUpdateMode` is true (updates must not destroy existing skill content).
- [x] **AC-US3-06**: Supertest integration test exercises: (a) successful multi-file write, (b) path-traversal attempt with `../../etc/passwd` returns 400, (c) path-traversal attempt with absolute path returns 400, (d) partial-failure rollback removes the entire skill directory in create mode but preserves content in update mode.

---

### US-004: `vskill check <skill>` preflight command (P1)
**Project**: vskill

**As a** skill operator about to run a skill
**I want** a preflight `vskill check stripe-refund-auditor` command
**So that** I can verify all declared MCPs are configured, all declared secrets are resolvable, the declared Python runtime exists, and the declared pytest file collects — before discovering the gap mid-run.

**Acceptance Criteria**:
- [x] **AC-US4-01**: A new `src/commands/check.ts` implements `checkCommand(skillName, opts)` and `src/index.ts` registers `program.command("check <skill> [path]")` following the existing commander.js dynamic-import pattern that `audit` uses.
- [x] **AC-US4-02**: The command loads the target skill's frontmatter via `lib/frontmatter.ts`. If the skill cannot be located, exit code is 1 with a clear "skill not found" message.
- [x] **AC-US4-03**: For each entry in `mcpDeps[]`, the command queries `MCP_REGISTRY` from `src/eval/mcp-detector.ts`, checks `~/.claude/mcp.json` and project-local `.claude/mcp.json`, and reports per-MCP `configured` / `not configured` / `unknown MCP` status. Unknown MCPs (not in registry) produce a warning, not a hard failure.
- [x] **AC-US4-04**: For each entry in `secrets[]`, the command calls `resolveAllCredentials()` (from `src/eval/credential-resolver.ts`) and reports per-secret `ready` (resolved from env or `.env.local`) / `missing`. **Secret values are never echoed** — only presence/absence.
- [x] **AC-US4-05**: When `runtime.python` is declared, the command runs `which python3 && python3 --version` and validates the installed version against the declared spec (e.g. `>=3.10`). Missing or wrong-version Python reports a failure.
- [x] **AC-US4-06**: When `integrationTests.runner === "pytest"`, the command runs `python3 -m pytest --collect-only` against `integrationTests.file` and reports collection success/failure. A pytest collection error counts as a failure.
- [x] **AC-US4-07**: Exit codes: `0` all green, `1` any required item missing (secret missing, MCP not configured, Python missing/wrong version, pytest collection failed), `2` partial — only soft warnings (e.g. unknown MCP).
- [x] **AC-US4-08**: A `--json` flag emits machine-readable output with shape `{ skill, mcps: [...], secrets: [...], runtime: {...}, tests: {...}, exitCode }` instead of human-readable lines.
- [x] **AC-US4-09**: Vitest test covers: (a) green path with all env present and MCPs configured, (b) red path with missing secret → exit 1, (c) warning path with unknown MCP → exit 2, (d) `--json` output shape, (e) reused secrets are read but never logged in any code path.

---

### US-005: `stripe-refund-auditor` fixture skill (worked example) (P1)
**Project**: vskill

**As a** SpecWeave/vskill developer
**I want** a worked-example fixture skill at `repositories/anton-abyzov/vskill/plugins/personal/skills/stripe-refund-auditor/`
**So that** the multi-file pipeline has a concrete reference proving end-to-end output (Python script + grader + pytest + reference + evals + .env.example + MCP-aware SKILL.md) and `vskill check` has a real target.

**Acceptance Criteria**:
- [x] **AC-US5-01**: `stripe-refund-auditor/SKILL.md` declares frontmatter with `secrets: [STRIPE_API_KEY]`, `runtime: { python: ">=3.10", pip: ["stripe>=8", "pydantic>=2"] }`, `integrationTests: { runner: "pytest", file: "tests/integration_test.py", requires: ["STRIPE_API_KEY"] }`, and `mcpDeps: [...]` per the schema in US-001.
- [x] **AC-US5-02**: `scripts/audit.py` is a runnable Python module that pulls refunds and detects anomalies. It uses `os.environ.get("STRIPE_API_KEY")` and degrades gracefully (no crash) when the env var is missing.
- [x] **AC-US5-03**: `scripts/grader.py` is a deterministic numeric grader suitable for integration eval cases — pure-function, no network calls, returns a numeric score against a known input shape.
- [x] **AC-US5-04**: `tests/integration_test.py` is a pytest module that calls `pytest.skip("STRIPE_API_KEY not set")` when the secret is absent and otherwise exercises the audit script against Stripe test mode (or mocked Stripe). Tests demonstrate the contract; the actual Stripe API calls are mocked or use test-mode keys only.
- [x] **AC-US5-05**: `references/refund-schema.md` documents the Stripe Refund object reference used by the script.
- [x] **AC-US5-06**: `evals/evals.json` contains 3-5 LLM-judged behavioral cases following the existing eval format consumed by `IntegrationRunner`.
- [x] **AC-US5-07**: `.env.example` ships at the skill root with `STRIPE_API_KEY=sk_test_...` placeholder. **No real secret values are committed** to the repository at any point.
- [x] **AC-US5-08**: Running `vskill check stripe-refund-auditor` against the fixture with no env returns exit 1 reporting "STRIPE_API_KEY: missing". With `STRIPE_API_KEY=sk_test_dummy` set in env, the secrets row turns green (MCP-related failures may remain depending on local MCP config). A vitest fixture test asserts both the red and green paths via mocked env.

---

## Out of Scope

- Replacing the existing dual-LLM path — `multiFile` is opt-in; the current 2-file path remains the default with no behavior change for existing callers.
- Shipping production-grade Stripe integration logic — `stripe-refund-auditor` is a fixture/demo, not a real auditor for production refund flows.
- Auto-installing MCP servers if missing — `vskill check` only reports presence/absence; remediation remains the operator's responsibility.
- Auto-running `pip install` when `runtime.pip` is declared — `vskill check` only validates that the declared Python version is present, not that pip dependencies are installed.
- Streaming progress UI for the 5 fan-out agents in the Studio frontend — server-side fan-out is sufficient for v1; a streaming UI is a follow-up increment.

## Risks + Mitigations

| Risk | Mitigation |
|---|---|
| 5 parallel LLM calls = high cost | `reference-agent` and `eval-agent` pinned to Haiku (~10x cheaper than Sonnet); `multiFile` is opt-in so default callers see no cost change |
| Path traversal via the `files` map | `resolveSafe()` helper rejects `..` segments and absolute paths; supertest covers malicious inputs (AC-US3-03, AC-US3-06) |
| Body-agent emits wrong filenames if a fan-out agent fails | Body-agent receives the **actual** produced filename list (post-`Promise.allSettled`); missing files become generic "see `references/` directory" references rather than broken links (AC-US2-04) |
| Stripe API dependency in fixture tests | Tests are pytest-marked `skip` without `STRIPE_API_KEY`; default CI path skips them, no Stripe network calls needed (AC-US5-04) |
| Frontmatter additions break existing scanners | All three new fields (`secrets`, `runtime`, `integrationTests`) are optional; scanner test fixtures cover both presence and absence; existing skills like `obsidian-brain` parse unchanged (AC-US1-05, AC-US1-06) |
| Update mode wiping user-edited files via batch rollback | Atomic `rmSync` rollback fires only when `isUpdateMode === false`; in update mode, partial writes remain on disk for the user to reconcile (AC-US3-05) |
| Secrets accidentally logged or written | `.env.example` ships placeholders only; `vskill check` reports presence/absence and never echoes values; `resolveCredential()` reads but never logs (AC-US3-04, AC-US4-04, AC-US4-09) |

## Dependencies

- Existing `IntegrationEvalCase` type at `src/eval/integration-types.ts`
- Existing `resolveAllCredentials()` chain at `src/eval/credential-resolver.ts`
- Existing `MCP_REGISTRY` + `buildConfigSnippet()` at `src/eval/mcp-detector.ts`
- Existing `createLlmClient()` at `src/eval/llm.ts`
- Existing `buildAgentAwareSystemPrompt()` at `src/eval-server/skill-create-routes.ts`
- Existing commander.js + dynamic-import pattern at `src/index.ts` (mirrors `audit` registration)
