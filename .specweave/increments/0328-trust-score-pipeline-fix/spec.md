# 0328: Fix Trust Score Calculation & Pipeline Publishing Gaps

## Problem

Homepage average trust score shows **2** instead of expected **~35-40**. Verified skills count appears stuck at ~5000. Admin-approved submissions don't create Skill records.

## User Stories

### US-001: Trust Score Display Accuracy
As a visitor, I want the average trust score to reflect actual computed values so that the metric is meaningful.

**Acceptance Criteria**:
- [x] AC-US1-01: `mapDbSkillToSkillData()` includes `trustScore`, `trustTier`, `provenanceVerified` from Prisma
- [x] AC-US1-02: Community skills from DB display their actual trust scores on homepage
- [x] AC-US1-03: Average trust score reflects real values (expected ~35-40 range)

### US-002: Trust Score Assignment on Publish
As a platform operator, I want newly published skills to receive computed trust scores so that they contribute meaningful data to the registry.

**Acceptance Criteria**:
- [x] AC-US2-01: `publishSkill()` computes trust score from scan results via `computeTrust()`
- [x] AC-US2-02: Trust score and tier are written to Prisma Skill record during upsert
- [x] AC-US2-03: A skill passing tier 1 with score 80+ gets trustScore ~40 and tier T2

### US-003: Admin Approve Creates Skill Records
As an admin, I want manually approved submissions to create visible Skill records so that they appear in the registry.

**Acceptance Criteria**:
- [x] AC-US3-01: Admin approve route calls `publishSkill()` after state transition
- [x] AC-US3-02: APPROVABLE_STATES includes `TIER1_FAILED` and `REJECTED` for admin override
- [x] AC-US3-03: Expired KV records (7-day TTL) are reconstructed from Prisma data before publishing

### US-004: Remove Artificial Result Cap
As a platform operator, I want all published skills returned by queries so that metrics are accurate.

**Acceptance Criteria**:
- [x] AC-US4-01: `take: 5000` safety cap raised to 50000 in `getPublishedSkillsFromDb()`

### US-005: Trust Score Backfill
As a platform operator, I want existing community skills to have correct trust scores so that the average reflects reality.

**Acceptance Criteria**:
- [x] AC-US5-01: Admin endpoint exists to backfill trust scores for existing skills
- [x] AC-US5-02: Published skills that passed tier 1 get baseline score ~40, tier T2
- [x] AC-US5-03: Backfill is idempotent and processes in batches
