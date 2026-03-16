# Architecture Plan: Search Performance Optimization

## Overview

Optimize the verified-skill.com search pipeline from sequential edge+Postgres to an edge-first architecture with conditional Postgres fallback, add trending skills preloading on palette open, improve cache headers, and add Server-Timing observability headers.

## Architecture Decision: Edge-First with Conditional Postgres Fallback

### Current Flow (Sequential)

```
SearchPalette (debounce 150ms, min 2 chars)
       |
       v
GET /api/v1/skills/search?q=X
       |
       +---> searchSkillsEdge() ---- KV read (~20-50ms)
       |
       +---> searchSkills()     ---- Postgres tsvector + ILIKE (~100-500ms+)
       |
       v
  Merge (Postgres authoritative for star counts)
       |
       v
  enrichWithBlocklistAndRejected() ---- 3x DB queries always (~50-100ms)
       |        getBlockedSkillNames()
       |        searchBlocklistEntries()
       |        searchRejectedSubmissions()
       |
       v
  Sort -> Dedup -> Paginate -> Response
       Cache-Control: public, max-age=10, s-maxage=30
```

**Problem**: Postgres is ALWAYS called, even when edge returns 200+ results. Blocklist enrichment ALWAYS runs all 3 DB queries. Total p95: 200-1000ms+.

### Target Flow (Edge-First, Conditional)

```
SearchPalette
  |-- query="" : show trendingSkills from /api/v1/stats (cached, <50ms)
  |-- query=1char : client-side filter of trending (instant, 0ms)
  |-- query>=2chars : debounce 150ms -> API call
       |
       v
GET /api/v1/skills/search?q=X
       |
       +---> searchSkillsEdge() ---- KV read (~20-50ms) [TIMED]
       |
       +---> IF edge.length < fetchLimit:
       |        searchSkills() ---- Postgres (~100-500ms) [TIMED]
       |     ELSE:
       |        skip Postgres
       |
       v
  Merge (only if both sources used)
       |
       v
  enrichWithBlocklistAndRejected() ---- CONDITIONAL:
       |  IF source == "edge" only:
       |     skip getBlockedSkillNames() (KV excludes blocked)
       |     still call searchBlocklistEntries() + searchRejectedSubmissions()
       |  ELSE (includes Postgres):
       |     all 3 queries as before
       |
       v
  Sort -> Dedup -> Paginate -> Response
       Cache-Control: public, max-age=10, s-maxage=60, stale-while-revalidate=300
       Server-Timing: edge;dur=X, postgres;dur=Y, enrichment;dur=Z
       X-Search-Source: edge | postgres | edge+postgres
```

**Expected impact**: ~80-90% of queries become edge-only at ~50ms p95. Remaining 10-20% still hit Postgres (niche queries, categories with sparse KV coverage).

## Component Changes

### C1: Search Route (`route.ts`)

**Current**: Always runs both searchSkillsEdge + searchSkills sequentially, always runs all 3 enrichment queries.

**Changes**:

1. **Edge-first conditional Postgres**: Call `searchSkillsEdge()` first. Only call `searchSkills()` if edge returns < `fetchLimit` results.
2. **Conditional enrichment**: Pass `edgeOnly` flag to `enrichWithBlocklistAndRejected()`. When source is "edge" only, skip `getBlockedSkillNames()` (KV index already excludes blocked skills per `buildSearchIndex()` which filters `if (blockedNames.has(skill.name)) continue`).
3. **Server-Timing headers**: Wrap each phase in `performance.now()` timing. Emit `Server-Timing: edge;dur=X, postgres;dur=Y, enrichment;dur=Z` header.
4. **Updated Cache-Control**: Change from `s-maxage=30` to `s-maxage=60, stale-while-revalidate=300`.

**Interface change to enrichWithBlocklistAndRejected**:

```typescript
async function enrichWithBlocklistAndRejected(
  results: SearchResult[],
  query: string,
  limit: number,
  edgeOnly: boolean,  // NEW: when true, skip getBlockedSkillNames()
): Promise<SearchResult[]>
```

**Key correctness constraint**: When `edgeOnly=true`, we skip `getBlockedSkillNames()` because the KV index build (`buildSearchIndex`) already filters out blocked skills from shards. But we STILL call `searchBlocklistEntries()` and `searchRejectedSubmissions()` because those surface blocked/rejected entries AS search results (showing them to users as "BLOCKED" or "REJECTED" rows), which is a different concern from cross-referencing existing results against the blocklist.

### C2: Search Service (`search.ts`)

**No changes needed**. The `searchSkillsEdge()` and `searchSkills()` functions are already well-separated. The conditional logic lives in the route handler (C1), not the service layer.

### C3: SearchPalette (`SearchPalette.tsx`)

**Current**: Empty state when query is empty. Categories + Actions shown. No data until user types >= 2 chars and debounce fires.

**Changes**:

1. **Fetch trending on mount**: On palette open, fetch `/api/v1/stats` and extract `trendingSkills` array. Cache result in a `useRef` for the session (no re-fetch on subsequent opens).
2. **Map TrendingSkillEntry to SearchResult**: Build a mapper that converts `TrendingSkillEntry` fields to the `SearchResult` shape used by the existing rendering logic. Fields map directly: `name`, `displayName`, `author`, `repoUrl`, `certTier`. Missing fields get defaults (`githubStars: 0`, `highlight: ""`, `category: ""`).
3. **Display when query is empty**: Show mapped trending skills in the SKILLS group when `query === ""` or `query.length < 2` and no API results.
4. **Client-side filter for 1-char**: When query is exactly 1 character, filter the trending skills array by `name` or `displayName` prefix match. No loading skeleton shown (instant filter).
5. **Transition to API results**: When query reaches 2+ chars and the debounce timer fires, API results replace trending/filtered data as they do today.
6. **SWR cache TTL update**: Change `SWR_TTL_MS` from `10_000` to `60_000` (60 seconds).

**Data flow**:

```
palette open (query="")
  |-> fetch /api/v1/stats -> cache in useRef -> show trending[0..9] as SKILLS
  |
user types "r" (query="r")
  |-> client filter: trending.filter(s =>
  |     s.name.toLowerCase().includes("r") ||
  |     s.displayName.toLowerCase().startsWith("r"))
  |-> show filtered trending, no loading state
  |
user types "re" (query="re")
  |-> debounce 150ms -> GET /api/v1/skills/search?q=re
  |-> show loading skeleton
  |-> replace with API results
```

**Trending cache strategy**: The `/api/v1/stats` endpoint already has aggressive caching (`Cache-Control: public, max-age=60, s-maxage=300, stale-while-revalidate=600`). The client stores the trending slice in a `useRef` that persists for the component lifetime (effectively session-scoped since SearchPalette lives in the root layout). No separate trending endpoint needed.

### C4: Cache Headers (Cross-Cutting)

**Search endpoint**: `Cache-Control: public, max-age=10, s-maxage=60, stale-while-revalidate=300`
- `max-age=10`: Client cache stays at 10s (user sees fresh results on repeat searches)
- `s-maxage=60`: CDN caches for 60s (up from 30s) -- most search results don't change within a minute
- `stale-while-revalidate=300`: CDN serves stale for up to 5 min while revalidating in background

**Frontend SWR**: `SWR_TTL_MS = 60_000` (up from 10_000). Matches the CDN `s-maxage` so the client doesn't re-fetch what the CDN would also serve stale.

## Data Flow Diagram

```
                          SearchPalette.tsx
                     +--------------------------+
                     | query="" : trending[10]  |
                     | query=1ch : filter trend |
                     | query>=2ch : API search  |
                     +------------+-------------+
                                  |
          +-----------------------+----------------------+
          | /api/v1/stats         | /api/v1/skills/      |
          | (trending src)        | search?q=X           |
          | CDN: s-max=300        | CDN: s-max=60        |
          +----------+------------+-----------+-----------+
                     |                        |
                     |    +-------------------v------------------+
                     |    | route.ts (search handler)            |
                     |    +--------------------------------------+
                     |    | 1. searchSkillsEdge (KV)             |--> SEARCH_CACHE_KV
                     |    | 2. IF < fetchLimit:                  |
                     |    |    searchSkills (PG)                 |--> Neon Postgres
                     |    | 3. enrichment (conditional)          |--> Neon Postgres
                     |    | 4. sort/dedup/paginate               |
                     |    | 5. Server-Timing header              |
                     |    +--------------------------------------+
                     |
                     v
          SUBMISSIONS_KV ("platform:stats")
          [trendingSkills cached by 5-min cron]
```

## Risk Analysis

| Risk | Probability | Mitigation |
|------|-------------|------------|
| Edge KV returns stale/incomplete data (no Postgres correction) | Low | KV index rebuilt by cron; incremental updates on skill publish. `fetchLimit=200` is generous -- most queries match far fewer. If edge returns 200 results, data quality is high. |
| Trending skills endpoint slow or unavailable on palette open | Low | `/api/v1/stats` has 3-tier fallback (KV -> memory -> DB -> hardcoded). CDN caches aggressively. Failure just shows empty palette (same as today). |
| Client-side filter for 1-char gives poor results | Low | This is a bridging UX -- replaces "nothing" with "something relevant". API takes over at 2 chars. Worst case: filter shows no matches (same empty state as before). |
| `stale-while-revalidate=300` serves stale results too long | Low | Search results change slowly (skills are published, not edited frequently). Max staleness is 5 min + 60s CDN cache = ~6 min worst case. Acceptable for a directory. |
| Skipping getBlockedSkillNames masks a newly blocked skill in edge results | None | Impossible by design: `buildSearchIndex()` excludes blocked skills from KV shards. A newly blocked skill is removed from KV on the next index rebuild (triggered by the block action). Between block and rebuild (~minutes), the skill may appear in edge results, but this is the same as today (Postgres also has lag). |

## File Inventory

All changes are confined to 3 files as specified in the spec constraints:

| File | Change Type | Scope |
|------|-------------|-------|
| `src/app/api/v1/skills/search/route.ts` | Modify | Edge-first logic, conditional enrichment, Server-Timing, cache headers |
| `src/lib/search.ts` | No change | Already well-structured, no modifications needed |
| `src/app/components/SearchPalette.tsx` | Modify | Trending preload, client-side filter, SWR TTL update |

## Non-Goals (Confirmed by Spec)

- No search algorithm changes (ranking, scoring, stemming)
- No KV index rebuild or re-sharding
- No new KV namespaces or DB tables
- No Postgres query optimization
- No real-time cache invalidation
- No search analytics

## Testing Strategy

- **Unit tests (route.ts)**: Mock KV responses for edge-first conditional logic, verify Postgres is/isn't called based on edge result count. Test Server-Timing header format. Test enrichment conditional logic (edgeOnly=true skips getBlockedSkillNames but still calls the other two).
- **Unit tests (SearchPalette.tsx)**: Test trending display when query is empty, client-side filter for 1-char queries, transition from trending to API results at 2+ chars.
- **Integration**: Full route handler test with mocked KV + DB, verify response headers and shape under edge-only and edge+postgres scenarios.
- **Manual verification**: Browser DevTools Network tab to confirm Server-Timing headers and cache behavior in production.
