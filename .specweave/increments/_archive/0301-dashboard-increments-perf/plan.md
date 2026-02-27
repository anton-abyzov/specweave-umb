# Implementation Plan: Dashboard Increments List Performance Optimization

## Overview

This increment optimizes the dashboard's increments list endpoint (`/api/increments`) and its frontend consumer (`IncrementsPage.tsx`) for projects with 300+ increments. The primary bottleneck is synchronous filesystem I/O in the fallback path, compounded by the absence of caching, pagination, and redundant scans.

The implementation follows a layered approach: first add caching and async I/O at the data layer, then add pagination at the API layer, then optimize the frontend SSE behavior.

## Architecture

### Components Modified

1. **`DashboardDataAggregator`** (`dashboard-data-aggregator.ts`):
   - Add `incrementsCache` + `incrementsCacheTime` + `incrementsCacheTTL` fields (mirrors existing `analyticsCache` pattern)
   - Convert `scanIncrementsFromFilesystem()` from sync to async
   - Convert `countTasksFromFile()` and `countAcsFromFile()` from sync to async
   - Convert `readJsonFile()` from sync to async
   - Add `invalidateIncrementsCache()` public method for SSE-triggered invalidation
   - Modify `getOverview()` to reuse `getIncrements()` cache instead of independent scan

2. **`DashboardServer`** (`dashboard-server.ts`):
   - Modify `/api/increments` route handler to parse `limit`, `offset`, `status`, `type` query params
   - Add pagination metadata to response
   - Wire file watcher `increment-update` events to `invalidateIncrementsCache()`

3. **`IncrementsPage`** (`IncrementsPage.tsx`):
   - Replace client-side-only filtering with server-side filter params
   - Add pagination controls (limit/offset state, "Load More" or page buttons)
   - Debounce SSE-triggered refetches (500ms window)
   - Update type interfaces for paginated response

4. **Types** (`types.ts`):
   - Extend `IncrementListPayload` with pagination metadata

### Data Flow (Current)

```
IncrementsPage -> useProjectApi("/api/increments") -> getIncrements()
  -> readDashboardJson() [sync]
  -> scanIncrementsFromFilesystem() [sync fallback, ~7 I/O ops per increment]
  -> sort + return ALL increments

getOverview() -> scanIncrementsFromFilesystem() [DUPLICATE scan]

SSE: increment-update -> setRefreshKey(k+1) -> FULL re-fetch (no debounce)
```

### Data Flow (Optimized)

```
IncrementsPage -> useProjectApi("/api/increments?limit=50&offset=0&status=active")
  -> getIncrements() -> check incrementsCache (TTL 30s)
    -> cache HIT: return cached data
    -> cache MISS: readDashboardJson() [async] OR scanIncrementsFromFilesystem() [async]
  -> apply server-side filters
  -> apply pagination (limit/offset)
  -> return page + metadata

getOverview() -> getIncrements() [shared cache] -> buildSummaryFromIncrements()

SSE: increment-update -> invalidateIncrementsCache()
     -> IncrementsPage debounces (500ms) -> single refetch
```

## Technology Stack

- **Language/Framework**: TypeScript, Node.js (ESM)
- **Libraries**: `fs/promises` (async I/O), React hooks (frontend)
- **Testing**: Vitest with vi.mock() for fs module mocking

## Architecture Decisions

### ADR-1: In-Memory TTL Cache (not LRU or external)
**Decision**: Simple in-memory TTL cache mirroring the analytics pattern.
**Rationale**: The analytics cache already proves this pattern works well. The data size is bounded (metadata only, not file contents). An LRU cache or Redis would add unnecessary complexity. 30s TTL provides good balance between freshness and performance.
**Alternatives**: LRU cache (overkill for single-key cache), Redis (external dependency), WeakRef-based (harder to reason about TTL).

### ADR-2: Async I/O over Worker Threads
**Decision**: Convert sync fs calls to `fs.promises.*` async equivalents.
**Rationale**: Worker threads add complexity (serialization overhead, thread management). Async I/O via libuv is sufficient for this workload -- the bottleneck is blocking the event loop, not CPU-bound work. The file reads are small (metadata.json, tasks.md headers).
**Alternatives**: Worker threads (too heavy), streaming reads (unnecessary for small files).

### ADR-3: Server-Side Pagination with Full Cache
**Decision**: Cache the full sorted increment list in memory, apply pagination/filtering on the cached array.
**Rationale**: With 300 increments, the full dataset is ~100KB in memory -- trivially small. This allows instant pagination without re-scanning. Filters are applied post-cache, and the summary counts always reflect the unfiltered total.
**Alternatives**: Filesystem-level pagination (complex, fragile), cursor-based (unnecessary for this scale).

### ADR-4: Frontend Debounce over Smart Diffing
**Decision**: Simple 500ms debounce on SSE-triggered refetches.
**Rationale**: The SSE event already triggers server-side cache invalidation. A simple debounce prevents rapid-fire refetches during bulk operations (e.g., closing multiple increments). Smart diffing (comparing SSE payload to local state) would require maintaining a second copy of the data and complex reconciliation logic.
**Alternatives**: Smart diff (complex), SSE partial updates (requires protocol changes).

## Implementation Phases

### Phase 1: Backend Caching & Async I/O (Core Performance)
1. Add increments TTL cache to `DashboardDataAggregator`
2. Convert `readJsonFile()` to async
3. Convert `scanIncrementsFromFilesystem()` to async
4. Convert `countTasksFromFile()` and `countAcsFromFile()` to async
5. Share scan results between `getOverview()` and `getIncrements()`
6. Add cache invalidation method + wire to file watcher

### Phase 2: Server-Side Pagination
1. Update `IncrementListPayload` type with pagination metadata
2. Add query parameter parsing to `/api/increments` route
3. Implement server-side filtering and pagination logic
4. Update response payload format

### Phase 3: Frontend Optimization
1. Add SSE debounce logic to `IncrementsPage`
2. Update `IncrementsPage` to pass pagination/filter params to API
3. Add pagination controls (Load More button)
4. Handle paginated response type

### Phase 4: Testing
1. Unit tests for cache mechanism
2. Unit tests for async scan
3. Unit tests for pagination logic
4. Integration test for cache sharing

## Testing Strategy

- **Unit tests**: Cache TTL behavior, async scan correctness, pagination math, filter logic
- **Mocking**: `fs/promises` module mocked via `vi.mock()` + `vi.hoisted()` for ESM compatibility
- **Existing tests**: Ensure existing `dashboard-data-aggregator.test.ts` tests continue to pass after async conversion
- **Test file**: `tests/unit/dashboard/dashboard-data-aggregator.test.ts` (extend existing)

## Technical Challenges

### Challenge 1: Async Migration Without Breaking Existing Callers
**Solution**: Since `getIncrements()` and `getOverview()` are already declared `async`, and `scanIncrementsFromFilesystem()` is only called internally, the conversion to async is safe. The public method `enrichSyncPlatforms()` is sync and not affected.
**Risk**: Low -- all callers already await the results.

### Challenge 2: Cache Coherence with File Watcher
**Solution**: The `FileWatcher` already watches `.specweave/increments/` recursively and emits `increment-update` SSE events. We add a cache invalidation call in the watcher callback alongside the SSE broadcast.
**Risk**: Edge case where file change is detected but cache is read before invalidation completes. Mitigated by the fact that the watcher has a 300ms debounce already.

### Challenge 3: Backward Compatibility of API Response
**Solution**: Pagination metadata is added as additional fields (`total`, `limit`, `offset`, `hasMore`). The `increments` array and `summary` fields remain in the same structure. Existing clients that don't use pagination will get the first 50 results (reasonable default).
**Risk**: Low -- additive change, no breaking field removals.
