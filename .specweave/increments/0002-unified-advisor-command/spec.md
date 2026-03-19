---
increment: 0002-unified-advisor-command
title: "Unified Help Command"
type: feature
priority: P1
status: planned
created: 2026-03-19
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Unified Help Command

## Problem Statement

SpecWeave has 6+ diagnostic commands (doctor, discrepancies, docs-health, qa, progress, next) that each answer a piece of the "what should I do now?" question. Users — especially those onboarding brownfield projects — must run multiple commands, mentally merge the output, and decide what matters most. There is no single entry point that synthesizes all signals into a prioritized action list.

## Goals

- Provide a single `/sw:help` skill and `specweave guide` CLI command that tells users exactly what to do next, ranked by priority
- Auto-detect project phase (fresh-init, brownfield-early, active-dev, mature) and adapt recommendations accordingly
- Compose existing core functions in parallel — no logic duplication
- Stay fast by default (< 3 seconds without `--deep`) by skipping LLM-based checks
- Give brownfield projects a clear onboarding path after `specweave init`

## CLI Naming

Commander.js reserves `help` as a built-in command. The CLI command MUST be `specweave guide` to avoid conflicts. The AI skill remains `/sw:help` since skill names do not conflict with Commander internals.

## User Stories

### US-001: Phase Detection Engine (P1)
**Project**: specweave

**As a** SpecWeave user
**I want** the help command to auto-detect my project's maturity phase
**So that** the recommendations I receive are relevant to where my project actually is

**Acceptance Criteria**:
- [ ] **AC-US1-01**: Given a project where `specweave init` was just run (0 increments, no living docs), when `specweave guide` runs, then the detected phase is `fresh-init`
- [ ] **AC-US1-02**: Given a project with existing source code but fewer than 3 completed increments and living-docs coverage below 30%, when `specweave guide` runs, then the detected phase is `brownfield-early`
- [ ] **AC-US1-03**: Given a project with 1+ active increments and at least 3 total increments, when `specweave guide` runs, then the detected phase is `active-dev`
- [ ] **AC-US1-04**: Given a project with 10+ completed increments and living-docs coverage above 60%, when `specweave guide` runs, then the detected phase is `mature`
- [ ] **AC-US1-05**: Given any project state, when the phase detector runs, then it completes in under 500ms (no LLM calls, no network I/O)

---

### US-002: Signal Collection via Composition (P1)
**Project**: specweave

**As a** SpecWeave maintainer
**I want** the help command to call existing core functions (runDoctor, discrepancy detector, progress tracker) rather than reimplementing their logic
**So that** diagnostic logic stays DRY and improvements to individual checkers automatically flow through to help output

**Acceptance Criteria**:
- [ ] **AC-US2-01**: Given the help command runs in default mode, when signal collection begins, then `runDoctor()` is called with `{ quick: true }` to get environment/structure health
- [ ] **AC-US2-02**: Given the help command runs in default mode, when signal collection begins, then `BrownfieldDiscrepancyManager.getIndex()` is called to get discrepancy counts by priority
- [ ] **AC-US2-03**: Given the help command runs in default mode, when signal collection begins, then `calculateProgressFromTasksFile()` is called for each active increment to get task completion status
- [ ] **AC-US2-04**: Given the help command runs in default mode, when signal collection begins, then the doctor, discrepancy, and progress collectors all run in parallel (Promise.all) not sequentially
- [ ] **AC-US2-05**: Given any individual signal collector throws an error, when the help command runs, then the error is caught and that signal is marked as `unavailable` in the output without crashing the entire command
- [ ] **AC-US2-06**: Given the help command runs with `--deep` flag, when signal collection begins, then `runQA()` is additionally called for active increments with `{ quick: true }` mode

---

### US-003: Prioritized Action Ranking (P1)
**Project**: specweave

**As a** SpecWeave user
**I want** a ranked list of 3-5 top actions based on all collected signals
**So that** I know exactly what to do next without parsing raw diagnostic output

**Acceptance Criteria**:
- [ ] **AC-US3-01**: Given signals are collected, when actions are ranked, then doctor failures (status=fail) are ranked highest (critical severity)
- [ ] **AC-US3-02**: Given signals are collected, when actions are ranked, then high-priority discrepancies are ranked above warnings and info items
- [ ] **AC-US3-03**: Given signals are collected, when actions are ranked, then near-complete increments (>= 80% done) are surfaced with a "finish it" action
- [ ] **AC-US3-04**: Given signals are collected, when actions are ranked, then the output contains at most 5 actions by default
- [ ] **AC-US3-05**: Given a fresh-init project with zero issues, when actions are ranked, then the output shows onboarding actions: "Create your first increment", "Set up external sync", "Run living-docs builder"
- [ ] **AC-US3-06**: Given each action in the ranked list, when the action renders, then it includes a severity indicator, a human-readable description, and a concrete `Run:` command the user can copy-paste

---

### US-004: CLI Command (`specweave guide`) (P1)
**Project**: specweave

**As a** developer working in the terminal
**I want** to run `specweave guide` and see a formatted summary of my project state and top actions
**So that** I can quickly orient myself without opening an AI chat session

**Acceptance Criteria**:
- [ ] **AC-US4-01**: Given the user runs `specweave guide`, when the command completes, then the output shows a header with the project name, detected phase, and a one-line phase description
- [ ] **AC-US4-02**: Given the user runs `specweave guide`, when the command completes, then the output shows the ranked action list with severity icons, descriptions, and `Run:` commands
- [ ] **AC-US4-03**: Given the user runs `specweave guide`, when the command completes, then a footer shows summary stats: health percentage, active increment count, and discrepancy count
- [ ] **AC-US4-04**: Given the user runs `specweave guide --json`, when the command completes, then the output is valid JSON containing `phase`, `actions[]`, and `summary` fields
- [ ] **AC-US4-05**: Given the user runs `specweave guide --verbose`, when the command completes, then each action includes additional context (which specific checks failed, which specific increments are near-complete)
- [ ] **AC-US4-06**: Given the user runs `specweave guide --deep`, when the command completes, then QA signals are included in signal collection and action ranking
- [ ] **AC-US4-07**: Given the user runs `specweave guide` in a directory without `.specweave/`, when the command runs, then it prints a clear error: "Not a SpecWeave project. Run: specweave init" and exits with code 1

---

### US-005: Skill Interface (`/sw:help`) (P2)
**Project**: specweave

**As an** AI agent or developer using Claude Code
**I want** to invoke `/sw:help` and receive structured guidance on what to do next
**So that** agent workflows and human conversations both benefit from the same advisory logic

**Acceptance Criteria**:
- [ ] **AC-US5-01**: Given the `/sw:help` skill is invoked, when the skill executes, then it calls the same core `runGuide()` function that the CLI uses
- [ ] **AC-US5-02**: Given the `/sw:help` skill is invoked, when the result is returned, then it is formatted as markdown suitable for AI agent context (not terminal ANSI codes)
- [ ] **AC-US5-03**: Given the `/sw:help` skill is invoked with a `--deep` argument, when the skill executes, then QA signals are included

---

### US-006: Adaptive Phase Guidance (P2)
**Project**: specweave

**As a** user at any project stage
**I want** the recommendations to change based on my detected project phase
**So that** I always get contextually relevant guidance rather than generic advice

**Acceptance Criteria**:
- [ ] **AC-US6-01**: Given phase is `fresh-init`, when no issues are detected, then recommended actions include: "Create your first increment", "Connect GitHub/JIRA sync", "Run living-docs builder"
- [ ] **AC-US6-02**: Given phase is `brownfield-early`, when discrepancies exist, then recommended actions prioritize: "Run discrepancy scan", "Document undocumented modules", "Create baseline specs for existing code"
- [ ] **AC-US6-03**: Given phase is `active-dev`, when active increments exist, then recommended actions prioritize: "Complete active tasks", "Fix failing doctor checks", "Update stale documentation"
- [ ] **AC-US6-04**: Given phase is `mature`, when the project is healthy, then recommended actions include: "Review docs-health score", "Check for stale increments", "Audit dependency versions"

## Functional Requirements

### FR-001: Core `runGuide()` Function
The core logic lives in `src/core/guide/guide-runner.ts` and exports `runGuide(projectRoot: string, options: GuideOptions): Promise<GuideReport>`. Both the CLI command and the skill call this function. It orchestrates:
1. Phase detection (sync, no I/O beyond filesystem)
2. Parallel signal collection (doctor, discrepancies, progress; optionally QA with `--deep`)
3. Action ranking and filtering
4. Report assembly

### FR-002: Phase Detection Heuristics
Phase detection uses only local filesystem state (config.json, increment directories, living-docs). Deterministic priority order ensures exactly one phase is selected:
1. `fresh-init`: 0 increments total, no `docs/internal/specs/` content
2. `brownfield-early`: has source code directories, < 3 completed increments OR living-docs coverage < 30%
3. `active-dev`: >= 1 active increment AND >= 3 total increments
4. `mature`: >= 10 completed increments AND living-docs coverage >= 60%

### FR-003: Action Severity Levels
Actions are classified into three severity levels for display:
- **critical** (red): Doctor failures, broken config, missing required files
- **warning** (yellow): Discrepancies, stale docs, incomplete increments
- **info** (green): Suggestions, optimizations, near-complete work to finish

### FR-004: Graceful Degradation
If any signal collector fails (e.g., corrupt config.json prevents doctor from running), the help command still produces output from the remaining signals. Failed collectors appear as a warning action: "Doctor check unavailable — run `specweave doctor` directly to diagnose".

## Success Criteria

- Users can run a single command (`specweave guide` or `/sw:help`) to get actionable next steps
- Default execution completes in under 3 seconds (no `--deep`)
- New users after `specweave init` see onboarding-specific guidance
- Brownfield users see discrepancy-focused guidance
- Zero duplicated diagnostic logic — all signals come from existing core functions

## Out of Scope

- Interactive/wizard mode (future increment)
- Dashboard widget integration (future increment)
- Auto-fix capabilities (doctor already has `--fix`; help only recommends)
- Custom action plugins/extensions
- Telemetry or analytics on which actions users follow

## Dependencies

- `src/core/doctor/doctor.ts` — `runDoctor()` for environment health
- `src/core/discrepancy/` — `BrownfieldDiscrepancyManager` for code-spec gaps
- `src/progress/us-progress-tracker.ts` — `calculateProgressFromTasksFile()` for increment progress
- `src/core/qa/qa-runner.ts` — `runQA()` for deep mode only
- `src/cli/commands/health.ts` — `runHealthCheck()` for sync connectivity (optional signal)
