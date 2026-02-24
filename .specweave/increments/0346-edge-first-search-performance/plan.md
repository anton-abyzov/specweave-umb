# Implementation Plan: Edge-First Search Performance

## Overview

Replace the Postgres-dependent search path with a sharded KV search index served entirely at the Cloudflare edge. The current architecture (SearchPalette -> API route -> `searchSkills()` -> Neon Postgres tsvector + ILIKE) suffers from cold start latency (574ms-6s). The new architecture pre-computes a compact search index in SEARCH_CACHE_KV, sharded by the first character of the skill name, and performs prefix matching and pagination entirely in-memory at the Worker. Postgres becomes a fallback-only path for zero-result queries. Client-side SWR caching and a reduced debounce complete the perceived-latency improvements.

## Architecture

### System Data Flow

```
CURRENT FLOW (every query hits Postgres):
  SearchPalette -> fetch(/api/v1/skills/search)
    -> route.ts -> searchSkills() -> KV cache check
    -> MISS -> Neon Postgres ($queryRaw tsvector + ILIKE fallback)
    -> KV cache write -> JSON response

NEW FLOW (95%+ of queries stay at edge):
  SearchPalette (in-memory SWR cache check)
    -> MISS -> fetch(/api/v1/skills/search)
      -> route.ts -> searchSkillsEdge() -> KV shard read
      -> in-memory prefix match + category filter + paginate
      -> JSON response (P99 < 50ms)

  FALLBACK (edge returns 0 results):
    -> searchSkills() -> Neon Postgres (existing path, unchanged)

  INDEX MAINTENANCE:
    publishSkill() -> SUBMISSION_QUEUE message {type: "rebuild_search_shard"}
    -> consumer.ts routes to handleSearchIndexUpdate()
    -> reads shard from KV, upserts/removes entry, writes back

    Admin: POST /api/v1/admin/rebuild-index
    -> full rebuild: Prisma query all skills -> build all shards -> write all to KV
```

### Components

| Component | File | Purpose |
|-----------|------|---------|
| **SearchIndexEntry** | `src/lib/search.ts` | Type definition for compact index entry (7 fields, no description) |
| **searchSkillsEdge()** | `src/lib/search.ts` | Edge search: KV shard read, prefix match, filter, paginate |
| **buildSearchIndex()** | `src/lib/search-index.ts` | Full rebuild: query Postgres, build all shards, write to KV |
| **updateSearchShard()** | `src/lib/search-index.ts` | Incremental update: read shard, upsert/remove single entry, write back |
| **handleSearchIndexUpdate()** | `src/lib/queue/search-index-consumer.ts` | Queue consumer for `rebuild_search_shard` messages |
| **SearchShardQueueMessage** | `src/lib/queue/types.ts` | Queue message type for index updates |
| **highlightMatches()** | `src/app/components/SearchPalette.tsx` | Client-side regex highlighting utility |
| **SWR cache** | `src/app/components/SearchPalette.tsx` | In-memory Map<string, {data, timestamp}> for stale-while-revalidate |
| **route.ts** (modified) | `src/app/api/v1/skills/search/route.ts` | Calls `searchSkillsEdge()` first, falls back to `searchSkills()` |
| **consumer.ts** (modified) | `src/lib/queue/consumer.ts` | Routes `rebuild_search_shard` messages to new handler |
| **submission-store.ts** (modified) | `src/lib/submission-store.ts` | Dispatches queue message after `publishSkill()` |
| **rebuild-index/route.ts** (modified) | `src/app/api/v1/admin/rebuild-index/route.ts` | Adds full search index rebuild to pipeline |

### Data Model

#### SearchIndexEntry (KV shard value)

```typescript
interface SearchIndexEntry {
  name: string;         // unique skill slug (e.g., "react-security-audit")
  displayName: string;  // human-readable (e.g., "React Security Audit")
  author: string;       // (e.g., "anthropic")
  category: string;     // (e.g., "security")
  certTier: string;     // "SCANNED" | "VERIFIED" | "CERTIFIED"
  githubStars: number;  // (e.g., 3240)
  repoUrl: string;      // (e.g., "https://github.com/anthropics/skills")
}
```

**Estimated size**: ~200-400 bytes/entry when JSON-serialized (shorter than the 300-500 byte spec estimate because field names are short).

#### SearchIndexMeta (KV metadata key)

```typescript
interface SearchIndexMeta {
  shardCount: number;     // number of shards written (up to 37)
  totalSkills: number;    // total entries across all shards
  builtAt: string;        // ISO timestamp of last build/update
  version: number;        // schema version (1)
}
```

#### KV Key Layout

```
search-index:shard:a   ->  SearchIndexEntry[]  (all skills starting with 'a')
search-index:shard:b   ->  SearchIndexEntry[]
...
search-index:shard:z   ->  SearchIndexEntry[]
search-index:shard:0   ->  SearchIndexEntry[]
...
search-index:shard:9   ->  SearchIndexEntry[]
search-index:shard:_   ->  SearchIndexEntry[]  (non-alphanumeric first chars)
search-index:meta      ->  SearchIndexMeta
```

All keys use the existing `SEARCH_CACHE_KV` binding. No new KV namespace needed. Index keys have no TTL (persistent until overwritten). The existing per-query cache keys (`search:{query}:{category}:{page}`) coexist without conflict.

#### Queue Message Type

```typescript
interface SearchShardQueueMessage {
  type: "rebuild_search_shard";
  skillName: string;
  action: "upsert" | "remove";
  // Skill data for upsert (avoids a DB read in the consumer)
  entry?: SearchIndexEntry;
}
```

Added to the existing `SubmissionQueueMessage` union in `src/lib/queue/types.ts` via a discriminated union on the `type` field.

### API Contracts

#### `GET /api/v1/skills/search` (UNCHANGED contract)

No changes to request params or response shape. Internal routing changes only:

```
Request: ?q=react&category=security&page=1&limit=10
Response: {
  results: SearchResult[],
  pagination: { page, limit, hasMore }
}
```

**Internal change**: route.ts calls `searchSkillsEdge()` first. On zero results, falls back to `searchSkills()` (Postgres). The retry-on-timeout loop is preserved for the Postgres fallback path only.

#### `POST /api/v1/admin/rebuild-index` (EXTENDED)

**New response fields** added to existing response:

```json
{
  "ok": true,
  "rebuilt": 1234,
  "errors": 0,
  "orphanedAliases": 5,
  "prismaBackfilled": 1234,
  "searchIndexRebuilt": true,
  "searchIndexShards": 27,
  "searchIndexTotalSkills": 1234
}
```

## Technology Stack

- **Runtime**: Cloudflare Workers (via OpenNext adapter, existing)
- **KV**: Cloudflare KV (existing SEARCH_CACHE_KV binding)
- **Queue**: Cloudflare Queues (existing SUBMISSION_QUEUE)
- **Database**: Neon Postgres via Prisma (existing, fallback-only for search)
- **Framework**: Next.js 15 (existing)
- **Testing**: Vitest with vi.hoisted() mocks (existing ESM pattern)

**No new dependencies or bindings required.**

## Architecture Decisions

### AD-1: Reuse SEARCH_CACHE_KV for index shards

**Decision**: Store search index shards in the existing SEARCH_CACHE_KV namespace alongside the per-query cache entries.

**Rationale**: Adding a new KV namespace requires a wrangler.jsonc change, a new binding ID, env.d.ts update, and worker-context plumbing. The key prefixes (`search-index:shard:*` vs `search:*`) are distinct and cannot collide. KV namespaces have no per-key limits, only per-value (25MB).

**Alternatives considered**: New dedicated KV namespace (rejected: unnecessary complexity for no benefit).

### AD-2: Single-character sharding

**Decision**: Shard by the first character of the lowercased skill name (a-z, 0-9, _).

**Rationale**: At 70k skills and assuming a roughly uniform distribution across 37 shards, each shard averages ~1,900 entries at ~400 bytes each = ~760KB. Worst-case skew (e.g., 5,000 entries on the "s" shard) = ~2MB, well under the 25MB limit and the 5MB safety margin from the spec. Single-character sharding is trivially predictable from the query (no hashing, no directory lookups).

**Alternatives considered**:
- No sharding (single blob): At 70k * 400 bytes = 28MB, exceeds the 25MB KV value limit.
- Bigram sharding (first two chars): Creates 1,369 possible shards, most nearly empty. Requires reading multiple shards for single-character queries (e.g., "r" needs r*, ra-rz, r0-r9). Unnecessary complexity.
- Category-based sharding: Skills have imbalanced category distribution. Would still need character-based sub-sharding.

### AD-3: Prefix matching at the edge, ILIKE deferred to Postgres

**Decision**: Edge search performs prefix matching only (matching the existing tsquery `word:*` behavior). Substring/contains matching is not available at the edge; queries that return zero results from the edge path fall through to the Postgres `searchSkills()` function, which includes both tsvector and ILIKE fallback.

**Rationale**: Building a trigram index at the edge would triple index size and dramatically increase search complexity for a marginal UX benefit. The existing ILIKE fallback already handles substring matches. Since <5% of queries are expected to miss the edge path, the Postgres latency is acceptable for those cases.

### AD-4: Queue message on the existing SUBMISSION_QUEUE with type discrimination

**Decision**: Dispatch `rebuild_search_shard` messages on the existing `SUBMISSION_QUEUE` rather than creating a new queue.

**Rationale**: Cloudflare Queues pricing is per-message. A new queue requires wrangler.jsonc changes, consumer registration in worker-with-queues.js, and additional configuration. The existing consumer already processes a discriminated union by `type` field (currently only `process_submission`). Adding `rebuild_search_shard` to the union is a single-line type change and a switch case in the consumer.

**Risk**: Search index updates share processing capacity with submission processing. **Mitigation**: Index updates are fast (single KV read-modify-write, <100ms), while submission processing takes 5-55s. At 10x concurrency, index updates will never contend meaningfully.

### AD-5: Incremental updates with data in queue message

**Decision**: The queue message includes the full `SearchIndexEntry` data (7 fields, ~200 bytes) so the consumer does not need to read from Postgres.

**Rationale**: The consumer runs in queue handler context where `getCloudflareContext()` is unavailable and Prisma access requires `runWithWorkerEnv()`. Including the data in the message makes the consumer a pure KV operation (read shard, modify, write shard) with no DB dependency. This also means index updates succeed even during Neon outages.

### AD-6: Client-side SWR with in-memory Map

**Decision**: Use a simple `Map<string, {data: SearchResponse, timestamp: number}>` in SearchPalette rather than a library like `swr` or `react-query`.

**Rationale**: SearchPalette is a single component with a single data source. Adding a library for one cache instance is over-engineering. The Map-based approach is ~15 lines of code, has zero bundle impact, and the 60s TTL + background revalidation pattern is trivial to implement with `useEffect`.

### AD-7: Client-side highlighting with regex

**Decision**: Compute search result highlighting in the browser via regex wrapping instead of server-side `ts_headline`.

**Rationale**: Edge search returns results from a compact KV index that contains no descriptions (descriptions are excluded to stay under KV size limits). Without description text, `ts_headline` has no content to excerpt. Client-side highlighting applies `<b>` tags to the `displayName` field, which is always available. When results come from the Postgres fallback path, the server-computed `highlight` is used as-is.

## Implementation Phases

### Phase 1: Search Index Infrastructure (US-001, US-004)

1. Add `SearchIndexEntry` and `SearchIndexMeta` types to `src/lib/search.ts`
2. Create `src/lib/search-index.ts` with:
   - `getShardKey(skillName)` - returns the shard key character
   - `buildSearchIndex(db, kv)` - full rebuild from Postgres
   - `updateSearchShard(kv, entry, action)` - incremental upsert/remove
3. Extend `POST /api/v1/admin/rebuild-index` to call `buildSearchIndex()`
4. Test with unit tests mocking KV

### Phase 2: Edge Search Service (US-002)

1. Add `searchSkillsEdge(options)` to `src/lib/search.ts`:
   - Read shard(s) from KV based on query prefix
   - Multi-word queries: read shard for first word, intersect matches across all words
   - Apply category filter in-memory
   - Paginate results in-memory
   - Return `SearchResponse` with empty `highlight` strings
2. Modify `src/app/api/v1/skills/search/route.ts`:
   - Call `searchSkillsEdge()` first
   - On zero results, fall back to existing `searchSkills()` with retry loop
   - Set `X-Search-Source: edge` or `X-Search-Source: postgres` response header for observability
3. Test edge path thoroughly

### Phase 3: Incremental Index Updates (US-003)

1. Add `SearchShardQueueMessage` to `src/lib/queue/types.ts` as discriminated union
2. Create `src/lib/queue/search-index-consumer.ts` with `handleSearchIndexUpdate()`
3. Modify `src/lib/queue/consumer.ts` to route `rebuild_search_shard` messages
4. Modify `src/lib/submission-store.ts` `publishSkill()` to dispatch queue message after successful upsert
5. Update `worker-with-queues.js` import if new module
6. Test consumer with mocked KV

### Phase 4: Client-Side Improvements (US-005, US-006, US-007)

1. Add `highlightMatches(text, query)` utility to SearchPalette
2. Apply client-side highlighting when `highlight` is empty
3. Add in-memory SWR cache (`Map` with 60s TTL)
4. Reduce debounce from 300ms to 100ms
5. Test SearchPalette behavior

## Testing Strategy

All testing follows the project's TDD enforcement (strict mode per config.json).

### Unit Tests

| Module | Test File | Coverage |
|--------|-----------|----------|
| `search-index.ts` | `src/lib/__tests__/search-index.test.ts` | `buildSearchIndex()`, `updateSearchShard()`, `getShardKey()`, edge cases (empty DB, max shard size) |
| `searchSkillsEdge()` | `src/lib/search.test.ts` (extended) | Edge search: prefix matching, multi-word, category filter, pagination, empty results (triggers fallback), KV unavailability |
| `search-index-consumer.ts` | `src/lib/queue/__tests__/search-index-consumer.test.ts` | Upsert, remove, retry on KV failure, metadata update |
| `consumer.ts` routing | `src/lib/queue/__tests__/consumer.test.ts` (extended) | Type discrimination routes to correct handler |
| `SearchPalette.tsx` | `src/app/components/__tests__/SearchPalette.test.tsx` (extended) | Client-side highlighting, SWR cache hit/miss/revalidate, 100ms debounce |
| `route.ts` | New or extended test | Edge-first with Postgres fallback, observability header |

### Mock Strategy

Following the project's ESM mocking pattern (`vi.hoisted()` + `vi.mock()`):

```typescript
// KV mocking (reuse existing pattern from search.test.ts)
const mockKvGet = vi.hoisted(() => vi.fn());
const mockKvPut = vi.hoisted(() => vi.fn());
vi.mock("@opennextjs/cloudflare", () => ({
  getCloudflareContext: vi.fn().mockResolvedValue({
    env: { SEARCH_CACHE_KV: { get: mockKvGet, put: mockKvPut } },
  }),
}));
```

### Integration Smoke Test

After deployment, verify with a manual curl sequence:
1. `POST /api/v1/admin/rebuild-index` (builds index)
2. `GET /api/v1/skills/search?q=re` (should return results from edge)
3. Check `X-Search-Source` header in response

## Technical Challenges

### Challenge 1: Multi-word queries spanning multiple shards

**Problem**: A query like "code review" has first word starting with 'c' and second with 'r'. Reading both shards and intersecting is more complex than single-shard reads.

**Solution**: Read the shard for the first query word only. Then filter in-memory: for each entry in the shard, check if ALL query words match as prefixes against `name` or `displayName`. This works because the first word narrows the candidate set to ~1,900 entries, and in-memory string matching across 1,900 entries is sub-millisecond.

**Edge case**: If the query starts with a non-alphanumeric character, use the `_` shard. If the `_` shard is empty (likely), fall through to Postgres.

### Challenge 2: Queue consumer KV access without getCloudflareContext()

**Problem**: The queue consumer runs in Worker context where `getCloudflareContext()` (from `@opennextjs/cloudflare`) is not available. The existing `getKv()` helper in `search.ts` uses `getCloudflareContext()`.

**Solution**: The queue consumer receives `env` directly as a parameter. The `handleSearchIndexUpdate()` function accepts `env.SEARCH_CACHE_KV` as a parameter rather than calling `getKv()`. This mirrors how the existing `handleSubmissionQueue()` receives `env.QUEUE_METRICS_KV`.

### Challenge 3: Race condition on shard updates

**Problem**: Two concurrent `publishSkill()` calls for skills in the same shard could both read the shard, modify independently, and one overwrites the other's changes (last-write-wins).

**Solution**: Queue messages are serialized per-queue. With `max_concurrency: 10` and `max_batch_size: 3`, concurrent processing is possible but unlikely for the same shard. Even if it occurs, the next publish for any skill in that shard will re-read and include the missing entry. The metadata key (`totalSkills`) may temporarily be inaccurate, but the full rebuild admin endpoint corrects this. Acceptable trade-off for simplicity.

**Mitigation**: If this becomes a problem, use KV's `metadata` field for optimistic locking (check shard version before write). Not implemented in v1.

### Challenge 4: SearchPalette highlighting with dangerouslySetInnerHTML

**Problem**: Client-side highlighting wraps matched terms in `<b>` tags, which are rendered via `dangerouslySetInnerHTML`. The query string must be sanitized to prevent XSS.

**Solution**: The `highlightMatches()` function escapes all HTML special characters in the input text BEFORE applying regex wrapping. The regex pattern itself is built from the escaped query terms. This is identical to the security model of the existing `dangerouslySetInnerHTML` usage for server-side highlights (which come from Postgres `ts_headline`, also HTML).

### Challenge 5: Keeping the edge index fresh during initial deployment

**Problem**: Before the admin rebuild endpoint is called, the KV search index is empty. All queries would go to Postgres (the fallback path), which is the current behavior anyway.

**Solution**: After deploying the code changes, the admin calls `POST /api/v1/admin/rebuild-index` once to seed the search index. From that point forward, incremental updates via the queue keep it current. There is no "big bang" migration -- the system gracefully degrades to the existing Postgres path when the index is absent.

### Challenge 6: worker-with-queues.js is auto-generated but manually maintained

**Problem**: `worker-with-queues.js` is documented as "Auto-generated -- do not edit manually" but is actually manually maintained. It needs a new import for the search index consumer.

**Solution**: The queue routing in `consumer.ts` already handles all `submission-processing` queue messages. The search index messages use the same queue. The only change to `consumer.ts` is adding a `type` check before calling `processSubmission()` or `handleSearchIndexUpdate()`. No changes needed to `worker-with-queues.js`.
