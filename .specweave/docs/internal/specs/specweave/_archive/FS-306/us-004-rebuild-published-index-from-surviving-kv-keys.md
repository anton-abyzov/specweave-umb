---
id: US-004
feature: FS-306
title: Rebuild Published Index from Surviving KV Keys
status: not-started
priority: P1
created: 2026-02-21
project: specweave
external:
  github:
    issue: 1250
    url: "https://github.com/anton-abyzov/specweave/issues/1250"
---
# US-004: Rebuild Published Index from Surviving KV Keys

**Feature**: [FS-306](./FEATURE.md)

platform operator
**I want** a one-time admin endpoint that rebuilds `skills:published-index` from individual `skill:*` KV keys
**So that** I can recover from a corrupted index without manual KV surgery

---

## Acceptance Criteria

- [ ] **AC-US4-01**: New `POST /api/v1/admin/rebuild-index` endpoint, authenticated via X-Internal-Key or SUPER_ADMIN JWT
- [ ] **AC-US4-02**: Endpoint enumerates all `skill:*` keys (excluding `skill:alias:*`), reads each value, rebuilds the `skills:published-index` blob
- [ ] **AC-US4-03**: Also populates Prisma `Skill` table from the KV data (backfill for US-002)
- [ ] **AC-US4-04**: Returns a report: `{ rebuilt: N, errors: M, orphanedAliases: K }`
- [ ] **AC-US4-05**: Idempotent: running multiple times produces the same result
- [ ] **AC-US4-06**: Unit tests cover: rebuild from 0 keys, rebuild from 50 keys with 2 aliases, error handling for malformed KV values

---

## Implementation

**Increment**: [0306-fix-marketplace-skill-loss](../../../../../increments/0306-fix-marketplace-skill-loss/spec.md)

