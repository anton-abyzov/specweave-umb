---
id: US-002
feature: FS-275
title: JIRA Issues Auto-Transition on AC Completion in Progress Sync
status: complete
priority: P2
created: 2026-02-21
project: specweave
external:
  github:
    issue: 1209
    url: https://github.com/anton-abyzov/specweave/issues/1209
---
# US-002: JIRA Issues Auto-Transition on AC Completion in Progress Sync

**Feature**: [FS-275](./FEATURE.md)

developer using SpecWeave with JIRA sync
**I want** JIRA issues to be transitioned to Done when progress-sync determines all ACs are complete
**So that** I do not have to wait for increment closure to see JIRA issues resolved

---

## Acceptance Criteria

- [x] **AC-US2-01**: `syncJiraACProgress()` in `ac-progress-sync.ts` already transitions to Done when `isAllComplete()` returns true -- verify this works correctly with an integration-level test scenario
- [x] **AC-US2-02**: The progress-sync CLI (`sync-progress.ts`) invokes the JIRA AC sync path (not just GitHub checkbox sync) when JIRA is configured

---

## Implementation

**Increment**: [0275-auto-close-on-status-complete](../../../../../increments/0275-auto-close-on-status-complete/spec.md)

