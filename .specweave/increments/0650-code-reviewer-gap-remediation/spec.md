---
increment: 0650-code-reviewer-gap-remediation
title: Code Reviewer Gap Remediation
type: feature
priority: P1
status: completed
created: 2026-03-26T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Code Reviewer Gap Remediation

## Overview

Align SpecWeave's code-reviewer skill with Anthropic's official code-review and pr-review-toolkit plugin best practices. Addresses 6 gaps: finding validation via independent haiku agents, model tiering (opus for logic/security, sonnet for pattern-matching), gate checks to skip draft/closed/trivial PRs, false-positive suppression ("DO NOT FLAG" sections), two missing agent types (comment accuracy + test coverage analyzers), and PR intent context propagation.

All changes are markdown-only: the SKILL.md orchestrator and 8 agent templates (6 existing + 2 new).

## User Stories

### US-001: Finding Validation (P1)
**Project**: specweave

**As a** developer receiving code review results
**I want** each CRITICAL/HIGH finding independently validated by a separate haiku agent before it appears in the report
**So that** false positives are eliminated and I only act on verified findings

**Acceptance Criteria**:
- [x] **AC-US1-01**: SKILL.md defines a validation step between result aggregation and report generation that spawns one haiku-model validator per CRITICAL/HIGH finding
- [x] **AC-US1-02**: Each validator prompt includes the finding text, the relevant code snippet, and instructions to confirm/reject/downgrade the finding
- [x] **AC-US1-03**: Rejected findings are excluded from the final report; downgraded findings appear at the corrected severity

---

### US-002: Model Tiering (P1)
**Project**: specweave

**As a** team lead managing review costs
**I want** reviewer agents routed to appropriate model tiers based on their analysis complexity
**So that** opus is reserved for deep-reasoning tasks (logic, security) and sonnet handles pattern-matching (performance, silent failures, types, spec compliance, comments, tests)

**Acceptance Criteria**:
- [x] **AC-US2-01**: The reviewer routing table in SKILL.md assigns `opus` to reviewer-logic and reviewer-security
- [x] **AC-US2-02**: The reviewer routing table assigns `sonnet` to reviewer-performance, reviewer-silent-failures, reviewer-types, reviewer-spec-compliance, reviewer-comments, and reviewer-tests
- [x] **AC-US2-03**: A "Model tiering rationale" paragraph in SKILL.md explains why logic/security need opus and others use sonnet

---

### US-003: Gate Check (P2)
**Project**: specweave

**As a** developer who triggers code review on PRs
**I want** draft PRs, closed PRs, and trivial PRs (fewer than 5 changed lines) to be skipped before spawning expensive reviewer agents
**So that** review resources are not wasted on non-reviewable content

**Acceptance Criteria**:
- [x] **AC-US3-01**: SKILL.md defines a gate-check step between scope detection and reviewer routing
- [x] **AC-US3-02**: Gate check queries `gh pr view --json isDraft,state,additions,deletions` and skips review with a user-facing message for draft, closed, or <5 total changed lines
- [x] **AC-US3-03**: A `--force` flag is documented to bypass the gate check

---

### US-004: False-Positive Suppression (P2)
**Project**: specweave

**As a** developer receiving code review feedback
**I want** each reviewer agent to have explicit "DO NOT FLAG" instructions for common false-positive patterns
**So that** review noise is reduced and only actionable findings are reported

**Acceptance Criteria**:
- [x] **AC-US4-01**: All 6 existing agent templates contain a "DO NOT FLAG" section listing 3-5 patterns to suppress
- [x] **AC-US4-02**: The 2 new agent templates (reviewer-comments, reviewer-tests) also contain "DO NOT FLAG" sections
- [x] **AC-US4-03**: DO NOT FLAG items are domain-specific (e.g., security reviewer suppresses intentional password hashing timing, logic reviewer suppresses intentional fallthrough in switch)

---

### US-005: Missing Agent Types (P2)
**Project**: specweave

**As a** developer using SpecWeave code review
**I want** comment accuracy and test coverage analyzer agents available
**So that** reviews catch misleading comments/docstrings and gaps in test coverage

**Acceptance Criteria**:
- [x] **AC-US5-01**: `agents/reviewer-comments.md` exists with a mission to find stale comments, misleading docstrings, TODO/FIXME debt, and comment-code contradictions
- [x] **AC-US5-02**: `agents/reviewer-tests.md` exists with a mission to find missing test coverage for changed code, weak assertions, and test-production drift
- [x] **AC-US5-03**: SKILL.md routing table includes both new reviewers with routing rules (comments: any code files; tests: when test files or testable source present)
- [x] **AC-US5-04**: Both new templates follow the same output format, communication protocol, and rules as existing reviewer agents

---

### US-006: PR Intent Context (P3)
**Project**: specweave

**As a** reviewer agent analyzing PR changes
**I want** the PR title and description passed to me as context
**So that** I can assess findings relative to the stated intent and avoid flagging known trade-offs

**Acceptance Criteria**:
- [x] **AC-US6-01**: SKILL.md instructs the orchestrator to fetch PR title and description via `gh pr view --json title,body` when scope is `pr`
- [x] **AC-US6-02**: All 8 agent templates include a `PR CONTEXT:` placeholder that receives the PR title and description
- [x] **AC-US6-03**: Each agent's instructions reference the PR context to calibrate severity (e.g., "if the PR description acknowledges a limitation, downgrade related findings to INFO")

## Out of Scope

- TypeScript code changes (all work is markdown templates)
- Changes to the closure pipeline or grill skill
- Changes to the report JSON schema
- New CLI flags beyond documenting `--force`
- Model selection logic in the TS runtime (model hints are advisory in templates)

## Dependencies

- Existing code-reviewer SKILL.md orchestrator
- Existing 6 agent templates (3 in team-lead, 3 in code-reviewer)
- Claude Code agent spawning system (Task, TeamCreate, SendMessage)
