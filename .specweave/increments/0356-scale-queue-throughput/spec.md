---
increment: 0356-scale-queue-throughput
title: "Scale Queue Throughput for Thousands of Repositories"
type: feature
priority: P1
status: planned
created: 2026-02-24
structure: user-stories
test_mode: test-after
coverage_target: 80
---

# Feature: Scale Queue Throughput for Thousands of Repositories

## Overview

The vskill-platform processes skill submissions through a Cloudflare Queue pipeline: discovery crawlers find repos, enqueue them, and queue consumers run security scans. Current config limits throughput -- small batch sizes (3), low concurrency (10), unauthenticated GitHub API calls (60 req/hr), and a sequential discovery submission loop create bottlenecks when processing thousands of repositories.

This increment makes five targeted changes to increase end-to-end throughput by an order of magnitude:

1. **Queue config**: Raise `max_batch_size` 3 to 10 and `max_concurrency` 10 to 20 in wrangler.jsonc
2. **Authenticated GitHub API**: Thread `GITHUB_TOKEN` from worker env through consumer.ts, processSubmission, fetchRepoFiles, and resolveCommitSha (60 req/hr to 5000 req/hr)
3. **Fast-approve threshold**: Lower `FAST_APPROVE_THRESHOLD` from 85 to 75 so more code-skills skip Tier 2 LLM scan
4. **Bulk-enqueue endpoint**: Add `POST /api/v1/admin/queue/bulk-enqueue` for Hetzner VMs to batch-enqueue discovered repos directly
5. **Parallel discovery**: Replace sequential `for` loop in `runGitHubDiscovery` with batched `Promise.allSettled` chunks

## User Stories

### US-001: Scale Queue Processing Capacity (P1)
**Project**: vskill-platform

**As a** platform operator
**I want** the queue consumer to process larger batches with higher concurrency
**So that** the pipeline can handle thousands of submissions per hour instead of hundreds

**Acceptance Criteria**:
- [ ] **AC-US1-01**: `wrangler.jsonc` queue consumer `max_batch_size` is set to 10 (was 3)
- [ ] **AC-US1-02**: `wrangler.jsonc` queue consumer `max_concurrency` is set to 20 (was 10)
- [ ] **AC-US1-03**: No other queue config values are changed (max_retries, max_batch_timeout, retry_delay, dead_letter_queue remain unchanged)

---

### US-002: Authenticate GitHub API Calls in Processing Pipeline (P1)
**Project**: vskill-platform

**As a** platform operator
**I want** the processing pipeline to use authenticated GitHub API calls
**So that** the rate limit increases from 60 req/hr (unauthenticated) to 5000 req/hr (authenticated), preventing 403 errors during high-volume processing

**Acceptance Criteria**:
- [ ] **AC-US2-01**: `handleSubmissionQueue` in `consumer.ts` reads `GITHUB_TOKEN` from worker `env` and passes it to `processSubmission` via a new `githubToken` option field
- [ ] **AC-US2-02**: `ProcessSubmissionOptions` interface gains an optional `githubToken?: string` field
- [ ] **AC-US2-03**: `processSubmission` passes `githubToken` to `fetchRepoFiles(repoUrl, skillPath, githubToken)` calls (both vendor and non-vendor paths)
- [ ] **AC-US2-04**: `fetchRepoFiles` accepts an optional `token` parameter and includes `Authorization: Bearer <token>` header on all `raw.githubusercontent.com` fetches and GitHub API calls when token is provided
- [ ] **AC-US2-05**: `resolveCommitSha` in `github-permalink.ts` accepts an optional `token` parameter and includes `Authorization: Bearer <token>` header when provided
- [ ] **AC-US2-06**: `processSubmission` passes `githubToken` to `resolveCommitSha(owner, repo, "HEAD", token)` call
- [ ] **AC-US2-07**: When no token is provided (e.g. direct API route calls), all functions fall back to unauthenticated requests (backward-compatible)
- [ ] **AC-US2-08**: `GITHUB_TOKEN` env binding is declared in the `handleSubmissionQueue` env type (optional string)

---

### US-003: Lower Fast-Approve Threshold (P1)
**Project**: vskill-platform

**As a** platform operator
**I want** the fast-approve threshold lowered from 85 to 75
**So that** more code-skills with clean Tier 1 scans skip the expensive Tier 2 LLM analysis, reducing processing time and AI API costs

**Acceptance Criteria**:
- [ ] **AC-US3-01**: `FAST_APPROVE_THRESHOLD` constant in `process-submission.ts` is changed from 85 to 75
- [ ] **AC-US3-02**: The fast-approve short-circuit logic (`hasCodeFiles && tier1WeightedScore > FAST_APPROVE_THRESHOLD`) remains unchanged -- only the threshold value changes
- [ ] **AC-US3-03**: Pure prompt-only skills are still never fast-approved (the `hasCodeFiles` guard remains)

---

### US-004: Bulk-Enqueue Admin Endpoint (P1)
**Project**: vskill-platform

**As a** Hetzner VM operator
**I want** a `POST /api/v1/admin/queue/bulk-enqueue` endpoint that accepts an array of repositories and enqueues them for processing
**So that** VMs running external discovery scripts can submit thousands of repos directly without the overhead of per-repo HTTP calls to `/api/v1/submissions`

**Acceptance Criteria**:
- [ ] **AC-US4-01**: `POST /api/v1/admin/queue/bulk-enqueue` route exists at `src/app/api/v1/admin/queue/bulk-enqueue/route.ts`
- [ ] **AC-US4-02**: Authentication requires either `X-Internal-Key` header matching `INTERNAL_BROADCAST_KEY` or `SUPER_ADMIN` JWT (same pattern as `/api/v1/admin/discovery/bulk`)
- [ ] **AC-US4-03**: Request body accepts `{ items: Array<{ repoUrl: string; skillName: string; skillPath?: string }> }` with a max of 1000 items per request
- [ ] **AC-US4-04**: Endpoint uses `createSubmissionsBatch` from `submission-store.ts` to batch-create KV + DB records
- [ ] **AC-US4-05**: Endpoint uses `SUBMISSION_QUEUE.sendBatch` in chunks of 100 (CF Queue limit) to enqueue all items
- [ ] **AC-US4-06**: Response returns `{ ok: true, enqueued: number, skipped: number, errors: string[] }` with HTTP 200
- [ ] **AC-US4-07**: Items with invalid `repoUrl` (not matching GitHub URL regex) are skipped with reason in `errors`
- [ ] **AC-US4-08**: Returns 400 if `items` is missing, not an array, or exceeds 1000 entries

---

### US-005: Parallelize Discovery Submission Loop (P1)
**Project**: vskill-platform

**As a** platform operator
**I want** the discovery submission loop in `runGitHubDiscovery` to process candidates in parallel batches
**So that** the enqueue phase (which is currently a sequential for-loop with per-repo dedup + HTTP call) completes faster when processing thousands of candidates

**Acceptance Criteria**:
- [ ] **AC-US5-01**: The sequential `for (const candidate of allCandidates)` loop in `runGitHubDiscovery` is replaced with batched `Promise.allSettled` processing
- [ ] **AC-US5-02**: Batch size is configurable via a constant (default 20 candidates per batch)
- [ ] **AC-US5-03**: The `maxResults` cap is still respected -- processing stops once `enqueued >= maxResults`
- [ ] **AC-US5-04**: Per-skill dedup via `hasBeenDiscovered` / `markDiscovered` still works correctly under parallelism (no duplicate submissions)
- [ ] **AC-US5-05**: Error counting (`errors`) and dedup counting (`skippedDedup`) remain accurate
- [ ] **AC-US5-06**: Per-repo stats logging (`repoStats`) remains functional

## Functional Requirements

### FR-001: Queue Configuration
Update `wrangler.jsonc` `queues.consumers[0]` to set `max_batch_size: 10` and `max_concurrency: 20`. The DLQ consumer config remains unchanged.

### FR-002: Token Threading
Add `githubToken` as an optional field in `ProcessSubmissionOptions`. Thread it from `env.GITHUB_TOKEN` in the queue consumer through to `fetchRepoFiles` and `resolveCommitSha`. Both functions accept an optional token parameter and add an `Authorization: Bearer` header when present. The `fetchRawFile`, `fetchDirectoryListing`, `checkSkillMdExists`, and `discoverSkills` helper functions in `scanner.ts` also gain optional token support for consistency.

### FR-003: Threshold Change
Change the `FAST_APPROVE_THRESHOLD` constant value from 85 to 75 in `process-submission.ts`. No logic changes.

### FR-004: Bulk-Enqueue Endpoint
New Next.js API route at `src/app/api/v1/admin/queue/bulk-enqueue/route.ts` following the same auth pattern as the existing `admin/discovery/bulk` route. Uses `createSubmissionsBatch` for storage and `SUBMISSION_QUEUE.sendBatch` for queueing.

### FR-005: Parallel Discovery
Refactor the sequential submission loop in `runGitHubDiscovery` into batched parallel chunks using `Promise.allSettled`. Use a shared atomic counter pattern for the `enqueued` cap (or pre-slice candidates to `maxResults` before parallel processing).

## Success Criteria

- Queue consumer processes 10 messages per batch at concurrency 20 (verified via wrangler config)
- GitHub API calls in the processing pipeline include Authorization header when GITHUB_TOKEN is set
- Code-skills with Tier 1 scores between 76-85 are now fast-approved (no Tier 2 scan)
- Bulk-enqueue endpoint accepts and queues 1000 items in a single HTTP call
- Discovery submission loop processes candidates in parallel batches of 20

## Out of Scope

- Changing Tier 2 LLM scoring thresholds or logic
- Adding new queue types or DLQ handling changes
- Modifying the discovery source crawlers themselves (code search, repo search, npm, skills.sh)
- Rate limiting on the bulk-enqueue endpoint beyond auth (trusted internal callers only)
- Horizontal scaling of queue consumers (managed by Cloudflare)

## Dependencies

- `GITHUB_TOKEN` must be set as a Cloudflare Workers secret via `wrangler secret put GITHUB_TOKEN`
- Cloudflare Queue service must support `max_batch_size: 10` and `max_concurrency: 20` (within documented limits)
- Existing `createSubmissionsBatch` and `sendBatch` patterns in `submission-store.ts` and `submissions/route.ts`
