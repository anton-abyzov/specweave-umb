---
id: US-003
feature: FS-499
title: "Dashboard Sync Error Display (P1)"
status: not_started
priority: P1
created: 2026-03-12
tldr: "**As a** SpecWeave user viewing the dashboard."
project: specweave
---

# US-003: Dashboard Sync Error Display (P1)

**Feature**: [FS-499](./FEATURE.md)

**As a** SpecWeave user viewing the dashboard
**I want** sync errors to be prominently displayed with real-time updates
**So that** I am immediately aware of sync failures and can take corrective action

---

## Acceptance Criteria

- [ ] **AC-US3-01**: Given sync errors occurred in the last 24 hours, when the user views the OverviewPage, then a "Recent Sync Errors" panel is visible showing up to 5 recent errors with provider name, increment ID, error message, and timestamp
- [ ] **AC-US3-02**: Given an external sync fails, when the failure is recorded, then an SSE event of type `sync-error` is broadcast to all connected dashboard clients
- [ ] **AC-US3-03**: Given an external sync fails, when the failure is recorded, then a notification entry is written to `.specweave/state/notifications.json` with severity `error`
- [ ] **AC-US3-04**: Given the user navigates to the SyncPage, when sync errors exist, then each error row is expandable to show the full error message and stack trace
- [ ] **AC-US3-05**: Given increments with incomplete provider coverage exist, when the user views the OverviewPage, then a sync gap count badge is displayed showing the number of increments with missing provider syncs

---

## Implementation

**Increment**: [0499-external-sync-resilience](../../../../../increments/0499-external-sync-resilience/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [ ] **T-008**: Add dashboard data endpoints for sync errors and sync gaps
- [ ] **T-009**: OverviewPage — Recent Sync Errors panel and sync gap badge
- [ ] **T-010**: SyncPage — Expandable error rows
