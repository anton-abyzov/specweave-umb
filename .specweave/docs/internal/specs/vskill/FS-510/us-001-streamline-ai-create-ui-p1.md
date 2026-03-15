---
id: US-001
feature: FS-510
title: Streamline AI Create UI (P1)
status: completed
priority: P1
created: 2026-03-12T00:00:00.000Z
tldr: "**As a** skill creator."
project: vskill
external_tools:
  jira:
    key: SWE2E-235
  ado:
    id: 194
---

# US-001: Streamline AI Create UI (P1)

**Feature**: [FS-510](./FEATURE.md)

**As a** skill creator
**I want** a clean, focused AI creation interface without unnecessary banners or test case generation
**So that** I can quickly create skills without visual clutter

---

## Acceptance Criteria

- [x] **AC-US1-01**: The AI mode prompt area does not display verbose help text below the textarea (remove "The AI will generate the name, description, system prompt, and test cases" paragraph)
- [x] **AC-US1-02**: AI generation does not pass or save test cases (evals) during skill creation — evals are handled separately in the workspace after creation
- [x] **AC-US1-03**: The SkillFileTree does not show an evals directory when creating via AI (since evals are no longer generated during creation)

---

## Implementation

**Increment**: [0510-skill-studio-ai-create-improvements](../../../../../increments/0510-skill-studio-ai-create-improvements/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_
