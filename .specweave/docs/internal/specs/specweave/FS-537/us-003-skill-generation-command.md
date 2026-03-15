---
id: US-003
feature: FS-537
title: Skill Generation Command
status: not_started
priority: P1
created: 2026-03-15
tldr: "**As a** SpecWeave user."
project: specweave
external_tools:
  jira:
    key: SWE2E-272
  ado:
    id: 209
---

# US-003: Skill Generation Command

**Feature**: [FS-537](./FEATURE.md)

**As a** SpecWeave user
**I want** an on-demand `/sw:skill-gen` skill that generates project-local SKILL.md files
**So that** I can codify detected patterns into permanent AI coding instructions

---

## Acceptance Criteria

- [ ] **AC-US3-01**: Given the user invokes `/sw:skill-gen`, when signals exist in `skill-signals.json`, then all signals with `incrementIds.length >= minSignalCount` are displayed regardless of `declined` status
- [ ] **AC-US3-02**: Given the user selects a pattern via natural language response, when generation starts, then the skill invokes the Anthropic skill-creator plugin at `~/.claude/plugins/cache/claude-plugins-official/skill-creator/` to build the SKILL.md with evals, benchmarks, and description optimization
- [ ] **AC-US3-03**: Given skill generation completes, when the SKILL.md is written, then it is placed in `.claude/skills/` (project-local directory)
- [ ] **AC-US3-04**: Given a skill is successfully generated, when the signal is updated, then `generated` is set to `true` on that signal entry
- [ ] **AC-US3-05**: Given no signals meet the minimum count threshold, when `/sw:skill-gen` is invoked, then a message indicates no qualifying patterns were found

---

## Implementation

**Increment**: [0537-project-skill-gen-docs](../../../../../increments/0537-project-skill-gen-docs/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_
