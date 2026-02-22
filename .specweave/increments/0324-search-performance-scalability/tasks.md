# Tasks: Search Performance & Scalability for 70k+ Skills

**Increment**: 0324-search-performance-scalability
**Project**: vskill-platform
**Test Mode**: TDD (RED -> GREEN -> REFACTOR)
**Coverage Target**: 80%

---

## US-001: Full-Text Search Column and Index

### T-001: Create Prisma migration for search_vector column
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-03, AC-US1-04 | **Status**: [x] completed
**Test**: Given the Skill table exists → When migration runs → Then `search_vector` column is added as `tsvector GENERATED ALWAYS AS` with A/B/C/D weights for name, displayName, description, and author+labels respectively
**Files**: `prisma/migrations/YYYYMMDDHHMMSS_add_search_vector/migration.sql`
**Notes**: Raw SQL migration. Column expression: `setweight(to_tsvector('english', coalesce(name, '')), 'A') || setweight(to_tsvector('english', coalesce("displayName", '')), 'B') || setweight(to_tsvector('english', coalesce(description, '')), 'C') || setweight(to_tsvector('english', coalesce(array_to_string(labels, ' ') || ' ' || coalesce(author, ''), '')), 'D')`. Zero-downtime: add nullable first, backfill, then alter to GENERATED.

### T-002: Create GIN index on search_vector
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02 | **Status**: [x] completed
**Test**: Given `search_vector` column exists → When GIN index migration runs → Then `idx_skill_search_vector` GIN index exists and `EXPLAIN` shows index scan for `@@ to_tsquery` queries
**Files**: `prisma/migrations/YYYYMMDDHHMMSS_add_search_vector/migration.sql` (appended)
**Notes**: Use `CREATE INDEX CONCURRENTLY idx_skill_search_vector ON "Skill" USING gin(search_vector)`. Must be in a separate statement (CONCURRENTLY cannot run inside a transaction). Prisma migration may need `-- CreateIndex` comment or a separate raw SQL step.

### T-003: Upsert 118 seed skills into Postgres
**User Story**: US-001 | **Satisfies ACs**: AC-US1-05 | **Status**: [x] completed
**Test**: Given seed-data.ts has 118 skills → When seed script runs → Then all 118 skills exist in the Skill table with populated search_vector values
**Files**: `scripts/seed-skills-to-db.ts` or migration SQL INSERT/ON CONFLICT
**Notes**: Use INSERT ... ON CONFLICT (name) DO UPDATE to upsert. Map seed-data.ts fields to Skill model columns. Run as part of deploy pipeline or as a one-time script.

---

## US-002: Search Service Module

### T-004: Create src/lib/search.ts with searchSkills function (RED)
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01 | **Status**: [x] completed
**Test**: Given a test with mocked getDb() → When searchSkills({ query: "react" }) is called → Then it executes $queryRaw with Prisma.sql tagged template containing plainto_tsquery
**Files**: `src/lib/search.test.ts`, `src/lib/search.ts`
**Notes**: TDD -- write failing test first. Define SearchOptions, SearchResult, SearchResponse interfaces. Export searchSkills function.

### T-005: Implement plainto_tsquery full-text matching (GREEN)
**User Story**: US-002 | **Satisfies ACs**: AC-US2-02 | **Status**: [x] completed
**Test**: Given mocked DB returning rows → When searchSkills({ query: "security" }) is called → Then SQL contains `WHERE search_vector @@ plainto_tsquery('english', $1)` and results are returned
**Files**: `src/lib/search.ts`, `src/lib/search.test.ts`
**Notes**: Implement the $queryRaw call. Use Prisma.sql`...` for parameterized queries.

### T-006: Add ts_rank_cd ranking with weighted scoring
**User Story**: US-002 | **Satisfies ACs**: AC-US2-03 | **Status**: [x] completed
**Test**: Given mocked DB with multiple matching rows → When searchSkills is called → Then SQL contains `ts_rank_cd(search_vector, query, '{1.0, 0.4, 0.2, 0.1}')` and results are ordered by rank DESC
**Files**: `src/lib/search.ts`, `src/lib/search.test.ts`

### T-007: Add ts_headline highlighting
**User Story**: US-002 | **Satisfies ACs**: AC-US2-04 | **Status**: [x] completed
**Test**: Given a search query matching a skill description → When searchSkills is called → Then each result includes a `highlight` field from `ts_headline('english', description, query)`
**Files**: `src/lib/search.ts`, `src/lib/search.test.ts`

### T-008: Add category filter and pagination support
**User Story**: US-002 | **Satisfies ACs**: AC-US2-05 | **Status**: [x] completed
**Test**: Given searchSkills({ query: "test", category: "security", page: 2, limit: 10 }) → When called → Then SQL includes `AND category = $category`, `LIMIT 11` (limit+1 for hasMore), `OFFSET 10`, and response has correct pagination metadata
**Files**: `src/lib/search.ts`, `src/lib/search.test.ts`
**Notes**: Fetch limit+1 rows to determine hasMore without a COUNT query.

---

## US-003: KV Query Cache Layer

### T-009: Add SEARCH_CACHE_KV binding to wrangler.jsonc and env.d.ts
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01 | **Status**: [x] completed
**Test**: Given wrangler.jsonc → When inspected → Then kv_namespaces includes SEARCH_CACHE_KV with a valid hex ID; CloudflareEnv declares SEARCH_CACHE_KV: KVNamespace
**Files**: `wrangler.jsonc`, `src/lib/env.d.ts`
**Notes**: Create namespace via `wrangler kv namespace create SEARCH_CACHE_KV` to get the ID.

### T-010: Implement KV cache check in searchSkills (RED)
**User Story**: US-003 | **Satisfies ACs**: AC-US3-04, AC-US3-01 | **Status**: [x] completed
**Test**: Given SEARCH_CACHE_KV contains key `search:react::1` with cached JSON → When searchSkills({ query: "react" }) is called → Then it returns cached data without calling $queryRaw
**Files**: `src/lib/search.test.ts`, `src/lib/search.ts`
**Notes**: Cache key format: `search:{normalizedQuery}:{category}:{page}`. Normalize = lowercase + trim.

### T-011: Implement KV cache write on miss (GREEN)
**User Story**: US-003 | **Satisfies ACs**: AC-US3-02, AC-US3-03 | **Status**: [x] completed
**Test**: Given SEARCH_CACHE_KV has no entry for query → When searchSkills hits Postgres → Then result is written to KV with expirationTtl: 300 before returning
**Files**: `src/lib/search.ts`, `src/lib/search.test.ts`

### T-012: Verify cache transparency (response shape identical)
**User Story**: US-003 | **Satisfies ACs**: AC-US3-05 | **Status**: [x] completed
**Test**: Given one cached and one uncached query with same data → When both are called → Then response JSON structure is byte-identical
**Files**: `src/lib/search.test.ts`

---

## US-004: Search API Upgrade

### T-013: Rewrite route.ts to use searchSkills (RED)
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01 | **Status**: [x] completed
**Test**: Given a GET request to /api/v1/skills/search?q=react → When route handler runs → Then it calls searchSkills({ query: "react", page: 1, limit: 10 }) instead of getSkills
**Files**: `src/app/api/v1/skills/search/route.test.ts`, `src/app/api/v1/skills/search/route.ts`
**Notes**: Mock searchSkills from src/lib/search.

### T-014: Add highlight and pagination to API response (GREEN)
**User Story**: US-004 | **Satisfies ACs**: AC-US4-02, AC-US4-03 | **Status**: [x] completed
**Test**: Given searchSkills returns results with highlight fields → When API responds → Then JSON includes `results[].highlight` and `pagination: { page, limit, hasMore }`
**Files**: `src/app/api/v1/skills/search/route.ts`, `src/app/api/v1/skills/search/route.test.ts`

### T-015: Add limit validation and query length check
**User Story**: US-004 | **Satisfies ACs**: AC-US4-04, AC-US4-05 | **Status**: [x] completed
**Test**: Given `?q=a` (1 char) → When API called → Then returns 400 with error message. Given `?limit=100` → When API called → Then limit is clamped to 50. Given no limit → Then default is 10.
**Files**: `src/app/api/v1/skills/search/route.ts`, `src/app/api/v1/skills/search/route.test.ts`

---

## US-005: SearchPalette UX Improvements

### T-016: Update SearchResult interface and debounce timing
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01 | **Status**: [x] completed
**Test**: Given SearchPalette renders → When user types 1 character → Then no fetch is made. When user types 2+ characters → Then fetch fires after 150ms debounce.
**Files**: `src/app/components/SearchPalette.tsx`, `src/app/components/SearchPalette.test.tsx`
**Notes**: Update SearchResult interface to include highlight, displayName, githubStars, category. Change setTimeout from 200 to 150. Add query.length >= 2 guard.

### T-017: Add loading skeleton rows
**User Story**: US-005 | **Satisfies ACs**: AC-US5-02 | **Status**: [x] completed
**Test**: Given query is typed and fetch is in-flight → When SearchPalette renders → Then 4 shimmer skeleton rows are visible with fixed height and CSS animation
**Files**: `src/app/components/SearchPalette.tsx`, `src/app/components/SearchPalette.test.tsx`
**Notes**: Add isLoading state. Set true before fetch, false after. Render 4 skeleton divs with pulse/shimmer animation when isLoading is true.

### T-018: Render highlighted matches from API
**User Story**: US-005 | **Satisfies ACs**: AC-US5-03 | **Status**: [x] completed
**Test**: Given API returns results with `highlight: "<b>react</b> framework"` → When SearchPalette renders results → Then the highlight HTML is rendered (dangerouslySetInnerHTML) below the skill name
**Files**: `src/app/components/SearchPalette.tsx`, `src/app/components/SearchPalette.test.tsx`

### T-019: Add "Load more" pagination button
**User Story**: US-005 | **Satisfies ACs**: AC-US5-04 | **Status**: [x] completed
**Test**: Given API returns `pagination.hasMore: true` → When SearchPalette renders → Then "Load more" button is visible. When clicked → Then page increments, new results append to existing, and button hides when hasMore is false.
**Files**: `src/app/components/SearchPalette.tsx`, `src/app/components/SearchPalette.test.tsx`
**Notes**: Add page state (starts at 1). On "Load more", increment page and append results to allResults array. Reset page to 1 on query change.

### T-020: Add empty state with "Browse by category" link
**User Story**: US-005 | **Satisfies ACs**: AC-US5-05 | **Status**: [x] completed
**Test**: Given API returns empty results for a query → When SearchPalette renders → Then "No results" text and a "Browse by category" link pointing to /skills are displayed
**Files**: `src/app/components/SearchPalette.tsx`, `src/app/components/SearchPalette.test.tsx`
**Notes**: Replace current minimal "No results" div with enhanced empty state including the browse link.
