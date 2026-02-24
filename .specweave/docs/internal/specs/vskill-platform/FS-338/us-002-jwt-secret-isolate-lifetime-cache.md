---
id: US-002
feature: FS-338
title: JWT Secret Isolate-Lifetime Cache
status: not-started
priority: P1
created: 2026-02-23
project: vskill-platform
---
# US-002: JWT Secret Isolate-Lifetime Cache

**Feature**: [FS-338](./FEATURE.md)

platform operator
**I want** the JWT_SECRET resolved once per isolate lifetime and cached in a module-level variable
**So that** subsequent `getJwtSecret()` calls within the same isolate avoid repeated `resolveEnv()` overhead

---

## Acceptance Criteria

- [ ] **AC-US2-01**: `getJwtSecret()` in `src/lib/auth.ts` caches the resolved `Uint8Array` in a module-level variable after first resolution
- [ ] **AC-US2-02**: Second and subsequent calls to `getJwtSecret()` return the cached value without calling `resolveEnv()`
- [ ] **AC-US2-03**: Unit test verifies cache hit: `resolveEnv` called once across two `getJwtSecret()` invocations
- [ ] **AC-US2-04**: No TTL or invalidation logic (isolate recycling on deploy handles rotation)

---

## Implementation

**Increment**: [0338-api-perf-optimization](../../../../../increments/0338-api-perf-optimization/spec.md)

