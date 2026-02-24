---
id: US-005
feature: FS-346
title: Client-Side Highlighting
status: complete
priority: P2
created: 2026-02-24
project: vskill-platform
---
# US-005: Client-Side Highlighting

**Feature**: [FS-346](./FEATURE.md)

user searching for skills
**I want** matched query terms highlighted in search results
**So that** I can quickly identify why a result matched my query

---

## Acceptance Criteria

- [x] **AC-US5-01**: SearchPalette applies client-side highlighting via regex: each query term is wrapped in `<b>` tags within `displayName` text
- [x] **AC-US5-02**: Highlighting is case-insensitive and handles multi-word queries (each word highlighted independently)
- [x] **AC-US5-03**: When results come from Postgres fallback (which returns server-side `highlight`), the server highlight is used as-is
- [x] **AC-US5-04**: When results come from edge (empty `highlight`), client-side highlighting is applied to `displayName`

---

## Implementation

**Increment**: [0346-edge-first-search-performance](../../../../../increments/0346-edge-first-search-performance/spec.md)

