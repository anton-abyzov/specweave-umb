---
id: US-003
feature: FS-458
title: "History Filtering (P1)"
status: not_started
priority: P1
created: 2026-03-09
tldr: "**As a** skill author."
project: vskill
external:
  github:
    issue: 30
    url: https://github.com/anton-abyzov/vskill/issues/30
---

# US-003: History Filtering (P1)

**Feature**: [FS-458](./FEATURE.md)

**As a** skill author
**I want** to filter history entries by model, run type (benchmark/comparison/baseline), and date range
**So that** I can quickly find relevant past runs

---

## Acceptance Criteria

- [ ] **AC-US3-01**: Given the history API endpoint, when query parameters `model`, `type`, `from`, and `to` are provided, then only matching entries are returned
- [ ] **AC-US3-02**: Given the HistoryPage UI, when a user selects filter values, then the timeline updates to show only matching runs
- [ ] **AC-US3-03**: Given multiple filters are applied simultaneously, when the user clears one filter, then the remaining filters stay active
- [ ] **AC-US3-04**: Given no runs match the current filters, when viewing the HistoryPage, then an empty state message indicates no matching runs

---

## Implementation

**Increment**: [0458-eval-run-history](../../../../../increments/0458-eval-run-history/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-005**: Server-side history filtering in listHistory
- [x] **T-006**: FilterBar UI and empty state on HistoryPage
