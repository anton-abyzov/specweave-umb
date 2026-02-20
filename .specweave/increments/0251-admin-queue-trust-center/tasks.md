# Tasks: Admin Queue Actions & Trust Center Consolidation

## Task Notation

- `[T###]`: Task ID
- `[P]`: Parallelizable
- `[ ]`: Not started
- `[x]`: Completed
- Model hints: haiku (simple), opus (default)

---

## Phase 1: Foundation

### T-001: Create useAdminStatus hook
**User Story**: US-001, US-003 | **Satisfies ACs**: AC-US1-02, AC-US3-01 | **Status**: [x] completed
**AC**: AC-US1-02, AC-US3-01

**Description**: Create a reusable hook that checks if the current user is an admin by calling `/api/v1/auth/me` and inspecting the response for admin role. Returns `{ isAdmin, isLoading }`.

**Implementation Details**:
- Create `src/app/hooks/useAdminStatus.ts`
- Call `/api/v1/auth/me` with credentials on mount
- Parse response for admin flag (check existing auth/me response shape)
- Return `{ isAdmin: boolean, isLoading: boolean }`
- Cache result in state to avoid repeated calls

**Test Plan**:
- **File**: `src/app/hooks/__tests__/useAdminStatus.test.ts`
- **Tests**:
  - **TC-001**: Returns isAdmin=true when auth/me returns admin role
    - Given a mocked `/api/v1/auth/me` returning `{ id: "1", role: "ADMIN" }`
    - When the hook is rendered
    - Then isAdmin is true and isLoading is false
  - **TC-002**: Returns isAdmin=false when auth/me returns non-admin user
    - Given a mocked `/api/v1/auth/me` returning `{ id: "1", role: "USER" }`
    - When the hook is rendered
    - Then isAdmin is false and isLoading is false
  - **TC-003**: Returns isAdmin=false when auth/me fails (unauthenticated)
    - Given a mocked `/api/v1/auth/me` returning 401
    - When the hook is rendered
    - Then isAdmin is false and isLoading is false

**Dependencies**: None
**Status**: [ ] Not Started

---

### T-002: Extract VerifiedSkillsTab component from audits page [P]
**User Story**: US-002 | **Satisfies ACs**: AC-US2-02 | **Status**: [x] completed
**AC**: AC-US2-02

**Description**: Extract the audits table (filters, sort, pagination, table) from `src/app/audits/page.tsx` into a standalone component `src/app/trust/VerifiedSkillsTab.tsx` that can be rendered inside the Trust Center.

**Implementation Details**:
- Create `src/app/trust/VerifiedSkillsTab.tsx`
- Move all audit types, state, fetch logic, and table rendering from `audits/page.tsx`
- Remove the `<main>` wrapper and `<h1>` header (those will come from the Trust Center layout)
- Keep all filter/sort/pagination logic intact
- The component should be self-contained (own state, own data fetching)

**Test Plan**:
- **File**: `src/app/trust/__tests__/VerifiedSkillsTab.test.tsx`
- **Tests**:
  - **TC-004**: Renders loading state initially
    - Given the component is mounted
    - When the fetch has not yet resolved
    - Then "Loading audits..." is displayed
  - **TC-005**: Renders audit table with data
    - Given a mocked `/api/v1/audits` returning 2 audit entries
    - When the component renders
    - Then 2 rows are visible in the table
  - **TC-006**: Filter buttons change active filter
    - Given the component is rendered with data
    - When "PASS" filter button is clicked
    - Then the fetch is called with status=PASS parameter

**Dependencies**: None
**Status**: [ ] Not Started

---

### T-003: Extract BlockedSkillsTab component from blocklist page [P]
**User Story**: US-002 | **Satisfies ACs**: AC-US2-03 | **Status**: [x] completed
**AC**: AC-US2-03

**Description**: Extract the blocklist table (search, expandable rows) from `src/app/blocklist/page.tsx` into a standalone component `src/app/trust/BlockedSkillsTab.tsx`.

**Implementation Details**:
- Create `src/app/trust/BlockedSkillsTab.tsx`
- Move all blocklist types, state, fetch logic, and table rendering from `blocklist/page.tsx`
- Remove the `<main>` wrapper and `<h1>` header
- Keep search, expand, severity sorting intact
- Self-contained component

**Test Plan**:
- **File**: `src/app/trust/__tests__/BlockedSkillsTab.test.tsx`
- **Tests**:
  - **TC-007**: Renders loading state initially
    - Given the component is mounted
    - When the fetch has not yet resolved
    - Then "Loading blocklist..." is displayed
  - **TC-008**: Renders blocklist entries
    - Given a mocked `/api/v1/blocklist` returning 3 entries
    - When the component renders
    - Then 3 rows are visible in the table
  - **TC-009**: Search filters entries by skill name
    - Given the component has loaded entries
    - When user types "malware" into the search input
    - Then only entries with "malware" in skill name are shown

**Dependencies**: None
**Status**: [ ] Not Started

---

## Phase 2: Core Functionality

### T-004: Build Trust Center page with tab navigation
**User Story**: US-002, US-004 | **Satisfies ACs**: AC-US2-01, AC-US2-05, AC-US4-01, AC-US4-02, AC-US4-03 | **Status**: [x] completed
**AC**: AC-US2-01, AC-US2-05, AC-US4-01, AC-US4-02, AC-US4-03

**Description**: Create the Trust Center page at `/trust` with a tabbed interface. Three tabs: Verified Skills, Blocked Skills, Reports. Tab state managed via URL search params (`?tab=verified|blocked|reports`).

**Implementation Details**:
- Create `src/app/trust/page.tsx` as a client component
- Use `useSearchParams()` to read/write tab state
- Default tab: "verified"
- Tab bar with 3 buttons, active tab visually highlighted
- Conditionally render VerifiedSkillsTab, BlockedSkillsTab, or ReportsTab based on active tab
- Use SectionDivider component for consistent header style
- Match the Queue page layout patterns (max-width 960, padding)

**Test Plan**:
- **File**: `src/app/trust/__tests__/TrustCenterPage.test.tsx`
- **Tests**:
  - **TC-010**: Default tab is "verified" when no query param
    - Given the page is rendered with no search params
    - When it mounts
    - Then the Verified Skills tab content is shown
  - **TC-011**: Tab switches to "blocked" on click
    - Given the page is rendered
    - When user clicks "Blocked Skills" tab
    - Then the Blocked Skills tab content is shown and URL updates
  - **TC-012**: Reads tab from URL search params
    - Given the page is rendered with `?tab=blocked`
    - When it mounts
    - Then the Blocked Skills tab content is shown

**Dependencies**: T-002, T-003
**Status**: [ ] Not Started

---

### T-005: Create Reports placeholder tab [P]
**User Story**: US-002 | **Satisfies ACs**: AC-US2-04 | **Status**: [x] completed
**AC**: AC-US2-04

**Description**: Create a placeholder Reports tab component that displays an informational message about upcoming community security reporting.

**Implementation Details**:
- Create `src/app/trust/ReportsTab.tsx`
- Simple component with an empty-state message: "Community security reports coming soon."
- Match the visual style of the other tabs (mono font, muted colors)

**Test Plan**:
- **File**: `src/app/trust/__tests__/ReportsTab.test.tsx`
- **Tests**:
  - **TC-013**: Renders placeholder text
    - Given the component is mounted
    - When it renders
    - Then text containing "coming soon" is displayed

**Dependencies**: None
**Status**: [ ] Not Started

---

### T-006: Implement admin dequeue API endpoint
**User Story**: US-001 | **Satisfies ACs**: AC-US1-03, AC-US1-05 | **Status**: [x] completed
**AC**: AC-US1-03, AC-US1-05

**Description**: Create `POST /api/v1/admin/submissions/:id/dequeue` API endpoint. Transitions a submission to "DEQUEUED" state. Admin JWT required.

**Implementation Details**:
- Create `src/app/api/v1/admin/submissions/[id]/dequeue/route.ts`
- Verify admin JWT from Authorization header
- Find submission by ID, verify it is in an active state (RECEIVED, TIER1_SCANNING, TIER2_SCANNING)
- Update submission state to "DEQUEUED"
- Create state event entry for audit trail
- Return updated submission

**Test Plan**:
- **File**: `src/app/api/v1/admin/submissions/[id]/dequeue/__tests__/route.test.ts`
- **Tests**:
  - **TC-014**: Successfully dequeues a RECEIVED submission
    - Given a submission in RECEIVED state and a valid admin token
    - When POST is sent to dequeue endpoint
    - Then submission state is updated to DEQUEUED and 200 returned
  - **TC-015**: Rejects request without admin token
    - Given no Authorization header
    - When POST is sent to dequeue endpoint
    - Then 401 is returned
  - **TC-016**: Rejects dequeue of non-active submission
    - Given a submission in PUBLISHED state
    - When POST is sent to dequeue endpoint
    - Then 400 is returned with error message

**Dependencies**: None
**Status**: [ ] Not Started

---

### T-007: Implement admin reprioritize API endpoint
**User Story**: US-001 | **Satisfies ACs**: AC-US1-04, AC-US1-05 | **Status**: [x] completed
**AC**: AC-US1-04, AC-US1-05

**Description**: Create `POST /api/v1/admin/submissions/:id/reprioritize` API endpoint. Accepts `{ position: "front" | "back" }` to adjust submission queue position. Admin JWT required.

**Implementation Details**:
- Create `src/app/api/v1/admin/submissions/[id]/reprioritize/route.ts`
- Verify admin JWT
- Validate body has `position` field with value "front" or "back"
- For "front": Update submission `createdAt` to current timestamp (or use re-enqueue mechanism)
- For "back": Update submission `createdAt` to oldest timestamp minus 1
- Create state event for audit trail
- Return updated submission

**Test Plan**:
- **File**: `src/app/api/v1/admin/submissions/[id]/reprioritize/__tests__/route.test.ts`
- **Tests**:
  - **TC-017**: Successfully reprioritizes to front
    - Given a RECEIVED submission and valid admin token
    - When POST with `{ position: "front" }` is sent
    - Then 200 is returned with success
  - **TC-018**: Successfully reprioritizes to back
    - Given a RECEIVED submission and valid admin token
    - When POST with `{ position: "back" }` is sent
    - Then 200 is returned with success
  - **TC-019**: Rejects invalid position value
    - Given a valid admin token
    - When POST with `{ position: "invalid" }` is sent
    - Then 400 is returned

**Dependencies**: None
**Status**: [ ] Not Started

---

### T-008: Add admin action buttons to Queue page
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-06 | **Status**: [x] completed
**AC**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-06

**Description**: Add conditional admin action buttons (Dequeue, Reprioritize) to each submission card in the public queue page. Only visible to authenticated admins.

**Implementation Details**:
- Import and use `useAdminStatus` hook in `queue/page.tsx`
- Create `AdminQueueActions` component that renders Dequeue + Reprioritize buttons
- Pass `isAdmin` to SubmissionCard; render AdminQueueActions when true
- Dequeue button: confirmation dialog, then calls `/api/v1/admin/submissions/:id/dequeue`
- Reprioritize: dropdown with "Bump to Front" / "Move to Back", calls reprioritize endpoint
- After action success, call `fetchQueue()` to refresh the list
- Use admin JWT from localStorage for API calls
- Buttons styled subtly (small, muted) to not dominate the card

**Test Plan**:
- **File**: `src/app/queue/__tests__/AdminQueueActions.test.tsx`
- **Tests**:
  - **TC-020**: Admin buttons not rendered when isAdmin is false
    - Given isAdmin is false
    - When SubmissionCard renders
    - Then no Dequeue or Reprioritize buttons are present
  - **TC-021**: Admin buttons rendered when isAdmin is true
    - Given isAdmin is true
    - When SubmissionCard renders
    - Then Dequeue and Reprioritize buttons are visible
  - **TC-022**: Dequeue button calls API and triggers refresh
    - Given isAdmin is true and Dequeue is clicked then confirmed
    - When the API call succeeds
    - Then fetchQueue is called to refresh

**Dependencies**: T-001, T-006, T-007
**Status**: [ ] Not Started

---

## Phase 3: Navigation & Redirects

### T-009: Add redirects from old routes to Trust Center
**User Story**: US-002 | **Satisfies ACs**: AC-US2-06 | **Status**: [x] completed
**AC**: AC-US2-06

**Description**: Make `/audits` redirect to `/trust?tab=verified` and `/blocklist` redirect to `/trust?tab=blocked`. Replace the existing page content with redirect calls.

**Implementation Details**:
- Update `src/app/audits/page.tsx` to use Next.js `redirect()` from `next/navigation`
- Update `src/app/blocklist/page.tsx` to use Next.js `redirect()`
- Both become simple server components that redirect on render
- Use permanent redirect (308) to signal search engines

**Test Plan**:
- **File**: `src/app/trust/__tests__/redirects.test.ts`
- **Tests**:
  - **TC-023**: /audits redirects to /trust?tab=verified
    - Given a request to /audits
    - When the page renders
    - Then redirect() is called with /trust?tab=verified
  - **TC-024**: /blocklist redirects to /trust?tab=blocked
    - Given a request to /blocklist
    - When the page renders
    - Then redirect() is called with /trust?tab=blocked

**Dependencies**: T-004
**Status**: [ ] Not Started

---

### T-010: Update site navigation (navbar, footer, mobile nav)
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03 | **Status**: [x] completed
**AC**: AC-US3-01, AC-US3-02, AC-US3-03

**Description**: Replace the separate "Audits" and "Blocklist" nav links with a single "Trust Center" link in the main navbar, footer, and mobile nav.

**Implementation Details**:
- Edit `src/app/layout.tsx`:
  - In `navLinks`: Remove `<a href="/audits">Audits</a>` and `<a href="/blocklist">Blocklist</a>`, add `<a href="/trust">Trust Center</a>`
  - In footer: Same replacement
- Edit `src/app/components/MobileNav.tsx`:
  - Add "Trust Center" link to `/trust`
  - No "Audits" or "Blocklist" links needed (they were not in MobileNav but verify)

**Test Plan**:
- **File**: `src/app/__tests__/navigation.test.tsx`
- **Tests**:
  - **TC-025**: Navbar contains Trust Center link
    - Given the root layout renders
    - When checking nav links
    - Then a link to /trust with text "Trust Center" exists
  - **TC-026**: Navbar does not contain separate Audits link
    - Given the root layout renders
    - When checking nav links
    - Then no link with text "Audits" exists
  - **TC-027**: Navbar does not contain separate Blocklist link
    - Given the root layout renders
    - When checking nav links
    - Then no link with text "Blocklist" exists

**Dependencies**: T-004
**Status**: [ ] Not Started

---

## Phase 4: Verification

### T-011: Integration verification and smoke test
**User Story**: US-001, US-002, US-003, US-004 | **Satisfies ACs**: All | **Status**: [x] completed
**AC**: AC-US1-01, AC-US1-02, AC-US2-01, AC-US2-06, AC-US3-01, AC-US4-02

**Description**: Run full test suite, verify all acceptance criteria, check no regressions in existing functionality.

**Implementation Details**:
- Run `npm run test` to execute all unit/component tests
- Run `npm run build` to verify no build errors
- Manually verify (or document for manual QA):
  - `/trust` loads with 3 tabs working
  - `/audits` redirects to `/trust?tab=verified`
  - `/blocklist` redirects to `/trust?tab=blocked`
  - Queue page shows admin buttons when logged in as admin
  - Queue page hides admin buttons for regular users
  - Navigation shows "Trust Center" instead of "Audits" and "Blocklist"

**Test Plan**:
- **File**: N/A (runs existing test suite)
- **Tests**:
  - **TC-028**: All tests pass
    - Given the full test suite
    - When `npm run test` is executed
    - Then all tests pass with 0 failures
  - **TC-029**: Build succeeds
    - Given the project
    - When `npm run build` is executed
    - Then the build completes successfully

**Dependencies**: T-001 through T-010
**Status**: [ ] Not Started
