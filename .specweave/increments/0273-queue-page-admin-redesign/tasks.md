# 0273 - Queue Page Admin Dashboard Redesign — Tasks

## Phase 1: API Layer

### T-001: Extend GET /api/v1/submissions with offset and state params
**User Story**: US-006, US-002 | **Satisfies ACs**: AC-US6-04 | **Status**: [x] completed
**AC**: AC-US6-04
**Test**: Given GET /api/v1/submissions?offset=50&limit=25&state=PUBLISHED -> When the endpoint processes the request -> Then it returns 25 submissions starting from offset 50 filtered to PUBLISHED state, with correct total count

### T-002: Create GET /api/v1/submissions/search endpoint
**User Story**: US-003 | **Satisfies ACs**: AC-US3-03 | **Status**: [x] completed
**AC**: AC-US3-03
**Test**: Given GET /api/v1/submissions/search?q=code-review&limit=50 -> When the endpoint queries Prisma -> Then it returns submissions where skillName, repoUrl, or id contains "code-review" (case-insensitive) with total count

### T-003: Write tests for submissions search endpoint
**User Story**: US-003 | **Satisfies ACs**: AC-US3-03 | **Status**: [x] completed
**AC**: AC-US3-03
**Test**: Given search endpoint test suite -> When run -> Then tests cover: valid search, empty query (400), short query (400), state filter + search, empty results, limit/offset

### T-004: Write tests for extended submissions listing endpoint
**User Story**: US-006 | **Satisfies ACs**: AC-US6-04 | **Status**: [x] completed
**AC**: AC-US6-04
**Test**: Given updated listing endpoint tests -> When run -> Then tests cover: offset pagination, state filter, combined offset+state, default behavior unchanged

---

## Phase 2: Core Table Component

### T-005: Create SubmissionTable component with sortable columns
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-04, AC-US1-05, AC-US1-06 | **Status**: [x] completed
**AC**: AC-US1-01, AC-US1-02, AC-US1-04, AC-US1-05, AC-US1-06
**Test**: Given a list of submissions -> When rendered in SubmissionTable -> Then a table with columns (Skill Name, Repo, State, Score, Submitted, Updated, Actions) is displayed, sorted by Submitted desc by default, with clickable headers that toggle sort direction

### T-006: Implement clickable rows with navigation
**User Story**: US-001 | **Satisfies ACs**: AC-US1-03, AC-US1-08 | **Status**: [x] completed
**AC**: AC-US1-03, AC-US1-08
**Test**: Given a table row -> When clicked -> Then navigates to /submit/{id}; admin actions in Actions column do NOT trigger navigation

### T-007: Implement SSE flash highlighting on table rows
**User Story**: US-001 | **Satisfies ACs**: AC-US1-07 | **Status**: [x] completed
**AC**: AC-US1-07
**Test**: Given an SSE event for submission X -> When the event fires -> Then the corresponding table row briefly pulses with a highlight background for 2s

### T-008: Write SubmissionTable component tests
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01 through AC-US1-08 | **Status**: [x] completed
**AC**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05, AC-US1-06, AC-US1-07, AC-US1-08
**Test**: Given test suite for SubmissionTable -> When run -> Then tests cover: rendering columns, sorting, row click, flash, admin actions visibility

---

## Phase 3: Stat Card Filters

### T-009: Make stat cards clickable with URL-driven filter state
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04, AC-US2-05 | **Status**: [x] completed
**AC**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04, AC-US2-05
**Test**: Given stat cards -> When "Active" is clicked -> Then URL updates to ?filter=active, table shows only active submissions, Active card has selected styling; clicking "Total" clears filter

### T-010: Add Avg Score stat card
**User Story**: US-002 | **Satisfies ACs**: AC-US2-06 | **Status**: [x] completed
**AC**: AC-US2-06
**Test**: Given completed submissions with scores [80, 60, 90] -> When page renders -> Then Avg Score card shows "77"

---

## Phase 4: Search

### T-011: Implement debounced search input with URL state
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-04, AC-US3-06 | **Status**: [x] completed
**AC**: AC-US3-01, AC-US3-02, AC-US3-04, AC-US3-06
**Test**: Given search input -> When user types "review" and waits 300ms -> Then URL updates to ?q=review, API call fires, table shows search results; clearing input restores default

### T-012: Combine search with stat card filters
**User Story**: US-003 | **Satisfies ACs**: AC-US3-05 | **Status**: [x] completed
**AC**: AC-US3-05
**Test**: Given filter=active and q=scanner -> When both are set -> Then table shows only active submissions matching "scanner"

---

## Phase 5: GitHub Links

### T-013: Implement GitHub links in Repo column
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-04 | **Status**: [x] completed
**AC**: AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-04
**Test**: Given a submission with repoUrl "https://github.com/acme/skill" -> When rendered -> Then "acme/skill" is a link opening in new tab; clicking the link does NOT navigate to the submission detail page

---

## Phase 6: Queue Status Bar

### T-014: Create QueueStatusBar component
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01, AC-US5-02, AC-US5-03, AC-US5-04, AC-US5-05, AC-US5-06 | **Status**: [x] completed
**AC**: AC-US5-01, AC-US5-02, AC-US5-03, AC-US5-04, AC-US5-05, AC-US5-06
**Test**: Given admin user with connected SSE -> When status endpoint returns {paused: true, health: "degraded"} -> Then status bar shows green SSE dot, yellow "PAUSED" badge, amber "DEGRADED" health badge, and last updated time

### T-015: Write QueueStatusBar tests
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01 through AC-US5-06 | **Status**: [x] completed
**AC**: AC-US5-01, AC-US5-02, AC-US5-03, AC-US5-04, AC-US5-05, AC-US5-06
**Test**: Given test suite -> When run -> Then tests cover: admin sees full status, non-admin sees only SSE, paused state, health states, timestamp display

---

## Phase 7: Pagination

### T-016: Implement pagination controls below the table
**User Story**: US-006 | **Satisfies ACs**: AC-US6-01, AC-US6-02, AC-US6-03, AC-US6-05, AC-US6-06 | **Status**: [x] completed
**AC**: AC-US6-01, AC-US6-02, AC-US6-03, AC-US6-05, AC-US6-06
**Test**: Given 150 total submissions and page size 50 -> When page renders -> Then "Showing 1-50 of 150" with Next enabled and Previous disabled; clicking Next updates to page=2 and shows "Showing 51-100 of 150"; page size selector allows switching to 25/100

---

## Phase 8: Keyboard Shortcuts

### T-017: Create KeyboardShortcutOverlay component
**User Story**: US-007 | **Satisfies ACs**: AC-US7-05, AC-US7-07 | **Status**: [x] completed
**AC**: AC-US7-05, AC-US7-07
**Test**: Given user presses "?" -> When overlay renders -> Then a modal listing all shortcuts is shown with "/" for search, j/k for navigation, Enter for open, Esc for clear

### T-018: Implement keyboard navigation (/, j, k, Enter, Escape)
**User Story**: US-007 | **Satisfies ACs**: AC-US7-01, AC-US7-02, AC-US7-03, AC-US7-04, AC-US7-06 | **Status**: [x] completed
**AC**: AC-US7-01, AC-US7-02, AC-US7-03, AC-US7-04, AC-US7-06
**Test**: Given table with 5 rows -> When user presses "j" 3 times then "Enter" -> Then row 3 is highlighted then navigated to; pressing "/" focuses search; pressing Escape clears highlight; shortcuts disabled when typing in search

### T-019: Write keyboard shortcut tests
**User Story**: US-007 | **Satisfies ACs**: AC-US7-01 through AC-US7-07 | **Status**: [x] completed
**AC**: AC-US7-01, AC-US7-02, AC-US7-03, AC-US7-04, AC-US7-05, AC-US7-06, AC-US7-07
**Test**: Given test suite -> When run -> Then tests cover: / focuses search, j/k moves highlight, Enter navigates, Escape clears, ? opens overlay, shortcuts disabled in input

---

## Phase 9: Integration and Polish

### T-020: Rewrite main page.tsx to compose all new components
**User Story**: US-001 through US-007 | **Satisfies ACs**: All | **Status**: [x] completed
**AC**: AC-US1-01, AC-US2-01, AC-US3-01, AC-US4-01, AC-US5-01, AC-US6-01, AC-US7-01
**Test**: Given the /queue page -> When loaded -> Then all components render correctly: stat cards, status bar, search, table, pagination, keyboard shortcuts; SSE updates propagate to table; batch submit still works for admin

### T-021: Update existing page tests and add integration tests
**User Story**: US-001 through US-007 | **Satisfies ACs**: All | **Status**: [x] completed
**AC**: All ACs
**Test**: Given existing tests in queue/__tests__/page.test.tsx -> When updated and run -> Then all pass including: admin sees Submit Skills, non-admin does not, table renders, stat card filters work

### T-022: Adapt AdminQueueActions for table cell context
**User Story**: US-001 | **Satisfies ACs**: AC-US1-08 | **Status**: [x] completed
**AC**: AC-US1-08
**Test**: Given AdminQueueActions rendered inside a table cell -> When Dequeue button clicked -> Then action fires without triggering row click; styling fits table cell context (no card borders)

### T-023: Mobile responsive table with horizontal scroll
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01 | **Status**: [x] completed
**AC**: AC-US1-01
**Test**: Given viewport width < 768px -> When table renders -> Then table scrolls horizontally with Skill Name column sticky; stat cards stack 2x2 on mobile

### T-024: Verify dark/light theme compatibility
**User Story**: US-001 through US-007 | **Satisfies ACs**: NFR-06 | **Status**: [x] completed
**Test**: Given the page in dark theme -> When all components render -> Then all text, borders, backgrounds use CSS custom properties and are legible in both themes
