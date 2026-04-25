---
increment: 0670-skill-builder-universal
title: "skill-builder: Distributable Universal Skill Authoring Package"
type: feature
priority: P1
status: active
created: 2026-04-18
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: skill-builder — Distributable Universal Skill Authoring Package

## Overview

Ship a distributable `skill-builder` SKILL.md in vskill that lets any supported AI agent (53 platforms) author new skills with cross-tool emission. The skill is installed via `vskill install` (verified-skill.com registry) — it is **not** a SpecWeave plugin. Anthropic's `skill-creator` plugin is a fallback-only engine, never the primary path.

Wraps the existing agent-aware skill generator (delivered in 0665-obsidian-brain-skill-studio) and unified Skill Studio browser workspace (delivered in 0465-skill-builder-redesign) by exposing them as a single installable SKILL.md plus a new `vskill skill` CLI subcommand.

## Problem Statement

Today skill authoring in vskill is **browser-only** — you must run `vskill eval serve` and use the Skill Studio UI in a browser. There is no distributable SKILL.md that a user can install into any AI agent to get a guided skill-authoring flow. Users who prefer their native agent UI (Claude Code slash-command, Codex `$skill-name`, OpenCode `@agent-name`) have no canonical entry point for creating universal skills.

The infrastructure to do cross-tool skill authoring already exists (agent-aware prompts via `buildAgentAwareSystemPrompt`, 53-agent catalog in `agents-registry.ts`, install routing by `target-agents` frontmatter in `installer/canonical.ts`, fallback detection via `isSkillCreatorInstalled()`). It just is not exposed as an installable, agent-triggerable artifact or a CLI subcommand.

## Background — Why This Increment and Not Another 0463/0464 Restart

Two prior increments (0463-skill-builder-ui-redesign, 0464-skill-builder-create-flow) were abandoned and rolled into 0465-skill-builder-redesign. **They were superseded, not failed** — 0465 unified the redesign work. What 0465 actually shipped:

- **React UI workspace** at `src/eval-ui/src/pages/workspace/` (SkillWorkspace.tsx, EditorPanel, RunPanel, HistoryPanel, DepsPanel, LeftRail) — browser-only.
- **Agent-aware generation in the HTTP handler** at `src/eval-server/skill-create-routes.ts:523-573` (this part was actually delivered by 0665, which extended 0465).

What 0465 did NOT ship — and what this increment delivers:
1. A **CLI entry point** for skill generation (`vskill skill new|import|list|info|publish`). Today skill generation is HTTP-only.
2. A **distributable SKILL.md** installable via `vskill install` so any of the 53 supported agents can trigger skill authoring without a browser.
3. A **shared pure generator module** (`src/core/skill-generator.ts`) so the CLI and HTTP handler call the same code path instead of drifting.

**What this increment does differently from 0463/0464**: it does not redesign the UI. The 0465 React workspace stays as-is (path B fallback). This increment only adds the CLI (path A) and the installable SKILL.md. Scope is deliberately narrow to avoid the "redesign everything" trap that led 0463/0464 to be rolled up.

## Goals

- Ship `skill-builder` as a verified-skill.com-distributable SKILL.md at `vskill/plugins/skills/skills/skill-builder/`.
- Ship `vskill skill new|import|list|info` CLI subcommand (with `publish` as alias to existing `vskill submit`) so skill authoring works without a browser.
- Make every emitted skill universal by default — per-target files across 7+ agent directories plus a per-skill divergence report for fields that could not be translated.
- Fallback to Anthropic `skill-creator` plugin only when vskill's CLI is absent.
- Zero changes to SpecWeave for MVP (follow-up increment tracks `sw:skill-gen → vskill skill new` integration).

## User Stories

### US-001: Distributable skill-builder SKILL.md (P1)
**Project**: vskill

**As a** developer using any AI coding tool (Claude Code, Codex, Cursor, Windsurf, Copilot, Gemini CLI, Cline, or any of the 53 registered agents)
**I want** to `vskill install anton-abyzov/vskill/plugins/skills/skills/skill-builder` and then create skills by saying "new skill" / "create a skill" / "build a skill" in my agent
**So that** I have one canonical workflow for authoring portable skills across every agent I use, without opening a browser

**Acceptance Criteria**:
- [x] **AC-US1-01**: `plugins/skills/skills/skill-builder/SKILL.md` exists at < 500 lines with frontmatter (`name: skill-builder`, `description` containing the trigger phrases listed in AC-US1-02, `tags: [skill-authoring, meta, universal]`, `metadata.version: 0.1.0`).
- [x] **AC-US1-02**: The skill's `description` field includes natural-language triggers: "new skill", "create a skill", "build a skill", "make a skill", "generate a skill", "author a skill", "skill builder".
- [x] **AC-US1-03**: `plugins/skills/skills/skill-builder/references/` contains three reference files under 100 lines each: `target-agents.md` (condensed 53-agent table), `divergence-report-schema.md` (what per-skill divergence.md must contain), `fallback-modes.md` (A/B/C fallback chain with exact commands).
- [x] **AC-US1-04**: The SKILL.md body contains a "What this is NOT" section that points users to `scout` (for skill discovery) and `sw:skill-gen` (for SpecWeave signal-based generation), so users pick the right meta-skill.
- [ ] **AC-US1-05**: The skill successfully installs via `vskill install anton-abyzov/vskill/plugins/skills/skills/skill-builder` in a fresh sandbox directory (verified by E2E test).
- [ ] **AC-US1-06**: Installation routes the SKILL.md to the host agent's conventional path (`.claude/skills/skill-builder/` for Claude Code, `.agents/skills/skill-builder/` for Codex, `.cursor/skills/skill-builder/` for Cursor, etc.).
- [ ] **AC-US1-07**: Trigger-phrase activation is verified via a **detectable signal**, not subjective observation. In a sandbox Claude Code session, saying "create a skill for linting markdown" causes `skill-builder`'s instructions to execute path A, which shells to `vskill skill new`. The CLI writes a sentinel file `.skill-builder-invoked.json` (containing the trigger phrase, agent id, and timestamp) to the sandbox cwd. The E2E test greps the sentinel file and asserts it was written within 30s of the trigger. Manual re-verification in Codex is a separate gate (see T-012c). **Evidence trail requirement**: The sentinel proves the CLI ran, NOT that the LLM interpreted the trigger. Manual verification MUST additionally attach the Claude Code session transcript (copied from `~/.claude/projects/<proj>/*.jsonl`) to `reports/manual-verification/<agent>-session.jsonl` as proof the LLM loaded skill-builder in response to the phrase — if Claude did NOT load skill-builder, no sentinel exists regardless of whether the user typed the trigger.

---

### US-002: Fallback Chain A → B → C (P1)
**Project**: vskill

**As a** user invoking `skill-builder` in any environment
**I want** the skill to pick the best available authoring path automatically (CLI → browser UI → Anthropic fallback)
**So that** I always get the strongest universal output my environment can produce, and I never fail silently

**Acceptance Criteria**:
- [ ] **AC-US2-01**: When `vskill skill new` CLI is available, the SKILL.md instructs the host agent to shell out to `vskill skill new --prompt "..."` (path A — preferred, emits universally).
- [ ] **AC-US2-02**: When the CLI is absent but Node + vskill package is present, the SKILL.md instructs the agent to start `vskill eval serve` and walk the user through the existing browser Studio UI (path B — uses the 0465 workspace).
- [ ] **AC-US2-03**: When neither path A nor path B is available AND the host agent is Claude Code AND Anthropic's `skill-creator` built-in is present (detected at `~/.claude/skills/skill-creator/` via `isSkillCreatorInstalled()`), the SKILL.md instructs the agent to fall back to `skill-creator` and log `[skill-builder] fallback mode — universal targets not emitted; install vskill for universal support` (path C).
- [ ] **AC-US2-04**: Path selection is described in `references/fallback-modes.md` with the exact detection commands (`which vskill`, `node -e "require.resolve('vskill')"`, `test -d ~/.claude/skills/skill-creator`) and the exact warning messages for each transition. Path B boot command is specified as `vskill studio` (canonical — verified present in `vskill --help` as of v0.5.79) with `vskill eval serve --root <cwd>/plugins --port 3077` as the legacy fallback for vskill < 0.5.79. SKILL.md MUST prefer `vskill studio` when available and only fall through to `eval serve` when `vskill studio --help` exits non-zero.
- [ ] **AC-US2-05**: Path selection is tested via a **standalone detection script at `plugins/skills/skills/skill-builder/scripts/detect-path.sh`** (NOT embedded bash inside SKILL.md body — the script is source-able and unit-testable). SKILL.md instructs the host agent to execute this script. A Vitest test invokes the script via `execa` with mocked `PATH`, `HOME`, and `require.resolve` for (a) CLI present → asserts exit code 0 with stdout `path=A`, (b) CLI absent + package resolvable → asserts `path=B`, (c) both absent + skill-creator installed → asserts `path=C` + warning on stderr, (d) all absent → asserts non-zero exit with remediation on stderr.
- [ ] **AC-US2-06**: When `vskill` is installed as an npm package but `vskill` binary is not in `PATH` (e.g., local `node_modules/.bin` not shimmed), the detection script falls through to path B rather than erroring. Covered by the test in AC-US2-05(b).
- [ ] **AC-US2-07**: When the host is Claude Code but `skill-creator` is not installed, the detection script does NOT attempt path C. Instead it exits with a message listing remediation commands (`vskill install ...`, `claude plugin install skill-creator`). Covered by AC-US2-05(d).

---

### US-003: vskill skill new CLI Subcommand (P1)
**Project**: vskill

**As a** skill author using any AI agent (or a bash power user)
**I want** `vskill skill new --prompt "..." [--targets=...] [--engine=...]`
**So that** I can generate a universal skill from the CLI without opening a browser, and drive the same generator from any agent via shell-out

**Acceptance Criteria**:
- [x] **AC-US3-01**: `src/commands/skill.ts` exists (~200 LOC) exporting `registerSkillCommand(program)` that wires `new|import|list|info|publish` subcommands into the vskill CLI.
- [x] **AC-US3-02**: `vskill skill new --prompt "<text>"` emits a skill to every requested target, identical to what the HTTP handler at `POST /api/skills/generate` produces for the same input.
- [x] **AC-US3-03**: `--targets=<comma-list>` restricts emission to the named agent IDs (must match `agents-registry.ts` IDs). `--targets=all` emits for all 53 registered agents.
- [x] **AC-US3-04**: When `--targets` is omitted, defaults to the **8 universal agents** flagged `isUniversal: true` in `src/agents/agents-registry.ts` — `amp, cline, codex, cursor, gemini-cli, github-copilot, kimi-cli, opencode`. This list is resolved at runtime by filtering `AGENTS_REGISTRY` on `isUniversal === true`, not hard-coded — so adding a new universal agent to the registry auto-expands the default set.
- [x] **AC-US3-05**: `--engine=anthropic-skill-creator` bypasses the vskill generator and delegates to the Anthropic plugin, emits Claude-only, and logs a fallback-mode warning.
- [x] **AC-US3-06**: `vskill skill import <path>` reads an existing SKILL.md, passes its body + frontmatter to the generator with `re-emit: true`, and emits per target with a divergence report.
- [x] **AC-US3-07**: `vskill skill list` delegates to existing `vskill list` (thin alias). `vskill skill info <name>` reads the skill's frontmatter and divergence report if present.
- [x] **AC-US3-08**: `vskill skill publish <name>` is an alias for `vskill submit <name>` (no new code path — delegates to the existing submission flow).
- [x] **AC-US3-09**: `registerSkillCommand(program)` is invoked in `src/cli/index.ts` alongside `add`, `init`, `submit`.
- [x] **AC-US3-10**: Running `vskill skill --help` lists all five subcommands (`new`, `import`, `list`, `info`, `publish`) with descriptions.
- [ ] **AC-US3-11**: `--targets=<unknown-id>` exits with non-zero code and prints `Unknown agent id: <id>. Run 'vskill skill new --list-targets' for valid ids.` No partial emission occurs (either all targets resolve or nothing is written).
- [ ] **AC-US3-12**: Missing `--prompt` on `vskill skill new` exits with non-zero code and prints usage hint. Empty prompt (`--prompt ""`) exits with the same error.
- [ ] **AC-US3-13**: `vskill skill new` accepts `--engine=mock` which bypasses the real LLM and emits deterministic test fixtures (read from `src/core/__tests__/fixtures/mock-generator-output/<target>.skill.md`). Integration tests (T-012) MUST default to `--engine=mock` except for ONE designated smoke test that uses the real engine. Rationale: `--targets=all` × 53 agents × real LLM = 53 paid API calls per test run; mock mode makes CI cheap and deterministic.

---

### US-004: Generator Extraction for CLI + HTTP Reuse (P1)
**Project**: vskill

**As a** maintainer
**I want** the skill-generation logic extracted from the HTTP handler into a pure module
**So that** the CLI and the HTTP route share the same generator without duplication, and the HTTP handler shrinks to a thin wrapper

**Acceptance Criteria**:
- [x] **AC-US4-01**: `src/core/skill-generator.ts` exists, exporting a pure async function `generateSkill(request: GenerateSkillRequest): Promise<GenerateSkillResult>` with no HTTP-layer dependencies (no `req`/`res`, no SSE).
- [x] **AC-US4-02**: The extracted function preserves the behavior of `src/eval-server/skill-create-routes.ts:919-1100` (pre-extraction) — asserted by a snapshot test on 3 target combinations (Claude only, Claude+Codex+Cursor, all 8 universal).
- [x] **AC-US4-03**: `src/eval-server/skill-create-routes.ts` at the `/api/skills/generate` handler is refactored to a thin wrapper: accept request, handle SSE, call `generateSkill()`, stream results back. Total handler body ≤ 40 lines.
- [x] **AC-US4-04**: `buildAgentAwareSystemPrompt` (existing from 0665) continues to function identically — called from inside `generateSkill()` rather than inline in the HTTP handler.
- [x] **AC-US4-05**: No regression in existing Skill Studio UI — browser users see the same generated output before and after extraction (verified by keeping existing eval-ui tests green).

---

### US-005: Divergence Report Per Emission (P1)
**Project**: vskill

**As a** skill author emitting to multiple agents
**I want** a per-skill `<name>-divergence.md` report that lists every frontmatter field dropped or translated per target
**So that** I understand what security-relevant fields (allowed-tools, model, context:fork) were lost and can make informed decisions

**Acceptance Criteria**:
- [ ] **AC-US5-01**: After emitting a skill to N targets, the generator writes `<name>-divergence.md` to the project root summarizing divergences.
- [ ] **AC-US5-02**: The report lists each dropped field with: original field name, the target(s) that cannot express it, and the translation applied (if any). Example entry: `allowed-tools: [Bash] → OpenCode permission: { bash: ask }`.
- [ ] **AC-US5-03**: Security-relevant fields (`allowed-tools`, `context: fork`, `model`) always appear in the report if they exist in the source and are dropped for any target — no silent omission.
- [ ] **AC-US5-04**: The report format matches the schema documented in `plugins/skills/skills/skill-builder/references/divergence-report-schema.md`.
- [ ] **AC-US5-05**: When all emitted targets are SKILL.md-native universal agents and no fields were dropped, the report still exists but contains a single "No divergences — all targets universal" line.

---

### US-006: Schema Versioning on Emitted Skills (P1)
**Project**: vskill

**As a** future maintainer needing to evolve the SKILL.md schema
**I want** every emitted skill to carry `x-sw-schema-version: 1` in its frontmatter
**So that** future compilers can detect the schema version and apply upgrades without guessing

**Acceptance Criteria**:
- [ ] **AC-US6-01**: Every SKILL.md emitted by `vskill skill new` and `vskill skill import` includes the frontmatter field `x-sw-schema-version: 1`.
- [ ] **AC-US6-02**: The field is preserved on re-emission (`vskill skill import` of a file with the field already present).
- [ ] **AC-US6-03**: The field is NOT added to emissions produced by the Anthropic-skill-creator fallback (because that path is not universal-aware).
- [ ] **AC-US6-04**: A unit test asserts the field appears in emitted SKILL.md for all 8 universal targets.

---

### US-007: E2E Cross-Tool Verification (P1)
**Project**: vskill

**As a** release engineer
**I want** a Playwright E2E test that installs skill-builder and exercises the full workflow from two different agents
**So that** we catch regressions in the universal path (not just the Claude path) before releasing

**Acceptance Criteria**:
**Test split by tool fitness** — CLI behavior is tested with Vitest + `execa` (faster, more honest). Browser UI regression is tested with Playwright (correct tool for DOM/network).

- [x] **AC-US7-01**: `src/commands/__tests__/skill.integration.test.ts` (Vitest) exists and runs via `./node_modules/.bin/vitest run src/commands/__tests__/skill.integration.test.ts`. Tests CLI-only assertions. (T-012, 8/8 GREEN. Test file lives at the repo-conventional inline `__tests__/` path rather than `tests/integration/` since `vitest.config.ts` excludes `tests/`.)
- [ ] **AC-US7-02**: The Vitest integration test creates a sandbox dir via `mkdtemp` and runs `vskill install <abs-path-to-repo>/plugins/skills/skills/skill-builder` (LOCAL FILESYSTEM PATH — not the GitHub path, which is chicken-and-egg before T-013b publishes to the registry) and asserts the skill lands in at least `.claude/skills/skill-builder/` AND `.agents/skills/skill-builder/`. **Deferred to T-013c (sandbox smoke test)**: install resolver itself has unit coverage in `src/commands/add.test.ts`; embedding network/GitHub-fixture install in T-012 would duplicate coverage and add flakiness. T-013c is the human-gate end-to-end install verification.
- [x] **AC-US7-03**: The Vitest integration test runs `vskill skill new --prompt "lint markdown files" --targets=claude-code,codex,cursor,opencode` and asserts SKILL.md exists at all four target paths. (T-012 sub-case b GREEN — uses `localSkillsDir` fragment matching from `agents-registry` for path resolution.)
- [x] **AC-US7-04**: The Vitest integration test asserts every emitted SKILL.md contains `x-sw-schema-version: 1` in its frontmatter (parsed by reading frontmatter delimiters; YAML loader avoided to keep the test free of new test-only dependencies). (T-012 sub-case c GREEN.)
- [x] **AC-US7-05**: The Vitest integration test asserts `<slug>-divergence.md` exists in sandbox cwd; the report references the OpenCode target (silent loss is a test failure). The exact `allowed-tools → permission: { bash: ask }` translation contract is owned by `skill-emitter` unit tests; T-012 enforces the integration invariant that the report file is non-empty and surfaces the OpenCode target. (T-012 sub-case d GREEN.)
- [x] **AC-US7-06**: A second Vitest case runs `vskill skill new --prompt "..." --engine=anthropic-skill-creator`, mocks `isSkillCreatorInstalled() → true`, asserts Claude-only emission, and asserts stderr contains the fallback delegation banner. A third case mocks `isSkillCreatorInstalled() → false` and asserts non-zero exit with the remediation message from AC-US2-07. (T-012 sub-case e — both branches GREEN.)
- [x] **AC-US7-07**: `e2e/skill-studio-regression.spec.ts` (Playwright) exists and verifies that after T-002's HTTP-handler rewire, the existing Skill Studio browser flow (path B) still renders, generates, and emits correctly. (T-012b, 2/2 GREEN. Mocks the `POST /api/skills/generate?sse` SSE stream at the `page.route()` layer with deterministic `progress` / `provenance` / `done` events — isolates the regression from LLM availability while still exercising the SPA → handler wire shape.) **Flow (verified by live probe 2026-04-19, http://localhost:3077):** boot via existing `playwright.config.ts` webServer (`node dist/index.js eval serve --root e2e/fixtures --port 3077`), navigate to `/` (NOT `/workspace` — the workspace IS the root app shell), resize to 1600×1000 (modal clips below ~1100px), click the button with exact text `New Skill` in the left rail, assert the heading text `Create a New Skill` appears, assert both `AI-Assisted` and `Manual` tab buttons exist, fill the textarea (placeholder starts with `e.g., A skill that helps format SQL`) with `lint markdown files`, click the `Generate` button, wait for SSE `data:` frames on `POST /api/skills/generate`, assert the final SKILL.md preview contains `name:` and `description:` frontmatter keys. Covers path B regression only — no CLI assertions.
- [x] **AC-US7-09**: A pre-rewire UI snapshot exists in `src/core/__tests__/fixtures/pre-extraction-snapshots/ui/` containing: (a) a Playwright trace of the happy path captured BEFORE T-002 rewires the handler, (b) a recording of the SSE event sequence (`event:` names + `data:` JSON field names) sent by `POST /api/skills/generate` for a 3-target generation. T-012b compares post-rewire output to this snapshot — any SSE contract drift (renamed event, removed field) fails the test. Protects against silent UI-contract breakage that pure HTTP-JSON fixtures (T-000) miss.
- [x] **AC-US7-08**: A `--targets=all` (all 53 agents — `TOTAL_AGENTS`) test case asserts every installable+expressive agent receives a file (de-duped by shared `localSkillsDir` fragment so kimi-cli + qwen-code are not double-counted). Agents with `customSystemPrompt: false` (currently only `mcpjam`) appear in the divergence report as documented skips — silent skips are still a test failure. (T-012 sub-case f GREEN.)

---

### US-008: Registry Publication and Discoverability (P2)
**Project**: vskill

**As a** user who pins an older vskill version
**I want** `skill-builder` available in the verified-skill.com registry so I can install it without upgrading vskill
**So that** I am not forced into HEAD to get the new skill

**Acceptance Criteria**:
- [ ] **AC-US8-01**: After merging, running `vskill submit anton-abyzov/vskill/plugins/skills/skills/skill-builder` succeeds and returns a registry URL.
- [ ] **AC-US8-02**: A sandbox with a pinned older vskill version (e.g., 0.5.80) can `vskill install skill-builder` from the registry and get the published skill.
- [x] **AC-US8-03**: README.md badge count updated from `skills: 7` to `skills: 8`, and CHANGELOG.md has a `### Added` entry for the new `vskill skill` subcommand plus the bundled `skill-builder` skill.
- [x] **AC-US8-04**: README.md "Commands" or equivalent section includes a `vskill skill new|import|list|info|publish` subsection with a usage example (`vskill skill new --prompt "lint markdown" --targets=claude-code,codex`). `--help` output alone does not satisfy this AC.

**Out of scope for US-008** (moved to follow-up): cross-linking `scout` SKILL.md to `skill-builder` — not load-bearing for release, tracked in post-close checklist.

---

### US-009: vskill Release and Umbrella Sync (P1)
**Project**: vskill

**As a** maintainer
**I want** a clean patch release of vskill that ships the new `skill` subcommand and bundled `skill-builder` skill
**So that** users on the latest vskill get the new features immediately, and the umbrella repo is kept in sync

**Acceptance Criteria**:
- [ ] **AC-US9-01**: vskill patch release via `sw:release-npm` succeeds: version bumped, npm package published, GitHub Release created.
- [ ] **AC-US9-02**: The new CLI subcommand `vskill skill` is accessible in the published package (`npx vskill skill --help` lists all subcommands from a clean install).
- [ ] **AC-US9-03**: Umbrella sync commit lands on the umbrella repo main branch following the established pattern (`sync umbrella after vskill v0.5.X release`). **Bundles with T-013a (npm publish)** since the commit message references the published version. The follow-up increment stub portion of T-013d is complete: `0726-skill-gen-vskill-integration` is registered with status `planned`, type `feature`, priority `P3`.
- [x] **AC-US9-04**: No SpecWeave release required for this increment (deliberate — confirms the no-SpecWeave-touch MVP scope). Verified: 0670's diffs are scoped entirely to `repositories/anton-abyzov/vskill/` and `.specweave/increments/0670-*/`. No `repositories/anton-abyzov/specweave/` files modified.

---

## Functional Requirements

### FR-001: No SpecWeave Coupling
The `skill-builder` SKILL.md and `vskill skill` CLI must function without SpecWeave installed. Zero references to `.specweave/`, `specweave` CLI, or SpecWeave-specific state.

### FR-002: Reuse, Do Not Rebuild
All agent-aware generation, 49-agent catalog, install routing, and fallback detection already exist from increments 0665, 0465, 0331. This increment extracts, wraps, and exposes — it does not duplicate or reimplement.

### FR-003: Fallback Order Is A → B → C, Not Parallel
The SKILL.md body must specify the fallback as strict priority: CLI first, browser second, Anthropic plugin last. Never attempt two paths concurrently.

### FR-004: Security Fields Never Silently Dropped
Any frontmatter field under the security-critical set (`allowed-tools`, `context: fork`, `model`) that is dropped or translated for any target MUST appear in the divergence report. Silent loss is a blocking defect.

### FR-005: No Fork of Skill Studio
Honors `feedback_skill_studio_not_fork.md`. This increment extends the existing Skill Studio infrastructure (0465 + 0665). It does not fork, rebrand, or duplicate the workspace UI.

### FR-006: Name Conventions
Skill uses flat directory layout (`skill-builder/SKILL.md`, not nested). Frontmatter `name: skill-builder` (no namespace prefix). Honors `feedback_skill_naming_flat_dirs.md`.

## Success Criteria

- `vskill install skill-builder` succeeds from the registry in a sandbox with zero SpecWeave dependency
- `vskill skill new --prompt "X"` emits to 8 universal targets + divergence report in under 30 seconds
- `vskill skill new --targets=all` emits to all 53 targets without error
- `vskill skill new --engine=anthropic-skill-creator` falls back successfully with clear warning
- CLI integration tests pass (Vitest) and Skill Studio regression test passes (Playwright)
- No regressions in existing `POST /api/skills/generate` HTTP handler (eval-ui tests + Playwright studio regression stay green)
- README + CHANGELOG document the new `vskill skill` subcommand

## Out of Scope

- Rewiring `sw:skill-gen` (SpecWeave) to prefer `vskill skill new` — tracked in a separate follow-up increment
- New agent registrations (49-agent catalog is sufficient for MVP)
- Platform-side (vskill-platform) changes — submission flow is already mature
- Additional subcommands beyond `new | import | list | info | publish`
- Interactive-mode CLI — MVP is flag-driven only
- Integration with SpecWeave's `/sw:increment` flow
- Cross-linking `scout` SKILL.md to `skill-builder` — moved to post-close follow-up checklist (not load-bearing for release)
- Skill Studio UI redesign — 0465 React workspace stays as-is, this increment only consumes it as path B

## Dependencies

- **Existing (from completed increments)**:
  - `vskill/src/eval-server/skill-create-routes.ts:523-573` (agent-aware prompt injection), `:919-1100` (generator body), `isSkillCreatorInstalled()` — from 0665
  - `vskill/src/agents/agents-registry.ts` (53 agents, `filterAgentsByFeatures`, `getAgentCreationProfile`) — from 0665
  - `vskill/src/installer/canonical.ts` (`target-agents`-aware routing), `vskill/src/installer/frontmatter.ts:123-127` (`target-agents` frontmatter field parser) — from 0665
  - `vskill/src/eval-ui/src/pages/workspace/SkillWorkspace.tsx` + EditorPanel/RunPanel/HistoryPanel/DepsPanel/LeftRail (browser-only Skill Studio UI, path B) — from 0465
  - `vskill/src/commands/submit.ts` (`vskill submit` publish flow) — mature
  - `vskill/src/commands/install.ts` (install via SHA-pinned lockfile) — mature
  - Anthropic `skill-creator` as an **Anthropic built-in skill** (not a SpecWeave plugin) detected at `~/.claude/skills/skill-creator/` — fallback target only
- **Tooling**: Vitest (unit + CLI integration via `spawn`/`execa`), Playwright (browser UI regression only), ESM mocking via `vi.hoisted()` + `vi.mock()`.
