---
increment: 0248-cloudflare-queue-processing
title: "Cloudflare Queue Admin Dashboard Completion"
type: feature
priority: P1
status: in-progress
created: 2026-02-20
structure: user-stories
test_mode: test-after
coverage_target: 80
---

# Feature: Cloudflare Queue Admin Dashboard Completion

## Overview

The Cloudflare Queue infrastructure is already built (consumer.ts, DLQ consumer, recovery.ts, wrangler.jsonc with `max_batch_timeout: 30s`). A rich `/api/v1/admin/queue/status` endpoint exists but the admin queue dashboard ignores it entirely. This increment wires up the status data to the admin UI and adds two new capabilities: queue pause/circuit-breaker and bulk requeue for stuck submissions.

## User Stories

### US-001: Queue health and stuck submission visibility (P1)
**Project**: vskill-platform

**As a** platform operator
**I want** to see queue health status and stuck submissions in the admin dashboard
**So that** I can spot and resolve processing backlogs without manually checking KV

**Acceptance Criteria**:
- [x] **AC-US1-01**: Queue page shows a health badge (HEALTHY / DEGRADED / UNHEALTHY) sourced from `/api/v1/admin/queue/status`
- [x] **AC-US1-02**: A "Stuck Submissions" panel lists submissions in non-terminal states >5 min, showing skill name, state, duration stuck, retry count
- [x] **AC-US1-03**: Each stuck submission has a "Requeue" button that re-enqueues it via the queue
- [x] **AC-US1-04**: Panel auto-refreshes every 30s alongside existing metrics
- [x] **AC-US1-05**: `/api/v1/admin/queue/status` response includes full `stuckList` array (capped at 50) with id, skillName, repoUrl, state, stuckForMs

---

### US-002: Queue pause / circuit breaker (P1)
**Project**: vskill-platform

**As a** platform operator
**I want** to pause queue processing during outages or deployments
**So that** I can prevent cascading failures without draining the queue

**Acceptance Criteria**:
- [x] **AC-US2-01**: Admin can toggle "Pause Processing" in the queue dashboard (SUPER_ADMIN only)
- [x] **AC-US2-02**: When paused, queue consumer checks `queue:paused` flag in QUEUE_METRICS_KV and calls `batch.retryAll()` for all messages, then returns
- [x] **AC-US2-03**: Dashboard shows a prominent red "QUEUE PAUSED" banner when paused
- [x] **AC-US2-04**: `POST /api/v1/admin/queue/pause` sets the flag; `DELETE /api/v1/admin/queue/pause` clears it (SUPER_ADMIN auth)
- [x] **AC-US2-05**: Pause state is reflected in `/api/v1/admin/queue/status` response as `paused: boolean`

---

### US-003: Bulk requeue for stuck submissions (P2)
**Project**: vskill-platform

**As a** platform operator
**I want** to requeue all stuck submissions in one click
**So that** I can efficiently recover from a processing outage

**Acceptance Criteria**:
- [x] **AC-US3-01**: "Requeue All Stuck" button in the Stuck Submissions panel bulk-requeues all stuck items
- [x] **AC-US3-02**: `POST /api/v1/admin/queue/bulk-requeue` re-enqueues all stuck submissions (reusing existing recovery logic)
- [x] **AC-US3-03**: Returns `{ requeued: N, failed: N, total: N }` and the UI shows the counts
- [x] **AC-US3-04**: Reuses existing `recoverStuckSubmissions()` from recovery.ts (no duplicate logic)

## Functional Requirements

### FR-001: Pause flag storage
Pause state stored as `queue:paused` key in `QUEUE_METRICS_KV` (no TTL — explicit clear required). Consumer checks this at the start of every batch.

### FR-002: Stuck submission data in status endpoint
The `/api/v1/admin/queue/status` response is extended with:
```json
{
  "paused": false,
  "stuck": {
    "count": 3,
    "byState": { "TIER1_SCANNING": 2, "RECEIVED": 1 },
    "oldest": { "id": "...", "state": "...", "stuckForMs": 360000 },
    "list": [{ "id": "...", "skillName": "...", "repoUrl": "...", "state": "...", "stuckForMs": 360000 }]
  }
}
```

## Success Criteria

- Zero duplicate re-enqueue logic (bulk-requeue uses recovery.ts)
- Pause flag honored by queue consumer within one batch cycle
- Admin can detect and recover stuck submissions without CLI access

## Out of Scope

- Queue depth from Cloudflare API (not accessible from Workers runtime)
- Individual submission retry tracking in UI
- Email/Slack alerts for queue degradation (future increment)
- Webhook-based queue management
