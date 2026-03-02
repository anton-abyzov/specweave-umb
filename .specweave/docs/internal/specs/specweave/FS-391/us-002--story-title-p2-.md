---
id: US-002
feature: FS-391
title: "Architect Skill Markdown Previews (P1)"
status: completed
priority: P1
created: 2026-03-01T00:00:00.000Z
tldr: "**As a** developer using `/sw:architect`
**I want** to see ASCII architecture diagrams and schema tables in side-by-side previews when choosing between approaches
**So that** I can visually compare structural trade-offs before committing to a decision."
project: specweave
---

# US-002: Architect Skill Markdown Previews (P1)

**Feature**: [FS-391](./FEATURE.md)

**As a** developer using `/sw:architect`
**I want** to see ASCII architecture diagrams and schema tables in side-by-side previews when choosing between approaches
**So that** I can visually compare structural trade-offs before committing to a decision

---

## Acceptance Criteria

- [x] **AC-US2-01**: `/sw:architect` SKILL.md includes instructions to use `AskUserQuestion` with `markdown` previews when presenting 2+ architectural approaches
- [x] **AC-US2-02**: Architecture decisions show box diagrams (service/component layouts) in preview panels
- [x] **AC-US2-03**: Schema decisions show ASCII table format (columns, types, relationships) in preview panels
- [x] **AC-US2-04**: SKILL.md includes at least 2 complete examples of AskUserQuestion calls with markdown previews

---

## Implementation

**Increment**: [0391-askuserquestion-markdown-previews](../../../../../increments/0391-askuserquestion-markdown-previews/spec.md)

**Tasks**: See increment tasks.md for implementation details.
