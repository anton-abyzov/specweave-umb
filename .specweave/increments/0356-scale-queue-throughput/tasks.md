# Tasks: Scale Queue Throughput for Thousands of Repositories

---
by_user_story:
  US-001: [T-001]
  US-002: [T-002, T-003, T-004, T-005]
  US-003: [T-006]
  US-004: [T-007, T-008]
  US-005: [T-009, T-010]
---

## User Story: US-001 - Scale Queue Processing Capacity

**Linked ACs**: AC-US1-01, AC-US1-02, AC-US1-03
**Tasks**: 1 total, 0 completed

### T-001: Bump queue config in wrangler.jsonc

**User Story**: US-001
**Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03
**Status**: [ ] pending

**Test Plan**:
- **Given** wrangler.jsonc with `max_batch_size: 3` and `max_concurrency: 10`
- **When** config values are updated
- **Then** `max_batch_size` is 10, `max_concurrency` is 20, and all other queue config values (max_retries: 3, max_batch_timeout: 60, retry_delay: 10, dead_letter_queue: submission-dlq) remain unchanged

**Test Cases**:
1. **Unit**: `src/lib/queue/__tests__/wrangler-config.test.ts`
   - verifyQueueBatchSize(): Reads wrangler.jsonc, asserts max_batch_size=10
   - verifyQueueConcurrency(): Reads wrangler.jsonc, asserts max_concurrency=20
   - verifyUnchangedConfig(): Asserts max_retries=3, max_batch_timeout=60, retry_delay=10, DLQ unchanged
   - **Coverage Target**: 100%

**Implementation**:
1. Edit `wrangler.jsonc`: change `max_batch_size` from 3 to 10
2. Edit `wrangler.jsonc`: change `max_concurrency` from 10 to 20
3. Write config validation test

---

## User Story: US-002 - Authenticate GitHub API Calls in Processing Pipeline

**Linked ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04, AC-US2-05, AC-US2-06, AC-US2-07, AC-US2-08
**Tasks**: 4 total, 0 completed

### T-002: Add githubToken to ProcessSubmissionOptions and consumer

**User Story**: US-002
**Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-08
**Status**: [ ] pending

**Test Plan**:
- **Given** handleSubmissionQueue receives env with GITHUB_TOKEN set
- **When** a queue message is processed
- **Then** processSubmission is called with githubToken from env

**Test Cases**:
1. **Unit**: `src/lib/queue/__tests__/consumer-token.test.ts`
   - passesGithubTokenFromEnv(): Verify processSubmission receives githubToken when env.GITHUB_TOKEN is set
   - omitsTokenWhenNotSet(): Verify processSubmission receives undefined githubToken when env.GITHUB_TOKEN is undefined
   - **Coverage Target**: 90%

**Implementation**:
1. Add `githubToken?: string` to `ProcessSubmissionOptions` interface in `process-submission.ts`
2. Add `GITHUB_TOKEN?: string` to the env type in `consumer.ts` `handleSubmissionQueue`
3. Pass `env.GITHUB_TOKEN` as `githubToken` in the `processSubmission` call inside consumer

### T-003: Thread token through fetchRepoFiles and helpers

**User Story**: US-002
**Satisfies ACs**: AC-US2-03, AC-US2-04, AC-US2-07
**Status**: [ ] pending
**Depends on**: T-002

**Test Plan**:
- **Given** fetchRepoFiles is called with a token
- **When** it fetches from raw.githubusercontent.com and api.github.com
- **Then** all requests include `Authorization: Bearer <token>` header

- **Given** fetchRepoFiles is called without a token
- **When** it fetches from raw.githubusercontent.com
- **Then** requests have no Authorization header (backward-compatible)

**Test Cases**:
1. **Unit**: `src/lib/scanner/__tests__/fetch-repo-files-token.test.ts`
   - includesAuthHeaderWhenTokenProvided(): Mock fetch, verify Authorization header present
   - omitsAuthHeaderWhenNoToken(): Mock fetch, verify no Authorization header
   - fetchRawFilePassesToken(): Verify internal fetchRawFile gets token
   - fetchDirectoryListingPassesToken(): Verify internal fetchDirectoryListing gets token
   - **Coverage Target**: 90%

**Implementation**:
1. Add optional `token?: string` param to `fetchRepoFiles`, `fetchRawFile`, `fetchDirectoryListing` in `scanner.ts`
2. Build headers object: add `Authorization: Bearer ${token}` when token is present
3. Pass headers to all fetch calls in fetchRepoFiles, fetchRawFile, fetchDirectoryListing
4. Update `processSubmission` to pass `opts.githubToken` to both `fetchRepoFiles` calls (vendor + non-vendor)

### T-004: Thread token through resolveCommitSha

**User Story**: US-002
**Satisfies ACs**: AC-US2-05, AC-US2-06, AC-US2-07
**Status**: [ ] pending
**Depends on**: T-002

**Test Plan**:
- **Given** resolveCommitSha is called with a token
- **When** it fetches the commit SHA from api.github.com
- **Then** the request includes `Authorization: Bearer <token>` header

- **Given** resolveCommitSha is called without a token
- **When** it fetches the commit SHA
- **Then** no Authorization header (backward-compatible)

**Test Cases**:
1. **Unit**: `src/lib/scanner/__tests__/github-permalink-token.test.ts`
   - includesAuthHeaderWhenTokenProvided(): Mock fetch, verify Authorization: Bearer header
   - omitsAuthHeaderWhenNoToken(): Mock fetch, verify User-Agent only (no Authorization)
   - **Coverage Target**: 90%

**Implementation**:
1. Add optional `token?: string` param to `resolveCommitSha` in `github-permalink.ts`
2. Conditionally add `Authorization: Bearer ${token}` to headers
3. Update `processSubmission` to pass `opts.githubToken` to `resolveCommitSha` call

### T-005: Verify existing tests still pass with token changes

**User Story**: US-002
**Satisfies ACs**: AC-US2-07
**Status**: [ ] pending
**Depends on**: T-003, T-004

**Test Plan**:
- **Given** all token threading changes are applied
- **When** existing test suites run
- **Then** all pass without modification (backward compatibility)

**Test Cases**:
1. **Regression**: `src/lib/queue/__tests__/process-submission.test.ts` - all existing tests pass
2. **Regression**: `src/lib/scanner/__tests__/github-permalink.test.ts` - all existing tests pass
   - **Coverage Target**: existing coverage maintained

**Implementation**:
1. Run `npx vitest run src/lib/queue/__tests__/process-submission.test.ts`
2. Run `npx vitest run src/lib/scanner/__tests__/github-permalink.test.ts`
3. Fix any regressions if parameter additions broke existing call sites

---

## User Story: US-003 - Lower Fast-Approve Threshold

**Linked ACs**: AC-US3-01, AC-US3-02, AC-US3-03
**Tasks**: 1 total, 0 completed

### T-006: Lower FAST_APPROVE_THRESHOLD from 85 to 75

**User Story**: US-003
**Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03
**Status**: [ ] pending

**Test Plan**:
- **Given** a code-skill with Tier 1 weighted score of 76
- **When** processSubmission runs the fast-approve check
- **Then** it is fast-approved (skips Tier 2)

- **Given** a code-skill with Tier 1 weighted score of 74
- **When** processSubmission runs the fast-approve check
- **Then** it proceeds to Tier 2 (not fast-approved)

- **Given** a prompt-only skill with Tier 1 weighted score of 90
- **When** processSubmission runs the fast-approve check
- **Then** it proceeds to Tier 2 (hasCodeFiles guard blocks fast-approve)

**Test Cases**:
1. **Unit**: `src/lib/queue/__tests__/process-submission-threshold.test.ts`
   - fastApprovesCodeSkillAbove75(): Score 76 + hasCodeFiles=true -> AUTO_APPROVED
   - doesNotFastApproveCodeSkillBelow76(): Score 74 + hasCodeFiles=true -> TIER2_SCANNING
   - neverFastApprovesPromptOnlySkill(): Score 90 + hasCodeFiles=false -> TIER2_SCANNING
   - **Coverage Target**: 90%

**Implementation**:
1. Change `const FAST_APPROVE_THRESHOLD = 85` to `const FAST_APPROVE_THRESHOLD = 75` in `process-submission.ts`
2. Write threshold boundary tests

---

## User Story: US-004 - Bulk-Enqueue Admin Endpoint

**Linked ACs**: AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-04, AC-US4-05, AC-US4-06, AC-US4-07, AC-US4-08
**Tasks**: 2 total, 0 completed

### T-007: Create bulk-enqueue route with auth and validation

**User Story**: US-004
**Satisfies ACs**: AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-07, AC-US4-08
**Status**: [ ] pending

**Test Plan**:
- **Given** a POST request without auth headers
- **When** hitting /api/v1/admin/queue/bulk-enqueue
- **Then** returns 401

- **Given** a POST with valid X-Internal-Key and items exceeding 1000
- **When** hitting the endpoint
- **Then** returns 400 with "exceeds maximum" error

- **Given** items with invalid repoUrl
- **When** processed
- **Then** those items appear in errors array, valid items are enqueued

**Test Cases**:
1. **Unit**: `src/app/api/v1/admin/queue/bulk-enqueue/__tests__/route.test.ts`
   - rejectsUnauthenticatedRequests(): No X-Internal-Key, no JWT -> 401
   - acceptsInternalKeyAuth(): Valid X-Internal-Key -> 200
   - rejectsExceeding1000Items(): 1001 items -> 400
   - rejectsMissingItems(): No items field -> 400
   - rejectsNonArrayItems(): items: "string" -> 400
   - skipsInvalidRepoUrls(): Invalid URLs appear in errors[], valid ones enqueued
   - skipsInvalidSkillNames(): Too short/long names appear in errors[]
   - **Coverage Target**: 90%

**Implementation**:
1. Create `src/app/api/v1/admin/queue/bulk-enqueue/route.ts`
2. Add POST handler with auth check (hasInternalAuth || requireRole SUPER_ADMIN)
3. Validate items array: required, max 1000, each item has valid repoUrl + skillName
4. Partition items into valid + invalid

### T-008: Implement batch creation and queue enqueue

**User Story**: US-004
**Satisfies ACs**: AC-US4-04, AC-US4-05, AC-US4-06
**Status**: [ ] pending
**Depends on**: T-007

**Test Plan**:
- **Given** 250 valid items
- **When** the endpoint processes them
- **Then** createSubmissionsBatch is called once with 250 items, sendBatch is called 3 times (chunks of 100)

- **Given** all items processed successfully
- **When** response is sent
- **Then** it returns `{ ok: true, enqueued: N, skipped: 0, errors: [] }`

**Test Cases**:
1. **Unit**: `src/app/api/v1/admin/queue/bulk-enqueue/__tests__/route.test.ts`
   - callsCreateSubmissionsBatch(): Verify batch creation with valid items
   - chunksSendBatchBy100(): 250 items -> 3 sendBatch calls (100, 100, 50)
   - returnsCorrectResponseShape(): { ok, enqueued, skipped, errors }
   - handlesQueueSendFailureGracefully(): sendBatch throws -> still returns partial success
   - **Coverage Target**: 85%

**Implementation**:
1. Call `createSubmissionsBatch` with validated items
2. Build `SubmissionQueueMessage` array from created submissions
3. Chunk into batches of 100, call `SUBMISSION_QUEUE.sendBatch` for each
4. Count enqueued vs errors, return aggregated response

---

## User Story: US-005 - Parallelize Discovery Submission Loop

**Linked ACs**: AC-US5-01, AC-US5-02, AC-US5-03, AC-US5-04, AC-US5-05, AC-US5-06
**Tasks**: 2 total, 0 completed

### T-009: Refactor submission loop to parallel batches

**User Story**: US-005
**Satisfies ACs**: AC-US5-01, AC-US5-02, AC-US5-03
**Status**: [ ] pending

**Test Plan**:
- **Given** 100 candidates with maxResults=50
- **When** runGitHubDiscovery processes them
- **Then** only the first 50 candidates are attempted (pre-sliced)

- **Given** DISCOVERY_SUBMIT_BATCH_SIZE=20 and 60 candidates
- **When** runGitHubDiscovery processes them
- **Then** candidates are processed in 3 batches of 20

**Test Cases**:
1. **Unit**: `src/lib/crawler/__tests__/discovery-parallel.test.ts`
   - processesInBatchesOf20(): Mock WORKER_SELF_REFERENCE, verify batched processing
   - respectsMaxResultsCap(): 100 candidates, maxResults=50 -> only 50 attempted
   - exportsBatchSizeConstant(): DISCOVERY_SUBMIT_BATCH_SIZE is exported and equals 20
   - **Coverage Target**: 85%

**Implementation**:
1. Add `export const DISCOVERY_SUBMIT_BATCH_SIZE = 20` constant in `github-discovery.ts`
2. Pre-slice candidates: `const toProcess = allCandidates.slice(0, maxResults)`
3. Replace sequential `for` loop with batched processing:
   - Chunk `toProcess` into groups of `DISCOVERY_SUBMIT_BATCH_SIZE`
   - Process each chunk with `Promise.allSettled`
   - Accumulate enqueued/skipped/errors after each batch
   - Break if enqueued >= maxResults

### T-010: Verify counter accuracy and stats under parallelism

**User Story**: US-005
**Satisfies ACs**: AC-US5-04, AC-US5-05, AC-US5-06
**Status**: [ ] pending
**Depends on**: T-009

**Test Plan**:
- **Given** 10 candidates where 3 are already discovered
- **When** processed in parallel batch
- **Then** enqueued=7, skippedDedup=3, errors=0

- **Given** 10 candidates where 2 fail submission
- **When** processed in parallel batch
- **Then** errors=2, repoStats has correct per-repo counts

**Test Cases**:
1. **Unit**: `src/lib/crawler/__tests__/discovery-parallel.test.ts`
   - accurateDedupCounting(): Mix of new and discovered -> correct skippedDedup count
   - accurateErrorCounting(): Some fail submission -> correct error count
   - repoStatsStillLogged(): Per-repo submitted/skipped stats are accurate
   - dedupWorksUnderParallelism(): No duplicate submissions for same repo
   - **Coverage Target**: 85%

**Implementation**:
1. Use local counters aggregated after each `Promise.allSettled` batch
2. Verify `repoStats` Map accumulates correctly from parallel results
3. Run existing discovery tests to ensure no regressions
