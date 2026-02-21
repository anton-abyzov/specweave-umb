---
id: US-003
feature: FS-271
title: Fix externalLinks format checking
status: complete
priority: P2
created: 2026-02-21
project: specweave
external:
  github:
    issue: 1201
    url: "https://github.com/anton-abyzov/specweave/issues/1201"
---
# US-003: Fix externalLinks format checking

**Feature**: [FS-271](./FEATURE.md)

developer using SpecWeave sync
**I want** existing issue checks to recognize all metadata formats
**So that** duplicate issues are not created

---

## Acceptance Criteria

- [x] **AC-US3-01**: `ExternalIssueAutoCreator.checkExistingIssue()` also checks `externalLinks.github` format
- [x] **AC-US3-02**: `sync-progress.ts checkExistingGitHubIssue()` also checks `externalLinks.github` format

---

## Implementation

**Increment**: [0271-fix-external-sync-pipeline](../../../../../increments/0271-fix-external-sync-pipeline/spec.md)

