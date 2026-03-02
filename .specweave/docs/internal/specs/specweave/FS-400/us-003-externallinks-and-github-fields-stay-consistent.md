---
id: US-003
feature: FS-400
title: "externalLinks and github fields stay consistent"
status: completed
priority: P1
created: 2026-03-02
tldr: "**As a** developer."
---

# US-003: externalLinks and github fields stay consistent

**Feature**: [FS-400](./FEATURE.md)

**As a** developer
**I want** the sync pipeline to write to both `externalLinks` and `github` metadata fields
**So that** all consumers (reconciler, progress-sync, living docs) can find sync data regardless of which field they read

---

## Acceptance Criteria

- [x] **AC-US3-01**: `GitHubFeatureSync.syncFeatureToGitHub()` writes issue numbers and milestone to BOTH `externalLinks.github` AND `github` fields in metadata.json
- [x] **AC-US3-02**: `syncToGitHub()` in LivingDocsSync writes to both fields
- [x] **AC-US3-03**: A migration utility normalizes existing metadata — if `github` has data but `externalLinks` is empty, populate `externalLinks` from `github`

---

## Implementation

**Increment**: [0400-sync-pipeline-reliability](../../../../../increments/0400-sync-pipeline-reliability/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_
