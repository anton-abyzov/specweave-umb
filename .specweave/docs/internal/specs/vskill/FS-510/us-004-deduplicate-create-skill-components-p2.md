---
id: US-004
feature: FS-510
title: Deduplicate Create Skill Components (P2)
status: completed
priority: P1
created: 2026-03-12T00:00:00.000Z
tldr: "**As a** developer."
project: vskill
external_tools:
  jira:
    key: SWE2E-244
  ado:
    id: 210
---

# US-004: Deduplicate Create Skill Components (P2)

**Feature**: [FS-510](./FEATURE.md)

**As a** developer
**I want** shared logic between CreateSkillPage and CreateSkillInline extracted into a reusable hook
**So that** changes only need to be made in one place

---

## Acceptance Criteria

- [x] **AC-US4-01**: A `useCreateSkill` custom hook encapsulates shared state and handlers (layout detection, form state, AI generation, draft saving, plugin recommendation)
- [x] **AC-US4-02**: Both CreateSkillPage and CreateSkillInline consume the shared hook instead of duplicating logic
- [x] **AC-US4-03**: Both components behave identically to before the refactor (no functional regression)

---

## Implementation

**Increment**: [0510-skill-studio-ai-create-improvements](../../../../../increments/0510-skill-studio-ai-create-improvements/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_
