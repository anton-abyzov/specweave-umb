---
id: US-011
feature: FS-398
title: "Fix GitHub Issue Search Title Format Mismatch (P0)"
status: completed
priority: P0
created: "2026-03-02T00:00:00.000Z"
tldr: "**As a** user with auto-create enabled."
project: specweave
---

# US-011: Fix GitHub Issue Search Title Format Mismatch (P0)

**Feature**: [FS-398](./FEATURE.md)

**As a** user with auto-create enabled
**I want** duplicate detection to work with the current issue title format
**So that** issues aren't duplicated when auto-create runs

---

## Acceptance Criteria

- [x] **AC-US11-01**: `external-issue-auto-creator.ts` createGitHubIssues() searches using current title format `US-XXX:` instead of legacy `[FS-XXX]` prefix which no longer matches (line 497-498)

---

## Implementation

**Increment**: [0398-sync-integration-critical-fixes](../../../../../increments/0398-sync-integration-critical-fixes/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_
