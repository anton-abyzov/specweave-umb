---
id: US-008
feature: FS-465
title: "Centralized State Management (P0)"
status: not_started
priority: P1
created: 2026-03-09
tldr: "**As a** developer."
project: vskill
---

# US-008: Centralized State Management (P0)

**Feature**: [FS-465](./FEATURE.md)

**As a** developer
**I want** shared workspace state via a single hook
**So that** cross-panel interactions work seamlessly without prop drilling or duplicated fetches

---

## Acceptance Criteria

- [ ] **AC-US8-01**: Given the workspace is mounted, when useSkillWorkspace() is called, then it returns shared state including: skillContent, evals, inlineResults, activePanel, selectedCaseId, isDirty, isRunning, iterationCount, and regressions
- [ ] **AC-US8-02**: Given the Editor saves content, when the save completes, then the shared skillContent updates and isDirty resets to false; given a Run completes, then shared inlineResults update for all panels
- [ ] **AC-US8-03**: Given a test case "Run" button is clicked in the Tests panel, when the action fires, then activePanel switches to "run" and scope is set to the selected case ID
- [ ] **AC-US8-04**: Given "Fix with AI" is clicked on a failed assertion, when the action fires, then activePanel switches to "editor" and the improve panel opens with the target eval_id pre-set

---

## Implementation

**Increment**: [0465-skill-builder-redesign](../../../../../increments/0465-skill-builder-redesign/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_
