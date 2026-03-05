---
id: US-002
feature: FS-432
title: Fluid Typography System
status: complete
priority: P2
created: 2026-03-05
project: specweave
---
# US-002: Fluid Typography System

**Feature**: [FS-432](./FEATURE.md)

site visitor on any device
**I want** typography that scales fluidly between mobile and desktop viewport widths
**So that** headings and body text are always optimally sized without breakpoint jumps

---

## Acceptance Criteria

- [x] **AC-US2-01**: Given display headings (hero title, section titles), when the viewport is resized from 375px to 1440px, then font sizes scale fluidly using CSS clamp() from a mobile minimum to a desktop maximum (display sizes ranging 48px to 80px)
- [x] **AC-US2-02**: Given body text and UI text, when the viewport is resized, then base font sizes remain readable at all widths with appropriate line-height adjustments
- [x] **AC-US2-03**: Given the typography token definitions, when reviewed, then they use clamp() functions referencing viewport units (e.g., clamp(3rem, 2.5rem + 2vw, 5rem)) rather than static rem values for display and heading sizes
- [x] **AC-US2-04**: Given the 12-column CSS Grid system, when a layout is viewed at any viewport width, then content respects max-width constraints and columns collapse gracefully on mobile

---

## Implementation

**Increment**: [0432-bold-website-redesign](../../../../../increments/0432-bold-website-redesign/spec.md)

