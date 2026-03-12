---
increment: 0503-vendor-auto-certification-fix
title: "Fix vendor auto-certification gap in publish pipeline"
type: bug-fix
priority: P1
status: active
created: 2026-03-12
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Fix vendor auto-certification gap in publish pipeline

## Problem Statement

Skills from certified vendor organizations (anthropics, openai, google, microsoft, vercel, cloudflare, google-gemini) display as "unreviewed" instead of "certified" in `vskill find` results. The vendor org registry correctly identifies these orgs, but the publish pipeline never propagates the `isVendor` flag on the submission record. As a result, `publishSkill()` treats vendor skills as community skills, assigning them VERIFIED/T1 instead of CERTIFIED/T4.

## Root Cause

Three gaps in the trust pipeline:

1. **processSubmission** (`process-submission.ts`) detects vendor status via `isVendorRepo()` at line 269, enters the vendor fast-path (VENDOR_APPROVED -> PUBLISHED), but never sets `submission.isVendor = true` in KV or DB before calling `publishSkill()`.
2. **publishSkill** (`submission-store.ts`) reads `sub.isVendor` (always `false` for vendor skills) to determine labels, trust tier, and cert tier. It has no fallback to check `isVendorOrg(owner)`.
3. **updateSkillTrust** (`trust-updater.ts`) DOES check `isVendorOrg(skill.author)` as a fallback, but is never called during the normal publish flow -- only via admin backfill endpoints.

## Goals

- Vendor skills are correctly certified as CERTIFIED/T4 at publish time
- Existing vendor skills published before the fix are backfilled to correct cert tier
- Defense-in-depth: `publishSkill` has a fallback vendor check independent of the submission flag

## User Stories

### US-001: Mark submission as vendor before publishing (P1)
**Project**: vskill-platform

**As a** vendor organization (e.g., anthropics, openai)
**I want** my submitted skills to have `isVendor=true` set on the submission record before `publishSkill()` runs
**So that** the publish pipeline correctly assigns CERTIFIED tier, vendor labels, and T4 trust score

**Acceptance Criteria**:
- [ ] **AC-US1-01**: Given a submission from a vendor org repo (e.g., `github.com/anthropics/my-skill`), when `processSubmission` detects vendor status via `isVendorRepo()`, then the submission's `isVendor` field is set to `true` in both KV and DB before `publishSkill()` is called
- [ ] **AC-US1-02**: Given a `markVendor(id, org)` function in `submission-store.ts`, when called with a valid submission ID and org name, then it updates the KV entry's `isVendor` to `true` and persists the same to the DB submission record
- [ ] **AC-US1-03**: Given a submission from a non-vendor org (e.g., `github.com/random-user/skill`), when `processSubmission` runs, then `markVendor` is NOT called and `isVendor` remains `false`

---

### US-002: Add vendor org fallback in publishSkill (P1)
**Project**: vskill-platform

**As a** platform operator
**I want** `publishSkill()` to check `isVendorOrg(owner)` as a fallback when `sub.isVendor` is `false`
**So that** vendor skills are correctly certified even if the submission flag was not propagated (defense-in-depth)

**Acceptance Criteria**:
- [ ] **AC-US2-01**: Given a submission where `sub.isVendor` is `false` but the repo owner is a vendor org (e.g., `anthropics`), when `publishSkill()` runs, then the skill receives CERTIFIED cert tier, VENDOR_AUTO cert method, T4 trust tier, trust score 100, and labels `["vendor", "certified"]`
- [ ] **AC-US2-02**: Given a submission where `sub.isVendor` is `false` and the repo owner is NOT a vendor org, when `publishSkill()` runs, then the skill receives VERIFIED cert tier and community labels (no change from current behavior)
- [ ] **AC-US2-03**: Given a submission where `sub.isVendor` is `true`, when `publishSkill()` runs, then the existing vendor path is used (no double-checking needed, current behavior preserved)

---

### US-003: Backfill existing vendor skills (P2)
**Project**: vskill-platform

**As a** platform operator
**I want** all existing vendor skills that were published with incorrect VERIFIED status to be updated to CERTIFIED/T4
**So that** `vskill find` displays accurate certification status for all vendor skills

**Acceptance Criteria**:
- [ ] **AC-US3-01**: Given existing skills in the DB with `author` matching a vendor org and `certTier = "VERIFIED"`, when the admin backfill endpoint is invoked, then those skills are updated to `certTier = "CERTIFIED"`, `certMethod = "VENDOR_AUTO"`, `trustTier = "T4"`, `trustScore = 100`
- [ ] **AC-US3-02**: Given the backfill runs, when a vendor skill already has `certTier = "CERTIFIED"`, then it is skipped (idempotent)

## Out of Scope

- CLI (`vskill`) changes -- display logic is already correct; it reads cert tier from the API
- Database schema changes -- `isVendor` and `vendorOrg` fields already exist
- Changes to the vendor org registry (`provider-registry.ts`) -- the org list is correct
- Changes to `updateSkillTrust` -- it already handles vendor orgs correctly as a fallback

## Non-Functional Requirements

- **Reliability**: `markVendor` must update both KV and DB atomically (best-effort on DB, KV is primary for pipeline continuity)
- **Backward Compatibility**: Existing non-vendor submission and publish flows must not be affected
- **Idempotency**: Calling `markVendor` multiple times for the same submission must be safe

## Edge Cases

- **DB unavailable during markVendor**: KV update succeeds, DB update fails -- `publishSkill` fallback via `isVendorOrg(owner)` still produces correct result
- **Submission already has isVendor=true**: `markVendor` is a no-op (or safe re-write of same value)
- **Vendor org removed from registry after publish**: Already-published skills retain their CERTIFIED status; only new submissions are affected
- **Race between processSubmission and publishSkill**: Not possible -- they run sequentially within the same function call

## Risks

| Risk | Probability | Impact | Severity | Mitigation |
|------|-------------|--------|----------|------------|
| markVendor DB write fails silently | 0.2 | 3 | 0.6 | publishSkill fallback via isVendorOrg(owner) ensures correct cert tier regardless |
| Backfill updates wrong skills | 0.1 | 5 | 0.5 | Filter strictly by vendor org list; dry-run mode on admin endpoint |

## Technical Notes

- `isVendorRepo()` is re-exported from `scanner.ts` but defined in `trust/trusted-orgs.ts` as `checkVendorRepo()`
- `isVendorOrg()` accepts a lowercase org string and checks against `VENDOR_ORG_IDS` set
- `extractOwner()` in `submission-store.ts` already extracts the GitHub org from repo URL
- The vendor detection in `processSubmission` (line 269) already has the org name from `isVendorRepo()` return value -- pass it to `markVendor()`
- `publishSkill()` already calls `extractOwner(sub.repoUrl)` at line 1035 -- this value can be passed to `isVendorOrg()` for the fallback check

## Success Metrics

- All skills from vendor orgs show `certTier: "CERTIFIED"` in the API response
- `vskill find` displays "certified" badge for vendor org skills
- Zero regression in non-vendor skill certification flow
