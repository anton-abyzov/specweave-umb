# Implementation Plan: Bulk Skill Discovery - Scale Queue Ingestion to 60k+

## Overview

Refactor `github-discovery.ts` to paginate GitHub search results (up to 1000/query), replace KV dedup with a persistent `DiscoveryRecord` Prisma model, add `POST /api/v1/admin/discovery/bulk` for admin-triggered large crawls, expand search queries, and raise the per-run cap. All changes in `vskill-platform`.

## Architecture

### Components

- **github-discovery.ts** (refactor): Paginated fetcher, rate-limit backoff, DB dedup, configurable caps
- **DiscoveryRecord model** (new): Prisma model for persistent dedup
- **DiscoveryRunLog model** (new): Prisma model for run metrics/observability
- **admin/discovery/bulk/route.ts** (new): Bulk-ingest admin endpoint
- **admin/discovery/stats/route.ts** (new): Discovery metrics endpoint

### Data Model

#### DiscoveryRecord (new)
```prisma
model DiscoveryRecord {
  id            String   @id @default(uuid())
  repoFullName  String   /// e.g. "owner/repo"
  skillPath     String   /// e.g. "SKILL.md" or ".claude/commands/foo.md"
  source        String   /// "github-code" | "github-repo" | "npm" | "skills.sh"
  submissionId  String?  /// Linked submission ID (null if submission failed)
  firstSeenAt   DateTime @default(now())
  lastSeenAt    DateTime @default(now())

  @@unique([repoFullName, skillPath])
  @@index([source])
  @@index([lastSeenAt])
}
```

#### DiscoveryRunLog (new)
```prisma
model DiscoveryRunLog {
  id              String   @id @default(uuid())
  trigger         String   /// "cron" | "admin" | "bulk"
  candidatesFound Int
  newSubmissions  Int
  skippedDedup    Int
  errors          Int
  durationMs      Int
  sourceBreakdown Json     @default("{}")
  createdAt       DateTime @default(now())

  @@index([createdAt])
}
```

### API Contracts

- `POST /api/v1/admin/discovery/bulk`
  - Auth: X-Internal-Key or SUPER_ADMIN JWT
  - Body: `{ sources?: string[], maxResults?: number, dryRun?: boolean }`
  - Response: `{ ok: true, candidatesFound, newSubmissions, skippedDedup, skippedErrors, durationMs, candidates?: [...] }`

- `GET /api/v1/admin/discovery/stats`
  - Auth: X-Internal-Key or SUPER_ADMIN JWT
  - Query: `?limit=30`
  - Response: `{ runs: DiscoveryRunLog[] }`

## Technology Stack

- **Language/Framework**: TypeScript, Next.js 15, Cloudflare Workers
- **Database**: Prisma + D1 (SQLite)
- **Testing**: Vitest, TDD (RED-GREEN-REFACTOR)

**Architecture Decisions**:

- **DB over KV for dedup**: KV TTL means dedup state is lost after 7 days, causing re-submissions. DB is permanent and queryable. Trade-off: slightly slower per-check (DB query vs KV get), but acceptable since dedup is not latency-sensitive in a cron job.
- **Pagination with delay**: GitHub search API maxes at 1000 results per query (10 pages of 100). We paginate with 1200ms delay between requests to stay within rate limits. This extends crawl time but is necessary.
- **Separate bulk endpoint**: Rather than overloading the existing POST /api/v1/admin/discovery, a new /bulk endpoint has different auth semantics (same auth) but different parameters. The existing endpoint is preserved for backward compatibility.
- **Run log in DB**: Storing run metrics in DB (not just console.log) enables admin monitoring without log access.

## Implementation Phases

### Phase 1: DB Models + Migration
- Add DiscoveryRecord and DiscoveryRunLog to Prisma schema
- Run migration
- Write unit tests for dedup logic

### Phase 2: Paginated Search + DB Dedup
- Refactor discoverFromCodeSearch/discoverFromRepoSearch to paginate
- Add rate-limit backoff (exponential on 403/429)
- Replace KV dedup with DB dedup in runGitHubDiscovery
- Remove SEEN_TTL / KV dedup code

### Phase 3: Admin Bulk Endpoint + Stats
- Add POST /api/v1/admin/discovery/bulk
- Add GET /api/v1/admin/discovery/stats
- Wire run logging into discovery orchestrator

### Phase 4: Expanded Queries + Cap Raise
- Add new CODE_SEARCH_QUERIES and REPO_SEARCH_QUERIES
- Raise MAX_PER_CRON to 500
- Add source filtering support

## Testing Strategy

- TDD: Write tests first for all new functions
- Unit tests for pagination logic (mock fetch responses with Link headers)
- Unit tests for DB dedup (mock Prisma)
- Integration tests for bulk endpoint (mock discovery, test auth/validation)
- Ensure existing discovery tests still pass after refactor

## Technical Challenges

### Challenge 1: GitHub Search API Rate Limits
**Solution**: 1200ms delay between requests + exponential backoff on 403/429. Authenticated requests get 30/min. With ~15 queries x 10 pages = 150 requests, at 2s average = ~5 minutes.
**Risk**: Rate limit exhaustion. Mitigation: stop pagination early if rate limited, log remaining quota from X-RateLimit-Remaining header.

### Challenge 2: Cloudflare Workers CPU Time Limit
**Solution**: Workers have a 30-second CPU time limit (not wall-clock). The 5-minute wall-clock time is mostly I/O wait (fetch). Monitor CPU time via `ctx.waitUntil` and stop early if approaching limit.
**Risk**: Very large crawls may hit limits. Mitigation: bulk endpoint returns partial results on timeout.

### Challenge 3: Migration of Existing KV Dedup Data
**Solution**: No migration needed. Existing KV data has 7-day TTL and will naturally expire. New DB dedup starts fresh -- any skill not in DB will be re-discovered once, then permanently tracked.
**Risk**: One-time re-submission of recently-seen skills. Mitigation: submission pipeline already handles duplicates via checkSubmissionDedup (Prisma query on Submission table).
