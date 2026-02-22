# Tasks: Community Problem Reporting

## Task Notation

- `[T###]`: Task ID
- `[P]`: Parallelizable
- `[ ]`: Not started
- `[x]`: Completed
- Model hints: haiku (simple), opus (default)

## Phase 1: Data Layer

### T-001: Add ProblemReport Prisma Model and Migration
**User Story**: US-001 | **Satisfies ACs**: AC-US1-04 | **Status**: [x] completed

**Description**: Add ProblemReportType enum (BUG, FEATURE_REQUEST, CONTENT_ISSUE, OTHER), ProblemReportStatus enum (OPEN, IN_REVIEW, RESOLVED, CLOSED), and ProblemReport model to schema.prisma. Add relation fields to User and Skill models. Generate and apply migration.

**Implementation Details**:
- Add enums to schema.prisma
- Add ProblemReport model with userId (required FK to User), skillId (optional FK to Skill), type, title, description, status, timestamps
- Add `problemReports ProblemReport[]` to User and Skill models
- Add indexes on userId, skillId, status, createdAt
- Run `npx prisma migrate dev --name add_problem_reports`

**Test Plan**:
- **File**: N/A (schema validation via migration)
- **Tests**:
  - **TC-001**: Migration applies without errors
    - Given the current database schema
    - When prisma migrate dev runs
    - Then migration succeeds and new tables/enums are created

**Dependencies**: None
**Status**: [x] completed

---

### T-002: Implement POST /api/v1/problem-reports API Route
**User Story**: US-001, US-002 | **Satisfies ACs**: AC-US1-04, AC-US1-05, AC-US1-06, AC-US2-04, AC-US2-05 | **Status**: [x] completed

**Description**: Create API route to submit a problem report. Requires user auth via requireUser. Validates input, resolves optional skillName to skillId, rate limits per user, saves to DB, triggers admin email notification (best-effort).

**Implementation Details**:
- Create `src/app/api/v1/problem-reports/route.ts`
- Add Zod schema: ProblemReportCreateSchema (type, title 1-200 chars, description 1-5000 chars, skillName optional)
- Use requireUser for auth (extract userId from JWT)
- Rate limit: 10/hour per user via RATE_LIMIT_KV key `problem-report:{userId}`
- Resolve skillName to skillId via Prisma query (null if not found)
- Create ProblemReport record
- Fire-and-forget admin email notification
- Return 201 with report summary

**Test Plan**:
- **File**: `src/app/api/v1/problem-reports/__tests__/route.test.ts`
- **Tests**:
  - **TC-002**: Rejects unauthenticated request with 401
    - Given no vskill_access cookie
    - When POST /api/v1/problem-reports
    - Then returns 401
  - **TC-003**: Rejects invalid body with 400
    - Given authenticated user
    - When POST with missing title
    - Then returns 400 with validation errors
  - **TC-004**: Creates report successfully with skill name
    - Given authenticated user and valid body with skillName
    - When POST /api/v1/problem-reports
    - Then returns 201 with report, skillId is resolved
  - **TC-005**: Creates report successfully without skill name
    - Given authenticated user and valid body without skillName
    - When POST /api/v1/problem-reports
    - Then returns 201 with report, skillId is null
  - **TC-006**: Rate limits excessive submissions
    - Given authenticated user who has submitted 10 reports in the last hour
    - When POST /api/v1/problem-reports
    - Then returns 429
  - **TC-007**: Rejects title over 200 chars
    - Given authenticated user
    - When POST with title of 201 chars
    - Then returns 400
  - **TC-008**: Rejects description over 5000 chars
    - Given authenticated user
    - When POST with description of 5001 chars
    - Then returns 400

**Dependencies**: T-001
**Status**: [x] completed

---

### T-003: Implement GET /api/v1/problem-reports/mine API Route
**User Story**: US-003 | **Satisfies ACs**: AC-US3-02, AC-US3-03, AC-US3-04, AC-US3-05 | **Status**: [x] completed

**Description**: Create API route to list the current user's problem reports. Requires user auth. Returns paginated list with skill name joined.

**Implementation Details**:
- Add GET handler to `src/app/api/v1/problem-reports/mine/route.ts`
- Use requireUser for auth
- Parse pagination params (page, limit with max 50)
- Query ProblemReport where userId matches, ordered by createdAt desc
- Include skill name via Prisma include
- Return paginated response

**Test Plan**:
- **File**: `src/app/api/v1/problem-reports/mine/__tests__/route.test.ts`
- **Tests**:
  - **TC-009**: Rejects unauthenticated request with 401
    - Given no vskill_access cookie
    - When GET /api/v1/problem-reports/mine
    - Then returns 401
  - **TC-010**: Returns empty list for user with no reports
    - Given authenticated user with no reports
    - When GET /api/v1/problem-reports/mine
    - Then returns 200 with empty reports array and total 0
  - **TC-011**: Returns paginated reports for user
    - Given authenticated user with 25 reports
    - When GET /api/v1/problem-reports/mine?page=1&limit=20
    - Then returns 200 with 20 reports, total 25
  - **TC-012**: Only returns reports belonging to current user
    - Given user A with 3 reports and user B with 5 reports
    - When user A calls GET /api/v1/problem-reports/mine
    - Then returns only user A's 3 reports

**Dependencies**: T-001
**Status**: [x] completed

---

## Phase 2: UI Components

### T-004: Create ReportProblemModal Client Component
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-05, AC-US1-06 | **Status**: [x] completed

**Description**: Create a "use client" modal component for reporting problems from the skill detail page. Pre-fills skill name. Checks auth status and shows login prompt if not authenticated. Submits to POST /api/v1/problem-reports.

**Implementation Details**:
- Create `src/app/skills/[name]/ReportProblemModal.tsx`
- Props: `skillName: string`
- State: open/closed, form fields, loading, error, success
- Check auth via `/api/v1/auth/me` on mount (cache result)
- If not authed: show "Login to report a problem" with link to GitHub OAuth
- Form: type dropdown, title input, description textarea
- Submit via fetch to POST API
- Show inline validation errors
- Show success message and auto-close on success
- Style: terminal/mono aesthetic matching existing components (Geist Mono, var(--border), var(--text), etc.)

**Test Plan**:
- **File**: `src/app/skills/[name]/__tests__/ReportProblemModal.test.tsx`
- **Tests**:
  - **TC-013**: Renders report button
    - Given the component is mounted
    - When rendered
    - Then a "Report a problem" button is visible
  - **TC-014**: Opens modal on button click
    - Given the component is mounted
    - When user clicks "Report a problem"
    - Then the modal form is visible
  - **TC-015**: Shows login prompt when not authenticated
    - Given user is not authenticated (/api/v1/auth/me returns 401)
    - When modal is opened
    - Then shows "Login to report a problem" message

**Dependencies**: T-002
**Status**: [x] completed

---

### T-005: Add ReportProblemModal to Skill Detail Page
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02 | **Status**: [x] completed

**Description**: Import and render ReportProblemModal on the skill detail page, passing the skill name.

**Implementation Details**:
- Import ReportProblemModal in `src/app/skills/[name]/page.tsx`
- Add it near the bottom of the page content (before closing main tag)
- Pass `skillName={skill.name}`

**Test Plan**:
- **File**: N/A (visual integration -- verified by TC-013)
- **Tests**:
  - **TC-016**: Skill detail page includes report button
    - Given a skill detail page renders
    - When the page loads
    - Then "Report a problem" button is present in the DOM

**Dependencies**: T-004
**Status**: [x] completed

---

### T-006: Create Standalone /report Page
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04, AC-US2-05, AC-US2-06 | **Status**: [x] completed

**Description**: Create a standalone /report page with a report form. Includes an optional skill selector dropdown. Supports `?skill=<name>` query parameter for pre-selection. Requires authentication.

**Implementation Details**:
- Create `src/app/report/page.tsx` (client component)
- Check auth on mount; show login prompt if not authenticated
- Fetch skills list from `/api/v1/skills?limit=100` for the dropdown (name + displayName)
- If `?skill=<name>` in URL, pre-select that skill
- Form: skill dropdown (optional), type dropdown, title, description
- Submit to POST /api/v1/problem-reports
- Show success/error feedback
- Style: consistent terminal/mono aesthetic
- Add link to "My Reports" at top of page

**Test Plan**:
- **File**: `src/app/report/__tests__/page.test.tsx`
- **Tests**:
  - **TC-017**: Renders report form
    - Given authenticated user visits /report
    - When the page loads
    - Then the form with type, title, description fields is visible
  - **TC-018**: Pre-selects skill from query param
    - Given URL is /report?skill=my-skill
    - When the page loads
    - Then the skill dropdown has "my-skill" selected
  - **TC-019**: Shows login prompt when unauthenticated
    - Given unauthenticated user visits /report
    - When the page loads
    - Then shows login prompt

**Dependencies**: T-002
**Status**: [x] completed

---

### T-007: Create My Reports Page
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04, AC-US3-05 | **Status**: [x] completed

**Description**: Create a /report/my-reports page that lists the current user's submitted reports with status tracking.

**Implementation Details**:
- Create `src/app/report/my-reports/page.tsx` (client component)
- Check auth on mount; show login prompt if not authenticated
- Fetch from GET /api/v1/problem-reports/mine with pagination
- Display table/list: title, type badge, skill name (or "General"), status badge (color-coded), date
- Status colors: OPEN = yellow, IN_REVIEW = blue, RESOLVED = green, CLOSED = gray
- Pagination controls
- Style: terminal/mono aesthetic, consistent with existing pages
- Link back to /report

**Test Plan**:
- **File**: `src/app/report/my-reports/__tests__/page.test.tsx`
- **Tests**:
  - **TC-020**: Renders report list
    - Given authenticated user with reports
    - When the page loads
    - Then reports are listed with title, type, status, and date
  - **TC-021**: Shows empty state
    - Given authenticated user with no reports
    - When the page loads
    - Then shows "No reports yet" message
  - **TC-022**: Requires authentication
    - Given unauthenticated user
    - When visiting /report/my-reports
    - Then shows login prompt

**Dependencies**: T-003
**Status**: [x] completed

---

## Phase 3: Notifications

### T-008: Admin Email Notification on New Report
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02, AC-US4-03 | **Status**: [x] completed

**Description**: Send a notification email to the configured admin address when a new problem report is submitted. Best-effort -- should not block the submission response.

**Implementation Details**:
- Create `src/lib/problem-report-notify.ts`
- Function: `notifyAdminNewReport(report: { id, title, type, skillName?, reporterUsername })`
- Read admin email from `ADMIN_NOTIFICATION_EMAIL` env var
- Use existing email sending infrastructure or Resend API
- Format email with report details and link to admin area
- Call from POST handler in fire-and-forget pattern (no await, catch errors silently)

**Test Plan**:
- **File**: `src/lib/__tests__/problem-report-notify.test.ts`
- **Tests**:
  - **TC-023**: Sends email with correct content
    - Given ADMIN_NOTIFICATION_EMAIL is set
    - When notifyAdminNewReport is called
    - Then email is sent with report title, type, and reporter username
  - **TC-024**: Does not throw when email sending fails
    - Given email service is unavailable
    - When notifyAdminNewReport is called
    - Then no error is thrown (silent failure)
  - **TC-025**: Skips notification when no admin email configured
    - Given ADMIN_NOTIFICATION_EMAIL is not set
    - When notifyAdminNewReport is called
    - Then no email is sent and no error thrown

**Dependencies**: T-002
**Status**: [x] completed

---

## Phase 4: Integration & Polish

### T-009: Add Navigation Links
**User Story**: US-002, US-003 | **Satisfies ACs**: AC-US2-01, AC-US3-01 | **Status**: [x] completed

**Description**: Add links to /report and /report/my-reports from relevant navigation points.

**Implementation Details**:
- Add "Report" link to site footer or secondary nav
- Add "My Reports" link to UserNav dropdown (when authenticated)
- Add "My Reports" link at top of /report page

**Test Plan**:
- **File**: N/A (visual integration)
- **Tests**:
  - **TC-026**: Report link is accessible from navigation
    - Given user is on any page
    - When looking at navigation
    - Then "Report" link is visible

**Dependencies**: T-006, T-007
**Status**: [x] completed

---

### T-010: End-to-End Verification
**User Story**: All | **Satisfies ACs**: All | **Status**: [x] completed

**Description**: Run all tests, verify all acceptance criteria, ensure build succeeds.

**Implementation Details**:
- Run `npm run test` in vskill-platform
- Run `npm run build` to verify no type errors
- Manually verify: modal on skill page, standalone page, my reports page
- Verify rate limiting works
- Check email notification fires

**Test Plan**:
- **File**: N/A (integration verification)
- **Tests**:
  - **TC-027**: All unit tests pass
    - Given implementation is complete
    - When running npm run test
    - Then all tests pass with >80% coverage on new files
  - **TC-028**: Build succeeds
    - Given all code is written
    - When running npm run build
    - Then build completes without errors

**Dependencies**: T-001 through T-009
**Status**: [x] completed
