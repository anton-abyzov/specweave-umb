---
increment: 0285-queue-pipeline-recovery-perf
title: "Queue Pipeline Recovery + Q Page Performance Overhaul"
type: hotfix
priority: P0
status: completed
created: 2026-02-21
structure: user-stories
test_mode: TDD
coverage_target: 80
---

# Feature: Queue Pipeline Recovery + Q Page Performance Overhaul

## Overview

The Cloudflare submission verification pipeline is stuck due to a TypeScript build error blocking deploys, and the public `/queue` page has severe performance issues fetching all 500 submissions on every load and SSE event. This increment fixes the pipeline blockers and overhauls the Q page to use server-side pagination with incremental SSE updates.

## User Stories

### US-001: Fix Pipeline Build Blockers (P0)
**Project**: vskill-platform

**As a** platform operator
**I want** the build to succeed and deploy cleanly
**So that** the submission verification pipeline processes new skills again

**Acceptance Criteria**:
- [x] **AC-US1-01**: All `useRef<ReturnType<typeof setTimeout>>(undefined)` calls replaced with `useRef<ReturnType<typeof setTimeout> | null>(null)` across codebase (3 files: queue/page.tsx, AnimatedTerminal.tsx, ThemeToggle.tsx)
- [x] **AC-US1-02**: `next build` succeeds without TypeScript errors
- [x] **AC-US1-03**: Production deploy via push-deploy.sh completes

---

### US-002: Queue Pause TTL Safety Net (P0)
**Project**: vskill-platform

**As a** platform operator
**I want** the queue pause flag to auto-expire after 1 hour
**So that** the queue never stays accidentally paused forever, blocking all submissions

**Acceptance Criteria**:
- [x] **AC-US2-01**: POST /api/v1/admin/queue/pause accepts optional `ttlSeconds` body parameter (default: 3600)
- [x] **AC-US2-02**: KV `put` call uses `expirationTtl` so the flag auto-expires
- [x] **AC-US2-03**: Consumer behavior unchanged (still checks `queue:paused` key existence)

---

### US-003: Server-Side Paginated Queue Page (P1)
**Project**: vskill-platform

**As a** user viewing the submission queue
**I want** the page to load only 50 submissions at a time with server-side pagination
**So that** the page loads fast regardless of total submission count

**Acceptance Criteria**:
- [x] **AC-US3-01**: GET /api/v1/submissions supports `state` filter, `sort`, `sortDir`, `limit`, `offset` query params with proper server-side application
- [x] **AC-US3-02**: Queue page fetches only current page from API (default 50 per page) instead of all 500
- [x] **AC-US3-03**: Filter by state (all/active/published/rejected) triggers server-side re-fetch with state param
- [x] **AC-US3-04**: Sort column changes trigger server-side re-fetch with sort/sortDir params
- [x] **AC-US3-05**: Stat card counts (total, active, published, rejected, avg score) fetched from a lightweight `/api/v1/submissions/stats` endpoint instead of derived from all rows

---

### US-004: SSE In-Place Updates (P1)
**Project**: vskill-platform

**As a** user watching the queue
**I want** SSE events to update individual rows in-place without refetching the entire page
**So that** the UI stays responsive and network usage is minimal

**Acceptance Criteria**:
- [x] **AC-US4-01**: SSE `state_changed` event updates the matching submission row in React state without calling fetchQueue
- [x] **AC-US4-02**: SSE `submission_created` event prepends new submission to current page if it matches the active filter
- [x] **AC-US4-03**: SSE `scan_complete` event updates score for the matching row in-place
- [x] **AC-US4-04**: Stat card counters update optimistically from SSE events (increment/decrement based on state transition)
- [x] **AC-US4-05**: Polling fallback interval increased from 5s to 30s when SSE is disconnected

---

### US-005: Submissions Stats Endpoint (P1)
**Project**: vskill-platform

**As a** frontend developer
**I want** a dedicated endpoint that returns aggregate counts by state
**So that** stat cards can be populated without fetching all submission rows

**Acceptance Criteria**:
- [x] **AC-US5-01**: GET /api/v1/submissions/stats returns `{ total, active, published, rejected, avgScore }` computed from KV index
- [x] **AC-US5-02**: Response time under 100ms (single KV read + in-memory aggregation)

## Functional Requirements

### FR-001: useRef Type Fix
Replace `useRef<ReturnType<typeof setTimeout>>(undefined)` with `useRef<ReturnType<typeof setTimeout> | null>(null)` in all 3 files. This is a TypeScript strict mode issue where `undefined` is not assignable to the `setTimeout` return type.

### FR-002: Queue Pause TTL
Modify POST /api/v1/admin/queue/pause to pass `expirationTtl` to `kv.put()`. Default 3600s (1 hour). Accept optional `ttlSeconds` in request body (max 86400s / 24 hours).

### FR-003: Server-Side Pagination on GET /api/v1/submissions
The existing endpoint already supports `limit` and `offset` but always reads the full KV index then slices. The KV index is capped at 500 entries. Add `state`, `sort`, `sortDir` params applied before slicing.

### FR-004: Submissions Stats Endpoint
New GET /api/v1/submissions/stats that reads the KV submissions:index once, counts by state category, computes average score, and returns aggregate-only response.

### FR-005: SSE In-Place Update Handler
Modify the `onEvent` callback in queue/page.tsx to mutate `submissions` state directly instead of calling `fetchQueue()`. The SSE event already carries `submissionId`, `state`, `score`.

## Success Criteria

- Build succeeds on first attempt after fixes
- Queue page initial load time < 500ms (vs current multi-second with 500 rows)
- Network payload per page load < 10KB (vs current ~200KB for 500 rows)
- SSE events trigger 0 additional API calls (currently triggers full refetch each time)
- Queue processes new submissions within 60 seconds of receiving them

## Out of Scope

- Database migration for Prisma indexes (already have state, createdAt, skillName indexes)
- Rewriting the KV-based submission storage to pure Postgres
- Queue consumer logic changes (except pause TTL)
- Scanner worker health monitoring endpoint (deferred)
- Admin submissions page refactor

## Dependencies

- Cloudflare Workers KV (existing)
- Cloudflare Queues (existing)
- push-deploy.sh (existing deploy script)
