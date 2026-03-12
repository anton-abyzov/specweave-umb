---
id: US-004
feature: FS-517
title: "Team-Lead Testing Agent Integration (P1)"
status: completed
priority: P1
created: 2026-03-12T00:00:00.000Z
tldr: "**As a** team-lead testing agent."
project: specweave
---

# US-004: Team-Lead Testing Agent Integration (P1)

**Feature**: [FS-517](./FEATURE.md)

**As a** team-lead testing agent
**I want** to invoke `sw:e2e` to handle E2E test suites
**So that** E2E testing integrates into parallel team development without requiring a nonexistent `testing:e2e` plugin

---

## Acceptance Criteria

- [x] **AC-US4-01**: Given the team-lead testing agent invokes `Skill({ skill: "sw:e2e", args: "--generate <increment-id>" })`, when the skill loads, then it reads the master spec from the increment path and generates tests
- [x] **AC-US4-02**: Given the team-lead testing agent invokes `Skill({ skill: "sw:e2e", args: "--run <increment-id>" })`, when tests complete, then `e2e-report.json` is written and the skill outputs a summary of pass/fail counts
- [x] **AC-US4-03**: Given sw:done invokes `Skill({ skill: "sw:e2e", args: "--run <increment-id>" })` during Gate 2a, when the skill completes, then Gate 2a reads `e2e-report.json` from the increment's `reports/` subfolder for pass/fail determination
- [x] **AC-US4-04**: Given the SKILL.md is placed at `plugins/specweave/skills/e2e/SKILL.md`, when any agent invokes `sw:e2e`, then the skill activates with correct frontmatter (description, argument-hint, allowed-tools, context, model)
- [x] **AC-US4-05**: Given an `evals.json` exists at `plugins/specweave/skills/e2e/evals/evals.json`, when skill quality is evaluated, then 3-4 eval scenarios validate generate, run, and a11y modes

---

## Implementation

**Increment**: [0517-sw-e2e-skill](../../../../../increments/0517-sw-e2e-skill/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-003**: Write evals/evals.json
- [x] **T-004**: Fix testing.md references (testing:e2e -> sw:e2e)
- [x] **T-005**: Clean ghost testing plugin cache and refresh plugins
