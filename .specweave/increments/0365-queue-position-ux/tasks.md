# Tasks: 0365 — Queue Position UX

### T-001: Add processingOrder sort to submissions API
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02 | **Status**: [x] completed
**Test**: Given GET /api/v1/submissions?sort=processingOrder → When response received → Then submissions ordered by priority DESC, createdAt ASC and queuePositions map included

- Add composite Prisma index `@@index([priority(sort: Desc), createdAt(sort: Asc)])`
- Add `processingOrder` to validSortColumns in `src/app/api/v1/submissions/route.ts`
- When sort=processingOrder, use `orderBy: [{ priority: 'desc' }, { createdAt: 'asc' }]`
- Compute and return `queuePositions: Record<string, number>` for active items
- Add `priority` to select clause

### T-002: Create positions endpoint
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01 | **Status**: [x] completed
**Test**: Given GET /api/v1/submissions/positions → When active queue has 5 items → Then returns positions {id: 1..5} with correct ordering

- New file: `src/app/api/v1/submissions/positions/route.ts`
- Query active submissions ordered by processing order, return `{ positions: Record<string, number>, total: number }`
- KV cache with 10s TTL

### T-003: Add avgProcessingTimeMs to stats endpoint
**User Story**: US-003 | **Satisfies ACs**: AC-US3-02 | **Status**: [x] completed
**Test**: Given recent hourly metrics exist → When GET /api/v1/submissions/stats → Then response includes avgProcessingTimeMs > 0

- Read last 6 hourly metrics buckets from KV
- Compute average duration per item
- Add to stats response alongside existing fields

### T-004: Add position column to SubmissionTable
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03 | **Status**: [x] completed
**Test**: Given active submission with position 3 → When table renders → Then shows #3 badge with estimated time

- Add `#` as first column in COLUMNS array
- Add `queuePosition` and `priority` to SubmissionRow interface
- Render `#N` badge for active items, `--` for others
- Show estimated time below badge: `~Xs`, `~Xm`, `~Xh`
- Accept `avgProcessingTimeMs` prop

### T-005: Queue page integration — default sort, positions, SSE refresh
**User Story**: US-002, US-004, US-005 | **Satisfies ACs**: AC-US2-01, AC-US2-03, AC-US4-01, AC-US4-02, AC-US5-01, AC-US5-02, AC-US5-03, AC-US5-04, AC-US5-05 | **Status**: [x] completed
**Test**: Given queue page loads → When filter is "all" → Then sort is processingOrder asc; When filter changes to "rejected" → Then sort changes to updatedAt desc

- Change default sort to `processingOrder asc`
- On filter change: "active"/"all" → processingOrder asc; "published"/"rejected" → updatedAt desc
- Fetch positions from API response, store in state, merge into submissions
- On SSE state_changed/scan_complete: re-fetch `/api/v1/submissions/positions`
- Pass avgProcessingTimeMs from stats to SubmissionTable

### T-006: Tests
**User Story**: US-001, US-002, US-003, US-004, US-005 | **Satisfies ACs**: all | **Status**: [x] completed
**Test**: All new and updated tests pass

- Update submissions API pagination tests for processingOrder sort
- Add positions endpoint tests
- Update stats endpoint tests for avgProcessingTimeMs
- Update SubmissionTable component tests for position column
