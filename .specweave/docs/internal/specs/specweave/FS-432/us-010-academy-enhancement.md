---
id: US-010
feature: FS-432
title: Academy Enhancement
status: complete
priority: P2
created: 2026-03-05
project: specweave
---
# US-010: Academy Enhancement

**Feature**: [FS-432](./FEATURE.md)

---

## Acceptance Criteria

- [x] **AC-US10-01**: Given the academy index page, when rendered, then it displays courses as a grid of ContentCards showing title, description, estimated reading time, difficulty level (beginner/intermediate/advanced), and prerequisites
- [x] **AC-US10-02**: Given course metadata, when a course frontmatter includes reading_time, difficulty, and prerequisites fields, then the ContentCard renders these as styled badges and metadata line items
- [x] **AC-US10-03**: Given the difficulty badges, when rendered, then beginner shows green, intermediate shows amber, and advanced shows purple, using Badge component variants
- [x] **AC-US10-04**: Given the academy page on mobile, when viewed at 375px, then the card grid collapses to a single column with cards stacking vertically

---

## Implementation

**Increment**: [0432-bold-website-redesign](../../../../../increments/0432-bold-website-redesign/spec.md)

