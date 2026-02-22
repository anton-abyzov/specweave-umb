# 0273 - Queue Page Admin Dashboard Redesign

## Overview

Redesign the `/queue` page (`src/app/queue/page.tsx`) from its current card-based grouped layout into a world-class admin dashboard with an information-dense table view. The current page groups submissions into "Processing", "Published", and "Rejected" sections using card components with pipeline dots. The redesign replaces this with a single sortable/filterable data table, clickable stat cards that act as state filters, Prisma-backed full-text search, direct GitHub links, a queue operational status bar, cursor-based pagination, and keyboard shortcuts.

**Key constraint**: This page is a `"use client"` component. The existing SSE real-time update mechanism (`useSubmissionStream`) and admin actions (`AdminQueueActions`) must be preserved. The `/admin/queue` page (a separate admin-only monitoring dashboard) is NOT part of this redesign.

---

## User Stories

### US-001: Table-Based Submission View
**Project**: vskill-platform

**As an** admin user
**I want** to see all submissions in a dense, sortable data table
**So that** I can scan and triage submissions efficiently without scrolling through grouped cards

**Acceptance Criteria**:
- [x] **AC-US1-01**: Replace the card-based `SubmissionGroup` + `SubmissionCard` layout with a single `<table>` element
- [x] **AC-US1-02**: Table columns: Skill Name, Repo (short org/name), State (badge), Score, Submitted (relative time), Updated (relative time), Actions
- [x] **AC-US1-03**: Table rows are clickable and navigate to `/submit/{id}` (preserving existing link behavior)
- [x] **AC-US1-04**: Table supports column sorting by clicking column headers (Skill Name asc/desc, State, Score, Submitted, Updated)
- [x] **AC-US1-05**: The currently active sort column shows a directional indicator (arrow up/down)
- [x] **AC-US1-06**: Default sort order is "Submitted" descending (newest first)
- [x] **AC-US1-07**: SSE flash highlighting still works on individual table rows (background color pulse on real-time update)
- [x] **AC-US1-08**: Admin actions (Dequeue, Bump to Front, Move to Back) render inline in the Actions column for active submissions

### US-002: Clickable Stat Card Filters
**Project**: vskill-platform

**As an** admin user
**I want** to click on stat cards (Total, Active, Published, Rejected) to filter the table
**So that** I can quickly focus on a specific category of submissions

**Acceptance Criteria**:
- [x] **AC-US2-01**: The existing 4 stat cards (Total, Active, Published, Rejected) become clickable
- [x] **AC-US2-02**: Clicking a stat card filters the table to show only submissions matching that category
- [x] **AC-US2-03**: Clicking "Total" clears the filter and shows all submissions
- [x] **AC-US2-04**: The active filter card has a visually distinct selected state (e.g., stronger border, background tint)
- [x] **AC-US2-05**: Filter state is reflected in the URL as a query parameter (`?filter=active`, `?filter=published`, `?filter=rejected`)
- [x] **AC-US2-06**: An "Avg Score" stat card is added showing the average score of scored submissions

### US-003: Prisma-Backed Full-Text Search
**Project**: vskill-platform

**As an** admin user
**I want** to search submissions by skill name, repo URL, or submission ID
**So that** I can quickly locate specific submissions without manual scanning

**Acceptance Criteria**:
- [x] **AC-US3-01**: A search input field is displayed above the table (monospace font, placeholder: "Search by skill name, repo, or ID...")
- [x] **AC-US3-02**: Search is debounced (300ms) and triggers a server-side API call
- [x] **AC-US3-03**: New API endpoint `GET /api/v1/submissions/search?q=<term>&limit=50` queries Prisma with `contains` (case-insensitive) across `skillName`, `repoUrl`, and `id` fields
- [x] **AC-US3-04**: Search results replace the table contents; clearing the search restores the default view
- [x] **AC-US3-05**: Search works in combination with stat card filters (filter + search are AND-ed)
- [x] **AC-US3-06**: Search query is reflected in the URL as `?q=<term>` for shareability

### US-004: GitHub Links
**Project**: vskill-platform

**As an** admin user
**I want** the repo column to have a direct clickable link to the GitHub repository
**So that** I can quickly jump to the source code for review

**Acceptance Criteria**:
- [x] **AC-US4-01**: The Repo column displays shortened `org/repo` text as a clickable link
- [x] **AC-US4-02**: Link opens the GitHub repository in a new tab (`target="_blank"`, `rel="noopener noreferrer"`)
- [x] **AC-US4-03**: Clicking the GitHub link does NOT trigger row navigation (event propagation stopped)
- [x] **AC-US4-04**: Link has subtle hover styling (underline on hover) distinct from row hover

### US-005: Queue Operational Status Bar
**Project**: vskill-platform

**As an** admin user
**I want** to see a status bar showing queue health, SSE connection status, and processing state
**So that** I can quickly assess whether the queue system is operating normally

**Acceptance Criteria**:
- [x] **AC-US5-01**: A status bar is displayed between the stat cards and the table
- [x] **AC-US5-02**: Status bar shows: SSE connection state (live/polling dot), queue health indicator (healthy/degraded/unhealthy), and pause state
- [x] **AC-US5-03**: Queue health is fetched from `GET /api/v1/admin/queue/status` (existing endpoint, requires admin auth)
- [x] **AC-US5-04**: If queue is paused, a yellow "PAUSED" badge is shown
- [x] **AC-US5-05**: Status bar displays "Last updated: HH:MM:SS" showing the most recent data refresh time
- [x] **AC-US5-06**: For non-admin users, the status bar shows only SSE connection state (no queue health — requires admin privileges)

### US-006: Cursor-Based Pagination
**Project**: vskill-platform

**As an** admin user
**I want** the table to paginate results instead of loading everything at once
**So that** the page performs well even with hundreds of submissions

**Acceptance Criteria**:
- [x] **AC-US6-01**: Table shows 50 submissions per page by default
- [x] **AC-US6-02**: "Previous" and "Next" buttons are displayed below the table
- [x] **AC-US6-03**: Pagination shows current range ("Showing 1-50 of 234")
- [x] **AC-US6-04**: The existing `GET /api/v1/submissions` endpoint is extended to support `offset` and `limit` query params
- [x] **AC-US6-05**: Pagination state is reflected in the URL (`?page=2`)
- [x] **AC-US6-06**: Page size selector (25, 50, 100) is available next to pagination controls

### US-007: Keyboard Shortcuts
**Project**: vskill-platform

**As an** admin user
**I want** keyboard shortcuts for common actions
**So that** I can navigate and manage the queue without using the mouse

**Acceptance Criteria**:
- [x] **AC-US7-01**: `/` focuses the search input (like GitHub)
- [x] **AC-US7-02**: `j`/`k` moves the visual row highlight down/up through table rows
- [x] **AC-US7-03**: `Enter` on a highlighted row navigates to `/submit/{id}`
- [x] **AC-US7-04**: `Escape` clears search and deselects row highlight
- [x] **AC-US7-05**: `?` opens a keyboard shortcut help overlay
- [x] **AC-US7-06**: Keyboard shortcuts are disabled when a text input is focused (except Escape)
- [x] **AC-US7-07**: A small "? Shortcuts" hint is shown in the bottom-right corner of the page

---

## Non-Functional Requirements

- **NFR-01**: Page initial load time must not regress (current: ~200ms to first meaningful paint)
- **NFR-02**: Table must remain responsive with 500+ rows (virtual scrolling NOT required for v1 since pagination caps at 100/page)
- **NFR-03**: All existing tests in `src/app/queue/__tests__/` must pass or be updated
- **NFR-04**: New code must have >80% test coverage
- **NFR-05**: No new npm dependencies; use only existing project dependencies
- **NFR-06**: Must work in both light and dark themes using existing CSS custom properties
- **NFR-07**: Mobile responsiveness: table scrolls horizontally on small screens with sticky first column

---

## Out of Scope

- `/admin/queue` page (separate admin monitoring dashboard — unchanged)
- Drag-and-drop reordering of submissions
- Bulk selection / multi-select actions
- Real-time WebSocket replacement for SSE
- Submission creation/batch submit UI (keep existing "Submit Skills" panel as-is)
