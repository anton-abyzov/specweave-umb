---
id: US-003
feature: FS-348
title: "Extract AC Checkbox Sync to GitHub Plugin (P1)"
status: completed
priority: P1
created: 2026-02-25
tldr: "Extract AC Checkbox Sync to GitHub Plugin (P1)"
project: specweave
---

# US-003: Extract AC Checkbox Sync to GitHub Plugin (P1)

**Feature**: [FS-348](./FEATURE.md)

---

## Acceptance Criteria

- [x] **AC-US3-01**: New `GitHubACCheckboxSync` class in `plugins/specweave-github/lib/github-ac-checkbox-sync.ts`
- [x] **AC-US3-02**: `syncACCheckboxesToGitHub()` and `parseACStatusFromSpec()` moved from SyncCoordinator to the new class
- [x] **AC-US3-03**: `update-ac-status.ts` hook updated to import from new location
- [x] **AC-US3-04**: `sync-progress.ts` CLI updated to import from new location
- [x] **AC-US3-05**: SyncCoordinator no longer has any `syncACCheckboxesToGitHub` or `parseACStatusFromSpec` methods

---

## Implementation

**Increment**: [0348-consolidate-github-sync-path](../../../../../increments/0348-consolidate-github-sync-path/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_
