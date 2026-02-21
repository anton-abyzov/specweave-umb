---
id: US-001
feature: FS-278
title: Detect default branch instead of hardcoding
status: complete
priority: P1
created: 2026-02-21
project: specweave
external:
  github:
    issue: 1212
    url: https://github.com/anton-abyzov/specweave/issues/1212
---
# US-001: Detect default branch instead of hardcoding

**Feature**: [FS-278](./FEATURE.md)

SpecWeave user with repos using non-`develop` default branches
**I want** the GitHub sync to detect the actual default branch from the GitHub API
**So that** links in GitHub issues point to valid URLs regardless of the repo's default branch

---

## Acceptance Criteria

- [x] **AC-US1-01**: `GitHubFeatureSync.syncFeatureToGitHub()` detects the default branch from GitHub API instead of hardcoding `'develop'`
- [x] **AC-US1-02**: `UserStoryIssueBuilder` receives the detected branch and uses it for all URL generation
- [x] **AC-US1-03**: `UserStoryContentBuilder.buildIssueBody()` uses detected branch instead of hardcoded `'develop'`
- [x] **AC-US1-04**: Default branch detection is cached per sync session (one API call per feature sync, not per user story)

---

## Implementation

**Increment**: [0278-fix-github-sync-links-and-comments](../../../../../increments/0278-fix-github-sync-links-and-comments/spec.md)

