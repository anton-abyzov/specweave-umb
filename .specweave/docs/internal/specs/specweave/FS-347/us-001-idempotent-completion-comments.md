---
id: US-001
feature: FS-347
title: "Idempotent Completion Comments"
status: completed
priority: P1
created: 2026-02-25
tldr: "**As a** developer using SpecWeave with GitHub/JIRA/ADO sync
**I want** completion comments to be posted exactly once per user story
**So that** my issue threads are clean and professional."
---

# US-001: Idempotent Completion Comments

**Feature**: [FS-347](./FEATURE.md)

**As a** developer using SpecWeave with GitHub/JIRA/ADO sync
**I want** completion comments to be posted exactly once per user story
**So that** my issue threads are clean and professional

---

## Acceptance Criteria

- [x] **AC-US1-01**: GitHub completion comments use `getLastComment()` dedup before posting (mirrors JIRA pattern)
- [x] **AC-US1-02**: ADO client has a `getLastComment()` method for idempotency checks
- [x] **AC-US1-03**: ADO completion comments use `getLastComment()` dedup before posting
- [x] **AC-US1-04**: `syncIncrementClosure()` uses a filesystem lock per increment to prevent concurrent execution
- [x] **AC-US1-05**: Existing JIRA dedup continues to work unchanged
- [x] **AC-US1-06**: Unit tests cover dedup logic for GitHub and ADO paths

---

## Implementation

**Increment**: [0347-fix-duplicate-sync-comments](../../../../../increments/0347-fix-duplicate-sync-comments/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_
