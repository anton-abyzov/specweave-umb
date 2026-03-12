---
id: US-001
feature: FS-493
title: "AI Mode Toggle (P1)"
status: completed
priority: P1
created: "2026-03-11T00:00:00.000Z"
tldr: "**As a** skill author using the inline create panel."
project: vskill
---

# US-001: AI Mode Toggle (P1)

**Feature**: [FS-493](./FEATURE.md)

**As a** skill author using the inline create panel
**I want** a Manual/AI mode toggle replacing the old passive banner
**So that** I can choose between manual form entry and AI-assisted generation without leaving Skill Studio

---

## Acceptance Criteria

- [x] **AC-US1-01**: Given the CreateSkillInline panel is open, when the component renders, then a Manual/AI-Assisted toggle is displayed in the header area where the old banner was, with Manual selected by default
- [x] **AC-US1-02**: Given the toggle is visible, when the user clicks "AI-Assisted", then the AI prompt section is shown and the manual form fields are hidden
- [x] **AC-US1-03**: Given the AI mode is active, when the user clicks "Manual", then the manual form fields are shown and the AI prompt section is hidden
- [x] **AC-US1-04**: Given the old passive banner ("AI-Assisted Authoring Available -- Run /skill-creator"), then it is completely removed from the component

---

## Implementation

**Increment**: [0493-ai-assisted-skill-authoring](../../../../../increments/0493-ai-assisted-skill-authoring/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-001**: Remove passive banner and creatorStatus code
- [x] **T-002**: Add new state, refs, and imports for AI mode
- [x] **T-003**: Render Manual/AI toggle in header
