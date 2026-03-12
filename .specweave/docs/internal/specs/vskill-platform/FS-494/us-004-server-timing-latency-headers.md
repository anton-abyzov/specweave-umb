---
id: US-004
feature: FS-494
title: "Server-Timing Latency Headers"
status: completed
priority: P1
created: "2026-03-11T00:00:00.000Z"
tldr: "**As a** platform operator."
project: vskill-platform
---

# US-004: Server-Timing Latency Headers

**Feature**: [FS-494](./FEATURE.md)

**As a** platform operator
**I want** Server-Timing headers on search responses showing edge and postgres latency
**So that** I can measure actual performance improvement in production via browser DevTools and CDN analytics

---

## Acceptance Criteria

- [x] **AC-US4-01**: The search response includes a `Server-Timing` header with `edge;dur=X` showing edge KV search duration in milliseconds
- [x] **AC-US4-02**: When Postgres is called, the Server-Timing header includes `postgres;dur=X` showing Postgres query duration
- [x] **AC-US4-03**: When Postgres is skipped, the Server-Timing header includes `postgres;desc="skipped"` with dur=0
- [x] **AC-US4-04**: The Server-Timing header includes `enrichment;dur=X` showing blocklist enrichment duration

---

## Implementation

**Increment**: [0494-search-performance-optimization](../../../../../increments/0494-search-performance-optimization/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-004**: Add Server-Timing headers for edge, postgres, and enrichment phases
