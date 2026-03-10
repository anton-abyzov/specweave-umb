---
id: US-005
feature: FS-458
title: "Trend Visualization (P2)"
status: completed
priority: P1
created: 2026-03-09T00:00:00.000Z
tldr: "**As a** skill author."
project: vskill
external:
  github:
    issue: 32
    url: https://github.com/anton-abyzov/vskill/issues/32
---

# US-005: Trend Visualization (P2)

**Feature**: [FS-458](./FEATURE.md)

**As a** skill author
**I want** to see a pass rate over time chart on the HistoryPage, color-coded by run type
**So that** I can spot quality trends and regressions at a glance

---

## Acceptance Criteria

- [x] **AC-US5-01**: Given the HistoryPage has history entries, when the page loads, then a fixed-width SVG trend chart renders above the timeline showing pass rate (0-100%) on Y axis and runs chronologically on X axis
- [x] **AC-US5-02**: Given runs of different types exist, when the chart renders, then benchmark runs are one color, comparison runs are another, and baseline runs are a third
- [x] **AC-US5-03**: Given the chart is rendered, when hovering over a data point, then a tooltip shows the run timestamp, model, type, and pass rate
- [x] **AC-US5-04**: Given fewer than 2 history entries exist, when the HistoryPage loads, then the trend chart is not displayed

---

## Implementation

**Increment**: [0458-eval-run-history](../../../../../increments/0458-eval-run-history/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-009**: TrendChart SVG component for HistoryPage
