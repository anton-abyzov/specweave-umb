# Preserve ranked model fallback and rule limits

## Problem

Workers discard ranked model lanes and coordinators abandon an eligible named fallback.

## Scope

Preserve ranked model fallback and rule limits and the associated regression tests.

## Acceptance Criteria

- [ ] AC-01: Worker and coordinator fallback honor ranked lanes and list-only rules while preserving billing exclusions.

## Tasks

### T-01 Preserve ranked model fallback and rule limits
- AC: AC-01 | Files: repositories/anton-abyzov/specwithcode-dev/packages/shared/src/providerFallback.ts, repositories/anton-abyzov/specwithcode-dev/packages/shared/src/providerFallback.test.ts | Test: pnpm --filter @specweave-studio/shared test src/providerFallback.test.ts
