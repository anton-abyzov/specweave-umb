---
id: US-002
feature: FS-529
title: "Eliminate redundant API calls in sync pipeline"
status: completed
priority: P1
created: 2026-03-15
tldr: "**As a** SpecWeave user."
---

# US-002: Eliminate redundant API calls in sync pipeline

**Feature**: [FS-529](./FEATURE.md)

**As a** SpecWeave user
**I want** sync operations to cache responses and batch requests
**So that** each sync session uses minimal API calls

---

## Acceptance Criteria

- [x] **AC-US2-01**: Given multiple `getIssue()` calls for the same issue within 30 seconds, when the second call is made, then the cached response is returned without an API call
- [x] **AC-US2-02**: Given DuplicateDetector creating a new issue, when Phase 1 search finds no duplicates, then Phase 3 verification search is skipped (1 API call instead of 3)
- [x] **AC-US2-03**: Given a sync operation starting, when remaining rate limit is below 100, then the operation is skipped with a warning log
- [x] **AC-US2-04**: Given AC checkbox sync with 4 user stories, when syncing checkboxes, then issue data is fetched in 1 batch GraphQL call instead of 4 individual calls

---

## Implementation

**Increment**: [0529-fix-github-api-rate-limit](../../../../../increments/0529-fix-github-api-rate-limit/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_
