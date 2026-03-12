---
id: US-001
feature: FS-485
title: AI-Assisted Skill Generation (P1)
status: completed
priority: P1
created: 2026-03-11T00:00:00.000Z
tldr: "**As a** skill author."
project: vskill
external:
  github:
    issue: 82
    url: https://github.com/anton-abyzov/vskill/issues/82
---

# US-001: AI-Assisted Skill Generation (P1)

**Feature**: [FS-485](./FEATURE.md)

**As a** skill author
**I want** to describe what my skill should do in natural language and have AI generate the full SKILL.md content
**So that** I can create production-quality skills without memorizing Skill Studio best practices

---

## Acceptance Criteria

- [x] **AC-US1-01**: The Create Skill page displays a Manual / AI-Assisted mode toggle in the header
- [x] **AC-US1-02**: Selecting AI-Assisted mode shows a prompt textarea, provider/model selectors, and a "Generate Skill" button
- [x] **AC-US1-03**: Submitting a prompt calls `POST /api/skills/generate?sse` with `{ prompt, provider, model }`
- [x] **AC-US1-04**: The backend sends SSE progress events (`preparing`, `generating`, `parsing`) so the user sees real-time feedback
- [x] **AC-US1-05**: On successful generation, the AI output (name, description, model, allowedTools, body, evals, reasoning) populates the manual form fields
- [x] **AC-US1-06**: After generation, mode switches to manual so the user can review and edit before creating
- [x] **AC-US1-07**: An AI-generated reasoning banner appears above the manual form after generation
- [x] **AC-US1-08**: The user can dismiss the reasoning banner and pending evals independently

---

## Implementation

**Increment**: [0485-skill-studio-ai-create](../../../../../increments/0485-skill-studio-ai-create/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_
