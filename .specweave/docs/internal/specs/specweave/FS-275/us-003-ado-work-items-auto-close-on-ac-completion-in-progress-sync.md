---
id: US-003
feature: FS-275
title: ADO Work Items Auto-Close on AC Completion in Progress Sync
status: complete
priority: P2
created: 2026-02-21
project: specweave
external:
  github:
    issue: 1210
    url: "https://github.com/anton-abyzov/specweave/issues/1210"
---
# US-003: ADO Work Items Auto-Close on AC Completion in Progress Sync

**Feature**: [FS-275](./FEATURE.md)

developer using SpecWeave with Azure DevOps sync
**I want** ADO work items to be transitioned to Closed when progress-sync determines all ACs are complete
**So that** ADO work items reflect the actual completion state without waiting for increment closure

---

## Acceptance Criteria

- [x] **AC-US3-01**: `syncAdoACProgress()` in `ac-progress-sync.ts` already transitions to Closed when `isAllComplete()` returns true -- verify this works correctly with an integration-level test scenario
- [x] **AC-US3-02**: The progress-sync CLI (`sync-progress.ts`) invokes the ADO AC sync path when ADO is configured

---

## Implementation

**Increment**: [0275-auto-close-on-status-complete](../../../../../increments/0275-auto-close-on-status-complete/spec.md)

