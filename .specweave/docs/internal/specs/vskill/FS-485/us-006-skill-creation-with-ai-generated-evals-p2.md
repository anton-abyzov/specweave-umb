---
id: US-006
feature: FS-485
title: Skill Creation with AI-Generated Evals (P2)
status: completed
priority: P1
created: 2026-03-11
tldr: "**As a** skill author."
project: vskill
external:
  github:
    issue: 89
    url: https://github.com/anton-abyzov/vskill/issues/89
---

# US-006: Skill Creation with AI-Generated Evals (P2)

**Feature**: [FS-485](./FEATURE.md)

**As a** skill author
**I want** the "Create Skill" action to persist both SKILL.md and the AI-generated evals
**So that** my new skill is immediately ready for benchmarking

---

## Acceptance Criteria

- [x] **AC-US6-01**: `POST /api/skills/create` accepts an optional `evals` array in the request body
- [x] **AC-US6-02**: When evals are provided, the backend writes `evals/evals.json` in the new skill directory
- [x] **AC-US6-03**: The evals JSON follows the standard `{ skill_name, evals: [...] }` schema
- [x] **AC-US6-04**: Plugin name is validated with regex to prevent path traversal

---

## Implementation

**Increment**: [0485-skill-studio-ai-create](../../../../../increments/0485-skill-studio-ai-create/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_
