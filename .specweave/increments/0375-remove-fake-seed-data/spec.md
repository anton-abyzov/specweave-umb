---
increment: 0375-remove-fake-seed-data
title: Remove fake seed data from vskill-platform
type: refactor
priority: P1
status: completed
created: 2026-02-25T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 80
---

# Feature: Remove fake seed data from vskill-platform

## Overview

The vskill-platform `seed-data.ts` (4681 lines) contains 156 hardcoded fake skill entries used for initial development. Now that the platform has a real submission pipeline and enrichment cron, these fake skills pollute the production database and inflate metrics. This increment removes all fake skill data, renames the file to `agent-data.ts` (keeping only the 44 real agent entries), updates the Prisma seed script to stop seeding fake skills, hardens enrichment 404 handling for deleted repos, writes a DB cleanup script to purge seeded rows, and updates all affected tests.

## User Stories

### US-001: Remove fake skill seed data (P1)
**Project**: vskill-platform

**As a** platform operator
**I want** all 156 hardcoded fake skills removed from the seed data file
**So that** the database only contains skills that came through the real submission/scanning pipeline

**Acceptance Criteria**:
- [x] **AC-US1-01**: `seed-data.ts` is renamed to `agent-data.ts` and contains ONLY the `agents` array (44 entries) and `AgentData` type re-export
- [x] **AC-US1-02**: The `skills` export, `SeedSkillData` type, and all 156 skill objects are deleted from the file
- [x] **AC-US1-03**: All imports of `seed-data` across the codebase are updated to `agent-data`
- [x] **AC-US1-04**: `data.ts` imports `agents` from `./agent-data` instead of `./seed-data`
- [x] **AC-US1-05**: `agent-branding.ts` comment referencing `seed-data` is updated

---

### US-002: Update Prisma seed script (P1)
**Project**: vskill-platform

**As a** platform developer
**I want** the Prisma seed script updated to only seed admins, blocklist, and agent compat data
**So that** running `prisma db seed` no longer inserts fake skills into the database

**Acceptance Criteria**:
- [x] **AC-US2-01**: `prisma/seed.ts` no longer imports `skills` from the data file
- [x] **AC-US2-02**: `prisma/seed.ts` imports `agents` from `../src/lib/agent-data`
- [x] **AC-US2-03**: The skill upsert loop and skill version creation are removed from seed.ts
- [x] **AC-US2-04**: The `SKILL_NAME_RENAMES` migration map is removed (no longer needed)
- [x] **AC-US2-05**: Admin seeding and blocklist seeding continue to work unchanged
- [x] **AC-US2-06**: Agent compat records can still be seeded against existing DB skills (not fake ones)

---

### US-003: Harden enrichment 404 handling (P1)
**Project**: vskill-platform

**As a** platform operator
**I want** the enrichment cron to handle GitHub 404s more robustly for skills with deleted/invalid repos
**So that** 404 responses are tracked and skills with persistently dead repos can be flagged

**Acceptance Criteria**:
- [x] **AC-US3-01**: When enrichment encounters a GitHub 404, it increments a `repo404Count` counter on the skill record
- [x] **AC-US3-02**: When `repo404Count` reaches a configurable threshold (default: 3), the skill's `isDeprecated` flag is set to `true` with a deprecation reason
- [x] **AC-US3-03**: A successful GitHub response (200) resets `repo404Count` to 0
- [x] **AC-US3-04**: The enrichment test suite has tests for 404 counter increment, threshold deprecation, and counter reset on success
- [x] **AC-US3-05**: The existing "does NOT auto-deprecate on single 404" test is updated to reflect the counter-based approach

---

### US-004: Write DB cleanup script (P1)
**Project**: vskill-platform

**As a** platform operator
**I want** a one-time DB cleanup script that removes all seeded fake skills from production
**So that** the production database only contains real pipeline-verified skills

**Acceptance Criteria**:
- [x] **AC-US4-01**: A `scripts/cleanup-seed-skills.ts` script is created that identifies and deletes skills matching the old seed data IDs/names
- [x] **AC-US4-02**: The script deletes associated `SkillVersion`, `AgentCompat`, and `MetricsSnapshot` records in the correct order (foreign key dependencies)
- [x] **AC-US4-03**: The script runs in dry-run mode by default (requires `--execute` flag to actually delete)
- [x] **AC-US4-04**: The script outputs a count of records that would be / were deleted
- [x] **AC-US4-05**: The script handles the case where some seed skills may have been replaced by real pipeline entries (skip those)

---

### US-005: Update tests (P1)
**Project**: vskill-platform

**As a** platform developer
**I want** all tests updated to reflect the removal of fake seed data
**So that** the test suite passes cleanly after the refactor

**Acceptance Criteria**:
- [x] **AC-US5-01**: `seed-data-accuracy.test.ts` is deleted (it validates the now-removed fake skill data)
- [x] **AC-US5-02**: `data.test.ts` mock path updated from `../seed-data` to `../agent-data`
- [x] **AC-US5-03**: `popularity-fetcher.test.ts` seed data import test (TC-021) is removed or updated
- [x] **AC-US5-04**: `data-enrichment.test.ts` continues to pass (no dependency on seed skills)
- [x] **AC-US5-05**: Enrichment cron tests are updated with new 404 counter tests (US-003)
- [x] **AC-US5-06**: All existing tests pass after the refactor

## Functional Requirements

### FR-001: File rename preserves git history
The rename from `seed-data.ts` to `agent-data.ts` should be done via `git mv` to preserve file history.

### FR-002: Agent data structure unchanged
The `agents` array and `AgentData` type interface must remain identical after the refactor. No agent entries are added, removed, or modified.

### FR-003: DB cleanup script is idempotent
Running the cleanup script multiple times must be safe (no errors on missing records).

### FR-004: Prisma schema change for repo404Count
A new optional `repo404Count Int @default(0)` field is needed on the Skill model for 404 tracking.

## Success Criteria

- `seed-data.ts` deleted, `agent-data.ts` exists with only agents (~50 lines vs 4681)
- `npx prisma db seed` succeeds and seeds only admins + blocklist + agent compat
- All tests pass (`npm test`)
- Cleanup script runs in dry-run against production DB showing count of fake skills to remove
- Enrichment handles GitHub 404s with counter-based deprecation

## Out of Scope

- Migrating agent data to the database (agents remain static)
- Changing the enrichment cron schedule
- Modifying the submission pipeline
- Removing the blocklist seed data

## Dependencies

- Prisma migration for `repo404Count` field (US-003)
- Production DB access for cleanup script execution (US-004)
