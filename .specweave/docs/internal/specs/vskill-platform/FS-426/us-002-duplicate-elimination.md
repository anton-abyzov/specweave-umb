---
id: US-002
feature: FS-426
title: Duplicate elimination
status: complete
priority: P1
created: 2026-03-07
project: vskill-platform
---
# US-002: Duplicate elimination

**Feature**: [FS-426](./FEATURE.md)

developer reading the skill page
**I want** each piece of information to appear exactly once
**So that** the page feels clean and authoritative rather than repetitive

**Context**: Currently the page shows category in three places (badge pill row, meta section `MetaRow`, and potentially in labels), extensible info in two places (callout block and badge pill), and author/version/repo/updated in the meta section which duplicates the hero. The `SectionDivider title="Meta"` section and the category pill are redundant once the hero byline exists.

---

## Acceptance Criteria

- [x] **AC-US2-01**: Category text appears only in the hero byline row (from US-001 AC-US1-02). The category `span` is removed from the badges/pills row. The `MetaRow` for "Category" in the meta section is removed.
- [x] **AC-US2-02**: Extensible info appears only as a compact one-liner under the install section (e.g., "Semi-Extensible -- supports customization via skill-memories" with a "Learn more" link). The standalone callout block (the `borderLeft: 3px solid` div rendered when `skill.extensible` is true, lines 167-225 in current code) is removed. The extensible badge pill in the badges row is removed. The extensibility tier label and link are consolidated into this single one-liner.
- [x] **AC-US2-03**: The entire meta section (the `div` containing `MetaRow` components for Author, Category, Version, Repository, Source, Last Updated -- lines 300-357 in current code) is removed. Author, version, repository, source path, and last-updated date are all rendered in the hero byline (AC-US1-02). No data is lost -- every field from the old meta section appears in the byline.

---

## Implementation

**Increment**: [0426-skill-page-redesign](../../../../../increments/0426-skill-page-redesign/spec.md)

