---
id: US-007
feature: FS-398
title: "Fix Missing Error Handling in Provider API Responses (P1)"
status: completed
priority: P0
created: 2026-03-02T00:00:00.000Z
tldr: "**As a** developer debugging sync failures."
project: specweave
---

# US-007: Fix Missing Error Handling in Provider API Responses (P1)

**Feature**: [FS-398](./FEATURE.md)

**As a** developer debugging sync failures
**I want** all provider API calls to check response status
**So that** errors surface clearly instead of crashing on JSON parse

---

## Acceptance Criteria

- [x] **AC-US7-01**: JIRA provider `transitionIssue()` checks response.ok before parsing JSON (line 335-336)
- [x] **AC-US7-02**: JIRA provider `detectHierarchy()` checks response.ok before parsing (line 233)
- [x] **AC-US7-03**: ADO provider `pullChanges()` checks WIQL response.ok and batch GET response.ok before parsing (lines 186, 193-196)
- [x] **AC-US7-04**: GitHub provider `applyLabels()` PUT request checks response.ok (line 187)
- [x] **AC-US7-05**: GitHub provider `ensureLabelExists()` distinguishes 422 (already exists) from real errors instead of blanket catch (line 273-275)

---

## Implementation

**Increment**: [0398-sync-integration-critical-fixes](../../../../../increments/0398-sync-integration-critical-fixes/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_
