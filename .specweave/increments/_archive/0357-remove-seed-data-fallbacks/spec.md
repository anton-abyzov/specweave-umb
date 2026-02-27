# 0357: Remove Seed Data Fallbacks

## Problem

The vskill-platform `data.ts` still falls back to a 3,756-line `seed-data.ts` when the database is unreachable at build time. All 118 skills are in PostgreSQL via Prisma — the seed fallback is dead code in production (`CF_PAGES` guard), creates false reliability, and keeps stale data bundled. The hardcoded trending scores (`trendingScore7d`, `trendingScore30d`) are meaningless — overwritten by the enrichment cron immediately.

## User Stories

### US-001: Clean data layer
As a developer, I want the data layer to only read from the database so that there is one clear data path and failures are visible instead of silently returning stale seed data.

**Acceptance Criteria:**
- [x] AC-US1-01: All 6 skill-fetching functions in `data.ts` return empty results (not seed data) when DB is unreachable
- [x] AC-US1-02: `applyFiltersInMemory()` helper is deleted (only used by seed fallback)
- [x] AC-US1-03: No dynamic `import("./seed-data")` remains in `data.ts`
- [x] AC-US1-04: Agent functions (`getAgents`, `getUniversalAgents`, `getAgentCount`) still work from static import (unchanged)

### US-002: Remove seed count from health check
As an operator, I want the health endpoint to compare DB vs KV counts only so that drift detection is meaningful.

**Acceptance Criteria:**
- [x] AC-US2-01: Health check route no longer imports `seed-data`
- [x] AC-US2-02: `seed_count` field removed from health response
- [x] AC-US2-03: Health check test updated

### US-003: Consolidate seed scripts
As a developer, I want a single seed script so that fresh deployments use one clear path.

**Acceptance Criteria:**
- [x] AC-US3-01: `scripts/seed-skills.ts` deleted
- [x] AC-US3-02: `scripts/seed-skills-to-db.ts` deleted
- [x] AC-US3-03: `prisma/seed.ts` remains as the single seed script

### US-004: Simplify seed-data.ts
As a developer, I want seed-data.ts to contain only stable fields so that volatile metrics don't create confusion.

**Acceptance Criteria:**
- [x] AC-US4-01: `trendingScore7d` and `trendingScore30d` removed from all 118 skill entries
- [x] AC-US4-02: Fields made optional in seed type or defaulted in `prisma/seed.ts`
- [x] AC-US4-03: `seed-data-trending.test.ts` deleted (tests removed fields)

### US-005: Update tests
As a developer, I want tests to reflect the DB-first reality so that they test real behavior.

**Acceptance Criteria:**
- [x] AC-US5-01: `data.test.ts` skill tests verify empty-state fallback (not seed data)
- [x] AC-US5-02: `data-prisma.test.ts` stale merge assumptions removed
- [x] AC-US5-03: All tests pass after changes

## Out of Scope
- Agent data migration to DB (separate concern)
- Trending formula changes (increment 0353)
- Data freshness/reliability (increment 0354)
