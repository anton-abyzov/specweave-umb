---
id: US-004
feature: FS-319
title: GitHub Code Search with Size Sharding
status: complete
priority: P1
created: 2026-02-22
project: vskill-platform
external:
  github:
    issue: 1268
    url: https://github.com/anton-abyzov/specweave/issues/1268
---
# US-004: GitHub Code Search with Size Sharding

**Feature**: [FS-319](./FEATURE.md)

platform operator
**I want** GitHub Code Search to use size-based sharding
**So that** I bypass the 1,000-result cap and discover 5-20x more repos

---

## Acceptance Criteria

- [x] **AC-US4-01**: Each code search query is split into size shards (e.g., `size:0..100`, `size:101..300`, `size:301..500`, etc.)
- [x] **AC-US4-02**: Size ranges are fine-grained enough that each shard returns <1000 results
- [x] **AC-US4-03**: Sharding is configurable — shard boundaries can be tuned based on observed distribution
- [x] **AC-US4-04**: Token rotation works across all sharded queries
- [x] **AC-US4-05**: Adaptive delay respects rate limits (9 req/min for code search)

---

## Implementation

**Increment**: [0319-discovery-scale-up](../../../../../increments/0319-discovery-scale-up/spec.md)

