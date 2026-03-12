---
id: US-002
feature: FS-485
title: "Provider and Model Selection for Generation (P1)"
status: completed
priority: P1
created: 2026-03-11T00:00:00.000Z
tldr: "**As a** skill author."
project: vskill
external:
  github:
    issue: 84
    url: https://github.com/anton-abyzov/vskill/issues/84
---

# US-002: Provider and Model Selection for Generation (P1)

**Feature**: [FS-485](./FEATURE.md)

**As a** skill author
**I want** to choose which AI provider and model generates my skill
**So that** I can use whichever provider is available and pick the right quality/speed tradeoff

---

## Acceptance Criteria

- [x] **AC-US2-01**: The provider dropdown shows only available providers (from `GET /api/config`)
- [x] **AC-US2-02**: Changing provider auto-selects the first available model for that provider
- [x] **AC-US2-03**: Claude CLI defaults to the `sonnet` model for generation
- [x] **AC-US2-04**: Provider and model dropdowns are disabled during generation

---

## Implementation

**Increment**: [0485-skill-studio-ai-create](../../../../../increments/0485-skill-studio-ai-create/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_
