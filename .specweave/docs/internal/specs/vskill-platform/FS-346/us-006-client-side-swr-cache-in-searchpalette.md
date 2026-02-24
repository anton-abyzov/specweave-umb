---
id: US-006
feature: FS-346
title: Client-Side SWR Cache in SearchPalette
status: complete
priority: P2
created: 2026-02-24
project: vskill-platform
---
# US-006: Client-Side SWR Cache in SearchPalette

**Feature**: [FS-346](./FEATURE.md)

user re-opening the search palette
**I want** recent search results cached in-memory
**So that** re-typing a recent query returns results instantly (zero network)

---

## Acceptance Criteria

- [x] **AC-US6-01**: SearchPalette maintains an in-memory `Map<string, SearchResponse>` cache keyed by normalized query string
- [x] **AC-US6-02**: On typing a query that matches a cache entry, results are shown immediately from cache (no fetch)
- [x] **AC-US6-03**: A background revalidation fetch runs after showing cached results (stale-while-revalidate pattern)
- [x] **AC-US6-04**: Cache entries expire after 60 seconds (configurable constant)
- [x] **AC-US6-05**: Cache is cleared when the page navigates away (component unmount) -- no persistence to localStorage

---

## Implementation

**Increment**: [0346-edge-first-search-performance](../../../../../increments/0346-edge-first-search-performance/spec.md)

