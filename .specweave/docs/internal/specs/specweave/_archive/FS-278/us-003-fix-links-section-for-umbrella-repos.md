---
id: US-003
feature: FS-278
title: Fix Links section for umbrella repos
status: complete
priority: P2
created: 2026-02-21
project: specweave
external:
  github:
    issue: 1214
    url: "https://github.com/anton-abyzov/specweave/issues/1214"
---
# US-003: Fix Links section for umbrella repos

**Feature**: [FS-278](./FEATURE.md)

SpecWeave user with an umbrella repo setup
**I want** Feature Spec and User Story File links in GitHub issues to point to accessible locations
**So that** GitHub issue links lead to valid content instead of 404 pages

---

## Acceptance Criteria

- [x] **AC-US3-01**: When the sync repo differs from the umbrella repo, links point to the increment's spec.md in the sync target repo (which is always pushed) rather than the umbrella's living docs
- [x] **AC-US3-02**: Feature Spec link uses the increment spec.md path as fallback when living docs are not in the target repo
- [x] **AC-US3-03**: User Story File link uses the increment spec.md path as fallback when living docs are not in the target repo
- [x] **AC-US3-04**: Increment link always points to the increment folder in the target repo

---

## Implementation

**Increment**: [0278-fix-github-sync-links-and-comments](../../../../../increments/0278-fix-github-sync-links-and-comments/spec.md)

