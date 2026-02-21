# Tasks: Bulk Skill Discovery - Scale Queue Ingestion to 60k+

## Task Notation

- `[T###]`: Task ID
- `[P]`: Parallelizable
- `[ ]`: Not started
- `[x]`: Completed
- Model hints: haiku (simple), opus (default)

## Phase 1: DB Models + Migration

### T-001: Add DiscoveryRecord and DiscoveryRunLog Prisma models

**Description**: Add two new models to the Prisma schema for persistent dedup and run observability.

**References**: AC-US2-01, AC-US2-02, AC-US5-02

**Implementation Details**:
- Add `DiscoveryRecord` model with fields: id, repoFullName, skillPath, source, submissionId, firstSeenAt, lastSeenAt
- Add unique constraint on (repoFullName, skillPath)
- Add `DiscoveryRunLog` model with fields: id, trigger, candidatesFound, newSubmissions, skippedDedup, errors, durationMs, sourceBreakdown, createdAt
- Run `npx prisma migrate dev`

**Test Plan**:
- **File**: `src/lib/__tests__/discovery-dedup-db.test.ts`
- **Tests**:
  - **TC-001**: DiscoveryRecord create + unique constraint
    - Given an empty DB
    - When two records with same repoFullName+skillPath are inserted
    - Then the second insert throws a unique constraint error
  - **TC-002**: DiscoveryRecord upsert updates lastSeenAt
    - Given an existing record
    - When upserted with same key
    - Then lastSeenAt is updated, firstSeenAt is preserved
  - **TC-003**: DiscoveryRunLog records run metrics
    - Given a completed discovery run
    - When a DiscoveryRunLog is created
    - Then all fields are persisted and queryable

**Dependencies**: None
**Status**: [x] Completed

---

### T-002: Create DB dedup helper functions

**Description**: Create `hasBeenDiscovered()` and `markDiscovered()` functions that use the DiscoveryRecord table instead of KV.

**References**: AC-US2-03, AC-US2-04, AC-US2-05

**Implementation Details**:
- `hasBeenDiscovered(repoFullName, skillPath): Promise<boolean>` - checks DiscoveryRecord table
- `markDiscovered(repoFullName, skillPath, source, submissionId?): Promise<void>` - upserts DiscoveryRecord, updates lastSeenAt
- `getDiscoveryStats(): Promise<{ total, bySource }>` - for admin stats
- Export from new file `src/lib/crawler/discovery-dedup.ts`

**Test Plan**:
- **File**: `src/lib/crawler/__tests__/discovery-dedup.test.ts`
- **Tests**:
  - **TC-004**: hasBeenDiscovered returns false for new skill
    - Given an empty DiscoveryRecord table
    - When hasBeenDiscovered("owner/repo", "SKILL.md") is called
    - Then it returns false
  - **TC-005**: hasBeenDiscovered returns true after markDiscovered
    - Given markDiscovered("owner/repo", "SKILL.md", "github-code") was called
    - When hasBeenDiscovered("owner/repo", "SKILL.md") is called
    - Then it returns true
  - **TC-006**: markDiscovered updates lastSeenAt on re-encounter
    - Given an existing DiscoveryRecord from 1 hour ago
    - When markDiscovered is called again
    - Then lastSeenAt is updated, firstSeenAt unchanged
  - **TC-007**: markDiscovered links submissionId
    - Given a new discovery
    - When markDiscovered is called with submissionId
    - Then the record has submissionId set

**Dependencies**: T-001
**Status**: [x] Completed

---

## Phase 2: Paginated Search + DB Dedup

### T-003: Refactor GitHub search to paginate results [P]

**Description**: Modify `discoverFromCodeSearch` and `discoverFromRepoSearch` to fetch multiple pages (up to 10 pages of 100 results each).

**References**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04

**Implementation Details**:
- Change `per_page=30` to `per_page=100`
- Add page loop: `for page 1..10`, stop when results < per_page or page > 10
- Parse `Link` header for `rel="next"` or just increment `&page=N`
- Add backoff: on 403/429, wait `Retry-After` header or 60s, then retry once
- Log `total_count` from first page response
- Process each page before fetching next (yield results to caller)

**Test Plan**:
- **File**: `src/lib/crawler/__tests__/github-discovery-pagination.test.ts`
- **Tests**:
  - **TC-008**: Fetches multiple pages when results span pages
    - Given GitHub search returns total_count=250 with 3 pages of 100
    - When discoverFromCodeSearch runs
    - Then all 250 results are returned
  - **TC-009**: Stops at page 10 even if more results exist
    - Given GitHub search returns total_count=5000
    - When discoverFromCodeSearch runs
    - Then exactly 10 requests are made (1000 results max)
  - **TC-010**: Stops early when page has fewer results than per_page
    - Given page 3 returns 42 items (less than 100)
    - When pagination loop runs
    - Then no page 4 request is made
  - **TC-011**: Backs off on 403 response
    - Given page 2 returns 403
    - When pagination encounters the error
    - Then it waits 60s and retries once, then stops on second failure
  - **TC-012**: Logs total_count vs fetched count
    - Given a query with total_count=500, fetched 500
    - When discovery completes
    - Then console.log includes "[discovery:code] query X: 500/500 fetched"

**Dependencies**: None (can parallelize with T-001/T-002 since this is pure function refactor)
**Status**: [x] Completed

---

### T-004: Wire DB dedup into runGitHubDiscovery

**Description**: Replace KV-based `hasBeenSeen`/`markSeen` with the new DB-based `hasBeenDiscovered`/`markDiscovered`. Remove SEEN_TTL and KV dedup code.

**References**: AC-US2-03, AC-US2-04, AC-US2-06

**Implementation Details**:
- Import `hasBeenDiscovered`, `markDiscovered` from `./discovery-dedup`
- Replace `hasBeenSeen(env.QUEUE_METRICS_KV, ...)` with `hasBeenDiscovered(...)`
- Replace `markSeen(env.QUEUE_METRICS_KV, ...)` with `markDiscovered(..., submissionId)`
- Remove `seenKey()`, `hasBeenSeen()`, `markSeen()` functions
- Remove `SEEN_TTL` constant
- Remove `QUEUE_METRICS_KV` from DiscoveryEnv (if no longer needed elsewhere)
- Add `logDiscoveryRun()` call at end to write DiscoveryRunLog

**Test Plan**:
- **File**: `src/lib/crawler/__tests__/github-discovery.test.ts` (update existing)
- **Tests**:
  - **TC-013**: runGitHubDiscovery skips already-discovered skills
    - Given DiscoveryRecord exists for "owner/repo" + "SKILL.md"
    - When runGitHubDiscovery encounters the same skill
    - Then it skips submission and updates lastSeenAt
  - **TC-014**: runGitHubDiscovery creates DiscoveryRecord for new skills
    - Given no DiscoveryRecord for "owner/repo" + "SKILL.md"
    - When runGitHubDiscovery discovers it
    - Then a DiscoveryRecord is created with submissionId linked
  - **TC-015**: runGitHubDiscovery writes DiscoveryRunLog
    - Given a discovery run completes
    - When the run finishes
    - Then a DiscoveryRunLog is created with correct metrics

**Dependencies**: T-002, T-003
**Status**: [x] Completed

---

## Phase 3: Admin Endpoints

### T-005: Implement POST /api/v1/admin/discovery/bulk [P]

**Description**: New admin endpoint for triggering bulk discovery with custom parameters.

**References**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04, AC-US3-05, AC-US3-06

**Implementation Details**:
- Create `src/app/api/v1/admin/discovery/bulk/route.ts`
- Auth: X-Internal-Key or SUPER_ADMIN JWT (reuse from existing admin/discovery)
- Parse body: `{ sources?: string[], maxResults?: number, dryRun?: boolean }`
- Validate: maxResults 1-5000 (default 500), sources from known set
- Call refactored `runGitHubDiscovery` with options: `{ maxResults, sources, dryRun }`
- On dryRun, return candidates array without submitting
- Return summary: candidatesFound, newSubmissions, skippedDedup, skippedErrors, durationMs

**Test Plan**:
- **File**: `src/app/api/v1/admin/discovery/bulk/__tests__/route.test.ts`
- **Tests**:
  - **TC-016**: Rejects unauthenticated requests with 401/403
    - Given no auth header
    - When POST /api/v1/admin/discovery/bulk is called
    - Then 401 or 403 is returned
  - **TC-017**: Accepts X-Internal-Key authentication
    - Given valid X-Internal-Key header
    - When POST /api/v1/admin/discovery/bulk is called
    - Then discovery runs and 200 is returned
  - **TC-018**: dryRun=true returns candidates without submitting
    - Given dryRun=true in body
    - When bulk discovery runs
    - Then candidates are returned, no submissions created
  - **TC-019**: maxResults caps number of submissions
    - Given maxResults=10 in body
    - When bulk discovery runs
    - Then at most 10 submissions are created
  - **TC-020**: sources filter limits crawl sources
    - Given sources=["github-code"] in body
    - When bulk discovery runs
    - Then only github-code search is executed
  - **TC-021**: Validates maxResults range (1-5000)
    - Given maxResults=10000 in body
    - When POST is called
    - Then 400 error with validation message

**Dependencies**: T-004
**Status**: [x] Completed

---

### T-006: Implement GET /api/v1/admin/discovery/stats [P]

**Description**: Admin endpoint to query recent discovery run metrics.

**References**: AC-US5-02, AC-US5-03

**Implementation Details**:
- Create `src/app/api/v1/admin/discovery/stats/route.ts`
- Auth: X-Internal-Key or SUPER_ADMIN JWT
- Query DiscoveryRunLog table, last N runs (default 30, max 100)
- Return: `{ runs: DiscoveryRunLog[], total: number }`

**Test Plan**:
- **File**: `src/app/api/v1/admin/discovery/stats/__tests__/route.test.ts`
- **Tests**:
  - **TC-022**: Returns empty array when no runs exist
    - Given no DiscoveryRunLog records
    - When GET /api/v1/admin/discovery/stats is called
    - Then { runs: [], total: 0 } is returned
  - **TC-023**: Returns runs sorted by createdAt desc
    - Given 3 DiscoveryRunLog records
    - When stats endpoint is called
    - Then runs are returned newest first
  - **TC-024**: Respects limit parameter
    - Given 50 run records
    - When limit=10 is passed
    - Then only 10 runs are returned
  - **TC-025**: Rejects unauthenticated requests
    - Given no auth header
    - When GET /api/v1/admin/discovery/stats is called
    - Then 401/403 is returned

**Dependencies**: T-001
**Status**: [x] Completed

---

## Phase 4: Expanded Queries + Cap Raise

### T-007: Add expanded search queries

**Description**: Add more CODE_SEARCH_QUERIES and REPO_SEARCH_QUERIES to cover additional skill patterns.

**References**: AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-04

**Implementation Details**:
- Add to CODE_SEARCH_QUERIES:
  - `"filename:skill.md"` (lowercase)
  - `"filename:SKILL.md"` (any path, broader)
  - `"path:.claude/commands extension:md"` (alternate path syntax)
  - `"filename:commands.md path:/.claude/"` (single-file command pattern)
- Add to REPO_SEARCH_QUERIES:
  - `"topic:mcp-server"`
  - `"topic:claude-code"`
  - `"topic:ai-skill"`
  - `'"SKILL.md" in:readme'`
  - `'"claude code" skill in:description'`
- Verify dedup across queries (same `seen` Set within a run)

**Test Plan**:
- **File**: `src/lib/crawler/__tests__/github-discovery-queries.test.ts`
- **Tests**:
  - **TC-026**: All new queries produce valid GitHub API URLs
    - Given the expanded query list
    - When each query is URL-encoded and used in fetch
    - Then the URL is valid and parseable
  - **TC-027**: Dedup works across queries (same repo in multiple query results)
    - Given repo "owner/skill" appears in both code and repo search
    - When both queries run
    - Then only one DiscoveredRepo entry exists for that fullName
  - **TC-028**: Existing queries are preserved unchanged
    - Given the original CODE_SEARCH_QUERIES and REPO_SEARCH_QUERIES
    - When the module is loaded
    - Then all original queries are present in the arrays

**Dependencies**: T-003
**Status**: [x] Completed

---

### T-008: Raise MAX_PER_CRON and add source filtering

**Description**: Raise the per-run submission cap and add source filtering to runGitHubDiscovery.

**References**: AC-US5-01, AC-US3-06

**Implementation Details**:
- Change `MAX_PER_CRON = 100` to `MAX_PER_CRON = 500`
- Add `options` parameter to `runGitHubDiscovery`: `{ maxResults?: number, sources?: string[], dryRun?: boolean }`
- When sources is provided, only run the matching source functions
- When maxResults is provided, use it instead of MAX_PER_CRON
- When dryRun is true, collect candidates but skip submission

**Test Plan**:
- **File**: `src/lib/crawler/__tests__/github-discovery-options.test.ts`
- **Tests**:
  - **TC-029**: Default MAX_PER_CRON is 500
    - Given no options override
    - When runGitHubDiscovery runs
    - Then it stops after 500 new submissions
  - **TC-030**: maxResults overrides MAX_PER_CRON
    - Given options.maxResults = 50
    - When runGitHubDiscovery runs
    - Then it stops after 50 new submissions
  - **TC-031**: sources filter limits which discovery functions run
    - Given options.sources = ["npm"]
    - When runGitHubDiscovery runs
    - Then only discoverFromNpm is called
  - **TC-032**: dryRun collects candidates without submitting
    - Given options.dryRun = true
    - When runGitHubDiscovery runs
    - Then candidates are returned, no fetch to submissions endpoint

**Dependencies**: T-004
**Status**: [x] Completed

---

## Phase 5: Integration + Verification

### T-009: Update existing discovery endpoint to use refactored code

**Description**: Update POST /api/v1/admin/discovery to use the refactored `runGitHubDiscovery` with DB dedup.

**References**: AC-US2-06

**Implementation Details**:
- Update imports in `src/app/api/v1/admin/discovery/route.ts`
- Remove QUEUE_METRICS_KV from DiscoveryEnv if fully migrated
- Ensure backward compatibility (same response format)
- Add DiscoveryRunLog writing to existing endpoint

**Test Plan**:
- **File**: `src/app/api/v1/admin/discovery/__tests__/route.test.ts`
- **Tests**:
  - **TC-033**: Existing discovery endpoint still works after refactor
    - Given authenticated admin request
    - When POST /api/v1/admin/discovery is called
    - Then discovery runs and returns { ok: true, message, durationMs }
  - **TC-034**: Discovery run creates DiscoveryRunLog entry
    - Given a successful discovery run via admin endpoint
    - When the run completes
    - Then a DiscoveryRunLog record exists in DB

**Dependencies**: T-004, T-005
**Status**: [x] Completed

---

### T-010: End-to-end verification

**Description**: Verify the full pipeline: paginated search -> DB dedup -> submission -> run log.

**References**: All ACs

**Implementation Details**:
- Run discovery locally with test GitHub token
- Verify pagination fetches multiple pages
- Verify DiscoveryRecord entries are created
- Verify DiscoveryRunLog has correct metrics
- Verify bulk endpoint works with dryRun and real mode
- Verify no duplicate submissions across back-to-back runs

**Test Plan**:
- **File**: Manual + `src/lib/crawler/__tests__/github-discovery-e2e.test.ts`
- **Tests**:
  - **TC-035**: Back-to-back runs produce 0 duplicates
    - Given a first run that discovers N skills
    - When a second run executes immediately after
    - Then newSubmissions = 0 (all deduped)
  - **TC-036**: Bulk endpoint with dryRun shows candidates
    - Given dryRun=true
    - When bulk endpoint is called
    - Then candidates array is returned, DB unchanged

**Dependencies**: T-005, T-006, T-007, T-008, T-009
**Status**: [x] Completed
