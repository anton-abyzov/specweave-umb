# Tasks: Crawl Pipeline Throughput Optimization

## Phase 1: Core Changes (P1)

### T-001: Reduce pending-submissions age filter
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03 | **Status**: [x] completed
**File**: `src/app/api/v1/internal/pending-submissions/route.ts`
- Changed 5-minute hardcoded filter to configurable `PENDING_AGE_SECONDS` (default: 30s)
- VMs now pick up items 10x faster (30s vs 5min)

### T-002: Increase CF Queue concurrency
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03 | **Status**: [x] completed
**Files**: `wrangler.jsonc`, `src/lib/queue/consumer.ts`
- `max_concurrency` 3 → 10
- `BATCH_CONCURRENCY` 1 → 3
- Effective concurrent submissions: up to 30 (10 batches x 3 per batch)

### T-003: Create TokenRotator utility
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04 | **Status**: [x] completed
**File**: `src/lib/token-rotator.ts` (new)
- Round-robin rotation across comma-separated GitHub PATs
- Integrated into CF Queue consumer (`consumer.ts`)
- Falls back to single `GITHUB_TOKEN` for backward compatibility

## Phase 2: Feature Flag + Dedup (P2)

### T-004: Add SKIP_QUEUE_ENQUEUE feature flag
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-04, AC-US4-05 | **Status**: [x] completed
**Files**: `submissions/route.ts`, `submissions/bulk/route.ts`, `enqueue-submissions/route.ts`
- When `SKIP_QUEUE_ENQUEUE=true` (default), CF Queue is bypassed
- Items stay in RECEIVED state for VM pickup
- Set via `wrangler secret put SKIP_QUEUE_ENQUEUE true`

### T-005: Per-state staleness windows
**User Story**: US-006 | **Satisfies ACs**: AC-US6-01, AC-US6-02, AC-US6-03, AC-US6-04, AC-US6-05, AC-US6-06 | **Status**: [x] completed
**File**: `src/lib/submission-dedup.ts`
- Published: 24h (re-scan for security updates)
- Rejected: 48h (retry transient failures)
- Blocked: never (permanent)
- Default: 72h (backward compatible)

### T-006: Re-scannable rejected submissions
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01, AC-US5-02, AC-US5-03 | **Status**: [x] completed
**File**: `src/lib/submission-dedup.ts`
- `checkSubmissionDedup` and `checkSubmissionDedupBatch` return `kind: "new"` for stale rejected
- BLOCKED remains permanent (never re-scannable)

## Phase 3: Deployment

### T-007: Update env.d.ts
**Status**: [x] completed
**File**: `src/lib/env.d.ts`
- Added: `SKIP_QUEUE_ENQUEUE`, `PENDING_AGE_SECONDS`, staleness env vars

### T-008: Deploy to Cloudflare Workers
**Status**: [x] completed
- Build + deploy successful
- Secrets set: `SKIP_QUEUE_ENQUEUE=true`, `PENDING_AGE_SECONDS=30`
- Platform healthy: 15,205 skills, 9,089 repos
