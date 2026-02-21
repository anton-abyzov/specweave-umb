---
increment: 0301-dashboard-increments-perf
title: "Dashboard Increments List Performance Optimization"
type: feature
priority: P1
status: planned
created: 2026-02-21
structure: user-stories
test_mode: test-after
coverage_target: 80
---

# Feature: Dashboard Increments List Performance Optimization

## Overview

The `/api/increments` endpoint is extremely slow for projects with 300+ increments. In the fallback path (no `dashboard.json` cache), `scanIncrementsFromFilesystem()` performs ~7 synchronous I/O calls per increment (existsSync x3, readFileSync x3, statSync x1), blocking the event loop and causing unacceptable load times. Additionally, there is no in-memory TTL cache for increments (unlike analytics which has a 30s cache), no server-side pagination, redundant scans between `getIncrements()` and `getOverview()`, and SSE `increment-update` events trigger a full re-fetch from the frontend.

## User Stories

### US-001: Fast Increments Loading with Server-Side Caching (P1)
**Project**: specweave

**As a** dashboard user
**I want** the increments list to load quickly even with 300+ increments
**So that** I can view and filter my project status without long wait times

**Acceptance Criteria**:
- [ ] **AC-US1-01**: In-memory TTL cache for increment data with configurable TTL (default 30s), matching the analytics cache pattern
- [ ] **AC-US1-02**: Synchronous filesystem reads (`readFileSync`, `readdirSync`, `existsSync`, `statSync`) in `scanIncrementsFromFilesystem()` converted to async equivalents (`readFile`, `readdir`, `stat`, `access`)
- [ ] **AC-US1-03**: `getOverview()` reuses cached increment scan results from `getIncrements()` instead of performing a duplicate filesystem scan
- [ ] **AC-US1-04**: Response time for `/api/increments` with 300 increments under 200ms on cache hit, under 2000ms on cold scan

---

### US-002: Server-Side Pagination for Increments API (P1)
**Project**: specweave

**As a** dashboard user
**I want** the increments list to support pagination and filtering on the server
**So that** only the data I need is transferred and rendered, improving responsiveness

**Acceptance Criteria**:
- [ ] **AC-US2-01**: `/api/increments` accepts `limit` (default 50, max 500), `offset` (default 0) query parameters
- [ ] **AC-US2-02**: `/api/increments` accepts `status` and `type` filter query parameters for server-side filtering
- [ ] **AC-US2-03**: Response includes pagination metadata: `{ total, limit, offset, hasMore }`
- [ ] **AC-US2-04**: Frontend `IncrementsPage` uses server-side pagination with "load more" or page navigation instead of loading all increments at once
- [ ] **AC-US2-05**: Summary counts remain unaffected by pagination (always reflect the full dataset)

---

### US-003: Smart SSE Refetch Behavior (P2)
**Project**: specweave

**As a** dashboard user
**I want** SSE-triggered updates to be efficient and not cause full data reloads
**So that** the dashboard remains responsive during active development

**Acceptance Criteria**:
- [ ] **AC-US3-01**: SSE `increment-update` events are debounced on the frontend (500ms window) to prevent rapid-fire refetches
- [ ] **AC-US3-02**: SSE events carry enough context (increment ID, change type) for the frontend to decide whether a refetch is needed
- [ ] **AC-US3-03**: Cache invalidation on the server is triggered by SSE file watcher events, ensuring fresh data on next request

---

### US-004: Performance Test Coverage (P2)
**Project**: specweave

**As a** developer
**I want** performance tests that validate the optimization improvements
**So that** regressions are caught early and performance characteristics are documented

**Acceptance Criteria**:
- [ ] **AC-US4-01**: Unit tests for the TTL cache mechanism (hit, miss, expiry, invalidation)
- [ ] **AC-US4-02**: Unit tests for async filesystem scan producing identical results to the original sync scan
- [ ] **AC-US4-03**: Unit tests for pagination logic (limit, offset, filtering, summary preservation)
- [ ] **AC-US4-04**: Integration test demonstrating cache sharing between `getIncrements()` and `getOverview()`

## Functional Requirements

### FR-001: TTL Cache for Increments
Add an in-memory cache for increment data in `DashboardDataAggregator`, following the same pattern as the existing `analyticsCache` (private field, timestamp, TTL). Cache invalidation occurs when the file watcher detects increment directory changes.

### FR-002: Async Filesystem I/O
Replace all synchronous `fs.*Sync` calls in `scanIncrementsFromFilesystem()`, `countTasksFromFile()`, `countAcsFromFile()`, and `readJsonFile()` with their async `fs.promises.*` equivalents. The method signatures become `async` to propagate properly.

### FR-003: Server-Side Pagination
The `/api/increments` endpoint parses `limit`, `offset`, `status`, and `type` query parameters. The full dataset is cached in memory; pagination and filtering are applied on the cached array. The response payload is extended with pagination metadata.

### FR-004: Shared Scan Results
`getOverview()` calls `getIncrements()` internally (or shares the same cache) instead of independently calling `scanIncrementsFromFilesystem()`.

### FR-005: Frontend Debounced SSE
The `IncrementsPage` component debounces SSE-triggered refetches with a 500ms window. Multiple rapid SSE events within the window are collapsed into a single refetch.

## Success Criteria

- `/api/increments` cache hit response time < 200ms for 300+ increments
- `/api/increments` cold scan response time < 2000ms for 300+ increments
- No duplicate filesystem scans per request cycle
- Frontend only fetches one page of data at a time
- All existing tests continue to pass
- New unit tests achieve >80% coverage of changed code

## Out of Scope

- Changing the `dashboard.json` cache format
- Frontend visual redesign beyond pagination controls
- Changing the increment file structure
- Database-backed caching or persistence layer

## Dependencies

- Existing `DashboardDataAggregator` class
- Existing `FileWatcher` and `SSEManager` infrastructure
- Existing `useProjectApi` and `useSSEEvent` hooks
