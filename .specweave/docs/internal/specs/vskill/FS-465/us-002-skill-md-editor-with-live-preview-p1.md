---
id: US-002
feature: FS-465
title: "SKILL.md Editor with Live Preview (P1)"
status: not_started
priority: P1
created: 2026-03-09
tldr: "**As a** skill developer."
project: vskill
---

# US-002: SKILL.md Editor with Live Preview (P1)

**Feature**: [FS-465](./FEATURE.md)

**As a** skill developer
**I want** to edit my SKILL.md in a raw editor with a live preview
**So that** I can see changes in real-time without leaving the workspace

---

## Acceptance Criteria

- [ ] **AC-US2-01**: Given the Editor panel is active, when viewing the editor, then a split view shows a raw textarea on the left and rendered markdown preview on the right
- [ ] **AC-US2-02**: Given the Editor panel is active, when clicking view mode toggles, then the layout switches between Raw-only, Preview-only, and Side-by-Side modes
- [ ] **AC-US2-03**: Given SKILL.md has frontmatter, when viewing the preview pane, then frontmatter fields are displayed as structured key-value cards (not raw YAML)
- [ ] **AC-US2-04**: Given the editor has changes, when pressing Ctrl+S, then content saves to disk via PUT /api/skills/:plugin/:skill/content and the dirty indicator clears
- [ ] **AC-US2-05**: Given the editor content differs from the last saved version, when viewing the workspace, then a dirty indicator (dot or asterisk) appears next to the Editor icon in the rail and in the WorkspaceHeader
- [ ] **AC-US2-06**: Given the Editor panel is active, when clicking "Improve with AI", then the existing SkillImprovePanel opens inline with the editor and its output can be applied to the textarea

---

## Implementation

**Increment**: [0465-skill-builder-redesign](../../../../../increments/0465-skill-builder-redesign/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_
