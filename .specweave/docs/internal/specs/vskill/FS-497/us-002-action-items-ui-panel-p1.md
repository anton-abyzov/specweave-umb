---
id: US-002
feature: FS-497
title: "Action items UI panel (P1)"
status: completed
priority: P1
created: "2026-03-11T00:00:00.000Z"
tldr: "**As a** skill author."
project: vskill
---

# US-002: Action items UI panel (P1)

**Feature**: [FS-497](./FEATURE.md)

**As a** skill author
**I want** to see action items rendered below the verdict card
**So that** I can quickly understand what to do without reading raw data

---

## Acceptance Criteria

- [x] **AC-US2-01**: ActionItemsPanel renders below verdict card with color-coded recommendation badge
- [x] **AC-US2-02**: Panel shows weaknesses (red) and strengths (green) in a 2-column grid
- [x] **AC-US2-03**: Suggested focus area is highlighted in a separate box
- [x] **AC-US2-04**: "Apply AI Fix" button appears for improve/rewrite recommendations

---

## Implementation

**Increment**: [0497-comparison-action-items](../../../../../increments/0497-comparison-action-items/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-004**: Create ActionItemsPanel UI component
- [x] **T-005**: Integrate ActionItemsPanel into ComparisonPage
