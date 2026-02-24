---
id: US-002
feature: FS-340
title: JWT Secret Isolate-Lifetime Cache
status: complete
priority: P1
created: 2026-02-24
project: vskill-platform
---
# US-002: JWT Secret Isolate-Lifetime Cache

**Feature**: [FS-340](./FEATURE.md)

platform operator
**I want** the JWT_SECRET resolved once per isolate lifetime and cached in a module-level variable
**So that** subsequent `getJwtSecret()` calls within the same isolate avoid repeated `resolveEnv()` overhead

---

## Acceptance Criteria

- [x] **AC-US2-01**: `getJwtSecret()` in `src/lib/auth.ts` caches the resolved `Uint8Array` in a module-level variable after first resolution
- [x] **AC-US2-02**: Second and subsequent calls to `getJwtSecret()` return the cached value without calling `resolveEnv()`
- [x] **AC-US2-03**: Unit test verifies cache hit: `resolveEnv` called once across two `getJwtSecret()` invocations
- [x] **AC-US2-04**: No TTL or invalidation logic (isolate recycling on deploy handles rotation)

---

## Implementation

**Increment**: [0340-api-perf-optimization](../../../../../increments/0340-api-perf-optimization/spec.md)

