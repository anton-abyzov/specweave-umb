# Tasks: 0328 Trust Score & Pipeline Fix

### T-001: Add trust fields to mapDbSkillToSkillData()
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03 | **Status**: [x] completed
**Test**: Given a Prisma Skill record with trustScore=40 and trustTier="T2" → When mapped via mapDbSkillToSkillData() → Then the returned SkillData has trustScore=40 and trustTier="T2"

### T-002: Compute and write trust score in publishSkill()
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03 | **Status**: [x] completed
**Test**: Given a scan result with verdict="PASS" and score=92 → When publishSkill() upserts to Prisma → Then the Skill record has trustScore ~40 and trustTier="T2"

### T-003: Fix admin approve to call publishSkill()
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03 | **Status**: [x] completed
**Test**: Given an AUTO_APPROVED submission → When admin approves → Then a Skill record is created in Prisma AND expired KV records are reconstructed

### T-004: Raise take:5000 cap
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01 | **Status**: [x] completed
**Test**: Given >5000 skills in DB → When getPublishedSkillsFromDb() is called → Then all skills are returned

### T-005: Create trust-backfill admin endpoint
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01, AC-US5-02, AC-US5-03 | **Status**: [x] completed
**Test**: Given 100 skills with trustScore=0 → When POST /api/v1/admin/trust-backfill → Then all 100 get trustScore ~40 and trustTier="T2"

### T-006: Update tests for all changes
**User Story**: US-001, US-002, US-003 | **Satisfies ACs**: AC-US1-01, AC-US2-02 | **Status**: [x] completed
**Test**: Given updated code → When vitest runs → Then all existing tests pass AND new assertions verify trustScore/trustTier in upsert
