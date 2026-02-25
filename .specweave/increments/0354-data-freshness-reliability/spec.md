# 0354 — Data Freshness & Reliability

## Problem

The enrichment pipeline has multiple reliability issues: metrics can never decrease (>0 guard prevents corrections), there is no `metricsRefreshedAt` timestamp so users cannot assess data freshness, the batch size of 20 skills/hour creates multi-day staleness for large catalogs, metric updates and trending score recalculation are not atomic, there is no rate-limit detection for GitHub/npm APIs, and the stats cache (2h TTL) desyncs from hourly enrichment.

## User Stories

### US-001: Allow metrics to decrease

As a platform operator, I want metrics to reflect real values even when they drop, so the platform does not show inflated numbers for deleted/declined repos.

**Acceptance Criteria:**
- [x] AC-US1-01: Enrichment batch updates stars/forks/downloads to fetched value regardless of direction
- [x] AC-US1-02: Live enrichment path also removes >0 guard
- [x] AC-US1-03: Null/error responses still skip update (only successful fetches overwrite)

### US-002: Atomic enrichment with trending recalc

As a platform operator, I want metric updates and trending recalc to be atomic so crashes cannot leave scores desynced.

**Acceptance Criteria:**
- [x] AC-US2-01: Per-skill metric update and trending score update happen in the same transaction
- [x] AC-US2-02: Failed metric update preserves old trending score

### US-003: Track and display data freshness

As a user, I want to see when metrics were last refreshed so I can assess data currency.

**Acceptance Criteria:**
- [x] AC-US3-01: Skill model has `metricsRefreshedAt DateTime?` column
- [x] AC-US3-02: Enrichment sets `metricsRefreshedAt` on each successful update
- [x] AC-US3-03: Skill detail page shows "Metrics updated X ago" in Popularity section

### US-004: Handle API rate limiting

As a platform operator, I want the enrichment batch to detect 429 responses and back off.

**Acceptance Criteria:**
- [x] AC-US4-01: GitHub 429 triggers exponential backoff with Retry-After header
- [x] AC-US4-02: npm 429 triggers same backoff
- [x] AC-US4-03: Rate-limit events are logged with retry-after value

### US-005: Invalidate stats cache after enrichment

As a platform operator, I want fresh stats after enrichment completes, not stale 2h cached data.

**Acceptance Criteria:**
- [x] AC-US5-01: Stats KV key is invalidated/refreshed after enrichment batch
- [x] AC-US5-02: Next homepage render picks up updated stats

### US-006: Increase batch throughput

As a platform operator, I want more skills refreshed per hour.

**Acceptance Criteria:**
- [x] AC-US6-01: Default batch size is 50 (was 20)
- [x] AC-US6-02: Batch size configurable via environment variable

## Out of Scope

- Delta-based trending formula (handled in 0353)
- MetricsSnapshot table (handled in 0353)
- Certification tier fixes (handled in 0352)

## Dependencies

- None (independent of 0352)
- 0353 depends on this increment being completed first
