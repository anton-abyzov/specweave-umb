# Tasks: Fix Scanner Infrastructure & Scale Discovery to 60K+

## Phase 1: Recovery (Operational)

### T-001: Deploy 0306 fixes to production
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01 | **Status**: [x] completed
**Test**: Given 0306 code is committed → When deployed via push-deploy.sh → Then /api/v1/admin/rebuild-index returns 200

**Implementation**:
- Verify 0306 changes are committed in vskill-platform repo
- Run `push-deploy.sh` to deploy to Cloudflare Workers
- Verify endpoints are live

---

### T-002: Configure Cloudflare secrets
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02 | **Status**: [x] completed
**Test**: Given secrets are configured → When cron fires → Then DATABASE_URL is available in worker context

**Implementation**:
- `wrangler secret put GITHUB_TOKEN`
- `wrangler secret put DATABASE_URL`
- `wrangler secret put INTERNAL_BROADCAST_KEY`
- Verify via worker log output

---

### T-003: Run rebuild-index to recover skills
**User Story**: US-001 | **Satisfies ACs**: AC-US1-03, AC-US1-04 | **Status**: [x] completed
**Test**: Given surviving skill:* KV keys exist → When POST /api/v1/admin/rebuild-index → Then report shows rebuilt > 0 AND health endpoint shows no drift

**Implementation**:
- POST /api/v1/admin/rebuild-index with admin auth
- GET /api/v1/admin/health/skills to verify
- If KV keys lost, trigger full discovery: POST /api/v1/admin/discovery

---

## Phase 2: Scale Platform Crawler (vskill-platform)

### T-004: Add GitHub token rotation support
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01 | **Status**: [x] completed
**Test**: Given GITHUB_TOKENS="tok1,tok2,tok3" → When crawler makes 6 API calls → Then tokens are used in round-robin: tok1,tok2,tok3,tok1,tok2,tok3

**Implementation**:
- Add `GITHUB_TOKENS?: string` to `CloudflareEnv` in `src/lib/env.d.ts`
- In `github-discovery.ts`: parse tokens, create `TokenRotator` class with `getNext()` method
- Backward compat: fall back to single `GITHUB_TOKEN` if `GITHUB_TOKENS` not set
- Replace `ghHeaders` construction to call `tokenRotator.getNextHeaders()`

---

### T-005: Add time-sharded and diverse search queries
**User Story**: US-002 | **Satisfies ACs**: AC-US2-02, AC-US2-08 | **Status**: [x] completed
**Test**: Given today is 2026-02-21 → When generateTimeShardedQueries("filename:SKILL.md", 7) is called → Then 7 date-bounded queries are generated for each of the last 7 days

**Implementation**:
- Add `generateTimeShardedQueries(base, days)` and `generateStarShardedQueries(base)` helpers
- Expand `CODE_SEARCH_QUERIES` with: `.cursorrules`, `mcp.json`, `.claude/settings.json`, `claude.config.json`
- Expand `REPO_SEARCH_QUERIES` with language and star shards
- Expand `NPM_KEYWORDS` with: `mcp`, `ai-agent`, `llm-tool`, `claude-mcp`, `ai-skill`
- Target 50+ total queries

---

### T-006: Parallelize source execution
**User Story**: US-002 | **Satisfies ACs**: AC-US2-03 | **Status**: [x] completed
**Test**: Given 4 sources available → When runGitHubDiscovery() executes → Then all 4 sources run concurrently and results are merged with dedup

**Implementation**:
- Replace sequential `for...of` loop with `Promise.allSettled()`
- Each source gets its own `Set<string>` for per-source dedup
- After all settle, merge results and cross-source dedup by `fullName`
- Isolate failures: if npm fails, GitHub sources still complete

---

### T-007: Raise submission caps and adaptive delays
**User Story**: US-002 | **Satisfies ACs**: AC-US2-04, AC-US2-05 | **Status**: [x] completed
**Test**: Given X-RateLimit-Remaining header is 25 → When adaptiveDelay() is called → Then delay is 200ms. Given remaining is 3 → Then delay waits until X-RateLimit-Reset timestamp

**Implementation**:
- Raise `MAX_PER_CRON` from 500 to 5000
- Create `adaptiveDelay(response)` that reads `X-RateLimit-Remaining` and `X-RateLimit-Reset`
- Thresholds: >20 → 200ms, >10 → 500ms, >5 → 1000ms, ≤5 → wait until reset
- Replace all `delay(QUERY_DELAY)` calls with `adaptiveDelay(lastResponse)`

---

### T-008: Add discovery TTL for re-scanning
**User Story**: US-002 | **Satisfies ACs**: AC-US2-06 | **Status**: [x] completed
**Test**: Given a DiscoveryRecord with lastSeenAt 45 days ago → When hasBeenDiscovered() is called with staleAfterDays=30 → Then returns false (allows re-scan)

**Implementation**:
- Add `staleAfterDays` parameter to `hasBeenDiscovered()` (default: 30)
- Compare `record.lastSeenAt` against `new Date(Date.now() - staleAfterDays * 86400000)`
- If stale, return false to allow re-discovery
- Existing `@@index([lastSeenAt])` ensures efficient query

---

### T-009: Enhance bulk discovery admin endpoint
**User Story**: US-002 | **Satisfies ACs**: AC-US2-07 | **Status**: [x] completed
**Test**: Given POST /api/v1/admin/discovery/bulk with tokens=["t1","t2"] and maxPerRun=2000 → When crawl completes → Then both tokens used and up to 2000 submissions created

**Implementation**:
- Extend request body to accept `tokens`, `dateRange`, `maxPerRun`
- Pass through to `runGitHubDiscovery()` options
- Validate maxPerRun ≤ 10000
- Return detailed progress report

---

### T-010: Tests for crawler scaling changes
**User Story**: US-002 | **Satisfies ACs**: AC-US2-09 | **Status**: [x] completed
**Test**: Full test suite covers: token rotation round-robin, adaptive delay calculation, parallel source execution, discovery TTL, time-sharded query generation

**Implementation**:
- `src/lib/crawler/__tests__/token-rotation.test.ts`
- `src/lib/crawler/__tests__/adaptive-delay.test.ts`
- `src/lib/crawler/__tests__/parallel-sources.test.ts`
- `src/lib/crawler/__tests__/discovery-ttl.test.ts`
- `src/lib/crawler/__tests__/query-generation.test.ts`
- Mock GitHub API responses, KV, and Prisma

---

## Phase 3: Fix SpecWeave Dashboard Scanner (specweave)

### T-011: Fix scanner worker GitHub token configuration
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01 | **Status**: [x] completed
**Test**: Given GITHUB_TOKEN is set in environment → When scanner worker starts → Then GitHub API calls use the token and rate limit is 5000/hr

**Implementation**:
- In `src/cli/workers/marketplace-scanner-worker.ts`: read `GITHUB_TOKEN` from `process.env` or `.specweave/config.json`
- Add clear error log when token is missing
- Pass token to all GitHub API calls

---

### T-012: Connect dashboard to platform API for verified skills
**User Story**: US-003 | **Satisfies ACs**: AC-US3-02, AC-US3-04 | **Status**: [x] completed
**Test**: Given verified-skill.com API returns 500 skills → When dashboard loads → Then Popular Skills section shows top skills from the platform

**Implementation**:
- In `src/dashboard/server/data/marketplace-aggregator.ts`: add `fetchPlatformSkills()` method
- Call `GET https://verified-skill.com/api/v1/skills?sortBy=trendingScore7d&limit=20`
- Merge platform data into aggregator response
- Handle network errors gracefully (show local data only)

---

### T-013: Fix rate limit display on dashboard
**User Story**: US-003 | **Satisfies ACs**: AC-US3-03 | **Status**: [x] completed
**Test**: Given scanner has no token configured → When Marketplace page loads → Then Rate Limit card shows "No token" with amber color instead of "null/undefined"

**Implementation**:
- In `src/dashboard/client/src/pages/MarketplacePage.tsx`: check for null/undefined rate limit
- Show "No token configured" message with link to docs
- Show actionable hint: "Set GITHUB_TOKEN in environment"

---

## Phase 4: Operational Scaling

### T-014: Create multi-token bulk crawl script
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01 | **Status**: [x] completed
**Test**: Given script is executed with 3 tokens → When complete → Then discovery endpoint was called 3 times with different token subsets

**Implementation**:
- `vskill-platform/scripts/bulk-crawl.sh`: reads tokens from env, distributes queries
- Supports `--dry-run` flag
- Logs progress and results

---

### T-015: Document scanner operations runbook
**User Story**: US-004 | **Satisfies ACs**: AC-US4-02 | **Status**: [x] completed
**Test**: Given runbook exists → When operator follows steps → Then bulk crawl can be executed successfully

**Implementation**:
- `vskill-platform/docs/scanner-ops.md`
- Sections: token setup, secrets config, bulk crawl execution, monitoring, recovery, scaling guide
