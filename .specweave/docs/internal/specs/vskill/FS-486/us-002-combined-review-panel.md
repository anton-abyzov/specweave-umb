---
id: US-002
feature: FS-486
title: Combined Review Panel
status: completed
priority: P1
created: 2026-03-11T00:00:00.000Z
tldr: "**As a** skill author."
project: vskill
external:
  github:
    issue: 73
    url: https://github.com/anton-abyzov/vskill/issues/73
---

# US-002: Combined Review Panel

**Feature**: [FS-486](./FEATURE.md)

**As a** skill author
**I want** to see both the SKILL.md diff and suggested eval changes in the AI Edit panel
**So that** I can review everything before applying

---

## Acceptance Criteria

- [x] **AC-US2-01**: When AI Edit returns eval changes, the panel shows eval change cards below the SKILL.md diff, grouped by type: removes first, then modifies, then adds
- [x] **AC-US2-02**: Each eval change card displays a compact summary (eval name, action badge, reason) with an expandable section showing full eval content
- [x] **AC-US2-03**: For modify actions, the expanded detail shows a mini-diff of which fields changed between the original and proposed eval case
- [x] **AC-US2-04**: When AI Edit returns no eval changes, the eval changes section is hidden entirely
- [x] **AC-US2-05**: Each eval change card has a checkbox that is checked by default; users can toggle individual changes on/off before applying

---

## Implementation

**Increment**: [0486-smart-ai-edit](../../../../../increments/0486-smart-ai-edit/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-003**: EvalChangeCard Component -- Summary, Action Badge, Expand/Collapse
- [x] **T-004**: EvalChangesPanel Component -- Grouping, Select All/Deselect All
- [x] **T-005**: Integrate EvalChangesPanel into AiEditBar
