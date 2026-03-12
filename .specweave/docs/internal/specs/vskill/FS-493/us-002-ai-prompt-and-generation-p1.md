---
id: US-002
feature: FS-493
title: "AI Prompt and Generation (P1)"
status: completed
priority: P1
created: "2026-03-11T00:00:00.000Z"
tldr: "**As a** skill author in AI mode."
project: vskill
---

# US-002: AI Prompt and Generation (P1)

**Feature**: [FS-493](./FEATURE.md)

**As a** skill author in AI mode
**I want** a textarea to describe my skill and a "Generate with AI" button
**So that** I can generate a complete skill definition from a natural language description

---

## Acceptance Criteria

- [x] **AC-US2-01**: Given AI mode is active, when the section renders, then a textarea with placeholder guidance and a "Generate Skill" button are displayed
- [x] **AC-US2-02**: Given the prompt textarea is empty, when the user looks at the generate button, then it is visually disabled (grayed out, not-allowed cursor)
- [x] **AC-US2-03**: Given a non-empty prompt, when the user clicks "Generate Skill", then the existing `POST /api/skills/generate?sse` endpoint is called with the prompt via SSE streaming
- [x] **AC-US2-04**: Given AI generation completes successfully, when the response arrives via SSE "done" event, then all form fields (name, description, model, allowedTools, body) are populated from the response and the view switches to manual mode for review
- [x] **AC-US2-05**: Given AI generation returns evals, when switching to manual mode, then pending evals are stored and included in the subsequent create request

---

## Implementation

**Increment**: [0493-ai-assisted-skill-authoring](../../../../../increments/0493-ai-assisted-skill-authoring/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-004**: Write failing tests for AI prompt section and SSE generation
- [x] **T-005**: Implement AI prompt section JSX and handleGenerate
- [x] **T-006**: Modify handleCreate to pass pendingEvals
