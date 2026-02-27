---
increment: 0319-discovery-scale-up
title: Massive Skill Discovery Scale-Up
type: feature
priority: P1
status: completed
created: 2026-02-22T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 80
---

# Feature: Massive Skill Discovery Scale-Up

## Overview

Scale skill discovery from ~5k to 70k+ by adding high-yield sources (Sourcegraph, GitHub sharding, GraphQL batch checks, Events API, GitLab), moving heavy crawling to Hetzner VMs (port 9600), and enabling batch submissions for performance.

## User Stories

### US-001: VM-Based Crawl Worker Infrastructure (P1)
**Project**: vskill-platform

**As a** platform operator
**I want** crawl workers running on Hetzner VMs alongside scanner workers
**So that** discovery can run for minutes/hours without Cloudflare Worker 30s timeouts

**Acceptance Criteria**:
- [x] **AC-US1-01**: Crawl worker HTTP server runs on port 9600 with `/health`, `/POST /crawl`, `/GET /status` endpoints
- [x] **AC-US1-02**: Auth via `X-Worker-Signature` header (same pattern as scanner-worker)
- [x] **AC-US1-03**: Docker Compose adds crawl-worker service alongside scanner-worker on same VMs
- [x] **AC-US1-04**: Deploy script SCPs crawl-worker files and health-checks port 9600
- [x] **AC-US1-05**: CF Worker dispatches crawl jobs to VMs via round-robin (like external-scan-dispatch.ts)

---

### US-002: Bulk Submission Endpoint (P1)
**Project**: vskill-platform

**As a** crawl worker
**I want** to submit discovered repos in batches of up to 100
**So that** HTTP overhead is reduced by 100x compared to 1-by-1 POSTs

**Acceptance Criteria**:
- [x] **AC-US2-01**: `POST /api/v1/submissions/bulk` accepts `{ repos: [{repoUrl, skillName, skillPath}] }` (max 100 per batch)
- [x] **AC-US2-02**: Internally fans out to existing submission + queue logic per repo
- [x] **AC-US2-03**: Returns summary: `{ submitted: N, skipped: N, errors: N }`
- [x] **AC-US2-04**: Auth via `X-Internal-Key` header (same as existing internal submissions)

---

### US-003: Sourcegraph Stream API Crawler (P1)
**Project**: vskill-platform

**As a** platform operator
**I want** to discover skills via Sourcegraph's Stream API
**So that** I get the highest-yield single-query discovery (5k-50k repos, no auth)

**Acceptance Criteria**:
- [x] **AC-US3-01**: Crawl worker queries `sourcegraph.com/.api/search/stream?q=type:path file:SKILL.md count:all`
- [x] **AC-US3-02**: Also searches for `.cursorrules`, `mcp.json`, `.claude/commands/*.md`, `claude.config.json`
- [x] **AC-US3-03**: Parses SSE stream, extracts repo full names and file paths
- [x] **AC-US3-04**: Batch-submits results to platform via bulk endpoint
- [x] **AC-US3-05**: Handles streaming errors, timeouts, and partial results gracefully

---

### US-004: GitHub Code Search with Size Sharding (P1)
**Project**: vskill-platform

**As a** platform operator
**I want** GitHub Code Search to use size-based sharding
**So that** I bypass the 1,000-result cap and discover 5-20x more repos

**Acceptance Criteria**:
- [x] **AC-US4-01**: Each code search query is split into size shards (e.g., `size:0..100`, `size:101..300`, `size:301..500`, etc.)
- [x] **AC-US4-02**: Size ranges are fine-grained enough that each shard returns <1000 results
- [x] **AC-US4-03**: Sharding is configurable — shard boundaries can be tuned based on observed distribution
- [x] **AC-US4-04**: Token rotation works across all sharded queries
- [x] **AC-US4-05**: Adaptive delay respects rate limits (9 req/min for code search)

---

### US-005: GitHub Repo Search + GraphQL Batch Check (P1)
**Project**: vskill-platform

**As a** platform operator
**I want** date-sharded repo search combined with GraphQL batch file-existence checks
**So that** I can discover 70k+ repos by checking candidates in bulk (250k repos/hr/token)

**Acceptance Criteria**:
- [x] **AC-US5-01**: Repo search uses monthly date shards (`created:2024-01-01..2024-01-31`, etc.) + star shards
- [x] **AC-US5-02**: Candidate repos are batch-checked for SKILL.md via GraphQL aliases (50 repos per query)
- [x] **AC-US5-03**: GraphQL queries check multiple file patterns: `SKILL.md`, `.cursorrules`, `mcp.json`, `.claude/commands`
- [x] **AC-US5-04**: Token rotation across multiple GitHub tokens for throughput
- [x] **AC-US5-05**: Repos confirmed to have target files are batch-submitted to platform

---

### US-006: GitHub Events API Monitor (P2)
**Project**: vskill-platform

**As a** platform operator
**I want** real-time monitoring of GitHub push events for new SKILL.md files
**So that** newly created skills are discovered within minutes, not hours

**Acceptance Criteria**:
- [x] **AC-US6-01**: Crawl worker polls `/events` endpoint continuously (respects `X-Poll-Interval` header)
- [x] **AC-US6-02**: Filters PushEvent payloads for commits adding SKILL.md, .cursorrules, mcp.json
- [x] **AC-US6-03**: Discovered repos are submitted to platform for scanning
- [x] **AC-US6-04**: Maintains last-seen event ID to avoid duplicates across poll cycles

---

### US-007: GitLab Code Search (P2)
**Project**: vskill-platform

**As a** platform operator
**I want** to discover skills on GitLab.com
**So that** non-GitHub repos are included in the registry

**Acceptance Criteria**:
- [x] **AC-US7-01**: Queries GitLab API `GET /api/v4/search?scope=projects&search=SKILL.md` (projects scope works without Premium)
- [x] **AC-US7-02**: For matched projects, checks file tree for SKILL.md presence
- [x] **AC-US7-03**: Handles pagination, rate limits, and auth via GITLAB_TOKEN
- [x] **AC-US7-04**: Submits discovered GitLab repos to platform

---

### US-008: npm Pagination Fix (P1)
**Project**: vskill-platform

**As a** platform operator
**I want** npm search to paginate beyond 100 results
**So that** all matching npm packages are discovered, not just the first 100

**Acceptance Criteria**:
- [x] **AC-US8-01**: npm search uses `from` offset parameter to paginate all results
- [x] **AC-US8-02**: Continues fetching until `objects` array is empty or total is reached
- [x] **AC-US8-03**: Dedup within and across keyword searches

---

### US-009: Crawl Orchestration and Monitoring (P1)
**Project**: vskill-platform

**As a** platform operator
**I want** staggered cron scheduling and queue depth monitoring
**So that** the discovery pipeline never stops and I can track throughput per source

**Acceptance Criteria**:
- [x] **AC-US9-01**: CF cron dispatches crawl jobs to VMs (replaces inline discovery for heavy sources)
- [x] **AC-US9-02**: Different sources run on different schedules (Sourcegraph: every 2h, GitHub sharded: every 30min, Events: continuous)
- [x] **AC-US9-03**: Crawl metrics tracked in KV: discoveries per source per hour, crawl duration, errors
- [x] **AC-US9-04**: `/api/v1/admin/crawl-metrics` endpoint returns current discovery rates

## Functional Requirements

### FR-001: Crawl Worker Capacity
Each Hetzner VM must support running multiple source crawls concurrently via `Promise.allSettled`. Max 3 concurrent crawl jobs per VM.

### FR-002: Rate Limit Awareness
Each source must implement adaptive rate limiting: GitHub (9 req/min code search, 30 req/min repo search, 5000 GraphQL points/hr), Sourcegraph (no known limit), GitLab (10k req/min auth).

### FR-003: Graceful Degradation
If a source fails (rate limited, API down), other sources continue. Partial results are still submitted.

## Success Criteria

- Discovery rate: 2,000-5,000 new candidates per hour across all sources
- Total published skills: 20k+ within first week, 70k+ within first month
- Queue never empty for more than 15 minutes during business hours
- Zero data loss: all discovered repos submitted and tracked

## Out of Scope

- PyPI, Hugging Face, VS Code Marketplace, Docker Hub, Codeberg scrapers (follow-up increments)
- Changes to the scanning pipeline (Tier 1/2 scanner logic unchanged)
- UI changes to the dashboard
- Prisma schema changes (reuses existing DiscoveryRecord + Submission models)

## Dependencies

- Existing 3 Hetzner VMs (5.161.69.232, 91.107.239.24, 5.161.56.136)
- GitHub API tokens (GITHUB_TOKENS env var, already configured)
- Cloudflare Workers deployment (wrangler)
- Sourcegraph public API (no auth needed)
