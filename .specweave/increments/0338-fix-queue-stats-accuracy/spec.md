# 0338 — Fix Queue Stats Accuracy + Page Performance

## Problem
Queue page shows 399 "Active" submissions but only ~5 are genuinely active. The `submissions:index` KV blob is stale due to read-modify-write races under concurrent Workers. Page also makes duplicate auth calls and polls unnecessarily when SSE is connected.

## User Stories

### US-001: Accurate queue stats
As an admin viewing the queue page, I want the stats counters (Active, Published, Rejected) to reflect actual DB state so I can trust the numbers.

**Acceptance Criteria:**
- [x] AC-US1-01: Stats endpoint uses Prisma DB as source of truth instead of stale KV index
- [x] AC-US1-02: Stats are cached in KV with 30s TTL to avoid Neon cold starts on every poll
- [x] AC-US1-03: List endpoint total count comes from DB, not stale KV array length

### US-002: Faster page load
As a user visiting the queue page, I want fewer unnecessary network requests on load.

**Acceptance Criteria:**
- [x] AC-US2-01: Only one /api/v1/auth/me call fires on page load (not two)
- [x] AC-US2-02: Polling only active when SSE is disconnected
- [x] AC-US2-03: Search debounce increased to 500ms for DB-backed queries
