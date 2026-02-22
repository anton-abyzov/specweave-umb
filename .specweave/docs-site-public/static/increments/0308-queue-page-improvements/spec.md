---
increment: 0308-queue-page-improvements
title: "Queue Page Improvements"
type: feature
priority: P1
status: planned
created: 2026-02-21
structure: user-stories
test_mode: test-after
coverage_target: 80
---

# Feature: Queue Page Improvements

## Overview

Four targeted fixes for the vskill-platform queue page: (1) prevent SSE/polling from resetting pagination, (2) raise the KV submission index cap from 500 to 2000, (3) fix the search endpoint so filter-category state expansion works correctly, and (4) replace Previous/Next pagination with a page-number UX.

---

## User Stories

### US-001: Fix SSE/Polling Pagination Reset (P1)
**Project**: vskill-platform

**As a** queue reviewer browsing page 3+ of submissions
**I want** SSE events and 30-second polling to update data without jumping me back to page 1
**So that** I can review submissions deep in the list without losing my place

**Acceptance Criteria**:
- [ ] **AC-US1-01**: `submission_created` SSE events refetch the current page (preserving `currentPage`, `filterParam`, `sortColumn`, `sortDirection`) instead of calling `fetchQueue()` with no arguments
- [ ] **AC-US1-02**: The 30-second polling interval calls `fetchQueue()` using the current URL-driven state (page, filter, sort) rather than re-deriving defaults from `useCallback` closure
- [ ] **AC-US1-03**: `state_changed` and `scan_complete` SSE events continue to perform in-place row updates without triggering a full refetch
- [ ] **AC-US1-04**: Stats polling (`fetchStats()`) remains independent and does not reset pagination

**Root Cause**: `fetchQueue` is recreated whenever `filterParam`, `sortColumn`, `sortDirection`, `currentPage`, or `pageSize` change (its dependency array). The 30-second `setInterval` in the `useEffect` that calls `fetchQueue()` is re-created on every state change, which is correct -- but the `submission_created` SSE handler calls `fetchQueue()` without explicit parameters, so it always uses the current closure values. The real bug is that the `useEffect` for SSE (`useSubmissionStream`) captures a stale `fetchQueue` reference if the user navigates pages, since the SSE hook's `onEvent` callback is stored in a ref but the outer `fetchQueue` closure may be stale.

---

### US-002: Raise KV Index Cap to 2000 (P2)
**Project**: vskill-platform

**As a** platform operator with a growing submission pipeline
**I want** the KV submission index to hold up to 2000 entries instead of 500
**So that** older submissions remain visible in the queue page without falling off the index

**Acceptance Criteria**:
- [ ] **AC-US2-01**: `MAX_INDEX_ENTRIES` in `src/lib/submission-store.ts` is changed from 500 to 2000
- [ ] **AC-US2-02**: The KV value size stays within Cloudflare's 25 MiB limit (each SubmissionSummary entry is ~300-400 bytes; 2000 * 400 = ~800 KB, well under limit)
- [ ] **AC-US2-03**: Existing index data is preserved -- the change is backward-compatible (index only truncates on write, never on read)

---

### US-003: Fix Search Filter State Expansion (P1)
**Project**: vskill-platform

**As a** reviewer filtering the queue by "active" and then searching
**I want** the search API to receive all expanded states (RECEIVED, TIER1_SCANNING, TIER2_SCANNING) rather than just "RECEIVED"
**So that** search results include all submissions matching the selected filter category

**Acceptance Criteria**:
- [ ] **AC-US3-01**: The `getStateForFilter()` function on the queue page is replaced with logic that passes the category name (e.g., "active") directly to the search API
- [ ] **AC-US3-02**: The search API route (`/api/v1/submissions/search`) accepts category names ("active", "published", "rejected") in the `state` parameter and expands them using `expandStateCategory()` / `isCategoryName()`
- [ ] **AC-US3-03**: When the "active" filter is selected and a search is performed, submissions in TIER1_SCANNING and TIER2_SCANNING states appear in results (not just RECEIVED)
- [ ] **AC-US3-04**: The main submissions list endpoint (`/api/v1/submissions`) continues to work with both category names and raw state values (no regression)

**Root Cause**: The queue page's `getStateForFilter()` maps "active" to only "RECEIVED", "published" to only "PUBLISHED", and "rejected" to only "REJECTED". Meanwhile, the main `/api/v1/submissions` endpoint correctly uses `expandStateCategory()` from `submission-categories.ts` to expand categories into all matching states. The search endpoint does not use expansion at all -- it passes the raw state value directly to Prisma `where.state`.

---

### US-004: Pagination UX with Page Numbers (P2)
**Project**: vskill-platform

**As a** queue reviewer navigating through many pages of submissions
**I want** to see page numbers (e.g., "1 2 3 ... 10") with direct-click navigation
**So that** I can jump to any page quickly instead of clicking Previous/Next repeatedly

**Acceptance Criteria**:
- [ ] **AC-US4-01**: The pagination bar shows clickable page numbers with ellipsis truncation for large page counts (e.g., "1 2 3 ... 8 9 10")
- [ ] **AC-US4-02**: The current page is visually highlighted (distinct background/border)
- [ ] **AC-US4-03**: Previous and Next buttons are retained alongside the page numbers
- [ ] **AC-US4-04**: Clicking a page number updates the URL `page` parameter and fetches that page from the server
- [ ] **AC-US4-05**: The ellipsis logic shows: first page, last page, current page +/- 1 sibling, with "..." gaps between discontinuous ranges

---

## Functional Requirements

### FR-001: Stable Pagination During Live Updates
The queue page must maintain the user's current page position when SSE events or polling cycles update data. Only `submission_created` should trigger a data refetch; `state_changed` and `scan_complete` should update rows in-place.

### FR-002: KV Index Scaling
The `submissions:index` KV blob must support up to 2000 entries. No changes to the index read path are needed -- only the write-time truncation cap changes.

### FR-003: Consistent State Expansion
Both the main list endpoint and search endpoint must use the same state-expansion logic (`expandStateCategory` from `submission-categories.ts`) when receiving category filter names.

### FR-004: Page Number Navigation
The pagination component must render page numbers with ellipsis for gaps, supporting direct page navigation via URL parameters.

## Success Criteria

- Queue reviewers can browse page 3+ without being reset to page 1 by SSE/polling
- All submissions up to 2000 are visible in the queue (not truncated at 500)
- Searching with "active" filter returns RECEIVED + TIER1_SCANNING + TIER2_SCANNING submissions
- Page numbers are clickable and URL-driven

## Out of Scope

- Infinite scroll or virtual scrolling
- Full-text search improvements beyond state filtering
- KV-to-Prisma migration for the submissions list endpoint
- Mobile-responsive pagination layout

## Dependencies

- `src/lib/submission-categories.ts` (expandStateCategory, isCategoryName) -- already exists
- Cloudflare KV 25 MiB value size limit (validated in AC-US2-02)
