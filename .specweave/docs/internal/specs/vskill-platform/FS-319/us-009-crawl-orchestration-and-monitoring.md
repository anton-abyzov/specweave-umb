---
id: US-009
feature: FS-319
title: Crawl Orchestration and Monitoring
status: complete
priority: P1
created: 2026-02-22
project: vskill-platform
external:
  github:
    issue: 1273
    url: https://github.com/anton-abyzov/specweave/issues/1273
---
# US-009: Crawl Orchestration and Monitoring

**Feature**: [FS-319](./FEATURE.md)

platform operator
**I want** staggered cron scheduling and queue depth monitoring
**So that** the discovery pipeline never stops and I can track throughput per source

---

## Acceptance Criteria

- [x] **AC-US9-01**: CF cron dispatches crawl jobs to VMs (replaces inline discovery for heavy sources)
- [x] **AC-US9-02**: Different sources run on different schedules (Sourcegraph: every 2h, GitHub sharded: every 30min, Events: continuous)
- [x] **AC-US9-03**: Crawl metrics tracked in KV: discoveries per source per hour, crawl duration, errors
- [x] **AC-US9-04**: `/api/v1/admin/crawl-metrics` endpoint returns current discovery rates

---

## Implementation

**Increment**: [0319-discovery-scale-up](../../../../../increments/0319-discovery-scale-up/spec.md)

