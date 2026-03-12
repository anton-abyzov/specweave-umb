---
id: US-001
feature: FS-502
title: Instant Model Propagation on Selection
status: completed
priority: P1
created: 2026-03-12T00:00:00.000Z
tldr: "**As a** skill author."
project: vskill
external:
  github:
    issue: 96
    url: https://github.com/anton-abyzov/vskill/issues/96
---

# US-001: Instant Model Propagation on Selection

**Feature**: [FS-502](./FEATURE.md)

**As a** skill author
**I want** all UI elements reflecting the active model to update immediately when I change the model in the sidebar selector
**So that** I have confidence that the correct model will be used for all actions

---

## Acceptance Criteria

- [x] **AC-US1-01**: Given the user is on the studio page with ModelSelector and CreateSkillInline both visible, when the user selects a different model in ModelSelector, then the "Generate with {model}" button text in CreateSkillInline reflects the new model name without page reload or component remount
- [x] **AC-US1-02**: Given the user changes the model in ModelSelector and the `api.setConfig()` call succeeds, then the context state updates only after server confirmation (not optimistically)
- [x] **AC-US1-03**: Given the user changes the model in ModelSelector and the `api.setConfig()` call fails, then the context retains the previous confirmed config and ModelSelector shows the `saving` state followed by reverting to the prior selection

---

## Implementation

**Increment**: [0502-config-context-sync](../../../../../increments/0502-config-context-sync/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-009**: Migrate ModelSelector to useConfig() and updateConfig() (Category C)
