---
increment: 0790-queue-health-orphaned-active
title: Fix queue-health oldestActive reporting state-desync orphans
type: bug
priority: P1
status: completed
---

# 0790: Fix queue-health oldestActive reporting state-desync orphans

## Problem

`GET /api/v1/queue/health` reports a submission as `oldestActive` (`state: "TIER1_SCANNING"`, `ageMs: 89337954` — ~25 hours) even when the submission has actually reached `PUBLISHED` long ago. Concrete example observed 2026-04-27:

```
$ curl https://verified-skill.com/api/v1/queue/health
"oldestActive":{"id":"sub_1a2ab80c-...","state":"TIER1_SCANNING","ageMs":89337954}

$ curl https://verified-skill.com/api/v1/submissions/sub_1a2ab80c-...
state: "PUBLISHED", updatedAt: "2026-04-26T05:52:35.122Z"
```

### Root cause

The DB `Submission.state` column and the KV "fresh state" cache can desync. The submissions GET handler reads DB state but **overrides it with KV state** via `getSubmissionsFresh()`. The corrected state is supposed to be flushed back to the DB via `flushDbUpdates()` — but that runs as fire-and-forget (`.catch()`'d, no retry, no dead-letter) at the end of the GET handler. When the worker that should write the terminal state crashes mid-flight, the DB row stays in an active state forever.

`/api/v1/queue/health` queries the DB directly with `WHERE state IN (RECEIVED, TIER1_SCANNING, TIER2_SCANNING) ORDER BY createdAt ASC` — so it picks up these orphaned rows as the "oldest active." The result: false-positive "stuck submission" alerts that drown out legitimate stalls.

## Goal

Stop reporting state-desync orphans as `oldestActive` while still surfacing them as a separate, distinct signal that monitoring can alert on independently. Don't fix the underlying desync (out of scope — that requires a worker-side fix), just stop the false positives.

## User Stories

### US-001: Filter oldestActive to recently-touched rows
**Project**: vskill-platform

**As an** on-call engineer watching queue-health alerts
**I want** `oldestActive` to only report submissions that have been touched in the last 6 hours
**So that** I see real queue stalls, not 25-hour-old state-desync orphans

**Acceptance Criteria**:
- [x] **AC-US1-01**: `oldestActive` query adds `updatedAt >= NOW() - INTERVAL '6 hours'` (parameterized via Prisma `gte`) — only "fresh" active rows count
- [x] **AC-US1-02**: When all active rows are stale (>6h since `updatedAt`), `oldestActive` is `null` — no false positive
- [x] **AC-US1-03**: The 6-hour window is encoded as a named constant `OLDEST_ACTIVE_FRESHNESS_MS = 6 * 60 * 60 * 1000` so future tuning is one-line

### US-002: Surface orphaned-active count separately
**Project**: vskill-platform

**As a** platform operator
**I want** a new field `orphanedActive: { count, oldestId, oldestUpdatedAt }` in the response
**So that** I can detect state desync without losing the signal entirely

**Acceptance Criteria**:
- [x] **AC-US2-01**: Response shape gains `orphanedActive: { count: number, oldestId: string | null, oldestUpdatedAt: string | null }`
- [x] **AC-US2-02**: `orphanedActive.count` is the count of `state IN (RECEIVED, TIER1_SCANNING, TIER2_SCANNING) AND updatedAt < NOW() - 6h`
- [x] **AC-US2-03**: The new query is bounded by `withDbTimeout(..., 4_000)` — same budget as the existing `oldestActive` query, so health stays fast even when orphans pile up
- [x] **AC-US2-04**: When `orphanedActive.count === 0`, `oldestId` and `oldestUpdatedAt` are null

### US-003: Cache invalidation on shape change
**Project**: vskill-platform

**As a** platform operator
**I want** existing cached responses to not break the new fields
**So that** clients consuming the new response shape don't see partial data after deploy

**Acceptance Criteria**:
- [x] **AC-US3-01**: When the cached response is missing `orphanedActive` (pre-deploy cache), the cached response is treated as stale and recomputed
- [x] **AC-US3-02**: Existing `cached: true` flag continues to work after this change

### US-004: Regression coverage
**Project**: vskill-platform

**As a** platform maintainer
**I want** unit tests asserting the new freshness filter and orphan count
**So that** silent regressions are caught

**Acceptance Criteria**:
- [x] **AC-US4-01**: New vitest TC mocks Prisma to return a stale-state row and asserts `oldestActive` is null when only orphans exist
- [x] **AC-US4-02**: New vitest TC asserts `orphanedActive.count` reflects the count of stale rows
- [x] **AC-US4-03**: All existing TCs in `src/app/api/v1/queue/health/__tests__/route.test.ts` still pass

### US-005: Partial-failure resilience
**Project**: vskill-platform

**As an** on-call engineer relying on `/queue/health`
**I want** a single failing DB query to not nuke the other two signals, and partial-failure responses to not be cached
**So that** when the orphan pile grows large enough to slow its own detection query, I still see the legitimate `oldestActive` signal — and a 30s "all clear" cache isn't pinned during a DB outage

**Acceptance Criteria**:
- [x] **AC-US5-01**: The three active-rows queries run via `Promise.allSettled` so one rejection doesn't propagate to the other results
- [x] **AC-US5-02**: Each rejected query logs a per-query `console.warn` with a distinct prefix (`oldestActive`, `orphan count`, `orphan sample`) for diagnosability
- [x] **AC-US5-03**: When ANY of the three queries reject, the response is returned to the caller but NOT written to KV (no falsified "all clear" pinned for 30s)
- [x] **AC-US5-04**: New vitest TC asserts that `orphan count rejects + oldestActive resolves` returns the legitimate `oldestActive` and skips the cache write

## Out of Scope

- Fixing the underlying state-desync (requires worker-side reconciliation)
- Dead-letter queue for failed `flushDbUpdates`
- Changing the cache TTL (stays at 30s)

## Non-Functional Requirements

- **Performance**: New query runs within the existing `withDbTimeout(4_000)` budget
- **Backwards compatibility**: Response shape gains a field but doesn't remove or rename existing ones
- **No cron required**: This is a read-time signal only — no new background work
