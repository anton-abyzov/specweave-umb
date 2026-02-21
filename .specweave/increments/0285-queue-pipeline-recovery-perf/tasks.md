# Tasks: Queue Pipeline Recovery + Q Page Performance Overhaul

## Task Notation

- `[T###]`: Task ID
- `[P]`: Parallelizable
- `[ ]`: Not started
- `[x]`: Completed
- Model hints: haiku (simple), opus (default)

## Phase 1: Pipeline Unblock (P0)

### US-001: Fix Pipeline Build Blockers

#### T-001: Fix useRef TypeScript errors across codebase

**Description**: Replace `useRef<ReturnType<typeof setTimeout>>(undefined)` with `useRef<ReturnType<typeof setTimeout> | null>(null)` in all files where this pattern appears. TypeScript strict mode rejects `undefined` as initial value for this type.

**References**: AC-US1-01

**Implementation Details**:
- `src/app/queue/page.tsx` line 53: `searchTimerRef`
- `src/app/components/AnimatedTerminal.tsx` line 81: `timerRef`
- `src/app/components/ThemeToggle.tsx` line 9: `debounceRef`
- Also update any `clearTimeout` guards that check `!== undefined` to check `!== null`

**Test Plan**:
- **File**: N/A (type-only fix verified by build)
- **Tests**:
  - **TC-001**: Build succeeds
    - Given the useRef calls use `| null` union type with `null` initial value
    - When `next build` runs
    - Then no TypeScript errors are reported

**Dependencies**: None
**Status**: [ ] Not Started

---

#### T-002: Verify build succeeds after useRef fix

**Description**: Run `next build` locally to confirm TypeScript compilation passes. This is a verification gate, not an implementation task.

**References**: AC-US1-02

**Test Plan**:
- **Tests**:
  - **TC-002**: Full build passes
    - Given T-001 fixes are applied
    - When `npm run build` or `next build` executes
    - Then exit code is 0 with no TypeScript errors

**Dependencies**: T-001
**Status**: [ ] Not Started

---

### US-002: Queue Pause TTL Safety Net

#### T-003: Add TTL to queue pause KV flag

**Description**: Modify POST /api/v1/admin/queue/pause to accept optional `ttlSeconds` body param and pass `expirationTtl` to the KV `put` call. This ensures the pause flag auto-expires, preventing indefinite queue stalls.

**References**: AC-US2-01, AC-US2-02, AC-US2-03

**Implementation Details**:
- Parse request body for `ttlSeconds` (default 3600, max 86400)
- Change `env.QUEUE_METRICS_KV.put(PAUSE_KEY, "1")` to `env.QUEUE_METRICS_KV.put(PAUSE_KEY, "1", { expirationTtl: ttl })`
- Update the value stored to include timestamp: `JSON.stringify({ pausedAt: new Date().toISOString(), ttlSeconds: ttl })`
- No changes to DELETE endpoint or consumer (consumer only checks key existence)

**Test Plan**:
- **File**: `src/app/api/v1/admin/queue/pause/__tests__/route.test.ts`
- **Tests**:
  - **TC-003**: POST sets KV with default TTL
    - Given admin is authenticated as SUPER_ADMIN
    - When POST /api/v1/admin/queue/pause is called with no body
    - Then KV.put is called with expirationTtl: 3600
  - **TC-004**: POST accepts custom TTL
    - Given admin provides `{ "ttlSeconds": 7200 }`
    - When POST is called
    - Then KV.put uses expirationTtl: 7200
  - **TC-005**: POST caps TTL at 24 hours
    - Given admin provides `{ "ttlSeconds": 999999 }`
    - When POST is called
    - Then KV.put uses expirationTtl: 86400

**Dependencies**: None
**Status**: [ ] Not Started

---

## Phase 2: API Enhancements

### US-003: Server-Side Paginated Queue Page (API side)

#### T-004: Add server-side sort and state filter to GET /api/v1/submissions

**Description**: Enhance the GET endpoint to support `state` (with category shortcuts), `sort`, and `sortDir` query params. Apply these before slicing with limit/offset.

**References**: AC-US3-01, AC-US3-03, AC-US3-04

**Implementation Details**:
- Add state category expansion: `active` -> `["RECEIVED", "TIER1_SCANNING", "TIER2_SCANNING"]`, `published` -> `["AUTO_APPROVED", "PUBLISHED", "VENDOR_APPROVED"]`, `rejected` -> `["REJECTED", "TIER1_FAILED", "DEQUEUED"]`
- If `state` is a raw SubmissionState enum value, filter to just that one
- If `state` is a category name, filter to all states in that category
- Add `sort` param: `createdAt` (default), `updatedAt`, `skillName`, `state`
- Add `sortDir` param: `desc` (default), `asc`
- Apply sort to array after filter, before slice
- Keep existing fresh-hydration logic for active submissions

**Test Plan**:
- **File**: `src/app/api/v1/submissions/__tests__/route.test.ts`
- **Tests**:
  - **TC-006**: Filter by state category "active"
    - Given KV index has 10 RECEIVED, 5 PUBLISHED, 3 REJECTED submissions
    - When GET /api/v1/submissions?state=active
    - Then response contains only RECEIVED/TIER1_SCANNING/TIER2_SCANNING submissions and total reflects filtered count
  - **TC-007**: Sort by skillName ascending
    - Given KV index has submissions with names A, C, B
    - When GET /api/v1/submissions?sort=skillName&sortDir=asc
    - Then submissions are ordered A, B, C
  - **TC-008**: Pagination with offset
    - Given 100 submissions in KV index
    - When GET /api/v1/submissions?limit=10&offset=20
    - Then 10 submissions returned starting from index 20, total=100

**Dependencies**: None
**Status**: [ ] Not Started

---

### US-005: Submissions Stats Endpoint

#### T-005: Create GET /api/v1/submissions/stats endpoint

**Description**: New lightweight endpoint that reads the KV submissions index once and returns aggregate counts by category plus average score.

**References**: AC-US5-01, AC-US5-02

**Implementation Details**:
- Create `src/app/api/v1/submissions/stats/route.ts`
- Read `submissions:index` from KV (single read, same as getSubmissionIndex)
- Count: total, active (RECEIVED|TIER1_SCANNING|TIER2_SCANNING), published (AUTO_APPROVED|PUBLISHED|VENDOR_APPROVED), rejected (REJECTED|TIER1_FAILED|DEQUEUED)
- Compute avgScore from all submissions with non-null scores > 0
- Return `{ total, active, published, rejected, avgScore }`
- Use shared state-category mapping (same as T-004)

**Test Plan**:
- **File**: `src/app/api/v1/submissions/stats/__tests__/route.test.ts`
- **Tests**:
  - **TC-009**: Returns correct counts
    - Given KV index has 5 RECEIVED, 10 PUBLISHED, 3 REJECTED submissions
    - When GET /api/v1/submissions/stats
    - Then response is `{ total: 18, active: 5, published: 10, rejected: 3, avgScore: ... }`
  - **TC-010**: Average score excludes null/zero scores
    - Given submissions with scores [80, null, 0, 60, 90]
    - When stats are computed
    - Then avgScore = Math.round((80 + 60 + 90) / 3) = 77
  - **TC-011**: Empty index returns zeros
    - Given KV index is empty
    - When GET /api/v1/submissions/stats
    - Then `{ total: 0, active: 0, published: 0, rejected: 0, avgScore: 0 }`

**Dependencies**: None
**Status**: [ ] Not Started

---

#### T-006: Extract shared state-category mapping utility

**Description**: Create a shared utility module that maps SubmissionState values to categories (active/published/rejected) and provides helper functions used by both the API and the frontend SSE handler.

**References**: AC-US3-03, AC-US4-04

**Implementation Details**:
- Create `src/lib/submission-categories.ts`
- Export `ACTIVE_STATES`, `SUCCESS_STATES`, `FAILED_STATES` arrays
- Export `getStateCategory(state: SubmissionState): "active" | "published" | "rejected" | "other"`
- Export `expandStateCategory(category: string): SubmissionState[]` for API filtering
- This avoids duplicating state-to-category mapping in page.tsx, submissions/route.ts, and stats/route.ts

**Test Plan**:
- **File**: `src/lib/__tests__/submission-categories.test.ts`
- **Tests**:
  - **TC-012**: getStateCategory maps correctly
    - Given state "RECEIVED"
    - When getStateCategory is called
    - Then returns "active"
  - **TC-013**: expandStateCategory expands "active"
    - Given category "active"
    - When expandStateCategory is called
    - Then returns ["RECEIVED", "TIER1_SCANNING", "TIER2_SCANNING"]

**Dependencies**: None
**Status**: [ ] Not Started

---

## Phase 3: Q Page Frontend Overhaul

### US-003: Server-Side Paginated Queue Page (Frontend side)

#### T-007: Refactor queue page to server-side pagination

**Description**: Rewrite the fetch logic in `src/app/queue/page.tsx` to request only the current page from the API with server-side filter/sort/pagination params. Remove the 500-row client-side approach.

**References**: AC-US3-02, AC-US3-03, AC-US3-04, AC-US3-05

**Implementation Details**:
- Change `fetchQueue` to call `GET /api/v1/submissions?limit=${pageSize}&offset=${offset}&state=${filter}&sort=${sortCol}&sortDir=${sortDir}`
- Change stat cards to fetch from `GET /api/v1/submissions/stats` on mount
- Remove client-side `filteredSubmissions` useMemo (server handles filtering)
- Remove client-side sort (server handles sorting)
- Keep `pageSubmissions = submissions` (already paginated from server)
- Update `handleFilter` to re-fetch with new state param
- Update `handleSort` to re-fetch with new sort/sortDir params
- Update page navigation to re-fetch with new offset
- Store `totalCount` from API response for pagination controls

**Test Plan**:
- **File**: `src/app/queue/__tests__/page.test.tsx` (if exists) or manual verification
- **Tests**:
  - **TC-014**: Initial load fetches limit=50 offset=0
    - Given page mounts
    - When initial fetch fires
    - Then API called with limit=50&offset=0 (not limit=500)
  - **TC-015**: Filter change triggers server-side refetch
    - Given user clicks "Active" stat card
    - When handleFilter("active") fires
    - Then API called with state=active
  - **TC-016**: Stat cards populated from /stats endpoint
    - Given page mounts
    - When stats endpoint responds
    - Then stat cards show correct counts from API, not derived from row data

**Dependencies**: T-004, T-005, T-006
**Status**: [ ] Not Started

---

### US-004: SSE In-Place Updates

#### T-008: Implement SSE in-place update handler

**Description**: Replace the `onEvent` callback that calls `fetchQueue()` with a handler that updates the specific submission in React state and adjusts stat counters optimistically.

**References**: AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-04, AC-US4-05

**Implementation Details**:
- On `state_changed` event: find submission by ID in state, update its `state` field. Use `getStateCategory` to determine if counter update needed.
- On `submission_created` event: prepend new row if it matches current filter. Increment total count and appropriate category counter.
- On `scan_complete` event: find submission by ID, update `score` field. Recalculate avg score.
- Remove `fetchQueue()` call from onEvent handler.
- Change polling fallback from `5000` to `30000` ms when SSE disconnected.
- Keep flash animation logic (it already works with submissionId).
- The stats counters need local state that gets periodically reconciled with a /stats refresh (every 30s).

**Test Plan**:
- **File**: `src/app/queue/__tests__/sse-handler.test.ts`
- **Tests**:
  - **TC-017**: state_changed updates row in-place
    - Given submissions state has a row with id "sub_123" state "RECEIVED"
    - When SSE event `{ submissionId: "sub_123", state: "TIER1_SCANNING" }` fires
    - Then that row's state becomes "TIER1_SCANNING" without API call
  - **TC-018**: submission_created prepends new row
    - Given submissions state has 50 rows
    - When SSE `submission_created` event fires with new submissionId
    - Then row count becomes 51 with new row at top
  - **TC-019**: Polling interval is 30s when SSE disconnected
    - Given connected === false
    - When polling interval is set
    - Then interval is 30000ms, not 5000ms

**Dependencies**: T-006, T-007
**Status**: [ ] Not Started

---

## Phase 4: Verification

#### T-009: End-to-end build and deploy verification

**Description**: Run full build, verify all tests pass, confirm deployment readiness.

**References**: AC-US1-02, AC-US1-03

**Implementation Details**:
- Run `npm run build` -- must succeed
- Run `npm test` -- all tests must pass
- Verify wrangler.jsonc unchanged (no config regressions)
- Confirm push-deploy.sh flow works with dry-run if available

**Test Plan**:
- **Tests**:
  - **TC-020**: Full build passes
    - Given all code changes applied
    - When `npm run build` executes
    - Then exit code 0, no errors
  - **TC-021**: All tests pass
    - Given all code changes and new tests
    - When `npm test` runs
    - Then all suites pass with coverage >= 80% on new code

**Dependencies**: T-001 through T-008
**Status**: [ ] Not Started
