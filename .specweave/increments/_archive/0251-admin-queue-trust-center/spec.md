---
increment: 0251-admin-queue-trust-center
title: "Admin Queue Actions & Trust Center Consolidation"
type: feature
priority: P1
status: in-progress
created: 2026-02-20
structure: user-stories
test_mode: TDD
coverage_target: 80
---

# Feature: Admin Queue Actions & Trust Center Consolidation

## Overview

Consolidate the fragmented security-related pages (Audits, Blocklist) into a unified "Trust Center" page with tab navigation. Add admin-only actions (dequeue, reprioritize) to the public Queue page. Hide admin navigation links from non-admin users. The goal is to reduce page sprawl, improve discoverability, and create a cleaner separation between public and admin concerns.

## User Stories

### US-001: Admin Queue Actions (P1)
**Project**: vskill-platform

**As a** platform admin
**I want** to dequeue and reprioritize submissions directly from the queue page
**So that** I can manage the verification pipeline without switching to the admin panel

**Acceptance Criteria**:
- [x] **AC-US1-01**: Admin users see action buttons (Dequeue, Reprioritize) on each submission card in the public queue page
- [x] **AC-US1-02**: Non-admin users see no admin action buttons on the queue page
- [x] **AC-US1-03**: Clicking "Dequeue" removes the submission from the active queue with a confirmation dialog
- [x] **AC-US1-04**: Clicking "Reprioritize" allows admin to move a submission up/down in the queue (bump to front / move to back)
- [x] **AC-US1-05**: Admin actions require valid authentication and admin role verification server-side
- [x] **AC-US1-06**: After any admin action, the queue list refreshes to reflect the change

---

### US-002: Trust Center Page (P1)
**Project**: vskill-platform

**As a** platform visitor
**I want** a unified Trust Center page combining security audits, blocked skills, and report functionality
**So that** I can assess the platform's security posture from a single location

**Acceptance Criteria**:
- [x] **AC-US2-01**: A new `/trust` route exists with tabbed navigation: "Verified Skills" (audits), "Blocked Skills" (blocklist), "Reports"
- [x] **AC-US2-02**: The "Verified Skills" tab shows the current audits table content (moved from `/audits`)
- [x] **AC-US2-03**: The "Blocked Skills" tab shows the current blocklist content (moved from `/blocklist`)
- [x] **AC-US2-04**: The "Reports" tab shows a placeholder for community-submitted security reports
- [x] **AC-US2-05**: Tab state is preserved in the URL via query parameter (e.g., `/trust?tab=blocked`)
- [x] **AC-US2-06**: Old routes `/audits` and `/blocklist` redirect to `/trust` with the appropriate tab selected

---

### US-003: Admin Navigation Visibility (P1)
**Project**: vskill-platform

**As a** platform developer
**I want** admin-only navigation links hidden from non-admin users
**So that** the public interface is clean and non-admin users are not confused by inaccessible pages

**Acceptance Criteria**:
- [x] **AC-US3-01**: The main navbar and footer no longer show "Audits" and "Blocklist" as separate links; they are replaced by a single "Trust Center" link
- [x] **AC-US3-02**: The mobile nav is updated to reflect the same consolidated navigation
- [x] **AC-US3-03**: The admin sidebar navigation remains unchanged (admin panel is a separate area)

---

### US-004: Disconnected Page Experience Fix (P2)
**Project**: vskill-platform

**As a** platform visitor
**I want** consistent page transitions and shared layout patterns
**So that** the platform feels cohesive rather than a collection of disconnected pages

**Acceptance Criteria**:
- [x] **AC-US4-01**: The Trust Center page uses the same SectionDivider and page layout patterns as the Queue page
- [x] **AC-US4-02**: Tab switching within Trust Center is instant (client-side) with no full page reload
- [x] **AC-US4-03**: Active tab is visually highlighted in the tab bar

## Functional Requirements

### FR-001: Admin Role Detection on Queue Page
The queue page must detect if the current user is an admin via the existing `/api/v1/auth/me` endpoint. If the response includes admin privileges, admin action buttons are rendered. The detection must be server-verified on action execution.

### FR-002: Dequeue API Endpoint
A new `POST /api/v1/admin/submissions/:id/dequeue` endpoint that transitions a submission to a "DEQUEUED" state, removing it from active processing. Requires admin JWT.

### FR-003: Reprioritize API Endpoint
A new `POST /api/v1/admin/submissions/:id/reprioritize` endpoint that accepts `{ position: "front" | "back" }` to bump a submission's processing priority. Requires admin JWT.

### FR-004: Trust Center Tabbed Layout
A client-side tabbed component at `/trust` that lazy-loads tab content. Tabs: Verified Skills (default), Blocked Skills, Reports. Uses URL search params for deep linking.

### FR-005: Route Redirects
Next.js middleware or `redirect()` from `/audits` to `/trust?tab=verified` and from `/blocklist` to `/trust?tab=blocked`.

## Success Criteria

- Zero separate top-level security pages (Audits, Blocklist removed as standalone)
- Admin actions visible only to authenticated admins
- All existing audit and blocklist functionality preserved in Trust Center
- No broken links from external sources (redirects handle old URLs)

## Out of Scope

- Admin panel redesign (the `/admin/*` pages stay as-is)
- New report submission form (Reports tab is placeholder only)
- Role-based access control overhaul (we use existing admin auth)
- Queue processing logic changes (only UI actions, not pipeline modifications)

## Dependencies

- Existing admin auth system (`/api/v1/auth/me`, admin JWT tokens)
- Existing audits API (`/api/v1/audits`)
- Existing blocklist API (`/api/v1/blocklist`)
- Existing submissions API (`/api/v1/submissions`)
