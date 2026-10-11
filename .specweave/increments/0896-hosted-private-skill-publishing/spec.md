# Hosted private skill publishing

## Problem

0847 shipped public publishing and local private GitHub installation, but its AC-US3-06 ("public and private publish sandboxes both pass, with private access using scoped GitHub credentials only") never passed. The platform has no tenant-preserving storage, queue and publish path for private skills: the 2026-10-09 release deliberately rejects private publish intent before billing, repository or queue writes and keeps `HOSTED_PRIVATE_PUBLISHING_AVAILABLE=false`. 0847 T-016 stayed blocked on that one criterion, so this increment carries it forward and lets 0847 close.

## Scope

In: a private publish path that keeps tenant and privacy through submission, scan, approval and publish; private reads with scoped GitHub installation credentials only; a private publish sandbox next to the existing public one; turning the launch gate on only after both pass. Out: pricing or billing changes, enterprise SSO/SCIM (0842), and the paywall UI that 0874 owns.

## Acceptance Criteria

- [ ] AC-01: A private skill submitted by an entitled tenant is stored, queued, scanned and published with its tenant and PRIVATE visibility preserved at every step, and never appears on public routes, search or publisher stats.
- [ ] AC-02: Private repository reads use only the tenant's scoped GitHub installation credentials; platform credentials are never used for private content.
- [ ] AC-03: Public and private publish sandboxes both pass in one automated run (moved from 0847 AC-US3-06).
- [ ] AC-04: `HOSTED_PRIVATE_PUBLISHING_AVAILABLE` is turned on only after AC-01..AC-03 pass, and turning it off again restores the current safe rejection.

## Approach

Starts from the 0847 October audit (T-041 refuses private intent today; T-042 keeps public scans off private content) and the 0874 tier gates. Coordinate with the 0874 owner before touching submission routes. Product-gated: start it only when Anton decides to sell hosted private publishing.

## Open questions

- Storage model for private skill content (tenant-scoped rows vs separate store) and whether a migration is acceptable.

## Tasks

### T-01 Tenant-preserving private submission and publish path
- AC: AC-01, AC-02 | Files: repositories/anton-abyzov/vskill-platform/src/app/api/v1/submissions/route.ts, repositories/anton-abyzov/vskill-platform/src/lib/submission/publish.ts, repositories/anton-abyzov/vskill-platform/src/lib/hosted-publishing.ts | Test: npm --prefix repositories/anton-abyzov/vskill-platform test -- src/app/api/v1/submissions/__tests__

### T-02 Private publish sandbox alongside the public one
- AC: AC-03 | Files: repositories/anton-abyzov/vskill-platform/tests/e2e/ | Test: npm --prefix repositories/anton-abyzov/vskill-platform run test:e2e

### T-03 Open the launch gate after both sandboxes pass
- AC: AC-04 | Files: repositories/anton-abyzov/vskill-platform/src/lib/hosted-publishing.ts | Test: npm --prefix repositories/anton-abyzov/vskill-platform test -- hosted-publishing
