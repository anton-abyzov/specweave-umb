---
id: US-004
feature: FS-340
title: Login Route Parallelization
status: complete
priority: P1
created: 2026-02-24
project: vskill-platform
---
# US-004: Login Route Parallelization

**Feature**: [FS-340](./FEATURE.md)

user logging in
**I want** the DB connection to be initiated concurrently with the rate limit check
**So that** DB cold-start latency overlaps with the rate-limit KV lookup instead of happening sequentially

---

## Acceptance Criteria

- [x] **AC-US4-01**: `getDb()` call starts concurrently with (not after) the rate-limit `checkRateLimit()` call in the login route
- [x] **AC-US4-02**: The `prisma` instance from the concurrent `getDb()` is used for subsequent `admin.findUnique` query
- [x] **AC-US4-03**: Rate-limit rejection still returns 429 before any DB query is attempted (await rate limit result before using prisma)

---

## Implementation

**Increment**: [0340-api-perf-optimization](../../../../../increments/0340-api-perf-optimization/spec.md)

