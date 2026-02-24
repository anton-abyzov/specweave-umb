---
id: US-001
feature: FS-346
title: Sharded KV Search Index Structure
status: complete
priority: P2
created: 2026-02-24
project: vskill-platform
---
# US-001: Sharded KV Search Index Structure

**Feature**: [FS-346](./FEATURE.md)

platform operator
**I want** a compact, sharded search index stored in Cloudflare KV
**So that** search queries can be served from the edge without hitting Postgres

---

## Acceptance Criteria

- [x] **AC-US1-01**: Each shard is stored in SEARCH_CACHE_KV under key `search-index:shard:{char}` where `{char}` is the lowercased first character of the skill name (a-z, 0-9, or `_` for non-alphanumeric)
- [x] **AC-US1-02**: Each shard value is a JSON array of `SearchIndexEntry` objects: `{ name, displayName, author, category, certTier, githubStars, repoUrl }` -- descriptions are excluded to stay within KV size limits
- [x] **AC-US1-03**: At ~300-500 bytes/skill and ~70k skills, individual shards stay well under the 25MB KV value limit (largest shard ~2-3k skills)
- [x] **AC-US1-04**: A metadata key `search-index:meta` stores `{ shardCount, totalSkills, builtAt, version }` for cache validation
- [x] **AC-US1-05**: Index entries are sorted by `githubStars DESC` within each shard for deterministic ordering

---

## Implementation

**Increment**: [0346-edge-first-search-performance](../../../../../increments/0346-edge-first-search-performance/spec.md)

