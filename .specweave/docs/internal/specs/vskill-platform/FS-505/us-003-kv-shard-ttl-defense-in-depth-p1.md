---
id: US-003
feature: FS-505
title: "KV Shard TTL Defense-in-Depth (P1)"
status: completed
priority: P1
created: 2026-03-12T00:00:00.000Z
tldr: "**As a** platform operator."
project: vskill-platform
---

# US-003: KV Shard TTL Defense-in-Depth (P1)

**Feature**: [FS-505](./FEATURE.md)

**As a** platform operator
**I want** KV search index entries to have a 7-day TTL
**So that** any stale entries that slip through (missed cleanup, race conditions) self-expire rather than persisting indefinitely

---

## Acceptance Criteria

- [x] **AC-US3-01**: Given `buildSearchIndex()` writes name shards and author shards to KV, when the shard data is written via `kv.put()`, then `expirationTtl: 604800` (7 days in seconds) is included in the put options
- [x] **AC-US3-02**: Given `updateSearchShard()` upserts a single entry into a shard, when the shard is written back to KV via `kv.put()`, then `expirationTtl: 604800` is included in the put options
- [x] **AC-US3-03**: Given the search index metadata key is written by `buildSearchIndex()`, when the meta is stored, then it also uses `expirationTtl: 604800`

---

## Implementation

**Increment**: [0505-fix-stale-search-404](../../../../../increments/0505-fix-stale-search-404/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-004**: Add expirationTtl to all KV shard writes in search-index.ts (TDD Red → Green → Refactor)
