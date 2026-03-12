---
id: US-003
feature: FS-494
title: "Improved CDN and Client Cache Headers"
status: completed
priority: P1
created: "2026-03-11T00:00:00.000Z"
tldr: "**As a** user performing repeated or popular searches."
project: vskill-platform
---

# US-003: Improved CDN and Client Cache Headers

**Feature**: [FS-494](./FEATURE.md)

**As a** user performing repeated or popular searches
**I want** search responses cached longer at the CDN edge and on my client
**So that** repeat queries are served instantly from cache

---

## Acceptance Criteria

- [x] **AC-US3-01**: The search endpoint returns `Cache-Control: public, max-age=10, s-maxage=60, stale-while-revalidate=300` (up from s-maxage=30, adding stale-while-revalidate)
- [x] **AC-US3-02**: The frontend SWR cache TTL is 60 seconds (up from 10 seconds)
- [x] **AC-US3-03**: Stale-while-revalidate allows the CDN to serve stale content for up to 300s while fetching fresh data in the background

---

## Implementation

**Increment**: [0494-search-performance-optimization](../../../../../increments/0494-search-performance-optimization/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-003**: Update Cache-Control header and frontend SWR TTL
