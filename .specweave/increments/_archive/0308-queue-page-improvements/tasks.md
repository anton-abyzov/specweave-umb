# Tasks: Queue Page Improvements

## Task Notation

- `[T###]`: Task ID
- `[P]`: Parallelizable
- `[ ]`: Not started
- `[x]`: Completed
- Model hints: haiku (simple), opus (default)

## Phase 1: Backend Fixes

### US-002: Raise KV Index Cap to 2000

#### T-001: Increase MAX_INDEX_ENTRIES constant
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03 | **Status**: [x] completed

**Description**: Change `MAX_INDEX_ENTRIES` from 500 to 2000 in `src/lib/submission-store.ts`. This is a single constant change. The index is only truncated on write (`addToIndex`), so reads are unaffected and existing data is preserved.

**File**: `repositories/anton-abyzov/vskill-platform/src/lib/submission-store.ts`

**Implementation Details**:
- Change line `const MAX_INDEX_ENTRIES = 500;` to `const MAX_INDEX_ENTRIES = 2000;`
- Size validation: each `SubmissionSummary` entry is ~300-400 bytes JSON. 2000 * 400 = 800 KB, well within Cloudflare KV's 25 MiB value limit.

**Test Plan**:
- **File**: `repositories/anton-abyzov/vskill-platform/src/lib/__tests__/submission-store.test.ts`
- **Tests**:
  - **TC-001**: Index truncation at 2000
    - Given a mock KV with an index containing 2001 entries
    - When `addToIndex` is called (via `createSubmission`)
    - Then the index is truncated to 2000 entries (newest first)

**Dependencies**: None
**Model**: haiku

---

### US-003: Fix Search API State Expansion

#### T-002: Add category expansion to search route
**User Story**: US-003 | **Satisfies ACs**: AC-US3-02, AC-US3-03, AC-US3-04 | **Status**: [x] completed

**Description**: Import `isCategoryName` and `expandStateCategory` from `@/lib/submission-categories` into the search route. When `stateFilter` is a category name, expand it to an array and use Prisma `{ in: [...] }` instead of exact match.

**File**: `repositories/anton-abyzov/vskill-platform/src/app/api/v1/submissions/search/route.ts`

**Implementation Details**:
- Add import: `import { isCategoryName, expandStateCategory } from "@/lib/submission-categories";`
- Replace the current state filter block:
  ```typescript
  // Before
  if (stateFilter) {
    where.state = stateFilter;
  }
  // After
  if (stateFilter) {
    if (isCategoryName(stateFilter)) {
      const expanded = expandStateCategory(stateFilter);
      if (expanded.length > 0) {
        where.state = { in: expanded };
      }
    } else {
      where.state = stateFilter;
    }
  }
  ```

**Test Plan**:
- **File**: `repositories/anton-abyzov/vskill-platform/src/app/api/v1/submissions/search/__tests__/route.test.ts`
- **Tests**:
  - **TC-002**: Search with category "active" returns RECEIVED + TIER1_SCANNING + TIER2_SCANNING
    - Given submissions in states RECEIVED, TIER1_SCANNING, TIER2_SCANNING, PUBLISHED
    - When GET `/api/v1/submissions/search?q=test&state=active`
    - Then response includes submissions in all three active states, excludes PUBLISHED
  - **TC-003**: Search with raw state "RECEIVED" still works (backward compat)
    - Given submissions in RECEIVED and TIER1_SCANNING states
    - When GET `/api/v1/submissions/search?q=test&state=RECEIVED`
    - Then response includes only RECEIVED submissions
  - **TC-004**: Search with category "published" returns AUTO_APPROVED + PUBLISHED + VENDOR_APPROVED
    - Given submissions in various states
    - When GET `/api/v1/submissions/search?q=test&state=published`
    - Then response includes all success-state submissions

**Dependencies**: None
**Model**: haiku

---

## Phase 2: Frontend Fixes

### US-001: Fix SSE/Polling Pagination Reset

#### T-003: Stabilize fetchQueue reference for SSE and polling
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04 | **Status**: [x] completed

**Description**: Use a ref to hold the latest `fetchQueue` function so SSE callbacks and polling always call the current version without recreating subscriptions.

**File**: `repositories/anton-abyzov/vskill-platform/src/app/queue/page.tsx`

**Implementation Details**:
1. Add a ref: `const fetchQueueRef = useRef(fetchQueue);`
2. Keep it synced: add `useEffect(() => { fetchQueueRef.current = fetchQueue; }, [fetchQueue]);` (or just assign directly after the `useCallback` definition: `fetchQueueRef.current = fetchQueue;`)
3. In the SSE `submission_created` handler (line ~224-227), replace `fetchQueue()` with `fetchQueueRef.current()`.
4. Similarly add `const fetchStatsRef = useRef(fetchStats);` and keep it synced.
5. In the SSE `submission_created` handler, replace `fetchStats()` with `fetchStatsRef.current()`.
6. In the polling `useEffect` (lines 232-240), replace `fetchQueue()` and `fetchStats()` calls with the ref-based versions, and remove `fetchQueue` and `fetchStats` from the dependency array so the interval is not torn down/recreated on every state change.

**Test Plan**:
- **File**: `repositories/anton-abyzov/vskill-platform/src/app/queue/__tests__/page.test.tsx`
- **Tests**:
  - **TC-005**: SSE submission_created does not reset page
    - Given the user is on page 3 (URL has `?page=3`)
    - When an SSE `submission_created` event fires
    - Then `fetchQueue` is called with page=3 (or current params), not page=1
  - **TC-006**: Polling interval preserves current page
    - Given the user navigates to page 2
    - When the 30-second polling interval fires
    - Then the fetch request includes `offset` corresponding to page 2

**Dependencies**: None
**Model**: opus

---

### US-003: Fix Queue Page Filter Passthrough

#### T-004: Remove getStateForFilter and pass category name to search API
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01 | **Status**: [x] completed

**Description**: Remove the `getStateForFilter()` helper function from `page.tsx` and pass the `filterParam` value directly to the search API as the `state` parameter. The search API (after T-002) will handle category expansion server-side.

**File**: `repositories/anton-abyzov/vskill-platform/src/app/queue/page.tsx`

**Implementation Details**:
- In the `doSearch` callback (~line 251), change:
  ```typescript
  // Before
  const stateParam = filterParam !== "all" ? getStateForFilter(filterParam) : "";
  // After
  const stateParam = filterParam !== "all" ? filterParam : "";
  ```
- Delete the `getStateForFilter()` function at the bottom of the file (lines 914-924).

**Test Plan**:
- **File**: `repositories/anton-abyzov/vskill-platform/src/app/queue/__tests__/page.test.tsx`
- **Tests**:
  - **TC-007**: Search with "active" filter passes "active" to search API
    - Given the filter is set to "active" and user types a search query
    - When the search API is called
    - Then the request URL contains `state=active` (not `state=RECEIVED`)

**Dependencies**: T-002 (search API must handle category names first)
**Model**: haiku

---

### US-004: Pagination UX with Page Numbers

#### T-005: Implement page number pagination component
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-04, AC-US4-05 | **Status**: [x] completed

**Description**: Replace the existing Previous/Next pagination bar with a page-number-based pagination that includes ellipsis truncation, current-page highlighting, and Previous/Next buttons.

**File**: `repositories/anton-abyzov/vskill-platform/src/app/queue/page.tsx`

**Implementation Details**:
1. Add a helper function `getPageNumbers(currentPage: number, totalPages: number): (number | "...")[]` that returns an array like `[1, "...", 4, 5, 6, "...", 10]`:
   - Always include page 1 and `totalPages`
   - Include `currentPage - 1`, `currentPage`, `currentPage + 1` (clamped)
   - Insert `"..."` between non-contiguous numbers
   - For <= 7 total pages, show all page numbers without ellipsis

2. Replace the pagination `<div>` (lines 637-699) with:
   - "Showing X-Y of Z" label (keep existing)
   - Page size selector (keep existing)
   - Previous button (keep existing)
   - Page number buttons generated from `getPageNumbers()`:
     - Regular pages: clickable, call `updateURL({ page: String(n) })` + `fetchQueue({ page: n })`
     - Current page: highlighted with distinct border/background
     - `"..."`: non-clickable span
   - Next button (keep existing)

3. Style page number buttons consistently with existing `paginationBtnStyle`:
   - Current page: `border: 1px solid var(--text-muted)`, `backgroundColor: var(--bg-subtle)`, `fontWeight: 600`
   - Other pages: same as existing pagination buttons
   - Ellipsis: `color: var(--text-faint)`, no border, no cursor

**Test Plan**:
- **File**: `repositories/anton-abyzov/vskill-platform/src/app/queue/__tests__/page.test.tsx`
- **Tests**:
  - **TC-008**: Page numbers render correctly for small page count
    - Given 5 total pages
    - When pagination renders
    - Then buttons 1, 2, 3, 4, 5 are shown (no ellipsis)
  - **TC-009**: Ellipsis renders for large page count
    - Given 20 total pages and current page is 10
    - When pagination renders
    - Then page numbers show: 1 ... 9 10 11 ... 20
  - **TC-010**: Current page is visually highlighted
    - Given the user is on page 5
    - When pagination renders
    - Then page 5 button has distinct styling (data-active or aria-current)
  - **TC-011**: Clicking a page number navigates correctly
    - Given the user is on page 1
    - When they click page 3
    - Then the URL updates to `?page=3` and fetchQueue is called with page=3

**Dependencies**: None (can be done in parallel with T-003)
**Model**: opus

---

## Phase 3: Verification

#### T-006: Integration verification and cleanup
**User Story**: All | **Satisfies ACs**: All | **Status**: [x] completed

**Description**: Run the full test suite, verify all acceptance criteria, and ensure no regressions.

**Implementation Details**:
- Run `npm test` in vskill-platform
- Verify no TypeScript errors (`npm run typecheck` or `npx tsc --noEmit`)
- Manual smoke test checklist:
  - [ ] Navigate to page 3, wait 30s, confirm page stays at 3
  - [ ] Submit a new skill via SSE, confirm page does not reset
  - [ ] Filter by "active", search for a skill name, confirm TIER1_SCANNING results appear
  - [ ] Click page number 5, confirm URL updates and correct data loads
  - [ ] Verify 2000 index cap by checking `MAX_INDEX_ENTRIES` value

**Dependencies**: T-001, T-002, T-003, T-004, T-005
**Model**: haiku

---

## Task Dependency Graph

```
T-001 (KV index cap)         [P] -- independent
T-002 (search API expansion) [P] -- independent
T-003 (SSE/polling fix)      [P] -- independent
T-004 (filter passthrough)        -- depends on T-002
T-005 (page numbers)         [P] -- independent
T-006 (verification)              -- depends on all above
```

## Execution Recommendation

Tasks: 6 | Domains: 2 (backend, frontend) | Complexity: Medium

Recommended approach: `/sw:do 0308` -- tasks are well-scoped and sequential execution is efficient. T-001, T-002, T-003, and T-005 can run in parallel if using `/sw:team-lead`.
