---
id: US-005
feature: FS-404
title: "Pagination and Rate Limiting for JIRA API"
status: completed
priority: P1
created: 2026-03-02
tldr: "**As a** user with large JIRA projects,."
---

# US-005: Pagination and Rate Limiting for JIRA API

**Feature**: [FS-404](./FEATURE.md)

**As a** user with large JIRA projects,
**I want** API calls to handle pagination and rate limits correctly,
**So that** searches return complete results and bulk operations don't get throttled.

---

## Acceptance Criteria

- [x] **AC-US5-01**: All JQL search calls paginate through full result sets using `startAt`/`maxResults`
- [x] **AC-US5-02**: A shared HTTP client wrapper implements exponential backoff retry on 429 responses
- [x] **AC-US5-03**: Rate limit headers (`X-RateLimit-Remaining`, `Retry-After`) are respected
- [x] **AC-US5-04**: Pagination is tested with mock responses exceeding default page size

---

## Implementation

**Increment**: [0404-jira-sync-plugin-fixes](../../../../../increments/0404-jira-sync-plugin-fixes/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_
