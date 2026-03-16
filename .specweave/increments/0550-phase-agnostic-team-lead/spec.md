---
increment: 0550-phase-agnostic-team-lead
title: "Phase-Agnostic Team Lead and Standalone Code Reviewer"
status: active
priority: P1
type: feature
created: 2026-03-16
---

# Phase-Agnostic Team Lead and Standalone Code Reviewer

## Problem Statement

The team-lead skill currently operates primarily as an implementation orchestrator. When users invoke it for planning, research, testing, or review, it either falls back to implementation mode or requires workarounds. Additionally, code review capabilities are embedded inside team-lead rather than being a first-class standalone skill, limiting reuse and discoverability.

## Goals

- Make team-lead detect user intent and route to the correct orchestration mode (brainstorm, plan, implement, review, research, test)
- Extract code review into a standalone /sw:code-reviewer skill with specialized parallel reviewer agents
- Provide dedicated agent templates for planning mode (PM + Architect in parallel)
- Support cross-repo review in umbrella projects
- Update the increment-existence-guard to recognize research-* and plan-* team name prefixes as non-implementation modes

## User Stories

### US-001: Mode Detection in Team Lead
**Project**: specweave
**As a** developer
**I want** team-lead to detect my intent (brainstorm, plan, implement, review, research, test) and use the appropriate orchestration mode
**So that** I get the right agent composition without manually specifying modes

**Acceptance Criteria**:
- [ ] **AC-US1-01**: Given a user invokes team-lead with "plan the checkout feature", when SKILL.md processes the request, then it detects plan mode and spawns PM + Architect agents instead of domain implementation agents
- [ ] **AC-US1-02**: Given a user invokes team-lead with "research how auth works in this codebase", when SKILL.md processes the request, then it detects research mode and spawns researcher agents without requiring an increment
- [ ] **AC-US1-03**: Given a user invokes team-lead with "test the payment flow", when SKILL.md processes the request, then it detects test mode and spawns testing-focused agents
- [ ] **AC-US1-04**: Given a user invokes team-lead without clear intent signals, when SKILL.md processes the request, then it defaults to implement mode (preserving backward compatibility)
- [ ] **AC-US1-05**: Given SKILL.md contains a mode detection section, when a developer reads it, then each mode lists its trigger keywords, required agent templates, and whether an increment is required

### US-002: Standalone Code Reviewer Skill
**Project**: specweave
**As a** developer
**I want** a standalone /sw:code-reviewer skill that spawns parallel specialized reviewers
**So that** I can invoke code review independently of team-lead with purpose-built reviewer agents

**Acceptance Criteria**:
- [ ] **AC-US2-01**: Given the code-reviewer skill directory exists at plugins/specweave/skills/code-reviewer/, when SKILL.md is created, then it contains frontmatter with description, hooks, and usage instructions
- [ ] **AC-US2-02**: Given the code-reviewer agents/ directory, when reviewer templates are created, then it contains reviewer-silent-failures.md, reviewer-types.md, and reviewer-spec-compliance.md
- [ ] **AC-US2-03**: Given a developer invokes /sw:code-reviewer, when the skill activates, then it spawns all three reviewer agents in parallel using TeamCreate + Task
- [ ] **AC-US2-04**: Given PLUGIN.md already has a code-reviewer entry at line 82, when SKILL.md is created, then the skill is fully functional without additional PLUGIN.md changes

### US-003: Planning Mode Agent Composition
**Project**: specweave
**As a** developer
**I want** team-lead planning mode to run PM and Architect agents in parallel
**So that** spec creation and technical design happen concurrently for faster planning cycles

**Acceptance Criteria**:
- [ ] **AC-US3-01**: Given team-lead detects plan mode, when it spawns agents, then it creates a PM agent using the existing agents/pm.md template and an Architect agent using the existing agents/architect.md template
- [ ] **AC-US3-02**: Given plan mode is active, when agents are spawned, then PM and Architect agents run in parallel (not sequentially)
- [ ] **AC-US3-03**: Given plan mode is active, when team-lead creates the team, then the team name uses the plan-* prefix (e.g., plan-checkout-feature)

### US-004: Cross-Repo Code Review
**Project**: specweave
**As a** developer
**I want** code review to work across multiple repos in an umbrella project
**So that** reviewers can detect issues spanning repo boundaries (e.g., API contract mismatches)

**Acceptance Criteria**:
- [ ] **AC-US4-01**: Given an umbrella project with repositories/*/* structure, when /sw:code-reviewer is invoked, then reviewer agents receive the list of child repo paths in their prompts
- [ ] **AC-US4-02**: Given a reviewer agent in an umbrella project, when it detects a cross-repo concern (e.g., frontend calling a backend API that changed), then it flags it in its review output
- [ ] **AC-US4-03**: Given the code-reviewer SKILL.md, when it contains umbrella detection logic, then it scans for repositories/*/* directories and passes them to agent prompts

## Out of Scope

- TypeScript/runtime code changes (this increment is markdown and shell only)
- Modifying the existing reviewer-logic.md, reviewer-performance.md, reviewer-security.md templates in team-lead (those remain as-is)
- Adding new CLI commands or flags
- Changing the team-lead's implementation mode behavior
- UI or dashboard changes

## Non-Functional Requirements

- **Compatibility**: All changes are markdown (.md) and shell (.sh) files -- no build step required
- **Backward Compatibility**: Existing team-lead implementation mode must work identically after changes
- **File Size**: SKILL.md files must stay under 1500 lines per the project limit

## Edge Cases

- Mode detection ambiguity: If intent is unclear, default to implement mode (AC-US1-04)
- Guard script prefix overlap: research-* must not conflict with existing analysis-* prefix handling
- Empty umbrella: If repositories/ directory exists but has no child repos, code-reviewer falls back to single-repo mode

## Risks

| Risk | Probability | Impact | Severity | Mitigation |
|------|-------------|--------|----------|------------|
| Mode detection misclassifies intent | 0.3 | 4 | 1.2 | Default to implement mode; provide --mode override flag |
| SKILL.md exceeds 1500-line limit after mode additions | 0.2 | 5 | 1.0 | Use progressive disclosure sections; keep modes concise |
| Guard script changes break existing team creation | 0.1 | 8 | 0.8 | Only add new prefixes to existing case statement; test existing prefixes still work |

## Technical Notes

- All target files live under: `repositories/anton-abyzov/specweave/plugins/specweave/`
- Agent templates pm.md, architect.md, and researcher.md already exist in team-lead/agents/ -- this increment updates SKILL.md to reference them in mode definitions, not create them
- code-reviewer skill directory and agents/ subdirectory already exist but are empty (no SKILL.md, no agent templates)
- PLUGIN.md already has code-reviewer registered at line 82 -- only verify, do not duplicate
- increment-existence-guard.sh case statement at line 62 needs research-* and plan-* added to the pipe-delimited pattern, plus test-* for completeness

## Success Metrics

- Team-lead correctly routes to plan mode when given planning-related prompts
- /sw:code-reviewer can be invoked standalone and spawns 3 parallel reviewer agents
- increment-existence-guard allows research-* and plan-* prefixed teams without blocking
