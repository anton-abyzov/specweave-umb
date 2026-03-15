---
id: US-003
feature: FS-525
title: "Add living docs sync skip mechanism"
status: completed
priority: P1
created: 2026-03-14T00:00:00.000Z
tldr: "**As a** developer working on increments that do not need external sync."
project: specweave
related_projects: [specweave-umb]
---

# US-003: Add living docs sync skip mechanism

**Feature**: [FS-525](./FEATURE.md)

**As a** developer working on increments that do not need external sync
**I want** to disable living docs sync globally or per-increment
**So that** unnecessary API calls and sync delays are avoided

---

## Acceptance Criteria

- [x] **AC-US3-01**: Given `autoSyncOnCompletion: false` in `.specweave/config.json`, when `onIncrementDone` fires, then living docs sync is skipped entirely
- [x] **AC-US3-02**: Given `skipLivingDocsSync: true` in an increment's `metadata.json` and `autoSyncOnCompletion` is not false globally, when `onIncrementDone` fires for that increment, then living docs sync is skipped for that increment only
- [x] **AC-US3-03**: Given the SpecWeave TypeScript codebase, when the `IncrementMetadata` interface is inspected, then it includes an optional `skipLivingDocsSync?: boolean` field

---

## Implementation

**Increment**: [0525-fix-living-docs-sync-architecture](../../../../../increments/0525-fix-living-docs-sync-architecture/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_
