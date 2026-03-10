---
id: US-003
feature: FS-466
title: Per-Case Execution History in TestsPanel
status: completed
priority: P1
created: 2026-03-09
tldr: "**As a** skill author."
project: vskill
external:
  github:
    issue: 51
    url: https://github.com/anton-abyzov/vskill/issues/51
---

# US-003: Per-Case Execution History in TestsPanel

**Feature**: [FS-466](./FEATURE.md)

**As a** skill author
**I want** to see a test case's execution history directly within the TestsPanel detail view
**So that** I can track how a specific test case has performed over time without switching panels

---

## Acceptance Criteria

- [x] **AC-US3-01**: Given a selected test case in TestsPanel, when the CaseDetail view renders, then a collapsible "Execution History" section appears below the LLM Output section, collapsed by default
- [x] **AC-US3-02**: Given the user expands the Execution History section, when history data is available, then it fetches via api.getCaseHistory() and displays the last 10 runs showing: timestamp, model, run type badge, pass rate percentage, duration, token count, and per-assertion pass/fail with reasoning
- [x] **AC-US3-03**: Given 2 or more history entries exist for a test case, when the Execution History section is expanded, then a MiniTrend sparkline is displayed showing the pass rate trend over time
- [x] **AC-US3-04**: Given the Execution History section is expanded, when the user looks at the bottom of the history list, then a "View full history" link is visible that switches the active panel to the HistoryPanel (Ctrl+4)
- [x] **AC-US3-05**: Given the user expands the Execution History section, when the API call is in progress, then a loading spinner is shown; when no history exists, then a "No history for this case" message is displayed

---

## Implementation

**Increment**: [0466-skill-builder-preview-history](../../../../../increments/0466-skill-builder-preview-history/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-009**: Add CaseHistorySection skeleton with collapsed default state
- [x] **T-010**: Wire API call and render history entries in CaseHistorySection
- [x] **T-011**: Add MiniTrend sparkline and "View full history" link
- [x] **T-012**: Run full test suite and confirm zero regressions
