---
id: US-004
feature: FS-393
title: "Feature Flag to Skip CF Queue Enqueue (P2)"
status: completed
priority: P1
created: "2026-03-01T00:00:00.000Z"
tldr: "**As a** platform operator."
project: vskill-platform
---

# US-004: Feature Flag to Skip CF Queue Enqueue (P2)

**Feature**: [FS-393](./FEATURE.md)

**As a** platform operator
**I want** a feature flag `SKIP_QUEUE_ENQUEUE` that prevents submissions from being sent to the CF Queue
**So that** when VMs are handling all work, we avoid unnecessary queue operations and can re-enable the CF Queue path as a fallback if VMs go down

---

## Acceptance Criteria

- [x] **AC-US4-01**: `submissions/route.ts` (POST handler) checks `SKIP_QUEUE_ENQUEUE` env var before calling `SUBMISSION_QUEUE.send()` or `sendBatch()`
- [x] **AC-US4-02**: When `SKIP_QUEUE_ENQUEUE` is truthy (default: "true"), the queue send is skipped entirely; submissions remain in RECEIVED state for VM pickup
- [x] **AC-US4-03**: When `SKIP_QUEUE_ENQUEUE` is falsy or unset, the existing CF Queue path works unchanged (backward compatible)
- [x] **AC-US4-04**: `env.d.ts` is updated to declare the `SKIP_QUEUE_ENQUEUE` binding
- [x] **AC-US4-05**: The `enqueue-submissions/route.ts` endpoint (called by queue-processor) also respects `SKIP_QUEUE_ENQUEUE` to prevent the queue-processor from re-enqueuing items

---

## Implementation

**Increment**: [0393-crawl-pipeline-throughput](../../../../../increments/0393-crawl-pipeline-throughput/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_
