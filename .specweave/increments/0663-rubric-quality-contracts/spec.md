---
increment: 0663-rubric-quality-contracts
title: Rubric Quality Contracts for Increment Closure
type: feature
priority: P1
status: completed
created: 2026-04-12T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Rubric Quality Contracts for Increment Closure

## Problem Statement

Closure gates (code-review, grill, judge-llm) have hardcoded pass/fail logic in `completion-validator.ts`. Users cannot customize what "quality" means per project or per increment. A solo developer may accept advisory-only coverage warnings, while a workspace owner may mandate zero critical findings AND 95% branch coverage. Today, the only recourse is editing `config.json` booleans (`grill.required`, `codeReview.required`) which are blunt on/off switches with no per-criterion granularity.

## Goals

- Introduce `rubric.md` as a per-increment quality contract: human-readable, machine-evaluatable
- Auto-generate rubric criteria from spec.md acceptance criteria during planning
- Support three-tier inheritance: global defaults -> project defaults -> per-increment
- Each criterion is binary (PASS/FAIL) with a severity of `[blocking]` or `[advisory]`
- Each criterion is assigned to an evaluator (grill, code-reviewer, judge-llm, coverage)
- During closure, gates evaluate their owned criteria and update rubric.md with results
- `completion-validator.ts` checks all `[blocking]` criteria are PASS before allowing closure
- Full backward compatibility: no `rubric.md` = current hardcoded behavior unchanged

## Personas

- **Solo Developer**: Uses defaults without customization. rubric.md is auto-generated and works out of the box.
- **Workspace Owner**: Customizes project-level `rubric-defaults.md` to enforce team quality standards across all increments.
- **CI/CD Pipeline**: Needs deterministic, machine-readable pass/fail from rubric validation for automated gates.

## User Stories

### US-001: Rubric Type System and Parsing (P0)
**Project**: specweave

**As a** SpecWeave developer
**I want** a well-defined type system and markdown parser for rubric.md
**So that** rubric criteria can be reliably read, validated, and manipulated by all consuming modules

**Acceptance Criteria**:
- [x] **AC-US1-01**: Given a valid rubric.md file with frontmatter and criteria sections, when `RubricParser.parse()` is called, then it returns a `Rubric` object containing all criteria with their IDs, titles, severities, sources, evaluators, verify descriptions, thresholds, and results
  - **Priority**: P0
- [x] **AC-US1-02**: Given a criterion line `### R-001: Title [blocking]`, when parsed, then `severity` is `"blocking"` and `id` is `"R-001"` and `title` is `"Title"`
  - **Priority**: P0
- [x] **AC-US1-03**: Given a criterion line `### R-005: Advisory Title [advisory]`, when parsed, then `severity` is `"advisory"`
  - **Priority**: P0
- [x] **AC-US1-04**: Given a criterion with `- **Result**: [ ] PENDING`, when parsed, then `result` is `"PENDING"`; given `- **Result**: [x] PASS`, then `result` is `"PASS"`; given `- **Result**: [!] FAIL`, then `result` is `"FAIL"`
  - **Priority**: P0
- [x] **AC-US1-05**: Given a criterion with `- **Evaluator**: grill`, when parsed, then `evaluator` is `"grill"`; supported evaluators are: `grill`, `code-reviewer`, `judge-llm`, `coverage`
  - **Priority**: P0
- [x] **AC-US1-06**: Given a criterion with `- **Source**: AC-US1-01, AC-US1-02`, when parsed, then `sources` is `["AC-US1-01", "AC-US1-02"]`
  - **Priority**: P0
- [x] **AC-US1-07**: Given a rubric.md with no frontmatter or malformed markdown, when `RubricParser.parse()` is called, then it throws a descriptive `RubricParseError` with line number context
  - **Priority**: P1
- [x] **AC-US1-08**: Given the `RubricCriterion` type, then it exports fields: `id: string`, `title: string`, `severity: "blocking" | "advisory"`, `sources: string[]`, `evaluator: RubricEvaluator`, `verify: string`, `threshold: string`, `result: RubricResult`, `category: string`
  - **Priority**: P0

---

### US-002: Rubric Generation from Acceptance Criteria (P0)
**Project**: specweave

**As a** planner agent (sw-planner)
**I want** rubric.md auto-generated from spec.md acceptance criteria
**So that** every increment gets a quality contract without manual authoring

**Acceptance Criteria**:
- [x] **AC-US2-01**: Given a spec.md with N acceptance criteria across M user stories, when `RubricGenerator.generate(specContent)` is called, then it produces a rubric.md with at least N functional correctness criteria (one per AC or grouped by related ACs)
  - **Priority**: P0
- [x] **AC-US2-02**: Given an AC `AC-US1-01` in spec.md, when a rubric criterion is generated for it, then the criterion's `Source` field contains `AC-US1-01`
  - **Priority**: P0
- [x] **AC-US2-03**: Given a generated rubric.md, then it also contains standard categories beyond functional correctness: "Test Coverage", "Code Quality", and "Independent Evaluation" with project-default criteria
  - **Priority**: P0
- [x] **AC-US2-04**: Given project-level defaults exist in `.specweave/rubric-defaults.md`, when generating a rubric, then default criteria from that file are merged into the generated rubric (matched by criterion ID, lower tier overrides higher)
  - **Priority**: P1
- [x] **AC-US2-05**: Given global defaults exist in `plugins/specweave/defaults/rubric-defaults.md`, when generating a rubric and no project defaults exist, then global defaults are used as the base
  - **Priority**: P1
- [x] **AC-US2-06**: Given the generated rubric.md, then it has YAML frontmatter with fields: `increment`, `title`, `generated` (ISO timestamp), `source`, `version`, `status: pending`
  - **Priority**: P0
- [x] **AC-US2-07**: Given the generated rubric.md, then all criteria have `Result: [ ] PENDING` initially
  - **Priority**: P0
- [x] **AC-US2-08**: Given spec.md has a `coverageTarget` in frontmatter or metadata.json has `coverageTarget`, when generating the "Test Coverage" category, then the threshold uses the actual target (e.g., `>= 90% line coverage`)
  - **Priority**: P1

---

### US-003: Three-Tier Rubric Inheritance (P1)
**Project**: specweave

**As a** workspace owner
**I want** rubric defaults inherited at three tiers (global -> project -> increment)
**So that** I can set organization-wide quality standards while allowing per-increment overrides

**Acceptance Criteria**:
- [x] **AC-US3-01**: Given a global defaults file at `plugins/specweave/defaults/rubric-defaults.md` with criteria R-D01 through R-D05, when no project defaults exist and a rubric is generated, then all 5 global criteria appear in the output
  - **Priority**: P1
- [x] **AC-US3-02**: Given a project defaults file at `.specweave/rubric-defaults.md` with criterion R-D01 that overrides the global R-D01 (different threshold), when a rubric is generated, then the project version of R-D01 is used
  - **Priority**: P1
- [x] **AC-US3-03**: Given a per-increment rubric.md with criterion R-D01 that further overrides the project R-D01, when the rubric is evaluated, then the per-increment version takes precedence
  - **Priority**: P1
- [x] **AC-US3-04**: Given a merge operation between tiers, when criterion IDs collide, then the lower tier (closer to increment) wins completely (no field-level merge)
  - **Priority**: P1
- [x] **AC-US3-05**: Given no `rubric-defaults.md` files exist at any tier, when a rubric is generated, then only spec-derived criteria and hardcoded standard categories are included (no error)
  - **Priority**: P0

---

### US-004: Rubric Evaluation by Closure Gates (P0)
**Project**: specweave

**As a** closure gate (grill, code-reviewer, judge-llm)
**I want** to evaluate only the rubric criteria assigned to me and write results back
**So that** each gate's findings are recorded as structured pass/fail in rubric.md

**Acceptance Criteria**:
- [x] **AC-US4-01**: Given a rubric.md with 3 criteria assigned to `grill` evaluator, when sw:grill runs, then it reads those 3 criteria and updates their `Result` field to `[x] PASS` or `[!] FAIL` with a reason
  - **Priority**: P0
- [x] **AC-US4-02**: Given a rubric.md with 2 criteria assigned to `code-reviewer` evaluator, when sw:code-reviewer runs, then it reads those 2 criteria and updates their `Result` field
  - **Priority**: P0
- [x] **AC-US4-03**: Given a rubric.md with 1 criterion assigned to `judge-llm` evaluator, when sw:judge-llm runs, then it reads that criterion and updates its `Result` field
  - **Priority**: P0
- [x] **AC-US4-04**: Given a rubric.md with 1 criterion assigned to `coverage` evaluator, when coverage validation runs in completion-validator, then it reads that criterion and updates its `Result` field based on actual coverage data
  - **Priority**: P1
- [x] **AC-US4-05**: Given a gate evaluates a criterion and sets it to FAIL, then the result line includes a brief reason: `- **Result**: [!] FAIL — 2 critical findings remain`
  - **Priority**: P0
- [x] **AC-US4-06**: Given no rubric.md exists in the increment directory, when a gate runs, then it proceeds with its existing behavior unchanged (backward compatibility)
  - **Priority**: P0
- [x] **AC-US4-07**: Given `RubricEvaluator.evaluateForGate(incrementPath, gateName)` is called, then it returns only criteria where `evaluator === gateName` and provides a `writeResults(results)` method to update rubric.md
  - **Priority**: P0

---

### US-005: Completion Validator Rubric Integration (P0)
**Project**: specweave

**As a** completion validator (sw:done flow)
**I want** to check all blocking rubric criteria are PASS before allowing closure
**So that** increments cannot close with unmet quality contracts

**Acceptance Criteria**:
- [x] **AC-US5-01**: Given a rubric.md where all `[blocking]` criteria have `[x] PASS`, when `IncrementCompletionValidator.validateCompletion()` runs, then rubric validation produces zero errors
  - **Priority**: P0
- [x] **AC-US5-02**: Given a rubric.md where 2 `[blocking]` criteria have `[!] FAIL`, when validation runs, then it adds an error: `"Rubric: 2 blocking criteria failed: R-001 (Title), R-003 (Title)"`
  - **Priority**: P0
- [x] **AC-US5-03**: Given a rubric.md where 1 `[blocking]` criterion has `[ ] PENDING`, when validation runs, then it adds an error: `"Rubric: 1 blocking criterion not yet evaluated: R-002 (Title)"`
  - **Priority**: P0
- [x] **AC-US5-04**: Given a rubric.md where all `[blocking]` criteria pass but 2 `[advisory]` criteria are FAIL, when validation runs, then advisory failures are reported as warnings (non-blocking)
  - **Priority**: P0
- [x] **AC-US5-05**: Given no rubric.md exists in the increment directory, when validation runs, then the existing hardcoded gate logic runs unchanged (full backward compatibility)
  - **Priority**: P0
- [x] **AC-US5-06**: Given both rubric validation AND existing hardcoded gates run (defense in depth), when results are collected, then errors from both sources are combined in the final `ValidationResult`
  - **Priority**: P0
- [x] **AC-US5-07**: Given config.json has `rubric.required: false`, when validation runs, then rubric validation is skipped entirely (opt-out mechanism)
  - **Priority**: P1

---

### US-006: Template Creator Integration (P1)
**Project**: specweave

**As a** template creator (increment scaffolding)
**I want** rubric.md included in the increment directory alongside spec.md, plan.md, tasks.md
**So that** the rubric file is part of the standard increment structure

**Acceptance Criteria**:
- [x] **AC-US6-01**: Given `createIncrementTemplates()` is called, when an increment directory is created, then a `rubric.md` template file is also created with placeholder content and a comment indicating it will be auto-generated by the planner
  - **Priority**: P1
- [x] **AC-US6-02**: Given the rubric.md template, then it contains YAML frontmatter with `status: template` and a comment block explaining the auto-generation process
  - **Priority**: P1
- [x] **AC-US6-03**: Given the increment structure rule "ONLY metadata.json, spec.md, plan.md, tasks.md" in the increment root, when rubric.md is added, then CLAUDE.md and relevant documentation are updated to list rubric.md as a valid root-level file
  - **Priority**: P2

---

### US-007: Skill Definition Updates (P1)
**Project**: specweave

**As a** skill maintainer
**I want** done, grill, judge-llm, and code-reviewer SKILL.md files updated to reference rubric.md
**So that** each skill knows to read and write rubric criteria during its execution

**Acceptance Criteria**:
- [x] **AC-US7-01**: Given the `sw:done` SKILL.md, when updated, then it instructs the done flow to run rubric validation as part of closure checks
  - **Priority**: P1
- [x] **AC-US7-02**: Given the `sw:grill` SKILL.md, when updated, then it instructs grill to read criteria where `evaluator: grill` and write results back to rubric.md
  - **Priority**: P1
- [x] **AC-US7-03**: Given the `sw:judge-llm` SKILL.md, when updated, then it instructs judge-llm to read criteria where `evaluator: judge-llm` and write results back to rubric.md
  - **Priority**: P1
- [x] **AC-US7-04**: Given the `sw:code-reviewer` SKILL.md, when updated, then it instructs code-reviewer to read criteria where `evaluator: code-reviewer` and write results back to rubric.md
  - **Priority**: P1
- [x] **AC-US7-05**: Given any skill that writes rubric results, when rubric.md does not exist, then the skill logs an info message and proceeds with existing behavior (no crash)
  - **Priority**: P0

---

### US-008: Planner Agent Integration (P1)
**Project**: specweave

**As a** planner agent (sw-planner)
**I want** to generate rubric.md alongside tasks.md during planning
**So that** the quality contract is established before implementation begins

**Acceptance Criteria**:
- [x] **AC-US8-01**: Given sw-planner generates tasks.md, when it finishes, then it also generates rubric.md in the same increment directory using `RubricGenerator`
  - **Priority**: P1
- [x] **AC-US8-02**: Given the planner agent SKILL.md (`sw-planner.md`), when updated, then it includes instructions to generate rubric.md after tasks.md
  - **Priority**: P1
- [x] **AC-US8-03**: Given rubric.md is generated during planning, then the user can review and modify criteria (change severity, add/remove criteria) before implementation begins
  - **Priority**: P1

---

### US-009: Global Default Rubric Criteria (P1)
**Project**: specweave

**As a** SpecWeave framework maintainer
**I want** a `plugins/specweave/defaults/rubric-defaults.md` file with sensible default criteria
**So that** every project gets baseline quality gates without configuration

**Acceptance Criteria**:
- [x] **AC-US9-01**: Given the defaults file exists, then it contains at least these standard categories: "Test Coverage", "Code Quality", "Independent Evaluation"
  - **Priority**: P1
- [x] **AC-US9-02**: Given the "Test Coverage" category, then it includes a blocking criterion for unit test coverage meeting the project's configured target
  - **Priority**: P1
- [x] **AC-US9-03**: Given the "Code Quality" category, then it includes a blocking criterion for zero critical/high code review findings
  - **Priority**: P1
- [x] **AC-US9-04**: Given the "Independent Evaluation" category, then it includes a blocking criterion for grill ship-readiness (`shipReadiness !== "NOT READY"`) and a blocking criterion for judge-llm verdict (`verdict !== "REJECTED"`)
  - **Priority**: P1
- [x] **AC-US9-05**: Given the defaults file, then all criteria use IDs prefixed with `R-D` (e.g., `R-D01`, `R-D02`) to distinguish them from spec-derived criteria (`R-001`, `R-002`)
  - **Priority**: P1

---

### US-010: Backward Compatibility (P0)
**Project**: specweave

**As a** user with existing increments (no rubric.md)
**I want** the system to work exactly as before when rubric.md is absent
**So that** the feature is fully opt-in and non-breaking

**Acceptance Criteria**:
- [x] **AC-US10-01**: Given an increment directory with no rubric.md, when `sw:done` runs, then all existing hardcoded gates (grill-report check, judge-llm check, code-review check, coverage check) execute unchanged
  - **Priority**: P0
- [x] **AC-US10-02**: Given an increment directory with no rubric.md, when `sw:grill` runs, then it produces `grill-report.json` without attempting rubric reads or writes
  - **Priority**: P0
- [x] **AC-US10-03**: Given an increment directory with no rubric.md, when `sw:code-reviewer` runs, then it produces `code-review-report.json` without attempting rubric reads or writes
  - **Priority**: P0
- [x] **AC-US10-04**: Given an increment created before this feature existed, when it goes through the full closure flow, then zero new errors or warnings appear that reference rubric.md
  - **Priority**: P0
- [x] **AC-US10-05**: Given `config.json` has no `rubric` section, when any rubric-related code path executes, then it defaults to backward-compatible behavior (rubric validation skipped if no rubric.md present)
  - **Priority**: P0

## Functional Requirements

### FR-001: Rubric Module Architecture
A new `src/core/rubric/` module with the following files:
- `types.ts` -- `RubricCriterion`, `Rubric`, `RubricResult`, `RubricEvaluator`, `RubricSeverity` types
- `rubric-parser.ts` -- Parses rubric.md markdown into `Rubric` object
- `rubric-generator.ts` -- Generates rubric.md from spec.md content + defaults inheritance
- `rubric-evaluator.ts` -- Reads criteria for a gate, provides `writeResults()` to update rubric.md
- `index.ts` -- Public API barrel export

### FR-002: Criterion Format
Each criterion follows this exact markdown format:
```markdown
### R-001: Title [blocking]
- **Source**: AC-US1-01, AC-US1-02
- **Evaluator**: grill
- **Verify**: Human-readable check description
- **Threshold**: Measurable pass/fail condition
- **Result**: [ ] PENDING
```

Result states: `[ ] PENDING`, `[x] PASS`, `[!] FAIL -- reason`

### FR-003: Severity Model
Two severity levels only:
- `[blocking]` -- Must pass for closure. Failure = error in completion-validator.
- `[advisory]` -- Reported only. Failure = warning in completion-validator.

No scoring, no weighted grades, no partial credit. Binary pass/fail.

### FR-004: Inheritance Resolution
Merge order (later overrides earlier):
1. `plugins/specweave/defaults/rubric-defaults.md` (global)
2. `.specweave/rubric-defaults.md` (project)
3. Per-increment `rubric.md` (increment -- user-edited after generation)

Merge by criterion ID. When IDs collide, the lower tier replaces the entire criterion (no field-level merge).

### FR-005: Defense in Depth
Both rubric validation AND existing hardcoded gates run during closure. This is intentional redundancy -- the existing gates serve as a safety net even if rubric.md is malformed or missing criteria. Neither system can disable the other.

## Architecture Decisions

- **Two severity levels ONLY**: blocking and advisory. No scoring or weighted grades -- keeps the system deterministic for CI/CD.
- **One rubric.md per increment**: Lives in the increment folder alongside spec.md, plan.md, tasks.md.
- **Pass/fail only**: Binary. Each criterion is either PASS or FAIL. No percentages, no grades.
- **Defense in depth**: Existing hardcoded gates continue to run alongside rubric validation. Both must pass.
- **Merge by ID, whole-criterion replacement**: When tiers collide on criterion ID, the lower tier wins completely. No field-level merge complexity.

## Implementation Scope

All changes target the specweave repo at `repositories/anton-abyzov/specweave/`:

1. **New** `src/core/rubric/` module: `types.ts`, `rubric-parser.ts`, `rubric-generator.ts`, `rubric-evaluator.ts`, `index.ts`
2. **Modified** `src/core/increment/completion-validator.ts` -- add rubric validation gate
3. **Modified** `src/core/increment/template-creator.ts` -- add rubric.md to increment scaffolding
4. **Modified** SKILL.md files: `plugins/specweave/skills/done/SKILL.md`, `plugins/specweave/skills/grill/SKILL.md`, `plugins/specweave/skills/judge-llm/SKILL.md`, `plugins/specweave/skills/code-reviewer/SKILL.md`
5. **Modified** planner agent: `plugins/specweave/agents/sw-planner.md` -- generate rubric.md alongside tasks.md
6. **New** `plugins/specweave/defaults/rubric-defaults.md` -- global default criteria

## Non-Functional Requirements

- **Performance**: Rubric parsing and validation must complete in < 50ms for a 50-criterion rubric
- **File Size**: Generated rubric.md should not exceed 500 lines for a typical 10-user-story increment
- **Compatibility**: ESM module system, no new npm dependencies
- **Reliability**: Malformed rubric.md must never crash the closure flow -- degrade to warnings

## Out of Scope

- Rubric editor UI (web dashboard)
- Rubric diffing or version history
- Automated criterion weight tuning
- Rubric templates marketplace
- Integration with external quality tools (SonarQube, CodeClimate)
- Rubric-based branch protection rules
- Criterion dependencies (R-001 depends on R-002)

## Dependencies

- `src/core/increment/completion-validator.ts` -- integration point for closure validation
- `src/core/increment/template-creator.ts` -- integration point for scaffolding
- `plugins/specweave/agents/sw-planner.md` -- integration point for generation
- Existing report files: `grill-report.json`, `code-review-report.json`, `judge-llm-report.json`

## Edge Cases

- **Empty spec.md**: Generator produces rubric with only default criteria (no functional correctness section)
- **Spec with 0 ACs**: Same as empty spec -- only defaults
- **Malformed rubric.md**: Parser throws `RubricParseError`, completion-validator catches it and adds a warning (non-blocking)
- **Criterion with unknown evaluator**: Parser accepts it, evaluator skips it, completion-validator warns about unevaluated blocking criteria
- **rubric.md deleted mid-implementation**: Gates skip rubric operations, completion-validator falls back to hardcoded behavior
- **Concurrent gate execution**: Each gate reads/writes only its own criteria -- no cross-gate conflicts as long as criteria IDs are unique per evaluator
- **100+ criteria rubric**: Parser handles efficiently (line-by-line scan, no regex backtracking)

## Risks

| Risk | Probability | Impact | Severity | Mitigation |
|------|-------------|--------|----------|------------|
| rubric.md format drift from spec.md changes | 0.3 | 4 | 1.2 | Generator re-runs are idempotent; user edits preserved by ID |
| Gate writes to rubric.md conflict during parallel execution | 0.2 | 5 | 1.0 | Each gate writes only its own evaluator criteria |
| Users confused by dual validation (rubric + hardcoded) | 0.3 | 3 | 0.9 | Documentation clearly explains defense-in-depth rationale |
| Inheritance complexity leads to unexpected criterion overrides | 0.2 | 4 | 0.8 | Whole-criterion replacement (no field merge) simplifies mental model |

## Success Metrics

- 100% of new increments created after this feature have auto-generated rubric.md
- Zero regressions in existing increments without rubric.md (backward compatibility)
- Closure gates correctly evaluate and update rubric criteria for 100% of criteria they own
- completion-validator blocks closure on any FAIL or PENDING blocking criterion
- Three-tier inheritance resolves correctly in all test scenarios
