---
id: US-001
feature: FS-474
title: "AI Skill Generation Appears in History (P1)"
status: completed
priority: P1
created: 2026-03-10T00:00:00.000Z
tldr: "**As a** skill author using Skill Studio."
project: vskill
---

# US-001: AI Skill Generation Appears in History (P1)

**Feature**: [FS-474](./FEATURE.md)

**As a** skill author using Skill Studio
**I want** AI-generated skill definitions to appear in the History tab
**So that** I have an audit trail of when and how skills were AI-generated

---

## Acceptance Criteria

- [x] **AC-US1-01**: When `POST /api/skills/generate` successfully returns a generated skill, a history entry with `type: "ai-generate"` is written to the target skill's `evals/history/` directory
- [x] **AC-US1-02**: The history entry includes the model used, provider, timestamp, and the generated skill's name in the `skill_name` field
- [x] **AC-US1-03**: The history entry stores the generation prompt and resulting skill content in a `generate` field (analogous to the `improve` field used by improve entries)

---

## Implementation

**Increment**: [0474-ai-command-history](../../../../../increments/0474-ai-command-history/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_
