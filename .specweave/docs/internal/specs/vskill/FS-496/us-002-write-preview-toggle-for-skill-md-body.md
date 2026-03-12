---
id: US-002
feature: FS-496
title: "Write/Preview Toggle for SKILL.md Body"
status: completed
priority: P1
created: "2026-03-11T00:00:00.000Z"
tldr: "**As a** skill author."
project: vskill
---

# US-002: Write/Preview Toggle for SKILL.md Body

**Feature**: [FS-496](./FEATURE.md)

**As a** skill author
**I want** a segmented Write/Preview toggle in the SKILL.md card header
**So that** I can preview how the markdown body content will render before creating the skill

---

## Acceptance Criteria

- [x] **AC-US2-01**: Given CreateSkillInline with the SKILL.md card visible, when the user sees the card header, then a segmented toggle with "Write" and "Preview" options is present, defaulting to "Write"
- [x] **AC-US2-02**: Given Write mode is active, when the user types in the textarea, then input works as before (no behavior change)
- [x] **AC-US2-03**: Given Preview mode is active, when the card body renders, then the body content is displayed as rendered markdown using renderMarkdown() with dangerouslySetInnerHTML, matching EditorPanel's preview pane styling
- [x] **AC-US2-04**: Given CreateSkillPage, when the user toggles to Preview, then the same markdown rendering behavior applies
- [x] **AC-US2-05**: Given the user switches between Write and Preview, then the body content is preserved (no data loss on toggle)

---

## Implementation

**Increment**: [0496-skill-studio-ui-polish](../../../../../increments/0496-skill-studio-ui-polish/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-002**: Add segmented Write/Preview toggle to SKILL.md card in both create forms
