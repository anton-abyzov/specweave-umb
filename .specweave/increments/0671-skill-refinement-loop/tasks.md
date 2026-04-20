# 0671 — Skill Refinement Loop — Tasks

## Phase 1 — Schema & signal emission

### T-001: Extend skill-signals.json schema to v2
**User Story:** US-001 | **Satisfies ACs:** AC-US1-04 | **Status:** [x] completed
**Test Plan (BDD):**
- Given an existing v1 `skill-signals.json` with 3 generation signals
- When `reader.read()` is invoked
- Then file is migrated in-memory to v2 (schemaVersion: 2) without data loss, and on next write the v2 format is persisted

### T-002: Implement appendRefinement() writer
**User Story:** US-001 | **Satisfies ACs:** AC-US1-01 | **Status:** [x] completed
**Test Plan (BDD):**
- Given an empty signals file
- When `appendRefinement({source, targetSkill, severity, incrementId, evidence})` is called
- Then the file contains exactly one entry with `type: "refinement"`, a generated `id`, and `consumedBy: null`

### T-003: Implement listForSkill() reader
**User Story:** US-002, US-004 | **Satisfies ACs:** AC-US2-01, AC-US4-01 | **Status:** [x] completed
**Test Plan (BDD):**
- Given a signals file with mixed generation + refinement entries across 3 target skills
- When `listForSkill("sw:architect", {lastNIncrements: 5})` is called
- Then only refinement signals targeting "sw:architect" within the last 5 increment IDs are returned, sorted by severity × recency

### T-004: Emit refinement signal from sw:judge-llm
**User Story:** US-001 | **Satisfies ACs:** AC-US1-01 | **Status:** [x] completed
**Test Plan (BDD):**
- Given a mock judge-llm-report.json with a finding that references skill slug "sw:architect" in its evidence
- When the judge-llm skill's post-processing runs
- Then a refinement signal is appended to skill-signals.json with source="judge-llm" and the correct targetSkill

### T-005: Emit refinement signal from rubric evaluator
**User Story:** US-001 | **Satisfies ACs:** AC-US1-02 | **Status:** [x] completed
**Test Plan (BDD):**
- Given a rubric criterion "skip-validation" has failed and the rubric rationale references a skill's instruction
- When the evaluator finalizes the report
- Then a refinement signal is emitted with source="rubric" and targetSkill populated via the attribution heuristics (see plan.md)

### T-006: Emit refinement signal from sw:code-reviewer
**User Story:** US-001 | **Satisfies ACs:** AC-US1-03 | **Status:** [x] completed
**Test Plan (BDD):**
- Given a code-reviewer critical finding attributable to a skill's instruction (via direct trace or evidence pattern match)
- When the review completes
- Then a refinement signal is emitted with source="code-reviewer" and correct targetSkill

## Phase 2 — sw:skill-refine skill

### T-007: Scaffold sw:skill-refine skill definition
**User Story:** US-002 | **Satisfies ACs:** AC-US2-01..06 | **Status:** [x] completed
**Test Plan (BDD):**
- Given the plugin loader
- When it scans plugins/specweave/skills/
- Then `sw:skill-refine` appears in the available-skills list with the documented slash command and flags

### T-008: Implement signal aggregation for a target skill
**User Story:** US-002 | **Satisfies ACs:** AC-US2-01 | **Status:** [x] completed
**Test Plan (BDD):**
- Given signals for "sw:architect" from 3 increments
- When aggregation is invoked
- Then the aggregate output includes signal count by source, severity distribution, evidence list, and N-increment window

### T-009: Haiku-based diff proposal
**User Story:** US-002 | **Satisfies ACs:** AC-US2-02 | **Status:** [x] completed
**Test Plan (BDD):**
- Given a current SKILL.md + aggregate signal data
- When the diff proposer runs with temperature=0
- Then it returns a unified diff plus a rationale string; repeat runs with same inputs produce identical diff (determinism check)

### T-010: Interactive approve/reject/edit UI
**User Story:** US-002 | **Satisfies ACs:** AC-US2-03 | **Status:** [x] completed
**Test Plan (BDD):**
- Given a proposed diff
- When the user chooses "reject"
- Then no file is written; the ledger records a rejection with reason

### T-011: Diff application + git commit + ledger entry
**User Story:** US-002 | **Satisfies ACs:** AC-US2-04, AC-US2-05 | **Status:** [x] completed
**Test Plan (BDD):**
- Given an approved diff
- When write-back runs in a git repo
- Then the SKILL.md is updated, `git commit -m "refine(<skill>): <rationale>"` succeeds, and `.specweave/state/skill-refinements.json` gains an entry with the commit SHA

### T-012: Flag handling: --dry-run, --show-signals, --scope
**User Story:** US-002 | **Satisfies ACs:** AC-US2-06 | **Status:** [x] completed
**Test Plan (BDD):**
- Given `--dry-run`
- When sw:skill-refine runs
- Then no writes occur and the diff is printed to stdout only

## Phase 3 — Reflect nudge + dashboard

### T-013: Session-end nudge in reflect stop-hook
**User Story:** US-003 | **Satisfies ACs:** AC-US3-01, AC-US3-03, AC-US3-04 | **Status:** [x] completed
**Test Plan (BDD):**
- Given a session with 2 refinement signals and 1 high-confidence learning
- When /sw:done closes the increment
- Then a single-line prompt is printed naming the top suggestion; no command is auto-executed

### T-014: Config gate for nudge (reflect.autoNudge)
**User Story:** US-003 | **Satisfies ACs:** AC-US3-02 | **Status:** [x] completed
**Test Plan (BDD):**
- Given `.specweave/config.json` has `reflect.autoNudge: false`
- When /sw:done closes with pending suggestions
- Then no nudge is printed

### T-015: Dashboard section in sw:reflect --status
**User Story:** US-004 | **Satisfies ACs:** AC-US4-01, AC-US4-02, AC-US4-03 | **Status:** [x] completed
**Test Plan (BDD):**
- Given 2 skills have ≥3 negative signals and 1 skill has 2 signals
- When `sw:reflect --status` runs
- Then the output `## Skill Refinement Suggestions` section lists the 2 qualifying skills with their counts and a `sw:skill-refine <slug>` hint, and the 3rd skill is omitted

### T-016: Omit dashboard section when no skills qualify
**User Story:** US-004 | **Satisfies ACs:** AC-US4-03 | **Status:** [x] completed
**Test Plan (BDD):**
- Given zero skills meet the threshold
- When status runs
- Then the Refinement Suggestions heading is not emitted at all

## Phase 4 — ADRs & red lines

### T-017: Write ADR-0671-01 no-runtime-mutation
**User Story:** US-005 | **Satisfies ACs:** AC-US5-01 | **Status:** [x] completed
**Test Plan (BDD):**
- Given the ADR directory
- When T-017 completes
- Then `.specweave/docs/internal/architecture/adr/0671-01-no-runtime-skill-mutation.md` exists with Decision/Consequence/Alternative sections

### T-018: Write ADR-0671-02 registry-immutability
**User Story:** US-005 | **Satisfies ACs:** AC-US5-02 | **Status:** [x] completed
**Test Plan (BDD):**
- Given the ADR directory
- When T-018 completes
- Then the ADR file exists with explicit "bit-identical for the lifetime of the version" language

### T-019: Write ADR-0671-03 no-self-improving-marketing
**User Story:** US-005 | **Satisfies ACs:** AC-US5-03 | **Status:** [x] completed
**Test Plan (BDD):**
- Given the ADR directory
- When T-019 completes
- Then the ADR names the two preconditions (reproducibility guarantee + audit log) required to lift the restriction

### T-020: Write ADR-0671-04 no-goodhart-loop
**User Story:** US-005 | **Satisfies ACs:** AC-US5-04 | **Status:** [x] completed
**Test Plan (BDD):**
- Given the ADR directory
- When T-020 completes
- Then the ADR contains the rule "a signal emitted by gate G in session S may not validate a refinement to its source skill within session S"

## Phase 5 — Docs, tests, closure

### T-021: Unit-test coverage ≥90% for signal/refine code
**User Story:** all | **Status:** [x] completed
**Test Plan (BDD):**
- Given the new src/core/skill-signals/ and src/skills/skill-refine.ts
- When `npx vitest run --coverage` is executed
- Then coverage for new files is ≥90%

### T-022: End-to-end integration test (judge-llm → signal → refine --dry-run)
**User Story:** US-001, US-002 | **Status:** [x] completed
**Test Plan (BDD):**
- Given a fixture increment where judge-llm rejects with skill-attributable evidence
- When the full flow runs: increment → judge-llm emits → signal stored → `sw:skill-refine <skill> --dry-run` invoked
- Then the output shows an attributable diff referencing the original evidence

### T-023: Update specweave CHANGELOG.md
**User Story:** Docs | **Status:** [x] completed
**Test Plan (BDD):**
- Given the specweave package.json version
- When CHANGELOG.md is updated
- Then an entry exists under the next patch version describing sw:skill-refine + schema v2 + ADRs

### T-024: Update sw:reflect docs page
**User Story:** Docs | **Status:** [x] completed
**Test Plan (BDD):**
- Given docs/skills/reflect.md (or equivalent)
- When T-024 completes
- Then the page documents the new `--status` Refinement Suggestions section and the session-end nudge behavior

### T-025: Add sw:skill-refine docs page
**User Story:** Docs | **Status:** [x] completed
**Test Plan (BDD):**
- Given docs/skills/
- When T-025 completes
- Then `skill-refine.md` exists documenting flags, signal sources, attribution heuristics, and the four red-line ADRs

---

## Estimated effort

| Phase | Tasks | Effort (with 30% buffer) |
|-------|-------|--------------------------|
| 1 — Schema & signal emission | T-001..T-006 | 1.2 days |
| 2 — sw:skill-refine | T-007..T-012 | 1.5 days |
| 3 — Reflect nudge + dashboard | T-013..T-016 | 0.8 days |
| 4 — ADRs | T-017..T-020 | 0.5 days |
| 5 — Docs, tests, closure | T-021..T-025 | 1.0 days |
| **Total** | **25 tasks** | **~5 days** |

Pragmatist estimated 4 days; adding 25% buffer for ADR quality + integration test = 5 days.
