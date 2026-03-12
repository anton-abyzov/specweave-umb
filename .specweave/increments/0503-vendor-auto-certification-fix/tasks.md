---
increment: 0503-vendor-auto-certification-fix
total_tasks: 4
completed_tasks: 0
by_user_story:
  US-001: [T-001, T-002]
  US-002: [T-003]
  US-003: [T-004]
---

# Tasks: Fix vendor auto-certification gap

## Task Notation

- `[ ]` Not started | `[x]` Completed
- **Satisfies ACs** links each task to spec acceptance criteria

---

## User Story: US-001 - Mark submission as vendor before publishing

**Linked ACs**: AC-US1-01, AC-US1-02, AC-US1-03
**Tasks**: 2 total, 0 completed

---

### T-001: Add markVendor() to submission-store.ts

**User Story**: US-001
**Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03
**Status**: [ ] pending

**Test Plan**:
- **Given** a valid submission ID and a vendor org name
- **When** `markVendor(id, org)` is called
- **Then** the KV entry for that submission has `isVendor=true` and the DB record is updated with `isVendor=true, vendorOrg=org`

- **Given** `markVendor` is called for a submission that already has `isVendor=true`
- **When** the function executes
- **Then** it completes without error and the value remains `true` (idempotent)

- **Given** the DB write fails during `markVendor`
- **When** the error is caught
- **Then** the KV update is preserved and the error is logged but not re-thrown

- **Given** a submission from a non-vendor org
- **When** `processSubmission` runs
- **Then** `markVendor` is NOT called and `isVendor` stays `false`

**Test Cases**:
1. **Unit**: `src/lib/__tests__/submission-store.markVendor.test.ts`
   - `markVendor_setsIsVendorInKV()`: KV entry read, mutated, written back with `isVendor=true`
   - `markVendor_updatesDB()`: Prisma `update` called with correct fields
   - `markVendor_isIdempotent()`: Second call with same ID is safe
   - `markVendor_DBFailureDoesNotThrow()`: DB error caught, KV still updated
   - **Coverage Target**: 95%

**Implementation**:
1. In `src/lib/submission-store.ts`, add exported `async function markVendor(id: string, org: string, env: CloudflareEnv): Promise<void>`
2. Read `sub:{id}` from KV; if `sub.isVendor` is already `true`, return early
3. Set `sub.isVendor = true`; put updated record back to KV (throws on failure)
4. Wrap DB update (`prisma.submission.update({ where: { id }, data: { isVendor: true, vendorOrg: org } })`) in try/catch; log on error, do not rethrow
5. Export `markVendor` alongside existing exports

---

### T-002: Call markVendor in processSubmission vendor fast-path

**User Story**: US-001
**Satisfies ACs**: AC-US1-01, AC-US1-03
**Status**: [ ] pending

**Test Plan**:
- **Given** `isVendorRepo()` returns `{ isVendor: true, org: "anthropics" }` for a repo URL
- **When** `processSubmission` runs its vendor fast-path
- **Then** `markVendor(id, "anthropics")` is awaited before `publishSkill(id)` is called

- **Given** `isVendorRepo()` returns `{ isVendor: false }` for a non-vendor repo
- **When** `processSubmission` runs
- **Then** `markVendor` is never called

**Test Cases**:
1. **Integration**: `src/lib/queue/__tests__/process-submission.vendor.test.ts`
   - `vendorFastPath_callsMarkVendorBeforePublish()`: mock `markVendor` and `publishSkill`; assert call order
   - `nonVendorPath_doesNotCallMarkVendor()`: mock `isVendorRepo` to return false; assert `markVendor` not called
   - **Coverage Target**: 90%

**Implementation**:
1. In `src/lib/queue/process-submission.ts`, add `markVendor` to the import from `@/lib/submission-store`
2. In the vendor fast-path (after `updateState(id, "VENDOR_APPROVED", ...)` and before `publishSkill(id, ...)`), insert: `await markVendor(id, vendor.org!, env);`
3. Confirm the vendor org value (`vendor.org`) is already available at that call site from the `isVendorRepo()` return

---

## User Story: US-002 - Add vendor org fallback in publishSkill

**Linked ACs**: AC-US2-01, AC-US2-02, AC-US2-03
**Tasks**: 1 total, 0 completed

---

### T-003: Add isVendorOrg fallback inside publishSkill

**User Story**: US-002
**Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03
**Status**: [ ] pending

**Test Plan**:
- **Given** `sub.isVendor` is `false` but `extractOwner(sub.repoUrl)` returns `"anthropics"` (a vendor org)
- **When** `publishSkill()` runs
- **Then** the skill is assigned `certTier=CERTIFIED`, `certMethod=VENDOR_AUTO`, `trustTier=T4`, `trustScore=100`, labels `["vendor", "certified"]`

- **Given** `sub.isVendor` is `false` and the owner is a non-vendor org
- **When** `publishSkill()` runs
- **Then** the skill receives `certTier=VERIFIED` and community labels (no regression)

- **Given** `sub.isVendor` is `true`
- **When** `publishSkill()` runs
- **Then** the existing vendor path is exercised; `isVendorOrg` check is not needed (preserved behavior)

**Test Cases**:
1. **Unit**: `src/lib/__tests__/submission-store.publishSkill.test.ts`
   - `publishSkill_vendorFlagFalseButVendorOwner_certifiesAsVendor()`: `sub.isVendor=false`, owner=`anthropics` → CERTIFIED/T4
   - `publishSkill_vendorFlagFalseNonVendorOwner_verifiedCommunity()`: `sub.isVendor=false`, owner=`random-user` → VERIFIED/T1
   - `publishSkill_vendorFlagTrue_existingPathPreserved()`: `sub.isVendor=true` → CERTIFIED/T4 (no regression)
   - **Coverage Target**: 95%

**Implementation**:
1. In `src/lib/submission-store.ts`, add `isVendorOrg` to imports from `./trust/trusted-orgs`
2. In `publishSkill()`, after reading `sub.isVendor` and `owner` (already via `extractOwner`), compute: `const effectiveVendor = sub.isVendor || (owner ? isVendorOrg(owner) : false);`
3. Replace all reads of `sub.isVendor` with `effectiveVendor` in: trust score/tier branch, labels assignment, and `deriveCertTier` call
4. No other changes to `publishSkill` logic

---

## User Story: US-003 - Backfill existing vendor skills

**Linked ACs**: AC-US3-01, AC-US3-02
**Tasks**: 1 total, 0 completed

---

### T-004: Create admin backfill-vendor-cert endpoint

**User Story**: US-003
**Satisfies ACs**: AC-US3-01, AC-US3-02
**Status**: [ ] pending

**Test Plan**:
- **Given** skills in the DB with `author IN (vendorOrgs)` and `certTier = "VERIFIED"`
- **When** `POST /api/v1/admin/backfill-vendor-cert` is called with valid admin auth
- **Then** those skills are updated to `certTier=CERTIFIED`, `certMethod=VENDOR_AUTO`, `trustTier=T4`, `trustScore=100` and the response contains `{ updated: N, skipped: M }`

- **Given** a vendor skill already has `certTier = "CERTIFIED"`
- **When** the backfill runs
- **Then** that skill is skipped (idempotent, not double-updated)

- **Given** the request lacks admin auth
- **When** the endpoint is called
- **Then** it returns 401

**Test Cases**:
1. **Unit/Integration**: `src/app/api/v1/admin/backfill-vendor-cert/__tests__/route.test.ts`
   - `backfill_updatesVerifiedVendorSkills()`: mock Prisma; assert correct `updateMany` call
   - `backfill_skipsAlreadyCertifiedSkills()`: WHERE clause excludes CERTIFIED skills
   - `backfill_isIdempotent()`: running twice produces `{ updated: 0 }` on second run
   - `backfill_returns401WithoutAuth()`: no auth header → 401
   - **Coverage Target**: 90%

**Implementation**:
1. Create `src/app/api/v1/admin/backfill-vendor-cert/route.ts`
2. Add admin auth check using the existing admin auth middleware pattern (check existing admin routes for the pattern)
3. Build vendor org list from `VENDOR_ORG_IDS` exported by `trust/trusted-orgs.ts`
4. Run `prisma.skill.updateMany({ where: { author: { in: [...vendorOrgIds] }, certTier: "VERIFIED" }, data: { certTier: "CERTIFIED", certMethod: "VENDOR_AUTO", trustTier: "T4", trustScore: 100 } })`
5. Count skipped by querying vendor skills with `certTier: "CERTIFIED"` or derive from total vs updated
6. Return `NextResponse.json({ updated: result.count, skipped })`
