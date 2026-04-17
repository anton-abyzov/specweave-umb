# Plan: Opus 4.7 Framework Alignment

**Increment**: 0669-opus-47-framework-alignment
**Type**: framework-refactor
**Project**: specweave
**Source of truth spec**: `spec.md` (12 user stories, 77 ACs)
**Source repo**: `repositories/anton-abyzov/specweave/`
**Target npm package**: `specweave` (currently v1.0.575)

---

## Overview

This increment realigns SpecWeave's skill framework with Claude Opus 4.7's behavioral changes — adaptive thinking, reduced default subagent fan-out, the new `xhigh` effort tier, and long-horizon coherence improvements. The scope is defensive (stop instructing the model in ways 4.7 silently ignores or contradicts) and consolidating (retire 4.5-era context-mitigation workarounds that the model no longer needs).

The execution strategy is a **5-wave rollout** against a single `specweave` npm version bump (1.0.575 → 1.1.0, minor bump per semver). Each wave is independently shippable, testable, and revertible. Earlier waves (P0) carry the most risk because they change defaults; later waves (P3–P4) are surface-area consolidation. Between every wave, we release a dev build to the marketplace, run the backwards-compatibility test suite, and verify telemetry on a canary increment in the umbrella repo before promoting to stable.

Key technical pillars: (a) a new `src/core/cache/static-context-loader.ts` module implements prompt caching via Anthropic SDK `cache_control` breakpoints driven by a declared `cache.staticContextFiles` list in config; (b) the skill-chain-enforcement-guard is rewritten to use `TaskGet`-based state instead of filesystem state markers; (c) deprecation routing lives in `plugins/specweave/marketplace.json` so existing `/sw:tdd-red` invocations silently route to `/sw:tdd-cycle --phase red` for one minor release. No user-facing workflow changes — all breaking changes have opt-out flags documented in `opus-47-migration.md`.

---

## Execution Phases (Wave-Based Rollout)

Each wave ends with a release tag (`v1.1.0-wave1`, etc.) and a sign-off gate (skill-lint CI green + backwards-compat suite green + canary increment smoke test).

### Wave 1 — P0 Ship-Blocking Correctness Fixes

**Goal**: Remove SKILL.md content that Opus 4.7 silently ignores or that contradicts documented 4.7 behavior. No behavior change for users; pure correctness of the meta-prompt.

**User stories covered**: US-001 (adaptive thinking), US-002 AC-01..02 (team-lead "spawn anyway" anti-pattern), US-005 AC-01 (15-task cap → 40).

**Files touched** (~6):
- `plugins/specweave/skills/judge-llm/SKILL.md` (remove "ULTRATHINK BY DEFAULT" directive and "extended thinking" from frontmatter; add adaptive-thinking prompt hint)
- `plugins/specweave/skills/grill/SKILL.md` (add adaptive-thinking hint to review procedure)
- `plugins/specweave/skills/team-lead/SKILL.md` (remove "spawn agents anyway"; raise TASK_CAP 15→40; document quantitative fan-out thresholds)
- `src/core/skills/skill-judge.ts` (guard `thinking` parameter behind model-version check)
- `.specweave/docs/internal/specs/opus-47-migration.md` (create; document Wave 1 changes with before/after)
- `.github/workflows/skill-lint.yml` (new: enforce no retired phrases in SKILL.md)

**Migration strategy**: Pure find-and-replace on SKILL.md text plus one guarded `if` in skill-judge.ts. No state-migration code. Existing increments unaffected (TASK_CAP is read at team-lead spawn time, not persisted).

**Rollback plan**: `git revert` the wave commit — SKILL.md is text, no data state involved. The model-version guard in skill-judge.ts falls back to legacy behavior if `quality.thinkingBudget: "legacy"` is set in config.

**Sign-off gate**: (a) `skill-lint` CI job green; (b) backwards-compat suite green; (c) canary: run `/sw:grill` on archived increment 0600; verify no error and no "extended thinking" phrase in output.

---

### Wave 2 — P1 High-Leverage Wins

**Goal**: Land prompt caching, deprecate the TDD trio + sync stubs, and delete orphan agent templates. These changes have high impact-per-byte and near-zero risk.

**User stories covered**: US-003 (prompt caching), US-004 (single-agent planner default), US-006 (deprecate 7 stale skills), US-007 AC-01 (TDD trio merge), US-008 (orphan templates + shared protocol), US-009 (config schema additions).

**Files touched** (~22):
- **New code**: `src/core/cache/static-context-loader.ts`, `src/core/config/schema.ts` (extend), `scripts/migrate-config-0669.ts`, `src/cli/commands/doctor.ts` (extend)
- **New skill**: `plugins/specweave/skills/team-lead/agents/_protocol.md`
- **New docs**: `.specweave/docs/internal/specs/config-reference.md`, `skill-deprecation-policy.md`, `planning-modes.md`
- **SKILL.md edits** (deprecation notices, prompt-caching sections): `github-sync`, `jira-sync`, `ado-sync`, `tdd-red`, `tdd-green`, `tdd-refactor`, `github-issue-standard`, `grill`, `code-reviewer`, `done`, `increment`, `help`
- **Agent templates collapsed**: `team-lead/agents/*.md` (all templates reference `_protocol.md`)
- **Deletes (or keep-with-redirect)**: `team-lead/agents/reviewer-logic.md`, `reviewer-performance.md` — delete unless wired into REVIEW mode (decide per US-008 AC-01)
- **Marketplace**: `plugins/specweave/marketplace.json` (add `deprecated: true` flag on 7 skills; add alias routing entries)
- **Test**: `test/integration/prompt-caching.test.ts` (new)

**Migration strategy**: 
1. Land `static-context-loader.ts` and config schema additions first (additive, no behavior change).
2. Run `scripts/migrate-config-0669.ts` during `specweave doctor` and at next `specweave` CLI invocation (idempotent — adds missing keys with defaults).
3. Turn on prompt caching in `sw:judge-llm` implementation (the first skill to use it), verify with integration test.
4. Apply `deprecated: true` flags to 7 skills; route `/sw:tdd-red` → `/sw:tdd-cycle --phase red` via marketplace alias. Deprecation warning is a one-line `console.warn` at the top of each deprecated SKILL.md body.
5. Collapse agent templates: extract `_protocol.md`, update each domain template to remove duplicated content, verify template-loader auto-prepends `_protocol.md`.

**Rollback plan**:
- Prompt caching: set `cache.staticContextFiles: []` in config to disable; existing skill works the same.
- TDD trio deprecation: remove `deprecated: true` from marketplace; skills still exist and work.
- Config migration: script is reversible (generates backup `.specweave/config.json.bak-0669` before mutating).

**Sign-off gate**: (a) prompt-caching integration test shows `cache_read_input_tokens > 0` on second call; (b) `/sw:tdd-red` alias test (invoke in a sandbox, verify it routes to tdd-cycle with deprecation warning); (c) backwards-compat suite green; (d) line-count check: `team-lead/agents/*.md` reduced ≥30% (AC-US8-04).

---

### Wave 3 — P2 Quality Improvements

**Goal**: Collapse code-reviewer fan-out, retire `--simple` mode, remove state-marker files, and add tool-use rationale blocks.

**User stories covered**: US-002 AC-03..04 (code-reviewer collapse), US-005 AC-02..09 (state markers + `--simple` + thresholds + fix-loop), US-010 (tool-use rationale), US-011 (effort-level conventions), US-012 (auto-mode coexistence).

**Files touched** (~18):
- `plugins/specweave/skills/code-reviewer/SKILL.md` (8 reviewers → 3; remove haiku validator fan-out; add full-fanout opt-in flag)
- `plugins/specweave/skills/auto/SKILL.md` (remove `--simple` from default path; keep `--simple-compat` alias with warning; add Native Auto section)
- `plugins/specweave/skills/pm/SKILL.md` (remove state-marker STEP 0; remove interview-state-markers section)
- `plugins/specweave/skills/architect/SKILL.md` (remove state-marker STEP 0)
- `plugins/specweave/skills/grill/SKILL.md` (lower default confidence threshold 70→50; read from `quality.grillConfidenceThreshold`)
- `plugins/specweave/skills/done/SKILL.md` (raise fix-loop cap 3→5)
- `plugins/specweave/skills/brainstorm/SKILL.md` (raise token budgets 3×; reference `quality.tokenBudgets`)
- `src/core/hooks/pretooluse-guard.ts` (rewrite: use TaskGet-based state, remove filesystem-marker reads)
- `src/cli/commands/auto.ts` (add `--respect-native`, `--force-sw-auto` flags)
- `src/cli/dispatcher.ts` (parse `--effort` flag)
- Add `tool-use-rationale` blocks to 9 skills (US-010 AC-02)
- `plugins/specweave/.lint/skill-lint.ts` (new: enforce rationale presence)
- `.specweave/docs/internal/specs/effort-levels.md`, `skill-authoring-guide.md`, `auto-mode-decision-tree.md` (new docs)

**Migration strategy**: The state-marker removal is the highest-risk item. Sequence per OQ-1:
1. Rewrite `pretooluse-guard.ts` to use TaskGet, but keep reading filesystem markers as fallback (dual-read).
2. Remove STEP 0 from pm/architect SKILL.md — new invocations don't write markers but guard still tolerates absence.
3. After one release cycle, remove the filesystem fallback from the guard.

`--simple` removal: the `--simple-compat` alias prints deprecation warning via `process.stderr.write` and sets the flag internally; this gives users one minor release to migrate.

Code-reviewer collapse: keep 3 reviewer agents (security, logic, performance); replace haiku validator fan-out with inline self-critique (reviewer agent re-reads its own finding and validates before emitting). `--full-fanout` flag restores the 8+10 path.

**Rollback plan**: Each change is gated by a config knob (`quality.grillConfidenceThreshold`, `codeReview.skipValidation`, etc.) — setting to legacy values restores old behavior. `--simple-compat` alias preserves the `--simple` escape path.

**Sign-off gate**: (a) code-review agent-spawn benchmark shows ≥50% reduction vs baseline (AC-NFR-4.4); (b) PreToolUse guard test green with no filesystem markers present; (c) `sw:auto --simple-compat` emits warning + works; (d) skill-lint CI enforces tool-use-rationale on 9 target skills.

---

### Wave 4 — P3 Consolidation & UX

**Goal**: Merge multi-project skills, fold `sw:team-build` into `sw:team-lead --preset`, simplify `sw:close-all`, add `sw:plan --regenerate-plan`.

**User stories covered**: US-007 AC-02..06 (multi-project merge, team-build fold, plan simplification, close-all simplification).

**Files touched** (~10):
- **Merge**: `plugins/specweave/skills/github-multi-project/SKILL.md` + `ado-multi-project/SKILL.md` → new `multi-project/SKILL.md` with `--tool` flag
- **Fold**: `team-build` preset logic → `team-lead --preset <name>`; `team-build/SKILL.md` becomes thin alias
- **Simplify**: `plan/SKILL.md` → regenerate-only mode; `close-all/SKILL.md` reduced to ~40 lines (delegates to `sw:done`)
- **Shared module**: `src/core/validators/resource-base.ts` (new) consumed by github/jira/ado resource validators
- **Marketplace alias routing**: `plugins/specweave/marketplace.json` (add `sw:github-multi-project` → `sw:multi-project --tool github`, etc.)
- **Docs**: Update `.specweave/docs/internal/specs/config-reference.md` with new merged-skill names

**Migration strategy**: All merges preserve backward compat via marketplace alias routing — existing `/sw:github-multi-project` invocations still work via silent redirect to `/sw:multi-project --tool github`. Deprecation warnings at skill body top per Wave 2 pattern. `team-build` remains invokable for one minor release.

**Rollback plan**: Marketplace alias routing is the reversal path — setting `aliases: []` in marketplace.json restores separate-skill behavior. The new `multi-project` and `resource-base` modules can coexist with the old split for a release cycle.

**Sign-off gate**: (a) alias routing test (invoke deprecated skill names, verify correct behavior + warning); (b) `close-all` LOC check ≤60; (c) shared resource-validator module passes per-tool tests.

---

### Wave 5 — P4 Telemetry, Future, Non-Audited Sweep

**Goal**: Stand up telemetry to measure the wins and prepare for the deferred non-priority skill audit.

**User stories covered**: AC-US3-06 (cache telemetry via `sw:analytics --cache-stats`), AC-NFR-4.4 (agent-spawn benchmark), plus scaffolding for the follow-up increment audit.

**Files touched** (~6):
- `src/core/telemetry/cache-metrics.ts` (new)
- `plugins/specweave/skills/analytics/SKILL.md` (add `--cache-stats` section)
- `test/benchmarks/agent-spawn-count.bench.ts` (new — measures baseline vs post-0669)
- `test/fixtures/baseline-increment/` (canonical 5-task fixture for benchmarking)
- `.specweave/docs/internal/specs/follow-up-audits.md` (lists the 20 non-priority skills awaiting audit)
- `CHANGELOG.md`, `README.md` (final release-notes pass)

**Migration strategy**: Pure additive. No risk to existing workflows.

**Rollback plan**: Telemetry is off-by-default (`analytics.cacheMetrics.enabled: false`). Remove the module if needed.

**Sign-off gate**: (a) `sw:analytics --cache-stats` shows cache hit rate on canary; (b) agent-spawn benchmark shows ≥50% reduction; (c) skill-count CI reports ≤40 non-deprecated skills (AC-NFR-4.2).

---

## Architectural Decisions (ADRs)

Each ADR lives in `.specweave/docs/internal/architecture/adr/` as a separate file. Summary here; full ADR text in those files.

- **0249 — Single-agent planner as default in sw:increment**: 3-agent PM+Architect+Planner fan-out is gated behind `--parallel` flag or user-story count ≥ 10. Default single-agent path halves planning latency for small features. Reversible via `--parallel`.
- **0250 — Prompt caching strategy via config.staticContextFiles**: A declarative list in config drives `cache_control` breakpoint placement in the Anthropic SDK request. Up to 4 breakpoints per request (4.7 limit). Default list: `CLAUDE.md`, `config.json`, active `spec.md`, `rubric.md`.
- **0251 — Adaptive-thinking conventions**: Instead of fixed `thinking.budget_tokens`, skills use prompt hints ("think carefully and step-by-step — this problem is harder than it looks"). The `quality.thinkingBudget` knob is reserved for future Anthropic SDK support but currently only gates legacy-mode fallback.
- **0252 — Skill deprecation policy (2-version soft window)**: A skill marked `deprecated: true` in marketplace.json stays functional, hidden from `/sw:help` default listing, and emits a one-line console warning. Removal happens in the next minor release after the deprecation window closes (2 minor releases).
- **0253 — Skill consolidation via --flag mode in parent skill**: Instead of separate skills like `sw:tdd-red`, `sw:tdd-green`, `sw:tdd-refactor`, the canonical skill `sw:tdd-cycle` takes a `--phase red|green|refactor|all` flag. Marketplace alias routing preserves old invocations. Applies to TDD trio, multi-project skills, and `team-build` → `team-lead --preset`.
- **0254 — Shared agent protocol via `_protocol.md` include**: A single `plugins/specweave/skills/team-lead/agents/_protocol.md` file holds the messaging/TaskUpdate/shutdown-response boilerplate. `template-loader.ts` auto-prepends `_protocol.md` content when spawning an agent. Domain templates shrink ~30%.
- **0255 — Effort-level convention (default xhigh, opt-in max)**: Framework-wide default effort is `xhigh` per 4.7 recommendation. `max` requires explicit `--effort max` flag (which emits a warning about overthinking risk). `model: opus` declarations in SKILL.md frontmatter are supplemented by a "Model Configuration" section documenting the effort expectation.

---

## File-Level Change Map

A summary table. Wave assignment indicates earliest wave; some files may be touched again in a later wave for a smaller edit.

| File | Change Type | Wave | Notes |
|------|------------|------|-------|
| `plugins/specweave/skills/judge-llm/SKILL.md` | Edit | 1 | Remove "extended thinking", "ULTRATHINK BY DEFAULT"; add adaptive-thinking hint + effort section |
| `plugins/specweave/skills/grill/SKILL.md` | Edit | 1 | Add adaptive-thinking hint; lower threshold 70→50 (Wave 3) |
| `plugins/specweave/skills/team-lead/SKILL.md` | Edit | 1 | Remove "spawn anyway"; TASK_CAP 15→40; fan-out heuristic; remove active-phase forbidden-list (Wave 3); raise heartbeat thresholds (Wave 3) |
| `plugins/specweave/skills/increment/SKILL.md` | Edit | 2 | Single-agent default for Step 4; `--parallel` trigger for Step 4a |
| `plugins/specweave/skills/code-reviewer/SKILL.md` | Edit | 3 | Collapse 8 reviewers → 3; remove haiku validator fan-out; `--full-fanout` opt-in |
| `plugins/specweave/skills/auto/SKILL.md` | Edit | 3 | Remove `--simple` default; `--simple-compat` alias; Native Auto section |
| `plugins/specweave/skills/pm/SKILL.md` | Edit | 3 | Remove state-marker STEP 0; remove interview markers; raise token budgets |
| `plugins/specweave/skills/architect/SKILL.md` | Edit | 3 | Remove state-marker STEP 0 |
| `plugins/specweave/skills/done/SKILL.md` | Edit | 3 | Fix-loop cap 3→5; prompt-caching section |
| `plugins/specweave/skills/do/SKILL.md` | Edit | 3 | Remove per-task model hints |
| `plugins/specweave/skills/brainstorm/SKILL.md` | Edit | 3 | Raise token budgets; reference config |
| `plugins/specweave/skills/close-all/SKILL.md` | Simplify | 4 | ~200 lines → ~40; delegate to sw:done |
| `plugins/specweave/skills/plan/SKILL.md` | Simplify | 4 | Regenerate-only mode |
| `plugins/specweave/skills/tdd-red/SKILL.md` | Deprecate | 2 | `[DEPRECATED]` + migration note to `sw:tdd-cycle --phase red` |
| `plugins/specweave/skills/tdd-green/SKILL.md` | Deprecate | 2 | Same pattern |
| `plugins/specweave/skills/tdd-refactor/SKILL.md` | Deprecate | 2 | Same pattern |
| `plugins/specweave/skills/tdd-cycle/SKILL.md` | Edit | 2 | Add `--phase` flag support |
| `plugins/specweave/skills/github-sync/SKILL.md` | Deprecate | 2 | Redirect to `sw-github:sync-spec` |
| `plugins/specweave/skills/jira-sync/SKILL.md` | Deprecate | 2 | Redirect to `sw-jira:push/pull` |
| `plugins/specweave/skills/ado-sync/SKILL.md` | Deprecate | 2 | Redirect to `sw-ado:push/pull` |
| `plugins/specweave/skills/github-issue-standard/SKILL.md` | Deprecate + Move | 2 | Content → `docs/internal/specs/github-issue-standard.md`; SKILL.md becomes thin redirect |
| `plugins/specweave/skills/github-multi-project/SKILL.md` | Deprecate | 4 | Alias → `sw:multi-project --tool github` |
| `plugins/specweave/skills/ado-multi-project/SKILL.md` | Deprecate | 4 | Alias → `sw:multi-project --tool ado` |
| `plugins/specweave/skills/multi-project/SKILL.md` | New | 4 | Consolidated multi-project skill |
| `plugins/specweave/skills/team-build/SKILL.md` | Deprecate | 4 | Alias → `sw:team-lead --preset` |
| `plugins/specweave/skills/team-merge/SKILL.md` | Edit | 2 | Inline closure for ≤5 increments |
| `plugins/specweave/skills/help/SKILL.md` | Edit | 2 | Hide deprecated by default; `--deprecated` flag |
| `plugins/specweave/skills/analytics/SKILL.md` | Edit | 5 | Add `--cache-stats` section |
| `plugins/specweave/skills/team-lead/agents/_protocol.md` | New | 2 | Shared protocol extract |
| `plugins/specweave/skills/team-lead/agents/*.md` (existing) | Edit | 2 | Reference `_protocol.md`, remove duplicated content |
| `plugins/specweave/skills/team-lead/agents/reviewer-logic.md` | Delete-or-wire | 2 | Per US-008 AC-01 |
| `plugins/specweave/skills/team-lead/agents/reviewer-performance.md` | Delete-or-wire | 2 | Per US-008 AC-01 |
| `plugins/specweave/marketplace.json` | Edit | 2 | `deprecated: true` flags; alias routing entries |
| `src/core/cache/static-context-loader.ts` | New | 2 | Prompt-cache helper |
| `src/core/config/schema.ts` | Edit | 2 | Add `quality.thinkingBudget`, `cache.staticContextFiles`, `quality.grillConfidenceThreshold`, `quality.tokenBudgets` |
| `src/core/skills/skill-judge.ts` | Edit | 1+2 | Wave 1: guard `thinking` param; Wave 2: integrate static-context-loader |
| `src/core/hooks/pretooluse-guard.ts` | Rewrite | 3 | TaskGet-based state; dual-read during transition |
| `src/core/team-lead/template-loader.ts` | Edit | 2 | Auto-prepend `_protocol.md` |
| `src/core/validators/resource-base.ts` | New | 4 | Shared base for github/jira/ado resource validators |
| `src/core/telemetry/cache-metrics.ts` | New | 5 | Cache hit rate tracking |
| `src/cli/commands/increment.ts` | Edit | 2 | Parse `--parallel` flag |
| `src/cli/commands/auto.ts` | Edit | 3 | Parse `--respect-native`, `--force-sw-auto`; keep `--simple-compat` |
| `src/cli/commands/doctor.ts` | Edit | 2 | Report missing `quality.*`, `cache.*` keys |
| `src/cli/dispatcher.ts` | Edit | 3 | Parse `--effort` flag, propagate |
| `scripts/migrate-config-0669.ts` | New | 2 | Idempotent config upgrade |
| `plugins/specweave/.lint/skill-lint.ts` | New | 3 | Lint retired phrases + tool-use-rationale |
| `.github/workflows/skill-lint.yml` | New | 1 | CI enforcement |
| `.specweave/docs/internal/specs/opus-47-migration.md` | New | 1 | Canonical migration doc, grows per wave |
| `.specweave/docs/internal/specs/planning-modes.md` | New | 2 | Single-agent vs parallel matrix |
| `.specweave/docs/internal/specs/config-reference.md` | New | 2 | All new config knobs |
| `.specweave/docs/internal/specs/skill-deprecation-policy.md` | New | 2 | Lifecycle and current batch |
| `.specweave/docs/internal/specs/effort-levels.md` | New | 3 | Default xhigh, max opt-in |
| `.specweave/docs/internal/specs/skill-authoring-guide.md` | Edit | 3 | Tool-use rationale section |
| `.specweave/docs/internal/specs/auto-mode-decision-tree.md` | New | 3 | Native vs sw:auto |
| `.specweave/docs/internal/specs/follow-up-audits.md` | New | 5 | 20 non-priority skills awaiting audit |
| `.specweave/docs/internal/specs/github-issue-standard.md` | New | 2 | Content moved from deprecated skill |
| `test/integration/prompt-caching.test.ts` | New | 2 | Verifies `cache_read_input_tokens > 0` |
| `test/integration/increment-single-agent-parity.test.ts` | New | 2 | Snapshot parity |
| `test/integration/backwards-compat-0669.test.ts` | New | 1 | Regression on 5 archived increments |
| `test/benchmarks/agent-spawn-count.bench.ts` | New | 5 | Baseline vs post-0669 |
| `test/fixtures/baseline-increment/` | New | 5 | Canonical fixture |
| `CHANGELOG.md` | Edit | 5 | 0669 release entry |
| `README.md` | Edit | 5 | "Upgrading" section |

**Total**: ~52 files touched across 5 waves. New files: 17. Edited files: 31. Deleted files: 0–2 (US-008 AC-01 decision).

---

## Technical Risks & Mitigations

Pulled from research-findings.md §5 and expanded with detection + rollback per risk.

- **R-1 (High): Collapsing 3-agent planning may surprise tmux-watchers.**
  - Detection: Users who rely on visible parallel agent panes will notice the single-agent path.
  - Mitigation: Preserve `--parallel` flag as explicit opt-in (AC-US4-02); document in planning-modes.md; keep parallel path fully functional (not removed, just not default).
  - Rollback: Flip default by editing one line in increment/SKILL.md.

- **R-2 (High): Raising TASK_CAP 15→40 could hide genuinely hung agents.**
  - Detection: Heartbeat stuck detection (existing feature) surfaces no-progress agents.
  - Mitigation: Keep stuck detection (AC-US5-06 retains it), raise thresholds conservatively (2min→5min no-progress, 10min→20min total) — not proportional to task cap increase. Measure on canary.
  - Rollback: TASK_CAP is a single constant; revert in one commit.

- **R-3 (Medium): Retiring `--simple` may slow auto-mode on very large specs (>50K tokens).**
  - Detection: Monitor auto-mode session length on canary increments >30 tasks.
  - Mitigation: Auto-fall-back heuristic in `sw:auto`: if spec.md size > 40KB, internally enable simple-compat behavior (skip spec re-reads) without user intervention.
  - Rollback: `--simple-compat` alias stays functional for one minor release.

- **R-4 (High): Collapsing code-reviewer agents could miss security edge cases.**
  - Detection: Judge-LLM reports on the 0669 increment itself will catch regressions (NFR-5.2).
  - Mitigation: Keep a dedicated **Opus-tier** security reviewer; only collapse sonnet-tier specialists. Haiku validator fan-out replaced with inline self-critique (reviewer re-reads its own output before emitting). `--full-fanout` flag restores the 8+10 path.
  - Rollback: The three-reviewer configuration is data-driven in code-reviewer/SKILL.md; revert by reverting one file.

- **R-5 (High): Dropping state-marker files requires guard rewrite; risk of write-blocking window.**
  - Detection: Integration test that simulates mid-upgrade state (guard expects files that are no longer written).
  - Mitigation: Per OQ-1 sequence: rewrite guard to **dual-read** (TaskGet first, fallback to filesystem) in Wave 3; remove filesystem fallback only after one release cycle. Old marker files present at upgrade time are tolerated (NFR-1.2).
  - Rollback: Filesystem fallback reactivation is one flag in the guard.

- **R-6 (Medium): Prompt caching may produce unexpected results if static files change mid-session.**
  - Detection: Integration test (AC-US3-05) verifies second-call cache hit.
  - Mitigation: Use Anthropic SDK `ephemeral` cache type (5-min TTL) — auto-invalidates. `static-context-loader` checks file mtime before caching; stale files bust cache.
  - Rollback: `cache.staticContextFiles: []` disables caching entirely.

- **R-7 (Medium): Marketplace alias routing may conflict with external tooling (vskill).**
  - Detection: Run vskill install smoke test on deprecated skill IDs.
  - Mitigation: NFR-1.4 — retain marketplace.json entries for deprecated skills (with `deprecated: true` flag) for two minor releases. Alias routing is a new field, additive.
  - Rollback: Remove alias entries; deprecated skills still work directly.

- **R-8 (Low): Config schema additions could fail on existing `.specweave/config.json` files lacking new keys.**
  - Detection: Config-load integration test.
  - Mitigation: Schema defaults + `scripts/migrate-config-0669.ts` run on first CLI invocation post-upgrade. Backup written to `.specweave/config.json.bak-0669`.
  - Rollback: Restore from backup file.

---

## Integration Points

- **NPM package versioning**: This increment ships as `specweave@1.1.0` (minor bump). The skill surface area changes are documented as deprecations, not breaking changes, so semver minor is correct. No dependents break: existing `/sw:tdd-red` invocations continue to work via alias routing.
- **Plugin cache invalidation**: After publish, users run `specweave refresh-plugins` to pick up SKILL.md changes. Existing CLAUDE.md instructions handle this.
- **Hook registration in settings.json**: No new hooks; rewritten PreToolUse guard remains at the same registration point.
- **CLAUDE.md propagation**: Existing projects consume `specweave` via npm; the SKILL.md bundle updates propagate via `specweave refresh-plugins`. No change to per-project `CLAUDE.md` is required.
- **Telemetry**: Wave 5 introduces opt-in `analytics.cacheMetrics.enabled` (default false). No privacy implications; metrics are local-only unless user runs `sw:analytics --export`.
- **External sync (GitHub/Jira/ADO)**: Deprecating `sw:github-sync`, `sw:jira-sync`, `sw:ado-sync` does **not** affect the `sw-{tool}:sync` command families (those live in separate plugins). The deprecated skills are guidance stubs, not sync executors.

---

## Component Boundaries

- `plugins/specweave/skills/<name>/SKILL.md` — per-skill markdown contract. Owns user-facing behavior and model instructions.
- `plugins/specweave/skills/team-lead/agents/*.md` — agent prompt templates. Owned by team-lead; NEW: `_protocol.md` extracted.
- `plugins/specweave/marketplace.json` — discoverability + alias routing. NEW fields: `deprecated: bool`, `alias: { from: "/sw:x", to: "/sw:y --flag" }`.
- `src/core/config/schema.ts` — config schema. Owns defaults and validation.
- `src/core/cache/static-context-loader.ts` (NEW) — prompt-cache helper, consumed by skill implementations.
- `src/core/hooks/pretooluse-guard.ts` — enforces skill-chain preconditions. Owned by hook layer; migrating off filesystem state.
- `src/core/team-lead/template-loader.ts` — resolves agent templates; NEW responsibility: prepend `_protocol.md`.
- `src/core/validators/resource-base.ts` (NEW) — shared base class for github/jira/ado resource validators.
- `bin/specweave` (CLI entry) — unchanged; dispatcher parses new flags.
- `src/cli/dispatcher.ts` — parses `--effort`, `--parallel`, `--simple-compat`, `--respect-native`, `--force-sw-auto`.
- `.specweave/config.json` — project-level config. NEW keys additive.
- `.specweave/state/*` — per-session state. Interview markers removed in Wave 3; skill-chain markers removed in Wave 3.
- `.specweave/docs/internal/specs/` — canonical docs. Several new files in Waves 1–5.
- `scripts/migrate-config-0669.ts` (NEW) — one-shot config upgrade, idempotent.
- `.github/workflows/skill-lint.yml` (NEW) — CI enforcement of skill-authoring conventions.

---

## Testing Strategy

**Unit tests** (target 95% coverage on new code):
- `src/core/cache/static-context-loader.test.ts` — breakpoint placement, cache-key stability, mtime invalidation.
- `src/core/config/schema.test.ts` — new keys parse, defaults apply, unknown keys rejected (or warned per doctor policy).
- `scripts/migrate-config-0669.test.ts` — idempotent application, backup created, no-op on already-migrated config.
- `src/core/hooks/pretooluse-guard.test.ts` — dual-read during transition, TaskGet-only path post-transition.
- `src/core/validators/resource-base.test.ts` — per-tool implementations share behavior.

**Integration tests** (90% coverage on changed code paths):
- `test/integration/prompt-caching.test.ts` — AC-US3-05: two consecutive invocations show `cache_read_input_tokens > 0` on the second.
- `test/integration/increment-single-agent-parity.test.ts` — AC-US4-04: single-agent vs 3-agent outputs are structurally identical.
- `test/integration/tdd-alias-routing.test.ts` — invoking `/sw:tdd-red` routes to `/sw:tdd-cycle --phase red` with deprecation warning.
- `test/integration/auto-simple-compat.test.ts` — `--simple-compat` emits warning + preserves behavior.
- `test/integration/multi-project-alias.test.ts` — deprecated multi-project skills route to consolidated `sw:multi-project`.

**Regression tests**:
- `test/integration/backwards-compat-0669.test.ts` — NFR-1.1: open, resume, close 5 archived increments end-to-end.
- Full existing integration test suite must remain green.

**E2E tests** (happy-path increment lifecycle on a sandbox repo):
- Create increment → plan (single-agent) → execute → close on a throwaway repo; verify no breakage.
- Create increment with `--parallel` → plan (3-agent) → execute → close; verify parity.

**Telemetry validation** (Wave 5):
- `test/benchmarks/agent-spawn-count.bench.ts` — AC-NFR-4.4: ≥50% reduction vs baseline on a 5-task fixture.
- `sw:analytics --cache-stats` on canary shows cache hit rate ≥40% (AC-NFR-4.3).

**CI pipelines**:
- `skill-lint` — enforces no retired phrases and tool-use-rationale presence.
- `skill-count` — fails if non-deprecated skill count > 40.
- `backwards-compat` — runs the 5-increment regression suite.

---

## Open Questions for Implementation

These build on spec.md's OQ-1..OQ-4 and add implementation-level questions the plan cannot resolve without user input:

- **OQ-5 (from OQ-1)**: Transition period length for the PreToolUse guard dual-read — one minor release or two? Longer window = safer for users on mixed versions, shorter = less dead code. Recommendation: **one minor release** given the 2-version deprecation window policy (ADR-0252).
- **OQ-6 (from OQ-2)**: Alias routing mechanism — marketplace.json field + runtime translator in CLI dispatcher? Recommendation: **both** — marketplace.json declares the mapping (discoverability); dispatcher enforces it (runtime). Single source of truth = marketplace.json.
- **OQ-7 (from OQ-3)**: Prompt-cache breakpoints — per-file or aggregated? Recommendation: **aggregated** single breakpoint for all static context (CLAUDE.md + config.json + spec.md + rubric.md concatenated), saving breakpoint budget for dynamic content (conversation history, etc.).
- **OQ-8 (from OQ-4)**: Model-version detection — string match or SDK helper? Recommendation: **SDK helper** (e.g., `isOpus47Family(modelId)`) to future-proof; fall back to string match if SDK doesn't expose one.
- **OQ-9**: Should `sw:judge-llm` retain the `--quick` flag from its current SKILL.md when `--effort max` is introduced? Recommendation: **retire `--quick`** in favor of `--effort low` — one effort taxonomy, no parallel vocabulary.
- **OQ-10**: Should the 2 orphan agent templates (`reviewer-logic.md`, `reviewer-performance.md`) be wired into REVIEW mode or deleted? Recommendation: **delete** — `sw:code-reviewer` already handles the equivalent, and Wave 3 collapses code-reviewer specialists anyway. Wiring them in would re-introduce the fan-out we're eliminating.
- **OQ-11**: Should the `--simple` → `--simple-compat` alias print the warning on **every** invocation or just the first per session? Recommendation: **first-per-session** (track in `.specweave/state/deprecation-warnings-shown.json`) to avoid noise.

---

## Summary for Implementer

Start with Wave 1 (correctness fixes, ~6 files) — this unblocks Opus 4.7 default-on safely. Wave 2 (prompt caching + deprecations) is the highest-value wave and should follow immediately. Wave 3 (behavioral changes + state-marker removal) requires the most care — rewrite the PreToolUse guard with dual-read, and keep `--simple-compat` working. Wave 4 consolidates the surface area; Wave 5 stands up telemetry and preps the follow-up audit.

Every wave has an explicit opt-out path and a reversible rollback; the 5-wave structure was chosen specifically to let any wave bail without regressing earlier waves. Ship each wave as a dev build first, run the backwards-compat suite, canary on the umbrella repo, then promote. Final release is `specweave@1.1.0`.
