---
increment: 0307-queue-search-observability
title: "Queue Search, Observability & Monitoring for Admin"
type: feature
priority: P1
status: completed
created: 2026-02-21
structure: user-stories
test_mode: test-after
coverage_target: 80
---

# Feature: Queue Search, Observability & Monitoring for Admin

## Overview

Enhance the admin queue page (`/admin/queue`) with search, state filtering, per-state distribution counts, and real-time updates so admins can quickly find any submission (e.g. "remotion-best-practices") and understand the full pipeline state at a glance. Also optimize the dashboard's N+1 state count queries.

## Problem Statement

The admin queue page currently shows metrics, stuck submissions, and DLQ — but has **no search or filtering**. Search only exists on `/admin/submissions`, which is a separate page. When admins submit skills and need to track them through the pipeline, there's no easy way to find a specific submission or see per-state counts on the operational queue page.

## User Stories

### US-001: Queue Search & Filtering (P1)
**Project**: vskill-platform

**As an** admin/reviewer
**I want** to search and filter submissions on the queue page
**So that** I can quickly find any submission by skill name and understand its current state

**Acceptance Criteria**:
- [x] **AC-US1-01**: Queue page has a search input that filters submissions by skill name (case-insensitive, debounced 300ms)
- [x] **AC-US1-02**: Queue page has a state filter dropdown with all SubmissionState values plus "All" option
- [x] **AC-US1-03**: Search results show submission table with: skill name, repo URL, state badge, submitted date, and link to detail page
- [x] **AC-US1-04**: Results are paginated (20 items/page) with server-side pagination via existing `/api/v1/admin/submissions` endpoint
- [x] **AC-US1-05**: Searching "remotion-best-practices" returns matching submissions when they exist
- [x] **AC-US1-06**: Empty state shows "No submissions found" with a clear filters button

---

### US-002: Per-State Distribution Overview (P1)
**Project**: vskill-platform

**As an** admin/reviewer
**I want** to see per-state submission counts at a glance on the queue page
**So that** I can understand what's happening in the pipeline without counting manually

**Acceptance Criteria**:
- [x] **AC-US2-01**: Queue page header shows count cards for each SubmissionState (RECEIVED, TIER1_SCANNING, TIER1_FAILED, TIER2_SCANNING, AUTO_APPROVED, PUBLISHED, REJECTED, VENDOR_APPROVED, DEQUEUED, RESCAN_REQUIRED)
- [x] **AC-US2-02**: Counts are fetched via a single `groupBy` API endpoint (not N+1 queries)
- [x] **AC-US2-03**: Clicking a state card filters the submission list to that state
- [x] **AC-US2-04**: Total submission count is displayed prominently

---

### US-003: Real-Time Queue Updates (P2)
**Project**: vskill-platform

**As an** admin/reviewer
**I want** state counts to update in real-time without manual page refresh
**So that** I can monitor the pipeline live as submissions flow through

**Acceptance Criteria**:
- [x] **AC-US3-01**: SSE stream (existing `/api/v1/submissions/stream`) is wired into queue page
- [x] **AC-US3-02**: State distribution counts auto-refresh when `state_changed` or `submission_created` events arrive
- [x] **AC-US3-03**: Connection status indicator shows whether the live feed is connected

---

### US-004: Dashboard State Count Optimization (P1)
**Project**: vskill-platform

**As an** admin/reviewer
**I want** the dashboard to load state distribution efficiently
**So that** the page loads faster and doesn't make N+1 API calls

**Acceptance Criteria**:
- [x] **AC-US4-01**: Dashboard uses the new `state-counts` API instead of individual per-state queries
- [x] **AC-US4-02**: State distribution section loads in a single network request

## Functional Requirements

### FR-001: State Counts API
New `GET /api/v1/admin/submissions/state-counts` endpoint returning `groupBy` state counts in a single Prisma query. Returns `{ counts: Record<SubmissionState, number>, total: number }`.

### FR-002: Queue Page Enhancement
Add search bar, state filter, submission results table, and state distribution cards to the existing queue page above the current metrics section.

### FR-003: SSE Integration
Wire existing `useSubmissionStream`-style hook into queue page for live count updates.

## Success Criteria

- Admin can find "remotion-best-practices" by typing the name in the queue search
- Per-state counts visible at a glance (no manual counting)
- Dashboard state distribution loads in 1 request (was N+1)
- Queue page search responds in <500ms

## Out of Scope

- No new database tables or schema migrations
- No changes to submission detail page (lifecycle timeline already works)
- No new auth patterns (reuses existing REVIEWER role)
- No changes to SSE endpoint (already broadcasts needed events)
- No changes to queue processing logic

## Dependencies

- Existing Prisma indexes on `state`, `skillName`, `repoUrl+skillName`, `createdAt`
- Existing SSE stream at `/api/v1/submissions/stream`
- Existing `/api/v1/admin/submissions` endpoint with search/filter support
