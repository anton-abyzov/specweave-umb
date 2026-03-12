---
id: US-002
feature: FS-393
title: "Increase CF Queue Concurrency (P1)"
status: completed
priority: P1
created: "2026-03-01T00:00:00.000Z"
tldr: "**As a** platform operator."
project: vskill-platform
---

# US-002: Increase CF Queue Concurrency (P1)

**Feature**: [FS-393](./FEATURE.md)

**As a** platform operator
**I want** the Cloudflare Queue consumer to process more submissions in parallel
**So that** queue drain time decreases and throughput increases when the CF path is active

---

## Acceptance Criteria

- [x] **AC-US2-01**: `wrangler.jsonc` sets `max_concurrency` to 10 for the `submission-processing` queue consumer
- [x] **AC-US2-02**: `consumer.ts` sets `BATCH_CONCURRENCY` to 3 (up from 1)
- [x] **AC-US2-03**: `max_batch_size` remains at 5 (no change needed)
- [x] **AC-US2-04**: The consumer handles concurrent processing failures gracefully without corrupting submission state

---

## Implementation

**Increment**: [0393-crawl-pipeline-throughput](../../../../../increments/0393-crawl-pipeline-throughput/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_
