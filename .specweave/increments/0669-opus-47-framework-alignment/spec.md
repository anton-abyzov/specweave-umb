---
status: completed
---
# Spec: Opus 4.7 Framework Alignment

**Increment**: 0669-opus-47-framework-alignment
**Type**: framework-refactor
**Project**: specweave
**Source**: Research findings from 3-agent audit (blog-analyst, skill-auditor, stale-detector) — see `research-findings.md`

---

## Problem Statement

Anthropic released Claude Opus 4.7 in 2026 with a set of behavioral and API changes that invalidate several of SpecWeave's long-standing design decisions:

- **Adaptive thinking** replaces fixed Extended Thinking — `thinking.budget_tokens` is no longer supported, and several skill descriptions still claim "uses extended thinking".
- **Reduced default subagent spawning** — the model is now "more judicious about when to delegate", but SpecWeave's `sw:team-lead` explicitly instructs agents to "spawn agents anyway… even if the work seems simple enough to do directly".
- **Reduced default tool-use** — skills need explicit *when/why* tool guidance; SpecWeave's `allowed-tools` blocks list the tools but not the conditions.
- **New `xhigh` effort tier** — described as "best setting for most coding and agentic uses"; `max` is discouraged for routine work.
- **Long-horizon coherence fixes** — 4.7 no longer needs the context-mitigation workarounds SpecWeave accumulated in the 4.5 era (15-task cap, `--simple` mode, state-marker files, task-by-task model switching).
- **Prompt caching** becomes table stakes — static context files (`CLAUDE.md`, `config.json`, `spec.md`, `rubric.md`) are read on every skill invocation without being cached.

Additionally, the skill index has drifted to 47 skills with confirmed redundancy (TDD trio, per-tool `*-sync` stubs, orphan agent templates, overlapping multi-project skills).

This increment realigns SpecWeave's framework (skills, agent templates, workflow mechanics, config) with Opus 4.7 best practices, retires obsolete compromises, and shrinks the skill surface area without user-facing workflow changes.

---

## Goals

1. **Correctness** — no SpecWeave skill instructs the model in ways that contradict documented 4.7 behavior (adaptive thinking, reduced fan-out, `xhigh` default).
2. **Efficiency** — prompt caching on static context files cuts input tokens on repeat skill invocations by ~60%.
3. **Simplification** — shrink the skill index from 47 to ~38 core skills by deprecating, merging, and simplifying stale entries, without removing any user-facing capability.
4. **Forward compatibility** — coexist with Claude Code's native Auto mode (Shift+Tab); do not reinvent what Claude Code now offers.
5. **Backwards safety** — existing increments continue to open, resume, and close; every removed flag has an opt-out alias for at least one minor release.

---

## Non-Goals

- MCP-related changes (blog post does not discuss MCP specifics; defer).
- Memory / auto-memory redesign (4.7 improved context-carry but exposed no new API; defer).
- The 20 non-priority skills (`sw:lsp`, `sw:qa`, `sw:npm`, `sw:release-*`, `sw:ado-*`, `sw:jira-*`, `sw:docs-*`, `sw:umbrella`, `sw:discrepancies`) — audit deferred to a follow-up increment; see research-findings.md §6.
- Redesigning `sw:remotion`, `sw:image`, or other media-generation skills beyond the simplifications already called out.
- Native Claude Code behavior changes (we adapt, we don't fork).

---

## User Stories

Priorities follow the P0–P4 framework in research-findings.md §4. A **P0** story blocks shipping before Opus 4.7 becomes default-on; **P1** is high-impact / low-risk; **P2–P4** are quality, consolidation, and future-telemetry work.

---

### US-001: Adopt adaptive-thinking semantics across all skills

**Priority**: P0
**Project**: specweave
**As a** SpecWeave user on Opus 4.7
**I want** skills that reference "extended thinking" or fixed `thinking.budget_tokens` to use the 4.7 adaptive-thinking prompt-hint pattern instead
**So that** thinking is actually triggered when needed (fixed budgets are silently ignored on 4.7) and my skill output does not mislead other contributors about how the skill works.

**Acceptance Criteria**:

- [x] **AC-US1-01**: `plugins/specweave/skills/judge-llm/SKILL.md` description no longer contains the phrase "extended thinking"; replaced with adaptive-thinking prompt-hint language (e.g., "think carefully and step-by-step — this evaluation is harder than it looks"). (File: `plugins/specweave/skills/judge-llm/SKILL.md`)
- [x] **AC-US1-02**: The same file's body (first 30 lines) no longer contains "ULTRATHINK BY DEFAULT" as a directive; replaced with a prompt-hint block that triggers adaptive thinking without specifying a token budget. (File: `plugins/specweave/skills/judge-llm/SKILL.md`)
- [x] **AC-US1-03**: `plugins/specweave/skills/grill/SKILL.md` includes an adaptive-thinking prompt hint in its review procedure (not a fixed budget). (File: `plugins/specweave/skills/grill/SKILL.md`)
- [x] **AC-US1-04**: No SKILL.md under `plugins/specweave/skills/` contains the literal strings `thinking.budget_tokens`, `budget_tokens:`, or `"thinking": {` outside of code comments explaining the 4.7 migration. (Grep scope: `plugins/specweave/skills/**/SKILL.md`)
- [x] **AC-US1-05**: `src/core/skills/skill-judge.ts` (implementation of `sw:judge-llm`) does not pass a `thinking` parameter to the Anthropic SDK call for 4.7-family models; if a `thinking` parameter exists, it is guarded by a model-version check. (File: `src/core/skills/skill-judge.ts`)
- [x] **AC-US1-06**: `docs/internal/specs/opus-47-migration.md` (new or existing) documents the adaptive-thinking pattern with a before/after example. (File: `.specweave/docs/internal/specs/opus-47-migration.md`)

---

### US-002: Recalibrate subagent-spawning defaults

**Priority**: P0
**Project**: specweave
**As a** SpecWeave user on Opus 4.7
**I want** orchestration skills (`sw:team-lead`, `sw:code-reviewer`, `sw:tdd-cycle`, `sw:do`) to stop forcing subagent spawning for work that can be done directly
**So that** the model's judgment about when to delegate is respected, I pay for fewer wasted agent spawns, and simple tasks complete in one context instead of N.

**Acceptance Criteria**:

- [x] **AC-US2-01**: `plugins/specweave/skills/team-lead/SKILL.md` no longer contains the directive "Even if the work seems simple enough to do directly — spawn agents anyway"; replaced with a heuristic that allows direct execution for 1-domain or <10-task work. (File: `plugins/specweave/skills/team-lead/SKILL.md`, line ~16)
- [x] **AC-US2-02**: `plugins/specweave/skills/team-lead/SKILL.md` defines a quantitative fan-out threshold (e.g., "spawn agents when domains ≥ 3 OR tasks ≥ 15 OR `--parallel` flag set") in the mode-detection section. (File: `plugins/specweave/skills/team-lead/SKILL.md`)
- [x] **AC-US2-03**: `plugins/specweave/skills/code-reviewer/SKILL.md` reduces the reviewer fan-out from 8 parallel specialists + 10 finding-validators to **≤3 reviewers** (security, logic, performance) with inline self-critique replacing the haiku validator pass. (File: `plugins/specweave/skills/code-reviewer/SKILL.md`)
- [x] **AC-US2-04**: `plugins/specweave/skills/code-reviewer/SKILL.md` no longer references the "independent-finding-validator" subroutine that spawns 10 haiku agents. (File: `plugins/specweave/skills/code-reviewer/SKILL.md`, lines ~310-344)
- [x] **AC-US2-05**: `plugins/specweave/skills/increment/SKILL.md` defaults to a **single-agent planner** (PM + Architect combined into one context); 3-agent fan-out is gated behind `--parallel` flag OR `|user-stories|` ≥ 10. (File: `plugins/specweave/skills/increment/SKILL.md`, Step 4a)
- [x] **AC-US2-06**: `plugins/specweave/skills/team-merge/SKILL.md` runs closure inline (no `sw-closer` subagent) when merging ≤5 increments; subagent path kicks in only for larger merges. (File: `plugins/specweave/skills/team-merge/SKILL.md`, lines ~81-92)
- [x] **AC-US2-07**: `plugins/specweave/skills/do/SKILL.md` no longer switches model per task via haiku/sonnet/opus hints; uses a single effort tier (default `xhigh`). (File: `plugins/specweave/skills/do/SKILL.md`, line ~158)

---

### US-003: Introduce prompt caching for static context files

**Priority**: P1
**Project**: specweave
**As a** SpecWeave user
**I want** skills that read the same static files on every invocation (`CLAUDE.md`, `.specweave/config.json`, the active `spec.md`, `rubric.md`) to use Anthropic prompt caching
**So that** repeat skill invocations within the 5-minute cache window cost ~60% fewer input tokens without changing any behavior.

**Acceptance Criteria**:

- [x] **AC-US3-01**: `src/core/cache/static-context-loader.ts` exists and exposes a helper that returns `cache_control: { type: "ephemeral" }` blocks for a declared list of static files. (File: `src/core/cache/static-context-loader.ts`)
- [x] **AC-US3-02**: `.specweave/config.json` schema includes a new `cache.staticContextFiles` array with defaults `["CLAUDE.md", ".specweave/config.json", ".specweave/increments/<active>/spec.md", ".specweave/increments/<active>/rubric.md"]`. (File: `src/core/config/schema.ts`)
- [x] **AC-US3-03**: `sw:judge-llm` implementation uses the static-context-loader when assembling the Anthropic API request; cached breakpoints are placed before any dynamic task content. (File: `src/core/skills/skill-judge.ts`)
- [x] **AC-US3-04**: `sw:grill`, `sw:code-reviewer`, and `sw:done` SKILL.md files include a "Prompt Caching" section explaining which files are cached and how to extend the cache list. (Files: `plugins/specweave/skills/{grill,code-reviewer,done}/SKILL.md`)
- [x] **AC-US3-05**: An integration test in `test/integration/prompt-caching.test.ts` verifies that two consecutive `sw:judge-llm` invocations on the same increment produce a second-call `cache_read_input_tokens` > 0 in the Anthropic response. (File: `test/integration/prompt-caching.test.ts`)
- [x] **AC-US3-06**: Telemetry records cache hit rate per skill invocation and exposes it via `sw:analytics --cache-stats`. (Files: `src/core/telemetry/cache-metrics.ts`, `plugins/specweave/skills/analytics/SKILL.md`)

---

### US-004: Simplify planning fan-out (sw:increment single-agent default)

**Priority**: P1
**Project**: specweave
**As a** SpecWeave user running `/sw:increment` for a small-to-medium feature
**I want** the planner to run as a single agent by default and only fan out to PM + Architect (+ Planner) when the feature is genuinely large
**So that** small increments plan in one fast context instead of three round-tripping contexts, and I still get parallelism when I actually need it.

**Acceptance Criteria**:

- [x] **AC-US4-01**: `plugins/specweave/skills/increment/SKILL.md` Step 4 (spec writing) runs in a single agent by default; Step 4a (team-based delegation) is gated behind explicit trigger conditions documented in the file. (File: `plugins/specweave/skills/increment/SKILL.md`)
- [x] **AC-US4-02**: Fan-out triggers documented in Step 4a: `--parallel` flag set, user-story count ≥ 10, OR explicit keywords ("parallel", "team lead", "fan out") in the feature description. Absent any trigger, single-agent path is taken. (File: `plugins/specweave/skills/increment/SKILL.md`)
- [x] **AC-US4-03**: `--parallel` flag is parsed by `src/cli/commands/increment.ts` and flows into the skill invocation. (File: `src/cli/commands/increment.ts`)
- [x] **AC-US4-04**: Single-agent planning produces the same output files (`spec.md`, `plan.md`, `tasks.md`, `rubric.md`) with the same structure as the 3-agent path; a snapshot test verifies parity. (File: `test/integration/increment-single-agent-parity.test.ts`)
- [x] **AC-US4-05**: `docs/internal/specs/planning-modes.md` documents single-agent vs parallel modes with a decision matrix (feature size, complexity, opt-in flag). (File: `.specweave/docs/internal/specs/planning-modes.md`)

---

### US-005: Retire legacy context-mitigation compromises

**Priority**: P0 (15-task cap removal), P1 (everything else in this story)
**Project**: specweave
**As a** SpecWeave user on Opus 4.7 (with long-horizon coherence fixes)
**I want** the 4.5-era context-mitigation workarounds removed or raised
**So that** the framework stops fighting the model's actual capabilities, and workflows that were forcibly split now complete in one agent run.

**Acceptance Criteria**:

- [x] **AC-US5-01**: `plugins/specweave/skills/team-lead/SKILL.md` raises the per-agent task cap from **15 to 40**; the `TASK_CAP` constant (or equivalent) is updated and the surrounding prose explains the 4.7 rationale. (File: `plugins/specweave/skills/team-lead/SKILL.md`, lines ~624-639)
- [x] **AC-US5-02**: `--simple` mode is removed from `plugins/specweave/skills/auto/SKILL.md` as a default path; a `--simple-compat` alias remains for one minor release and emits a deprecation warning. (File: `plugins/specweave/skills/auto/SKILL.md`, lines ~47-57)
- [x] **AC-US5-03**: State-marker files `skill-chain-{increment-id}.json` are no longer written by `sw:pm` or `sw:architect`; the PreToolUse guard in `src/core/hooks/pretooluse-guard.ts` is rewritten to use `TaskGet`-based state instead of filesystem markers. (Files: `plugins/specweave/skills/pm/SKILL.md` lines ~18-34, `plugins/specweave/skills/architect/SKILL.md` lines ~9-24, `src/core/hooks/pretooluse-guard.ts`)
- [x] **AC-US5-04**: Grill default confidence threshold is lowered from 70 to 50 in `plugins/specweave/skills/grill/SKILL.md`; the `quality.grillConfidenceThreshold` config knob in `.specweave/config.json` allows override. (File: `plugins/specweave/skills/grill/SKILL.md`, lines ~156-173)
- [x] **AC-US5-05**: PM interview state markers (`.specweave/state/interview-*.json`) are removed; interview state lives in memory for the duration of the planning session. (File: `plugins/specweave/skills/pm/SKILL.md`, lines ~79-96)
- [x] **AC-US5-06**: Heartbeat stuck-detection thresholds in `plugins/specweave/skills/team-lead/SKILL.md` are raised (no-progress window from 2min → 5min; total-stuck from 10min → 20min); the section is retained (not removed) because long-horizon coherence ≠ infinite patience. (File: `plugins/specweave/skills/team-lead/SKILL.md`, lines ~928-979)
- [x] **AC-US5-07**: Code-review fix-loop cap is raised from 3 to 5 iterations in `plugins/specweave/skills/done/SKILL.md`. (File: `plugins/specweave/skills/done/SKILL.md`, lines ~58-67)
- [x] **AC-US5-08**: Hardcoded token budgets (400/500/600) in `plugins/specweave/skills/pm/SKILL.md` and `plugins/specweave/skills/brainstorm/SKILL.md` are raised 3×; replaced with `config.quality.tokenBudgets` defaults. (Files: `plugins/specweave/skills/pm/SKILL.md` lines ~163-168, `plugins/specweave/skills/brainstorm/SKILL.md` lines ~508-524)
- [x] **AC-US5-09**: `team-lead` active-phase forbidden-list (no closure skills loaded) is removed from `plugins/specweave/skills/team-lead/SKILL.md` lines ~863-888; closure skills may load at any time. (File: `plugins/specweave/skills/team-lead/SKILL.md`)
- [x] **AC-US5-10**: Migration notes in `.specweave/docs/internal/specs/opus-47-migration.md` cover every retired workaround with a before/after and an opt-out path where applicable.

---

### US-006: Deprecate stale skills covered by command families or Claude Code natives

**Priority**: P1
**Project**: specweave
**As a** SpecWeave user
**I want** skills that are now thin wrappers over `sw-{tool}:sync` command families (or Claude Code natives like plan mode, TodoWrite, Agent tool) to be deprecated with clear migration guidance
**So that** the skill index is discoverable and the 7 deprecated skills stop appearing as first-class options in `/sw:help`.

**Acceptance Criteria**:

- [x] **AC-US6-01**: The following 7 skills have a deprecation notice at the top of their SKILL.md frontmatter description (`[DEPRECATED]` prefix) AND a migration section pointing to the replacement: `sw:github-sync`, `sw:jira-sync`, `sw:ado-sync`, `sw:tdd-red`, `sw:tdd-green`, `sw:tdd-refactor`, `sw:github-issue-standard`. (Files: `plugins/specweave/skills/{github-sync,jira-sync,ado-sync,tdd-red,tdd-green,tdd-refactor,github-issue-standard}/SKILL.md`)
- [x] **AC-US6-02**: `sw:github-issue-standard` content is moved to `.specweave/docs/internal/specs/github-issue-standard.md` and the skill becomes a thin redirect ("see docs/internal/specs/github-issue-standard.md"). (Files: `.specweave/docs/internal/specs/github-issue-standard.md`, `plugins/specweave/skills/github-issue-standard/SKILL.md`)
- [x] **AC-US6-03**: `plugins/specweave/skills/help/SKILL.md` hides deprecated skills from the default `/sw:help` listing; a `--deprecated` flag surfaces them with their migration notes. (File: `plugins/specweave/skills/help/SKILL.md`)
- [x] **AC-US6-04**: Each deprecated skill logs a one-time deprecation warning when invoked (via console.warn-style output at the top of the skill body). (Files: same as AC-US6-01)
- [x] **AC-US6-05**: `docs/internal/specs/skill-deprecation-policy.md` documents the deprecation lifecycle (deprecated → hidden → removed across 3 minor releases) and lists the current batch. (File: `.specweave/docs/internal/specs/skill-deprecation-policy.md`)
- [x] **AC-US6-06**: No active skill (non-deprecated) references any of the 7 deprecated skills as a "See also" or chain target; CI grep check enforces this. (File: `.github/workflows/skill-lint.yml`)

---

### US-007: Consolidate redundant skills

**Priority**: P1 (TDD trio), P2 (everything else)
**Project**: specweave
**As a** SpecWeave user
**I want** overlapping skills merged into a canonical skill with mode flags
**So that** I don't have to remember which of three TDD skills to invoke, and the framework has a single source of truth per concern.

**Acceptance Criteria**:

- [x] **AC-US7-01**: `sw:tdd-red`, `sw:tdd-green`, and `sw:tdd-refactor` are merged into `sw:tdd-cycle` with `--phase red|green|refactor|all` flag; `--phase all` runs the full cycle (current `tdd-cycle` behavior). (File: `plugins/specweave/skills/tdd-cycle/SKILL.md`)
- [x] **AC-US7-02**: `sw:github-multi-project` and `sw:ado-multi-project` are merged into `sw:multi-project` with `--tool github|ado|jira` flag; JIRA support is added as part of the merge. (File: `plugins/specweave/skills/multi-project/SKILL.md`)
- [x] **AC-US7-03**: `sw:github-resource-validator`, `sw:jira-resource-validator`, and `sw:ado-resource-validator` are kept (1:1 per tool due to divergent APIs) but all three use a shared base module at `src/core/validators/resource-base.ts`. (File: `src/core/validators/resource-base.ts`)
- [x] **AC-US7-04**: `sw:team-build` preset logic is folded into `sw:team-lead --preset <name>`; `sw:team-build` becomes a thin alias that prints a deprecation warning and calls `sw:team-lead --preset`. (Files: `plugins/specweave/skills/team-lead/SKILL.md`, `plugins/specweave/skills/team-build/SKILL.md`)
- [x] **AC-US7-05**: `sw:plan` becomes `sw:increment --regenerate-plan` (regenerate-only mode) and is marked deprecated for standalone use. (File: `plugins/specweave/skills/plan/SKILL.md`)
- [x] **AC-US7-06**: `sw:close-all` is simplified to ~40 lines (today ~200 lines) by delegating the per-increment closure to `sw:done` and keeping only the batch-discovery loop. (File: `plugins/specweave/skills/close-all/SKILL.md`)
- [x] **AC-US7-07**: Consolidated skills preserve a machine-readable alias map in `plugins/specweave/marketplace.json` so existing `/sw:tdd-red` invocations route to `/sw:tdd-cycle --phase red` with a one-time migration warning. (File: `plugins/specweave/marketplace.json`)

---

### US-008: Remove orphan agent templates and extract shared protocol

**Priority**: P1
**Project**: specweave
**As a** SpecWeave maintainer
**I want** dead agent templates deleted and duplicated agent-protocol boilerplate extracted to a shared file
**So that** every team-lead template doesn't re-declare the same 80 lines of messaging/TaskUpdate/shutdown boilerplate.

**Acceptance Criteria**:

- [x] **AC-US8-01**: `plugins/specweave/skills/team-lead/agents/reviewer-logic.md` and `plugins/specweave/skills/team-lead/agents/reviewer-performance.md` are either wired into the REVIEW mode section of `team-lead/SKILL.md` OR deleted; a git-grep confirms no other file references these two templates. (Files: `plugins/specweave/skills/team-lead/agents/*`, `plugins/specweave/skills/team-lead/SKILL.md`)
- [x] **AC-US8-02**: A new file `plugins/specweave/skills/team-lead/agents/_protocol.md` contains the shared agent protocol (messaging patterns, TaskUpdate contract, shutdown_response handling, PLAN_READY / COMPLETION signal format). (File: `plugins/specweave/skills/team-lead/agents/_protocol.md`)
- [x] **AC-US8-03**: All remaining agent templates under `plugins/specweave/skills/team-lead/agents/` reference `_protocol.md` via a `See shared protocol: _protocol.md` header block; duplicated protocol lines are removed from each template. (Files: `plugins/specweave/skills/team-lead/agents/*.md`)
- [x] **AC-US8-04**: Total line count across `team-lead/agents/*.md` is reduced by ≥30% after the refactor; a before/after line-count is recorded in the migration doc. (File: `.specweave/docs/internal/specs/opus-47-migration.md`)
- [x] **AC-US8-05**: `src/core/team-lead/template-loader.ts` (or the current equivalent) auto-prepends `_protocol.md` content when spawning an agent from a template, so agents see a unified prompt. (File: `src/core/team-lead/template-loader.ts`)

---

### US-009: Add quality.thinkingBudget and cache.staticContextFiles config knobs

**Priority**: P1
**Project**: specweave
**As a** SpecWeave user / maintainer
**I want** centralized config knobs for thinking-budget hints and static-context cache lists
**So that** I can tune every skill's behavior from `.specweave/config.json` instead of editing individual SKILL.md files.

**Acceptance Criteria**:

- [x] **AC-US9-01**: `.specweave/config.json` schema adds `quality.thinkingBudget` with values `"low" | "medium" | "high" | "xhigh" | "max"` and default `"xhigh"`. (File: `src/core/config/schema.ts`)
- [x] **AC-US9-02**: `.specweave/config.json` schema adds `cache.staticContextFiles` (array of glob-style paths) with the default list from AC-US3-02. (File: `src/core/config/schema.ts`)
- [x] **AC-US9-03**: `.specweave/config.json` schema adds `quality.grillConfidenceThreshold` (number 0-100, default 50) referenced by `sw:grill`. (File: `src/core/config/schema.ts`)
- [x] **AC-US9-04**: `.specweave/config.json` schema adds `quality.tokenBudgets` as a map (e.g., `{ "pm.interview": 1500, "brainstorm.idea": 1800 }`) overriding the hardcoded budgets from US-005. (File: `src/core/config/schema.ts`)
- [x] **AC-US9-05**: Every config knob added in this story has a documented default, an allowed-values description, and an entry in `.specweave/docs/internal/specs/config-reference.md`. (File: `.specweave/docs/internal/specs/config-reference.md`)
- [x] **AC-US9-06**: A config migration script (`scripts/migrate-config-0669.ts`) upgrades existing `.specweave/config.json` files in place, adding the new knobs with defaults if absent. (File: `scripts/migrate-config-0669.ts`)
- [x] **AC-US9-07**: The `specweave doctor` diagnostic reports missing or unknown keys under `quality.*` and `cache.*`. (File: `src/cli/commands/doctor.ts`)

---

### US-010: Update tool-use guidance (add when/why to allowed-tools blocks)

**Priority**: P2
**Project**: specweave
**As a** SpecWeave user on Opus 4.7 (reduced default tool-use)
**I want** skill frontmatter and bodies to document *when* and *why* each tool is used, not just *which* tools are allowed
**So that** the model (which is now more conservative about calling tools) has explicit invocation conditions and doesn't skip a necessary call.

**Acceptance Criteria**:

- [x] **AC-US10-01**: `plugins/specweave/skills/judge-llm/SKILL.md` frontmatter `allowed-tools` line is followed by a `tool-use-rationale` block (plain-text, not YAML) explaining when each of Read/Grep/Glob/Bash is called. (File: `plugins/specweave/skills/judge-llm/SKILL.md`)
- [x] **AC-US10-02**: The same pattern is applied to `sw:grill`, `sw:code-reviewer`, `sw:do`, `sw:pm`, `sw:architect`, `sw:done`, `sw:team-lead`, `sw:increment`. (Files: respective SKILL.md files)
- [x] **AC-US10-03**: `plugins/specweave/.lint/skill-lint.ts` (new or existing) enforces the presence of tool-use-rationale for any skill that declares `allowed-tools`. CI fails if missing. (File: `plugins/specweave/.lint/skill-lint.ts`)
- [x] **AC-US10-04**: `.specweave/docs/internal/specs/skill-authoring-guide.md` is updated with a "Documenting Tool Use" section and a before/after example. (File: `.specweave/docs/internal/specs/skill-authoring-guide.md`)

---

### US-011: Document effort-level conventions (default xhigh, avoid max)

**Priority**: P2
**Project**: specweave
**As a** SpecWeave user / skill author
**I want** framework-wide guidance on which effort level to use per skill class (planning, implementation, review, closure)
**So that** skills default to `xhigh` per the 4.7 recommendation and `max` is reserved for exceptional cases where its overthinking risk is accepted.

**Acceptance Criteria**:

- [x] **AC-US11-01**: `.specweave/docs/internal/specs/effort-levels.md` is created and documents: default `xhigh` for planning/implementation/review, `high` for short-and-sweet skills (e.g., `sw:help`), `max` opt-in only via `--effort max` flag with warning. (File: `.specweave/docs/internal/specs/effort-levels.md`)
- [x] **AC-US11-02**: `plugins/specweave/skills/judge-llm/SKILL.md` documents effort-level choice (replacing the removed "ULTRATHINK BY DEFAULT" line) — default `xhigh`, `--effort max` opt-in. (File: `plugins/specweave/skills/judge-llm/SKILL.md`)
- [x] **AC-US11-03**: `sw:grill`, `sw:code-reviewer` SKILL.md files declare their default effort in a "Model Configuration" section. (Files: `plugins/specweave/skills/{grill,code-reviewer}/SKILL.md`)
- [x] **AC-US11-04**: `plugins/specweave/skills/increment/SKILL.md` line 4 (currently `model: opus`) is updated to also document the effort-level expectation OR that directive is moved into the body with the 4.7 rationale. (File: `plugins/specweave/skills/increment/SKILL.md`)
- [x] **AC-US11-05**: CLI `--effort <level>` flag is parsed by the core dispatcher and propagated into skill invocations (`src/cli/dispatcher.ts`). (File: `src/cli/dispatcher.ts`)

---

### US-012: Coexist with Claude Code native auto mode (Shift+Tab)

**Priority**: P2
**Project**: specweave
**As a** SpecWeave user on Claude Code Max (Opus 4.7)
**I want** `sw:auto` to detect and defer to the native Claude Code Auto mode when available, rather than maintaining a parallel autonomous-execution loop
**So that** I don't get two competing "run-until-done" behaviors and the framework stays slim.

**Acceptance Criteria**:

- [x] **AC-US12-01**: `plugins/specweave/skills/auto/SKILL.md` has a "Native Auto Mode" section documenting Claude Code's Shift+Tab auto mode and explaining when `sw:auto` is still preferred (increment-aware gates, external sync hooks). (File: `plugins/specweave/skills/auto/SKILL.md`)
- [x] **AC-US12-02**: When `sw:auto` is invoked within Claude Code, the skill prints a one-time advisory: "Claude Code native auto mode (Shift+Tab) is available. Use sw:auto only when you need increment-aware gates or external sync." (File: `plugins/specweave/skills/auto/SKILL.md`)
- [x] **AC-US12-03**: `sw:auto --respect-native` flag (default true on Claude Code) enables the advisory; `--force-sw-auto` suppresses it for power users. (File: `src/cli/commands/auto.ts`)
- [x] **AC-US12-04**: `.specweave/docs/internal/specs/auto-mode-decision-tree.md` documents when to use native Auto vs `sw:auto` with concrete examples. (File: `.specweave/docs/internal/specs/auto-mode-decision-tree.md`)
- [x] **AC-US12-05**: `sw:auto` retains `/sw:auto-status` and `/sw:cancel-auto` as first-class commands (no changes) — the coexistence does not remove existing functionality. (File: `plugins/specweave/skills/auto-status/SKILL.md`)

---

## Non-Functional Requirements

### NFR-1: Backwards Compatibility

- **NFR-1.1**: Every existing increment under `.specweave/increments/` continues to open, resume, execute, and close after the 0669 changes. A regression test suite at `test/integration/backwards-compat-0669.test.ts` exercises at least 5 archived increments end-to-end.
- **NFR-1.2**: `.specweave/state/interview-*.json` and `skill-chain-*.json` files that exist in the working tree at upgrade time are tolerated (not read, but not errored) until the next `sw:done` cleanup pass.
- **NFR-1.3**: Any CLI flag removed by this increment (`--simple`, standalone `sw:tdd-red`, etc.) has an alias or `--<name>-compat` variant that emits a deprecation warning and still works for one minor release.
- **NFR-1.4**: `marketplace.json` retains entries for deprecated skills (with `deprecated: true` flag) for at least two minor releases so external tooling (e.g., `vskill install`) does not break on missing IDs.

### NFR-2: Opt-Out Paths

- **NFR-2.1**: `quality.thinkingBudget` can be set to `"legacy"` in `.specweave/config.json` to re-enable pre-4.7 behavior (passes fixed `thinking` parameter) for users still on 4.6 or earlier.
- **NFR-2.2**: `sw:increment --parallel` forces the 3-agent fan-out path even for small features (explicit opt-in to the old behavior).
- **NFR-2.3**: `sw:code-reviewer --full-fanout` restores the 8-reviewer + 10-validator path for users who want maximum coverage and accept the cost.
- **NFR-2.4**: `cache.staticContextFiles: []` (empty array) disables prompt caching for users who want deterministic token accounting (e.g., CI benchmarks).

### NFR-3: Migration Documentation

- **NFR-3.1**: `.specweave/docs/internal/specs/opus-47-migration.md` is the canonical migration guide; it covers every AC retirement, every opt-out flag, and a before/after code sample for each user-facing change.
- **NFR-3.2**: `CHANGELOG.md` entry for the 0669 release explicitly calls out the breaking-ish changes (fixed extended-thinking removed; `--simple` deprecated; state markers gone) with links to the migration doc.
- **NFR-3.3**: `README.md` "Upgrading" section references the migration doc and lists the three P0 fixes.
- **NFR-3.4**: Release notes emitted by `sw-release:npm` for the 0669 release include an "Opus 4.7 Alignment" heading.

### NFR-4: CI / Telemetry Evidence

- **NFR-4.1**: CI job `skill-lint` passes — no SKILL.md contains the retired phrases (`extended thinking`, `ULTRATHINK BY DEFAULT`, `spawn agents anyway`, `thinking.budget_tokens`).
- **NFR-4.2**: CI job `skill-count` reports total non-deprecated skills ≤ 40 (target 38).
- **NFR-4.3**: `specweave analytics --cache-stats` (new) reports cache hit rate ≥ 40% for repeat `sw:judge-llm` and `sw:done` invocations within a session. Measured via an integration test.
- **NFR-4.4**: Agent-spawn count for a baseline 5-task increment (documented in `test/fixtures/baseline-increment/`) drops from N_old (current) to ≤ N_old × 0.5 after the 0669 changes — measured by a benchmark at `test/benchmarks/agent-spawn-count.bench.ts`.

### NFR-5: Quality Gates

- **NFR-5.1**: `/sw:grill` report on this increment shows zero critical, zero high findings before `/sw:done` can close it.
- **NFR-5.2**: `/sw:judge-llm` report on representative skill changes (sampling at least `judge-llm/SKILL.md`, `team-lead/SKILL.md`, `code-reviewer/SKILL.md`) shows a verdict of PASS or PASS_WITH_NOTES.
- **NFR-5.3**: Unit + integration test coverage on new code paths (static-context-loader, config schema additions, alias routing in marketplace.json) ≥ 90% lines.

---

## Scope Boundaries

### In Scope

- The **27 priority skills** identified in research-findings.md §2 and §3:
  `sw:team-lead`, `sw:increment`, `sw:do`, `sw:done`, `sw:pm`, `sw:architect`, `sw:grill`, `sw:judge-llm`, `sw:code-reviewer`, `sw:plan`, `sw:auto`, `sw:auto-status`, `sw:brainstorm`, `sw:close-all`, `sw:team-merge`, `sw:team-build`, `sw:tdd-cycle`, `sw:tdd-red`, `sw:tdd-green`, `sw:tdd-refactor`, `sw:github-sync`, `sw:jira-sync`, `sw:ado-sync`, `sw:github-multi-project`, `sw:ado-multi-project`, `sw:github-issue-standard`, `sw:help`.
- The **14 agent templates** under `plugins/specweave/skills/team-lead/agents/`.
- The **config schema** at `src/core/config/schema.ts`.
- The **migration documentation** under `.specweave/docs/internal/specs/`.
- The **PreToolUse guard** at `src/core/hooks/pretooluse-guard.ts`.
- The **skill-judge implementation** at `src/core/skills/skill-judge.ts`.

### Out of Scope (deferred to follow-up increment)

- The **20 non-priority skills** (see research-findings.md §6): `sw:lsp`, `sw:qa`, `sw:npm`, `sw:release-*` (6 skills), `sw:ado-*` (remaining 8 after consolidation), `sw:jira-*` (remaining 6 after consolidation), `sw:docs-*` (6 skills), `sw:umbrella`, `sw:discrepancies`, `sw:skill-gen`, `sw:image`, `sw:video`, `sw:remotion`.
- **MCP-related changes** — no 4.7 blog content on MCP.
- **Memory / auto-memory redesign** — 4.7 improved context-carry but introduced no new API.
- **User-facing workflow changes** — no command renames, no increment-folder restructure, no spec.md / tasks.md format changes.
- **Skill removal** — only deprecation; removal is a separate increment after the deprecation window closes.
- **Anthropic SDK version bump** — the skill-judge.ts changes assume current SDK; a bump is deferred.

---

## Success Metrics

Measurable outcomes once this increment ships:

1. **Skill count**: 47 → ≤40 non-deprecated skills (target 38).
2. **Input token cost** (per `sw:judge-llm` invocation on the same increment): ≥50% reduction on the second call within 5-min cache window.
3. **Agent-spawn count** (baseline 5-task increment): ≥50% reduction.
4. **Planning time** (small feature, <5 user stories): single-agent path completes in ≤60% of the current 3-agent path's wall-clock.
5. **CI enforcement**: `skill-lint` catches ≥10 distinct retired phrases and blocks PRs introducing them.
6. **Zero regressions**: All existing increments open, resume, and close unchanged; `backwards-compat-0669.test.ts` is green.

---

## Priority Summary

| Tier | Count | Stories |
|------|-------|---------|
| P0   | 3     | US-001, US-002, US-005 (partial — the 15-task cap portion) |
| P1   | 7     | US-003, US-004, US-005 (remainder), US-006, US-007 (TDD portion), US-008, US-009 |
| P2   | 3     | US-007 (non-TDD portion), US-010, US-011, US-012 |
| P3   | 0     | (P3 items from research-findings.md §4 are absorbed into US-006/US-007 where appropriate) |
| P4   | 0     | (P4 telemetry items deferred to a follow-up increment) |

Total: **12 user stories, 77 acceptance criteria, 21 non-functional requirements**.

---

## Open Questions (for Architect + implementation)

These are explicitly *not* resolved in this spec and are left for the Architect's plan.md:

- **OQ-1**: Exact sequencing of state-marker removal (US-005 AC-03) vs PreToolUse guard rewrite — which lands first to avoid a window where the guard reads missing files?
- **OQ-2**: Alias routing mechanism for deprecated skills (US-007 AC-07) — is it a `marketplace.json` field, a runtime translator in the CLI dispatcher, or both?
- **OQ-3**: Prompt-cache breakpoint strategy (US-003) — one breakpoint per file, or one aggregated breakpoint for all static context? (4.7 allows up to 4 breakpoints per request.)
- **OQ-4**: Model-version detection for US-001 AC-05 — string match on the model ID, or a version-range check via SDK helper?

---

## References

- `research-findings.md` — consolidated audit from blog-analyst, skill-auditor, stale-detector (2026-04-16)
- Anthropic blog: "Introducing Claude Opus 4.7" (2026)
- Current skill sources: `plugins/specweave/skills/**/SKILL.md`
- Current agent templates: `plugins/specweave/skills/team-lead/agents/`
- SpecWeave CLAUDE.md (umbrella repo): governing rules for increments, plan mode, auto-closure
