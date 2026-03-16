---
increment: 0494-search-performance-optimization
title: "Search Performance Optimization"
status: active
test_mode: TDD
coverage_target: 90
by_user_story:
  US-001: [T-001]
  US-002: [T-002]
  US-003: [T-003]
  US-004: [T-004]
  US-005: [T-005]
  US-006: [T-006]
---

# Tasks: Search Performance Optimization

## User Story: US-001 - Edge-First Search with Conditional Postgres Fallback

**Linked ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04
**Tasks**: 1 total, 1 completed

### T-001: Implement edge-first conditional Postgres fallback in route.ts

**User Story**: US-001
**Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04
**Status**: [x] completed

**Test Plan**:
- **Given** edge KV returns >= fetchLimit (200) results
- **When** GET /api/v1/skills/search?q=X is called
- **Then** `searchSkills` (Postgres) is NOT called and X-Search-Source header is "edge"

- **Given** edge KV returns < fetchLimit results
- **When** GET /api/v1/skills/search?q=X is called
- **Then** `searchSkills` (Postgres) IS called and X-Search-Source header is "edge+postgres"

- **Given** edge KV throws an error
- **When** GET /api/v1/skills/search?q=X is called
- **Then** Postgres is called as full fallback, results are returned, X-Search-Source is "postgres"

**Test Cases**:
1. **Unit**: `src/app/api/v1/skills/search/__tests__/route.test.ts`
   - `edgeOnly_skipsPostgres_whenEdgeReturnsFetchLimit()`: mock edge returning 200 results, assert mockSearchSkills not called, assert X-Search-Source: "edge"
   - `edgePlusPg_callsPostgres_whenEdgeBelowFetchLimit()`: mock edge returning 5 results, assert mockSearchSkills called, assert X-Search-Source: "edge+postgres"
   - `pgFallback_whenEdgeFails()`: mock searchSkillsEdge to reject, assert searchSkills called, assert X-Search-Source: "postgres"
   - `xSearchSourceHeader_exactValue_edgeOnly()`: assert header value is exactly "edge" when edge returns >= fetchLimit
   - **Coverage Target**: 95%

**Implementation**:
1. In `route.ts`, call `searchSkillsEdge()` first and capture result count
2. Add conditional: if `edgeResults.length >= fetchLimit`, skip `searchSkills()` call entirely
3. Track source string: `"edge"` | `"postgres"` | `"edge+postgres"` based on which paths executed
4. Set `X-Search-Source` response header with the tracked source string
5. Update existing tests that assume Postgres is always called — set edge results to < 200 to trigger Postgres path
6. Run: `cd repositories/anton-abyzov/vskill-platform && npx vitest run src/app/api/v1/skills/search/__tests__/route.test.ts`

---

## User Story: US-002 - Conditional Blocklist Enrichment

**Linked ACs**: AC-US2-01, AC-US2-02, AC-US2-03
**Tasks**: 1 total, 1 completed

### T-002: Skip getBlockedSkillNames when source is edge-only

**User Story**: US-002
**Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03
**Status**: [x] completed

**Test Plan**:
- **Given** search results came exclusively from edge KV (source = "edge")
- **When** enrichWithBlocklistAndRejected runs
- **Then** `getBlockedSkillNames` is NOT called, but `searchBlocklistEntries` and `searchRejectedSubmissions` still ARE called

- **Given** search results include Postgres data (source = "edge+postgres" or "postgres")
- **When** enrichWithBlocklistAndRejected runs
- **Then** all 3 blocklist queries execute (getBlockedSkillNames, searchBlocklistEntries, searchRejectedSubmissions)

**Test Cases**:
1. **Unit**: `src/app/api/v1/skills/search/__tests__/route.test.ts`
   - `edgeOnly_skipsGetBlockedSkillNames()`: set edge >= fetchLimit, assert mockGetBlockedSkillNames not called
   - `edgeOnly_stillCallsBlocklistEntries()`: edge-only path, assert mockSearchBlocklistEntries called
   - `edgeOnly_stillCallsRejectedSubmissions()`: edge-only path, assert mockSearchRejectedSubmissions called
   - `pgPath_callsAllThreeBlocklistQueries()`: edge < fetchLimit triggers PG, assert all 3 mocks called
   - **Coverage Target**: 95%

**Implementation**:
1. Add `edgeOnly: boolean` parameter to `enrichWithBlocklistAndRejected()` function signature in `route.ts`
2. Inside the function, wrap the `getBlockedSkillNames()` call in `if (!edgeOnly)`
3. Leave `searchBlocklistEntries()` and `searchRejectedSubmissions()` unconditional (always called)
4. Pass `edgeOnly = (source === "edge")` from the route handler
5. Run: `cd repositories/anton-abyzov/vskill-platform && npx vitest run src/app/api/v1/skills/search/__tests__/route.test.ts`

---

## User Story: US-003 - Improved CDN and Client Cache Headers

**Linked ACs**: AC-US3-01, AC-US3-02, AC-US3-03
**Tasks**: 1 total, 1 completed

### T-003: Update Cache-Control header and frontend SWR TTL

**User Story**: US-003
**Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03
**Status**: [x] completed

**Test Plan**:
- **Given** any valid search request
- **When** the response is returned from the search endpoint
- **Then** Cache-Control header is `public, max-age=10, s-maxage=60, stale-while-revalidate=300`

- **Given** the SearchPalette SWR cache constant
- **When** the constant value is inspected
- **Then** `SWR_TTL_MS` is 60000 (60 seconds, up from 10000)

**Test Cases**:
1. **Unit**: `src/app/api/v1/skills/search/__tests__/route.test.ts`
   - `cacheControlHeader_hasStaleWhileRevalidate300()`: call GET, assert Cache-Control header contains `stale-while-revalidate=300`
   - `cacheControlHeader_sMaxageIs60()`: assert Cache-Control contains `s-maxage=60` (not `s-maxage=30`)
   - **Coverage Target**: 90%

2. **Unit**: `src/app/components/__tests__/SearchPalette.test.tsx`
   - `swrTtlConstant_is60000()`: import or spy on SWR options passed to useSWR, assert dedupingInterval is 60000
   - **Coverage Target**: 85%

**Implementation**:
1. In `route.ts`, update the Cache-Control header string from `public, max-age=10, s-maxage=30` to `public, max-age=10, s-maxage=60, stale-while-revalidate=300`
2. In `SearchPalette.tsx`, change the `SWR_TTL_MS` constant from `10_000` to `60_000`
3. Run: `cd repositories/anton-abyzov/vskill-platform && npx vitest run src/app/api/v1/skills/search/__tests__/route.test.ts src/app/components/__tests__/SearchPalette.test.tsx`

---

## User Story: US-004 - Server-Timing Latency Headers

**Linked ACs**: AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-04
**Tasks**: 1 total, 1 completed

### T-004: Add Server-Timing headers for edge, postgres, and enrichment phases

**User Story**: US-004
**Satisfies ACs**: AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-04
**Status**: [x] completed

**Test Plan**:
- **Given** any search request is handled
- **When** the response is returned
- **Then** Server-Timing header contains `edge;dur=X` with a numeric duration in milliseconds

- **Given** Postgres was called (edge < fetchLimit)
- **When** response headers are inspected
- **Then** Server-Timing includes `postgres;dur=X` with a numeric duration (not "skipped")

- **Given** Postgres was skipped (edge >= fetchLimit)
- **When** response headers are inspected
- **Then** Server-Timing includes `postgres;desc="skipped";dur=0`

- **Given** any search request is handled
- **When** the response is returned
- **Then** Server-Timing includes `enrichment;dur=X` with a numeric duration

**Test Cases**:
1. **Unit**: `src/app/api/v1/skills/search/__tests__/route.test.ts`
   - `serverTiming_includesEdgeDuration()`: call GET, parse Server-Timing header, assert contains `edge;dur=` followed by a number
   - `serverTiming_includesPostgresDuration_whenPgCalled()`: edge < fetchLimit, assert Server-Timing contains `postgres;dur=` (numeric, not "skipped")
   - `serverTiming_marksPostgresSkipped_whenEdgeOnly()`: edge >= fetchLimit, assert Server-Timing contains `postgres;desc="skipped";dur=0`
   - `serverTiming_includesEnrichmentDuration()`: assert Server-Timing contains `enrichment;dur=`
   - **Coverage Target**: 95%

**Implementation**:
1. In `route.ts`, capture `performance.now()` before and after `searchSkillsEdge()`, store as `edgeDur`
2. Capture `performance.now()` before and after `searchSkills()` call, store as `pgDur`; when Postgres is skipped, set `pgDur = 0` and `pgSkipped = true`
3. Capture `performance.now()` before and after `enrichWithBlocklistAndRejected()`, store as `enrichDur`
4. Build Server-Timing string: `edge;dur=${edgeDur.toFixed(1)}, postgres;desc="${pgSkipped ? "skipped" : "db"}";dur=${pgDur.toFixed(1)}, enrichment;dur=${enrichDur.toFixed(1)}`
5. Simplify when Postgres skipped: `postgres;desc="skipped";dur=0`
6. Set `Server-Timing` response header
7. Run: `cd repositories/anton-abyzov/vskill-platform && npx vitest run src/app/api/v1/skills/search/__tests__/route.test.ts`

---

## User Story: US-005 - Preload Trending Skills on Palette Open

**Linked ACs**: AC-US5-01, AC-US5-02, AC-US5-03, AC-US5-04, AC-US5-05
**Tasks**: 1 total, 1 completed

### T-005: Fetch and display trending skills when search palette opens

**User Story**: US-005
**Satisfies ACs**: AC-US5-01, AC-US5-02, AC-US5-03, AC-US5-04, AC-US5-05
**Status**: [x] completed

**Test Plan**:
- **Given** the search palette opens with an empty query
- **When** the component mounts
- **Then** up to 10 trending skills are displayed in the SKILLS group without the user typing

- **Given** trending skills are already in session cache (useRef holds data)
- **When** the palette is closed and re-opened
- **Then** no new fetch to /api/v1/stats is made

- **Given** the user types >= 2 characters and debounce fires
- **When** API search results arrive
- **Then** trending skills are replaced by actual API search results

**Test Cases**:
1. **Unit**: `src/app/components/__tests__/SearchPalette.test.tsx`
   - `trendingSkills_shownOnPaletteOpen_queryEmpty()`: mock global fetch for /api/v1/stats returning trendingSkills array, open palette, assert skill rows visible before typing
   - `trendingSkills_notRefetched_onSecondOpen()`: open palette (fetch called once), close and re-open, assert fetch for /api/v1/stats still called only once total
   - `trendingSkills_replacedByApiResults_atTwoChars()`: mock fetch for search endpoint, type "re", wait for debounce, assert search results shown (trending replaced)
   - `trendingSkills_sameRowLayout_asSearchResults()`: assert trending rows render the same component as search result rows (displayName visible, certTier badge present)
   - **Coverage Target**: 90%

**Implementation**:
1. In `SearchPalette.tsx`, add `trendingRef = useRef<TrendingSkillEntry[] | null>(null)` to hold session-cached data
2. Add `useEffect(() => { if (trendingRef.current) return; fetch("/api/v1/stats").then(r => r.json()).then(data => { trendingRef.current = data.trendingSkills ?? []; }); }, [])` — runs once on mount
3. Define `mapTrendingToSearchResult(t: TrendingSkillEntry): SearchResult`: map `name`, `displayName`, `author`, `repoUrl`, `certTier`; set `githubStars: 0`, `highlight: ""`, `category: ""`
4. In render logic: when `query === ""` and API results are not loading, derive results from `trendingRef.current?.slice(0, 10).map(mapTrendingToSearchResult) ?? []`
5. Ensure the same result row JSX renders for trending as for search results (reuse existing component)
6. Run: `cd repositories/anton-abyzov/vskill-platform && npx vitest run src/app/components/__tests__/SearchPalette.test.tsx`

---

## User Story: US-006 - Client-Side Filter of Preloaded Trending Data

**Linked ACs**: AC-US6-01, AC-US6-02, AC-US6-03, AC-US6-04
**Tasks**: 1 total, 1 completed

### T-006: Filter trending skills client-side for 1-character queries

**User Story**: US-006
**Satisfies ACs**: AC-US6-01, AC-US6-02, AC-US6-03, AC-US6-04
**Status**: [x] completed

**Test Plan**:
- **Given** trending skills are loaded and the user types exactly 1 character
- **When** the component renders
- **Then** the trending list is filtered instantly by name/displayName prefix match, no loading skeleton shown, and no fetch to search endpoint

- **Given** the query reaches 2+ characters and the debounce fires
- **When** API results arrive
- **Then** API results replace the client-filtered trending list

- **Given** trending data has not loaded yet when the user types 1 character
- **When** the component renders
- **Then** standard empty state is shown (no error, no loading skeleton)

**Test Cases**:
1. **Unit**: `src/app/components/__tests__/SearchPalette.test.tsx`
   - `oneCharQuery_filtersClientSide_byNamePrefix()`: load trending with ["react", "rust", "redis"], type "r", assert all 3 names visible; assert no fetch to /api/v1/skills/search
   - `oneCharQuery_noLoadingSkeleton()`: type 1 char, assert loading skeleton element NOT present in DOM
   - `oneCharQuery_noSearchFetch()`: spy on fetch, type "r", advance timers 200ms, assert fetch not called for /api/v1/skills/search
   - `twoCharQuery_apiResultsReplaceTrending()`: type "re" (2 chars), wait debounce, assert API results shown and trending not shown
   - `oneCharQuery_emptyState_whenTrendingNotLoaded()`: do not resolve /api/v1/stats fetch, type "r", assert empty results (no error thrown)
   - **Coverage Target**: 90%

**Implementation**:
1. In `SearchPalette.tsx`, add derived value: when `query.length === 1` and `trendingRef.current` is not null, compute `filteredTrending = trendingRef.current.filter(s => s.name.toLowerCase().startsWith(query.toLowerCase()) || s.displayName.toLowerCase().startsWith(query.toLowerCase()))`
2. Use `filteredTrending` as displayed results when `query.length === 1` — no fetch triggered, no loading skeleton
3. Verify the existing debounce guard (`query.length < 2` prevents fetch) remains intact
4. When `query.length === 1` and `trendingRef.current` is null, use empty array as results (empty state, no error)
5. When `query.length >= 2`, debounce fires and API results take over as today
6. Run: `cd repositories/anton-abyzov/vskill-platform && npx vitest run src/app/components/__tests__/SearchPalette.test.tsx`
7. Run full suite: `cd repositories/anton-abyzov/vskill-platform && npx vitest run`
