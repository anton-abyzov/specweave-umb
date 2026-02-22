---
id: US-005
feature: FS-306
title: Fix addToPublishedIndex Race Condition
status: not-started
priority: P1
created: 2026-02-21
project: specweave
external:
  github:
    issue: 1251
    url: "https://github.com/anton-abyzov/specweave/issues/1251"
---
# US-005: Fix addToPublishedIndex Race Condition

**Feature**: [FS-306](./FEATURE.md)

platform operator
**I want** concurrent skill publishes to not lose index entries
**So that** the published index stays consistent under queue concurrency

---

## Acceptance Criteria

- [ ] **AC-US5-01**: `addToPublishedIndex()` is made idempotent and resilient to concurrent writes: either uses KV metadata versioning for optimistic concurrency, or the index becomes a secondary cache that is periodically rebuilt (US-004 approach)
- [ ] **AC-US5-02**: Since Prisma is now the primary source (US-002/US-003), the KV index becomes a performance cache; if a race loses an entry, the next cache rebuild or Prisma read recovers it
- [ ] **AC-US5-03**: Document in code comments that `skills:published-index` is a best-effort cache, not source of truth
- [ ] **AC-US5-04**: Unit tests verify that concurrent calls to `addToPublishedIndex()` with different slugs do not lose entries (simulated with delayed reads)

---

## Implementation

**Increment**: [0306-fix-marketplace-skill-loss](../../../../../increments/0306-fix-marketplace-skill-loss/spec.md)

