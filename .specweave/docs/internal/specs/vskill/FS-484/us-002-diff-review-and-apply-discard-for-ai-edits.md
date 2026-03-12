---
id: US-002
feature: FS-484
title: "Diff Review and Apply/Discard for AI Edits"
status: completed
priority: P1
created: "2026-03-11T00:00:00.000Z"
tldr: "**As a** skill author."
project: vskill
---

# US-002: Diff Review and Apply/Discard for AI Edits

**Feature**: [FS-484](./FEATURE.md)

**As a** skill author
**I want** to see a diff of AI-proposed changes with reasoning before applying them
**So that** I can review and control what gets changed in my SKILL.md

---

## Acceptance Criteria

- [x] **AC-US2-01**: Given the AI returns a modified version, then a unified diff view appears in a bottom panel (same pattern as the existing SkillImprovePanel) showing added/removed lines with color coding
- [x] **AC-US2-02**: Given the diff is displayed, then a reasoning box above the diff explains what the AI changed and why
- [x] **AC-US2-03**: Given the diff is displayed, when the user clicks "Apply", then the editor content is updated with the AI's version, the content is saved to disk, and the diff panel closes
- [x] **AC-US2-04**: Given the diff is displayed, when the user clicks "Discard", then the diff panel closes and the editor content remains unchanged
- [x] **AC-US2-05**: Given the backend returns an error, then an error message is displayed in the prompt bar area and the user can retry or dismiss

---

## Implementation

**Increment**: [0484-skill-studio-ai-edit](../../../../../increments/0484-skill-studio-ai-edit/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-004**: Create AiEditBar component
- [x] **T-005**: Integrate AiEditBar and Cmd/Ctrl+K shortcut into EditorPanel toolbar
- [x] **T-006**: Render AI edit diff panel with Apply/Discard in EditorPanel
- [x] **T-007**: Integration test - full AI edit flow end-to-end
