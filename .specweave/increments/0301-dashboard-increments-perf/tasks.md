# Tasks: Dashboard Increments List Performance Optimization

## Task Notation

- `[T###]`: Task ID
- `[P]`: Parallelizable
- `[ ]`: Not started
- `[x]`: Completed
- Model hints: haiku (simple), opus (default)

## Phase 1: Backend Caching & Async I/O

### US-001: Fast Increments Loading with Server-Side Caching (P1)

#### T-001: Add in-memory TTL cache for increments data
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01 | **Status**: [ ] not started

**Description**: Add `incrementsCache`, `incrementsCacheTime`, and `incrementsCacheTTL` private fields to `DashboardDataAggregator`, following the exact pattern of the existing `analyticsCache`. Modify `getIncrements()` to check cache first and return cached data on hit.

**Implementation Details**:
- Add three fields: `private incrementsCache: { increments: IncrementSummary[]; summary: Record<string, number> } | null = null`, `private incrementsCacheTime = 0`, `private readonly incrementsCacheTTL = 30_000`
- In `getIncrements()`, add cache check at the top: if cache exists and `Date.now() - incrementsCacheTime < incrementsCacheTTL`, return cached data
- After computing the result (from dashboard.json or filesystem scan), store in cache before returning
- Add public `invalidateIncrementsCache()` method that sets `incrementsCache = null`

**Test Plan**:
- **File**: `tests/unit/dashboard/dashboard-data-aggregator.test.ts`
- **Tests**:
  - **TC-001**: Cache returns same data on subsequent calls within TTL
    - Given a DashboardDataAggregator with populated increments
    - When getIncrements() is called twice within 30s
    - Then both calls return identical data and filesystem is read only once
  - **TC-002**: Cache expires after TTL
    - Given a DashboardDataAggregator with cached data
    - When TTL elapses and getIncrements() is called
    - Then fresh data is read from filesystem
  - **TC-003**: invalidateIncrementsCache() forces re-read
    - Given a DashboardDataAggregator with cached data
    - When invalidateIncrementsCache() is called then getIncrements()
    - Then fresh data is read from filesystem

**Dependencies**: None

---

#### T-002: Convert readJsonFile() to async
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02 | **Status**: [ ] not started

**Description**: Convert the private `readJsonFile()` method from sync `fs.readFileSync`/`fs.existsSync` to async `fs.promises.readFile`/`fs.promises.access`. Update all callers.

**Implementation Details**:
- Import `fs.promises` as `fsp` (or use `import { readFile, access } from 'fs/promises'`)
- Change `readJsonFile()` signature to `private async readJsonFile(relativePath: string): Promise<any>`
- Replace `fs.existsSync(fullPath)` with try/catch around `await fsp.access(fullPath)`
- Replace `fs.readFileSync(fullPath, 'utf-8')` with `await fsp.readFile(fullPath, 'utf-8')`
- Update callers: `readDashboardJson()`, `readSyncMetadata()`, `readNotifications()`, `readConfig()` all become async
- All public methods that call these are already `async`, so no signature changes needed upstream

**Test Plan**:
- **File**: `tests/unit/dashboard/dashboard-data-aggregator.test.ts`
- **Tests**:
  - **TC-004**: readJsonFile returns parsed JSON for valid file
    - Given a valid JSON file at the expected path
    - When readJsonFile is called (via getConfig())
    - Then the parsed JSON object is returned
  - **TC-005**: readJsonFile returns null for missing file
    - Given no file exists at the path
    - When readJsonFile is called
    - Then null is returned without throwing

**Dependencies**: None

---

#### T-003: Convert scanIncrementsFromFilesystem() to async
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02 | **Status**: [ ] not started

**Description**: Convert `scanIncrementsFromFilesystem()` from synchronous to async. This is the critical hot path that currently does ~7 sync I/O calls per increment.

**Implementation Details**:
- Change signature to `async scanIncrementsFromFilesystem(): Promise<IncrementSummary[]>`
- Replace `fs.existsSync(incrementsDir)` with `try { await fsp.access(incrementsDir) } catch { return [] }`
- Replace `fs.readdirSync(incrementsDir, { withFileTypes: true })` with `await fsp.readdir(incrementsDir, { withFileTypes: true })`
- For each entry: replace `fs.existsSync(metadataPath)` with access check, `fs.readFileSync(metadataPath, 'utf-8')` with `await fsp.readFile()`
- Replace `fs.statSync(metadataPath)` with `await fsp.stat(metadataPath)`
- Convert `countTasksFromFile()` and `countAcsFromFile()` to async as well (they each do existsSync + readFileSync)
- Update callers in `getIncrements()` and `getOverview()` to await

**Test Plan**:
- **File**: `tests/unit/dashboard/dashboard-data-aggregator.test.ts`
- **Tests**:
  - **TC-006**: Async scan produces identical results to sync scan
    - Given a directory with 5 increment folders containing metadata.json, tasks.md, spec.md
    - When scanIncrementsFromFilesystem() is called
    - Then all 5 increments are returned with correct id, title, status, tasks, acs counts
  - **TC-007**: Async scan handles missing/corrupt metadata gracefully
    - Given some increment folders with missing or invalid metadata.json
    - When scanIncrementsFromFilesystem() is called
    - Then only valid increments are returned, corrupt ones are skipped

**Dependencies**: T-002

---

#### T-004: Share scan results between getOverview() and getIncrements()
**User Story**: US-001 | **Satisfies ACs**: AC-US1-03 | **Status**: [ ] not started

**Description**: Eliminate the redundant filesystem scan in `getOverview()`. Currently `getOverview()` independently calls `this.scanIncrementsFromFilesystem()` on line 41. It should instead call `this.getIncrements()` which will use the cache.

**Implementation Details**:
- In `getOverview()`, replace: `const summary = dashboard?.summary ?? this.buildSummaryFromIncrements(this.scanIncrementsFromFilesystem());`
- With: `const incrementData = await this.getIncrements(); const summary = incrementData.summary;`
- This ensures both endpoints share the same cached scan results
- Remove the direct call to `scanIncrementsFromFilesystem()` from `getOverview()`

**Test Plan**:
- **File**: `tests/unit/dashboard/dashboard-data-aggregator.test.ts`
- **Tests**:
  - **TC-008**: getOverview() and getIncrements() share cache
    - Given a DashboardDataAggregator with no dashboard.json
    - When getOverview() then getIncrements() are called
    - Then filesystem is scanned only once (the second call uses cache)

**Dependencies**: T-001, T-003

---

#### T-005: Wire cache invalidation to file watcher events
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01 | **Status**: [ ] not started

**Description**: When the `FileWatcher` detects changes in the increments directory, call `invalidateIncrementsCache()` on the aggregator so the next request gets fresh data.

**Implementation Details**:
- In `DashboardServer.addProject()`, in the `watcher` callback (line 97-106), add: `if (event.type === 'increment-update') { aggregator.invalidateIncrementsCache(); }`
- This ensures cache is invalidated before the SSE event reaches the frontend
- The next API call from the frontend (triggered by the SSE event) will get fresh data

**Test Plan**:
- **File**: `tests/unit/dashboard/dashboard-data-aggregator.test.ts`
- **Tests**:
  - **TC-009**: Cache is invalidated when invalidateIncrementsCache() is called
    - Given cached increment data
    - When invalidateIncrementsCache() is called
    - Then next getIncrements() call performs a fresh scan

**Dependencies**: T-001

---

## Phase 2: Server-Side Pagination

### US-002: Server-Side Pagination for Increments API (P1)

#### T-006: Extend IncrementListPayload type with pagination metadata
**User Story**: US-002 | **Satisfies ACs**: AC-US2-03 | **Status**: [ ] not started

**Description**: Add pagination metadata fields to the `IncrementListPayload` interface.

**Implementation Details**:
- In `types.ts`, modify `IncrementListPayload`:
  ```typescript
  export interface IncrementListPayload {
    increments: IncrementSummary[];
    summary: Record<string, number>;
    pagination: {
      total: number;
      limit: number;
      offset: number;
      hasMore: boolean;
    };
  }
  ```
- Update `getIncrements()` return type to include full (unpaginated) data -- pagination is applied at the route handler level

**Dependencies**: None

---

#### T-007: Add server-side pagination and filtering to /api/increments route
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-05 | **Status**: [ ] not started

**Description**: Parse pagination and filter query parameters in the `/api/increments` route handler. Apply filtering and pagination on the server side.

**Implementation Details**:
- In `dashboard-server.ts`, update the `/api/increments` GET handler:
  ```typescript
  const url = new URL(req.url || '/', `http://${req.headers.host || 'localhost'}`);
  const limit = safeParseInt(url.searchParams.get('limit'), 50, 1, 500);
  const offset = safeParseInt(url.searchParams.get('offset'), 0, 0, 100000);
  const statusFilter = url.searchParams.get('status') || undefined;
  const typeFilter = url.searchParams.get('type') || undefined;
  ```
- Get full increment data from aggregator: `const fullData = await project.aggregator.getIncrements();`
- Apply filters on `fullData.increments` (filter by status, type if provided)
- Compute `total` as filtered length, then slice with offset/limit
- Summary always comes from the full unfiltered dataset
- Return: `{ increments: page, summary: fullData.summary, pagination: { total, limit, offset, hasMore: offset + limit < total } }`

**Test Plan**:
- **File**: `tests/unit/dashboard/dashboard-data-aggregator.test.ts`
- **Tests**:
  - **TC-010**: Pagination returns correct slice
    - Given 100 increments in cache
    - When limit=20, offset=40
    - Then increments[40..59] are returned with hasMore=true
  - **TC-011**: Status filter applied correctly
    - Given increments with mixed statuses
    - When status=active filter applied
    - Then only active increments returned, total reflects filtered count
  - **TC-012**: Default pagination returns first 50
    - Given 100 increments
    - When no limit/offset specified
    - Then first 50 returned with hasMore=true

**Dependencies**: T-006, T-001

---

## Phase 3: Frontend Optimization

### US-003: Smart SSE Refetch Behavior (P2)

#### T-008: Add SSE debounce to IncrementsPage
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-03 | **Status**: [ ] not started

**Description**: Add debounced SSE event handling to prevent rapid-fire full refetches when multiple increment files change in quick succession.

**Implementation Details**:
- Replace the current `useSSEEvent('increment-update', () => setRefreshKey((k) => k + 1))` pattern
- Add a `useRef` for the debounce timer:
  ```typescript
  const debounceRef = useRef<ReturnType<typeof setTimeout>>();
  useSSEEvent('increment-update', () => {
    if (debounceRef.current) clearTimeout(debounceRef.current);
    debounceRef.current = setTimeout(() => setRefreshKey((k) => k + 1), 500);
  });
  ```
- Clean up timer in useEffect cleanup

**Test Plan**:
- Manual verification: multiple rapid SSE events result in single refetch
- **TC-013**: Verify debounce timer is set and cleared correctly (code review)

**Dependencies**: None

---

#### T-009: Update IncrementsPage for server-side pagination
**User Story**: US-002 | **Satisfies ACs**: AC-US2-04 | **Status**: [ ] not started

**Description**: Update `IncrementsPage` to use server-side pagination and filtering instead of loading all increments and filtering client-side.

**Implementation Details**:
- Add pagination state: `const [page, setPage] = useState(0); const pageSize = 50;`
- Pass filter and pagination params to API: `/api/increments?limit=${pageSize}&offset=${page * pageSize}&status=${statusFilter !== 'all' ? statusFilter : ''}&type=${typeFilter !== 'all' ? typeFilter : ''}`
- Update interface to include `pagination` field from response
- Replace client-side filtering logic (lines 41-45) with server-side params
- Add "Load More" button or page navigation at bottom of table
- When filters change, reset offset to 0
- Summary counts should come from the full dataset (server sends these in `summary`)
- Keep filter chip counts from `summary` field instead of computing from local `data.increments`

**Test Plan**:
- Manual verification: page loads with first 50 increments, "Load More" fetches next page
- **TC-014**: Verify filter changes reset pagination to page 0

**Dependencies**: T-007, T-008

---

## Phase 4: Testing & Validation

### US-004: Performance Test Coverage (P2)

#### T-010: Write unit tests for cache mechanism
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01 | **Status**: [ ] not started

**Description**: Write comprehensive unit tests for the TTL cache mechanism added in T-001.

**Implementation Details**:
- Extend `tests/unit/dashboard/dashboard-data-aggregator.test.ts`
- Test cases: TC-001, TC-002, TC-003 from T-001
- Mock `fs/promises` module using `vi.hoisted()` + `vi.mock()` for ESM compatibility
- Use `vi.advanceTimersByTime()` for TTL expiry testing

**Dependencies**: T-001, T-003

---

#### T-011: Write unit tests for async scan and pagination
**User Story**: US-004 | **Satisfies ACs**: AC-US4-02, AC-US4-03, AC-US4-04 | **Status**: [ ] not started

**Description**: Write unit tests for the async filesystem scan and pagination logic.

**Implementation Details**:
- Test cases: TC-006, TC-007, TC-008, TC-010, TC-011, TC-012 from earlier tasks
- Create test fixtures with mock increment directory structure
- Verify async scan produces the same structure as the original sync version
- Test pagination edge cases: empty results, offset beyond total, limit=0

**Dependencies**: T-003, T-007

---

#### T-012: Verify existing tests pass after async migration
**User Story**: US-004 | **Satisfies ACs**: AC-US4-02 | **Status**: [ ] not started

**Description**: Run the full test suite to ensure the sync-to-async migration does not break existing functionality.

**Implementation Details**:
- Run `npm test` in the specweave repo
- Fix any tests that break due to the async conversion
- Ensure existing `dashboard-data-aggregator.test.ts` tests are updated for async methods

**Dependencies**: T-002, T-003, T-004
