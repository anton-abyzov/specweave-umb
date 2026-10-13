# Hosted private skill publishing

## Problem

0847 shipped public publishing and local private GitHub installation, but its AC-US3-06 ("public and private publish sandboxes both pass, with private access using scoped GitHub credentials only") never passed. The platform has no tenant-preserving storage, queue and publish path for private skills: the 2026-10-09 release deliberately rejects private publish intent before billing, repository or queue writes and keeps `HOSTED_PRIVATE_PUBLISHING_AVAILABLE=false`. 0847 T-016 stayed blocked on that one criterion, so this increment carries it forward and lets 0847 close.

## Scope

In: a private publish path that keeps tenant and privacy through submission, scan, approval and publish; private reads with scoped GitHub installation credentials only; a private publish sandbox next to the existing public one; turning the launch gate on only after both pass. Out: pricing or billing changes, enterprise SSO/SCIM (0842), and the paywall UI that 0874 owns.

## Acceptance Criteria

- [ ] AC-01: A private skill submitted by an entitled tenant is stored, queued, scanned and published with its tenant and PRIVATE visibility preserved at every step, and never appears on public routes, search or publisher stats.
- [ ] AC-02: Private repository reads use only the tenant's scoped GitHub installation credentials; platform credentials are never used for private content.
- [ ] AC-03: Public and private publish sandboxes both pass in one automated run (moved from 0847 AC-US3-06).
- [ ] AC-04: `HOSTED_PRIVATE_PUBLISHING_AVAILABLE` is turned on only after AC-01..AC-03 and AC-05..AC-08 pass, and turning it off again restores the current safe rejection.
- [ ] AC-05: With the gate open, a Studio private publish by an entitled user sends the selected tenant's `tenantId` (from every caller that renders `PublishButton`: the Overview tab via `PublishStatusRow` and the Edit tab via `EditorPanel`), so the platform never answers 400 `missing_tenant`; with the gate closed, Studio still omits `tenantId`. (0874 acceptance step 8: no Studio caller passes `tenantId`.)
- [ ] AC-06: The Studio eval-server submission guard follows the gate: while closed it refuses every private repository with 422 `private_repository` as today; while open, a private-repo skill with private intent and a `tenantId` goes to the tenant-scoped private path, and public intent for a private repo is still refused. (0874 acceptance: the guard refuses every private repo whatever the gate says.)
- [ ] AC-07: Before AC-04 opens the gate, production `VSKILL_FREE_PRIVATE_SKILL_LIMIT` matches a recorded owner decision. Today `vskill-platform/wrangler.jsonc` `vars` sets it to `"50"`, overriding the code default of 0 in `src/lib/tenant-caps.ts` (`FREE_PRIVATE_SKILL_LIMIT_DEFAULT`), so free tenants would get 50 private skills, not the 0874 "paid unlocks private" paywall. A test pins the shipped value to the decision, and a free tenant past it gets 402 `TENANT_LIMIT_REACHED`.
- [ ] AC-08: The real publish pipeline never drops private intent: Submission persistence carries privacy and tenant, and a private-intent `POST /api/v1/submissions` is either carried PRIVATE and tenant-scoped through scan and publish or rejected; it is never stored or published as PUBLIC. (0874 acceptance: the Submission table has no privacy or tenant column, so private intent for a public repo entered the public pipeline with 201; private publish only worked through the tenant route.)

## Approach

Anton authorized completing hosted private publishing on 2026-10-13. Existing 0874 fixes are merged and its tasks complete; 0896 has no existing claims. Implementation uses isolated worktrees, preserving the dirty umbrella ledger and unrelated work.

Private submission records and processing are isolated from the existing public submission store, queue listings, lifecycle broadcasts, and external public scan dispatch. An additive tenant-scoped private submission model avoids migrating the public catalog's global identity constraints. Private publication uses tenant-namespaced internal Skill identities with normal display names; every private status/read authenticates tenant membership. Queue messages carry only the private record ID, and processing re-resolves tenant, entitlement and scoped GitHub installation credentials from persistence. Never fall back to platform GitHub credentials. A content-hash match is an idempotent no-op; changed bundles create versions. Closed-gate rollback rejects new private work and checkout.

Free hosted private allowance is 0 (Anton's 2026-10-12 decision, preserved in ledger). Local private GitHub installation remains free. Tests use an isolated local database, never inherited production DATABASE_URL, and explicitly headless browsers. Production migration and new UI require concrete manual acceptance before closure. Existing Prisma schema exceeds 1500 lines; split it into a Prisma schema folder before adding models, retaining all existing definitions and SQL semantics.

## Tasks

### T-01 Tenant-preserving private submission and publish path
- AC: AC-01, AC-02 | Files: repositories/anton-abyzov/vskill-platform/src/app/api/v1/submissions/route.ts, repositories/anton-abyzov/vskill-platform/src/lib/private-publishing/, repositories/anton-abyzov/vskill-platform/src/lib/queue/consumer.ts, repositories/anton-abyzov/vskill-platform/src/lib/queue/types.ts, repositories/anton-abyzov/vskill-platform/src/app/api/v1/tenants/, repositories/anton-abyzov/vskill-platform/src/app/api/v1/submissions/[id]/route.ts, repositories/anton-abyzov/vskill-platform/src/app/api/v1/submissions/__tests__/ | Test: npm --prefix repositories/anton-abyzov/vskill-platform test -- src/app/api/v1/submissions/__tests__

### T-02 Private publish sandbox alongside the public one
- AC: AC-03 | Files: repositories/anton-abyzov/vskill-platform/tests/e2e/ | Test: npm --prefix repositories/anton-abyzov/vskill-platform run test:e2e

### T-03 Open the launch gate after both sandboxes pass
- AC: AC-04 | Files: repositories/anton-abyzov/vskill-platform/src/lib/hosted-publishing.ts | Test: npm --prefix repositories/anton-abyzov/vskill-platform test -- hosted-publishing

### T-04 Studio sends the tenant on private publish
- AC: AC-05 | Files: repositories/anton-abyzov/vskill/src/eval-ui/, repositories/anton-abyzov/vskill/src/api/, repositories/anton-abyzov/vskill/src/eval-server/platform-proxy.ts, repositories/anton-abyzov/vskill/src/lib/hosted-publishing.ts | Test: npm --prefix repositories/anton-abyzov/vskill test -- src/eval-ui/src/components/__tests__/PublishButton.test.tsx src/eval-ui/src/components/__tests__/PublishDrawerPrivacy.test.tsx

### T-05 Gate-aware eval-server submission guard
- AC: AC-06 | Files: repositories/anton-abyzov/vskill/src/eval-server/submission-guard.ts, repositories/anton-abyzov/vskill/src/eval-server/__tests__/ | Test: npm --prefix repositories/anton-abyzov/vskill test -- src/eval-server/__tests__/platform-proxy-submission-guard.test.ts

### T-06 Free private allowance matches the owner decision
- AC: AC-07 | Files: repositories/anton-abyzov/vskill-platform/wrangler.jsonc, repositories/anton-abyzov/vskill-platform/src/lib/tenant-caps.ts, repositories/anton-abyzov/vskill-platform/src/lib/tenant-caps.test.ts | Test: npm --prefix repositories/anton-abyzov/vskill-platform test -- src/lib/tenant-caps.test.ts

### T-07 Persist privacy and tenant on submissions
- AC: AC-08, AC-01 | Files: repositories/anton-abyzov/vskill-platform/prisma/, repositories/anton-abyzov/vskill-platform/package.json, repositories/anton-abyzov/vskill-platform/package-lock.json, repositories/anton-abyzov/vskill-platform/src/__tests__/schema/, repositories/anton-abyzov/vskill-platform/scripts/, repositories/anton-abyzov/vskill-platform/src/lib/private-publishing/ | Test: npm --prefix repositories/anton-abyzov/vskill-platform test -- src/app/api/v1/submissions/__tests__ src/lib/submission

### T-08 Verify private status, publication and no public egress
- AC: AC-01, AC-02, AC-03, AC-08 | Files: repositories/anton-abyzov/vskill-platform/tests/integration/0896/, repositories/anton-abyzov/vskill-platform/tests/e2e/0896/, repositories/anton-abyzov/vskill-platform/scripts/0896/ | Test: npm --prefix repositories/anton-abyzov/vskill-platform test -- tests/integration/0896

### T-09 Release evidence and manual acceptance
- AC: AC-04 | Files: .specweave/increments/0896-hosted-private-skill-publishing/reports/, repositories/anton-abyzov/vskill/docs/private-skills-repo.md, repositories/anton-abyzov/vskill/package.json, repositories/anton-abyzov/vskill/package-lock.json | Test: git diff --check
