---
id: US-004
feature: FS-398
title: "Fix Pagination Gaps in Pull Operations (P1)"
status: completed
priority: P0
created: 2026-03-02T00:00:00.000Z
tldr: "**As a** user with many external issues."
project: specweave
---

# US-004: Fix Pagination Gaps in Pull Operations (P1)

**Feature**: [FS-398](./FEATURE.md)

**As a** user with many external issues
**I want** sync pull operations to retrieve all relevant items
**So that** no issues are missed during sync

---

## Acceptance Criteria

- [x] **AC-US4-01**: GitHub provider `pullChanges()` handles pagination via Link header beyond the first 50 results
- [x] **AC-US4-02**: JIRA provider `pullChanges()` handles pagination via `startAt` beyond `maxResults: 50`
- [x] **AC-US4-03**: ADO provider `pullChanges()` handles WIQL results beyond the first 50 IDs via batching

---

## Implementation

**Increment**: [0398-sync-integration-critical-fixes](../../../../../increments/0398-sync-integration-critical-fixes/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_
