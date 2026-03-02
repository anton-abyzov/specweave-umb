---
id: US-003
feature: FS-318
title: Add sync_to_github_project handler to LifecycleHookDispatcher
status: complete
priority: P1
created: 2026-02-22
project: specweave
external:
  github:
    issue: 1256
    url: https://github.com/anton-abyzov/specweave/issues/1256
---
# US-003: Add sync_to_github_project handler to LifecycleHookDispatcher

**Feature**: [FS-318](./FEATURE.md)

SpecWeave user with GitHub Project integration
**I want** the `sync_to_github_project` hook to fire after increment completion
**So that** my GitHub Project items are automatically updated when I close an increment

---

## Acceptance Criteria

- [x] **AC-US3-01**: `LifecycleHookDispatcher.onIncrementDone()` checks `hooks.post_increment_done.sync_to_github_project` config flag
- [x] **AC-US3-02**: When enabled, it invokes the GitHub feature sync CLI (`github-feature-sync-cli.js`) for the increment's feature ID
- [x] **AC-US3-03**: Feature ID is resolved from the increment's spec.md frontmatter or metadata.json
- [x] **AC-US3-04**: Handler failure does not block other post-closure operations (error-isolated)
- [x] **AC-US3-05**: Unit test verifies the handler dispatches when flag is true and skips when false

---

## Implementation

**Increment**: [0318-post-closure-sync-pipeline](../../../../../increments/0318-post-closure-sync-pipeline/spec.md)

