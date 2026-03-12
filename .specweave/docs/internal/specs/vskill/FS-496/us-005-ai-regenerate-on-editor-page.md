---
id: US-005
feature: FS-496
title: "AI Regenerate on Editor Page"
status: completed
priority: P1
created: "2026-03-11T00:00:00.000Z"
tldr: "**As a** skill author."
project: vskill
---

# US-005: AI Regenerate on Editor Page

**Feature**: [FS-496](./FEATURE.md)

**As a** skill author
**I want** a "Regenerate" button in the EditorPanel toolbar that opens a prompt input, calls /api/skills/generate?sse, and shows a diff of the result
**So that** I can iterate on skill content using AI without leaving the editor

---

## Acceptance Criteria

- [x] **AC-US5-01**: Given the EditorPanel toolbar, when rendered, then a "Regenerate" button with a sparkle icon appears next to the existing "AI Edit" button
- [x] **AC-US5-02**: Given the user clicks "Regenerate," when the panel opens, then a prompt textarea is displayed below the toolbar (or as an inline panel) for entering the regeneration prompt
- [x] **AC-US5-03**: Given the user submits a prompt, when the SSE call to /api/skills/generate?sse completes, then a diff view is shown using computeDiff + the same diff rendering pattern from SkillImprovePanel (line-by-line with green/red highlighting)
- [x] **AC-US5-04**: Given the diff is displayed, when the user clicks "Apply," then the editor content is replaced with the generated content and the diff panel closes
- [x] **AC-US5-05**: Given the diff is displayed, when the user clicks "Discard," then the generated content is discarded and the diff panel closes without changes
- [x] **AC-US5-06**: Given a regeneration is in progress, when the user clicks "Regenerate" again, then the current SSE stream is aborted (AbortController pattern) and a new generation starts
- [x] **AC-US5-07**: Given the regeneration, when the provider/model is resolved, then the current workspace config provider/model is used (no separate model picker)

---

## Implementation

**Increment**: [0496-skill-studio-ui-polish](../../../../../increments/0496-skill-studio-ui-polish/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-005**: Add "Regenerate" button with sparkle icon to EditorPanel toolbar
- [x] **T-006**: Add Regenerate prompt panel and SSE streaming with diff display
- [x] **T-007**: Implement Apply and Discard actions for Regenerate diff
