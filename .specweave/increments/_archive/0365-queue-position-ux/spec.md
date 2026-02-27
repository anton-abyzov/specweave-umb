---
status: completed
---
# 0365 — Queue Position UX

## Problem
Users submitting skills can't tell where they are in the queue or when their submission will be processed. Default sort (newest first) doesn't match actual processing order. After bumping to front, there's no feedback. Filtering by state (rejected, published) still needs proper time-based sorting.

## User Stories

### US-001: Queue Position Visibility
As a skill submitter, I want to see my position in the queue (#N) so I know how many items are ahead of me.

**Acceptance Criteria:**
- [x] AC-US1-01: Active submissions show `#N` position badge (1-indexed, processing order)
- [x] AC-US1-02: Non-active submissions (published/rejected/dequeued) show `--` instead of position
- [x] AC-US1-03: Position is the first column in the queue table

### US-002: Default Processing Order Sort
As a user, I want the queue to default-sort by processing order so I see what's being processed next at the top.

**Acceptance Criteria:**
- [x] AC-US2-01: Default sort is `processingOrder asc` (priority DESC, createdAt ASC)
- [x] AC-US2-02: User can sort by any column (skillName, state, score, createdAt, updatedAt)
- [x] AC-US2-03: When filtering to "rejected" or "published", default sort changes to `updatedAt desc` (most recently changed first)

### US-003: Estimated Processing Time
As a submitter, I want to see how long until my submission is processed (~Xm) so I can set expectations.

**Acceptance Criteria:**
- [x] AC-US3-01: Active submissions show estimated wait time below position badge
- [x] AC-US3-02: Estimate based on recent throughput (avgProcessingTimeMs from last 6h metrics)
- [x] AC-US3-03: Format: `~Xs` (<1m), `~Xm` (1-60m), `~Xh` (>60m)

### US-004: Real-Time Position Updates
As a user watching the queue, I want positions to update automatically as items are processed.

**Acceptance Criteria:**
- [x] AC-US4-01: On SSE state_changed/scan_complete events, positions refresh automatically
- [x] AC-US4-02: Polling fallback refreshes positions every 30s when SSE disconnects

### US-005: State Filter Sorting
As a user, I want to filter by rejected/published and sort by when it happened (ascending or descending).

**Acceptance Criteria:**
- [x] AC-US5-01: "Active" filter defaults to processingOrder sort
- [x] AC-US5-02: "Rejected" filter defaults to updatedAt desc
- [x] AC-US5-03: "Published" filter defaults to updatedAt desc
- [x] AC-US5-04: "All" filter defaults to processingOrder sort
- [x] AC-US5-05: User can toggle sort direction on any column in any filter view

## Out of Scope
- Position on submission detail page (future)
- Historical processing time graphs
- Position notifications/alerts
