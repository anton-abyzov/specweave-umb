# Architecture Plan: Fix vendor auto-certification gap

## Overview

Three targeted fixes to an existing pipeline. No new services, no schema changes, no new dependencies. All changes are in `repositories/anton-abyzov/vskill-platform/src/lib/`.

## Root Cause Analysis

The data flow today:

```
processSubmission()
  |-- isVendorRepo(repoUrl) -> { isVendor: true, org: "anthropics" }
  |-- updateState(id, "VENDOR_APPROVED")
  |-- publishSkill(id)              <-- sub.isVendor is still FALSE
       |-- deriveCertTier(scan, { isVendor: false })  -> VERIFIED
       |-- labels = ["community", "verified"]          <-- WRONG
       |-- trustTier = T1, trustScore = 0              <-- WRONG
```

`processSubmission` knows the repo is a vendor repo (line 269-270) but never writes `isVendor=true` onto the submission record. By the time `publishSkill` reads the submission from KV, `isVendor` is still `false`.

## Architecture Decisions

### AD-1: Where to set isVendor -- processSubmission (chosen) vs publishSkill

**Chosen: Set it at the source -- processSubmission.**

The vendor detection already happens there. Writing it to the submission record immediately after detection is the natural place. `publishSkill` should not need to re-detect vendor status from scratch; it should trust the submission record.

However, defense-in-depth (US-002) adds a fallback in `publishSkill` so that even if the KV write fails or a code path is added later that bypasses `markVendor`, the correct cert tier is still assigned.

### AD-2: markVendor -- new exported function vs inline update

**Chosen: New exported function `markVendor(id, org)` in submission-store.ts.**

Rationale: The function encapsulates dual-write (KV + DB) with best-effort DB semantics. It is unit-testable in isolation and can be called from the admin backfill endpoint too. The spec explicitly requires it (AC-US1-02).

### AD-3: Backfill -- admin API endpoint vs one-off script

**Chosen: Extend existing admin API surface.**

The platform already has admin endpoints. A new `POST /api/v1/admin/backfill-vendor-cert` endpoint is minimal, idempotent, and can be invoked manually. No one-off scripts to manage.

### AD-4: No ADR needed

This is a bug fix within existing architecture. No new patterns, no schema changes, no new services. The vendor trust pipeline, KV+DB dual-write pattern, and admin endpoint pattern all already exist.

## Component Changes

### 1. submission-store.ts -- `markVendor(id, org)`

New exported function. Two writes:

```
KV: read sub:{id} -> set isVendor=true -> put sub:{id}
DB: update submission set isVendor=true, vendorOrg=org where id=id (best-effort)
```

Idempotent: if `isVendor` is already `true`, the write is a harmless re-write of the same value.

Error handling: KV is primary (throws on failure -- the pipeline depends on it). DB is best-effort (catch and log).

Lines affected: ~15 lines, inserted near `updateState()` / `updateStateMulti()`.

### 2. process-submission.ts -- call markVendor before publishSkill

In the vendor fast-path (lines 270-293), insert `await markVendor(id, vendor.org)` after the `VENDOR_APPROVED` state update and before `publishSkill(id)`.

```
Line 271: await updateState(id, "VENDOR_APPROVED", ...)
+         await markVendor(id, vendor.org!);     <-- NEW
Line 282: await updateState(id, "PUBLISHED", ...)
Line 284: await publishSkill(id, vendorExt, ...)
```

Import change: add `markVendor` to the import from `@/lib/submission-store`.

Lines affected: 2 lines (1 import addition, 1 function call).

### 3. submission-store.ts -- publishSkill fallback

In `publishSkill()`, after reading `sub.isVendor`, add a fallback:

```
const owner = extractOwner(sub.repoUrl);          <-- already exists (line 1035)
const effectiveVendor = sub.isVendor || (owner ? isVendorOrg(owner) : false);
```

Then replace all reads of `sub.isVendor` with `effectiveVendor`:
- Line 994: trust score / tier branch
- Line 1036: labels
- Line 1048: deriveCertTier call

Import change: add `isVendorOrg` to imports from `./trust/trusted-orgs` (currently only imports `isTrustedOrg`).

Lines affected: ~5 lines changed, 1 import addition.

### 4. Admin backfill endpoint -- new route

`src/app/api/v1/admin/backfill-vendor-cert/route.ts`

Logic:
1. Auth check (existing admin auth middleware pattern)
2. Query: `SELECT id, name, author FROM Skill WHERE author IN (...vendorOrgs) AND certTier = 'VERIFIED'`
3. For each skill: `UPDATE Skill SET certTier='CERTIFIED', certMethod='VENDOR_AUTO', trustTier='T4', trustScore=100`
4. Return `{ updated: count, skipped: count }`

Idempotent: the WHERE clause excludes already-CERTIFIED skills.

Lines affected: ~40-50 lines in a new route file.

## Data Flow After Fix

```
processSubmission()
  |-- isVendorRepo(repoUrl) -> { isVendor: true, org: "anthropics" }
  |-- updateState(id, "VENDOR_APPROVED")
  |-- markVendor(id, "anthropics")     <-- NEW: sets sub.isVendor=true in KV+DB
  |-- publishSkill(id)
       |-- sub.isVendor = true          <-- NOW CORRECT
       |-- [fallback] isVendorOrg(owner) <-- defense-in-depth, not needed here
       |-- deriveCertTier(scan, { isVendor: true }) -> CERTIFIED / VENDOR_AUTO
       |-- labels = ["vendor", "certified"]
       |-- trustTier = T4, trustScore = 100
```

## Risk Mitigation

| Risk | Mitigation |
|------|-----------|
| markVendor KV write fails | processSubmission throws, queue retries. No partial state. |
| markVendor DB write fails | Best-effort. publishSkill fallback via isVendorOrg covers it. |
| publishSkill fallback produces false positive | isVendorOrg checks against the same VENDOR_ORG_IDS set used everywhere. Only 7 orgs. No ambiguity. |
| Backfill updates wrong skills | WHERE clause filters strictly by vendor org list + certTier=VERIFIED. Idempotent. |
| Non-vendor skills affected | No code path changes for non-vendor submissions. effectiveVendor=false for them. |

## Test Strategy

TDD -- tests written before implementation.

1. **markVendor unit tests**: verify KV update, verify DB update, verify idempotency, verify DB-failure resilience
2. **processSubmission integration test**: mock isVendorRepo to return true, assert markVendor is called before publishSkill
3. **publishSkill unit tests**: test with sub.isVendor=true (existing path preserved), test with sub.isVendor=false + vendor owner (fallback triggers), test with sub.isVendor=false + non-vendor owner (no change)
4. **backfill endpoint test**: verify correct query, verify idempotency, verify auth gate

## File Impact Summary

| File | Change Type | Lines |
|------|-------------|-------|
| `src/lib/submission-store.ts` | Add `markVendor()`, modify `publishSkill()` | ~20 |
| `src/lib/queue/process-submission.ts` | Add 1 import, 1 function call | ~2 |
| `src/app/api/v1/admin/backfill-vendor-cert/route.ts` | New file | ~45 |
| Test files | New test cases | ~100-150 |

Total production code delta: ~67 lines across 3 files.

## Out of Scope (confirmed)

- No CLI changes needed
- No DB schema migration
- No changes to provider-registry.ts
- No changes to trust-updater.ts (already correct)
- No changes to trust-score.ts computation
