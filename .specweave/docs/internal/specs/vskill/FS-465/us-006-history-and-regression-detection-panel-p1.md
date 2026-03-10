---
id: US-006
feature: FS-465
title: History and Regression Detection Panel (P1)
status: not_started
priority: P1
created: 2026-03-09
tldr: "**As a** skill developer."
project: vskill
external:
  github:
    issue: 46
    url: https://github.com/anton-abyzov/vskill/issues/46
---

# US-006: History and Regression Detection Panel (P1)

**Feature**: [FS-465](./FEATURE.md)

**As a** skill developer
**I want** to view run history with regression detection
**So that** I can track improvements and catch regressions over time

---

## Acceptance Criteria

- [ ] **AC-US6-01**: Given the History panel is active, when viewing the layout, then three sub-tabs are available: Timeline, Per-Eval, and Statistics
- [ ] **AC-US6-02**: Given the Timeline tab is active, when viewing the list, then historical runs display with model, type (benchmark/comparison/baseline), date, and pass rate; filterable by model, type, and date range
- [ ] **AC-US6-03**: Given the Timeline tab is active, when selecting 2 runs via checkboxes, then a "Compare" button enables and clicking it shows a side-by-side regression/improvement diff
- [ ] **AC-US6-04**: Given the Per-Eval tab is active, when viewing the grid, then an assertion-level heatmap renders with rows=assertions, columns=runs (most recent on right), cells colored green (pass) or red (fail)
- [ ] **AC-US6-05**: Given the heatmap is displayed, when clicking any cell, then a detail overlay shows that run's full output text and the assertion's reasoning
- [ ] **AC-US6-06**: Given regressions are detected (assertions that were passing but now fail), when viewing the WorkspaceHeader, then a regression alert banner is visible with count and link to History panel
- [ ] **AC-US6-07**: Given the Statistics tab is active, when viewing the content, then it reuses the existing StatsPanel and TrendChart components

---

## Implementation

**Increment**: [0465-skill-builder-redesign](../../../../../increments/0465-skill-builder-redesign/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_
