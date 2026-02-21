---
id: US-001
feature: FS-271
title: Fix loadUserStoriesForIncrement fallback
status: complete
priority: P1
created: 2026-02-21
project: specweave
external:
  github:
    issue: 1199
    url: https://github.com/anton-abyzov/specweave/issues/1199
---
# US-001: Fix loadUserStoriesForIncrement fallback

**Feature**: [FS-271](./FEATURE.md)

developer using SpecWeave sync
**I want** the sync coordinator to find user stories even when living docs folders are missing
**So that** GitHub issues are created reliably for all increments

---

## Acceptance Criteria

- [x] **AC-US1-01**: `loadUserStoriesForIncrement()` uses `deriveFeatureId()` as fallback when featureId is not in spec.md frontmatter or metadata.json
- [x] **AC-US1-02**: When living docs folder is missing, falls back to parsing user stories directly from spec.md (same as `ExternalIssueAutoCreator.parseUserStories()`)
- [x] **AC-US1-03**: Logs a warning when falling back, so developers know living docs sync should be run

---

## Implementation

**Increment**: [0271-fix-external-sync-pipeline](../../../../../increments/0271-fix-external-sync-pipeline/spec.md)

