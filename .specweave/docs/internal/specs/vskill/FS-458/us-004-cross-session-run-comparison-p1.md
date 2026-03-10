---
id: US-004
feature: FS-458
title: "Cross-Session Run Comparison (P1)"
status: not_started
priority: P1
created: 2026-03-09
tldr: "**As a** skill author."
project: vskill
---

# US-004: Cross-Session Run Comparison (P1)

**Feature**: [FS-458](./FEATURE.md)

**As a** skill author
**I want** to select any two historical runs and see a side-by-side diff showing per-case regressions and improvements
**So that** I can understand how changes to my skill affected evaluation outcomes

---

## Acceptance Criteria

- [ ] **AC-US4-01**: Given the HistoryPage timeline, when a user checks exactly two run checkboxes, then a "Compare" button becomes visible
- [ ] **AC-US4-02**: Given the user clicks "Compare" with two runs selected, when the comparison loads, then a side-by-side view shows per-case pass/fail status for both runs with regressions highlighted in red and improvements in green
- [ ] **AC-US4-03**: Given a compare API endpoint `GET /api/skills/:plugin/:skill/history-compare?a={timestamp}&b={timestamp}`, when called with two valid timestamps, then it returns per-case diff data using the existing `computeRegressions` function
- [ ] **AC-US4-04**: Given one run has eval cases that the other does not (different eval sets), when comparing, then unmatched cases are shown with a "new" or "removed" indicator

---

## Implementation

**Increment**: [0458-eval-run-history](../../../../../increments/0458-eval-run-history/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-007**: History-compare API endpoint
- [x] **T-008**: CompareView UI on HistoryPage with checkbox selection
