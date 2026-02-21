---
id: US-007
feature: FS-306
title: Marketplace Health Monitoring Endpoint
status: not-started
priority: P2
created: 2026-02-21
project: specweave
external:
  github:
    issue: 1253
    url: https://github.com/anton-abyzov/specweave/issues/1253
---
# US-007: Marketplace Health Monitoring Endpoint

**Feature**: [FS-306](./FEATURE.md)

platform operator
**I want** a health endpoint that reports skill count consistency across data sources
**So that** I can detect skill loss early before users are affected

---

## Acceptance Criteria

- [ ] **AC-US7-01**: New `GET /api/v1/admin/health/skills` endpoint returns `{ kv_index_count, kv_enumerated_count, prisma_count, seed_count, drift_detected, drifts: [] }`
- [ ] **AC-US7-02**: Drift is flagged when any count differs from another by more than 5% or more than 10 skills
- [ ] **AC-US7-03**: Endpoint is authenticated (SUPER_ADMIN or X-Internal-Key)
- [ ] **AC-US7-04**: Response includes a `recommendations` array with actionable suggestions (e.g., "Run rebuild-index to fix KV drift")
- [ ] **AC-US7-05**: Unit tests cover: no drift scenario, KV index < KV keys drift, Prisma < KV drift

---

## Implementation

**Increment**: [0306-fix-marketplace-skill-loss](../../../../../increments/0306-fix-marketplace-skill-loss/spec.md)

