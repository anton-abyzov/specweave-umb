---
increment: 0355-fix-homepage-zero-stats
title: "Fix Homepage Zero Stats"
type: bugfix
priority: P0
status: in-progress
created: 2026-02-24
structure: user-stories
test_mode: test-after
coverage_target: 80
---

# Bugfix: Fix Homepage Zero Stats

## Overview

Homepage at verified-skill.com shows "172 security-scanned skills" but ALL other metrics are zero: GitHub Stars 0, Unique Repos 0, NPM Downloads 0, Scan Pass Rate 0%, trending scores -0.0. Three compounding root causes: (1) `computeFullStats()` times out running 12 parallel queries against cold Neon DB within a 10s timeout, falling back to `computeMinimalStats()` which returns hardcoded zeros; (2) enrichment batch is starved — skills without valid GitHub/npm data never advance `updatedAt`, blocking enrichable skills from being reached; (3) trending score formula produces 0.0 when all input metrics are zero.

## User Stories

### US-001: Resilient Stats Computation (P0)
**Project**: vskill-platform

**As a** visitor to the homepage
**I want** to always see real platform statistics
**So that** the platform appears credible with accurate data

**Acceptance Criteria**:
- [x] **AC-US1-01**: `computeMinimalStats()` runs individual queries with per-query try/catch instead of returning hardcoded zeros — each metric degrades independently
- [x] **AC-US1-02**: `computeFullStats()` uses a 25s timeout (up from 10s) for the 12-query Promise.all batch
- [x] **AC-US1-03**: Structured error logging in `computePlatformStats` catch block includes error message and short stack trace
- [x] **AC-US1-04**: `scanPassRate` correctly computes as ~100% when there are skills but no blocklist entries (not 0%)

---

### US-002: Fix Enrichment Pipeline (P0)
**Project**: vskill-platform

**As a** platform operator
**I want** the enrichment cron to cycle through all skills
**So that** GitHub stars, npm downloads, and trending scores reflect real data

**Acceptance Criteria**:
- [x] **AC-US2-01**: Enrichment always advances `updatedAt` for processed skills, even when no metric updates are available — prevents starvation
- [x] **AC-US2-02**: Enrichment batch size increased from 20 to 50 (172 skills / 50 = ~3.5h full cycle)
- [x] **AC-US2-03**: Enrichment batch logs start info including skill count and token availability

---

### US-003: Non-Zero Trending Scores (P1)
**Project**: vskill-platform

**As a** visitor to the homepage
**I want** the trending section to show meaningful scores
**So that** I can discover active and popular skills

**Acceptance Criteria**:
- [x] **AC-US3-01**: Trending score formula includes recency boost: +5 for skills created within 7 days, +3 for active repos (lastCommitAt within 7 days)
- [x] **AC-US3-02**: 30-day trending formula includes proportional recency boost: +3 for skills created within 30 days, +2 for active repos

---

### US-004: Cron Observability & Independence (P1)
**Project**: vskill-platform

**As a** platform operator
**I want** stats refresh to run independently and with timing logs
**So that** I can diagnose cron failures and ensure stats refresh isn't blocked by other tasks

**Acceptance Criteria**:
- [x] **AC-US4-01**: `refreshPlatformStats` runs in its own `ctx.waitUntil` block, independent of the sequential cron chain
- [x] **AC-US4-02**: Enrichment and stats-refresh steps have timing logs in the cron handler
- [x] **AC-US4-03**: KV `put()` calls remove `expirationTtl` — data persists indefinitely, staleness tracked via `updatedAt`

---

### US-005: Bulk Enrichment Recovery (P1)
**Project**: vskill-platform

**As a** platform operator
**I want** an admin endpoint to bulk-enrich all skills
**So that** I can recover from enrichment pipeline starvation without waiting for hourly cron cycles

**Acceptance Criteria**:
- [x] **AC-US5-01**: POST `/api/v1/admin/enrich` endpoint exists with X-Internal-Key auth
- [x] **AC-US5-02**: Endpoint processes all non-deprecated skills in batches of 50 with 1s pause between batches
- [x] **AC-US5-03**: Endpoint recomputes trending scores and refreshes stats cache after enrichment
- [x] **AC-US5-04**: Returns JSON summary: `{ processed, updated, errors }`

---

### US-006: Stats Health Check (P2)
**Project**: vskill-platform

**As a** platform operator
**I want** a health check endpoint for stats freshness
**So that** I can monitor whether the stats pipeline is healthy

**Acceptance Criteria**:
- [x] **AC-US6-01**: GET `/api/v1/stats/health` endpoint returns cache age, staleness status, and key metrics
- [x] **AC-US6-02**: Returns HTTP 503 when stats are missing or stale (>4 hours)

## Success Criteria

- Homepage shows non-zero scan pass rate (~100%), real verified/certified counts, unique repo count
- After bulk enrichment, homepage shows real GitHub stars and npm download counts
- Trending section shows non-zero scores for recently created/active skills
- Stats refresh completes even when other cron tasks time out

## Out of Scope

- Homepage visual redesign
- Real-time stats updates
- Schema changes or migrations
