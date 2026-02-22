---
increment: 0280-queue-search-observability-admin
title: "Queue Search, Observability & Admin Monitoring"
type: feature
priority: P1
status: in-progress
created: 2026-02-21
structure: user-stories
test_mode: test-after
coverage_target: 80
---

# Feature: Queue Search, Observability & Admin Monitoring

## Overview

Add search/filter capabilities to the admin submission queue API, replace hard-coded mock stats on the dashboard with live database counts by status, and add a dedicated admin submissions list page with search, filter, and pagination.

## User Stories

### US-001: Admin Submission Search & Filter API (P1)
**Project**: vskill-platform

**As an** admin reviewer
**I want** to search and filter submissions by skill name, state, and date range
**So that** I can quickly find specific submissions without scrolling through the full list

**Acceptance Criteria**:
- [x] **AC-US1-01**: GET /api/v1/admin/submissions accepts `search`, `state`, and `sort` query params
- [x] **AC-US1-02**: The search param filters submissions by skillName (case-insensitive contains)
- [x] **AC-US1-03**: The state param filters by SubmissionState enum value
- [x] **AC-US1-04**: Results are paginated with page/limit params and return totalCount
- [x] **AC-US1-05**: The endpoint returns real database results instead of mock data

---

### US-002: Live Dashboard Stats (P1)
**Project**: vskill-platform

**As an** admin reviewer
**I want** the dashboard to show live counts by submission state
**So that** I have real-time visibility into the pipeline health

**Acceptance Criteria**:
- [x] **AC-US2-01**: Dashboard fetches stats from /api/v1/admin/stats on load
- [x] **AC-US2-02**: Stats cards show totalSkills, pendingCount, approvalRate, and totalSubmissions from the API
- [x] **AC-US2-03**: State distribution breakdown is displayed showing count per SubmissionState

---

### US-003: Admin Submissions List Page (P1)
**Project**: vskill-platform

**As an** admin reviewer
**I want** a dedicated submissions list page with search, state filter, and pagination
**So that** I can browse and manage all submissions efficiently

**Acceptance Criteria**:
- [x] **AC-US3-01**: /admin/submissions page renders a searchable, filterable table
- [x] **AC-US3-02**: Search input filters by skill name in real-time (debounced)
- [x] **AC-US3-03**: State dropdown filters submissions by pipeline state
- [x] **AC-US3-04**: Pagination controls allow navigating through results
- [x] **AC-US3-05**: Clicking a submission row navigates to the detail page

## Functional Requirements

### FR-001: Admin Submissions API Enhancement
The GET /api/v1/admin/submissions endpoint must query Prisma with optional where clauses for `skillName` (contains, case-insensitive) and `state` (exact match). Must support `page`, `limit`, `search`, `state`, and `sort` query params. Returns `{ submissions, totalCount, page, limit }`.

### FR-002: Live Dashboard Stats
Replace hard-coded STATS array in admin dashboard with data from /api/v1/admin/stats. Display total skills, pending submissions, approval rate, and total submissions with real values.

### FR-003: Admin Submissions List Page
Create /admin/submissions/page.tsx with search input, state filter dropdown, paginated table, and navigation to detail pages.

## Success Criteria

- Admin can search submissions by skill name
- Admin can filter by state
- Dashboard shows live stats from the database
- All tests pass with >80% coverage on new code

## Out of Scope

- Full-text search across all fields
- Export/download functionality
- Real-time WebSocket updates

## Dependencies

- Existing Prisma schema (Submission model)
- Existing auth module (requireRole)
- Existing admin layout
