# 0857 — Plan

## A. Deterministic `stub` provider (`src/eval/llm.ts`)

- Extend `ProviderName` union with `"stub"`.
- `createStubClient(modelOverride?)`:
  - Resolve model = `modelOverride ?? VSKILL_EVAL_MODEL ?? "sonnet"`. Set `client.model`
    to the resolved value so non-default selection is directly assertable.
  - `generate(system, user)` is pure: FNV-1a hash of `system\n\nuser` → stable slug.
    Returns a single JSON **envelope** that satisfies every downstream parser at once:
    `{ name, description, model, allowedTools, body, evals, pass, reasoning }`.
    - skill-gen body parser reads `name/description/model/body`.
    - skill-gen evals parser reads `evals`.
    - judge parser reads `pass/reasoning`.
    - `model` echoes the requested model so the emitted SKILL.md frontmatter and the
      benchmark `model` both reflect the chosen model.
  - `billingMode: "free"`, `cost: 0`, tokens null. No network, no spawn, no key.
- Dispatch: add `case "stub"` in `createLlmClient`.
- **Hide it**: do NOT add `stub` to `KNOWN_PROVIDER_NAMES` or `detectAvailableProviders`
  in `src/eval-server/api-routes.ts`. (PROVIDER_MODELS is a `Record<ProviderName,...>`;
  add a minimal `stub: []` entry only if the type requires exhaustiveness — verified at
  build.)
- **Preserve** the 0856 `CLAUDE_CLI_NORMALIZE` map verbatim (incl. `claude-opus-4-8`).

## B. Thread `--provider/--model` into `vskill skill new`

`generateSkill()` already accepts `{ provider, model }`. The CLI command does not expose
them. Add `--provider <id>` and `--model <id>` options to `skill new` and pass them into
`generateSkill(... { prompt, targetAgents, provider, model })`. Backward compatible —
both optional, default behavior unchanged.

## C. Promote 0853 harness → `repositories/anton-abyzov/vskill/test/verify/`

Copy (not move): `run-verify.mjs`, `runner.mjs`, `matrix.test.mjs`, `registry.mjs`,
`record.mjs`, `verify-types.mjs`, `lib/vskill-runner.mjs`, `verifiers/*.mjs`,
`units/*.verify.mjs`, `fixtures/tiny-skill-source/`.

Re-root all paths: harness now lives at `<vskill>/test/verify/`, so `REPO_ROOT`,
`VSKILL_BIN` (`<vskill>/dist/bin.js`), `FIXTURE_SOURCE`, report + agent-handle paths all
resolve against the vskill repo root (2 levels up from `test/verify`). Keep the
VerifyResult JSON contract and the agent-handle write.

`package.json` scripts: `"verify"`, `"verify:matrix"`.

## D. U-GOLDEN unit (`test/verify/units/golden-path.verify.mjs`)

Tmp HOME/CLAUDE_HOME-isolated workdir. Non-default model = `opus` (CLI default is
`sonnet`). Steps:
1. `vskill skill new --prompt ... --provider stub --model opus` → assert SKILL.md name +
   claude-code `model: opus` frontmatter.
2. install via add `--copy --no-enable` → assert lockfile entry + `.claude/skills` files.
3. `VSKILL_EVAL_PROVIDER=stub VSKILL_EVAL_MODEL=opus vskill eval run <skill>` → read
   benchmark.json model = ranModel.
4. Surface `{created, installed, ranModel, requestedModel, benchmark}` + invariant
   `ranModel === requestedModel`.
5. Probes: unknown-provider → BLOCKED, requested-model-ignored → FAIL.

## E. Unit-level guards (fast PR feedback)

- `run.test.ts`: assert `createLlmClient` is called with parsed `{provider, model}` from
  `--judge-model`.
- `llm.test.ts`: claude-cli argv `['-p','--model',<model>]` + `client.model ===
  normalized(input)`; stub echoes `haiku` + determinism across two calls.
- `claude-cli-compliance.test.ts`: pin no-API-key + CLAUDE*-stripped +
  `billingMode==='subscription'`.
- Cross-surface invariant test: CLI claude-cli default `sonnet`
  (`createClaudeCliClient`) vs Studio default `opus` (`PROVIDER_MODELS["claude-cli"][0]`).

## F. Loud-skip gate (`matrix.test.mjs`)

Add a test: run the harness (or inspect unit verdicts) and assert ≥1 model-run fixture is
PASS; for each SKIP, `console.warn("::warning:: ...")` with provider+reason. All-SKIP ≠
green.

## Verification

`npm run verify`, `node --test test/verify/matrix.test.mjs`,
`npx vitest run src/eval/__tests__/llm.test.ts src/commands/eval/__tests__/run.test.ts
src/eval/__tests__/claude-cli-compliance.test.ts`.
