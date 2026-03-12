---
id: US-001
feature: FS-496
title: "Rename 'System Prompt' to 'SKILL.md'"
status: completed
priority: P1
created: "2026-03-11T00:00:00.000Z"
tldr: "**As a** skill author."
project: vskill
---

# US-001: Rename "System Prompt" to "SKILL.md"

**Feature**: [FS-496](./FEATURE.md)

**As a** skill author
**I want** the body textarea section labeled "SKILL.md" with a file icon badge and "Skill Definition" subtitle
**So that** the form labeling matches the actual file being created and is consistent with SkillContentViewer

---

## Acceptance Criteria

- [x] **AC-US1-01**: Given CreateSkillInline is rendered, when the user views the body textarea card, then the heading reads "SKILL.md" (not "System Prompt") with a file icon badge matching SkillContentViewer's icon style
- [x] **AC-US1-02**: Given CreateSkillPage is rendered, when the user views the body textarea card, then the heading reads "SKILL.md" with the same file icon badge and "Skill Definition" subtitle
- [x] **AC-US1-03**: Given either create form, when the user views the heading, then a secondary subtitle "Skill Definition" appears below/beside the "SKILL.md" label

---

## Implementation

**Increment**: [0496-skill-studio-ui-polish](../../../../../increments/0496-skill-studio-ui-polish/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-001**: Replace "System Prompt" heading with SKILL.md file icon badge in both create forms
