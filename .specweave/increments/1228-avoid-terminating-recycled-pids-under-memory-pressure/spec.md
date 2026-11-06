# Avoid terminating recycled PIDs under memory pressure

## Problem

An arbitrary PID can be recycled between process inspection and signal delivery.

## Scope

Avoid terminating recycled PIDs under memory pressure and the associated regression tests.

## Acceptance Criteria

- [ ] AC-01: Default scans keep kernel OOM priority and never signal arbitrary PIDs. An explicitly owned transport preserves the tested signal flow.

## Tasks

### T-01 Avoid terminating recycled PIDs under memory pressure
- AC: AC-01 | Files: repositories/anton-abyzov/specwithcode-dev/apps/server/src/resourceTelemetry/MemoryGuard.ts, repositories/anton-abyzov/specwithcode-dev/apps/server/src/resourceTelemetry/MemoryGuard.test.ts | Test: pnpm --filter specweave-studio test src/resourceTelemetry/MemoryGuard.test.ts
