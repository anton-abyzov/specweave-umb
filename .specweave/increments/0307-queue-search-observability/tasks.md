# Tasks: Queue Search, Observability & Monitoring for Admin

## Task Notation

- `[T###]`: Task ID
- `[P]`: Parallelizable
- `[ ]`: Not started
- `[x]`: Completed
- Model hints: haiku (simple), opus (default)

## Phase 1: API

### US-002: Per-State Distribution Overview (P1)

#### T-001: Create state-counts API endpoint

**Description**: Create `GET /api/v1/admin/submissions/state-counts` endpoint that returns submission counts grouped by state using Prisma `groupBy`. This replaces the N+1 query pattern currently used on the dashboard (which makes 8 separate requests, one per state).

**References**: AC-US2-01, AC-US2-02, AC-US4-01

**Implementation Details**:
- Create `src/app/api/v1/admin/submissions/state-counts/route.ts`
- Use `requireRole(request, "REVIEWER")` auth pattern (same as `/api/v1/admin/submissions`)
- Query: `prisma.submission.groupBy({ by: ['state'], _count: { _all: true } })`
- Transform to `{ counts: Record<SubmissionState, number>, total: number }`
- Return all states including zero counts for completeness

**Test Plan**:
- **File**: `src/app/api/v1/admin/submissions/state-counts/__tests__/route.test.ts`
- **Tests**:
  - **TC-001**: Returns grouped counts for all states
    - Given submissions exist in RECEIVED (3), PUBLISHED (5), REJECTED (1)
    - When GET `/api/v1/admin/submissions/state-counts` with valid REVIEWER token
    - Then response includes `{ counts: { RECEIVED: 3, PUBLISHED: 5, REJECTED: 1, ... }, total: 9 }`
  - **TC-002**: Returns zero total when no submissions exist
    - Given empty submissions table
    - When GET `/api/v1/admin/submissions/state-counts`
    - Then response includes `{ counts: {}, total: 0 }`
  - **TC-003**: Requires REVIEWER role
    - Given user with USER role
    - When GET `/api/v1/admin/submissions/state-counts`
    - Then returns 403

**Dependencies**: None
**Status**: [x] Completed

---

## Phase 2: Queue Page Enhancement

### US-001: Queue Search & Filtering (P1)

#### T-002: Add state distribution cards to queue page header

**Description**: Add clickable per-state count cards at the top of the queue page (below the existing header, above the existing stats grid). Fetch counts from the new `state-counts` endpoint. Clicking a card sets the state filter.

**References**: AC-US2-01, AC-US2-03, AC-US2-04

**Implementation Details**:
- Add state to queue page: `stateCounts` (Record<string, number>), `stateCountsTotal` (number)
- Fetch from `/api/v1/admin/submissions/state-counts` in the existing `fetchData` callback
- Render a flex-wrap grid of state count cards (reuse `StateBadge`-style coloring from dashboard)
- Show total prominently (e.g. "142 Total Submissions")
- Clicking a state card sets `stateFilter` state variable (used by T-003's search)
- Active state card gets highlighted border
- Follow existing inline style patterns (mono font, card bg/border CSS vars)

**Dependencies**: T-001
**Status**: [x] Completed

#### T-003: Add search bar, state filter dropdown, and submission results table

**Description**: Add a search input + state filter dropdown + paginated submission results table to the queue page. Place it between the state distribution cards and the existing "Stuck Submissions" section. Reuse the pattern from `/admin/submissions/page.tsx` (debounced search, state select, table with pagination) and call the existing `/api/v1/admin/submissions` API.

**References**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05, AC-US1-06

**Implementation Details**:
- Add states: `search`, `debouncedSearch`, `stateFilter`, `submissions[]`, `totalCount`, `submissionPage`, `submissionsLoading`
- Debounce search input at 300ms (same pattern as submissions page)
- State filter dropdown with STATES constant (All, RECEIVED, TIER1_SCANNING, etc.)
- When state card from T-002 is clicked, update the `stateFilter` state
- Fetch from `GET /api/v1/admin/submissions?search=X&state=Y&page=Z&limit=20`
- Render results table: skill name, repo URL (truncated), state badge, submitted date, View link to `/admin/submissions/{id}`
- Empty state: "No submissions found" with clear filters button
- Pagination controls (Previous/Next) same pattern as submissions page
- Keep existing queue page content below (stuck, throughput, processing time, DLQ)

**Test Plan**:
- **File**: `src/app/admin/queue/__tests__/page.test.tsx`
- **Tests**:
  - **TC-004**: Search input filters submissions by skill name
    - Given queue page is rendered with mock API
    - When user types "remotion" in search input
    - Then API is called with `?search=remotion` after 300ms debounce
  - **TC-005**: State filter dropdown changes results
    - Given queue page is rendered
    - When user selects "Published" from state dropdown
    - Then API is called with `?state=PUBLISHED`
  - **TC-006**: Empty state shows clear button
    - Given API returns 0 results
    - When page renders
    - Then "No submissions found" message is shown with clear filters button
  - **TC-007**: Clicking state card sets state filter
    - Given state distribution cards are rendered
    - When user clicks "RECEIVED" card
    - Then state filter dropdown updates to "RECEIVED"

**Dependencies**: T-001, T-002
**Status**: [x] Completed

---

### US-004: Dashboard State Count Optimization (P1)

#### T-004: Refactor dashboard to use state-counts API

**Description**: Replace the N+1 state count fetching on `/admin/dashboard` (lines 130-151 of dashboard/page.tsx) with a single call to the new `state-counts` endpoint.

**References**: AC-US4-01, AC-US4-02

**Implementation Details**:
- Remove the `Promise.all(states.map(...))` block that makes 8 separate `?state=X&limit=1` calls
- Replace with single `fetch("/api/v1/admin/submissions/state-counts", ...)`
- Transform response `counts` object to `StateCounts[]` format: `Object.entries(counts).filter(([_, count]) => count > 0).map(([state, count]) => ({ state, count }))`
- Everything else on dashboard stays unchanged

**Dependencies**: T-001
**Status**: [x] Completed

---

## Phase 3: Real-Time Updates

### US-003: Real-Time Queue Updates (P2)

#### T-005: Wire SSE stream into queue page for live count updates

**Description**: Connect the existing SSE stream (`/api/v1/submissions/stream`) to the queue page. When `state_changed` or `submission_created` events arrive, re-fetch state counts. Show a connection status indicator.

**References**: AC-US3-01, AC-US3-02, AC-US3-03

**Implementation Details**:
- Create `EventSource` connection to `/api/v1/submissions/stream` on mount
- On `state_changed` or `submission_created` events, call the state-counts API to refresh counts
- Throttle re-fetches to max once per 5 seconds (batch rapid events)
- Add connection status dot (green=connected, gray=disconnected, yellow=reconnecting) next to page title
- Clean up EventSource on unmount
- Graceful degradation: if SSE fails, fall back to existing 30s polling (already in place)

**Dependencies**: T-002
**Status**: [x] Completed

---

## Phase 4: Testing & Verification

#### T-006: Write tests for state-counts API endpoint

**Description**: Write unit tests for the new state-counts API endpoint.

**References**: AC-US2-02

**Implementation Details**:
- Test file: `src/app/api/v1/admin/submissions/state-counts/__tests__/route.test.ts`
- Mock Prisma with `vi.hoisted()` + `vi.mock("@prisma/client", ...)`
- Mock `requireRole` for auth tests
- Test cases per TC-001, TC-002, TC-003 from T-001

**Dependencies**: T-001
**Status**: [x] Completed

#### T-007: Write tests for queue page enhancements

**Description**: Write component tests for the enhanced queue page (search, state cards, table).

**References**: AC-US1-01, AC-US1-05, AC-US2-03

**Implementation Details**:
- Test file: `src/app/admin/queue/__tests__/page.test.tsx`
- Mock fetch for API calls
- Test cases per TC-004, TC-005, TC-006, TC-007 from T-003

**Dependencies**: T-002, T-003
**Status**: [x] Completed

#### T-008: Verify all ACs and cross-page consistency

**Description**: Manual verification that all acceptance criteria pass end-to-end. Check that state counts on queue page match dashboard. Verify search finds "remotion-best-practices" when it exists.

**References**: AC-US1-05, AC-US2-01, AC-US4-01

**Implementation Details**:
- Verify queue page shows same state counts as dashboard
- Verify searching "remotion-best-practices" returns correct results
- Verify clicking state card → filters table → matches card count
- Verify dashboard loads state distribution in 1 network request (DevTools check)
- Verify SSE connection indicator works

**Dependencies**: T-001, T-002, T-003, T-004, T-005, T-006, T-007
**Status**: [x] Completed
