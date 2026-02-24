---
id: US-006
feature: FS-355
title: Stats Health Check
status: complete
priority: P2
created: 2026-02-24
project: vskill-platform
---
# US-006: Stats Health Check

**Feature**: [FS-355](./FEATURE.md)

platform operator
**I want** a health check endpoint for stats freshness
**So that** I can monitor whether the stats pipeline is healthy

---

## Acceptance Criteria

- [x] **AC-US6-01**: GET `/api/v1/stats/health` endpoint returns cache age, staleness status, and key metrics
- [x] **AC-US6-02**: Returns HTTP 503 when stats are missing or stale (>4 hours)

---

## Implementation

**Increment**: [0355-fix-homepage-zero-stats](../../../../../increments/0355-fix-homepage-zero-stats/spec.md)

