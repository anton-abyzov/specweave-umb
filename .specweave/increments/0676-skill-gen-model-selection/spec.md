---
status: completed
project: vskill-platform
---
# 0676 — Skill Generation Model Selection

## Context

`vskill-platform/src/lib/eval/claude-adapter.ts` currently hardcodes
`claude-sonnet-4-6` as the model for skill evaluation. The rest of the skill
generation ecosystem (SpecWeave `sw:skill-gen`, Anthropic's `skill-creator`,
vskill CLI) already inherits the parent Claude session's model, so no change
is required there.

The surgical fix is: make the vskill-platform eval path config-driven,
default to the newest Opus model (quality-first — skill descriptions drive
auto-activation heuristics, so wording precision compounds), and thread
`ANTHROPIC_BASE_URL` through the Anthropic SDK so users can route through the
`anymodel` proxy to any backend (OpenRouter, LM Studio, GPT-5, local models)
without adding new SDK dependencies.

Critical constraint from user: **no hardcoded model string constants**. A
priority-ordered registry resolves the newest supported Opus. When Opus 4.8
ships, one line changes.

## User Stories

### US-001: Default to newest Opus via registry
**As** the vskill-platform operator
**I want** skill evaluation to use the newest supported Opus model by default
**So that** skill description quality (which drives Claude auto-activation) is
maximized without any hardcoded model string outside the registry.

**Acceptance Criteria**
- [x] AC-US1-01: `resolveDefaultModel()` with no arg returns the first
  `status: "current"` Opus entry in the registry
- [x] AC-US1-02: `claude-adapter.ts` no longer contains the literal string
  `claude-sonnet-4-6` — it imports `resolveModel` instead
- [x] AC-US1-03: Registry contains at least `claude-opus-4-7`,
  `claude-sonnet-4-6`, `claude-haiku-4-5-20251001` each marked `current`,
  with a header comment describing the forward-compat update pattern

### US-002: Env-driven override (BYO model via AnyModel)
**As** a developer who wants to route evals through GPT-5 / DeepSeek / local
**I want** to set `SKILL_EVAL_MODEL` and/or `ANTHROPIC_BASE_URL` and have the
adapter honor them with zero code changes
**So that** I can use the existing AnyModel proxy pattern without forking
the SDK or adding new providers.

**Acceptance Criteria**
- [x] AC-US2-01: `resolveModel(process.env.SKILL_EVAL_MODEL)` returns the
  hint if set to a known alias (`opus`|`sonnet`|`haiku`) or full model ID
- [x] AC-US2-02: `new Anthropic({ baseURL: process.env.ANTHROPIC_BASE_URL })`
  forwards the override (SDK treats `undefined` as default — verified
  against SDK type `baseURL?: string | null | undefined`)
- [x] AC-US2-03: Aliases `"opus"`, `"sonnet"`, `"haiku"` map to the current
  entry of that tier

### US-003: Regression-safe skill markdown generation
**As** a skill reviewer
**I want** a validator that rejects malformed skill frontmatter
**So that** model changes (or prompt drift) can't silently produce
auto-activation-breaking SKILL.md files.

**Acceptance Criteria**
- [x] AC-US3-01: `validateSkillMarkdown` rejects missing frontmatter
- [x] AC-US3-02: Rejects `name` that doesn't match the flat/namespaced regex
- [x] AC-US3-03: Rejects `description` shorter than 60 chars, missing an
  action verb, or not ending with a period
- [x] AC-US3-04: Rejects missing `##` heading in body
- [x] AC-US3-05: Rejects HTML tags inside mermaid code blocks
  (Docusaurus regression guard per feedback memory)

### US-004: Full-assertion Playwright E2E
**As** the CI pipeline
**I want** the E2E suite to hard-assert default model resolution, happy-path
skill creation produces a valid SKILL.md, BYO override is honored, and
invalid frontmatter fails
**So that** regressions in the adapter or prompt path break the build, not
production.

**Acceptance Criteria**
- [x] AC-US4-01: Default-model test asserts response reports Opus-tier
- [x] AC-US4-02: Happy-path test produces a SKILL.md that passes
  `validateSkillMarkdown` (ok: true)
- [x] AC-US4-03: BYO override test asserts `resolveModel("claude-haiku-...")`
  echoes the hint
- [x] AC-US4-04: Regression fixture with invalid frontmatter fails validator

## Out of Scope
- Building the "Universal Skill Builder" (separate ~5-day increment per memory)
- Touching `sw:skill-gen` / `skill-creator` (no LLM of their own)
- Refactoring vskill CLI (already configurable via `--models`)
- Adding new provider SDKs (LiteLLM, Vercel AI SDK, etc.)
- Other Anthropic SDK call sites (`skill-judge.ts`, `anthropic-provider.ts`)
