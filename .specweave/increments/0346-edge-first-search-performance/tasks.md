---
increment: 0346-edge-first-search-performance
title: "Edge-First Search Performance"
by_user_story:
  US-001: [T-001, T-002]
  US-002: [T-003, T-004]
  US-003: [T-005, T-006, T-007]
  US-004: [T-008]
  US-005: [T-009]
  US-006: [T-010]
  US-007: [T-011]
---

# Tasks: Edge-First Search Performance

## User Story: US-001 - Sharded KV Search Index Structure

**Linked ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05
**Tasks**: 2 total, 2 completed

### T-001: Search index types and shard key utility

**User Story**: US-001
**Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-04
**Status**: [x] completed

**Test Plan**:
- **Given** a skill name starting with a letter, digit, or special char
- **When** `getShardKey(skillName)` is called
- **Then** it returns the correct shard key (lowercased first char, or `_` for non-alphanumeric)

**Test Cases**:
1. **Unit**: `src/lib/__tests__/search-index.test.ts`
   - testGetShardKeyLowercase(): "React-Audit" -> "r"
   - testGetShardKeyDigit(): "3d-scanner" -> "3"
   - testGetShardKeySpecialChar(): "@scope/tool" -> "_"
   - testGetShardKeyEmpty(): "" -> "_"
   - testSearchIndexEntryShape(): validates 7-field compact format (no description)
   - testSearchIndexMetaShape(): validates metadata key structure
   - **Coverage Target**: 95%

**Implementation**:
1. Add `SearchIndexEntry` and `SearchIndexMeta` interfaces to `src/lib/search-index.ts`
2. Implement `getShardKey(skillName: string): string`
3. Export `SHARD_KEY_PREFIX = "search-index:shard:"` and `META_KEY = "search-index:meta"` constants

---

### T-002: Build and update search index functions

**User Story**: US-001
**Satisfies ACs**: AC-US1-03, AC-US1-05
**Status**: [x] completed

**Test Plan**:
- **Given** a list of skills from Postgres
- **When** `buildSearchIndex(db, kv)` is called
- **Then** shards are written to KV sorted by githubStars DESC, and metadata key is updated

- **Given** a single skill entry and action "upsert"
- **When** `updateSearchShard(kv, entry, "upsert")` is called
- **Then** the entry is added/replaced in the correct shard, sorted by githubStars DESC

**Test Cases**:
1. **Unit**: `src/lib/__tests__/search-index.test.ts`
   - testBuildSearchIndexWritesShards(): builds from mock DB rows, verifies KV puts per shard
   - testBuildSearchIndexSortsByStars(): entries within shard sorted DESC
   - testBuildSearchIndexWritesMeta(): metadata key has shardCount, totalSkills, builtAt, version
   - testBuildSearchIndexEmptyDb(): handles 0 skills gracefully
   - testUpdateSearchShardUpsertNew(): adds new entry to shard
   - testUpdateSearchShardUpsertExisting(): replaces existing entry by name
   - testUpdateSearchShardRemove(): removes entry from shard
   - testUpdateSearchShardRemoveNonexistent(): no-op when entry not found
   - testUpdateSearchShardMaintainsSortOrder(): after upsert, shard is still sorted DESC
   - testUpdateSearchShardUpdatesMeta(): metadata totalSkills and builtAt updated
   - **Coverage Target**: 95%

**Implementation**:
1. Implement `buildSearchIndex(db, kv)` in `src/lib/search-index.ts`:
   - Query `db.skill.findMany({ where: { isDeprecated: false }, select: { name, displayName, author, category, certTier, githubStars, repoUrl } })`
   - Group by `getShardKey(name)`, sort each group by `githubStars DESC`
   - Write each shard to KV with key `search-index:shard:{char}`
   - Write metadata to `search-index:meta`
2. Implement `updateSearchShard(kv, entry, action)`:
   - Read shard from KV, parse, upsert/remove, re-sort, write back
   - Update metadata

---

## User Story: US-002 - Edge Search Service

**Linked ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04, AC-US2-05, AC-US2-06, AC-US2-07, AC-US2-08
**Tasks**: 2 total, 2 completed

### T-003: Edge search function (searchSkillsEdge)

**User Story**: US-002
**Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04, AC-US2-05, AC-US2-07, AC-US2-08
**Status**: [x] completed

**Test Plan**:
- **Given** a KV shard with skills starting with "r"
- **When** `searchSkillsEdge({ query: "react" })` is called
- **Then** returns skills where name or displayName starts with "react" (case-insensitive), with empty highlight, paginated

**Test Cases**:
1. **Unit**: `src/lib/search.test.ts` (new describe block)
   - testEdgePrefixMatchSingleWord(): "react" matches "react-security-audit"
   - testEdgePrefixMatchCaseInsensitive(): "React" matches "react-audit"
   - testEdgeMultiWordQuery(): "code rev" matches "code-review-tool"
   - testEdgeCategoryFilter(): filters results by category in-memory
   - testEdgePagination(): page=2, limit=5 slices correctly, hasMore computed
   - testEdgeHighlightEmpty(): highlight field is empty string for all edge results
   - testEdgeResponseShape(): matches SearchResponse interface exactly
   - testEdgeKvMiss(): returns empty results when shard is null (triggers fallback)
   - testEdgeKvUnavailable(): gracefully returns empty on getKv() failure
   - testEdgeNoMatchInShard(): returns empty results for query with no prefix matches
   - **Coverage Target**: 90%

**Implementation**:
1. Add `searchSkillsEdge(options: SearchOptions): Promise<SearchResponse>` to `src/lib/search.ts`
2. Read shard from KV using `getShardKey(query.split(/\s+/)[0])`
3. Filter entries where ALL query words match as prefix of `name` or `displayName`
4. Apply category filter if provided
5. Paginate: slice for `page`/`limit`, compute `hasMore`
6. Map to `SearchResult[]` with `highlight: ""`

---

### T-004: API route edge-first with Postgres fallback

**User Story**: US-002
**Satisfies ACs**: AC-US2-06, AC-US2-07, AC-US2-08
**Status**: [x] completed

**Test Plan**:
- **Given** edge search returns results
- **When** GET /api/v1/skills/search?q=react is called
- **Then** response comes from edge path, no Postgres call

- **Given** edge search returns 0 results
- **When** GET /api/v1/skills/search?q=xyzrare is called
- **Then** Postgres fallback is invoked, results come from searchSkills()

**Test Cases**:
1. **Unit**: `src/app/api/v1/skills/search/__tests__/route.test.ts`
   - testEdgeFirstHappy(): edge returns results, searchSkills not called
   - testFallbackOnZeroEdgeResults(): edge returns 0, searchSkills called
   - testSearchSourceHeaderEdge(): X-Search-Source is "edge" for KV results
   - testSearchSourceHeaderPostgres(): X-Search-Source is "postgres" for fallback
   - testRetryOnlyForPostgres(): retry loop only applies to Postgres path
   - testResponseShapeUnchanged(): contract matches existing SearchResponse
   - **Coverage Target**: 90%

**Implementation**:
1. Modify `src/app/api/v1/skills/search/route.ts`:
   - Import `searchSkillsEdge` from `@/lib/search`
   - Call `searchSkillsEdge()` first
   - If `results.length > 0`, return with `X-Search-Source: edge` header
   - If `results.length === 0`, fall through to existing retry loop with `searchSkills()`
   - Add `X-Search-Source: postgres` header on fallback responses

---

## User Story: US-003 - Incremental Index Updates via Queue

**Linked ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04, AC-US3-05
**Tasks**: 3 total, 3 completed

### T-005: Queue message type and dispatch from publishSkill

**User Story**: US-003
**Satisfies ACs**: AC-US3-01, AC-US3-03
**Status**: [x] completed

**Test Plan**:
- **Given** a skill is published via publishSkill()
- **When** the DB upsert succeeds
- **Then** a `rebuild_search_shard` message is dispatched to SUBMISSION_QUEUE

**Test Cases**:
1. **Unit**: `src/lib/__tests__/submission-store.test.ts` (extended)
   - testPublishSkillDispatchesSearchIndexMessage(): after upsert, queue.send() called with correct type and entry
   - testPublishSkillQueueMessageFormat(): message has type, skillName, action, entry fields
   - testPublishSkillQueueFailureNonFatal(): queue dispatch failure does not fail publishSkill()
   - **Coverage Target**: 90%

**Implementation**:
1. Add `SearchShardQueueMessage` to `src/lib/queue/types.ts` as a union member:
   ```typescript
   export type QueueMessage = SubmissionQueueMessage | SearchShardQueueMessage;
   ```
2. Update `CloudflareEnv.SUBMISSION_QUEUE` type in `src/lib/env.d.ts` to accept the union
3. Modify `publishSkill()` in `src/lib/submission-store.ts`:
   - After `db.skill.upsert()`, dispatch queue message (best-effort, catch errors)
   - Build `SearchIndexEntry` from the upserted data
   - Call `queue.send({ type: "rebuild_search_shard", skillName: slug, action: "upsert", entry })`

---

### T-006: Search index queue consumer

**User Story**: US-003
**Satisfies ACs**: AC-US3-02, AC-US3-04, AC-US3-05
**Status**: [x] completed

**Test Plan**:
- **Given** a `rebuild_search_shard` message with action "upsert"
- **When** the consumer processes it
- **Then** the shard is read from KV, entry upserted, shard written back, metadata updated

**Test Cases**:
1. **Unit**: `src/lib/queue/__tests__/search-index-consumer.test.ts`
   - testHandleUpsert(): reads shard, adds entry, writes back sorted
   - testHandleRemove(): reads shard, removes entry by name, writes back
   - testHandleUpsertToEmptyShard(): creates new shard with single entry
   - testMetadataUpdated(): search-index:meta updated with new totalSkills and builtAt
   - testKvReadFailureThrows(): consumer throws (triggers queue retry)
   - testKvWriteFailureThrows(): consumer throws (triggers queue retry)
   - **Coverage Target**: 90%

**Implementation**:
1. Create `src/lib/queue/search-index-consumer.ts`:
   ```typescript
   export async function handleSearchIndexUpdate(
     message: SearchShardQueueMessage,
     kv: QueueKV,
   ): Promise<void>
   ```
2. Call `updateSearchShard(kv, message.entry, message.action)` from `search-index.ts`
3. Errors propagate to trigger queue retry semantics

---

### T-007: Consumer routing for search index messages

**User Story**: US-003
**Satisfies ACs**: AC-US3-03
**Status**: [x] completed

**Test Plan**:
- **Given** a batch with a `rebuild_search_shard` message
- **When** the consumer processes the batch
- **Then** it routes to `handleSearchIndexUpdate()` instead of `processSubmission()`

**Test Cases**:
1. **Unit**: `src/lib/queue/__tests__/consumer.test.ts` (extended)
   - testRoutesSearchIndexMessage(): type "rebuild_search_shard" goes to search handler
   - testRoutesSubmissionMessage(): type "process_submission" still goes to processSubmission
   - testMixedBatch(): batch with both types routes each correctly
   - **Coverage Target**: 85%

**Implementation**:
1. Modify `src/lib/queue/consumer.ts`:
   - Import `handleSearchIndexUpdate` from `./search-index-consumer`
   - In the batch loop, check `message.body.type`:
     - `"process_submission"` -> existing `processSubmission()` path
     - `"rebuild_search_shard"` -> `handleSearchIndexUpdate(message.body, env.SEARCH_CACHE_KV)`

---

## User Story: US-004 - Full Rebuild via Admin Endpoint

**Linked ACs**: AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-04, AC-US4-05
**Tasks**: 1 total, 1 completed

### T-008: Extend rebuild-index endpoint with search index rebuild

**User Story**: US-004
**Satisfies ACs**: AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-04, AC-US4-05
**Status**: [x] completed

**Test Plan**:
- **Given** an admin calls POST /api/v1/admin/rebuild-index with valid auth
- **When** the endpoint runs
- **Then** response includes searchIndexRebuilt: true, searchIndexShards, searchIndexTotalSkills

**Test Cases**:
1. **Unit**: `src/app/api/v1/admin/rebuild-index/__tests__/route.test.ts`
   - testRebuildIndexIncludesSearchIndex(): response has searchIndexRebuilt field
   - testRebuildIndexSearchShardCount(): searchIndexShards matches number of non-empty shards
   - testRebuildIndexSearchMetaWritten(): KV put called for search-index:meta
   - testRebuildIndexExistingAuthStillWorks(): X-Internal-Key auth path unchanged
   - testRebuildIndexSearchFailureNonFatal(): search index failure does not fail the whole endpoint
   - **Coverage Target**: 85%

**Implementation**:
1. Modify `src/app/api/v1/admin/rebuild-index/route.ts`:
   - Import `buildSearchIndex` from `@/lib/search-index`
   - After existing backfill logic, call `buildSearchIndex(db, searchKv)`
   - Get `searchKv` from `getCloudflareContext().env.SEARCH_CACHE_KV`
   - Add `searchIndexRebuilt`, `searchIndexShards`, `searchIndexTotalSkills` to response
   - Wrap in try/catch so search index failure does not break existing functionality

---

## User Story: US-005 - Client-Side Highlighting

**Linked ACs**: AC-US5-01, AC-US5-02, AC-US5-03, AC-US5-04
**Tasks**: 1 total, 1 completed

### T-009: Client-side highlighting in SearchPalette

**User Story**: US-005
**Satisfies ACs**: AC-US5-01, AC-US5-02, AC-US5-03, AC-US5-04
**Status**: [x] completed

**Test Plan**:
- **Given** a search result with empty highlight (edge path)
- **When** SearchPalette renders the result
- **Then** `displayName` has query terms wrapped in `<b>` tags

- **Given** a search result with server-provided highlight (Postgres path)
- **When** SearchPalette renders the result
- **Then** the server highlight is used as-is

**Test Cases**:
1. **Unit**: `src/app/components/__tests__/SearchPalette.test.tsx` (extended)
   - testHighlightMatchesSingleWord(): "react" in "React Security Audit" -> "<b>React</b> Security Audit"
   - testHighlightMatchesMultiWord(): "react sec" highlights both words independently
   - testHighlightMatchesCaseInsensitive(): "REACT" matches "react" in displayName
   - testHighlightServerProvided(): server highlight used when non-empty
   - testHighlightClientApplied(): client highlight applied when highlight is empty
   - testHighlightEscapesHtml(): special chars in displayName are escaped before wrapping
   - **Coverage Target**: 90%

**Implementation**:
1. Add `highlightMatches(text: string, query: string): string` utility in SearchPalette.tsx
   - Escape HTML special chars in `text`
   - Split query into words, build regex for each, wrap matches in `<b>` tags
2. In result rendering, use `item.highlight || highlightMatches(item.label, query)`

---

## User Story: US-006 - Client-Side SWR Cache in SearchPalette

**Linked ACs**: AC-US6-01, AC-US6-02, AC-US6-03, AC-US6-04, AC-US6-05
**Tasks**: 1 total, 1 completed

### T-010: In-memory SWR cache in SearchPalette

**User Story**: US-006
**Satisfies ACs**: AC-US6-01, AC-US6-02, AC-US6-03, AC-US6-04, AC-US6-05
**Status**: [x] completed

**Test Plan**:
- **Given** a query "react" was fetched 10 seconds ago
- **When** the user types "react" again
- **Then** cached results are shown instantly, and a background revalidation fetch runs

- **Given** a cache entry is older than 60 seconds
- **When** the user types the same query
- **Then** it is treated as a cache miss (fresh fetch, no stale data shown)

**Test Cases**:
1. **Unit**: `src/app/components/__tests__/SearchPalette.test.tsx` (extended)
   - testSwrCacheHit(): second identical query shows results without fetch
   - testSwrBackgroundRevalidation(): after cache hit, a background fetch is made
   - testSwrCacheExpiry(): entries older than 60s are treated as miss
   - testSwrCacheClearedOnUnmount(): cache is empty after component unmounts
   - testSwrCacheKeyNormalized(): "React" and "react" use same cache key
   - **Coverage Target**: 85%

**Implementation**:
1. Add `useRef<Map<string, { data: SearchResponse; timestamp: number }>>()` to SearchPalette
2. In the debounced search effect:
   - Check cache: if entry exists and age < 60s, set results from cache, then fetch in background
   - On fetch response, update cache entry and results
3. Clear cache on unmount via cleanup function

---

## User Story: US-007 - Reduced Debounce

**Linked ACs**: AC-US7-01, AC-US7-02, AC-US7-03
**Tasks**: 1 total, 1 completed

### T-011: Reduce debounce from 300ms to 150ms

**User Story**: US-007
**Satisfies ACs**: AC-US7-01, AC-US7-02, AC-US7-03
**Status**: [x] completed

**Test Plan**:
- **Given** a user types "re" in the search palette
- **When** 150ms elapses after last keystroke
- **Then** a fetch is triggered (not 300ms)

**Test Cases**:
1. **Unit**: `src/app/components/__tests__/SearchPalette.test.tsx` (extended)
   - testDebounce150ms(): fetch fires after 150ms, not sooner
   - testMinQueryLength2Preserved(): single-char query does not trigger fetch
   - testAbortControllerPreserved(): typing replaces previous fetch with AbortController cancel
   - **Coverage Target**: 85%

**Implementation**:
1. Change `setTimeout` delay in SearchPalette debounced search effect from `300` to `150`
2. Extract debounce constant: `const SEARCH_DEBOUNCE_MS = 150;`
