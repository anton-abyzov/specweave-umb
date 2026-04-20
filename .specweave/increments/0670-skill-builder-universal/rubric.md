---
increment: 0670-skill-builder-universal
title: "skill-builder: Distributable Universal Skill Authoring Package"
generated: "2026-04-19"
source: hand-authored-post-grill
version: "1.0"
status: active
---

# Quality Contract: 0670-skill-builder-universal

> Hand-authored from the 42+ ACs in spec.md after the three-agent deep-verification pass.
> Blocking criteria must pass before `/sw:done` can close this increment.
> Tier thresholds (MVP / standard / strict) let us ship partial value if Day 5 slips.

---

## Tier Thresholds

- **MVP** (ship-blocker minimum): R-001..R-009 blocking pass. Enough to ship `vskill skill new` CLI + `skill-builder` SKILL.md to npm with path A working. Registry + cross-tool E2E can land in a `+0.0.1`.
- **Standard** (default closure target): MVP + R-010..R-016 blocking pass. All ACs met including path-B regression, divergence report, schema versioning, registry submit, sandbox smoke.
- **Strict** (release-candidate): Standard + R-017..R-020 blocking pass. Includes manual verification signoff, follow-up increment stub, umbrella sync commit, and zero eval-ui regressions across three runs.

**`/sw:done` target for this increment: Standard.** Escalate to Strict only if reviewers flag risk.

---

## R-001: Generator extracted as pure module [blocking]
- **Source**: AC-US4-01, AC-US4-04
- **Evaluator**: sw:grill + Vitest
- **Verify**: `src/core/skill-generator.ts` exists; `grep -n "req\|res\|SSE" src/core/skill-generator.ts` returns zero; grep shows only imports from `src/core/`, `src/utils/`, `src/agents/`, `src/installer/`, or node_modules
- **Threshold**: File exists, zero HTTP-layer references, imports clean
- **Result**: [ ] PENDING

## R-002: HTTP handler reduced to ≤40 lines [blocking]
- **Source**: AC-US4-03
- **Evaluator**: sw:grill
- **Verify**: `router.post("/api/skills/generate", …)` handler body ≤40 lines in `src/eval-server/skill-create-routes.ts`
- **Threshold**: Handler body line count ≤40
- **Result**: [ ] PENDING

## R-003: Pre-extraction snapshot parity [blocking]
- **Source**: AC-US4-02
- **Evaluator**: Vitest
- **Verify**: `npx vitest run src/core/__tests__/skill-generator.test.ts` passes; all 3 target combinations × targets match T-000 fixtures byte-for-byte
- **Threshold**: Zero diffs across all combo×target combinations
- **Result**: [ ] PENDING

## R-004: vskill skill CLI subcommand wired and exposes 5 subcommands [blocking]
- **Source**: AC-US3-01, AC-US3-09, AC-US3-10
- **Evaluator**: sw:grill + Vitest
- **Verify**: `src/commands/skill.ts` exists; `registerSkillCommand(program)` invoked in `src/cli/index.ts`; `node dist/index.js skill --help` output contains exactly `new`, `import`, `list`, `info`, `publish` with descriptions
- **Threshold**: All 5 subcommands in help output
- **Result**: [ ] PENDING

## R-005: Default target set emits to 8 universal agents [blocking]
- **Source**: AC-US3-04
- **Evaluator**: Vitest integration
- **Verify**: `vskill skill new --prompt "X"` (no `--targets` flag) writes SKILL.md to the 8 directories sourced from `AGENTS_REGISTRY.filter(a => a.isUniversal).map(a => a.localSkillsDir)` — currently `.amp/skills/X/`, `.cline/skills/X/`, `.codex/skills/X/`, `.cursor/skills/X/`, `.gemini/skills/X/`, `.github/copilot/skills/X/`, `.kimi/skills/X/`, `.opencode/skills/X/`. Directory list is resolved at test time from the registry to stay in sync.
- **Threshold**: All 8 directories contain valid SKILL.md
- **Result**: [ ] PENDING

## R-006: Target resolution — unknown ID errors, all resolves to 49 [blocking]
- **Source**: AC-US3-03, AC-US3-11, AC-US7-08
- **Evaluator**: Vitest integration
- **Verify**: `--targets=unknown-id` exits non-zero with `Unknown agent id: unknown-id`; `--targets=all` emits to all 49 registered agents (count matches `agents-registry.ts`)
- **Threshold**: Unknown-id error + 49 directories created
- **Result**: [ ] PENDING

## R-007: Missing/empty prompt errors cleanly [blocking]
- **Source**: AC-US3-12
- **Evaluator**: Vitest integration
- **Verify**: `vskill skill new` without `--prompt` exits non-zero with usage hint; `--prompt ""` exits non-zero with the same error
- **Threshold**: Both cases exit non-zero with helpful message
- **Result**: [ ] PENDING

## R-008: skill-builder SKILL.md exists, <500 lines, correct frontmatter [blocking]
- **Source**: AC-US1-01, AC-US1-02
- **Evaluator**: sw:grill + frontmatter-parser test
- **Verify**: `plugins/skills/skills/skill-builder/SKILL.md` exists; `wc -l` < 500; frontmatter has `name: skill-builder`, `description` containing all 7 trigger phrases from AC-US1-02, `tags: [skill-authoring, meta, universal]`, `metadata.version: 0.1.0`
- **Threshold**: File exists, <500 lines, all frontmatter fields present
- **Result**: [ ] PENDING

## R-009: Fallback chain detection script tested for all 4 branches [blocking]
- **Source**: AC-US2-01..07
- **Evaluator**: Vitest
- **Verify**: Detection-logic test covers (a) CLI present → path A, (b) CLI absent + package resolvable → path B, (c) both absent + skill-creator installed + host=Claude Code → path C + warning, (d) all absent → non-zero exit with remediation; path C requires `~/.claude/skills/skill-creator/` detection via `isSkillCreatorInstalled()`
- **Threshold**: All 4 branches tested with assertion on selected path AND stderr content
- **Result**: [ ] PENDING

---

## R-010: Divergence report generated with security-critical enforcement [blocking]
- **Source**: AC-US5-01..05, FR-004
- **Evaluator**: Vitest
- **Verify**: Positive case — source with `allowed-tools: [Bash]` emitting to OpenCode produces divergence entry `allowed-tools → permission: { bash: ask }`; Negative case — stubbed generator that omits the entry FAILS the test; Edge case — all-universal-targets produces single line `No divergences — all targets universal`
- **Threshold**: All 3 cases pass (positive, negative=failure-catching, edge)
- **Result**: [ ] PENDING

## R-011: x-sw-schema-version tag on every non-fallback emission [blocking]
- **Source**: AC-US6-01..04
- **Evaluator**: Vitest
- **Verify**: Unit test parses frontmatter YAML across 8 universal-target emissions and asserts `x-sw-schema-version: 1`; re-emission preserves the field; `--engine=anthropic-skill-creator` output does NOT contain the field
- **Threshold**: Tag present on all non-fallback emissions, absent on fallback
- **Result**: [ ] PENDING

## R-012: vskill skill import re-emits with divergence [blocking]
- **Source**: AC-US3-06
- **Evaluator**: Vitest integration
- **Verify**: Given a fixture SKILL.md, `vskill skill import <path> --targets=claude-code,codex` produces two target outputs + divergence report; fixture frontmatter fields are preserved where compatible or translated where not
- **Threshold**: Two target outputs + divergence present
- **Result**: [ ] PENDING

## R-013: vskill skill info + list + publish aliases function [blocking]
- **Source**: AC-US3-07, AC-US3-08
- **Evaluator**: Vitest integration
- **Verify**: `vskill skill list` output == `vskill list` output; `vskill skill info skill-builder` prints frontmatter + divergence content; `vskill skill publish X` invokes `submit X` logic (spy assertion)
- **Threshold**: All three aliases match expected behavior
- **Result**: [ ] PENDING

## R-014: CLI install via vskill install lands skill in correct dirs [blocking]
- **Source**: AC-US1-05, AC-US1-06, AC-US7-02
- **Evaluator**: Vitest integration
- **Verify**: Sandbox `vskill install anton-abyzov/vskill/plugins/skills/skills/skill-builder` lands SKILL.md in `.claude/skills/skill-builder/` AND `.agents/skills/skill-builder/`
- **Threshold**: Both directories contain SKILL.md
- **Result**: [ ] PENDING

## R-015: Skill Studio browser regression (path B) stays green [blocking]
- **Source**: AC-US7-07, AC-US4-05
- **Evaluator**: Playwright
- **Verify**: `npx playwright test tests/e2e/skill-studio-regression.spec.ts` passes post-T-002 rewire; full flow (prompt → generate → preview → save) works
- **Threshold**: Test passes; no console errors beyond those pre-existing
- **Result**: [ ] PENDING

## R-016: Registry publication succeeds + old-version sandbox install works [blocking]
- **Source**: AC-US8-01, AC-US8-02
- **Evaluator**: Manual + log inspection
- **Verify**: T-013b `vskill submit` returns registry URL (captured in `reports/t013b-submit.log`); T-013c sandbox with pinned `vskill@0.5.80` `vskill install skill-builder` succeeds
- **Threshold**: Registry URL returned AND pinned-old-version install works
- **Result**: [ ] PENDING

---

## R-017: Manual verification signed off [blocking for strict]
- **Source**: AC-US2-02 (path B manual), AC-US1-07 (Codex re-verification)
- **Evaluator**: Human tester
- **Verify**: `reports/manual-verification.md` exists with `[x]` signoff on (a) path B flow, (b) sentinel file written, (c) emitted SKILL.md valid, (d) optional Codex re-verification
- **Threshold**: All 4 items checked with date + initials
- **Result**: [ ] PENDING

## R-018: Coverage ≥90% on new modules [blocking]
- **Source**: plan.md Testing Strategy
- **Evaluator**: Vitest coverage report
- **Verify**: `npx vitest run --coverage` shows ≥90% line coverage on `src/core/skill-generator.ts` and `src/commands/skill.ts`
- **Threshold**: Coverage ≥90% on both files
- **Result**: [ ] PENDING

## R-019: No regressions — existing eval-ui + skill-create-routes + installer tests green [blocking]
- **Source**: AC-US4-05, FR-005
- **Evaluator**: Vitest
- **Verify**: `npx vitest run src/eval-ui/ src/eval-server/ src/installer/` passes with zero failures across three consecutive runs
- **Threshold**: Zero failures × 3 runs
- **Result**: [ ] PENDING

## R-020: Release + umbrella sync + follow-up stub landed [blocking for strict]
- **Source**: AC-US9-01..04
- **Evaluator**: Git log + filesystem check
- **Verify**: npm package version bumped and published; GitHub Release created; umbrella commit `sync umbrella after vskill v0.5.X release` on main; `.specweave/increments/<next-id>-skill-gen-vskill-integration/` stub exists with metadata.json status `planned`
- **Threshold**: All four artifacts confirmed
- **Result**: [ ] PENDING

---

## Scope Guardrails (anti-creep)

These are NOT in the rubric — if they appear in closure evidence, flag as out-of-scope:
- Any SpecWeave source modification (AD-006, FR-001)
- `sw:skill-gen → vskill skill new` rewire (follow-up increment)
- Skill Studio UI redesign (0465 workspace stays as-is)
- `scout` cross-link (moved to post-close checklist)
- New agent registrations (49-agent catalog is sufficient)
- Interactive-mode CLI (flag-driven only)
- Additional subcommands beyond the 5 named

## Scoring Rubric for Closure Decision

| Outcome | Criteria |
|---|---|
| PASS (Standard tier) | R-001..R-016 all `[x]` + R-019 passes |
| PASS (Strict tier) | All of Standard + R-017, R-018, R-020 all `[x]` |
| FAIL | Any blocking item `[ ]` at Standard tier |
| DEFERRED | R-016 or R-020 fails at T-013b/c/d — increment stays open until retry succeeds, but R-001..R-015 can be declared "code-complete" with a note |

Closure decision is recorded in `reports/closure-decision.md` with the rubric state captured as evidence.
