---
id: US-005
feature: FS-494
title: "Preload Trending Skills on Palette Open"
status: completed
priority: P1
created: "2026-03-11T00:00:00.000Z"
tldr: "**As a** user opening the search palette."
project: vskill-platform
---

# US-005: Preload Trending Skills on Palette Open

**Feature**: [FS-494](./FEATURE.md)

**As a** user opening the search palette
**I want** to see popular/trending skills immediately before I start typing
**So that** I can discover and navigate to popular skills with zero wait time

---

## Acceptance Criteria

- [x] **AC-US5-01**: When the search palette opens and the query is empty, then 10 trending skills are displayed in the SKILLS group
- [x] **AC-US5-02**: Trending skills are fetched from the existing KV-backed home stats endpoint (`/api/v1/stats` or equivalent `getHomeStats()` data)
- [x] **AC-US5-03**: Trending skills are displayed identically to search results (same row layout, tier badges, star counts) with no special "trending" indicator
- [x] **AC-US5-04**: Once the user starts typing (>= 2 chars), the trending skills are replaced by actual search results
- [x] **AC-US5-05**: Trending skills data is cached on the client and does not re-fetch on every palette open (cache for the session or with a reasonable TTL)

---

## Implementation

**Increment**: [0494-search-performance-optimization](../../../../../increments/0494-search-performance-optimization/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-005**: Fetch and display trending skills when search palette opens
