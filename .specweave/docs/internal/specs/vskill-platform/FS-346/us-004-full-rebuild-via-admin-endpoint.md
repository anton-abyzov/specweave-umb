---
id: US-004
feature: FS-346
title: Full Rebuild via Admin Endpoint
status: complete
priority: P2
created: 2026-02-24
project: vskill-platform
---
# US-004: Full Rebuild via Admin Endpoint

**Feature**: [FS-346](./FEATURE.md)

platform admin
**I want** `POST /api/v1/admin/rebuild-index` to also rebuild the search index
**So that** I can trigger a full index rebuild for initial setup or recovery

---

## Acceptance Criteria

- [x] **AC-US4-01**: The existing `POST /api/v1/admin/rebuild-index` endpoint (in `src/app/api/v1/admin/rebuild-index/route.ts`) adds search index rebuild to its pipeline
- [x] **AC-US4-02**: Full rebuild queries all non-deprecated skills from Postgres, builds shard arrays, and writes each shard to KV
- [x] **AC-US4-03**: Response includes `searchIndexRebuilt: true` and `searchIndexShards: N` in the JSON body
- [x] **AC-US4-04**: Full rebuild writes the `search-index:meta` key with current timestamp and total skill count
- [x] **AC-US4-05**: Existing auth (X-Internal-Key OR SUPER_ADMIN JWT) applies -- no new auth requirements

---

## Implementation

**Increment**: [0346-edge-first-search-performance](../../../../../increments/0346-edge-first-search-performance/spec.md)

