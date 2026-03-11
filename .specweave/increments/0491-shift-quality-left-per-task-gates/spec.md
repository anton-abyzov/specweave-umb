---
increment: 0491-shift-quality-left-per-task-gates
title: Shift Quality Left — Per-Task Gates
type: feature
priority: P1
status: completed
created: 2026-03-11T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Shift Quality Left -- Per-Task Gates

## Problem Statement

SpecWeave currently batches all quality review at increment closure (`sw:grill` + `sw:done`). By the time reviewers examine the work, multiple tasks may have drifted from the spec. Bugs compound, and fixing late-discovered issues requires revisiting decisions made 10+ tasks ago. The obra/superpowers research (14 AI coding agent skills) proved that per-task spec-compliance and code-quality reviews catch drift early, reducing rework by surfacing misalignment after each task -- not at the end.

## Goals

- Move quality checks from end-of-increment to after-each-task
- Add adversarial spec compliance verification to the grill process
- Provide a systematic debugging skill to replace ad-hoc troubleshooting
- Enforce fresh verification evidence before marking tasks complete
- Embed anti-rationalization discipline into TDD and grill workflows
- Document all new capabilities in public docs and changelog

## User Stories

### US-001: Per-Task Review Gates in sw:do (P1)
**Project**: specweave

**As a** SpecWeave user executing tasks with sw:do
**I want** two lightweight review subagents (spec-compliance + code-quality) to run after each task completion
**So that** spec drift and code quality issues are caught immediately rather than accumulating until increment closure

**Acceptance Criteria**:
- [x] **AC-US1-01**: Given `quality.perTaskReview: true` in config.json, when sw:do completes a task (before marking [x]), then two subagent reviews run: (1) spec-compliance reviewer checking AC-by-AC alignment, (2) code-quality reviewer doing focused diff review
- [x] **AC-US1-02**: Given the spec-compliance reviewer finds a misalignment, when the review completes, then the implementer must fix the issue before proceeding to the next task
- [x] **AC-US1-03**: Given the code-quality reviewer finds issues, when the review completes, then the implementer must address findings before proceeding to the next task
- [x] **AC-US1-04**: Given `quality.perTaskReview` is absent or false in config.json, when sw:do runs, then per-task review gates are skipped entirely (backward compatible)
- [x] **AC-US1-05**: Given team-lead is active (detected via team-lead state), when sw:do runs, then per-task review gates are skipped (team-lead has its own review flow)

---

### US-002: Adversarial Spec Reviewer in sw:grill (P1)
**Project**: specweave

**As a** SpecWeave user running sw:grill before increment closure
**I want** a new Phase 0 (Spec Compliance Interrogation) that adversarially verifies every AC against the implementation
**So that** spec drift, missing features, and misinterpretations are caught with adversarial framing before the existing code review phases

**Acceptance Criteria**:
- [x] **AC-US2-01**: Given sw:grill is invoked, when Phase 0 runs, then it loads spec.md, extracts all ACs, and verifies implementation exists for each with adversarial framing ("prove this AC is satisfied")
- [x] **AC-US2-02**: Given Phase 0 completes, when it finds an AC not satisfied, then the finding includes: AC ID, expected behavior, actual behavior, and a pass/fail status
- [x] **AC-US2-03**: Given Phase 0 completes, when it finds functionality not traceable to any AC (scope creep), then it flags the extra functionality as a finding
- [x] **AC-US2-04**: Given Phase 0 runs, when grill-report.json is written, then it includes an `acCompliance` section with per-AC pass/fail results
- [x] **AC-US2-05**: Phase 0 always runs (not opt-in) and executes before existing Phase 1 (Context Gathering)

---

### US-003: Systematic Debugging Skill (P1)
**Project**: specweave

**As a** SpecWeave user encountering a difficult bug
**I want** a dedicated sw:debug skill with a 4-phase systematic debugging methodology
**So that** I follow a disciplined investigation process instead of ad-hoc trial-and-error

**Acceptance Criteria**:
- [x] **AC-US3-01**: Given a user invokes /sw:debug with a bug description, when Phase 1 (Root Cause Investigation) runs, then it systematically gathers evidence: error messages, stack traces, recent changes, and affected code paths
- [x] **AC-US3-02**: Given Phase 1 completes, when Phase 2 (Pattern Analysis) runs, then it identifies recurring patterns, similar past bugs, and potential root cause hypotheses
- [x] **AC-US3-03**: Given Phase 2 completes, when Phase 3 (Hypothesis Testing) runs, then it tests each hypothesis with minimal, targeted experiments and captures results
- [x] **AC-US3-04**: Given Phase 3 completes, when Phase 4 (Implementation) runs, then it implements the verified fix with tests proving the bug is resolved
- [x] **AC-US3-05**: Given 3 consecutive fix attempts fail, when the next attempt would start, then the skill stops and questions the architectural assumptions (escalation protocol)
- [x] **AC-US3-06**: The SKILL.md includes an anti-rationalization table with 8+ entries mapping common excuses to rebuttals (e.g., "quick fix for now" -> rebuttal)
- [x] **AC-US3-07**: The SKILL.md defines red flags that trigger escalation: "quick fix for now", "skip the test", "one more attempt", "it works on my machine"

---

### US-004: Fresh Verification Discipline in sw:do (P2)
**Project**: specweave

**As a** SpecWeave user completing tasks via sw:do
**I want** an iron law enforced: no task marked [x] without fresh verification evidence from running the task's test command
**So that** completion claims are always backed by proof, not assumptions

**Acceptance Criteria**:
- [x] **AC-US4-01**: Given a task has a `**Test**:` block with a Given/When/Then, when the task is about to be marked [x], then the test command must be run and output captured as evidence
- [x] **AC-US4-02**: Given a task has no `**Test**:` block, when the task is about to be marked [x], then the project-level test command is run as fallback verification
- [x] **AC-US4-03**: Given the verification command fails, when the implementer attempts to mark [x], then the task remains [ ] and the failure output is presented for fixing
- [x] **AC-US4-04**: The SKILL.md states the iron law explicitly: "NO COMPLETION CLAIMS WITHOUT FRESH VERIFICATION EVIDENCE"

---

### US-005: Anti-Rationalization Tables (P2)
**Project**: specweave

**As a** SpecWeave user following TDD or running grill reviews
**I want** explicit anti-rationalization tables with common excuses and rebuttals embedded in the skill instructions
**So that** AI agents resist the temptation to skip quality steps with plausible-sounding justifications

**Acceptance Criteria**:
- [x] **AC-US5-01**: Given sw:tdd-cycle SKILL.md is updated, when an agent reads it, then it contains an anti-rationalization table with 8+ entries (excuse -> rebuttal pairs)
- [x] **AC-US5-02**: The tdd-cycle table includes at minimum: "I'll test after" -> "Tests written after pass immediately, proving nothing", "This is too simple to test" -> rebuttal, "Just this once" -> rebuttal
- [x] **AC-US5-03**: Given sw:grill SKILL.md is updated, when an agent reads it, then it contains an anti-rationalization table with 6+ entries relevant to code review shortcuts
- [x] **AC-US5-04**: The grill table includes at minimum: "Close enough to the spec" -> "Close enough ships bugs", "We can fix it later" -> rebuttal, "The tests pass" -> rebuttal

---

### US-006: Public Docs and Changelog Updates (P2)
**Project**: specweave

**As a** SpecWeave user or evaluator reading public documentation
**I want** the skills reference, tutorial script, and changelog updated to reflect all new quality-left capabilities
**So that** new features are discoverable and documented

**Acceptance Criteria**:
- [x] **AC-US6-01**: Given docs-site/docs/reference/skills.md is updated, when a user reads the Quality & Testing section, then sw:debug appears with description and usage guidance
- [x] **AC-US6-02**: Given docs-site/docs/guides/youtube-tutorial-script.md is updated, when a user reads it, then a section on quality-left features (per-task gates, adversarial grill, debug skill) is present
- [x] **AC-US6-03**: Given CHANGELOG.md is updated, when a user reads it, then all 5 features from this increment are documented with version reference

## Out of Scope

- Runtime code changes (TypeScript/JavaScript) -- all changes are SKILL.md markdown and docs
- New CLI commands or hooks -- this uses existing skill infrastructure
- Changes to the completion-validator or hook guards
- Per-task review in team-lead mode (team-lead has its own review flow)
- Automated test infrastructure for the skill changes (skills are tested via grill + manual validation)

## Technical Notes

- All target files are in `repositories/anton-abyzov/specweave/`
- Skills are SKILL.md markdown files that AI agents parse at runtime -- no compilation needed
- Config flag `quality.perTaskReview` follows existing config patterns in `.specweave/config.json`
- The new sw:debug skill needs a new directory: `plugins/specweave/skills/debug/SKILL.md`
- Grill Phase 0 must prepend to existing phases without renumbering (existing Phase 1-3 become Phase 1-3 still, new phase is "Phase 0")
- Anti-rationalization tables are inline markdown tables within SKILL.md files

## Success Metrics

- Per-task review gates catch spec drift during implementation (measured via grill-report finding reduction at closure)
- sw:debug skill provides structured debugging path instead of ad-hoc fixes
- Zero backward compatibility breaks -- existing workflows unchanged when config flags are absent
- All changes pass sw:grill and sw:validate quality gates
