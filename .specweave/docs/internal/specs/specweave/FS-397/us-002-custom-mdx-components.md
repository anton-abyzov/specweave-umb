---
id: US-002
feature: FS-397
title: Custom MDX Components
status: complete
priority: P1
created: 2026-03-02
project: specweave
---
# US-002: Custom MDX Components

**Feature**: [FS-397](./FEATURE.md)

docs author
**I want** reusable styled components (Callouts, Steps, Cards, Accordions)
**So that** I can create rich, structured documentation pages

---

## Acceptance Criteria

- [x] **AC-US2-01**: `<Note>`, `<Tip>`, `<Warning>`, `<Info>` callout components with icon, optional title, left border accent, tinted background
- [x] **AC-US2-02**: `<Steps>`/`<Step title="">` with CSS counter numbering and vertical connector
- [x] **AC-US2-03**: `<CardGroup cols={2|3|4}>`/`<Card title="" href="" icon="">` responsive grid
- [x] **AC-US2-04**: `<Accordion>`/`<AccordionGroup>` with native details/summary, chevron animation
- [x] **AC-US2-05**: All components globally registered via `src/theme/MDXComponents.tsx`

---

## Implementation

**Increment**: [0397-development-loom-docs-rework](../../../../../increments/0397-development-loom-docs-rework/spec.md)

