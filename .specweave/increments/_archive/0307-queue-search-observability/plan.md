# Implementation Plan: Queue Search, Observability & Monitoring for Admin

## Overview

Enhance the admin queue page with search/filter, per-state distribution counts, and real-time updates. Optimize dashboard state count loading. All changes leverage existing Prisma schema, indexes, SSE stream, and REVIEWER auth — no new infrastructure needed.

## Architecture

### Current State

```
/admin/queue      → metrics, DLQ, stuck submissions (NO search)
/admin/submissions → search + state filter + pagination (Prisma-backed)
/admin/dashboard   → stat cards + N+1 state queries
SSE stream         → broadcasts state_changed, submission_created, scan_complete
```

### Target State

```
/admin/queue      → [NEW] state distribution cards + search + state filter + submission table
                    [NEW] SSE-powered live count updates
                    [EXISTING] metrics, DLQ, stuck submissions (unchanged below)
/admin/dashboard   → [OPTIMIZED] single state-counts API call replaces N+1
```

### Components

- **State Counts API** (`GET /api/v1/admin/submissions/state-counts`): Single Prisma `groupBy` query returning `{ counts: Record<SubmissionState, number>, total: number }`
- **Queue Search Section**: Search input + state filter + paginated submission table (reuses `/api/v1/admin/submissions` endpoint pattern)
- **State Distribution Cards**: Clickable count cards per SubmissionState at top of queue page
- **SSE Hook**: `useSubmissionStream` integration for auto-refreshing counts on state_changed events

### Data Model

No schema changes. Uses existing:
- `Submission` table with indexes on `state`, `skillName`, `repoUrl+skillName`, `createdAt`
- `SubmissionStateEvent` for lifecycle (already rendered on detail page)

### API Contracts

**New endpoint:**
- `GET /api/v1/admin/submissions/state-counts`
  - Auth: REVIEWER+ role (existing pattern)
  - Response: `{ counts: { RECEIVED: 5, TIER1_SCANNING: 2, ... }, total: 42 }`
  - Implementation: `prisma.submission.groupBy({ by: ['state'], _count: true })`

**Existing endpoint (reused as-is):**
- `GET /api/v1/admin/submissions?search=X&state=Y&page=Z&limit=20`

## Technology Stack

- **Framework**: Next.js 15 (existing)
- **Database**: Prisma + PostgreSQL (existing)
- **Real-time**: SSE via existing `/api/v1/submissions/stream`
- **UI**: React server/client components (existing patterns)

**Architecture Decisions**:
- **Reuse `/admin/submissions` API**: The existing endpoint already supports search + state filter + pagination. No need for a new search endpoint. Queue page just calls the same API.
- **New state-counts endpoint vs. inline**: Separate endpoint allows both queue page and dashboard to use it, and avoids N+1 on both pages.
- **SSE for counts only**: Don't try to live-update search results via SSE (too complex). Just refresh the state distribution counts when events arrive. Search results refresh on user action.

## Implementation Phases

### Phase 1: API (T-001)
- Create `state-counts` endpoint with `groupBy` query

### Phase 2: Queue Page Enhancement (T-002, T-003)
- Add state distribution cards to queue page header
- Add search bar + state filter + submission results table

### Phase 3: Dashboard Optimization (T-004)
- Refactor dashboard to use new `state-counts` API

### Phase 4: Real-Time (T-005)
- Wire SSE into queue page for live count updates

### Phase 5: Testing & Verification (T-006, T-007, T-008)
- API tests, component tests, cross-page verification

## Testing Strategy

- Unit tests for state-counts API endpoint (Vitest)
- Component tests for queue page enhancements
- BDD test plans embedded in tasks.md
- Target: >80% coverage on new code

## Technical Challenges

### Challenge 1: Queue page is already large (~400 lines)
**Solution**: Add search section above existing content. Keep it as a single page since the sections are logically related (observability + operations).
**Risk**: Low — the page is well-structured with clear sections.

### Challenge 2: SSE reconnection across Cloudflare edge
**Solution**: Use existing SSE pattern with reconnect. Degrade gracefully to manual refresh if SSE disconnects.
**Risk**: Low — existing SSE infrastructure handles this.

## Files to Change

| File | Action | Description |
|------|--------|-------------|
| `src/app/api/v1/admin/submissions/state-counts/route.ts` | NEW | State counts groupBy API |
| `src/app/admin/queue/page.tsx` | MODIFY | Add search, state cards, submission table |
| `src/app/admin/dashboard/page.tsx` | MODIFY | Replace N+1 with state-counts API |
| `src/app/api/v1/admin/submissions/state-counts/__tests__/route.test.ts` | NEW | API tests |
| `src/app/admin/queue/__tests__/page.test.tsx` | NEW/MODIFY | Queue page component tests |
