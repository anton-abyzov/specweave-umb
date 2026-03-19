---
id: US-008
feature: FS-622
title: Client-Side Caching (P3)
status: completed
priority: P1
created: 2026-03-19T00:00:00.000Z
tldr: "**As a** skill developer."
project: vskill
external_tools:
  jira:
    key: SWE2E-721
  ado:
    id: 1560
---

# US-008: Client-Side Caching (P3)

**Feature**: [FS-622](./FEATURE.md)

**As a** skill developer
**I want** fast panel switches without unnecessary API calls
**So that** the dashboard feels responsive and doesn't waste resources

---

## Acceptance Criteria

- [x] **AC-US8-01**: SWR cache with 30-second TTL for API responses
- [x] **AC-US8-02**: Duplicate in-flight requests are deduplicated (same key returns same promise)
- [x] **AC-US8-03**: Cache is invalidated by SSE data events from US-007
- [x] **AC-US8-04**: StatsPanel, HistoryPanel, LeaderboardPanel use SWR instead of raw useEffect+fetch

---

## Implementation

**Increment**: [0622-dashboard-cost-realtime-redesign](../../../../../increments/0622-dashboard-cost-realtime-redesign/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_
