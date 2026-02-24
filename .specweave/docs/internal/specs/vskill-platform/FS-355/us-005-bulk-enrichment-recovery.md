---
id: US-005
feature: FS-355
title: Bulk Enrichment Recovery
status: complete
priority: P1
created: 2026-02-24
project: vskill-platform
---
# US-005: Bulk Enrichment Recovery

**Feature**: [FS-355](./FEATURE.md)

platform operator
**I want** an admin endpoint to bulk-enrich all skills
**So that** I can recover from enrichment pipeline starvation without waiting for hourly cron cycles

---

## Acceptance Criteria

- [x] **AC-US5-01**: POST `/api/v1/admin/enrich` endpoint exists with X-Internal-Key auth
- [x] **AC-US5-02**: Endpoint processes all non-deprecated skills in batches of 50 with 1s pause between batches
- [x] **AC-US5-03**: Endpoint recomputes trending scores and refreshes stats cache after enrichment
- [x] **AC-US5-04**: Returns JSON summary: `{ processed, updated, errors }`

---

## Implementation

**Increment**: [0355-fix-homepage-zero-stats](../../../../../increments/0355-fix-homepage-zero-stats/spec.md)

