---
id: US-005
feature: FS-519
title: "sw:add Skill Definition"
status: completed
priority: P1
created: 2026-03-13T00:00:00.000Z
tldr: "**As a** developer using Claude Code."
project: specweave
---

# US-005: sw:add Skill Definition

**Feature**: [FS-519](./FEATURE.md)

**As a** developer using Claude Code
**I want** an `sw:get` skill that activates on natural language triggers for adding repos
**So that** I can say "add repo" or "clone repo" instead of remembering the CLI syntax

---

## Acceptance Criteria

- [x] **AC-US5-01**: Given the skill SKILL.md exists at `plugins/specweave/skills/get/SKILL.md`, when a user says "add repo owner/name", then the skill activates and delegates to `specweave get`
- [x] **AC-US5-02**: Given a user says "add a feature" or "add a task", when intent detection runs, then the `sw:get` skill does NOT activate (those route to `sw:increment`)
- [x] **AC-US5-03**: Given the SKILL.md `description` field, when parsed, then it contains trigger phrases: "add repo", "clone repo", "add github repo to umbrella", "register this repo"

---

## Implementation

**Increment**: [0519-specweave-add-command](../../../../../increments/0519-specweave-add-command/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_
