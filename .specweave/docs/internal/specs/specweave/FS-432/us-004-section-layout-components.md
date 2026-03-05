---
id: US-004
feature: FS-432
title: Section Layout Components
status: complete
priority: P2
created: 2026-03-05
project: specweave
---
# US-004: Section Layout Components

**Feature**: [FS-432](./FEATURE.md)

developer assembling landing page sections
**I want** Section wrapper and SectionHeader components with multiple layout variants
**So that** every section has consistent padding, max-width, and heading hierarchy

---

## Acceptance Criteria

- [x] **AC-US4-01**: Given the Section component, when rendered with variant prop (default, dark, gradient, accent), then the background, padding, and inner max-width are applied from tokens with correct light/dark mode behavior
- [x] **AC-US4-02**: Given the SectionHeader component, when rendered with label, title, and subtitle props, then it displays an uppercase label, a large title using fluid typography, and a muted subtitle paragraph beneath
- [x] **AC-US4-03**: Given a Section with variant="dark", when rendered, then the section uses --sw-surface-dark background with light text tokens and the SectionHeader label uses the primary accent color
- [x] **AC-US4-04**: Given sections on mobile viewport (375px), when viewed, then section vertical padding reduces proportionally and content stacks vertically

---

## Implementation

**Increment**: [0432-bold-website-redesign](../../../../../increments/0432-bold-website-redesign/spec.md)

