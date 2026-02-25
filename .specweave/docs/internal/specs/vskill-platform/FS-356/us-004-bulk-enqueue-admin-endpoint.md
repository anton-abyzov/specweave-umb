---
id: US-004
feature: FS-356
title: Bulk-Enqueue Admin Endpoint
status: complete
priority: P1
created: 2026-02-25
project: vskill-platform
---
# US-004: Bulk-Enqueue Admin Endpoint

**Feature**: [FS-356](./FEATURE.md)

Hetzner VM operator
**I want** a `POST /api/v1/admin/queue/bulk-enqueue` endpoint that accepts an array of repositories and enqueues them for processing
**So that** VMs running external discovery scripts can submit thousands of repos directly without the overhead of per-repo HTTP calls to `/api/v1/submissions`

---

## Acceptance Criteria

- [x] **AC-US4-01**: `POST /api/v1/admin/queue/bulk-enqueue` route exists at `src/app/api/v1/admin/queue/bulk-enqueue/route.ts`
- [x] **AC-US4-02**: Authentication requires either `X-Internal-Key` header matching `INTERNAL_BROADCAST_KEY` or `SUPER_ADMIN` JWT (same pattern as `/api/v1/admin/discovery/bulk`)
- [x] **AC-US4-03**: Request body accepts `{ items: Array<{ repoUrl: string; skillName: string; skillPath?: string }> }` with a max of 1000 items per request
- [x] **AC-US4-04**: Endpoint uses `createSubmissionsBatch` from `submission-store.ts` to batch-create KV + DB records
- [x] **AC-US4-05**: Endpoint uses `SUBMISSION_QUEUE.sendBatch` in chunks of 100 (CF Queue limit) to enqueue all items
- [x] **AC-US4-06**: Response returns `{ ok: true, enqueued: number, skipped: number, errors: string[] }` with HTTP 200
- [x] **AC-US4-07**: Items with invalid `repoUrl` (not matching GitHub URL regex) are skipped with reason in `errors`
- [x] **AC-US4-08**: Returns 400 if `items` is missing, not an array, or exceeds 1000 entries

---

## Implementation

**Increment**: [0356-scale-queue-throughput](../../../../../increments/0356-scale-queue-throughput/spec.md)

