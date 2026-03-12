---
id: US-001
feature: FS-494
title: "Edge-First Search with Conditional Postgres Fallback"
status: completed
priority: P1
created: "2026-03-11T00:00:00.000Z"
tldr: "**As a** user searching for skills."
project: vskill-platform
---

# US-001: Edge-First Search with Conditional Postgres Fallback

**Feature**: [FS-494](./FEATURE.md)

**As a** user searching for skills
**I want** search results returned as fast as possible
**So that** I get near-instant results without waiting for unnecessary database queries

---

## Acceptance Criteria

- [x] **AC-US1-01**: Given edge KV returns >= fetchLimit results, when a search query is executed, then Postgres is NOT called and results are returned from edge only
- [x] **AC-US1-02**: Given edge KV returns < fetchLimit results, when a search query is executed, then Postgres is called to fill gaps and results are merged as before
- [x] **AC-US1-03**: Given edge KV fails entirely, when a search query is executed, then Postgres is called as full fallback and the response includes results
- [x] **AC-US1-04**: The response `X-Search-Source` header accurately reflects which sources were used ("edge", "postgres", or "edge+postgres")

---

## Implementation

**Increment**: [0494-search-performance-optimization](../../../../../increments/0494-search-performance-optimization/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-001**: Implement edge-first conditional Postgres fallback in route.ts
