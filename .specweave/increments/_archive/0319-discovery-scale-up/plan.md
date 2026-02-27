# Implementation Plan: Massive Skill Discovery Scale-Up

## Overview

Move heavy crawling from Cloudflare Workers (30s limit) to Hetzner VMs (port 9600), add Sourcegraph Stream API as highest-yield source, enable GitHub search sharding and GraphQL batch checks, fix npm pagination, add GitLab search, and enable batch submissions for performance.

## Architecture

### Components
- **crawl-worker** (new): Node.js HTTP server on port 9600, deployed to 3 Hetzner VMs via Docker
- **crawl-dispatch** (new): CF-side function to dispatch crawl jobs to VMs (mirrors `external-scan-dispatch.ts`)
- **bulk-submissions** (new): `POST /api/v1/submissions/bulk` endpoint for batch repo submission
- **source crawlers** (new): Modular source implementations in `crawl-worker/sources/`
- **github-discovery.ts** (modified): npm pagination fix, sharding wired in

### Data Flow
```
CF Worker Cron (hourly)
  |
  ├─ dispatches crawl jobs → Hetzner VM:9600
  │    ├─ sourcegraph.js    → stream SSE → batch submit
  │    ├─ github-sharded.js → size-sharded search → batch submit
  │    ├─ github-graphql.js → date-shard + batch check → batch submit
  │    ├─ github-events.js  → continuous poll → submit
  │    └─ gitlab.js         → project search → submit
  │
  ├─ npm pagination fix (runs inline in CF, fast)
  └─ recovery (stuck submissions)
```

### API Contracts

**POST /crawl** (crawl-worker:9600):
```json
Request: { "source": "sourcegraph|github-sharded|github-graphql|github-events|gitlab", "config": {} }
Response: { "accepted": true, "jobId": "uuid" }
```

**GET /status** (crawl-worker:9600):
```json
Response: { "activeCrawls": 2, "maxConcurrent": 3, "lastResults": {...} }
```

**POST /api/v1/submissions/bulk** (platform):
```json
Request: { "repos": [{ "repoUrl": "...", "skillName": "...", "skillPath": "..." }] }
Response: { "submitted": 45, "skipped": 3, "errors": 2 }
```

## Technology Stack

- **Crawl Worker**: Node.js 20, plain HTTP server (no framework, matches scanner-worker pattern)
- **Docker**: node:20-slim base, git only (no Python/semgrep needed)
- **CF Side**: TypeScript, existing patterns from `external-scan-dispatch.ts`

**Architecture Decisions**:
- **Size sharding over time sharding for code search**: GitHub Code Search doesn't support `created:` qualifier. `size:` is the only effective sharding axis for code search.
- **Two-phase approach for repo search**: Enumerate candidates via date-sharded repo search, then batch-check via GraphQL (250k checks/hr/token). This is the only way to reach 70k+.
- **Sourcegraph as primary**: No auth, no rate limits, single streaming query. This should be the first source to run on every crawl cycle.
- **Same VMs, different ports**: Avoids additional infrastructure cost. Scanner-worker (9500) and crawl-worker (9600) coexist.

## Implementation Phases

### Phase 1: Infrastructure
1. Crawl worker HTTP server skeleton (`server.js`)
2. Dockerfile + docker-compose addition
3. Deploy script update
4. CF-side dispatch function (`crawl-dispatch.ts`)
5. Bulk submission endpoint

### Phase 2: Source Implementations
6. Sourcegraph Stream API crawler
7. GitHub Code Search with size sharding
8. GitHub Repo Search + GraphQL batch check
9. npm pagination fix
10. GitLab code search
11. GitHub Events API monitor

### Phase 3: Orchestration
12. Staggered cron scheduling
13. Update `build-worker-entry.ts` for crawl dispatch
14. Queue depth monitoring + metrics

### Phase 4: Testing & Deployment
15. Unit tests for source crawlers
16. Deploy to VMs + update CF config

## Testing Strategy

- **TDD**: Write failing tests first for each source crawler and endpoint
- **Mocked HTTP**: All external API calls mocked in tests (Sourcegraph SSE, GitHub REST/GraphQL, GitLab, npm)
- **Integration**: End-to-end crawl-worker → bulk submit → queue processing
- **Smoke test**: Manual Sourcegraph curl before implementation to validate API

## Technical Challenges

### Challenge 1: Sourcegraph SSE Stream Parsing
**Solution**: Use Node.js readable stream + line-by-line parsing for SSE events. Each `data:` line contains a JSON match object with repo and path.
**Risk**: Stream may be very large (50k+ matches). Process incrementally, batch-submit every 100 repos.

### Challenge 2: GitHub 9 req/min Code Search Rate Limit
**Solution**: Distribute across multiple tokens (TokenRotator). With 5 tokens = 45 req/min. Size sharding generates many queries but adaptive delay handles throttling.
**Risk**: Even with rotation, a full sharded crawl may take 2+ hours. This is fine on VMs (no timeout).

### Challenge 3: GraphQL Batch Check Reliability
**Solution**: Repos that error in GraphQL (deleted, private) are silently skipped. Batch size of 50 keeps query complexity under GitHub's 5000-point limit.
**Risk**: Very new repos may not be indexed in GraphQL yet. Mitigated by also running direct code search.
