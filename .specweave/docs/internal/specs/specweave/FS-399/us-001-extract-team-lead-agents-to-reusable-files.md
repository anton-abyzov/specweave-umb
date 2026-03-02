---
id: US-001
feature: FS-399
title: "Extract Team-Lead Agents to Reusable Files"
status: completed
priority: P1
created: 2026-03-02
tldr: "**As a** skill author, **I want** domain agent definitions as `agents/*.md` files inside team-lead skill, **so that** agent prompts are maintainable, inspectable, and distributable via vskill."
project: specweave
related_projects: [vskill]
---

# US-001: Extract Team-Lead Agents to Reusable Files

**Feature**: [FS-399](./FEATURE.md)

**As a** skill author, **I want** domain agent definitions as `agents/*.md` files inside team-lead skill, **so that** agent prompts are maintainable, inspectable, and distributable via vskill.

---

## Acceptance Criteria

- [x] **AC-US1-01**: 5 agent .md files in `plugins/specweave/skills/team-lead/agents/`
- [x] **AC-US1-02**: team-lead SKILL.md Section 4 replaced with reference table + "Read agents/{name}.md"
- [x] **AC-US1-03**: team-lead SKILL.md reduced by ~250 lines (927→653)
- [x] **AC-US1-04**: spawned agents receive identical prompt content (behavioral equivalence)

---

## Implementation

**Increment**: [0399-skill-embedded-agents](../../../../../increments/0399-skill-embedded-agents/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-006**: Run tests and verify behavioral equivalence
