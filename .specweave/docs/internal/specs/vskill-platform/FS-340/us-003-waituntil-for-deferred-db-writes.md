---
id: US-003
feature: FS-340
title: waitUntil for Deferred DB Writes
status: complete
priority: P1
created: 2026-02-24
project: vskill-platform
---
# US-003: waitUntil for Deferred DB Writes

**Feature**: [FS-340](./FEATURE.md)

user logging in
**I want** the `lastLoginAt` update and refresh token storage to happen after the response is sent
**So that** login and OAuth callback responses return faster without waiting for non-critical writes

---

## Acceptance Criteria

- [x] **AC-US3-01**: Login route (`src/app/api/v1/auth/login/route.ts`) obtains `ctx` via `getCloudflareContext({ async: true })` and defers `lastLoginAt` update with `ctx.waitUntil()`
- [x] **AC-US3-02**: Login route defers refresh token `create` with `ctx.waitUntil()`
- [x] **AC-US3-03**: OAuth callback route (`src/app/api/v1/auth/github/callback/route.ts`) obtains `ctx` via `getCloudflareContext({ async: true })` and defers refresh token storage with `ctx.waitUntil()`
- [x] **AC-US3-04**: Response is returned before deferred operations complete
- [x] **AC-US3-05**: Unit test verifies `waitUntil` is called with deferred operations (mock `getCloudflareContext`)

---

## Implementation

**Increment**: [0340-api-perf-optimization](../../../../../increments/0340-api-perf-optimization/spec.md)

