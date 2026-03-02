---
increment: 0393-crawl-pipeline-throughput
title: Crawl Pipeline Throughput Optimization
type: feature
priority: P1
status: completed
created: 2026-03-01T00:00:00.000Z
structure: user-stories
test_mode: test-after
coverage_target: 80
---

# Feature: Crawl Pipeline Throughput Optimization

## Overview

The crawl pipeline currently processes submissions through two paths: Hetzner VMs running `submission-scanner.js` (primary) and Cloudflare Queue consumer (secondary). Several bottlenecks limit throughput:

1. **5-minute age filter** on `pending-submissions` endpoint causes race conditions and unnecessary delays
2. **CF Queue consumer** runs at `max_concurrency=3` and `BATCH_CONCURRENCY=1`, artificially limiting parallelism
3. **Single GitHub token** in CF Worker `consumer.ts` limits API rate to 5000 req/hr per token
4. **Rejected submissions** are permanently blocked from re-scanning despite transient failure causes
5. **Flat staleness window** (72h for all states) doesn't match different freshness needs per state
6. **Queue enqueue** always sends to CF Queue even though VMs handle the work, wasting queue resources

This increment optimizes the pipeline by reducing the age filter, increasing CF Queue concurrency, adding multi-token rotation to the CF Worker, making rejected submissions re-scannable, implementing per-state staleness windows, and adding a feature flag to skip CF Queue enqueue when VMs are handling submissions.

## User Stories

### US-001: Reduce Pending Submission Age Filter (P1)
**Project**: vskill-platform

**As a** platform operator
**I want** the pending-submissions endpoint to return items after 30 seconds instead of 5 minutes
**So that** VMs can pick up and process new submissions much faster, reducing end-to-end latency

**Acceptance Criteria**:
- [x] **AC-US1-01**: `pending-submissions/route.ts` uses a 30-second age filter (`updatedAt < 30 seconds ago`) instead of the current 5-minute filter
- [x] **AC-US1-02**: The age filter value is configurable via an environment variable `PENDING_AGE_SECONDS` (default: 30) for operational flexibility
- [x] **AC-US1-03**: Existing tests for the pending-submissions endpoint pass with the updated filter value

---

### US-002: Increase CF Queue Concurrency (P1)
**Project**: vskill-platform

**As a** platform operator
**I want** the Cloudflare Queue consumer to process more submissions in parallel
**So that** queue drain time decreases and throughput increases when the CF path is active

**Acceptance Criteria**:
- [x] **AC-US2-01**: `wrangler.jsonc` sets `max_concurrency` to 10 for the `submission-processing` queue consumer
- [x] **AC-US2-02**: `consumer.ts` sets `BATCH_CONCURRENCY` to 3 (up from 1)
- [x] **AC-US2-03**: `max_batch_size` remains at 5 (no change needed)
- [x] **AC-US2-04**: The consumer handles concurrent processing failures gracefully without corrupting submission state

---

### US-003: Multi-Token GitHub Support in CF Worker (P1)
**Project**: vskill-platform

**As a** platform operator
**I want** the CF Worker consumer to support multiple GitHub PATs via comma-separated `GITHUB_TOKENS` env var
**So that** rate limits are distributed across 3-5 tokens, increasing effective throughput from 5000 to 15000-25000 req/hr

**Acceptance Criteria**:
- [x] **AC-US3-01**: `consumer.ts` reads `GITHUB_TOKENS` (comma-separated) from env, falling back to `GITHUB_TOKEN` (single) for backward compatibility
- [x] **AC-US3-02**: A `TokenRotator` utility is created in `src/lib/token-rotator.ts` that round-robin rotates through available tokens
- [x] **AC-US3-03**: The rotator is passed to `processSubmission` via the `githubToken` option, providing a fresh token per submission
- [x] **AC-US3-04**: `env.d.ts` is updated to declare the `GITHUB_TOKENS` binding
- [x] **AC-US3-05**: `.env.example` in `crawl-worker/` documents the `GITHUB_TOKENS` format (already present, verify accuracy)

---

### US-004: Feature Flag to Skip CF Queue Enqueue (P2)
**Project**: vskill-platform

**As a** platform operator
**I want** a feature flag `SKIP_QUEUE_ENQUEUE` that prevents submissions from being sent to the CF Queue
**So that** when VMs are handling all work, we avoid unnecessary queue operations and can re-enable the CF Queue path as a fallback if VMs go down

**Acceptance Criteria**:
- [x] **AC-US4-01**: `submissions/route.ts` (POST handler) checks `SKIP_QUEUE_ENQUEUE` env var before calling `SUBMISSION_QUEUE.send()` or `sendBatch()`
- [x] **AC-US4-02**: When `SKIP_QUEUE_ENQUEUE` is truthy (default: "true"), the queue send is skipped entirely; submissions remain in RECEIVED state for VM pickup
- [x] **AC-US4-03**: When `SKIP_QUEUE_ENQUEUE` is falsy or unset, the existing CF Queue path works unchanged (backward compatible)
- [x] **AC-US4-04**: `env.d.ts` is updated to declare the `SKIP_QUEUE_ENQUEUE` binding
- [x] **AC-US4-05**: The `enqueue-submissions/route.ts` endpoint (called by queue-processor) also respects `SKIP_QUEUE_ENQUEUE` to prevent the queue-processor from re-enqueuing items

---

### US-005: Re-Scannable Rejected Submissions (P2)
**Project**: vskill-platform

**As a** platform operator
**I want** rejected submissions to be eligible for re-scanning after a configurable cooldown period
**So that** submissions rejected due to transient issues (rate limits, temporary scan failures) can be automatically retried without manual intervention

**Acceptance Criteria**:
- [x] **AC-US5-01**: `submission-dedup.ts` treats `kind: "rejected"` as `kind: "new"` when the submission's `updatedAt` exceeds the configured staleness window for rejected state
- [x] **AC-US5-02**: BLOCKED submissions remain permanently blocked (never re-scannable via dedup staleness)
- [x] **AC-US5-03**: The `checkSubmissionDedupBatch` function also applies the same re-scan logic for rejected submissions
- [x] **AC-US5-04**: Existing dedup tests are updated to cover the rejected-re-scan path

---

### US-006: Per-State Staleness Configuration (P2)
**Project**: vskill-platform

**As a** platform operator
**I want** per-state staleness windows configurable via environment variables
**So that** published skills are re-scanned more frequently (24h) than rejected ones (48h), with a sensible default fallback (72h)

**Acceptance Criteria**:
- [x] **AC-US6-01**: `submission-dedup.ts` reads `DEDUP_STALE_PUBLISHED_HOURS` (default: 24), `DEDUP_STALE_REJECTED_HOURS` (default: 48), and `DEDUP_STALE_DEFAULT_HOURS` (default: 72) from environment
- [x] **AC-US6-02**: The existing single `DEDUP_STALE_HOURS` env var is replaced by the per-state variables; backward compatibility is maintained by using `DEDUP_STALE_DEFAULT_HOURS` as the fallback
- [x] **AC-US6-03**: The `isStale()` function accepts a state parameter and applies the corresponding staleness window
- [x] **AC-US6-04**: Published skills with a linked Skill record are re-scanned after `DEDUP_STALE_PUBLISHED_HOURS` (24h default)
- [x] **AC-US6-05**: Rejected/DEQUEUED/TIER1_FAILED submissions are re-scannable after `DEDUP_STALE_REJECTED_HOURS` (48h default)
- [x] **AC-US6-06**: All other states use `DEDUP_STALE_DEFAULT_HOURS` (72h default)

## Functional Requirements

### FR-001: Age Filter Reduction
Change the `pending-submissions` route to use a 30-second age threshold instead of 5 minutes. This prevents race conditions where multiple VMs pick up the same submission (the `claim-submission` endpoint handles atomic claiming), while reducing the delay from submission creation to first processing attempt.

### FR-002: CF Queue Concurrency Tuning
Update `wrangler.jsonc` to set `max_concurrency=10` and `consumer.ts` to set `BATCH_CONCURRENCY=3`. With `max_batch_size=5`, this yields up to 10 concurrent consumer invocations, each processing 3 submissions in parallel = 30 effective concurrent submissions through the CF path (when enabled).

### FR-003: Token Rotation in CF Worker
Create a `TokenRotator` class in `src/lib/token-rotator.ts` that accepts a comma-separated string of PATs and provides a `next()` method for round-robin selection. The consumer creates a single rotator instance per batch and passes tokens to each `processSubmission` call. This matches the existing pattern in `crawl-worker/sources/*.js` files.

### FR-004: SKIP_QUEUE_ENQUEUE Feature Flag
Add `SKIP_QUEUE_ENQUEUE` as a Cloudflare secret (default "true"). When set, `submissions/route.ts` skips `SUBMISSION_QUEUE.send()` / `sendBatch()` calls. Submissions stay in RECEIVED state and are picked up by VMs via `pending-submissions`. If VMs go down, set `SKIP_QUEUE_ENQUEUE` to empty/false to re-enable the CF Queue path.

### FR-005: Per-State Dedup Staleness
Refactor `submission-dedup.ts` to replace the flat `DEDUP_STALE_HOURS` with per-state windows. The `isStale()` function signature changes to `isStale(updatedAt: Date, state: string): boolean`. Each state maps to its own environment variable with a sensible default.

## Success Criteria

- Submission pickup latency reduced from ~5 minutes to ~30 seconds
- CF Queue throughput increased by ~10x when CF path is active (from 3 to 30 concurrent submissions)
- GitHub API rate headroom increased 3-5x via multi-token rotation
- Rejected submissions automatically retried after 48h without manual intervention
- Published skills re-scanned for security updates every 24h
- No regression in existing submission processing correctness

## Out of Scope

- Deprecating or removing the `queue-processor.js` source (kept as-is)
- Changes to Tier 1 or Tier 2 scan logic
- Changes to the VM scheduler or `ASSIGNED_SOURCES` configuration
- Provisioning new GitHub PATs (operational task, not code change)
- Changes to the DLQ consumer or recovery cron logic

## Dependencies

- **Cloudflare Workers**: `wrangler.jsonc` changes require a deploy
- **Cloudflare Secrets**: `GITHUB_TOKENS`, `SKIP_QUEUE_ENQUEUE`, staleness env vars must be set via `wrangler secret put` or wrangler.jsonc vars
- **VM .env files**: Staleness env vars may also need to be set on VMs if crawl-worker sources reference them (they currently don't -- dedup runs server-side only)
