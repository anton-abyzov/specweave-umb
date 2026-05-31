# 0857 — Deterministic stub LLM provider + shared verify harness

## Problem

The core promise of vskill is: **create a skill → install it → run it against a model
you chose**. Today nothing proves that pipeline stays unbroken in CI. The three weak
points are:

1. **Model selection silently drops.** A refactor that loses a `--model` /
   `--judge-model` flag would make every run fall back to the default model. No test
   catches it because the existing eval tests mock the client regardless of the input.
2. **No deterministic engine.** Every real provider needs a network call, an API key,
   or a local `claude` binary, so the end-to-end path can't run in CI. The 0853 harness
   stubbed `skill new` by hand-writing files — it never exercised the real generator.
3. **Silent-green skips.** A verify run where every model lane SKIPs (no binary, no key)
   currently looks the same as a passing run. A SKIP can masquerade as green.

## Users / Stories

### US-001 — Guaranteed create→install→run-with-non-default-model
As a maintainer, I want one deterministic test that creates a skill with a NON-DEFAULT
model, installs it, and runs an eval against that same model — so a dropped model flag
or a broken install can never ship green.

- **AC-US1-01**: A `stub` LLM provider exists that runs in-process, needs no network or
  API key, returns deterministic content-addressed output, and echoes back the requested
  model (`client.model === requested`).
- **AC-US1-02**: `vskill skill new --prompt "..." --provider stub --model <non-default>`
  writes a real `SKILL.md` with a `name` and, on the claude-code target, a `model`
  frontmatter equal to the requested model.
- **AC-US1-03**: The skill installs via the add command (`--copy --no-enable`) producing
  a lockfile entry and files under `.claude/skills`.
- **AC-US1-04**: `VSKILL_EVAL_PROVIDER=stub VSKILL_EVAL_MODEL=<non-default> vskill eval
  run <skill>` produces a benchmark whose model equals the requested model.
- **AC-US1-05**: The U-GOLDEN unit surfaces `{created, installed, ranModel,
  requestedModel, benchmark:{cases,passed}}` and asserts the **regression guard
  `ranModel === requestedModel`**.

### US-002 — A SKIP can never masquerade as green
As a CI reviewer, I want a run where everything SKIPs to be visibly NOT green.

- **AC-US2-01**: The matrix gate asserts at least one model-run fixture reports PASS
  (not SKIP/BLOCKED) per run.
- **AC-US2-02**: Every SKIP emits a `::warning::`-prefixed line carrying provider + reason.
- **AC-US2-03**: Probe fixtures encode the lie-detectors: unknown provider → BLOCKED,
  requested-model-ignored → FAIL.

### US-003 — The stub is hidden from users
As a Studio user, I must never see the stub in the provider list or model picker — it is
a test seam, not a product.

- **AC-US3-01**: `detectAvailableProviders()` does not include `stub`.
- **AC-US3-02**: `stub` is excluded from `KNOWN_PROVIDER_NAMES`, so a tampered
  `studio.json` cannot route the API to it.
- **AC-US3-03**: The 0856 `CLAUDE_CLI_NORMALIZE` `claude-opus-4-8 → opus` mapping is
  preserved unchanged.

## Out of scope
- Real provider behavior changes (Anthropic, OpenAI, Ollama, etc.).
- Studio UI changes.
- CI workflow wiring (separate increment 0858).
