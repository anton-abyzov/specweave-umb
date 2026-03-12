---
id: US-001
feature: FS-484
title: "Freeform AI Edit via Inline Prompt Bar"
status: completed
priority: P1
created: "2026-03-11T00:00:00.000Z"
tldr: "**As a** skill author."
project: vskill
---

# US-001: Freeform AI Edit via Inline Prompt Bar

**Feature**: [FS-484](./FEATURE.md)

**As a** skill author
**I want** to type a freeform instruction in an inline prompt bar and have AI modify my SKILL.md accordingly
**So that** I can quickly iterate on specific aspects of my skill without manual editing

---

## Acceptance Criteria

- [x] **AC-US1-01**: Given the editor is open, when the user clicks the "AI Edit" toolbar button (sparkle/wand icon), then an inline prompt bar appears at the bottom of the editor pane with an auto-focused textarea
- [x] **AC-US1-02**: Given the editor is open, when the user presses Cmd/Ctrl+K, then the same inline prompt bar appears with auto-focus
- [x] **AC-US1-03**: Given the prompt bar is visible, when the user presses Escape, then the prompt bar is dismissed without any API call
- [x] **AC-US1-04**: Given the prompt bar is visible, when the user types an instruction and submits (Enter or button click), then the current in-editor content (including unsaved changes) is sent to the backend along with the instruction
- [x] **AC-US1-05**: Given a request is in-flight, when the user views the prompt bar, then the submit button is disabled and a loading indicator is shown

---

## Implementation

**Increment**: [0484-skill-studio-ai-edit](../../../../../increments/0484-skill-studio-ai-edit/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-001**: Extend backend /improve endpoint with instruct mode
- [x] **T-002**: Extend workspace state and reducer with AI edit actions
- [x] **T-003**: Add instructEdit API method and submitAiEdit context action
