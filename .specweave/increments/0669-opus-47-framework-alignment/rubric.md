# Rubric: Opus 4.7 Framework Alignment

**Increment**: 0669-opus-47-framework-alignment
**Generated**: 2026-04-16
**Total criteria**: 45 (30 functional + 15 infrastructure/NFR)

---

## Functional Correctness — US-001: Adaptive Thinking

### R-001: judge-llm SKILL.md drops "extended thinking" and "ULTRATHINK BY DEFAULT" [blocking]
- **Source**: AC-US1-01, AC-US1-02
- **Evaluator**: sw:grill
- **Verify**: `grep -c "extended thinking\|ULTRATHINK BY DEFAULT" plugins/specweave/skills/judge-llm/SKILL.md` returns 0; an adaptive-thinking prompt-hint block is present
- **Threshold**: Zero matches for retired phrases
- **Result**: [ ] PENDING

### R-002: grill SKILL.md has adaptive-thinking prompt hint in review procedure [blocking]
- **Source**: AC-US1-03
- **Evaluator**: sw:grill
- **Verify**: `grep -c "think carefully" plugins/specweave/skills/grill/SKILL.md` returns ≥ 1 within the review procedure section
- **Threshold**: At least 1 match
- **Result**: [ ] PENDING

### R-003: No SKILL.md contains retired thinking parameter strings [blocking]
- **Source**: AC-US1-04
- **Evaluator**: sw:grill
- **Verify**: `grep -r "thinking.budget_tokens\|budget_tokens:\|\"thinking\": {" plugins/specweave/skills/**/SKILL.md` returns zero matches outside code comments
- **Threshold**: Zero matches
- **Result**: [ ] PENDING

### R-004: skill-judge.ts guards `thinking` parameter behind model-version check [blocking]
- **Source**: AC-US1-05
- **Evaluator**: sw:grill
- **Verify**: Unit tests in `src/core/skills/skill-judge.test.ts` pass; `isOpus47Family` helper exists; `thinking` param absent for 4.7-family models
- **Threshold**: All unit tests green
- **Result**: [ ] PENDING

### R-005: opus-47-migration.md exists with before/after examples [standard]
- **Source**: AC-US1-06
- **Evaluator**: sw:grill
- **Verify**: File exists at `.specweave/docs/internal/specs/opus-47-migration.md`; contains at least 3 before/after pairs; covers adaptive thinking pattern
- **Threshold**: File present with ≥ 3 before/after examples
- **Result**: [ ] PENDING

---

## Functional Correctness — US-002: Subagent Spawning

### R-006: team-lead SKILL.md removes "spawn agents anyway" and adds fan-out heuristic [blocking]
- **Source**: AC-US2-01, AC-US2-02
- **Evaluator**: sw:grill
- **Verify**: `grep -c "spawn agents anyway" team-lead/SKILL.md` returns 0; quantitative fan-out threshold (domains ≥ 3 OR tasks ≥ 15 OR --parallel) is documented
- **Threshold**: Zero matches for banned phrase; heuristic present
- **Result**: [ ] PENDING

### R-007: code-reviewer SKILL.md collapses to ≤3 reviewers; haiku fan-out removed [blocking]
- **Source**: AC-US2-03, AC-US2-04
- **Evaluator**: sw:grill
- **Verify**: `grep -c "independent-finding-validator" code-reviewer/SKILL.md` returns 0; 3 named reviewers (security, logic, performance) present; `--full-fanout` flag documented
- **Threshold**: Zero haiku-validator references; 3 reviewers documented
- **Result**: [ ] PENDING

### R-008: increment SKILL.md defaults to single-agent planner [blocking]
- **Source**: AC-US2-05
- **Evaluator**: sw:grill
- **Verify**: Step 4 runs single-agent by default; Step 4a fan-out gated behind `--parallel` / ≥10 stories
- **Threshold**: Default path is single-agent; fan-out is gated
- **Result**: [ ] PENDING

### R-009: team-merge SKILL.md runs closure inline for ≤5 increments [standard]
- **Source**: AC-US2-06
- **Evaluator**: sw:grill
- **Verify**: Inline-closure condition (≤5 increments) is documented; subagent path only for larger merges
- **Threshold**: Inline-closure condition present
- **Result**: [ ] PENDING

### R-010: do SKILL.md removes per-task model hints; uses single xhigh effort tier [blocking]
- **Source**: AC-US2-07
- **Evaluator**: sw:grill
- **Verify**: `grep -c "haiku\|sonnet.*per.task" do/SKILL.md` returns 0; `grep -c "xhigh" do/SKILL.md` returns ≥ 1
- **Threshold**: Zero per-task model hints; xhigh referenced
- **Result**: [ ] PENDING

---

## Functional Correctness — US-003: Prompt Caching

### R-011: static-context-loader.ts exists and returns cache_control blocks [blocking]
- **Source**: AC-US3-01
- **Evaluator**: sw:grill
- **Verify**: File at `src/core/cache/static-context-loader.ts`; unit tests pass; returned objects contain `cache_control: { type: "ephemeral" }`
- **Threshold**: File present; all unit tests green
- **Result**: [ ] PENDING

### R-012: sw:judge-llm uses static-context-loader in API request [blocking]
- **Source**: AC-US3-03
- **Evaluator**: sw:grill
- **Verify**: `skill-judge.ts` calls `loadStaticContext`; constructed request has cache breakpoint before dynamic content
- **Threshold**: Cache breakpoint in request; existing tests green
- **Result**: [ ] PENDING

### R-013: grill, code-reviewer, done SKILL.md have "Prompt Caching" sections [standard]
- **Source**: AC-US3-04
- **Evaluator**: sw:grill
- **Verify**: `grep -c "Prompt Caching"` on each of the 3 files returns ≥ 1
- **Threshold**: Section present in all 3 files
- **Result**: [ ] PENDING

### R-014: Prompt-caching integration test shows cache_read_input_tokens > 0 on second call [blocking]
- **Source**: AC-US3-05
- **Evaluator**: sw:grill
- **Verify**: `test/integration/prompt-caching.test.ts` passes; second invocation `cache_read_input_tokens` > 0
- **Threshold**: Integration test green
- **Result**: [ ] PENDING

### R-015: Cache telemetry records hit rate; sw:analytics --cache-stats available [standard]
- **Source**: AC-US3-06
- **Evaluator**: sw:grill
- **Verify**: `src/core/telemetry/cache-metrics.ts` exists; analytics SKILL.md has `--cache-stats` section
- **Threshold**: Both artifacts present
- **Result**: [ ] PENDING

---

## Functional Correctness — US-004: Single-Agent Planning

### R-016: increment SKILL.md fan-out triggers documented (--parallel, ≥10 stories, keywords) [blocking]
- **Source**: AC-US4-01, AC-US4-02
- **Evaluator**: sw:grill
- **Verify**: All 3 trigger conditions present in Step 4a; absent any trigger, single-agent default is explicit
- **Threshold**: All 3 triggers documented; single-agent default explicit
- **Result**: [ ] PENDING

### R-017: increment.ts parses --parallel flag and flows into skill invocation [blocking]
- **Source**: AC-US4-03
- **Evaluator**: sw:grill
- **Verify**: Unit tests in `src/cli/commands/increment.test.ts` pass for `--parallel` flag parsing
- **Threshold**: All unit tests green
- **Result**: [ ] PENDING

### R-018: Single-agent planning parity test is green [blocking]
- **Source**: AC-US4-04
- **Evaluator**: sw:grill
- **Verify**: `test/integration/increment-single-agent-parity.test.ts` passes; output structure matches 3-agent path
- **Threshold**: Integration test green
- **Result**: [ ] PENDING

### R-019: planning-modes.md created with decision matrix [standard]
- **Source**: AC-US4-05
- **Evaluator**: sw:grill
- **Verify**: File exists at `.specweave/docs/internal/specs/planning-modes.md`; decision matrix present; `--parallel` documented
- **Threshold**: File present with matrix
- **Result**: [ ] PENDING

---

## Functional Correctness — US-005: Legacy Workaround Removal

### R-020: team-lead TASK_CAP raised to 40 with 4.7 rationale [blocking]
- **Source**: AC-US5-01
- **Evaluator**: sw:grill
- **Verify**: `grep -c "TASK_CAP.*40\|40.*task" team-lead/SKILL.md` returns ≥ 1; no reference to cap of 15
- **Threshold**: Cap updated to 40; 4.7 rationale present
- **Result**: [ ] PENDING

### R-021: auto SKILL.md removes --simple default; --simple-compat alias present [blocking]
- **Source**: AC-US5-02
- **Evaluator**: sw:grill
- **Verify**: `grep -c "simple-compat" auto/SKILL.md` ≥ 1; `--simple` no longer a default path
- **Threshold**: --simple-compat present; --simple removed from defaults
- **Result**: [ ] PENDING

### R-022: pm and architect SKILL.md remove state-marker STEP 0; interview markers removed [blocking]
- **Source**: AC-US5-03, AC-US5-05
- **Evaluator**: sw:grill
- **Verify**: `grep -c "skill-chain.*json\|interview.*json\|STEP 0" pm/SKILL.md architect/SKILL.md` returns 0
- **Threshold**: Zero matches
- **Result**: [ ] PENDING

### R-023: pretooluse-guard.ts rewritten to TaskGet-based state with filesystem fallback [blocking]
- **Source**: AC-US5-03
- **Evaluator**: sw:grill
- **Verify**: `src/core/hooks/pretooluse-guard.test.ts` passes including no-marker test case
- **Threshold**: All guard tests green including no-filesystem-marker case
- **Result**: [ ] PENDING

### R-024: grill default confidence threshold lowered to 50; references config [standard]
- **Source**: AC-US5-04
- **Evaluator**: sw:grill
- **Verify**: `grep -c "70.*threshold" grill/SKILL.md` returns 0; threshold 50 and `grillConfidenceThreshold` referenced
- **Threshold**: Old value gone; new value and config knob present
- **Result**: [ ] PENDING

### R-025: done SKILL.md fix-loop cap raised from 3 to 5 [standard]
- **Source**: AC-US5-07
- **Evaluator**: sw:grill
- **Verify**: `grep -c "cap.*3\|3.*iteration" done/SKILL.md` returns 0; cap of 5 present
- **Threshold**: Old cap gone; new cap present
- **Result**: [ ] PENDING

### R-026: pm and brainstorm SKILL.md token budgets raised 3x; reference config [standard]
- **Source**: AC-US5-08
- **Evaluator**: sw:grill
- **Verify**: `grep -c ": 400\|: 500\|: 600" pm/SKILL.md brainstorm/SKILL.md` returns 0; `quality.tokenBudgets` referenced
- **Threshold**: Old budgets gone; config reference present
- **Result**: [ ] PENDING

### R-027: team-lead heartbeat thresholds raised (5min no-progress, 20min total) [standard]
- **Source**: AC-US5-06
- **Evaluator**: sw:grill
- **Verify**: Old 2min/10min values gone; 5min/20min documented with 4.7 rationale
- **Threshold**: New thresholds present
- **Result**: [ ] PENDING

### R-028: team-lead active-phase forbidden-list removed [standard]
- **Source**: AC-US5-09
- **Evaluator**: sw:grill
- **Verify**: `grep -c "forbidden.*list\|forbidden-list" team-lead/SKILL.md` returns 0
- **Threshold**: Zero matches
- **Result**: [ ] PENDING

---

## Functional Correctness — US-006: Deprecated Skills

### R-029: All 7 target skills have [DEPRECATED] prefix and migration note [blocking]
- **Source**: AC-US6-01, AC-US6-04
- **Evaluator**: sw:grill
- **Verify**: `grep -c "\[DEPRECATED\]"` on each of the 7 SKILL.md files returns ≥ 1; migration note present in each
- **Threshold**: All 7 files have deprecation notice and migration note
- **Result**: [ ] PENDING

### R-030: github-issue-standard content moved to docs; SKILL.md is thin redirect [blocking]
- **Source**: AC-US6-02
- **Evaluator**: sw:grill
- **Verify**: `.specweave/docs/internal/specs/github-issue-standard.md` exists with content > 50 lines; `wc -l github-issue-standard/SKILL.md` < 20
- **Threshold**: Content in docs; SKILL.md < 20 lines
- **Result**: [ ] PENDING

### R-031: help SKILL.md hides deprecated by default; --deprecated flag present [standard]
- **Source**: AC-US6-03
- **Evaluator**: sw:grill
- **Verify**: Filtering logic documented; `--deprecated` flag section present
- **Threshold**: Both present
- **Result**: [ ] PENDING

### R-032: skill-deprecation-policy.md created with lifecycle and current batch [standard]
- **Source**: AC-US6-05
- **Evaluator**: sw:grill
- **Verify**: File exists; 3-release lifecycle documented; all 7 deprecated skill names present
- **Threshold**: File present with complete content
- **Result**: [ ] PENDING

---

## Functional Correctness — US-007: Skill Consolidation

### R-033: tdd-cycle SKILL.md supports --phase red|green|refactor|all [blocking]
- **Source**: AC-US7-01
- **Evaluator**: sw:grill
- **Verify**: `grep -c "\-\-phase" tdd-cycle/SKILL.md` returns ≥ 3; all 4 phase values documented
- **Threshold**: All 4 phase values present
- **Result**: [ ] PENDING

### R-034: multi-project SKILL.md created with --tool github|ado|jira [blocking]
- **Source**: AC-US7-02
- **Evaluator**: sw:grill
- **Verify**: File exists; `--tool` flag with 3 values; JIRA covered; deprecated originals have migration notes
- **Threshold**: File present with all 3 tool values
- **Result**: [ ] PENDING

### R-035: resource-base.ts shared validator module exists and tests pass [standard]
- **Source**: AC-US7-03
- **Evaluator**: sw:grill
- **Verify**: `src/core/validators/resource-base.ts` exists; unit tests pass
- **Threshold**: File present; all tests green
- **Result**: [ ] PENDING

### R-036: team-build folded into team-lead --preset; team-build is thin alias [standard]
- **Source**: AC-US7-04
- **Evaluator**: sw:grill
- **Verify**: `--preset` section in team-lead SKILL.md; `wc -l team-build/SKILL.md` < 30
- **Threshold**: --preset present; team-build < 30 lines
- **Result**: [ ] PENDING

### R-037: close-all SKILL.md simplified to ≤60 lines; delegates to sw:done [standard]
- **Source**: AC-US7-06
- **Evaluator**: sw:grill
- **Verify**: `wc -l close-all/SKILL.md` ≤ 60; `grep -c "sw:done" close-all/SKILL.md` ≥ 1
- **Threshold**: ≤60 lines; sw:done delegation present
- **Result**: [ ] PENDING

### R-038: marketplace.json has alias routing for all deprecated skills [blocking]
- **Source**: AC-US7-07
- **Evaluator**: sw:grill
- **Verify**: `jq '[.skills[] | select(.deprecated == true)] | length' marketplace.json` ≥ 7; alias entries for TDD trio and multi-project skills
- **Threshold**: ≥7 deprecated entries; alias routing present
- **Result**: [ ] PENDING

---

## Functional Correctness — US-008: Agent Templates

### R-039: _protocol.md created with shared agent protocol content [blocking]
- **Source**: AC-US8-02, AC-US8-03
- **Evaluator**: sw:grill
- **Verify**: File exists at `agents/_protocol.md`; `wc -l _protocol.md` ≥ 40; contains TaskUpdate, PLAN_READY, COMPLETION; all other templates have "See shared protocol" header
- **Threshold**: File present ≥40 lines; all templates reference it
- **Result**: [ ] PENDING

### R-040: Orphan agent templates deleted; no references remain [blocking]
- **Source**: AC-US8-01
- **Evaluator**: sw:grill
- **Verify**: `ls reviewer-logic.md reviewer-performance.md` exits non-zero; `git grep "reviewer-logic\|reviewer-performance"` returns zero
- **Threshold**: Files absent; no references
- **Result**: [ ] PENDING

### R-041: template-loader.ts auto-prepends _protocol.md; unit tests pass [blocking]
- **Source**: AC-US8-05
- **Evaluator**: sw:grill
- **Verify**: `src/core/team-lead/template-loader.ts` prepends protocol content; unit test asserting protocol at start of assembled prompt passes
- **Threshold**: Unit test green
- **Result**: [ ] PENDING

---

## Functional Correctness — US-009: Config Knobs

### R-042: config/schema.ts adds all 4 new knobs with correct defaults and validation [blocking]
- **Source**: AC-US9-01, AC-US9-02, AC-US9-03, AC-US9-04
- **Evaluator**: sw:grill
- **Verify**: Schema tests pass; 4 new keys present with correct defaults (`xhigh`, default list, 50, empty map)
- **Threshold**: All schema tests green; 4 keys present
- **Result**: [ ] PENDING

### R-043: config-reference.md documents all new knobs [standard]
- **Source**: AC-US9-05
- **Evaluator**: sw:grill
- **Verify**: File exists; `grep -c "Default:" config-reference.md` ≥ 4; all 4 knobs documented
- **Threshold**: File present with ≥4 Default entries
- **Result**: [ ] PENDING

---

## Functional Correctness — US-010, US-011, US-012

### R-044: tool-use-rationale blocks present in all 9 target SKILL.md files [blocking]
- **Source**: AC-US10-01, AC-US10-02
- **Evaluator**: sw:grill
- **Verify**: `grep -rn "tool-use-rationale\|Tool-Use Rationale" plugins/specweave/skills/{judge-llm,grill,code-reviewer,do,pm,architect,done,team-lead,increment}/SKILL.md` returns 9 matches
- **Threshold**: 9 matches
- **Result**: [ ] PENDING

### R-045: skill-lint.ts enforces tool-use-rationale; effort-levels.md exists; auto-mode-decision-tree.md exists [blocking]
- **Source**: AC-US10-03, AC-US11-01, AC-US12-04
- **Evaluator**: sw:grill
- **Verify**: `plugins/specweave/.lint/skill-lint.ts` exists and lint tests pass; both doc files exist at expected paths
- **Threshold**: Lint tests green; both doc files present
- **Result**: [ ] PENDING

---

## Infrastructure Criteria

### R-046: Unit test coverage ≥ 95% on all new TypeScript modules [blocking]
- **Source**: NFR-5.3 (Testing Strategy — unit coverage target)
- **Evaluator**: sw:grill
- **Verify**: Run `npx vitest run --coverage` on new files: `static-context-loader.ts`, `schema.ts` additions, `migrate-config-0669.ts`, `pretooluse-guard.ts`, `template-loader.ts`, `resource-base.ts`, `cache-metrics.ts`, `dispatcher.ts` additions — each at ≥95% line coverage
- **Threshold**: ≥95% line coverage per new module
- **Result**: [ ] PENDING

### R-047: Integration test coverage ≥ 90% on changed code paths [standard]
- **Source**: NFR-5.3 (Testing Strategy — integration coverage target)
- **Evaluator**: sw:grill
- **Verify**: Integration tests for prompt-caching, single-agent parity, tdd-alias-routing, backwards-compat all pass
- **Threshold**: All named integration tests green
- **Result**: [ ] PENDING

### R-048: skill-lint CI job passes — zero retired phrases across all SKILL.md [blocking]
- **Source**: NFR-4.1
- **Evaluator**: sw:grill
- **Verify**: `.github/workflows/skill-lint.yml` exists; the grep step passes on the current SKILL.md files (zero matches for `extended thinking`, `ULTRATHINK BY DEFAULT`, `spawn agents anyway`, `thinking.budget_tokens`)
- **Threshold**: CI step exits 0
- **Result**: [ ] PENDING

### R-049: Non-deprecated skill count ≤ 40 [standard]
- **Source**: NFR-4.2
- **Evaluator**: sw:grill
- **Verify**: Count of skills in `marketplace.json` where `deprecated != true` is ≤ 40
- **Threshold**: ≤40 non-deprecated skills
- **Result**: [ ] PENDING

### R-050: Backwards-compatibility regression test suite is green [blocking]
- **Source**: NFR-1.1
- **Evaluator**: sw:grill
- **Verify**: `test/integration/backwards-compat-0669.test.ts` passes all 5 archived-increment open/resume/close scenarios
- **Threshold**: All 5 scenarios pass
- **Result**: [ ] PENDING

### R-051: Existing state marker files tolerated (no crash) at upgrade time [standard]
- **Source**: NFR-1.2
- **Evaluator**: sw:grill
- **Verify**: Running the guard with pre-existing `.specweave/state/interview-*.json` and `skill-chain-*.json` files present does not error; files are ignored silently
- **Threshold**: No crash; files silently ignored
- **Result**: [ ] PENDING

### R-052: All deprecated CLI flags have --<name>-compat aliases that still work [standard]
- **Source**: NFR-1.3
- **Evaluator**: sw:grill
- **Verify**: `sw:auto --simple-compat` emits a deprecation warning and succeeds; integration test `test/integration/auto-simple-compat.test.ts` passes
- **Threshold**: --simple-compat functional; integration test green
- **Result**: [ ] PENDING

### R-053: marketplace.json retains deprecated skill entries for ≥ 2 minor releases [standard]
- **Source**: NFR-1.4
- **Evaluator**: sw:grill
- **Verify**: All 7 deprecated skills remain in marketplace.json with `deprecated: true`; no entry is removed
- **Threshold**: All 7 entries present
- **Result**: [ ] PENDING

### R-054: quality.thinkingBudget: "legacy" re-enables pre-4.7 thinking parameter behavior [blocking]
- **Source**: NFR-2.1
- **Evaluator**: sw:grill
- **Verify**: With `quality.thinkingBudget: "legacy"` set, `skill-judge.ts` includes the `thinking` parameter in the API call regardless of model version; unit test covers this branch
- **Threshold**: Unit test for legacy-mode branch passes
- **Result**: [ ] PENDING

### R-055: opus-47-migration.md covers all retired workarounds with opt-out paths [blocking]
- **Source**: NFR-3.1
- **Evaluator**: sw:grill
- **Verify**: File exists; contains entries for all P0 and P1 behavioral changes; each entry has an opt-out flag documented
- **Threshold**: All changes covered; opt-out paths documented
- **Result**: [ ] PENDING

### R-056: CHANGELOG.md has Opus 4.7 Alignment entry with links to migration doc [standard]
- **Source**: NFR-3.2
- **Evaluator**: sw:grill
- **Verify**: `grep -c "Opus 4.7 Alignment\|v1.1.0" CHANGELOG.md` ≥ 2; migration doc link present
- **Threshold**: Entry and link present
- **Result**: [ ] PENDING

### R-057: README.md "Upgrading" section references migration doc and lists P0 fixes [standard]
- **Source**: NFR-3.3
- **Evaluator**: sw:grill
- **Verify**: "Upgrading" section exists; `opus-47-migration.md` linked; 3 P0 fixes listed
- **Threshold**: Section present with correct content
- **Result**: [ ] PENDING

### R-058: Agent-spawn benchmark shows ≥50% reduction for baseline 5-task increment [blocking]
- **Source**: NFR-4.4
- **Evaluator**: sw:grill
- **Verify**: `test/benchmarks/agent-spawn-count.bench.ts` runs; post-0669 spawn count ≤ pre-0669 × 0.5
- **Threshold**: ≥50% reduction vs baseline
- **Result**: [ ] PENDING

### R-059: sw:grill report on 0669 increment shows zero critical and zero high findings [blocking]
- **Source**: NFR-5.1
- **Evaluator**: sw:grill
- **Verify**: Run `sw:grill` on this increment; `grill-report.json` shows `critical: 0`, `high: 0`
- **Threshold**: Zero critical, zero high
- **Result**: [ ] PENDING

### R-060: sw:judge-llm report on sampled skill changes shows PASS or PASS_WITH_NOTES [blocking]
- **Source**: NFR-5.2
- **Evaluator**: sw:judge-llm
- **Verify**: Run `sw:judge-llm` sampling judge-llm/SKILL.md, team-lead/SKILL.md, code-reviewer/SKILL.md; verdict in `judge-llm-report.json` is PASS or PASS_WITH_NOTES
- **Threshold**: PASS or PASS_WITH_NOTES verdict
- **Result**: [ ] PENDING
