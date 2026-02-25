# Tasks: Fix Homepage Categories & Trending Momentum

## Phase 1: Shared Formula Module

### T-001: Create trending-formula.ts
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-04 | **Status**: [ ] pending
**Test**: Given buildTrendingScoreUpdateSql() is called → When result inspected → Then returns Prisma.Sql with LN-based scoring, both 7d and 30d fields

**File**: `src/lib/trending-formula.ts`
- Export `buildTrendingScoreUpdateSql()` returning `Prisma.Sql`
- Use `LN(1 + value)` scaling for stars, npm, installs
- Keep `LEAST(100, GREATEST(0, ...))` as safety clamp
- 7d coefficients: stars×5, npm×2, installs×3, created-bonus +5, commit-bonus +3
- 30d coefficients: stars×4.5, npm×1.8, installs×2.7, created-bonus +3, commit-bonus +2

### T-002: Add trending-formula unit test
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01 | **Status**: [ ] pending
**Test**: Given test file → When vitest runs → Then validates Prisma.Sql instance, LN presence, both score fields

**File**: `src/lib/__tests__/trending-formula.test.ts`

## Phase 2: Integration

### T-003: Update enrichment.ts to use shared formula
**User Story**: US-002 | **Satisfies ACs**: AC-US2-05 | **Status**: [ ] pending
**Test**: Given enrichment batch runs → When SQL UPDATE executes → Then uses shared formula from trending-formula.ts

**File**: `src/lib/cron/enrichment.ts` (lines 93-108)
- Import `buildTrendingScoreUpdateSql`
- Replace inline SQL template with `db.$executeRaw(buildTrendingScoreUpdateSql())`

### T-004: Update admin/enrich route to use shared formula
**User Story**: US-002 | **Satisfies ACs**: AC-US2-05 | **Status**: [ ] pending
**Test**: Given admin enrich endpoint called → When SQL UPDATE executes → Then uses shared formula

**File**: `src/app/api/v1/admin/enrich/route.ts` (lines 98-113)
- Import `buildTrendingScoreUpdateSql`
- Replace inline SQL template with `db.$executeRaw(buildTrendingScoreUpdateSql())`

### T-005: Adjust MomentumArrow thresholds
**User Story**: US-002 | **Satisfies ACs**: AC-US2-03 | **Status**: [ ] pending
**Test**: Given log-scaled deltas (~2-6 range) → When MomentumArrow renders → Then shows up/down arrows (not flat)

**File**: `src/app/components/charts/MomentumArrow.tsx`
- Change `delta > 1` → `delta > 0.5`
- Change `delta < -1` → `delta < -0.5`

### T-006: Fix computeMinimalStats category recovery
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02, AC-US1-03 | **Status**: [ ] pending
**Test**: Given computeMinimalStats runs → When category groupBy succeeds → Then categories array populated (not empty)

**File**: `src/lib/stats-compute.ts`
- Add try/catch category groupBy query before return statement
- Add try/catch topStarRepos query via safeTopStarRepos()
- Replace hard-coded `categories: []` and `topStarRepos: []` with recovered variables

## Phase 3: Verification

### T-007: Run tests and build
**Status**: [ ] pending
- Run vitest for trending-formula and enrichment tests
- Full build: `npm run db:generate && npm run build && npm run build:worker`

### T-008: Deploy and verify
**Status**: [ ] pending
- Deploy: `npm run deploy`
- Trigger admin enrich to recompute scores with new formula
- Verify homepage: categories populated, momentum arrows showing varied deltas
