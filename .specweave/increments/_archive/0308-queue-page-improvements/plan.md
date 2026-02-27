# Implementation Plan: Queue Page Improvements

## Overview

Four independent fixes targeting the queue page and its backend. All changes are within the vskill-platform repo. No new dependencies, no schema migrations, no new API routes.

## Architecture

### Components Affected

1. **`src/app/queue/page.tsx`** -- SSE handler, polling effect, pagination UI, search filter logic
2. **`src/lib/submission-store.ts`** -- `MAX_INDEX_ENTRIES` constant
3. **`src/app/api/v1/submissions/search/route.ts`** -- state filter expansion

### Data Flow (Current vs Fixed)

**US-001 (SSE/Polling Reset)**:
- Current: `submission_created` SSE -> `fetchQueue()` (no args) -> uses closure defaults -> correct page
- Bug: If `fetchQueue` reference in the SSE callback is stale (captured before page change), it fetches with old params. The real fix is ensuring `fetchQueue` is always called with current params.
- Fix: Remove the bare `fetchQueue()` call from SSE handler. Instead, use a ref to always access the latest `fetchQueue` without recreating the SSE callback.

**US-003 (Search Filter)**:
- Current: Queue page `getStateForFilter("active")` -> "RECEIVED" -> search API `where.state = "RECEIVED"` -> misses TIER1_SCANNING, TIER2_SCANNING
- Fix: Queue page passes `filterParam` directly (e.g., "active") -> search API checks `isCategoryName()` -> expands via `expandStateCategory()` -> Prisma `where.state = { in: [...] }`

## Technology Stack

- **Framework**: Next.js 15 (App Router, React client components)
- **Runtime**: Cloudflare Workers (via OpenNext)
- **Storage**: Cloudflare KV (submission index), Prisma/D1 (search)
- **Testing**: Vitest + React Testing Library

## Implementation Phases

### Phase 1: Backend Fixes (US-002, US-003)
- Raise `MAX_INDEX_ENTRIES` from 500 to 2000 (one-line change)
- Add category expansion to search API route (import + conditional logic)

### Phase 2: Frontend Fixes (US-001, US-004)
- Stabilize SSE/polling pagination (ref-based fetchQueue access)
- Replace Previous/Next with page-number pagination component
- Remove `getStateForFilter()` function, pass category name directly

## Testing Strategy

- **US-001**: Unit test verifying `fetchQueue` is called with current page params after SSE event
- **US-002**: Unit test asserting `MAX_INDEX_ENTRIES === 2000` and index truncation at 2000
- **US-003**: Integration test for search API with `state=active` returning expanded states
- **US-004**: Component test for page number rendering, ellipsis logic, click behavior

## Technical Challenges

### Challenge 1: Stale Closure in SSE Callback
**Solution**: Store `fetchQueue` in a ref (`fetchQueueRef.current = fetchQueue`) and call `fetchQueueRef.current()` from the SSE handler. This avoids recreating the SSE subscription on every `fetchQueue` change while always invoking the latest version.
**Risk**: Low -- this is a standard React pattern for stable callbacks.

### Challenge 2: Prisma `where.state` with Category Expansion
**Solution**: When `isCategoryName(stateFilter)` is true, use `where.state = { in: expandStateCategory(stateFilter) }` instead of `where.state = stateFilter`. This matches the pattern already used in the main submissions route.
**Risk**: None -- `expandStateCategory` is battle-tested in the main route.

### Challenge 3: Page Number Ellipsis Algorithm
**Solution**: Standard windowed pagination: always show first page, last page, current +/- 1 sibling. Insert "..." between non-contiguous ranges. This is a pure function with no side effects.
**Risk**: None -- well-understood UI pattern.

## Architecture Decisions

- **No new components**: The pagination page-number logic will be inline in `page.tsx` or a small helper function, not a separate component file. The queue page is already self-contained.
- **No new API routes**: State expansion is added to the existing search route. No breaking changes.
- **Backward compatibility**: The search API still accepts raw state values (e.g., "RECEIVED") in addition to category names. The main submissions endpoint is unchanged.
