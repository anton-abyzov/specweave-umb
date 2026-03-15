---
id: US-002
feature: FS-530
title: "Verify no excessive API calls during sync"
status: not_started
priority: P1
created: 2026-03-15
tldr: "**As a** SpecWeave user."
---

# US-002: Verify no excessive API calls during sync

**Feature**: [FS-530](./FEATURE.md)

**As a** SpecWeave user
**I want** sync operations to use minimal API calls
**So that** rate limits are not exhausted by normal operations

---

## Acceptance Criteria

- [ ] **AC-US2-01**: Given sync-living-docs runs for this increment, when checking rate limit before and after, then fewer than 100 GitHub API calls are used for an update (not creation) cycle
- [ ] **AC-US2-02**: Given the AC status hook fires, when checking JIRA API calls, then no more than 4 calls per user story are made (1 fetch + 1 update + 0-1 comment)

---

## Implementation

**Increment**: [0530-verify-full-sync-pipeline](../../../../../increments/0530-verify-full-sync-pipeline/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_
