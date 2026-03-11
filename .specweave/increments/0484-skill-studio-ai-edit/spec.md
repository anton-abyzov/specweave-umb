---
increment: 0484-skill-studio-ai-edit
title: Skill Studio AI Edit Feature
type: feature
priority: P1
status: completed
created: 2026-03-11T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Skill Studio AI Edit Feature

## Problem Statement

Skill authors currently rely on the "Improve Skill" feature which applies opinionated best-practice improvements automatically. There is no way to give the AI a specific, freeform instruction like "add error handling section" or "make the description more concise." Authors must either manually edit the SKILL.md or accept the AI's generic improvements wholesale. This slows down targeted iteration.

## Goals

- Let skill authors send freeform natural-language instructions to modify SKILL.md content
- Show a clear diff with reasoning so authors can review before applying
- Integrate naturally into the existing editor toolbar and keyboard shortcut workflow

## User Stories

### US-001: Freeform AI Edit via Inline Prompt Bar
**Project**: vskill
**As a** skill author
**I want** to type a freeform instruction in an inline prompt bar and have AI modify my SKILL.md accordingly
**So that** I can quickly iterate on specific aspects of my skill without manual editing

**Acceptance Criteria**:
- [x] **AC-US1-01**: Given the editor is open, when the user clicks the "AI Edit" toolbar button (sparkle/wand icon), then an inline prompt bar appears at the bottom of the editor pane with an auto-focused textarea
- [x] **AC-US1-02**: Given the editor is open, when the user presses Cmd/Ctrl+K, then the same inline prompt bar appears with auto-focus
- [x] **AC-US1-03**: Given the prompt bar is visible, when the user presses Escape, then the prompt bar is dismissed without any API call
- [x] **AC-US1-04**: Given the prompt bar is visible, when the user types an instruction and submits (Enter or button click), then the current in-editor content (including unsaved changes) is sent to the backend along with the instruction
- [x] **AC-US1-05**: Given a request is in-flight, when the user views the prompt bar, then the submit button is disabled and a loading indicator is shown

---

### US-002: Diff Review and Apply/Discard for AI Edits
**Project**: vskill
**As a** skill author
**I want** to see a diff of AI-proposed changes with reasoning before applying them
**So that** I can review and control what gets changed in my SKILL.md

**Acceptance Criteria**:
- [x] **AC-US2-01**: Given the AI returns a modified version, then a unified diff view appears in a bottom panel (same pattern as the existing SkillImprovePanel) showing added/removed lines with color coding
- [x] **AC-US2-02**: Given the diff is displayed, then a reasoning box above the diff explains what the AI changed and why
- [x] **AC-US2-03**: Given the diff is displayed, when the user clicks "Apply", then the editor content is updated with the AI's version, the content is saved to disk, and the diff panel closes
- [x] **AC-US2-04**: Given the diff is displayed, when the user clicks "Discard", then the diff panel closes and the editor content remains unchanged
- [x] **AC-US2-05**: Given the backend returns an error, then an error message is displayed in the prompt bar area and the user can retry or dismiss

## Out of Scope

- Instruction history or command recall (arrow-up through previous instructions)
- Inline editor diff (side-by-side within the editor pane itself)
- Request cancellation or queuing of concurrent instructions
- Partial/streaming diff display during generation
- Multi-turn conversation context (each instruction is independent)

## Technical Notes

### Backend
- Extend `POST /api/skills/:plugin/:skill/improve` to accept `mode: "instruct"`, `instruction: string`, and `content: string` fields
- When `mode === "instruct"`, use a focused system prompt that executes the user's instruction precisely against the provided content (skip benchmark failure context)
- Reuse existing `createLlmClient`, `---REASONING---` parsing, and history recording

### Frontend
- New `AiEditBar` component: inline prompt bar with textarea, submit button, loading state, and Escape-to-dismiss
- New workspace actions: `OPEN_AI_EDIT`, `CLOSE_AI_EDIT`, `AI_EDIT_LOADING`, `AI_EDIT_RESULT`, `AI_EDIT_ERROR`
- New workspace state fields: `aiEditOpen: boolean`, `aiEditLoading: boolean`, `aiEditResult: { improved, reasoning } | null`, `aiEditError: string | null`
- Toolbar button in EditorPanel with sparkle/wand icon
- Cmd/Ctrl+K keyboard shortcut registered on the editor pane
- Reuse `computeDiff` utility and unified diff rendering from SkillImprovePanel
- New `api.instructEdit(plugin, skill, { instruction, content, provider?, model? })` method

### Key Constraint
- The `content` field sent to the backend is `state.skillContent` (current editor text, including unsaved changes), NOT the disk version

## Success Metrics

- Feature is usable end-to-end: type instruction, see diff, apply or discard
- No regressions in existing "Improve Skill" flow
- Response latency matches existing improve endpoint (same LLM call pattern)
