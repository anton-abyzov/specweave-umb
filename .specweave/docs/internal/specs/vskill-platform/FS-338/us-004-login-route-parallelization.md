---
id: US-004
feature: FS-338
title: Login Route Parallelization
status: not-started
priority: P1
created: 2026-02-23
project: vskill-platform
---
# US-004: Login Route Parallelization

**Feature**: [FS-338](./FEATURE.md)

user logging in
**I want** the DB connection to be initiated concurrently with the rate limit check
**So that** DB cold-start latency overlaps with the rate-limit KV lookup instead of happening sequentially

---

## Acceptance Criteria

- [ ] **AC-US4-01**: `getDb()` call starts concurrently with (not after) the rate-limit `checkRateLimit()` call in the login route
- [ ] **AC-US4-02**: The `prisma` instance from the concurrent `getDb()` is used for subsequent `admin.findUnique` query
- [ ] **AC-US4-03**: Rate-limit rejection still returns 429 before any DB query is attempted (await rate limit result before using prisma)

---

## Implementation

**Increment**: [0338-api-perf-optimization](../../../../../increments/0338-api-perf-optimization/spec.md)

