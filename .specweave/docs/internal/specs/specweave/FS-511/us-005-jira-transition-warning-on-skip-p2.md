---
id: US-005
feature: FS-511
title: JIRA Transition Warning on Skip (P2)
status: completed
priority: P1
created: 2026-03-12T00:00:00.000Z
tldr: "**As a** SpecWeave user syncing to JIRA."
project: specweave
external:
  github:
    issue: 1556
    url: https://github.com/anton-abyzov/specweave/issues/1556
---

# US-005: JIRA Transition Warning on Skip (P2)

**Feature**: [FS-511](./FEATURE.md)

**As a** SpecWeave user syncing to JIRA
**I want** a warning logged when a transition cannot be found
**So that** I can diagnose why work items remain in the wrong status

---

## Acceptance Criteria

- [x] **AC-US5-01**: `transitionIssue()` in `jira.ts` logs a warning (via `console.warn` or logger) when no matching transition is found, including the issue key, target status name, and the list of available transition names
- [x] **AC-US5-02**: `closeIssue()` in `jira.ts` reads the target status from config (`statusSync.mappings.jira.completed`) with fallback to `'Done'` instead of hardcoding `'Done'`
- [x] **AC-US5-03**: No error is thrown on missing transition (resilient sync continues)

---

## Implementation

**Increment**: [0511-fix-ado-jira-sync](../../../../../increments/0511-fix-ado-jira-sync/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_
