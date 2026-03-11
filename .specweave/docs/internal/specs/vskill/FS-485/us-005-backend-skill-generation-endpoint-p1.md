---
id: US-005
feature: FS-485
title: Backend Skill Generation Endpoint (P1)
status: completed
priority: P1
created: 2026-03-11
tldr: "**As a** Skill Studio backend."
project: vskill
external:
  github:
    issue: 88
    url: https://github.com/anton-abyzov/vskill/issues/88
---

# US-005: Backend Skill Generation Endpoint (P1)

**Feature**: [FS-485](./FEATURE.md)

**As a** Skill Studio backend
**I want** a `POST /api/skills/generate` endpoint that calls an LLM with Skill Studio best-practice instructions
**So that** the frontend can offer AI-assisted skill creation

---

## Acceptance Criteria

- [x] **AC-US5-01**: The endpoint accepts `{ prompt, provider?, model? }` and returns a `GenerateSkillResult`
- [x] **AC-US5-02**: The system prompt encodes Skill Studio best practices: trigger description quality, imperative writing style, progressive disclosure, structured sections, eval generation rules
- [x] **AC-US5-03**: The LLM is asked to return JSON followed by `---REASONING---` separator
- [x] **AC-US5-04**: `parseGenerateResponse` extracts and sanitizes the JSON, strips code fences, and separates reasoning
- [x] **AC-US5-05**: Invalid skill names after sanitization throw a descriptive error
- [x] **AC-US5-06**: The endpoint supports both SSE mode (`?sse` query param or `Accept: text/event-stream`) and plain JSON mode
- [x] **AC-US5-07**: SSE mode sends heartbeat events every 3 seconds during long LLM calls via `withHeartbeat`

---

## Implementation

**Increment**: [0485-skill-studio-ai-create](../../../../../increments/0485-skill-studio-ai-create/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_
