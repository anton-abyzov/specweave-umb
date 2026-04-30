# Implementation Plan: Multi-file skill generation with parallel sub-agents

## Overview

Skill Studio's `generateSkill()` currently fans out exactly two LLM calls (Sonnet body + Haiku evals) and emits two files: `SKILL.md` and `evals/evals.json`. Real-world skills also need deterministic Python helpers, JSON config, graders, runnable integration tests, references, and an `.env.example` matching declared secrets. The supporting infrastructure is already in place — `IntegrationEvalCase.requiredCredentials[]`, `resolveAllCredentials()`, the `MCP_REGISTRY` and `IntegrationRunner` 5-phase pipeline — but the generator never reaches it and the manifest contract has no top-level `secrets[]` or `runtime` declaration.

This increment adds a backwards-compatible `multiFile: true` opt-in that fans `generateSkill()` out to **5 parallel sub-agents** (script, grader, test, reference, eval) via `Promise.allSettled`, then runs the body agent **last** so the produced filenames can be referenced from `SKILL.md`. The schema is extended with three optional fields (`secrets`, `runtime`, `integrationTests`); `POST /api/skills/create` accepts an arbitrary `files: Record<string, string>` map with a `resolveSafe()` traversal guard; a new `vskill check <skill>` preflight command verifies declared MCPs and secrets before a run; and `stripe-refund-auditor` lands as the worked fixture proving the contract end-to-end.

```
                         ┌── script-agent     → scripts/audit.py             (Sonnet)
                         ├── grader-agent     → scripts/grader.py            (Sonnet)
generateSkill ───────────┼── test-agent       → tests/integration_test.py    (Sonnet)
  (multiFile === true)   ├── reference-agent  → references/*.md              (Haiku)
                         └── eval-agent       → evals/evals.json             (Haiku, existing path)
                                       ↓
                              Promise.allSettled
                                       ↓
                         body-agent (sequential, sees produced filenames)    (Sonnet)
                                       ↓
                         merge → GenerateSkillResult { files, secrets, runtime, integrationTests }
```

The existing 2-call path (`multiFile !== true`) is untouched — pure additive change, no behavior shift for any current caller.

## Architecture

### Components

| Component | Purpose |
|---|---|
| **Manifest schema** (`SkillInfo`, frontmatter parsers, scanner) | Adds optional top-level `secrets[]`, `runtime`, `integrationTests` fields. All `?`/`null` to keep the existing path unchanged. |
| **`generateSkill()` multi-file branch** (`skill-generator.ts`) | New `multiFile` branch that fans out 5 LLM calls in parallel via `Promise.allSettled`, then runs body sequentially with the produced filename list injected into its prompt. |
| **Per-role agent prompts** (new `core/agent-prompts.ts`) | Houses 4 new system prompts (`SCRIPT_SYSTEM_PROMPT`, `GRADER_SYSTEM_PROMPT`, `TEST_SYSTEM_PROMPT`, `REFERENCE_SYSTEM_PROMPT`) + JSON parsers modeled on existing `parseBodyResponse` / `parseEvalsResponse`. |
| **`POST /api/skills/create` extension** (`skill-create-routes.ts`) | Accepts `files: Record<string, string>`, `secrets[]`, `runtime`, `integrationTests` blocks. Uses `resolveSafe()` to reject `..` and absolute paths. On error, `rmSync` the partial directory unless `isUpdateMode`. |
| **`vskill check <skill>`** (new `commands/check.ts` + `index.ts` registration) | Preflight that loads frontmatter, calls `resolveAllCredentials()`, checks `MCP_REGISTRY`, validates Python runtime if declared, optionally collects pytest. Exit codes 0/1/2 + `--json` flag. |
| **Fixture skill** (new `plugins/personal/skills/stripe-refund-auditor/`) | Worked example with all 6 file types — `SKILL.md`, `scripts/audit.py`, `scripts/grader.py`, `references/refund-schema.md`, `tests/integration_test.py`, `evals/evals.json`, `.env.example`. |

### Schema contract — frontmatter additions

All new fields are **optional** to preserve the existing 2-file path. Mirror the same shape across `SkillInfo` (TS), `lib/frontmatter.ts` parser, `installer/frontmatter.ts`, and `eval/skill-scanner.ts` normalization.

```yaml
# SKILL.md frontmatter — new top-level fields (all optional)
secrets:
  - name: STRIPE_API_KEY
    purpose: List refunds via API
    test_value_hint: sk_test_*
runtime:
  python: ">=3.10"
  pip: [stripe>=8, pydantic>=2]
integrationTests:
  runner: pytest                # vitest | pytest | none
  file: tests/integration_test.py
  requires: [STRIPE_API_KEY]
```

```ts
// types.ts — additions to SkillInfo
export interface SkillSecret {
  name: string;
  purpose: string;
  test_value_hint?: string | null;
}

export interface SkillRuntime {
  python?: string | null;        // semver range, e.g. ">=3.10"
  node?: string | null;
  pip?: string[] | null;
  npm?: string[] | null;
}

export interface SkillIntegrationTests {
  runner: "vitest" | "pytest" | "none";
  file: string;                  // relative to skill dir
  requires?: string[] | null;    // secret names that must be present
}

export interface SkillInfo {
  // ...existing fields...
  secrets?: SkillSecret[] | null;
  runtime?: SkillRuntime | null;
  integrationTests?: SkillIntegrationTests | null;
}
```

```ts
// skill-generator.ts — extension to GenerateSkillRequest / Result
export interface GenerateSkillRequest {
  // ...existing fields...
  multiFile?: boolean;
}

export interface GenerateSkillResult {
  // ...existing fields (body, evals, warning)...
  files?: Record<string, string>;          // relPath → contents (only when multiFile)
  secrets?: SkillSecret[];
  runtime?: SkillRuntime;
  integrationTests?: SkillIntegrationTests;
}
```

```ts
// skill-create-routes.ts — extension to CreateSkillRequest body
interface CreateSkillRequestBody {
  // ...existing fields...
  files?: Record<string, string>;
  secrets?: SkillSecret[];
  runtime?: SkillRuntime;
  integrationTests?: SkillIntegrationTests;
}
```

## File-by-file change list

| File | Change |
|---|---|
| `repositories/anton-abyzov/vskill/src/eval-ui/src/types.ts` (line 119+) | Extend `SkillInfo` with optional `secrets[]`, `runtime`, `integrationTests`. Export new `SkillSecret`, `SkillRuntime`, `SkillIntegrationTests` interfaces. |
| `repositories/anton-abyzov/vskill/src/lib/frontmatter.ts` | Parse the new top-level YAML keys; emit `null` when absent. Preserve existing field handling unchanged. |
| `repositories/anton-abyzov/vskill/src/installer/frontmatter.ts` | Mirror the same parser additions on the install path. |
| `repositories/anton-abyzov/vskill/src/eval/skill-scanner.ts` | Propagate the three new fields through `normalizeSkillInfo` so `/api/skills` clients see them. |
| `repositories/anton-abyzov/vskill/src/core/skill-generator.ts` (line 92-164) | Add `multiFile` branch: 5 `Promise.allSettled` calls (script/grader/test/reference + existing eval) → body call sequential with produced filenames in prompt → return extended `GenerateSkillResult`. Existing path untouched. |
| **New**: `repositories/anton-abyzov/vskill/src/core/agent-prompts.ts` | Four system prompts + four JSON response parsers (`parseScriptResponse`, `parseGraderResponse`, `parseTestResponse`, `parseReferenceResponse`). Modeled on `parseBodyResponse` / `parseEvalsResponse`. |
| `repositories/anton-abyzov/vskill/src/eval-server/skill-create-routes.ts` (line 1297-1340) | After `mkdirSync` + `SKILL.md` + `evals.json`, loop `body.files` through new `resolveSafe(targetDir, relPath)` helper + `mkdirSync(dirname(safe))` + `writeFileSync`. Write `.env.example` from `body.secrets`. On any error inside the try, `rmSync(targetDir, { recursive: true })` unless `isUpdateMode`. |
| **New helper** in `skill-create-routes.ts` (or `lib/path-safety.ts`) | `resolveSafe(base, rel)` that rejects absolute paths, `..` segments, and any resolved path outside `base`. `buildEnvExample(secrets)` formats the file. |
| **New**: `repositories/anton-abyzov/vskill/src/commands/check.ts` | `checkCommand(skillName, opts)` — load frontmatter, run MCP registry check, secrets check via `resolveAllCredentials()`, Python version check if `runtime.python`, pytest collect-only if `integrationTests.runner === "pytest"`. Exit 0 (all green) / 1 (any missing) / 2 (warnings). `--json` flag. |
| `repositories/anton-abyzov/vskill/src/index.ts` (line 184 pattern) | Register `program.command("check <skill> [path]")` with `--json` option, dynamic-import `./commands/check.js`. Mirror `audit` registration. |
| **New fixture**: `repositories/anton-abyzov/vskill/plugins/personal/skills/stripe-refund-auditor/` | Worked end-to-end example (see Fixture section below). |

## Files to reuse (do not duplicate)

- **`resolveAllCredentials()`** at `repositories/anton-abyzov/vskill/src/eval/credential-resolver.ts:52` — secret resolution chain (env → `.env.local`). The `check` command consumes this directly; do not re-implement.
- **`MCP_REGISTRY`** + **`buildConfigSnippet()`** at `repositories/anton-abyzov/vskill/src/eval/mcp-detector.ts:35` and `:107` — registry of known MCPs. The `check` command queries this for declared `mcpDeps[]`.
- **`IntegrationEvalCase`** at `repositories/anton-abyzov/vskill/src/eval/integration-types.ts:40-50` — already has `requiredCredentials?: string[]`. The test-agent emits this shape directly.
- **`parseBodyResponse` / `parseEvalsResponse`** patterns in `repositories/anton-abyzov/vskill/src/core/skill-generator.ts:139-146` — model the four new agent parsers on these (extract JSON from text, strip `---REASONING---` trailer).
- **`createLlmClient`** in `repositories/anton-abyzov/vskill/src/eval/llm.ts` — provider-aware client. Each new agent calls this with its own `{ provider, model }` (script/grader/test → Sonnet; reference → Haiku; eval already on Haiku).
- **`buildAgentAwareSystemPrompt`** in `repositories/anton-abyzov/vskill/src/eval-server/skill-create-routes.ts:938` — applies target-agent constraints. Apply to all 5 prompts identically to the existing body call at `skill-generator.ts:131`.
- **`detectProjectLayout`** + **`existingPlugins`** discovery at `skill-generator.ts:117-124` — reuse so multi-file skills still get plugin context injected into prompts.

## Sequencing / build order

Strictly bottom-up — schema before generator, generator before route, route before CLI, CLI before fixture, fixture before manual E2E.

1. **Schema layer** — `types.ts` interfaces, both `frontmatter.ts` parsers, `skill-scanner.ts` normalizer. Vitest fixtures cover presence + absence of every new field.
2. **`agent-prompts.ts`** — four system prompts + four JSON parsers. Vitest covers schema rejection on malformed JSON before the generator wires them up.
3. **`generateSkill()` multi-file branch** — adds the `multiFile` request flag, the 5-way `Promise.allSettled`, the sequential body call. Vitest mocks the LLM client to assert fan-out shape and result-merging behavior.
4. **`POST /api/skills/create` files-map handling** — adds `resolveSafe()`, `.env.example` emission, atomic rollback. Vitest + supertest covers the happy path, path-traversal rejection, and rollback on partial-write failure.
5. **`vskill check` command** — registered in `index.ts`, implemented in `commands/check.ts`. Vitest covers exit codes 0/1/2 against fixture skills with mocked env.
6. **`stripe-refund-auditor` fixture** — landed by hand to prove the manifest contract round-trips through `check`. Pytest layer uses `pytest.skip` when `STRIPE_API_KEY` is absent so CI without Python remains green.
7. **Manual E2E** — `npm run build` → `npm test` → `node dist/bin.js check stripe-refund-auditor` (red) → set env, re-check (partial green) → studio fan-out via `POST /api/skills/generate` with `multiFile: true`.

Each step lands its tests before the next step begins. The `multiFile` flag is **opt-in** at every layer — generator default is `false`, route default ignores `files` if absent, scanner emits `null` for missing fields. No existing test should break.

## Test strategy

All new TypeScript code uses **vitest** (`npm test` is the existing runner). Pytest tests inside the fixture use `pytest.skip` paths when `STRIPE_API_KEY` is missing so CI without Python doesn't break.

### Unit + integration tests (vitest)

| Test file | Coverage |
|---|---|
| `src/core/__tests__/skill-generator.multiFile.test.ts` | Mock all 5 LLM clients. Assert: `Promise.allSettled` runs 5 in parallel; body-agent runs **after** the others; produced filenames are injected into the body prompt; one failed sub-agent does not abort the result; `multiFile !== true` path is identical to today. |
| `src/core/__tests__/agent-prompts.test.ts` | Each of the 4 new parsers rejects malformed JSON, missing required fields, and trailing junk. Happy-path emits the documented shape. |
| `src/eval-server/__tests__/skill-create-routes.multiFile.test.ts` | Supertest `POST /api/skills/create` with `files` map → assert all files written; with `..` or absolute path → assert 400; with mid-write throw → assert directory rolled back via `rmSync`; with `secrets[]` → assert `.env.example` emitted with correct key list. |
| `src/commands/__tests__/check.test.ts` | Fixture skill + mocked env: all green → exit 0; one secret missing → exit 1; only warnings → exit 2; `--json` → schema-validated JSON output. |
| `src/lib/__tests__/frontmatter.secrets.test.ts` | Parses the new `secrets`, `runtime`, `integrationTests` blocks. Absent fields → `null`. Round-trip via `dump` preserves shape. |
| `src/eval/__tests__/skill-scanner.multiFile.test.ts` | Scanner propagates new fields through `normalizeSkillInfo`; absent fields surface as `null` (not `undefined`) per the `SkillInfo` contract. |

### Fixture validation

| Test | Coverage |
|---|---|
| `src/commands/__tests__/check.stripe-fixture.test.ts` | Run `vskill check stripe-refund-auditor` against the actual landed fixture. With no env: exit 1, `STRIPE_API_KEY: missing`, `stripe MCP: not configured`. With `STRIPE_API_KEY` set: secrets row green, MCP row still red → exit 1, then assert `--json` shape. |
| Pytest `tests/integration_test.py` (in fixture) | Uses `os.environ.get("STRIPE_API_KEY")` + `pytest.skip` if absent. Demonstrates the contract; not run by vitest CI. |

**Coverage target**: 95% on new code per project policy (`testing.coverageTarget: 90` in metadata.json bumps to 95 for new lines).

### Stripe fixture skill layout

```
plugins/personal/skills/stripe-refund-auditor/
├── SKILL.md                        # frontmatter with secrets, runtime, integrationTests, mcpDeps: [stripe]
├── scripts/
│   ├── audit.py                    # pull refunds, detect anomalies (uses stripe SDK)
│   └── grader.py                   # deterministic numeric grader for evals
├── references/
│   └── refund-schema.md            # Stripe Refund object reference
├── tests/
│   └── integration_test.py         # pytest hitting Stripe test mode (skips without key)
├── evals/
│   └── evals.json                  # 3-5 LLM-judged behavioral cases
└── .env.example                    # STRIPE_API_KEY=sk_test_...
```

## ADR review

The ADR directory at `.specweave/docs/internal/architecture/adr/` contains 21+ existing decisions. Relevant ones for this increment:

- **adr/0008-interface-first-typescript-design-for-type-safety.md** — supports the schema-first sequencing here (extend `SkillInfo` interfaces before any consumer).
- **adr/0001-use-zod-for-runtime-schema-validation.md** — if Zod is the project standard for request validation, the new `files: Record<string, string>` payload and `secrets[]` block on `POST /api/skills/create` should be validated through the same Zod pattern, not ad-hoc `if` checks. **Action**: confirm during implementation; reuse existing schemas in `skill-create-routes.ts` rather than introducing a parallel validation style.
- **adr/0009-factory-pattern.md** — the new per-role agent prompts (`SCRIPT_SYSTEM_PROMPT`, etc.) should be exported as constants alongside `BODY_SYSTEM_PROMPT` / `EVAL_SYSTEM_PROMPT`, not behind a factory. The existing skill-generator pattern is direct constant + `createLlmClient`; preserve that.

**No new ADR proposed.** This increment is a feature-level extension of an existing pipeline. The decisions (opt-in multi-file flag, parallel-then-sequential fan-out, per-agent model assignment, optional manifest fields) are tactical choices documented in this plan rather than architectural ones. If the multi-file path becomes the default in a future increment, that flip *would* warrant an ADR.

## Risks + mitigations

| Risk | Mitigation |
|---|---|
| 5 parallel LLM calls = high cost per generation | `reference` and `eval` agents pinned to Haiku (cheap); `multiFile` is **opt-in** via request flag; default path remains 2-call. Cost only borne by callers that explicitly set `multiFile: true`. |
| Path traversal via attacker-controlled `files` map keys | `resolveSafe(base, rel)` helper rejects absolute paths and `..` segments and verifies the resolved path stays inside `targetDir`. Covered by an explicit vitest test asserting 400 on `../../etc/passwd` and `/etc/passwd`. |
| Body-agent emits wrong filenames if a sub-agent fails (`Promise.allSettled` returns mixed results) | Body-agent receives the **actual** produced-filename list as input (built from `result.status === "fulfilled"`). Missing files become "see the `references/` directory" generics rather than dangling links. |
| Stripe API dependency in fixture pytest | Tests are decorated with `pytest.mark.skipif(not os.environ.get("STRIPE_API_KEY"))`. Default CI path skips. The `STRIPE_API_KEY` is never checked in. |
| Frontmatter additions break existing scanners or installers | All new fields are optional (`?` / `| null`). Vitest fixtures explicitly cover both presence and absence. The `installer/frontmatter.ts` mirror prevents drift between author-time and install-time parsers. |
| Atomic write half-fails leaving a partial skill on disk | Inside the existing try/catch in `skill-create-routes.ts`, `rmSync(targetDir, { recursive: true })` rolls back on any post-`mkdirSync` exception **unless** `isUpdateMode` (in which case existing files must be preserved). Covered by the supertest mid-write-throw test. |
| Adding a new commander.js command breaks the help banner / CLI ordering | Register `check` immediately after `audit` (per the established pattern at `src/index.ts:184`); use the same dynamic-import shape. |

## Verification (manual E2E)

```bash
cd repositories/anton-abyzov/vskill

# 1. Build + tests
npm run build
npm test

# 2. Preflight against the fixture (no env)
node dist/bin.js check stripe-refund-auditor
#   expect: exit 1, "STRIPE_API_KEY: missing", "stripe MCP: not configured"

# 3. Set env, re-check
STRIPE_API_KEY=sk_test_dummy node dist/bin.js check stripe-refund-auditor --json
#   expect: exit 1 (MCP still missing), JSON with secrets[0].status="ready"

# 4. Studio end-to-end
node dist/bin.js studio --port 3077
# In another terminal:
curl -X POST http://localhost:3077/api/skills/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt":"Stripe refund auditor with python script and pytest integration test","multiFile":true}' \
  | jq .
#   expect: response includes files map with scripts/, tests/, references/

# 5. Optional pytest (only if Python + Stripe key available)
cd plugins/personal/skills/stripe-refund-auditor && python3 -m pytest tests/ -v
```

## Out of scope (non-goals)

- **Replacing the existing dual-LLM path** — `multiFile` is opt-in; default remains 2-call.
- **Production-grade Stripe integration logic** — `stripe-refund-auditor` is a fixture / contract demo.
- **Auto-installing MCP servers** when `vskill check` finds them missing — only reports.
- **Auto-running `pip install`** when `runtime.pip` is declared — only validates that the Python version satisfies the spec.
- **Streaming progress UI for the 5 agents** in the studio frontend — server-side fan-out is enough for v1; UI streaming is a separate increment.
