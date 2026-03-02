---
id: US-002
feature: FS-399
title: "Token Isolation for Non-Interactive Skills"
status: completed
priority: P1
created: 2026-03-02
tldr: "**As a** user running `/sw:increment`, **I want** architect and test-aware-planner to run in isolated context, **so that** skill instructions don't consume main conversation tokens."
project: specweave
related_projects: [vskill]
---

# US-002: Token Isolation for Non-Interactive Skills

**Feature**: [FS-399](./FEATURE.md)

**As a** user running `/sw:increment`, **I want** architect and test-aware-planner to run in isolated context, **so that** skill instructions don't consume main conversation tokens.

---

## Acceptance Criteria

- [x] **AC-US2-01**: `architect/SKILL.md` has `context: fork` and `model: opus`
- [x] **AC-US2-02**: `test-aware-planner/SKILL.md` has `context: fork` and `model: opus`
- [x] **AC-US2-03**: `grill/SKILL.md` has `context: fork` and `model: opus`
- [x] **AC-US2-04**: `/sw:increment` produces equivalent quality output

---

## Implementation

**Increment**: [0399-skill-embedded-agents](../../../../../increments/0399-skill-embedded-agents/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-006**: Run tests and verify behavioral equivalence
