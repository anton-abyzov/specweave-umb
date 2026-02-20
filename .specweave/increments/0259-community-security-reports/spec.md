# 0259: Community Security Reports

## Problem
The Trust Center Reports tab is a placeholder showing "coming soon." Users have no way to report suspicious skills, flag false positives, or request re-scans. This is a critical feedback loop gap in the trust infrastructure.

## Solution
Implement a public community reporting system integrated into the Trust Center Reports tab. Users can submit security reports anonymously. Admins can review, resolve, or dismiss reports through a dedicated admin moderation panel. Confirmed malware reports auto-create BlocklistEntry records.

## User Stories

### US-001: Submit Security Report
As a community member, I want to report a suspicious skill so that the security team can investigate it.

**Acceptance Criteria:**
- [x] AC-US1-01: Public form at `/trust?tab=reports` with fields: skill name (required), report type (required), description (required), evidence URLs (optional), contact email (optional)
- [x] AC-US1-02: Report types: SECURITY_CONCERN, FALSE_POSITIVE, TYPOSQUATTING, MALWARE, OTHER
- [x] AC-US1-03: No authentication required to submit
- [x] AC-US1-04: Rate limited to 5 reports per IP per 15 minutes
- [x] AC-US1-05: Success confirmation shown after submission

### US-002: View Public Reports Feed
As a community member, I want to see recent reports and their resolution status for transparency.

**Acceptance Criteria:**
- [x] AC-US2-01: Public feed below the submission form showing recent reports
- [x] AC-US2-02: Each report shows: skill name, report type, status, date
- [x] AC-US2-03: Resolved reports show resolution note
- [x] AC-US2-04: Reports ordered newest-first, paginated (20 per page)

### US-003: Admin Report Moderation
As an admin, I want to review and resolve community reports so that security concerns are addressed.

**Acceptance Criteria:**
- [x] AC-US3-01: Admin reports page at `/admin/reports` with table of all reports
- [x] AC-US3-02: Filter by status (all, submitted, under_review, resolved, dismissed)
- [x] AC-US3-03: Admin can change status to UNDER_REVIEW, RESOLVED, or DISMISSED
- [x] AC-US3-04: Resolution requires a note explaining the outcome
- [x] AC-US3-05: "Reports" nav item added to admin sidebar
- [x] AC-US3-06: Resolving as "confirmed malware" auto-creates BlocklistEntry

## Technical Design

### Database: SecurityReport model
- id, skillName, reportType (enum), description, evidenceUrls, contactEmail
- status (enum: SUBMITTED, UNDER_REVIEW, RESOLVED, DISMISSED)
- resolutionNote, resolvedById (Admin relation)
- createdAt, updatedAt

### API Endpoints
- POST /api/v1/reports — public submit (rate limited)
- GET /api/v1/reports — public list (recent, paginated)
- GET /api/v1/admin/reports — admin list (filterable)
- PATCH /api/v1/admin/reports/[id] — admin update status

## Out of Scope
- Email notifications
- Report tracking by ID for reporters
- Bulk operations
