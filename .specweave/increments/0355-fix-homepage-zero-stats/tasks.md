# Tasks: Fix Homepage Zero Stats

## Phase 1: Core Stats Fix (P0)

### T-001: Fix computeMinimalStats to compute real stats
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-04 | **Status**: [x] completed
**File**: `repositories/anton-abyzov/vskill-platform/src/lib/stats-compute.ts`
**Test**: Given computeFullStats fails → When computeMinimalStats runs → Then individual queries return real data with per-query try/catch

### T-002: Increase DB timeout for full stats computation
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02 | **Status**: [x] completed
**File**: `repositories/anton-abyzov/vskill-platform/src/lib/stats-compute.ts`
**Test**: Given cold Neon DB → When 12 parallel queries run → Then 25s timeout provides enough headroom

### T-003: Add structured error logging to stats computation
**User Story**: US-001 | **Satisfies ACs**: AC-US1-03 | **Status**: [x] completed
**File**: `repositories/anton-abyzov/vskill-platform/src/lib/stats-compute.ts`
**Test**: Given computeFullStats throws → When error is caught → Then error message and stack trace are logged

## Phase 2: Enrichment Pipeline Fix (P0)

### T-004: Fix enrichment starvation — always advance updatedAt
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01 | **Status**: [x] completed
**File**: `repositories/anton-abyzov/vskill-platform/src/lib/cron/enrichment.ts`
**Test**: Given skill with no valid GitHub URL → When enrichment runs → Then updatedAt is still advanced

### T-005: Increase enrichment batch size to 50
**User Story**: US-002 | **Satisfies ACs**: AC-US2-02 | **Status**: [x] completed
**File**: `repositories/anton-abyzov/vskill-platform/src/lib/cron/enrichment.ts`

### T-006: Add recency boost to trending score formula
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02 | **Status**: [x] completed
**File**: `repositories/anton-abyzov/vskill-platform/src/lib/cron/enrichment.ts`
**Test**: Given newly created skill with 0 stars → When trending scores computed → Then score > 0 due to recency boost

## Phase 3: Cron & Observability (P1)

### T-007: Isolate stats refresh in cron + add timing logs + remove KV TTL
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02, AC-US4-03 | **Status**: [x] completed
**Files**: `scripts/build-worker-entry.ts`, `src/lib/cron/stats-refresh.ts`

## Phase 4: Admin Endpoints (P1-P2)

### T-008: Add admin bulk enrichment endpoint
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01, AC-US5-02, AC-US5-03, AC-US5-04 | **Status**: [x] completed
**File**: `repositories/anton-abyzov/vskill-platform/src/app/api/v1/admin/enrich/route.ts` (NEW)

### T-009: Add stats health check endpoint
**User Story**: US-006 | **Satisfies ACs**: AC-US6-01, AC-US6-02 | **Status**: [x] completed
**File**: `repositories/anton-abyzov/vskill-platform/src/app/api/v1/stats/health/route.ts` (NEW)
