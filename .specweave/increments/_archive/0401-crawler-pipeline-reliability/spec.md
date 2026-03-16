---
increment: 0401-crawler-pipeline-reliability
title: Crawler Pipeline Reliability and Guardrails
type: bug
priority: P1
status: completed
created: 2026-03-02T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Crawler Pipeline Reliability and Guardrails

## Overview

The discovery pipeline has five critical reliability issues causing data loss, timeouts, and silent failures across Hetzner VMs. This increment fixes each bug and adds health monitoring guardrails to prevent regressions.

**Target throughput**: 2,000-3,000 submissions per 30 minutes (combined across all sources).

## User Stories

### US-001: GitHub-Sharded Timeout Recovery (P1)
**Project**: vskill-platform

**As a** platform operator
**I want** github-sharded crawls to checkpoint progress and resume from where they left off
**So that** the 490-shard "full" mode completes across multiple scheduler cycles instead of timing out and restarting from scratch

**Acceptance Criteria**:
- [x] **AC-US1-01**: Crawl state (last completed shard index, seenRepos set) is persisted to a JSON file at a configurable state directory after each shard completes
- [x] **AC-US1-02**: On startup, if a checkpoint file exists and is less than 24 hours old, the crawl resumes from the last completed shard index
- [x] **AC-US1-03**: The seenRepos set is restored from checkpoint so cross-shard dedup still works after resumption
- [x] **AC-US1-04**: When all shards complete successfully, the checkpoint file is deleted (clean slate for next cycle)
- [x] **AC-US1-05**: Stale checkpoints (>24 hours old) are ignored and a fresh crawl starts

---

### US-002: Skills.sh Page Resumption (P1)
**Project**: vskill-platform

**As a** platform operator
**I want** skills-sh crawls to resume from the last successfully crawled page
**So that** timeout does not discard progress and the entire catalog is eventually crawled

**Acceptance Criteria**:
- [x] **AC-US2-01**: After each successfully crawled page, the page number is persisted to a state file
- [x] **AC-US2-02**: On next crawl invocation, if a state file exists, crawling resumes from the saved page number
- [x] **AC-US2-03**: When the crawler reaches the last page (hasMore === false or empty skills array), the state file is deleted so the next run starts fresh from page 1
- [x] **AC-US2-04**: State files older than 24 hours are treated as stale and ignored

---

### US-003: InlineSubmitter Safe Batching (P1)
**Project**: vskill-platform

**As a** platform operator
**I want** the InlineSubmitter to not lose repos when a batch submission fails or times out
**So that** discovered repos are retried on the next flush instead of being silently dropped

**Acceptance Criteria**:
- [x] **AC-US3-01**: The `_flush()` method copies the batch from the buffer BEFORE removing it, and only removes from buffer after confirmed success
- [x] **AC-US3-02**: On submission failure (network error, HTTP error after retries exhausted), the failed batch is re-added to the buffer
- [x] **AC-US3-03**: A `maxRetryBatches` cap prevents infinite retry loops (default: 2 retries per batch, then drop with error log)
- [x] **AC-US3-04**: The `totalLost` counter tracks repos that were dropped after max retries

---

### US-004: SAST Scanner Pre-flight Health Check (P1)
**Project**: vskill-platform

**As a** platform operator
**I want** the sast-scanner source to verify scanner-worker health before claiming scans
**So that** scans are not claimed and left in stuck RUNNING state when scanner-worker is down

**Acceptance Criteria**:
- [x] **AC-US4-01**: Before fetching pending scans, sast-scanner makes a GET request to scanner-worker's /health endpoint (localhost:9500/health)
- [x] **AC-US4-02**: If health check fails (network error, non-200, or timeout >5s), the crawl returns immediately with `{ healthCheckFailed: true, checked: 0 }`
- [x] **AC-US4-03**: No scans are claimed from the platform when health check fails
- [x] **AC-US4-04**: The health check failure is logged with the specific error for debugging

---

### US-005: Health Monitoring and Metrics (P2)
**Project**: vskill-platform

**As a** platform operator
**I want** per-source metrics, consecutive failure tracking, and a /metrics endpoint
**So that** I can monitor pipeline health and detect degradation before it becomes critical

**Acceptance Criteria**:
- [x] **AC-US5-01**: The scheduler tracks per-source metrics: totalDiscovered, totalSubmitted, totalErrors, totalRuns, lastDurationMs, averageDurationMs
- [x] **AC-US5-02**: Consecutive failure count is tracked per source; when it exceeds a configurable threshold (default: 5), a warning is logged with `[ALERT]` prefix
- [x] **AC-US5-03**: Dedup ratio (seenRepos / totalDiscovered) is tracked for discovery sources and logged when ratio exceeds 95% (indicating diminishing returns)
- [x] **AC-US5-04**: A GET /metrics endpoint on the crawl-worker server returns JSON with all per-source metrics, uptime, and current scheduler state
- [x] **AC-US5-05**: Metrics are accumulated in memory and reset on process restart (no persistence needed)

---

## Functional Requirements

### FR-001: State File Convention
All state files live in a configurable directory (default: `/tmp/crawl-state/`), with filenames matching the source name (e.g., `github-sharded.json`, `skills-sh.json`). The directory is created on first write if it doesn't exist.

### FR-002: Checkpoint File Format
```json
{
  "lastShardIndex": 42,
  "seenRepos": ["owner/repo:SKILL.md", "..."],
  "updatedAt": "2026-03-02T12:00:00Z",
  "shardMode": "full",
  "totalShards": 490
}
```

### FR-003: Skills.sh State File Format
```json
{
  "lastPage": 15,
  "updatedAt": "2026-03-02T12:00:00Z"
}
```

### FR-004: InlineSubmitter Batch Safety
The `_flush()` method must follow this sequence:
1. Copy batch: `const batch = this.buffer.slice(0, this.batchSize)`
2. Attempt submission
3. On success: `this.buffer.splice(0, batch.length)` (remove from buffer)
4. On failure: increment retry count on the batch; if under limit, leave in buffer; if over limit, splice and log as lost

### FR-005: Metrics Accumulation
Metrics are stored in a Map keyed by source name. Each entry accumulates across runs within the process lifetime. The scheduler's `runSourceLoop` updates metrics after each crawl completes or fails.

## Success Criteria

- github-sharded in "full" mode (490 shards) completes across multiple scheduler cycles, processing all shards within 3 cycles
- skills-sh crawl resumes from last page after timeout, eventually reaching the end
- Zero data loss in InlineSubmitter under normal timeout conditions
- SAST scanner returns immediately when scanner-worker is unhealthy, no stuck RUNNING scans
- /metrics endpoint returns comprehensive per-source health data
- Combined submission throughput reaches 2,000-3,000 per 30 minutes

## Out of Scope

- External monitoring/alerting integration (Prometheus, Grafana, PagerDuty)
- Persistent metrics across restarts (in-memory only for now)
- Changes to the platform API endpoints themselves
- Scanner-worker (localhost:9500) reliability improvements
- Rate limit strategy changes for GitHub API

## Dependencies

- Existing crawl-worker scheduler infrastructure (scheduler.js, server.js)
- Existing source modules (github-sharded.js, skills-sh.js, sast-scanner.js)
- Existing InlineSubmitter (lib/inline-submitter.js)
- Docker volumes for state file persistence (may need volume mount for /tmp/crawl-state)
