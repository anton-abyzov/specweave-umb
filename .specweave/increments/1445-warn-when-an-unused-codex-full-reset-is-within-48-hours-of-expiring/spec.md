# Warn before an unused full reset expires

## Problem

Usage shows the next expiry. A user can miss a banked reset because nothing calls attention to the last two days.

## Scope

Use available full resets from the existing native usage snapshot. Keep redemption manual and confirmed.

## Acceptance Criteria

- [ ] AC-01: The wire contract preserves the next available credit id and identifies available full resets with their expiries. Older payloads still decode.
- [ ] AC-02: Within the inclusive 48-hour window, each unexpired full reset gets one system notification per credit id through the existing quota notification path. Restarting preserves the record.
- [ ] AC-03: Usage shows the expiring count and earliest local time alongside the existing confirmation-gated action. Expired, redeemed and unavailable resets do not warn.

## Approach

Extend the existing mapper and optional contract. Reuse quota alerts, their persistent notification record and the account redemption target. Exercise eligibility, persistence, wording and confirmation with fixtures.

## Tasks

### T-01 Preserve reset identities in usage snapshots
- AC: AC-01 | Files: repositories/anton-abyzov/specwithcode/packages/contracts/src/providerUsageLimits.ts, repositories/anton-abyzov/specwithcode/apps/server/src/provider/codexUsageLimits.ts, repositories/anton-abyzov/specwithcode/apps/server/src/provider/codexUsageLimits.test.ts | Test: pnpm test src/provider/codexUsageLimits.test.ts

### T-02 Warn on existing usage reads and show manual redemption
- AC: AC-02, AC-03 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/usage/alerts/QuotaAlertBanner.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/usage/alerts/resetExpiry.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/usage/alerts/resetExpiry.test.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/usage/UsageLimits.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/usage/UsagePage.tsx | Test: pnpm test src/components/usage/alerts/resetExpiry.test.tsx
