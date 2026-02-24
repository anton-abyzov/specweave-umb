---
id: US-002
feature: FS-346
title: Edge Search Service
status: complete
priority: P2
created: 2026-02-24
project: vskill-platform
---
# US-002: Edge Search Service

**Feature**: [FS-346](./FEATURE.md)

developer using the search API
**I want** `/api/v1/skills/search` to read from the KV search index first
**So that** search results are returned in sub-50ms at the edge

---

## Acceptance Criteria

- [x] **AC-US2-01**: New `searchSkillsEdge(options)` function in `src/lib/search.ts` reads the appropriate shard(s) from KV based on the query's first character
- [x] **AC-US2-02**: Prefix matching: each query term is matched as a prefix against `name` and `displayName` fields (case-insensitive), matching current tsquery behavior
- [x] **AC-US2-03**: Category filtering is applied in-memory after the KV read when `category` param is provided
- [x] **AC-US2-04**: Results are paginated in-memory: slice the filtered array for `page`/`limit` and compute `hasMore`
- [x] **AC-US2-05**: `highlight` field is empty string from edge results (highlighting is handled client-side per US-005)
- [x] **AC-US2-06**: The API route in `src/app/api/v1/skills/search/route.ts` calls `searchSkillsEdge()` first; on zero results, falls back to existing `searchSkills()` (Postgres path)
- [x] **AC-US2-07**: Response shape is identical to current `SearchResponse` -- no breaking changes to the API contract
- [x] **AC-US2-08**: Pagination is preserved in the API contract; "Load more" button in SearchPalette remains functional

---

## Implementation

**Increment**: [0346-edge-first-search-performance](../../../../../increments/0346-edge-first-search-performance/spec.md)

