---
increment: 0346-edge-first-search-performance
title: "Edge-First Search Performance"
type: feature
priority: P1
status: ready_for_review
created: 2026-02-24
structure: user-stories
test_mode: test-after
coverage_target: 80
---

# Feature: Edge-First Search Performance

## Problem Statement

The current search architecture in `src/lib/search.ts` makes a Postgres round-trip for every query (full-text tsvector + ILIKE fallback). At ~70k skills, Neon Postgres cold starts and cross-region latency produce P99 search times well above 200ms. The existing KV cache in SEARCH_CACHE_KV only caches individual query results (TTL 300s) and still misses on first access, novel queries, and after expiry. The 300ms debounce in SearchPalette masks this latency but makes the palette feel sluggish.

The goal is to move 95%+ of search queries to a sharded KV search index served at the edge (sub-50ms P99), with Postgres as a fallback for the remaining edge cases, and add client-side SWR caching so repeat searches are instant (zero network).

## Solution

Build a compact, sharded search index in Cloudflare KV. Each shard contains a JSON array of skill summaries (name, displayName, author, category, certTier, githubStars, repoUrl) keyed by a shard identifier (first character of the normalized skill name). The search API reads one or more shards from KV, performs prefix matching and category filtering in-memory at the edge, and falls back to Postgres when KV yields zero results. The index is incrementally updated via a queue message dispatched after each `publishSkill()` call, with full rebuild available via the existing admin endpoint. SearchPalette gains client-side SWR caching and a reduced 100ms debounce. Highlights are computed client-side via regex.

## User Stories

### US-001: Sharded KV Search Index Structure
**Project**: vskill-platform

**As a** platform operator
**I want** a compact, sharded search index stored in Cloudflare KV
**So that** search queries can be served from the edge without hitting Postgres

**Acceptance Criteria**:
- [x] **AC-US1-01**: Each shard is stored in SEARCH_CACHE_KV under key `search-index:shard:{char}` where `{char}` is the lowercased first character of the skill name (a-z, 0-9, or `_` for non-alphanumeric)
- [x] **AC-US1-02**: Each shard value is a JSON array of `SearchIndexEntry` objects: `{ name, displayName, author, category, certTier, githubStars, repoUrl }` -- descriptions are excluded to stay within KV size limits
- [x] **AC-US1-03**: At ~300-500 bytes/skill and ~70k skills, individual shards stay well under the 25MB KV value limit (largest shard ~2-3k skills)
- [x] **AC-US1-04**: A metadata key `search-index:meta` stores `{ shardCount, totalSkills, builtAt, version }` for cache validation
- [x] **AC-US1-05**: Index entries are sorted by `githubStars DESC` within each shard for deterministic ordering

---

### US-002: Edge Search Service
**Project**: vskill-platform

**As a** developer using the search API
**I want** `/api/v1/skills/search` to read from the KV search index first
**So that** search results are returned in sub-50ms at the edge

**Acceptance Criteria**:
- [x] **AC-US2-01**: New `searchSkillsEdge(options)` function in `src/lib/search.ts` reads the appropriate shard(s) from KV based on the query's first character
- [x] **AC-US2-02**: Prefix matching: each query term is matched as a prefix against `name` and `displayName` fields (case-insensitive), matching current tsquery behavior
- [x] **AC-US2-03**: Category filtering is applied in-memory after the KV read when `category` param is provided
- [x] **AC-US2-04**: Results are paginated in-memory: slice the filtered array for `page`/`limit` and compute `hasMore`
- [x] **AC-US2-05**: `highlight` field is empty string from edge results (highlighting is handled client-side per US-005)
- [x] **AC-US2-06**: The API route in `src/app/api/v1/skills/search/route.ts` calls `searchSkillsEdge()` first; on zero results, falls back to existing `searchSkills()` (Postgres path)
- [x] **AC-US2-07**: Response shape is identical to current `SearchResponse` -- no breaking changes to the API contract
- [x] **AC-US2-08**: Pagination is preserved in the API contract; "Load more" button in SearchPalette remains functional

---

### US-003: Incremental Index Updates via Queue
**Project**: vskill-platform

**As a** platform operator
**I want** the search index to update incrementally when skills are published, updated, or deprecated
**So that** the index stays current without full rebuilds

**Acceptance Criteria**:
- [x] **AC-US3-01**: After `publishSkill()` completes in `src/lib/submission-store.ts`, a `rebuild-search-index` queue message is dispatched containing `{ type: "rebuild_search_shard", skillName, action: "upsert" | "remove" }`
- [x] **AC-US3-02**: A new queue consumer handler processes `rebuild_search_shard` messages: reads the affected shard from KV, upserts or removes the skill entry, writes the shard back
- [x] **AC-US3-03**: The queue message is dispatched to the existing `SUBMISSION_QUEUE` (or a dedicated queue if type discrimination is cleaner) with a distinct `type` field to differentiate from `process_submission` messages
- [x] **AC-US3-04**: If the shard read/write fails, the message is retried via standard queue retry semantics
- [x] **AC-US3-05**: The metadata key `search-index:meta` is updated with `totalSkills` and `builtAt` after each incremental update

---

### US-004: Full Rebuild via Admin Endpoint
**Project**: vskill-platform

**As a** platform admin
**I want** `POST /api/v1/admin/rebuild-index` to also rebuild the search index
**So that** I can trigger a full index rebuild for initial setup or recovery

**Acceptance Criteria**:
- [x] **AC-US4-01**: The existing `POST /api/v1/admin/rebuild-index` endpoint (in `src/app/api/v1/admin/rebuild-index/route.ts`) adds search index rebuild to its pipeline
- [x] **AC-US4-02**: Full rebuild queries all non-deprecated skills from Postgres, builds shard arrays, and writes each shard to KV
- [x] **AC-US4-03**: Response includes `searchIndexRebuilt: true` and `searchIndexShards: N` in the JSON body
- [x] **AC-US4-04**: Full rebuild writes the `search-index:meta` key with current timestamp and total skill count
- [x] **AC-US4-05**: Existing auth (X-Internal-Key OR SUPER_ADMIN JWT) applies -- no new auth requirements

---

### US-005: Client-Side Highlighting
**Project**: vskill-platform

**As a** user searching for skills
**I want** matched query terms highlighted in search results
**So that** I can quickly identify why a result matched my query

**Acceptance Criteria**:
- [x] **AC-US5-01**: SearchPalette applies client-side highlighting via regex: each query term is wrapped in `<b>` tags within `displayName` text
- [x] **AC-US5-02**: Highlighting is case-insensitive and handles multi-word queries (each word highlighted independently)
- [x] **AC-US5-03**: When results come from Postgres fallback (which returns server-side `highlight`), the server highlight is used as-is
- [x] **AC-US5-04**: When results come from edge (empty `highlight`), client-side highlighting is applied to `displayName`

---

### US-006: Client-Side SWR Cache in SearchPalette
**Project**: vskill-platform

**As a** user re-opening the search palette
**I want** recent search results cached in-memory
**So that** re-typing a recent query returns results instantly (zero network)

**Acceptance Criteria**:
- [x] **AC-US6-01**: SearchPalette maintains an in-memory `Map<string, SearchResponse>` cache keyed by normalized query string
- [x] **AC-US6-02**: On typing a query that matches a cache entry, results are shown immediately from cache (no fetch)
- [x] **AC-US6-03**: A background revalidation fetch runs after showing cached results (stale-while-revalidate pattern)
- [x] **AC-US6-04**: Cache entries expire after 60 seconds (configurable constant)
- [x] **AC-US6-05**: Cache is cleared when the page navigates away (component unmount) -- no persistence to localStorage

---

### US-007: Reduced Debounce
**Project**: vskill-platform

**As a** user typing in the search palette
**I want** search results to appear faster
**So that** the palette feels responsive with edge-speed responses

**Acceptance Criteria**:
- [x] **AC-US7-01**: Debounce in SearchPalette reduced from 300ms to 150ms
- [x] **AC-US7-02**: Minimum 2-character query threshold is preserved
- [x] **AC-US7-03**: AbortController cancellation pattern is preserved for in-flight requests

## Non-Functional Requirements

- **NFR-01**: Edge search (KV path) P99 latency < 50ms for prefix queries
- **NFR-02**: Postgres fallback P99 latency remains < 200ms (unchanged)
- **NFR-03**: KV search index handles 95%+ of all search queries without hitting Postgres
- **NFR-04**: Individual KV shard values stay under 5MB (safety margin below 25MB limit)
- **NFR-05**: No breaking changes to `/api/v1/skills/search` response shape
- **NFR-06**: `npm run build` passes with no errors
- **NFR-07**: Existing search tests continue to pass; new tests added for edge path

## Out of Scope

- Vectorize / semantic search -- prefix matching covers current needs
- Full-text search within skill descriptions at the edge -- Postgres fallback handles this
- Per-category shard keys -- in-memory filtering after KV read is simpler and sufficient
- localStorage persistence of SWR cache -- in-memory only
- Infinite scroll in SearchPalette -- "Load more" button is retained
- Rate limiting beyond existing Cloudflare protections
- Real-time WebSocket push of index updates
- Multi-character shard keys (bigram sharding) -- single-char sharding is sufficient for 70k skills

## Technical Notes

### Index Format
```typescript
interface SearchIndexEntry {
  name: string;         // unique skill identifier (slug)
  displayName: string;  // human-readable name
  author: string;
  category: string;
  certTier: string;
  githubStars: number;
  repoUrl: string;
}
```

### Sharding Strategy
- Key: `search-index:shard:{char}` where `char` = first character of lowercased skill name
- 37 possible shards (a-z, 0-9, _)
- At 70k skills evenly distributed: ~1,900 entries/shard at ~500 bytes each = ~950KB/shard
- Worst case (skewed distribution): 5,000 entries/shard = ~2.5MB, well under 25MB

### Dependencies
- Increment 0324 (completed): Full-text search infrastructure (tsvector, GIN index, search.ts module)
- Increment 0344 (completed): SearchPalette hero input, Suspense streaming
- Cloudflare KV: Existing SEARCH_CACHE_KV binding (reused for search index shards)
- Cloudflare Queue: Existing SUBMISSION_QUEUE for dispatching index update messages

### Key Decisions (from interview)
1. **Sharded by first character** -- simple, predictable, keeps shards under KV limits
2. **Compact format** -- no descriptions in index, only fields needed for search + display
3. **Prefix matching only** -- matches current tsquery behavior; substring matching deferred to Postgres fallback
4. **Client-side highlights** -- simple regex in SearchPalette, no server-side ts_headline for edge path
5. **Queue message for index updates** -- decoupled from publishSkill(), uses existing queue infra
6. **Incremental updates** -- upsert/remove per skill, full rebuild admin-only
7. **Postgres fallback on zero results** -- safest transition path, KV handles 95%+
8. **In-memory category filtering** -- single KV read per shard, filter after read
9. **Client-side SWR** -- in-memory cache in SearchPalette, 60s TTL, stale-while-revalidate
10. **100ms debounce** -- down from 300ms, justified by sub-50ms edge responses
11. **Pagination preserved** -- API contract unchanged, internally served from single KV read

## Success Metrics

- P99 search latency < 50ms for edge path (measured via response timing headers)
- KV hit rate > 95% (Postgres fallback < 5% of queries)
- SearchPalette perceived latency < 200ms (150ms debounce + sub-50ms edge response)
- SWR cache hit rate > 30% for repeat queries within 60s window
- Zero regressions in existing search functionality
