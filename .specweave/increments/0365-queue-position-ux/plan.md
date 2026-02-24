# Plan: 0365 — Queue Position UX

## Architecture

### Position Computation
- Positions are ephemeral, computed on demand (not stored)
- Query: active submissions ordered by `priority DESC, createdAt ASC`, map to 1-based index
- Active queue is typically <200 items, so a single `findMany({ select: { id: true } })` is sub-ms

### Processing Time Estimate
- `avgProcessingTimeMs` computed from hourly metrics buckets (last 6h)
- Served via existing stats endpoint
- Client computes: `position * avgProcessingTimeMs / 60000`

### Real-Time Updates
- Re-fetch lightweight `/positions` endpoint on SSE events (no new event type needed)
- 10s KV cache on positions endpoint to avoid DB hammering

### Smart Default Sort by Filter
- "all" / "active" → `processingOrder asc` (priority DESC, createdAt ASC)
- "published" / "rejected" → `updatedAt desc` (most recently changed first)
- Sort direction toggleable by user on any column

## Execution Order
1. T-001: Prisma index + processingOrder sort in submissions API
2. T-002: Positions endpoint
3. T-003: avgProcessingTimeMs in stats
4. T-004: Position column in SubmissionTable
5. T-005: Page integration (default sort, positions, SSE refresh, filter-aware defaults)
6. T-006: Tests
