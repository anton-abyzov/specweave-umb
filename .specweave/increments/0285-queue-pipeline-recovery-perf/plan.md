# Implementation Plan: Queue Pipeline Recovery + Q Page Performance Overhaul

## Overview

Two-track fix: (1) unblock the build/deploy pipeline with TypeScript fixes and queue pause TTL, (2) overhaul the Q page from client-side-everything to server-side pagination with SSE in-place updates.

## Architecture

### Current State

The `/queue` page fetches all submissions via `GET /api/v1/submissions?limit=500`, which reads a single KV blob (`submissions:index`) containing up to 500 serialized entries. All filtering, sorting, and pagination happen client-side. Every SSE event triggers a full refetch of all 500 rows.

### Target State

```
Browser                          API                           KV
  |                               |                             |
  |-- GET /submissions?limit=50   |                             |
  |   &offset=0&state=RECEIVED    |-- get("submissions:index")--|
  |   &sort=createdAt&sortDir=desc|                             |
  |                               |-- filter+sort+slice in-mem--|
  |<-- { submissions[50], total } |                             |
  |                               |                             |
  |-- GET /submissions/stats      |-- get("submissions:index")--|
  |<-- { total, active, ... }     |-- count by category---------|
  |                               |                             |
  |<== SSE state_changed =========|                             |
  |-- update row in React state   |                             |
  |   (NO refetch)                |                             |
```

### Components Modified

1. **`src/app/queue/page.tsx`** - Rewrite fetch logic to server-side pagination, SSE in-place updates
2. **`src/app/api/v1/submissions/route.ts` GET** - Add server-side sort/filter before slicing
3. **`src/app/api/v1/submissions/stats/route.ts`** - New lightweight stats endpoint
4. **`src/app/api/v1/admin/queue/pause/route.ts`** - Add TTL to KV put
5. **`src/app/components/AnimatedTerminal.tsx`** - useRef fix
6. **`src/app/components/ThemeToggle.tsx`** - useRef fix

### API Contracts

#### GET /api/v1/submissions (modified)

Request params:
- `limit` (int, 1-500, default 50)
- `offset` (int, default 0)
- `state` (string, optional - SubmissionState enum value or category: "active"|"published"|"rejected")
- `sort` (string, optional - "createdAt"|"updatedAt"|"skillName"|"state", default "createdAt")
- `sortDir` (string, optional - "asc"|"desc", default "desc")

Response: `{ submissions: SubmissionSummary[], total: number }`

The `state` param supports both individual states (RECEIVED, TIER1_SCANNING, etc.) and category shortcuts:
- `active` -> RECEIVED, TIER1_SCANNING, TIER2_SCANNING
- `published` -> AUTO_APPROVED, PUBLISHED, VENDOR_APPROVED
- `rejected` -> REJECTED, TIER1_FAILED, DEQUEUED

#### GET /api/v1/submissions/stats (new)

Response:
```json
{
  "total": 142,
  "active": 3,
  "published": 120,
  "rejected": 19,
  "avgScore": 78
}
```

#### POST /api/v1/admin/queue/pause (modified)

Request body (optional): `{ "ttlSeconds": 3600 }`
- Default: 3600 (1 hour)
- Max: 86400 (24 hours)
- KV put uses `expirationTtl` so flag auto-expires

## Technology Stack

- **Framework**: Next.js 15 on Cloudflare Workers (existing)
- **Storage**: Cloudflare KV for submissions index (existing)
- **Queue**: Cloudflare Queues (existing)
- **Testing**: Vitest (existing)

**Architecture Decisions**:

- **Keep KV index as primary data source for Q page**: The KV index is already fast (single read) and capped at 500 entries. Server-side filter/sort on a 500-element array in memory is negligible. No need to introduce Prisma queries for the main Q page when KV already works well.
- **Category shortcuts in state param**: Rather than requiring the frontend to know which SubmissionState values map to "active" vs "published", the API accepts category names and expands them server-side. This keeps the frontend simple.
- **SSE in-place updates over WebSocket**: The SSE infrastructure already exists and works. The issue is purely in the handler (calling fetchQueue). No need to add WebSocket complexity.

## Implementation Phases

### Phase 1: Pipeline Unblock (US-001, US-002) - 30 min

1. Fix useRef TypeScript errors (3 files)
2. Add TTL to queue pause endpoint
3. Verify build succeeds locally

### Phase 2: API + Stats Endpoint (US-003, US-005) - 1 hour

1. Add sort/filter logic to GET /api/v1/submissions
2. Create GET /api/v1/submissions/stats
3. Write tests for both

### Phase 3: Q Page Overhaul (US-003, US-004) - 2 hours

1. Refactor queue/page.tsx fetch to use server-side params
2. Implement SSE in-place update handler
3. Add optimistic stat counter updates
4. Increase polling fallback interval

## Testing Strategy

- Unit tests for sort/filter logic in submissions API
- Unit tests for stats aggregation
- Unit tests for SSE in-place update reducer
- Integration test for queue pause TTL
- Manual verification of build + deploy

## Technical Challenges

### Challenge 1: KV Index Sorted by createdAt DESC by Default
**Issue**: The KV index is maintained by `addToIndex()` which uses `unshift()` (newest first). When the user requests `sort=skillName&sortDir=asc`, we need to re-sort in memory.
**Solution**: Apply `Array.sort()` on the 500-entry array before slicing. Performance is negligible for 500 items.
**Risk**: None - in-memory sort on 500 items takes microseconds.

### Challenge 2: Stat Card Counts Must Reflect All Submissions, Not Just Current Page
**Issue**: Currently stat cards derive counts from all 500 loaded submissions. With server-side pagination, we only have 50 rows.
**Solution**: New `/stats` endpoint computes counts from full KV index (single read, ~500 entries). Frontend fetches stats separately from page data.
**Risk**: Two KV reads instead of one. Both cached and fast.

### Challenge 3: SSE State Transition Accuracy for Stat Counters
**Issue**: When a submission transitions from RECEIVED to TIER1_SCANNING, both are "active" states - the active count should not change. But RECEIVED to REJECTED means active -1, rejected +1.
**Solution**: Define state-to-category mapping in a shared utility. SSE handler computes old category and new category, and only updates counters when categories differ.
**Risk**: Edge cases around states not in any category. Mitigated by periodic stats refresh (30s polling).
