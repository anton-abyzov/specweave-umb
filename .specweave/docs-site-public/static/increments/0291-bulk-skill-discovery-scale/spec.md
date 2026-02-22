---
increment: 0291-bulk-skill-discovery-scale
title: "Bulk Skill Discovery - Scale Queue Ingestion to 60k+"
type: feature
priority: P1
status: ready_for_review
created: 2026-02-21
structure: user-stories
test_mode: TDD
coverage_target: 80
---

# Feature: Bulk Skill Discovery - Scale Queue Ingestion to 60k+

## Overview

The current discovery crawler is limited to ~500 skills per cron cycle due to non-paginated GitHub search (per_page=30, 1 page), ephemeral KV dedup (7-day TTL loses history), a hard cap of 100 new items per run, and only 6 search queries. This increment scales ingestion to 60k+ by adding paginated GitHub search (up to 1000 results per query), a persistent DB dedup table, an admin bulk-ingest endpoint for batch processing, and broader search query coverage.

## User Stories

### US-001: Paginated GitHub Search (P1)
**Project**: specweave

**As a** platform operator
**I want** the discovery crawler to paginate through all GitHub search results
**So that** I can discover thousands of skills per query instead of just 30

**Acceptance Criteria**:
- [x] **AC-US1-01**: Code search and repo search fetch up to 10 pages (per_page=100, max 1000 results per query per GitHub API limit)
- [x] **AC-US1-02**: Pagination respects GitHub rate limits (1200ms delay between requests, backs off on 403/429)
- [x] **AC-US1-03**: Each page is processed before fetching the next (no unbounded memory)
- [x] **AC-US1-04**: Crawler logs total_count vs fetched count per query for observability

---

### US-002: Persistent Dedup DB Table (P1)
**Project**: specweave

**As a** platform operator
**I want** discovery dedup to be stored in a persistent DB table instead of KV with TTL
**So that** I never re-submit a skill that was already discovered, even across weeks or months

**Acceptance Criteria**:
- [x] **AC-US2-01**: New Prisma model `DiscoveryRecord` with fields: id, repoFullName, skillPath, source, firstSeenAt, lastSeenAt, submissionId (nullable)
- [x] **AC-US2-02**: Unique constraint on (repoFullName, skillPath) prevents duplicates
- [x] **AC-US2-03**: Crawler checks DiscoveryRecord before submitting; skips if exists
- [x] **AC-US2-04**: On successful submission, DiscoveryRecord.submissionId is linked
- [x] **AC-US2-05**: lastSeenAt is updated on every re-encounter (for freshness tracking)
- [x] **AC-US2-06**: KV-based dedup (SEEN_TTL) is removed; DB is sole source of truth

---

### US-003: Admin Bulk-Ingest Endpoint (P1)
**Project**: specweave

**As a** platform admin
**I want** an endpoint to trigger bulk ingestion with custom parameters
**So that** I can run one-off large crawls, re-crawl specific sources, or ingest from new sources

**Acceptance Criteria**:
- [x] **AC-US3-01**: POST /api/v1/admin/discovery/bulk accepts body: { sources?: string[], maxResults?: number, dryRun?: boolean }
- [x] **AC-US3-02**: Authenticated via X-Internal-Key or SUPER_ADMIN JWT (same as existing admin/discovery)
- [x] **AC-US3-03**: dryRun=true returns candidates without submitting
- [x] **AC-US3-04**: Response includes: { candidatesFound, newSubmissions, skippedDedup, skippedErrors, durationMs }
- [x] **AC-US3-05**: maxResults overrides MAX_PER_CRON for this run (default: 500, max: 5000)
- [x] **AC-US3-06**: sources filter limits crawl to specific sources (e.g., ["github-code", "npm"])

---

### US-004: Expanded Search Query Coverage (P2)
**Project**: specweave

**As a** platform operator
**I want** more search queries to cover additional skill patterns on GitHub
**So that** the crawler discovers skills that use non-standard naming or structures

**Acceptance Criteria**:
- [x] **AC-US4-01**: Code search includes queries for: SKILL.md at any path, skill.md (lowercase), .claude/commands/**/*.md, commands/*.md in skill repos
- [x] **AC-US4-02**: Repo search includes queries for: topic:mcp-server, topic:claude-code, topic:ai-skill, "SKILL.md" in:readme, "claude code" skill in:description
- [x] **AC-US4-03**: Each new query is additive (existing queries are preserved)
- [x] **AC-US4-04**: Duplicate repos across queries are deduplicated within a single run

---

### US-005: Raised Ingestion Cap and Observability (P2)
**Project**: specweave

**As a** platform operator
**I want** the per-run cap raised and discovery metrics logged
**So that** I can ingest more skills per cycle and monitor discovery health

**Acceptance Criteria**:
- [x] **AC-US5-01**: MAX_PER_CRON raised from 100 to 500 for scheduled runs
- [x] **AC-US5-02**: Discovery run writes summary metrics to DB: timestamp, candidatesFound, newSubmissions, skippedDedup, errors, durationMs, source breakdown
- [x] **AC-US5-03**: Metrics queryable via GET /api/v1/admin/discovery/stats (last 30 runs)

## Functional Requirements

### FR-001: GitHub Search Pagination
The crawler must follow the Link header or increment page=N to fetch all available pages (up to 10 pages of 100 results each = 1000 per query). GitHub Code Search API returns max 1000 results. Stop when: no more results, page > 10, or rate limited.

### FR-002: Persistent Dedup
Replace KV-based `disco:seen:{fullName}:{skillPath}` with a DB table. The table persists indefinitely (no TTL). Re-crawls update lastSeenAt but do not create duplicate submissions.

### FR-003: Bulk Ingest API
New admin endpoint that runs the same discovery logic but with configurable parameters. Supports dry-run mode for previewing what would be ingested without side effects.

### FR-004: Rate Limit Awareness
GitHub authenticated search allows 30 requests/minute. With ~15 queries and 10 pages each = 150 requests. At 1200ms delay that is ~3 minutes. The crawler must handle 403/429 gracefully with exponential backoff.

## Success Criteria

- Discovery finds 10x+ more unique skills per crawl cycle (from ~180 to 2000+)
- No duplicate submissions across runs (0% re-submission rate for known skills)
- Bulk-ingest endpoint processes up to 5000 candidates in a single run
- Discovery run completes within 10 minutes (Cloudflare Workers CPU time limit)

## Out of Scope

- Real-time streaming of discovery results (batch only)
- Non-GitHub sources beyond what already exists (npm, skills.sh)
- UI for managing discovery configuration
- Automatic re-scanning of previously discovered skills

## Dependencies

- GitHub API (rate limits: 30 search requests/min authenticated, 10/min unauthenticated)
- Prisma schema migration for DiscoveryRecord model
- Existing submission pipeline (POST /api/v1/submissions)
