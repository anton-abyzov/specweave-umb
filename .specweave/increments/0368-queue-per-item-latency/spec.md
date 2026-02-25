---
increment: 0368-queue-per-item-latency
title: "Queue Per-Item Latency Optimization"
type: performance
priority: P1
status: completed
created: 2026-02-24
structure: user-stories
test_mode: test-after
coverage_target: 80
---

# Feature: Queue Per-Item Latency Optimization

## Overview

Each submission processed through the queue pipeline incurs ~25-35 KV round-trips and sequential awaits on non-critical telemetry. This increment targets 6 optimizations to reduce per-item wall-clock time by ~1.3-2.2 seconds (20-50% on the fast path).

Complementary to 0356 (infrastructure scaling — wider pipe). This increment makes each item flow faster.

## User Stories

### US-001: Fire-and-Forget Metrics and Scan Log (P1)
**Project**: vskill-platform

**As a** platform operator
**I want** metrics and scan log recording to not block message acknowledgment
**So that** per-item processing latency is reduced by ~400-700ms

**Acceptance Criteria**:
- [x] **AC-US1-01**: `recordProcessed`, `recordFailed`, `recordTimeout` calls in `consumer.ts` are fire-and-forget (no `await`)
- [x] **AC-US1-02**: `writeScanLog` calls in `consumer.ts` are fire-and-forget (no `await`)
- [x] **AC-US1-03**: All fire-and-forget calls have `.catch(() => {})` to suppress unhandled rejections
- [x] **AC-US1-04**: Message `ack()`/`retry()` happens immediately after processing, not after telemetry

---

### US-002: Merge setContentHash into storeScanResult (P1)
**Project**: vskill-platform

**As a** platform operator
**I want** content hash to be stored in the same KV write as the scan result
**So that** 2 redundant KV round-trips are eliminated per submission

**Acceptance Criteria**:
- [x] **AC-US2-01**: `storeScanResult` accepts optional `contentHash` parameter
- [x] **AC-US2-02**: When `contentHash` is provided, `storeScanResult` sets `contentHashAtScan` on the submission record during its existing read-modify-write
- [x] **AC-US2-03**: Standalone `setContentHash` call is removed from `processSubmission`
- [x] **AC-US2-04**: Exported `setContentHash` function retained for backward compatibility

---

### US-003: Cache detectBranch in KV (P1)
**Project**: vskill-platform

**As a** platform operator
**I want** GitHub branch detection results to be cached in KV
**So that** redundant GitHub API calls are eliminated for same-repo submissions

**Acceptance Criteria**:
- [x] **AC-US3-01**: `detectBranch` checks KV cache key `branch:{owner}/{repo}` before calling GitHub API
- [x] **AC-US3-02**: On cache miss, result is written to KV with 1-hour TTL
- [x] **AC-US3-03**: KV access uses `getWorkerEnv()` fallback to `getCloudflareContext()` (same as `getKV()`)
- [x] **AC-US3-04**: If KV read fails, falls through to GitHub API (graceful degradation)

---

### US-004: Parallelize getMetricsWindow Reads (P2)
**Project**: vskill-platform

**As a** platform operator
**I want** the admin dashboard metrics to load faster
**So that** the 24 sequential KV reads are parallelized

**Acceptance Criteria**:
- [x] **AC-US4-01**: `getMetricsWindow` uses `Promise.all` instead of sequential loop for 24 hourly bucket reads
- [x] **AC-US4-02**: Totals read is included in the parallel batch

---

### US-005: Batch updateState for Publish Flow (P1)
**Project**: vskill-platform

**As a** platform operator
**I want** sequential state transitions (AUTO_APPROVED → PUBLISHED) to be batched
**So that** 4 KV reads + 4 KV writes are reduced to 2+2

**Acceptance Criteria**:
- [x] **AC-US5-01**: New `updateStateMulti` function accepts array of `{state, message}` transitions
- [x] **AC-US5-02**: Single KV read/write cycle for submission + history
- [x] **AC-US5-03**: DB persistence fires per-transition (best-effort, as before)
- [x] **AC-US5-04**: `processSubmission` uses `updateStateMulti` for AUTO_APPROVED→PUBLISHED sequences

---

### US-006: Parallelize Enrichment Batch (P2)
**Project**: vskill-platform

**As a** platform operator
**I want** the enrichment cron to process skills in parallel chunks
**So that** total cron execution time is reduced ~5x

**Acceptance Criteria**:
- [x] **AC-US6-01**: Skills are processed in chunks of 10 using `Promise.allSettled`
- [x] **AC-US6-02**: Error counting remains accurate per-skill
- [x] **AC-US6-03**: Trending score recomputation still runs after all chunks complete

## Out of Scope

- Queue config changes (covered by 0356)
- Tier 2 LLM model changes
- Schema/migration changes
- API contract changes
