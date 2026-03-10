---
id: US-006
feature: FS-470
title: "Responsive Layout"
status: not_started
priority: P1
created: 2026-03-10
tldr: "**As a** skill author using the Studio on a smaller screen or narrow window."
project: vskill
---

# US-006: Responsive Layout

**Feature**: [FS-470](./FEATURE.md)

**As a** skill author using the Studio on a smaller screen or narrow window
**I want** the layout to adapt gracefully
**So that** the UI remains usable at various viewport widths

---

## Acceptance Criteria

- [ ] **AC-US6-01**: Below 768px viewport width, the split-pane collapses to a single-column layout showing only the skill list
- [ ] **AC-US6-02**: On narrow viewports, tapping a skill shows the detail panel as a full-width overlay with a back button to return to the list
- [ ] **AC-US6-03**: The back button preserves the current search/filter state
- [ ] **AC-US6-04**: The left panel width (280px) can be reduced to 240px at viewport widths between 768px and 1024px

---

## Implementation

**Increment**: [0470-skill-studio-full-redesign](../../../../../increments/0470-skill-studio-full-redesign/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-018**: Implement mobile view toggle in `StudioContext` and `RightPanel`
- [x] **T-019**: CSS media query single-column layout finalization
