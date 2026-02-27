# Plan: 0328 Trust Score & Pipeline Fix

## Architecture

All changes are in `repositories/anton-abyzov/vskill-platform/src/`.

### T-001: data.ts mapDbSkillToSkillData()
Add `trustScore`, `trustTier`, `provenanceVerified` to return object (lines 76-101).

### T-002: submission-store.ts publishSkill()
Import `computeTrust`/`TrustInputs` from `./trust/trust-score`. Build TrustInputs from StoredScanResult fields (tier1Verdict from verdict, tier2Score, tier2Verdict). Add trustScore/trustTier to db.skill.upsert create+update.

### T-003: admin approve route
Import publishSkill + getSubmission. Expand APPROVABLE_STATES with TIER1_FAILED, REJECTED. After Prisma Submission update: check KV sub record, reconstruct if expired, call publishSkill(id).

### T-004: data.ts getPublishedSkillsFromDb()
Change `take: 5000` to `take: 50000`.

### T-005: trust-backfill route (new)
POST /api/v1/admin/trust-backfill. Requires SUPER_ADMIN. Query skills with trustScore=0, batch update with baseline trust (tier1 PASS + clean community = ~40, T2).

### T-006: Tests
Update dual-publish.test.ts assertions to verify trustScore/trustTier in upsert calls.
