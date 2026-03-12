---
id: US-009
feature: FS-398
title: "Fix JIRA Idempotency Check Comparing Different Formats (P0)"
status: completed
priority: P0
created: "2026-03-02T00:00:00.000Z"
tldr: "**As a** user with JIRA sync enabled."
project: specweave
---

# US-009: Fix JIRA Idempotency Check Comparing Different Formats (P0)

**Feature**: [FS-398](./FEATURE.md)

**As a** user with JIRA sync enabled
**I want** duplicate comment prevention to work correctly
**So that** JIRA issues don't get flooded with duplicate comments on every sync

---

## Acceptance Criteria

- [x] **AC-US9-01**: `sync-coordinator.ts` JIRA idempotency check at line 700 handles the fact that `lastComment.body` returns an ADF object while `completionComment` is a plain text string — comparison must normalize formats

---

## Implementation

**Increment**: [0398-sync-integration-critical-fixes](../../../../../increments/0398-sync-integration-critical-fixes/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_
