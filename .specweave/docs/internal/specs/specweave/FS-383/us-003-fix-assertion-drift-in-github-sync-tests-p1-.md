---
id: US-003
feature: FS-383
title: "Fix assertion drift in GitHub sync tests (P1)"
status: completed
priority: P1
created: 2026-02-27T00:00:00.000Z
tldr: "**As a** developer maintaining the GitHub sync features
**I want** GitHub sync test expectations to match current call patterns
**So that** sync-related test files pass."
project: specweave
---

# US-003: Fix assertion drift in GitHub sync tests (P1)

**Feature**: [FS-383](./FEATURE.md)

**As a** developer maintaining the GitHub sync features
**I want** GitHub sync test expectations to match current call patterns
**So that** sync-related test files pass

---

## Acceptance Criteria

- [x] **AC-US3-01**: `github-ac-sync-integration.test.ts` expects the correct number of `gh` calls (currently 4, not 3)
- [x] **AC-US3-02**: `github-feature-sync-auto-close.test.ts` close call count expectation matches current behavior
- [x] **AC-US3-03**: `github-us-auto-closer.test.ts` call count expectations match current behavior (4, not 3)
- [x] **AC-US3-04**: All three GitHub sync test files pass

---

## Implementation

**Increment**: [0383-fix-develop-tests-automerge](../../../../../increments/0383-fix-develop-tests-automerge/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_
