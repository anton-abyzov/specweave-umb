# Spec: Fix Scanner Infrastructure & Scale Discovery to 60K+

## Problem Statement

The vskill-platform discovery crawler is limited by single-token GitHub API rate limits (5,000 requests/hour), sequential source execution, fixed delays, and no re-scanning of stale records. The SpecWeave local dashboard shows broken rate limit data and has no connection to the platform API. Together, these limit discovery throughput to ~500 new skills per cron run and prevent the system from reaching the 3,000+ verified skills target.

## Goals

1. Scale the platform crawler to discover 3,000+ skills across multiple cron runs by rotating multiple GitHub tokens, parallelizing sources, and spreading queries across hourly runs
2. Add TTL-based re-scanning so previously rejected repos get re-evaluated after 30 days
3. Fix the SpecWeave local dashboard to gracefully handle missing tokens and show platform API data alongside local results

## Non-Goals

- Complex token health tracking or automatic rotation mechanisms
- Interactive token setup wizards in the dashboard
- Replacing local scanner results with platform data (supplement, not replace)
- Startup validation of tokens
- Different TTLs per discovery outcome

## Architecture Decisions

- **Token rotation**: Private implementation inside `github-discovery.ts`. Simple round-robin. On 401/403, skip the token for the current cycle and move to the next. No health tracking persistence.
- **Token storage**: Comma-separated string in a single Cloudflare secret (`GITHUB_TOKENS`). Designed for 2-10 tokens. Falls back to existing single `GITHUB_TOKEN` for backward compatibility.
- **Source parallelism**: Parallelize at the source level only (github-code, github-repo, npm, skills.sh run concurrently via `Promise.allSettled`). Within each source, queries stay sequential per token to respect rate limits.
- **Query spreading**: Each hourly cron run picks a rotating subset of queries (rotating index based on hour-of-day). With 24 runs/day, each doing ~10-15 queries with 2-3 tokens, load is naturally spread without hitting rate limits.
- **Discovery TTL**: Uniform 30-day TTL for all records regardless of outcome. Stale records allow re-discovery.
- **Dashboard token state**: Static "No token configured" message with documentation link. No interactive setup.
- **Platform integration**: Dashboard shows both local scanner results and platform API data. Platform supplements local, does not replace.

---

## User Stories

### US-001: Recover Scanner Infrastructure

**Project**: vskill-platform
**As a** platform operator
**I want** the scanner infrastructure deployed and operational
**So that** skill discovery and indexing resume after the 0306 deployment

**Acceptance Criteria**:
- [ ] **AC-US1-01**: 0306 fixes are deployed via push-deploy.sh and all endpoints respond 200
- [ ] **AC-US1-02**: Cloudflare secrets (GITHUB_TOKEN, DATABASE_URL, INTERNAL_BROADCAST_KEY) are configured and available in worker context
- [ ] **AC-US1-03**: POST /api/v1/admin/rebuild-index successfully rebuilds from surviving KV keys (rebuilt > 0)
- [ ] **AC-US1-04**: GET /api/v1/admin/health/skills reports no index drift after rebuild

---

### US-002: Scale Platform Discovery Crawler

**Project**: vskill-platform
**As a** platform operator
**I want** the crawler to rotate multiple GitHub tokens, parallelize sources, and spread queries across cron runs
**So that** discovery throughput reaches 3,000+ skills without hitting rate limits

**Acceptance Criteria**:
- [ ] **AC-US2-01**: Given GITHUB_TOKENS="tok1,tok2,tok3", tokens are used in round-robin order. On 401/403, the failing token is skipped for the current cycle. Falls back to single GITHUB_TOKEN when GITHUB_TOKENS is not set.
- [ ] **AC-US2-02**: 50+ search queries available across code search, repo search, and npm keywords, including time-sharded and star-sharded variants
- [ ] **AC-US2-03**: All 4 sources (github-code, github-repo, npm, skills.sh) execute concurrently via Promise.allSettled with per-source error isolation and cross-source dedup by fullName
- [ ] **AC-US2-04**: MAX_PER_CRON raised to 5,000 submissions per run
- [ ] **AC-US2-05**: Adaptive delay reads X-RateLimit-Remaining and X-RateLimit-Reset headers: >20 remaining = 200ms, >10 = 500ms, >5 = 1000ms, <=5 = wait until reset timestamp
- [ ] **AC-US2-06**: hasBeenDiscovered() accepts staleAfterDays parameter (default 30). Records older than 30 days return false, allowing re-discovery.
- [ ] **AC-US2-07**: POST /api/v1/admin/discovery/bulk accepts optional tokens array, dateRange, and maxPerRun (validated <=10,000) passed through to runGitHubDiscovery
- [ ] **AC-US2-08**: Each hourly cron run selects a rotating subset of queries (rotating index based on hour-of-day), spreading 50+ queries across 24 runs
- [ ] **AC-US2-09**: Unit tests cover: token rotation round-robin, token skip on 401/403, adaptive delay calculation, parallel source execution with error isolation, discovery TTL expiry, time-sharded and star-sharded query generation, query rotation index

---

### US-003: Fix SpecWeave Dashboard Scanner Display

**Project**: specweave
**As a** SpecWeave user
**I want** the dashboard to show real scanner data and handle missing tokens gracefully
**So that** I can see verified skills and understand scanner configuration status

**Acceptance Criteria**:
- [ ] **AC-US3-01**: Scanner worker reads GITHUB_TOKEN from process.env or .specweave/config.json and logs a clear error when missing
- [ ] **AC-US3-02**: Dashboard fetches and displays top skills from verified-skill.com platform API (GET /api/v1/skills?sortBy=trendingScore7d&limit=20)
- [ ] **AC-US3-03**: When no token is configured, Rate Limit card shows static "No token configured" text with amber styling and a link to documentation, instead of showing null/undefined
- [ ] **AC-US3-04**: Platform API errors are handled gracefully — dashboard falls back to local-only data without crashing

---

### US-004: Operational Scaling Tooling

**Project**: vskill-platform
**As a** platform operator
**I want** a bulk crawl script and operations runbook
**So that** I can run large-scale discovery manually and onboard new operators

**Acceptance Criteria**:
- [ ] **AC-US4-01**: scripts/bulk-crawl.sh reads tokens from environment, distributes queries across tokens, supports --dry-run, and logs progress
- [ ] **AC-US4-02**: docs/scanner-ops.md documents: token setup, secrets configuration, bulk crawl execution, monitoring, recovery procedures, and scaling guidance
