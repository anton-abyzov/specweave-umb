# Implementation Plan: Scale Queue Throughput for Thousands of Repositories

## Overview

Five targeted changes to the vskill-platform submission pipeline that collectively increase throughput by ~10x. No new services, no schema migrations, no new dependencies. All changes are in the existing Cloudflare Workers + Next.js codebase.

**Key principle**: Thread configuration and credentials through existing call chains rather than introducing new abstractions. Each change is independently deployable.

## Architecture

### Component Map (Modified Files)

```
wrangler.jsonc                              ← US-001: config bump
src/lib/queue/consumer.ts                   ← US-002: thread GITHUB_TOKEN to processSubmission
src/lib/queue/process-submission.ts         ← US-002: accept + forward githubToken; US-003: threshold
src/lib/scanner.ts                          ← US-002: fetchRepoFiles accepts token
src/lib/scanner/github-permalink.ts         ← US-002: resolveCommitSha accepts token
src/app/api/v1/admin/queue/bulk-enqueue/route.ts  ← US-004: new endpoint
src/lib/crawler/github-discovery.ts         ← US-005: parallelize submission loop
```

### Data Flow: Token Threading (US-002)

```
Worker env (GITHUB_TOKEN secret)
  │
  ▼
handleSubmissionQueue(batch, env)           ← reads env.GITHUB_TOKEN
  │
  ▼
processSubmission({ ..., githubToken })     ← new optional field
  │
  ├─► fetchRepoFiles(repoUrl, skillPath, token)
  │     ├─► fetch raw.githubusercontent.com  (+ Authorization header)
  │     ├─► fetchRawFile(owner, repo, branch, path, token)
  │     └─► fetchDirectoryListing(owner, repo, branch, path, token)
  │
  └─► resolveCommitSha(owner, repo, "HEAD", token)
        └─► fetch api.github.com/repos/.../commits/HEAD  (+ Authorization header)
```

The token flows through existing function signatures as an optional trailing parameter. No global state, no env reads inside scanners. Testable via direct function calls with or without token.

### Data Flow: Bulk-Enqueue (US-004)

```
Hetzner VM
  │
  POST /api/v1/admin/queue/bulk-enqueue
  { items: [{ repoUrl, skillName, skillPath? }, ...] }  (max 1000)
  │
  ▼
Auth check (X-Internal-Key || SUPER_ADMIN JWT)
  │
  ▼
Validate all items (GitHub URL regex, skillName length)
  │
  ▼
createSubmissionsBatch(validItems)          ← parallel KV writes + batch DB insert
  │
  ▼
SUBMISSION_QUEUE.sendBatch(chunk)           ← chunks of 100 (CF limit)
  │
  ▼
Response: { ok, enqueued, skipped, errors }
```

### Data Flow: Parallel Discovery (US-005)

```
allCandidates (from source crawlers)
  │
  ▼
Pre-slice to maxResults                     ← avoids over-processing
  │
  ▼
Chunk into batches of DISCOVERY_BATCH_SIZE (20)
  │
  ▼
for each chunk:
  Promise.allSettled(chunk.map(candidate => {
    hasBeenDiscovered(candidate) → if new → WORKER_SELF_REFERENCE.fetch → markDiscovered
  }))
  │
  Accumulate: enqueued, skippedDedup, errors, repoStats
  │
  Break if enqueued >= maxResults
```

## API Contracts

### POST /api/v1/admin/queue/bulk-enqueue

**Auth**: `X-Internal-Key` header matching `INTERNAL_BROADCAST_KEY` env, or `SUPER_ADMIN` JWT cookie.

**Request**:
```json
{
  "items": [
    { "repoUrl": "https://github.com/owner/repo", "skillName": "my-skill", "skillPath": "SKILL.md" },
    ...
  ]
}
```

- `items`: required, array, max 1000 entries
- `repoUrl`: required, must match `/^https:\/\/github\.com\/[\w.-]+\/[\w.-]+(\/.*)?$/`
- `skillName`: required, 2-100 characters
- `skillPath`: optional, defaults to `"SKILL.md"`

**Response (200)**:
```json
{
  "ok": true,
  "enqueued": 847,
  "skipped": 12,
  "errors": ["Invalid repoUrl: ftp://bad-url"]
}
```

**Error responses**: 400 (validation), 401 (auth), 500 (internal)

## Technology Stack

No new dependencies. All changes use existing:
- **Runtime**: Cloudflare Workers (wrangler.jsonc config)
- **Framework**: Next.js 15 API routes (bulk-enqueue endpoint)
- **Queue**: Cloudflare Queues (sendBatch, consumer)
- **Storage**: Cloudflare KV + Prisma/Neon (createSubmissionsBatch)

## Architecture Decisions

### AD-001: Optional parameter threading vs env globals for GitHub token

**Decision**: Add `token?: string` as optional trailing parameter to `fetchRepoFiles`, `resolveCommitSha`, `fetchRawFile`, `fetchDirectoryListing`.

**Why not read env.GITHUB_TOKEN inside scanner functions?**
- Scanner functions are pure library code with no env dependency today
- `getCloudflareContext()` is unavailable in queue consumer context (only `runWithWorkerEnv` provides it)
- Optional parameter is testable without mocking env
- Backward-compatible: omitting token falls back to unauthenticated

**Rejected**: Global singleton pattern (breaks async isolation with max_concurrency: 20)

### AD-002: Pre-slicing vs atomic counter for parallel discovery cap

**Decision**: Pre-slice `allCandidates.slice(0, maxResults)` before parallel processing rather than using a shared atomic counter.

**Trade-off**: May process slightly more dedup checks than needed (some pre-sliced candidates may be already-discovered), but avoids concurrent mutation bugs. At 5000 candidates max, the overhead is negligible.

**Rejected**: Shared `Atomics` counter (not available in Workers runtime without SharedArrayBuffer)

### AD-003: Separate bulk-enqueue endpoint vs extending existing bulk submission

**Decision**: New route at `/api/v1/admin/queue/bulk-enqueue` rather than adding another mode to `/api/v1/submissions/bulk`.

**Rationale**: The existing `submissions/bulk` endpoint does sequential per-item dedup, repository resolution, and SSE event emission. The bulk-enqueue endpoint is purpose-built for high-throughput VM callers: skip dedup (VMs already deduped via discovery), skip repo resolution, skip SSE. Different auth pattern too (internal-only vs user-facing).

### AD-004: Batch size 10 / concurrency 20 selection

**Decision**: Conservative 3x increase (not max Cloudflare limits of 100/250).

**Rationale**: Each message in the batch triggers fetchRepoFiles (multiple GitHub fetches) + tier 1 scan + possibly tier 2 LLM call. With 10 messages x 20 concurrent batches = 200 parallel submissions, each making 3-5 GitHub API calls = 600-1000 concurrent fetches. With 5000 req/hr authenticated rate limit, this is sustainable. Going higher risks hitting GitHub secondary rate limits.

## Implementation Phases

### Phase 1: Config + Threshold (US-001, US-003)
Two constant changes with zero risk:
- `wrangler.jsonc`: bump batch_size and concurrency
- `process-submission.ts`: lower FAST_APPROVE_THRESHOLD

### Phase 2: Token Threading (US-002)
Plumbing changes across 4 files:
1. Add `githubToken` to `ProcessSubmissionOptions` interface
2. Update `consumer.ts` to read `env.GITHUB_TOKEN` and pass through
3. Update `fetchRepoFiles` signature + all internal fetch calls
4. Update `resolveCommitSha` signature
5. Update `processSubmission` to forward token to both functions

### Phase 3: Parallel Discovery (US-005)
Refactor `runGitHubDiscovery` submission loop:
1. Extract submission logic into a per-candidate async function
2. Pre-slice candidates to maxResults
3. Process in batches of 20 with `Promise.allSettled`
4. Accumulate counters after each batch

### Phase 4: Bulk-Enqueue Endpoint (US-004)
New route file (follows established patterns):
1. Auth check (copy from `admin/discovery/bulk`)
2. Validate items array
3. `createSubmissionsBatch` for storage
4. `sendBatch` in 100-item chunks for queue
5. Aggregate response

## Testing Strategy

**TDD mode is active** (config.json `testing.defaultTestMode: "TDD"`).

| Component | Test Type | Key Assertions |
|-----------|-----------|----------------|
| wrangler.jsonc | Config validation | batch_size=10, concurrency=20 |
| Token threading | Unit (vitest) | fetchRepoFiles/resolveCommitSha include Auth header when token provided, omit when not |
| Fast-approve threshold | Unit (vitest) | Score 76 triggers fast-approve; score 74 does not |
| Bulk-enqueue | Unit (vitest) | Auth check, validation, batch creation, sendBatch chunking |
| Parallel discovery | Unit (vitest) | Correct enqueued/skipped counts, maxResults cap, batch processing |

Existing tests in `src/lib/queue/__tests__/process-submission.test.ts` and `src/lib/crawler/__tests__/` must continue to pass (backward compatibility).

## Technical Challenges

### Challenge 1: Concurrent dedup in parallel discovery
**Problem**: `hasBeenDiscovered` is a DB read. Two parallel candidates from the same repo could both pass dedup and get double-submitted.
**Solution**: The existing `markDiscovered` uses a unique constraint on `(fullName, skillPath)` in the DiscoveryRecord table. Double-inserts are idempotent (INSERT ... ON CONFLICT). The downstream submission endpoint also has its own dedup check. Double-enqueue is harmless (same submission ID processed twice = same result).
**Risk**: Low. Worst case: a handful of duplicate submissions per discovery run, which the pipeline handles gracefully.

### Challenge 2: max_concurrency: 20 memory pressure
**Problem**: 20 concurrent queue consumer instances in the same Worker isolate could exhaust memory (128MB default).
**Solution**: Each processSubmission call handles one submission at a time (no unbounded buffering). The heaviest operation is Tier 2 LLM which streams. Cloudflare auto-scales isolates when memory is tight. Monitor via queue metrics after deployment.
**Risk**: Medium. Mitigated by incremental rollout (deploy config change first, monitor before other changes).

### Challenge 3: GitHub token rate limit with 200 parallel submissions
**Problem**: 20 concurrency x 10 batch = 200 parallel submissions, each making 3-5 GitHub API calls.
**Solution**: Authenticated rate limit is 5000 req/hr. At burst of 1000 calls, that's 20% of hourly budget. The raw.githubusercontent.com CDN has much higher limits than api.github.com. Only `resolveCommitSha` and `fetchDirectoryListing` hit api.github.com (2 of ~5 calls per submission). The existing retry logic in `fetchRepoFiles` handles 429 responses.
**Risk**: Low with current config. Would need token rotation (already exists in discovery) if scaling further.
