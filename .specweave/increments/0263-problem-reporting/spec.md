---
increment: 0263-problem-reporting
title: "Community Problem Reporting"
type: feature
priority: P1
status: planned
created: 2026-02-21
structure: user-stories
test_mode: TDD
coverage_target: 80
---

# Feature: Community Problem Reporting

## Overview

A problem/feedback reporting system for registered users on verified-skill.com. Users can report bugs, feature requests, content issues, and other problems via a modal on each skill detail page (pre-filled with skill name) or a standalone `/report` page for general/platform issues. Users can track their submitted reports through a "My Reports" view.

This is SEPARATE from the existing SecurityReport model, which handles security concerns (malware, typosquatting, etc.). ProblemReport is for general feedback and quality issues.

## User Stories

### US-001: Submit Problem Report from Skill Page (P1)
**Project**: vskill-platform

**As a** registered user viewing a skill detail page
**I want** to report a problem or feedback about that skill via a modal
**So that** I can quickly flag bugs, request features, or report content issues with relevant context pre-filled

**Acceptance Criteria**:
- [ ] **AC-US1-01**: A "Report a problem" button is visible on each skill detail page
- [ ] **AC-US1-02**: Clicking the button opens a modal form (client-side) pre-filled with the skill name
- [ ] **AC-US1-03**: The modal requires authentication -- unauthenticated users see a "Login to report" prompt
- [ ] **AC-US1-04**: The form includes: type selector (BUG, FEATURE_REQUEST, CONTENT_ISSUE, OTHER), title (required, max 200 chars), description (required, max 5000 chars)
- [ ] **AC-US1-05**: On successful submission, the modal shows a confirmation message and closes
- [ ] **AC-US1-06**: Validation errors are displayed inline in the form

---

### US-002: Submit Problem Report from Standalone Page (P1)
**Project**: vskill-platform

**As a** registered user
**I want** to submit a problem report from a standalone `/report` page
**So that** I can report general platform issues or problems not tied to a specific skill

**Acceptance Criteria**:
- [ ] **AC-US2-01**: A `/report` page exists and is accessible from site navigation
- [ ] **AC-US2-02**: The page requires authentication -- redirects or shows login prompt for unauthenticated users
- [ ] **AC-US2-03**: The form includes an optional skill selector dropdown (fetches published skills)
- [ ] **AC-US2-04**: The form includes: type selector, title, description (same validation as modal)
- [ ] **AC-US2-05**: On successful submission, a confirmation message is shown
- [ ] **AC-US2-06**: If navigated to with `?skill=<name>` query param, the skill is pre-selected

---

### US-003: View My Reports (P2)
**Project**: vskill-platform

**As a** registered user
**I want** to view a list of my submitted reports and their status
**So that** I can track whether my feedback has been acknowledged or resolved

**Acceptance Criteria**:
- [ ] **AC-US3-01**: A "My Reports" page exists at `/report/my-reports`
- [ ] **AC-US3-02**: The page lists all reports submitted by the current user, ordered by newest first
- [ ] **AC-US3-03**: Each report shows: title, type, skill name (if any), status (OPEN, IN_REVIEW, RESOLVED, CLOSED), creation date
- [ ] **AC-US3-04**: Reports are paginated (20 per page)
- [ ] **AC-US3-05**: The page requires authentication

---

### US-004: Admin Email Notification (P2)
**Project**: vskill-platform

**As a** platform admin
**I want** to receive an email notification when a new problem report is submitted
**So that** I can triage and respond to user feedback promptly

**Acceptance Criteria**:
- [ ] **AC-US4-01**: An email is sent to the configured admin address on each new report submission
- [ ] **AC-US4-02**: The email includes: report title, type, skill name (if any), reporter username, and a link to the admin dashboard
- [ ] **AC-US4-03**: Email sending is best-effort and does not block the submission response

## Functional Requirements

### FR-001: ProblemReport Prisma Model
New Prisma model with: id (cuid), userId (required, FK to User), skillId (optional, FK to Skill), type enum (BUG, FEATURE_REQUEST, CONTENT_ISSUE, OTHER), title (string), description (string), status enum (OPEN, IN_REVIEW, RESOLVED, CLOSED), timestamps.

### FR-002: API Routes
- `POST /api/v1/problem-reports` -- Create report (requires user auth)
- `GET /api/v1/problem-reports/mine` -- List current user's reports (requires user auth)

### FR-003: Rate Limiting
Reports are rate-limited to 10 per hour per user via existing rate-limit infrastructure.

## Success Criteria

- Registered users can submit problem reports from both skill pages and standalone page
- Users can track their report status via My Reports
- Admin receives email notification for each new report

## Out of Scope

- Admin dashboard UI for managing problem reports (future increment)
- Report commenting/threading
- File/screenshot attachments
- Public report visibility (reports are private to submitter + admin)

## Dependencies

- Existing GitHub OAuth authentication (User model, requireUser middleware)
- Existing Skill model for optional skill linking
- Existing rate-limit infrastructure (RATE_LIMIT_KV)
- SendGrid for email delivery (SENDGRID_API_KEY, SENDGRID_FROM_EMAIL, ADMIN_REPORT_EMAIL configured in .env and Cloudflare secrets)
