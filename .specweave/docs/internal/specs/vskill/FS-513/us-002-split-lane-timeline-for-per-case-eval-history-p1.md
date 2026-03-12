---
id: US-002
feature: FS-513
title: "Split-lane timeline for per-case eval history (P1)"
status: not_started
priority: P1
created: 2026-03-12
tldr: "**As a** skill developer."
project: vskill
---

# US-002: Split-lane timeline for per-case eval history (P1)

**Feature**: [FS-513](./FEATURE.md)

**As a** skill developer
**I want** the per-case execution history to use a two-column "Skill | Baseline" layout
**So that** I can visually distinguish benchmark runs from baseline runs and see how they compare over time

---

## Acceptance Criteria

- [ ] **AC-US2-01**: Given the CaseHistorySection renders, then it displays a two-column layout with "Skill" label on the left column and "Baseline" label on the right column
- [ ] **AC-US2-02**: Given history entries exist, when an entry has type `benchmark`, then it renders in the left (Skill) column only
- [ ] **AC-US2-03**: Given history entries exist, when an entry has type `baseline`, then it renders in the right (Baseline) column only
- [ ] **AC-US2-04**: Given history entries exist, when an entry has type `comparison`, then it renders as a single merged card spanning both columns with the delta and verdict badge centered between the two sides
- [ ] **AC-US2-05**: Given only benchmark entries exist and no baseline entries, then the left column is populated with entries and the right column displays "No baseline runs" in `var(--text-tertiary)` color at font-size 12px

---

## Implementation

**Increment**: [0513-skill-studio-eval-history-redesign](../../../../../increments/0513-skill-studio-eval-history-redesign/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [ ] **T-004**: Extract lane-partitioning logic for CaseHistorySection
- [ ] **T-005**: Render two-column CSS grid with column headers and empty-column placeholders
- [ ] **T-006**: Render comparison entries as full-width merged cards with delta and verdict badge
