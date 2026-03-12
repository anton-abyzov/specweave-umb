---
id: US-002
feature: FS-474
title: "AI Eval Generation Appears in History (P1)"
status: completed
priority: P1
created: 2026-03-10T00:00:00.000Z
tldr: "**As a** skill author using Skill Studio."
project: vskill
---

# US-002: AI Eval Generation Appears in History (P1)

**Feature**: [FS-474](./FEATURE.md)

**As a** skill author using Skill Studio
**I want** AI-generated test cases to appear in the History tab
**So that** I can track when evals were auto-generated and which model was used

---

## Acceptance Criteria

- [x] **AC-US2-01**: When `POST /api/skills/:plugin/:skill/generate-evals` successfully returns generated evals, a history entry with `type: "eval-generate"` is written to the skill's `evals/history/` directory
- [x] **AC-US2-02**: The history entry includes the model used, provider, timestamp, skill name, and the number of generated test cases
- [x] **AC-US2-03**: The history entry is visible in the History tab timeline alongside benchmark and improve entries

---

## Implementation

**Increment**: [0474-ai-command-history](../../../../../increments/0474-ai-command-history/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_
