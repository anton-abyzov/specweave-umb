---
id: US-002
feature: FS-383
title: "Fix assertion drift in external-issue-auto-creator tests (P1)"
status: completed
priority: P1
created: 2026-02-27T00:00:00.000Z
tldr: "**As a** developer maintaining the GitHub sync features
**I want** `external-issue-auto-creator."
project: specweave
---

# US-002: Fix assertion drift in external-issue-auto-creator tests (P1)

**Feature**: [FS-383](./FEATURE.md)

**As a** developer maintaining the GitHub sync features
**I want** `external-issue-auto-creator.test.ts` assertions to match current source behavior
**So that** the 20+ failures in this file are resolved

---

## Acceptance Criteria

- [x] **AC-US2-01**: `feature_id` format expectations match the current output format
- [x] **AC-US2-02**: Call pattern assertions (argument order, call count) match current implementation
- [x] **AC-US2-03**: All tests in `external-issue-auto-creator.test.ts` pass

---

## Implementation

**Increment**: [0383-fix-develop-tests-automerge](../../../../../increments/0383-fix-develop-tests-automerge/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_
