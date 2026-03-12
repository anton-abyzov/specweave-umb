---
id: US-003
feature: FS-496
title: "Increase Description Textarea Height"
status: completed
priority: P1
created: "2026-03-11T00:00:00.000Z"
tldr: "**As a** skill author."
project: vskill
---

# US-003: Increase Description Textarea Height

**Feature**: [FS-496](./FEATURE.md)

**As a** skill author
**I want** a taller description textarea with vertical resize support
**So that** I have more room to write meaningful descriptions without scrolling

---

## Acceptance Criteria

- [x] **AC-US3-01**: Given CreateSkillInline, when the description textarea renders, then rows is 3 (was 2), minHeight is 72px, and CSS resize is set to "vertical"
- [x] **AC-US3-02**: Given CreateSkillPage, when the description textarea renders, then the same rows=3, minHeight=72px, and resize="vertical" are applied
- [x] **AC-US3-03**: Given either form, when the user drags the textarea resize handle vertically, then the textarea expands or contracts (no horizontal resize)

---

## Implementation

**Increment**: [0496-skill-studio-ui-polish](../../../../../increments/0496-skill-studio-ui-polish/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-003**: Update description textarea to rows=3, minHeight 72px, vertical resize in both create forms
