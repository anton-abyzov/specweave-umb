---
id: US-003
feature: FS-622
title: Cost in StatsPanel (P1)
status: completed
priority: P1
created: 2026-03-19T00:00:00.000Z
tldr: "**As a** skill developer."
project: vskill
external_tools:
  jira:
    key: SWE2E-716
  ado:
    id: 1555
---

# US-003: Cost in StatsPanel (P1)

**Feature**: [FS-622](./FEATURE.md)

**As a** skill developer
**I want** cost metrics in the statistics panel
**So that** I can understand my evaluation spending over time

---

## Acceptance Criteria

- [x] **AC-US3-01**: "Total Cost" summary card shows aggregate cost across all runs
- [x] **AC-US3-02**: "Avg Cost/Run" summary card shows average cost per benchmark run
- [x] **AC-US3-03**: Model performance table includes "Avg Cost" column
- [x] **AC-US3-04**: Cost trend line shows cost per data point over time
- [x] **AC-US3-05**: StatsResult type extended with `totalCost`, `costPerRun`, and per-model cost fields
- [x] **AC-US3-06**: Stats API endpoint returns cost data from history entries

---

## Implementation

**Increment**: [0622-dashboard-cost-realtime-redesign](../../../../../increments/0622-dashboard-cost-realtime-redesign/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-010**: Extend frontend types
