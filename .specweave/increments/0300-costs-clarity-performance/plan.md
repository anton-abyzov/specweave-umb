# 0300 - Architecture Plan

## Current State

### Backend (`cost-aggregator.ts`)
- `CostAggregator` reads JSONL session files from `~/.claude/projects/-{slug}/`
- `getTokenSummaries(limit=200)` has a naive 60s TTL response cache
- On every cache miss, it: `getSessionFiles()` -> `readdirSync` + `statSync` per file for sort -> reads up to 200 files via `createReadStream` + `readline` -> JSON.parse per line -> aggregate
- Concurrency: batches of 15 parallel file reads
- Problem: 200 files x full parse = 1-3 seconds on cold cache; 60s stale window

### Frontend - Costs Page (`CostsPage.tsx`)
- Subscription banner is conditional (`isSubscription && ...`) -- no universal source header
- Sessions table uses client-side pagination (PAGE_SIZE=30) with full DOM rendering of the visible page
- No virtualization

### Frontend - Overview Page (`OverviewPage.tsx`)
- Cost KPI card title is "Usage Value" or "Total Cost" -- no source attribution
- Subscription banner duplicated from Costs page, also conditional

## Target Architecture

### Backend: Two-Level Cache Strategy

```
Request
  |
  v
[Response Cache] -- if valid (all files unchanged) --> return cached response
  |
  v (cache miss or files changed)
[Per-File Cache Map]
  filePath -> { mtimeMs, summary: SessionTokenSummary }
  |
  v (check each file's mtime)
  - Unchanged files: use cached summary
  - Changed files: re-parse, update cache entry
  - New files: parse, add cache entry
  - Deleted files: evict from cache
  |
  v
[Incremental Aggregation]
  - Rebuild totals from all cached summaries (fast Map iteration)
  - Store as response cache
  |
  v
Return CostsSummaryPayload
```

Key design decisions:
1. **No file-system watcher** -- mtime comparison on request is simpler, avoids watcher overhead, works on all platforms
2. **Map<string, { mtimeMs: number; summary: SessionTokenSummary }>** as the per-file cache
3. **Response cache invalidation** -- compare file list hash (sorted filenames + mtimes) against last-known hash
4. **No limit parameter changes** -- the limit still controls how many recent sessions to include in the response, but ALL files are cached for fast subsequent access
5. **No external dependencies** -- uses native Node.js Map

### Frontend: Source Header Design

**Costs Page:**
```
+--------------------------------------------------+
| [CC icon] Claude Code Usage        [refresh btn] |
| Data from local Claude Code session logs          |
+--------------------------------------------------+
| [subscription details if applicable]              |
+--------------------------------------------------+
| KPI cards...                                      |
| ...                                               |
| [subtle] More providers coming soon               |
+--------------------------------------------------+
```

**Overview Page Cost KPI Card:**
- Add subtitle "via Claude Code" or tooltip "Data: Claude Code sessions"

### Frontend: Virtualized Sessions Table

Options considered:
1. **@tanstack/react-virtual** -- ~4KB, well-maintained, React-native
2. **Hand-rolled IntersectionObserver** -- zero deps but more code
3. **react-window** -- proven but heavier

**Decision**: Use a simple hand-rolled approach with a fixed-height container and `overflow-y: auto`, rendering only rows within the visible viewport + buffer. This avoids adding a new dependency and keeps the bundle small. The existing PAGE_SIZE pagination can be replaced by rendering all rows virtually.

If hand-rolled proves too complex with expandable rows, fall back to @tanstack/react-virtual.

## File Changes

### Modified Files
1. `src/dashboard/server/data/cost-aggregator.ts` -- Major refactor: per-file cache, incremental aggregation
2. `src/dashboard/client/src/pages/CostsPage.tsx` -- Source header, "more providers" footer, virtual sessions table
3. `src/dashboard/client/src/pages/OverviewPage.tsx` -- Cost KPI card source label

### New Files (potential)
4. `src/dashboard/server/data/__tests__/cost-aggregator.test.ts` -- TDD tests for cache logic
5. `src/dashboard/client/src/components/VirtualTable.tsx` -- Reusable virtual scroll component (if extracted)

## Risk Assessment

- **Low risk**: UI text changes (US-001, US-002) -- purely presentational
- **Medium risk**: CostAggregator refactor (US-003, US-004) -- must preserve exact API contract, edge cases around file deletion during read
- **Low risk**: Sessions table virtualization (US-005) -- isolated to one component, fallback to pagination if issues arise
