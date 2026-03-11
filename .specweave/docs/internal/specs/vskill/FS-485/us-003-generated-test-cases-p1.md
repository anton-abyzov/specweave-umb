---
id: US-003
feature: FS-485
title: Generated Test Cases (P1)
status: completed
priority: P1
created: 2026-03-11
tldr: "**As a** skill author."
project: vskill
external:
  github:
    issue: 86
    url: https://github.com/anton-abyzov/vskill/issues/86
---

# US-003: Generated Test Cases (P1)

**Feature**: [FS-485](./FEATURE.md)

**As a** skill author
**I want** the AI to generate starter eval test cases alongside the SKILL.md
**So that** I can immediately benchmark the new skill without writing evals from scratch

---

## Acceptance Criteria

- [x] **AC-US3-01**: The AI generation prompt instructs the LLM to produce 2-3 eval test cases with assertions
- [x] **AC-US3-02**: Generated evals are displayed as a card list in the manual form under "Generated Test Cases"
- [x] **AC-US3-03**: Each eval card shows name, truncated prompt, and assertion badges
- [x] **AC-US3-04**: When the skill is created with pending evals, the backend writes `evals/evals.json` alongside SKILL.md
- [x] **AC-US3-05**: Generated evals are capped at 10 to prevent LLM overgeneration

---

## Implementation

**Increment**: [0485-skill-studio-ai-create](../../../../../increments/0485-skill-studio-ai-create/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_
