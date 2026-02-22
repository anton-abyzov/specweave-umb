# Tasks: Queue Search, Observability & Admin Monitoring

## Task Notation

- `[T###]`: Task ID
- `[P]`: Parallelizable
- `[ ]`: Not started
- `[x]`: Completed

## Phase 1: API Enhancement

### T-001: Replace mock admin submissions with Prisma queries

**Description**: Rewrite GET /api/v1/admin/submissions to query the database with search, state filter, pagination, and sort support.

**References**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05

**Implementation Details**:
- Remove MOCK_SUBMISSIONS array
- Parse query params: search, state, page, limit, sort
- Build Prisma where clause with optional skillName contains and state filter
- Return { submissions, totalCount, page, limit }

**Test Plan**:
- **File**: `src/app/api/v1/admin/submissions/__tests__/route.test.ts`
- **Tests**:
  - **TC-001**: Returns paginated results with totalCount
  - **TC-002**: Filters by state query param
  - **TC-003**: Searches by skillName (case-insensitive)
  - **TC-004**: Handles sort param

**Dependencies**: None
**Status**: [x] Completed

---

### T-002: Write API route tests for enhanced submissions endpoint

**Description**: Update existing tests and add new ones for search/filter/pagination.

**References**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04

**Test Plan**:
- **File**: `src/app/api/v1/admin/submissions/__tests__/route.test.ts`

**Dependencies**: T-001
**Status**: [x] Completed

## Phase 2: Dashboard Enhancement

### T-003: Replace hard-coded dashboard stats with live API data

**Description**: Modify the admin dashboard to fetch stats from /api/v1/admin/stats and display real counts.

**References**: AC-US2-01, AC-US2-02, AC-US2-03

**Implementation Details**:
- Fetch /api/v1/admin/stats on mount
- Replace static STATS array with dynamic data
- Show state distribution breakdown
- Handle loading and error states

**Dependencies**: None
**Status**: [x] Completed

---

### T-004: Write dashboard component tests

**Description**: Test that the dashboard fetches and displays live stats.

**References**: AC-US2-01, AC-US2-02

**Test Plan**:
- **File**: `src/app/admin/dashboard/__tests__/page.test.tsx`

**Dependencies**: T-003
**Status**: [x] Completed

## Phase 3: Submissions List Page

### T-005: Create admin submissions list page

**Description**: Build /admin/submissions/page.tsx with search, state filter, pagination, and row click navigation.

**References**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04, AC-US3-05

**Implementation Details**:
- Search input with debounce
- State filter dropdown
- Paginated table with navigation
- Click row to navigate to /admin/submissions/[id]

**Dependencies**: T-001
**Status**: [x] Completed

---

### T-006: Write submissions list page tests

**Description**: Test search, filter, pagination, and navigation behavior.

**References**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04, AC-US3-05

**Test Plan**:
- **File**: `src/app/admin/submissions/__tests__/page.test.tsx`

**Dependencies**: T-005
**Status**: [x] Completed

## Phase 4: Verification

### T-007: Run all tests and verify coverage

**Description**: Run vitest, verify all new tests pass, check coverage target.

**Dependencies**: T-002, T-004, T-006
**Status**: [x] Completed
